<template>
  <div class="settings-panel" v-if="isOpen">
    <div class="settings-overlay" @click="close"></div>
    <div class="settings-content">
      <div class="settings-header">
        <h3>⚙️ 系统设置</h3>
        <button class="close-btn" @click="close">×</button>
      </div>
      
      <div class="settings-body">
        <!-- 显示设置 -->
        <div class="settings-section">
          <div class="section-title">显示</div>
          <div class="setting-item">
            <span class="setting-label">
              <span class="icon">{{ isDark ? '🌙' : '☀️' }}</span>
              主题模式
            </span>
            <div class="setting-control">
              <button 
                :class="['toggle-btn', { active: !isDark }]" 
                @click="setTheme(false)">亮色</button>
              <button 
                :class="['toggle-btn', { active: isDark }]" 
                @click="setTheme(true)">暗色</button>
            </div>
          </div>
          <div class="setting-item">
            <span class="setting-label">
              <span class="icon">📺</span>
              CRT 效果
            </span>
            <div class="setting-control">
              <label class="switch">
                <input type="checkbox" v-model="crtEnabled" @change="toggleCrt">
                <span class="slider"></span>
              </label>
            </div>
          </div>
          <div class="setting-item">
            <span class="setting-label">
              <span class="icon">✨</span>
              动画效果
            </span>
            <div class="setting-control">
              <label class="switch">
                <input type="checkbox" v-model="animationsEnabled">
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>

        <!-- 音频设置 -->
        <div class="settings-section">
          <div class="section-title">音频</div>
          <div class="setting-item">
            <span class="setting-label">
              <span class="icon">🔊</span>
              背景音乐
            </span>
            <div class="setting-control">
              <label class="switch">
                <input type="checkbox" v-model="bgmEnabled" @change="toggleBgm">
                <span class="slider"></span>
              </label>
            </div>
          </div>
          <div class="setting-item">
            <span class="setting-label">
              <span class="icon">🔔</span>
              音效
            </span>
            <div class="setting-control">
              <label class="switch">
                <input type="checkbox" v-model="sfxEnabled">
                <span class="slider"></span>
              </label>
            </div>
          </div>
          <div class="setting-item">
            <span class="setting-label">
              <span class="icon">🎚️</span>
              主音量
            </span>
            <div class="setting-control wide">
              <input 
                type="range" 
                min="0" 
                max="100" 
                v-model="masterVolume"
                class="volume-slider"
              />
              <span class="volume-value">{{ masterVolume }}%</span>
            </div>
          </div>
        </div>

        <!-- 语言设置 -->
        <div class="settings-section">
          <div class="section-title">语言</div>
          <div class="setting-item">
            <span class="setting-label">
              <span class="icon">🌐</span>
              界面语言
            </span>
            <div class="setting-control">
              <select v-model="language" class="lang-select">
                <option value="zh-CN">简体中文</option>
                <option value="zh-TW">繁體中文</option>
                <option value="en">English</option>
                <option value="ja">日本語</option>
              </select>
            </div>
          </div>
        </div>

        <!-- 游戏设置 -->
        <div class="settings-section">
          <div class="section-title">游戏</div>
          <div class="setting-item">
            <span class="setting-label">
              <span class="icon">⏩</span>
              自动推进速度
            </span>
            <div class="setting-control">
              <select v-model="gameSpeed" class="speed-select">
                <option value="slow">慢速 (3秒/月)</option>
                <option value="normal">正常 (2秒/月)</option>
                <option value="fast">快速 (1秒/月)</option>
              </select>
            </div>
          </div>
          <div class="setting-item">
            <span class="setting-label">
              <span class="icon">📝</span>
              显示教程提示
            </span>
            <div class="setting-control">
              <label class="switch">
                <input type="checkbox" v-model="showTutorial">
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>

        <!-- 数据管理 -->
        <div class="settings-section">
          <div class="section-title">数据</div>
          <div class="setting-item">
            <span class="setting-label">
              <span class="icon">💾</span>
              导出存档
            </span>
            <div class="setting-control">
              <button class="action-btn" @click="exportSave">导出</button>
            </div>
          </div>
          <div class="setting-item">
            <span class="setting-label">
              <span class="icon">📂</span>
              导入存档
            </span>
            <div class="setting-control">
              <button class="action-btn" @click="importSave">导入</button>
            </div>
          </div>
          <div class="setting-item danger">
            <span class="setting-label">
              <span class="icon">🗑️</span>
              清除本地数据
            </span>
            <div class="setting-control">
              <button class="action-btn danger" @click="clearData">清除</button>
            </div>
          </div>
        </div>
      </div>

      <div class="settings-footer">
        <div class="version-info">
          EchoPolis v1.0.0 | © 2025
        </div>
        <button class="save-btn" @click="saveAndClose">保存设置</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useThemeStore } from '../stores/theme'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'bgmToggle', 'crtToggle'])

const themeStore = useThemeStore()

// 设置状态
const isDark = ref(themeStore.isDark)
const crtEnabled = ref(true)
const animationsEnabled = ref(true)
const bgmEnabled = ref(true)
const sfxEnabled = ref(true)
const masterVolume = ref(70)
const language = ref('zh-CN')
const gameSpeed = ref('normal')
const showTutorial = ref(true)

// 从localStorage加载设置
const loadSettings = () => {
  try {
    const saved = localStorage.getItem('echopolis_settings')
    if (saved) {
      const settings = JSON.parse(saved)
      isDark.value = settings.isDark ?? themeStore.isDark
      crtEnabled.value = settings.crtEnabled ?? true
      animationsEnabled.value = settings.animationsEnabled ?? true
      bgmEnabled.value = settings.bgmEnabled ?? true
      sfxEnabled.value = settings.sfxEnabled ?? true
      masterVolume.value = settings.masterVolume ?? 70
      language.value = settings.language ?? 'zh-CN'
      gameSpeed.value = settings.gameSpeed ?? 'normal'
      showTutorial.value = settings.showTutorial ?? true
    }
  } catch (e) {
    console.error('加载设置失败:', e)
  }
}

// 保存设置到localStorage
const saveSettings = () => {
  const settings = {
    isDark: isDark.value,
    crtEnabled: crtEnabled.value,
    animationsEnabled: animationsEnabled.value,
    bgmEnabled: bgmEnabled.value,
    sfxEnabled: sfxEnabled.value,
    masterVolume: masterVolume.value,
    language: language.value,
    gameSpeed: gameSpeed.value,
    showTutorial: showTutorial.value
  }
  localStorage.setItem('echopolis_settings', JSON.stringify(settings))
}

// 方法
const close = () => {
  emit('close')
}

const setTheme = (dark) => {
  isDark.value = dark
  if (dark) {
    themeStore.setTheme('orange')
  } else {
    themeStore.setTheme('beige')
  }
}

const toggleCrt = () => {
  emit('crtToggle', crtEnabled.value)
}

const toggleBgm = () => {
  emit('bgmToggle', bgmEnabled.value)
}

const exportSave = () => {
  try {
    const data = {
      settings: JSON.parse(localStorage.getItem('echopolis_settings') || '{}'),
      currentCharacter: localStorage.getItem('currentCharacter'),
      timestamp: new Date().toISOString()
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `echopolis_save_${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    alert('导出失败')
  }
}

const importSave = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    try {
      const text = await file.text()
      const data = JSON.parse(text)
      if (data.settings) {
        localStorage.setItem('echopolis_settings', JSON.stringify(data.settings))
      }
      if (data.currentCharacter) {
        localStorage.setItem('currentCharacter', data.currentCharacter)
      }
      alert('导入成功！请刷新页面。')
      loadSettings()
    } catch (e) {
      alert('导入失败：文件格式错误')
    }
  }
  input.click()
}

const clearData = () => {
  if (confirm('确定要清除所有本地数据吗？此操作不可恢复！')) {
    localStorage.removeItem('echopolis_settings')
    localStorage.removeItem('currentCharacter')
    alert('数据已清除')
    location.reload()
  }
}

const saveAndClose = () => {
  saveSettings()
  close()
}

// 监听主题变化
watch(() => themeStore.isDark, (val) => {
  isDark.value = val
})

onMounted(() => {
  loadSettings()
})

// 暴露给父组件
defineExpose({
  bgmEnabled,
  crtEnabled
})
</script>

<style scoped>
.settings-panel {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.settings-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
}

.settings-content {
  position: relative;
  width: 520px;
  max-width: 95vw;
  max-height: 85vh;
  background: var(--term-panel-bg);
  border: 3px solid var(--term-border);
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 2px solid var(--term-border);
}

.settings-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
}

.close-btn {
  width: 28px;
  height: 28px;
  border: 2px solid var(--term-border);
  background: none;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--term-text);
}

.close-btn:hover {
  background: var(--term-accent);
  color: #000;
}

.settings-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.settings-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 11px;
  font-weight: 800;
  color: var(--term-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px dashed var(--term-border);
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.setting-item.danger .setting-label {
  color: #ef4444;
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
}

.setting-label .icon {
  font-size: 16px;
}

.setting-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-control.wide {
  flex: 1;
  max-width: 180px;
  display: flex;
  gap: 10px;
}

/* Toggle buttons */
.toggle-btn {
  padding: 4px 12px;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid var(--term-border);
  background: var(--term-bg);
  color: var(--term-text);
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn:first-child {
  border-radius: 4px 0 0 4px;
}

.toggle-btn:last-child {
  border-radius: 0 4px 4px 0;
  border-left: none;
}

.toggle-btn.active {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

/* Switch */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: var(--term-border);
  border-radius: 24px;
  transition: 0.3s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background: white;
  border-radius: 50%;
  transition: 0.3s;
}

input:checked + .slider {
  background: var(--term-accent);
}

input:checked + .slider:before {
  transform: translateX(20px);
}

/* Volume slider */
.volume-slider {
  flex: 1;
  height: 4px;
  -webkit-appearance: none;
  background: var(--term-border);
  border-radius: 2px;
  cursor: pointer;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  background: var(--term-accent);
  border-radius: 50%;
  cursor: pointer;
}

.volume-value {
  font-size: 11px;
  font-weight: 700;
  min-width: 42px;
  text-align: right;
  flex-shrink: 0;
  color: var(--term-text);
}

/* Select */
.lang-select,
.speed-select {
  padding: 6px 10px;
  font-size: 12px;
  border: 1px solid var(--term-border);
  background: var(--term-bg);
  color: var(--term-text);
  cursor: pointer;
}

/* Action button */
.action-btn {
  padding: 6px 14px;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid var(--term-border);
  background: var(--term-panel-bg);
  color: var(--term-text);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--term-accent);
  color: #000;
}

.action-btn.danger {
  border-color: #ef4444;
  color: #ef4444;
}

.action-btn.danger:hover {
  background: #ef4444;
  color: white;
}

/* Footer */
.settings-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-top: 2px solid var(--term-border);
  background: rgba(0,0,0,0.02);
}

.version-info {
  font-size: 10px;
  color: var(--term-text-secondary);
}

.save-btn {
  padding: 8px 20px;
  font-size: 12px;
  font-weight: 800;
  background: var(--term-accent);
  color: #000;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn:hover {
  filter: brightness(1.1);
}
</style>
