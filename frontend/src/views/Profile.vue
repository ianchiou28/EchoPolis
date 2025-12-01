<template>
  <div class="profile-page">
    <div class="game-bg"></div>
    <div class="page-header">
      <div class="header-content">
        <h1>PERSONAL TERMINAL // 个人终端</h1>
        <p class="subtitle">MANAGE ASSETS & PREFERENCES // 管理资产与偏好</p>
      </div>
      <button class="btn ghost" @click="$router.push('/home')">
        BACK // 返回
      </button>
    </div>

    <div class="profile-container">
      <!-- 用户信息卡片 -->
      <div class="user-card glass-panel tech-border">
        <div class="avatar-wrapper">
          <div class="avatar-circle">{{ avatar?.name?.charAt(0) || 'U' }}</div>
          <div class="status-indicator online"></div>
        </div>
        <div class="user-info">
          <div class="username">{{ avatar?.name || 'Unknown User' }}</div>
          <div class="user-meta">
            <span class="tag mbti">{{ avatar?.mbti_type || 'UNKNOWN' }}</span>
            <span class="tag id">ID: {{ avatar?.id?.substring(0, 8) || '--------' }}</span>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">NET WORTH // 总资产</span>
              <span class="stat-value money">¥{{ formatNumber(avatar?.total_assets || 0) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">TRUST RATING // 信任评级</span>
              <span class="stat-value trust">{{ avatar?.trust_level || 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 设置列表 -->
      <div class="settings-grid">
        <!-- 游戏设置 -->
        <div class="setting-section glass-panel tech-border">
          <div class="section-header">
            <span class="section-icon">⚙️</span>
            <span class="section-title">SYSTEM PREFS // 系统偏好</span>
          </div>
          
          <div class="setting-item" @click="showThemeModal = true">
            <div class="item-left">
              <span class="item-icon">🎨</span>
              <div class="item-content">
                <span class="item-name">INTERFACE THEME // 界面主题</span>
                <span class="item-desc">Customize visual style</span>
              </div>
            </div>
            <div class="item-right">
              <span class="item-value">{{ currentThemeName }}</span>
              <span class="arrow">›</span>
            </div>
          </div>

          <div class="setting-item">
            <div class="item-left">
              <span class="item-icon">🔔</span>
              <div class="item-content">
                <span class="item-name">NOTIFICATIONS // 消息通知</span>
                <span class="item-desc">System alerts</span>
              </div>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="settings.notification">
              <span class="slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="item-left">
              <span class="item-icon">🔊</span>
              <div class="item-content">
                <span class="item-name">AUDIO FEEDBACK // 音效反馈</span>
                <span class="item-desc">Interaction sounds</span>
              </div>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="settings.sound">
              <span class="slider"></span>
            </label>
          </div>
        </div>

        <!-- 账号管理 -->
        <div class="setting-section glass-panel tech-border">
          <div class="section-header">
            <span class="section-icon">🛡️</span>
            <span class="section-title">DATA MGMT // 数据管理</span>
          </div>

          <div class="setting-item danger-hover" @click="resetGame">
            <div class="item-left">
              <span class="item-icon">🔄</span>
              <div class="item-content">
                <span class="item-name">RESET TIMELINE // 重置时间线</span>
                <span class="item-desc">Clear all progress</span>
              </div>
            </div>
            <span class="arrow">›</span>
          </div>

          <div class="setting-item" @click="exportData">
            <div class="item-left">
              <span class="item-icon">📤</span>
              <div class="item-content">
                <span class="item-name">EXPORT MEMORY // 导出记忆</span>
                <span class="item-desc">Backup save data</span>
              </div>
            </div>
            <span class="arrow">›</span>
          </div>

          <div class="setting-item" @click="logout">
            <div class="item-left">
              <span class="item-icon">🚪</span>
              <div class="item-content">
                <span class="item-name">DISCONNECT // 断开连接</span>
                <span class="item-desc">Logout session</span>
              </div>
            </div>
            <span class="arrow">›</span>
          </div>
        </div>

        <!-- 关于 -->
        <div class="setting-section glass-panel tech-border">
          <div class="section-header">
            <span class="section-icon">ℹ️</span>
            <span class="section-title">SYSTEM INFO // 系统信息</span>
          </div>
          
          <div class="setting-item">
            <div class="item-left">
              <span class="item-icon">🤖</span>
              <div class="item-content">
                <span class="item-name">FinAI Core</span>
                <span class="item-desc">Version</span>
              </div>
            </div>
            <span class="item-value mono">v1.0.0-alpha</span>
          </div>

          <div class="setting-item" @click="showHelp">
            <div class="item-left">
              <span class="item-icon">❓</span>
              <div class="item-content">
                <span class="item-name">HELP CENTER // 帮助中心</span>
                <span class="item-desc">User manual</span>
              </div>
            </div>
            <span class="arrow">›</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主题选择弹窗 -->
    <transition name="modal-fade">
      <div v-if="showThemeModal" class="modal-overlay" @click="showThemeModal = false">
        <div class="modal-content glass-panel" @click.stop>
          <div class="modal-header">
            <h3>视觉风格配置</h3>
            <p>选择最适合你的终端界面主题</p>
          </div>
          <div class="theme-options">
            <div 
              v-for="(theme, key) in themeStore.themes" 
              :key="key"
              class="theme-option"
              :class="{ active: themeStore.currentTheme === key }"
              @click="selectTheme(key)"
            >
              <div class="theme-preview" :style="{ background: getThemeColor(key) }">
                <div class="preview-dot"></div>
              </div>
              <div class="theme-info">
                <div class="theme-name">{{ theme.name }}</div>
                <div class="theme-key">{{ key.toUpperCase() }}</div>
              </div>
              <div class="active-indicator" v-if="themeStore.currentTheme === key">●</div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'
import { useThemeStore } from '../stores/theme'

const router = useRouter()
const gameStore = useGameStore()
const themeStore = useThemeStore()

const avatar = computed(() => gameStore.avatar)
const showThemeModal = ref(false)

const settings = ref({
  notification: true,
  sound: true
})

const currentThemeName = computed(() => {
  return themeStore.theme.name
})

const formatNumber = (num) => {
  return num?.toLocaleString('zh-CN') || '0'
}

const getThemeColor = (key) => {
  const colors = {
    slate: '#64748b',
    silver: '#94a3b8',
    ocean: '#0ea5e9',
    emerald: '#10b981',
    royal: '#8b5cf6',
    pink: '#ec4899'
  }
  return colors[key] || '#64748b'
}

const selectTheme = (key) => {
  themeStore.setTheme(key)
  // showThemeModal.value = false // Optional: keep open to see effect
}

const resetGame = () => {
  if (confirm('⚠️ 警告：确定要重置时间线吗？\n此操作将清除所有进度且无法撤销！')) {
    console.log('重置游戏')
    // TODO: 调用API重置游戏
  }
}

const exportData = () => {
  alert('正在打包记忆数据...\n(功能开发中)')
}

const logout = () => {
  if (confirm('确定要断开与 FinAI金融模拟沙盘 的连接吗？')) {
    localStorage.removeItem('username')
    localStorage.removeItem('currentCharacter')
    router.push('/login')
  }
}

const showHelp = () => {
  alert('正在连接帮助中心数据库...\n(功能开发中)')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap');

.profile-page {
  width: 100%;
  min-height: 100vh;
  padding: 40px;
  position: relative;
  overflow-x: hidden;
  color: #e2e8f0;
  font-family: 'Rajdhani', sans-serif;
}

.bg-grid {
  display: none;
}

.game-bg {
  position: fixed;
  inset: 0;
  background-color: var(--bg-dark);
  background-image: 
    linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

.game-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, transparent 0%, var(--bg-dark) 90%);
  pointer-events: none;
}

.page-header {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 40px;
  z-index: 1;
}

.header-content h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: 0.05em;
  font-family: 'Rajdhani', sans-serif;
}

.subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 1px;
}

.profile-container {
  position: relative;
  max-width: 900px;
  margin: 0 auto;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* User Card */
.user-card {
  padding: 32px;
  display: flex;
  align-items: center;
  gap: 32px;
}

.avatar-wrapper {
  position: relative;
}

.avatar-circle {
  width: 96px;
  height: 96px;
  border-radius: 24px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: bold;
  color: white;
  box-shadow: 0 8px 24px rgba(59,130,246,0.3);
  font-family: 'Rajdhani', sans-serif;
}

.status-indicator {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 3px solid #1e293b;
}
.status-indicator.online { background: #10b981; box-shadow: 0 0 8px #10b981; }

.user-info { flex: 1; }

.username {
  font-size: 28px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 8px;
  font-family: 'Rajdhani', sans-serif;
}

.user-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.tag {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 2px;
  font-weight: 600;
  letter-spacing: 0.05em;
  font-family: 'Rajdhani', sans-serif;
}

.tag.mbti { background: rgba(139,92,246,0.15); color: #a78bfa; border: 1px solid rgba(139,92,246,0.2); }
.tag.id { background: rgba(148,163,184,0.15); color: #94a3b8; border: 1px solid rgba(148,163,184,0.2); font-family: 'JetBrains Mono', monospace; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(148,163,184,0.1);
}

.stat-item { display: flex; flex-direction: column; gap: 4px; }
.stat-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; font-family: 'Rajdhani', sans-serif; letter-spacing: 1px; }
.stat-value { font-size: 24px; font-weight: 700; font-family: 'Rajdhani', sans-serif; }
.stat-value.money { color: #34d399; text-shadow: 0 0 10px rgba(52, 211, 153, 0.3); }
.stat-value.trust { color: #60a5fa; text-shadow: 0 0 10px rgba(96, 165, 250, 0.3); }

/* Settings Grid */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.setting-section {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(148,163,184,0.1);
}

.section-icon { font-size: 20px; }
.section-title { font-size: 14px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-family: 'Rajdhani', sans-serif; }

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.setting-item:hover { background: rgba(255,255,255,0.05); }
.setting-item.danger-hover:hover { background: rgba(239,68,68,0.1); }
.setting-item.danger-hover:hover .item-name { color: #ef4444; }

.item-left { display: flex; align-items: center; gap: 16px; }
.item-icon { font-size: 20px; width: 24px; text-align: center; }
.item-content { display: flex; flex-direction: column; gap: 2px; }
.item-name { font-size: 15px; font-weight: 600; color: #e2e8f0; font-family: 'Rajdhani', sans-serif; }
.item-desc { font-size: 12px; color: #64748b; font-family: 'Rajdhani', sans-serif; }

.item-right { display: flex; align-items: center; gap: 8px; }
.item-value { font-size: 13px; color: #94a3b8; font-family: 'Rajdhani', sans-serif; }
.item-value.mono { font-family: 'JetBrains Mono', monospace; }
.arrow { color: #475569; font-size: 18px; }

/* Switch */
.switch { position: relative; width: 44px; height: 24px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #334155; transition: 0.3s; border-radius: 24px; }
.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: 0.3s; border-radius: 50%; }
input:checked + .slider { background: #3b82f6; }
input:checked + .slider:before { transform: translateX(20px); }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-content {
  width: 100%;
  max-width: 500px;
  padding: 32px;
  background: #1e293b;
  border: 1px solid rgba(59,130,246,0.2);
}

.modal-header { margin-bottom: 24px; text-align: center; }
.modal-header h3 { margin: 0 0 8px 0; color: #e2e8f0; font-size: 20px; font-family: 'Rajdhani', sans-serif; }
.modal-header p { margin: 0; color: #94a3b8; font-size: 13px; font-family: 'Rajdhani', sans-serif; }

.theme-options { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }

.theme-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 4px;
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(148,163,184,0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.theme-option:hover { background: rgba(30,41,59,0.8); border-color: rgba(59,130,246,0.3); }
.theme-option.active { background: rgba(59,130,246,0.1); border-color: #3b82f6; }

.theme-preview {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-dot { width: 12px; height: 12px; background: white; border-radius: 50%; opacity: 0.8; }

.theme-info { flex: 1; }
.theme-name { font-size: 14px; font-weight: 600; color: #e2e8f0; font-family: 'Rajdhani', sans-serif; }
.theme-key { font-size: 10px; color: #64748b; font-weight: 700; font-family: 'Rajdhani', sans-serif; }

.active-indicator { color: #3b82f6; font-size: 12px; }

/* Tech Border Effect */
.tech-border {
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
  position: relative;
}

.tech-border::after {
  content: '';
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 10px;
  height: 10px;
  border-bottom: 2px solid #3b82f6;
  border-right: 2px solid #3b82f6;
}

.tech-border::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  width: 10px;
  height: 10px;
  border-top: 2px solid #3b82f6;
  border-left: 2px solid #3b82f6;
}

/* Transitions */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
