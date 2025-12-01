<template>
  <div class="music-player" :class="{ minimized: isMinimized }">
    <!-- 唱片封面 -->
    <div class="vinyl-container" @click="togglePlay">
      <div class="vinyl-disc" :class="{ spinning: isPlaying }">
        <div class="vinyl-grooves"></div>
        <div class="vinyl-label">
          <div class="default-cover">🎵</div>
        </div>
      </div>
      <div class="play-indicator">
        {{ isPlaying ? '⏸' : '▶' }}
      </div>
    </div>

    <!-- 歌曲信息 -->
    <div class="song-info" v-if="!isMinimized">
      <div class="song-title">{{ currentSong?.name || '未选择歌曲' }}</div>
      <div class="song-artist">{{ currentSong?.artist || '点击添加音乐' }}</div>
    </div>

    <!-- 进度条 -->
    <div class="progress-bar" v-if="!isMinimized && currentSong" @click="seekTo">
      <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      <div class="progress-time">
        <span>{{ formatTime(currentTime) }}</span>
        <span>{{ formatTime(duration) }}</span>
      </div>
    </div>

    <!-- 控制按钮 -->
    <div class="controls" v-if="!isMinimized">
      <button class="ctrl-btn" @click="prevSong">⏮</button>
      <button class="ctrl-btn main" @click="togglePlay">
        {{ isPlaying ? '⏸' : '▶' }}
      </button>
      <button class="ctrl-btn" @click="nextSong">⏭</button>
      <button class="ctrl-btn small" @click="togglePlaylist">
        📋
      </button>
    </div>

    <!-- 音量控制 -->
    <div class="volume-control" v-if="!isMinimized">
      <span class="vol-icon">{{ volume === 0 ? '🔇' : volume < 50 ? '🔉' : '🔊' }}</span>
      <input type="range" min="0" max="100" v-model="volume" @input="setVolume" class="vol-slider" />
    </div>

    <!-- 播放列表面板 -->
    <div class="playlist-panel" v-if="showPlaylist && !isMinimized">
      <div class="playlist-header">
        <span>播放列表</span>
        <button class="close-btn" @click="showPlaylist = false">×</button>
      </div>
      
      <!-- 拖拽上传区域 -->
      <div 
        class="add-music-section"
        :class="{ 'drag-over': isDragging }"
        @dragenter.prevent="onDragEnter"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
      >
        <label class="add-music-btn">
          📁 选择本地音乐文件
          <input 
            type="file" 
            accept="audio/*" 
            multiple 
            @change="handleFileSelect"
            style="display: none"
          />
        </label>
        <div class="drop-hint">或拖拽音乐文件到此处</div>
        <div class="supported-formats">支持 MP3, WAV, OGG, FLAC 等格式</div>
        
        <!-- 拖拽提示遮罩 -->
        <div v-if="isDragging" class="drag-overlay">
          <div class="drag-icon">📥</div>
          <div>释放以添加音乐</div>
        </div>
      </div>

      <!-- 播放列表 -->
      <div class="playlist-items">
        <div 
          v-for="(song, idx) in playlist" 
          :key="song.id"
          :class="['playlist-item', { active: currentIndex === idx }]"
          @click="playSong(idx)"
        >
          <div class="item-cover placeholder">🎵</div>
          <div class="item-info">
            <div class="item-name">{{ song.name }}</div>
            <div class="item-artist">{{ song.artist }}</div>
          </div>
          <button class="remove-btn" @click.stop="removeFromPlaylist(idx)">×</button>
        </div>
        <div v-if="playlist.length === 0" class="empty-list">
          <div>🎧</div>
          <div>还没有音乐</div>
          <div class="empty-hint">点击上方按钮或拖拽文件添加音乐</div>
        </div>
      </div>
    </div>

    <!-- 最小化按钮 -->
    <button class="minimize-btn" @click="isMinimized = !isMinimized">
      {{ isMinimized ? '🎵' : '−' }}
    </button>

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

const emit = defineEmits(['stateChange'])

// 状态
const isPlaying = ref(false)
const isMinimized = ref(false)
const showPlaylist = ref(false)
const volume = ref(70)
const currentTime = ref(0)
const duration = ref(0)
const currentIndex = ref(0)
const isDragging = ref(false)

const audioRef = ref(null)

// 播放列表
const playlist = ref([])

// 计算属性
const currentSong = computed(() => playlist.value[currentIndex.value] || null)
const progress = computed(() => duration.value ? (currentTime.value / duration.value) * 100 : 0)

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
  
  // 如果没有歌曲，打开播放列表
  if (!currentSong.value?.url) {
    showPlaylist.value = true
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

const togglePlaylist = () => {
  showPlaylist.value = !showPlaylist.value
}

const removeFromPlaylist = (index) => {
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
.music-player {
  position: relative;
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: all 0.3s ease;
}

.music-player.minimized {
  padding: 6px;
  gap: 0;
}

/* 唱片样式 */
.vinyl-container {
  position: relative;
  width: 60px;
  height: 60px;
  margin: 0 auto;
  cursor: pointer;
}

.minimized .vinyl-container {
  width: 36px;
  height: 36px;
}

.vinyl-disc {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #1a1a1a 0%, #333 50%, #1a1a1a 100%);
  position: relative;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  transition: transform 0.3s ease;
}

.vinyl-disc.spinning {
  animation: spin 3s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.vinyl-grooves {
  position: absolute;
  inset: 8px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.1);
  background: repeating-radial-gradient(
    circle at center,
    transparent 0px,
    transparent 2px,
    rgba(255,255,255,0.03) 2px,
    rgba(255,255,255,0.03) 3px
  );
}

.vinyl-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--term-highlight);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.minimized .vinyl-label {
  width: 16px;
  height: 16px;
}

.vinyl-label img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-cover {
  font-size: 12px;
}

.minimized .default-cover {
  font-size: 8px;
}

.play-indicator {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.4);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 16px;
  color: white;
}

.vinyl-container:hover .play-indicator {
  opacity: 1;
}

/* 歌曲信息 */
.song-info {
  text-align: center;
  padding: 2px 0;
}

.song-title {
  font-size: 11px;
  color: var(--term-highlight);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.song-artist {
  font-size: 9px;
  color: var(--term-dim);
  margin-top: 1px;
}

/* 进度条 */
.progress-bar {
  height: 4px;
  background: var(--term-border);
  border-radius: 2px;
  cursor: pointer;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: var(--term-highlight);
  border-radius: 2px;
  transition: width 0.1s linear;
}

.progress-time {
  display: flex;
  justify-content: space-between;
  font-size: 8px;
  color: var(--term-dim);
  margin-top: 2px;
}

/* 控制按钮 */
.controls {
  display: flex;
  justify-content: center;
  gap: 4px;
}

.ctrl-btn {
  background: transparent;
  border: 1px solid var(--term-border);
  color: var(--term-text);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  transition: all 0.2s;
}

.ctrl-btn:hover {
  background: var(--term-highlight);
  color: var(--term-bg);
  border-color: var(--term-highlight);
}

.ctrl-btn.main {
  width: 28px;
  height: 28px;
  font-size: 12px;
}

.ctrl-btn.small {
  font-size: 10px;
}

/* 音量控制 */
.volume-control {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 0;
}

.vol-icon {
  font-size: 10px;
  width: 16px;
  text-align: center;
}

.vol-slider {
  flex: 1;
  height: 3px;
  -webkit-appearance: none;
  background: var(--term-border);
  border-radius: 2px;
  outline: none;
}

.vol-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 10px;
  height: 10px;
  background: var(--term-highlight);
  border-radius: 50%;
  cursor: pointer;
}

/* 播放列表面板 */
.playlist-panel {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  border-bottom: none;
  max-height: 300px;
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.playlist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  border-bottom: 1px solid var(--term-border);
  font-size: 11px;
  color: var(--term-highlight);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--term-dim);
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
}

.close-btn:hover {
  color: var(--term-text);
}

/* 添加音乐区域 */
.add-music-section {
  padding: 10px;
  border-bottom: 1px solid var(--term-border);
  text-align: center;
  position: relative;
  transition: all 0.3s ease;
  border: 2px dashed transparent;
  margin: 4px;
  border-radius: 6px;
}

.add-music-section.drag-over {
  border-color: var(--term-highlight);
  background: rgba(var(--term-highlight-rgb), 0.1);
}

.add-music-btn {
  display: inline-block;
  padding: 8px 16px;
  background: var(--term-highlight);
  color: var(--term-bg);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s;
}

.add-music-btn:hover {
  filter: brightness(1.1);
  transform: scale(1.02);
}

.drop-hint {
  font-size: 10px;
  color: var(--term-dim);
  margin-top: 6px;
}

.supported-formats {
  font-size: 9px;
  color: var(--term-dim);
  margin-top: 4px;
  opacity: 0.7;
}

/* 拖拽遮罩层 */
.drag-overlay {
  position: absolute;
  inset: 0;
  background: rgba(var(--term-highlight-rgb), 0.15);
  border: 2px dashed var(--term-highlight);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: var(--term-highlight);
  font-size: 12px;
  font-weight: 500;
  z-index: 10;
}

.drag-icon {
  font-size: 24px;
  animation: bounce 0.5s ease infinite alternate;
}

@keyframes bounce {
  from { transform: translateY(0); }
  to { transform: translateY(-4px); }
}

/* 播放列表项 */
.playlist-items {
  flex: 1;
  overflow-y: auto;
  max-height: 180px;
}

.playlist-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid var(--term-border);
}

.playlist-item:hover {
  background: rgba(var(--term-highlight-rgb), 0.1);
}

.playlist-item.active {
  background: rgba(var(--term-highlight-rgb), 0.2);
}

.playlist-item.active .item-name {
  color: var(--term-highlight);
}

.item-cover {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  object-fit: cover;
  flex-shrink: 0;
}

.item-cover.placeholder {
  background: var(--term-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 11px;
  color: var(--term-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-artist {
  font-size: 9px;
  color: var(--term-dim);
  margin-top: 1px;
}

.remove-btn {
  background: transparent;
  border: none;
  color: var(--term-dim);
  cursor: pointer;
  font-size: 14px;
  padding: 2px 6px;
  opacity: 0;
  transition: opacity 0.2s;
}

.playlist-item:hover .remove-btn {
  opacity: 1;
}

.remove-btn:hover {
  color: #f66;
}

.empty-list {
  padding: 20px;
  text-align: center;
  color: var(--term-dim);
  font-size: 11px;
}

.empty-list > div:first-child {
  font-size: 24px;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 9px;
  margin-top: 8px;
  opacity: 0.7;
}

/* 最小化按钮 */
.minimize-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  background: transparent;
  border: none;
  color: var(--term-dim);
  cursor: pointer;
  font-size: 10px;
  padding: 2px;
  line-height: 1;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.minimize-btn:hover {
  opacity: 1;
}

/* 滚动条 */
.playlist-items::-webkit-scrollbar {
  width: 4px;
}

.playlist-items::-webkit-scrollbar-track {
  background: var(--term-bg);
}

.playlist-items::-webkit-scrollbar-thumb {
  background: var(--term-border);
  border-radius: 2px;
}

.playlist-items::-webkit-scrollbar-thumb:hover {
  background: var(--term-dim);
}
</style>
