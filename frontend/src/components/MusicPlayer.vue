<template>
  <div class="music-player-compact">
    <!-- 唱片按钮（始终显示） -->
    <div class="vinyl-btn" @click="togglePanel">
      <div class="vinyl-disc-mini" :class="{ spinning: isPlaying }">
        <div class="vinyl-grooves-mini"></div>
        <div class="vinyl-center">🎵</div>
      </div>
    </div>

    <!-- 展开面板 -->
    <div class="music-panel" v-if="isPanelOpen">
      <div class="panel-header">
        <span class="panel-title">🎵 音乐播放器</span>
        <button class="close-panel-btn" @click="isPanelOpen = false">×</button>
      </div>

      <!-- 当前播放 -->
      <div class="now-playing">
        <div class="vinyl-container-small" @click="togglePlay">
          <div class="vinyl-disc" :class="{ spinning: isPlaying }">
            <div class="vinyl-grooves"></div>
            <div class="vinyl-label">🎵</div>
          </div>
          <div class="play-overlay">{{ isPlaying ? '⏸' : '▶' }}</div>
        </div>
        <div class="song-info">
          <div class="song-title">{{ currentSong?.name || '未选择歌曲' }}</div>
          <div class="song-artist">{{ currentSong?.artist || '点击添加音乐' }}</div>
        </div>
      </div>

      <!-- 进度条 -->
      <div class="progress-bar" v-if="currentSong" @click="seekTo">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
      <div class="progress-time" v-if="currentSong">
        <span>{{ formatTime(currentTime) }}</span>
        <span>{{ formatTime(duration) }}</span>
      </div>

      <!-- 控制按钮 -->
      <div class="controls">
        <button class="ctrl-btn" @click="prevSong">⏮</button>
        <button class="ctrl-btn main" @click="togglePlay">{{ isPlaying ? '⏸' : '▶' }}</button>
        <button class="ctrl-btn" @click="nextSong">⏭</button>
      </div>

      <!-- 音量控制 -->
      <div class="volume-control">
        <span class="vol-icon">{{ volume === 0 ? '🔇' : volume < 50 ? '🔉' : '🔊' }}</span>
        <input type="range" min="0" max="100" v-model="volume" @input="setVolume" class="vol-slider" />
      </div>

      <!-- 添加音乐 -->
      <div 
        class="add-music-section"
        :class="{ 'drag-over': isDragging }"
        @dragenter.prevent="onDragEnter"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
      >
        <label class="add-music-btn">
          📁 添加音乐
          <input type="file" accept="audio/*" multiple @change="handleFileSelect" style="display: none" />
        </label>
      </div>

      <!-- 播放列表 -->
      <div class="playlist-items" v-if="playlist.length > 0">
        <div 
          v-for="(song, idx) in playlist" 
          :key="song.id"
          :class="['playlist-item', { active: currentIndex === idx }]"
          @click="playSong(idx)"
        >
          <span class="item-icon">🎵</span>
          <div class="item-info">
            <div class="item-name">{{ song.name }}</div>
            <div class="item-artist">{{ song.artist }}</div>
          </div>
          <button class="remove-btn" @click.stop="removeFromPlaylist(idx)">×</button>
        </div>
      </div>
    </div>

    <!-- 隐藏的audio元素 -->
    <audio 
      ref="audioRef"
      :src="currentSong?.url"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
      @loadedmetadata="onLoaded"
      @canplay="onCanPlay"
      @error="onError"
      preload="auto"
    ></audio>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { buildAssetUrl } from '../utils/api'

const emit = defineEmits(['stateChange'])

// 状态
const isPlaying = ref(false)
const isPanelOpen = ref(false)
const volume = ref(70)
const currentTime = ref(0)
const duration = ref(0)
const currentIndex = ref(0)
const isDragging = ref(false)

const audioRef = ref(null)

// 播放列表 - 包含默认歌曲
const playlist = ref([
  {
    id: 'default-1',
    name: 'Affection',
    artist: 'jinsang',
    url: buildAssetUrl('assets/music/default.mp3'),
    isDefault: true
  }
])

// 计算属性
const currentSong = computed(() => playlist.value[currentIndex.value] || null)
const progress = computed(() => duration.value ? (currentTime.value / duration.value) * 100 : 0)

// 切换面板显示
const togglePanel = () => {
  isPanelOpen.value = !isPanelOpen.value
}

// ============ 文件处理 ============

// 处理文件选择
const handleFileSelect = (event) => {
  const files = event.target.files
  if (!files || files.length === 0) return
  
  for (const file of files) {
    // 检查是否是音频文件
    if (!file.type.startsWith('audio/')) continue
    
    // 解析文件名获取歌曲信息
    const fileName = file.name.replace(/\.[^/.]+$/, '') // 去掉扩展名
    let name = fileName
    let artist = '本地音乐'
    
    // 尝试解析 "歌手 - 歌名" 格式
    if (fileName.includes(' - ')) {
      const parts = fileName.split(' - ')
      artist = parts[0].trim()
      name = parts.slice(1).join(' - ').trim()
    }
    
    // 创建 Object URL
    const url = URL.createObjectURL(file)
    
    // 添加到播放列表
    playlist.value.push({
      id: Date.now() + Math.random(),
      name,
      artist,
      url,
      file // 保存文件引用
    })
  }
  
  // 保存播放列表信息（不包含 blob URL）
  savePlaylistMeta()
  
  // 如果是第一首歌，自动选中
  if (playlist.value.length === files.length) {
    currentIndex.value = 0
  }
  
  // 清空 input 以允许重复选择
  event.target.value = ''
}

// 处理文件（通用方法，用于拖拽和选择）
const addFiles = (files) => {
  if (!files || files.length === 0) return
  
  const startCount = playlist.value.length
  
  for (const file of files) {
    // 检查是否是音频文件
    if (!file.type.startsWith('audio/')) continue
    
    // 解析文件名获取歌曲信息
    const fileName = file.name.replace(/\.[^/.]+$/, '') // 去掉扩展名
    let name = fileName
    let artist = '本地音乐'
    
    // 尝试解析 "歌手 - 歌名" 格式
    if (fileName.includes(' - ')) {
      const parts = fileName.split(' - ')
      artist = parts[0].trim()
      name = parts.slice(1).join(' - ').trim()
    }
    
    // 创建 Object URL
    const url = URL.createObjectURL(file)
    
    // 添加到播放列表
    playlist.value.push({
      id: Date.now() + Math.random(),
      name,
      artist,
      url,
      file
    })
  }
  
  savePlaylistMeta()
  
  // 如果是第一批歌曲，自动选中第一首
  if (startCount === 0 && playlist.value.length > 0) {
    currentIndex.value = 0
  }
}

// ============ 拖拽处理 ============

const onDragEnter = (e) => {
  isDragging.value = true
}

const onDragOver = (e) => {
  isDragging.value = true
}

const onDragLeave = (e) => {
  // 检查是否真的离开了区域
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX
  const y = e.clientY
  if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
    isDragging.value = false
  }
}

const onDrop = (e) => {
  isDragging.value = false
  
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    addFiles(files)
  }
}

// ============ 播放控制 ============

const togglePlay = () => {
  if (!audioRef.value) return
  
  // 如果没有歌曲，打开面板
  if (!currentSong.value?.url) {
    isPanelOpen.value = true
    return
  }
  
  if (isPlaying.value) {
    audioRef.value.pause()
    isPlaying.value = false
  } else {
    audioRef.value.play().catch(e => {
      if (e.name !== 'AbortError') {
        console.log('播放失败:', e)
      }
    })
    isPlaying.value = true
  }
  emit('stateChange', isPlaying.value)
}

const playSong = (index) => {
  if (index === currentIndex.value && isPlaying.value) {
    // 点击当前正在播放的歌曲，暂停
    togglePlay()
    return
  }
  
  currentIndex.value = index
  isPlaying.value = true
  emit('stateChange', true)
}

const prevSong = () => {
  if (playlist.value.length === 0) return
  currentIndex.value = currentIndex.value > 0 
    ? currentIndex.value - 1 
    : playlist.value.length - 1
  isPlaying.value = true
  emit('stateChange', true)
}

const nextSong = () => {
  if (playlist.value.length === 0) return
  currentIndex.value = currentIndex.value < playlist.value.length - 1 
    ? currentIndex.value + 1 
    : 0
  isPlaying.value = true
  emit('stateChange', true)
}

const setVolume = () => {
  if (audioRef.value) {
    audioRef.value.volume = volume.value / 100
  }
}

const seekTo = (e) => {
  if (!audioRef.value || !duration.value) return
  const rect = e.target.getBoundingClientRect()
  const percent = (e.clientX - rect.left) / rect.width
  audioRef.value.currentTime = percent * duration.value
}

const removeFromPlaylist = (index) => {
  // 不允许删除默认歌曲
  if (playlist.value[index]?.isDefault) return
  
  // 释放 Object URL
  if (playlist.value[index]?.url?.startsWith('blob:')) {
    URL.revokeObjectURL(playlist.value[index].url)
  }
  
  playlist.value.splice(index, 1)
  
  if (currentIndex.value >= playlist.value.length) {
    currentIndex.value = Math.max(0, playlist.value.length - 1)
  }
  
  if (playlist.value.length === 0) {
    isPlaying.value = false
    emit('stateChange', false)
  }
  
  savePlaylistMeta()
}

// ============ 工具函数 ============

const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 保存播放列表元信息（用于显示，不包含实际音频）
const savePlaylistMeta = () => {
  try {
    const meta = playlist.value.map(s => ({
      name: s.name,
      artist: s.artist
    }))
    localStorage.setItem('echopolis_playlist_meta', JSON.stringify(meta))
  } catch (e) {}
}

// ============ Audio 事件处理 ============

const onTimeUpdate = () => {
  if (audioRef.value) {
    currentTime.value = audioRef.value.currentTime
  }
}

const onLoaded = () => {
  if (audioRef.value) {
    duration.value = audioRef.value.duration
  }
}

const onCanPlay = () => {
  if (audioRef.value && isPlaying.value) {
    audioRef.value.play().catch(e => {
      if (e.name !== 'AbortError') {
        console.log('播放失败:', e)
      }
    })
  }
}

const onEnded = () => {
  nextSong()
}

const onError = (e) => {
  if (!currentSong.value?.url) return
  console.error('音频加载失败')
}

// ============ 键盘快捷键 ============

const handleKeyboard = (e) => {
  if (e.target.tagName === 'INPUT') return
  if (e.code === 'Space') {
    e.preventDefault()
    togglePlay()
  }
}

// ============ 生命周期 ============

onMounted(() => {
  if (audioRef.value) {
    audioRef.value.volume = volume.value / 100
  }
  window.addEventListener('keydown', handleKeyboard)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboard)
  // 清理所有 Object URLs
  playlist.value.forEach(song => {
    if (song.url?.startsWith('blob:')) {
      URL.revokeObjectURL(song.url)
    }
  })
})

// 暴露方法给父组件
defineExpose({
  togglePlay,
  isPlaying
})
</script>

<style scoped>
.music-player-compact {
  position: relative;
  display: flex;
  align-items: center;
}

/* 右上角唱片按钮 */
.vinyl-btn {
  width: 36px;
  height: 36px;
  cursor: pointer;
  transition: transform 0.2s;
}

.vinyl-btn:hover {
  transform: scale(1.1);
}

.vinyl-disc-mini {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #1a1a1a 0%, #333 50%, #1a1a1a 100%);
  position: relative;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.vinyl-disc-mini.spinning {
  animation: spin 3s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.vinyl-grooves-mini {
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.1);
  background: repeating-radial-gradient(
    circle at center,
    transparent 0px,
    transparent 1px,
    rgba(255,255,255,0.05) 1px,
    rgba(255,255,255,0.05) 2px
  );
}

.vinyl-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--term-highlight, #22c55e);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 8px;
}

/* 展开面板 */
.music-panel {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  width: 280px;
  background: var(--term-panel-bg, #0a0a0a);
  border: 2px solid var(--term-border, #333);
  border-radius: 8px;
  z-index: 1000;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid var(--term-border, #333);
}

.panel-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--term-highlight, #22c55e);
}

.close-panel-btn {
  background: transparent;
  border: none;
  color: var(--term-dim, #666);
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  padding: 0;
}

.close-panel-btn:hover {
  color: var(--term-text, #fff);
}

/* 当前播放区域 */
.now-playing {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
}

.vinyl-container-small {
  position: relative;
  width: 50px;
  height: 50px;
  cursor: pointer;
  flex-shrink: 0;
}

.vinyl-container-small .vinyl-disc {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #1a1a1a 0%, #333 50%, #1a1a1a 100%);
  position: relative;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.vinyl-container-small .vinyl-disc.spinning {
  animation: spin 3s linear infinite;
}

.vinyl-container-small .vinyl-grooves {
  position: absolute;
  inset: 6px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.1);
  background: repeating-radial-gradient(
    circle at center,
    transparent 0px,
    transparent 1px,
    rgba(255,255,255,0.03) 1px,
    rgba(255,255,255,0.03) 2px
  );
}

.vinyl-container-small .vinyl-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--term-highlight, #22c55e);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
}

.play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.4);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 14px;
  color: white;
}

.vinyl-container-small:hover .play-overlay {
  opacity: 1;
}

.song-info {
  flex: 1;
  min-width: 0;
}

.song-title {
  font-size: 12px;
  color: var(--term-text, #fff);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.song-artist {
  font-size: 10px;
  color: var(--term-dim, #666);
  margin-top: 2px;
}

/* 进度条 */
.progress-bar {
  height: 4px;
  background: var(--term-border, #333);
  border-radius: 2px;
  cursor: pointer;
  margin: 0 12px;
}

.progress-fill {
  height: 100%;
  background: var(--term-highlight, #22c55e);
  border-radius: 2px;
  transition: width 0.1s linear;
}

.progress-time {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: var(--term-dim, #666);
  padding: 4px 12px 0;
}

/* 控制按钮 */
.controls {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 10px;
}

.ctrl-btn {
  background: transparent;
  border: 1px solid var(--term-border, #333);
  color: var(--term-text, #fff);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  transition: all 0.2s;
}

.ctrl-btn:hover {
  background: var(--term-highlight, #22c55e);
  color: var(--term-bg, #000);
  border-color: var(--term-highlight, #22c55e);
}

.ctrl-btn.main {
  width: 32px;
  height: 32px;
  font-size: 13px;
}

/* 音量控制 */
.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px 10px;
}

.vol-icon {
  font-size: 12px;
}

.vol-slider {
  flex: 1;
  height: 4px;
  -webkit-appearance: none;
  background: var(--term-border, #333);
  border-radius: 2px;
  outline: none;
}

.vol-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  background: var(--term-highlight, #22c55e);
  border-radius: 50%;
  cursor: pointer;
}

/* 添加音乐区域 */
.add-music-section {
  padding: 10px 12px;
  border-top: 1px solid var(--term-border, #333);
  text-align: center;
}

.add-music-section.drag-over {
  background: rgba(34, 197, 94, 0.1);
}

.add-music-btn {
  display: inline-block;
  padding: 6px 14px;
  background: var(--term-highlight, #22c55e);
  color: var(--term-bg, #000);
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 500;
  transition: all 0.2s;
}

.add-music-btn:hover {
  filter: brightness(1.1);
}

/* 播放列表 */
.playlist-items {
  max-height: 150px;
  overflow-y: auto;
  border-top: 1px solid var(--term-border, #333);
}

.playlist-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.playlist-item:hover {
  background: rgba(255,255,255,0.05);
}

.playlist-item.active {
  background: rgba(34, 197, 94, 0.15);
}

.playlist-item.active .item-name {
  color: var(--term-highlight, #22c55e);
}

.item-icon {
  font-size: 14px;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 11px;
  color: var(--term-text, #fff);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-artist {
  font-size: 9px;
  color: var(--term-dim, #666);
  margin-top: 1px;
}

.remove-btn {
  background: transparent;
  border: none;
  color: var(--term-dim, #666);
  cursor: pointer;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.2s;
}

.playlist-item:hover .remove-btn {
  opacity: 1;
}

.remove-btn:hover {
  color: #f66;
}

/* 滚动条 */
.playlist-items::-webkit-scrollbar {
  width: 4px;
}

.playlist-items::-webkit-scrollbar-track {
  background: transparent;
}

.playlist-items::-webkit-scrollbar-thumb {
  background: var(--term-border, #333);
  border-radius: 2px;
}
</style>
