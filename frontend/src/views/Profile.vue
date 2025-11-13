<template>
  <div class="profile-page">
    <div class="page-header">
      <h1>👤 我的</h1>
      <button class="back-btn" @click="$router.push('/home')">返回首页</button>
    </div>

    <div class="profile-container">
      <!-- 用户信息卡片 -->
      <div class="user-card">
        <div class="avatar-circle">{{ avatar?.name?.charAt(0) || 'U' }}</div>
        <div class="user-info">
          <div class="username">{{ avatar?.name || '用户' }}</div>
          <div class="mbti">{{ avatar?.mbti_type || 'INTJ' }} 人格</div>
          <div class="stats">
            <span>💰 ¥{{ formatNumber(avatar?.total_assets || 0) }}</span>
            <span>🤝 信任值 {{ avatar?.trust_level || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- 设置列表 -->
      <div class="settings-list">
        <div class="setting-section">
          <div class="section-title">游戏设置</div>
          
          <div class="setting-item" @click="showThemeModal = true">
            <div class="item-left">
              <span class="item-icon">🎨</span>
              <span class="item-name">主题色调</span>
            </div>
            <span class="item-value">{{ currentThemeName }} ›</span>
          </div>

          <div class="setting-item">
            <div class="item-left">
              <span class="item-icon">🔔</span>
              <span class="item-name">消息通知</span>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="settings.notification">
              <span class="slider"></span>
            </label>
          </div>

          <div class="setting-item">
            <div class="item-left">
              <span class="item-icon">🔊</span>
              <span class="item-name">音效</span>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="settings.sound">
              <span class="slider"></span>
            </label>
          </div>
        </div>

        <div class="setting-section">
          <div class="section-title">账户管理</div>
          
          <div class="setting-item" @click="resetGame">
            <div class="item-left">
              <span class="item-icon">🔄</span>
              <span class="item-name">重置游戏</span>
            </div>
            <span class="item-value">›</span>
          </div>

          <div class="setting-item" @click="exportData">
            <div class="item-left">
              <span class="item-icon">📤</span>
              <span class="item-name">导出数据</span>
            </div>
            <span class="item-value">›</span>
          </div>

          <div class="setting-item" @click="logout">
            <div class="item-left">
              <span class="item-icon">🚪</span>
              <span class="item-name">退出登录</span>
            </div>
            <span class="item-value">›</span>
          </div>
        </div>

        <div class="setting-section">
          <div class="section-title">关于</div>
          
          <div class="setting-item">
            <div class="item-left">
              <span class="item-icon">ℹ️</span>
              <span class="item-name">版本信息</span>
            </div>
            <span class="item-value">v1.0.0</span>
          </div>

          <div class="setting-item" @click="showHelp">
            <div class="item-left">
              <span class="item-icon">❓</span>
              <span class="item-name">帮助中心</span>
            </div>
            <span class="item-value">›</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主题选择弹窗 -->
    <div v-if="showThemeModal" class="modal" @click="showThemeModal = false">
      <div class="modal-content" @click.stop>
        <h3>选择主题</h3>
        <div class="theme-options">
          <div 
            v-for="(theme, key) in themeStore.themes" 
            :key="key"
            class="theme-option"
            :class="{ active: themeStore.currentTheme === key }"
            @click="selectTheme(key)"
          >
            <div class="theme-preview" :style="{ background: theme.background }"></div>
            <div class="theme-name">{{ theme.name }}</div>
          </div>
        </div>
      </div>
    </div>
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

const selectTheme = (key) => {
  themeStore.setTheme(key)
  showThemeModal.value = false
}

const resetGame = () => {
  if (confirm('确定要重置游戏吗？所有数据将被清空！')) {
    console.log('重置游戏')
    // TODO: 调用API重置游戏
  }
}

const exportData = () => {
  console.log('导出数据')
  // TODO: 导出游戏数据
  alert('数据导出功能开发中...')
}

const logout = () => {
  if (confirm('确定要退出登录吗？')) {
    console.log('退出登录')
    // TODO: 清除登录状态
    router.push('/login')
  }
}

const showHelp = () => {
  alert('帮助中心开发中...')
}
</script>

<style scoped>
.profile-page {
  width: 100%;
  min-height: 100vh;
  padding: 40px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: white;
  font-size: 32px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.back-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  background: rgba(255,255,255,0.9);
  color: #ff9a9e;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: white;
  transform: translateY(-2px);
}

.profile-container {
  max-width: 800px;
  margin: 0 auto;
}

.user-card {
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 30px;
  display: flex;
  align-items: center;
  gap: 25px;
  margin-bottom: 30px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: bold;
  color: white;
}

.user-info {
  flex: 1;
}

.username {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.mbti {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
}

.stats {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #ff9a9e;
  font-weight: bold;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-section {
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.section-title {
  font-size: 14px;
  color: #999;
  font-weight: bold;
  margin-bottom: 15px;
  padding-left: 10px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 10px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item:hover {
  background: rgba(255,154,158,0.05);
  border-radius: 10px;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.item-icon {
  font-size: 24px;
}

.item-name {
  font-size: 16px;
  color: #333;
}

.item-value {
  font-size: 14px;
  color: #999;
}

.switch {
  position: relative;
  width: 50px;
  height: 26px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 26px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

input:checked + .slider:before {
  transform: translateX(24px);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
}

.modal-content h3 {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.theme-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.theme-option {
  padding: 15px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  text-align: center;
}

.theme-option:hover {
  border-color: #ff9a9e;
}

.theme-option.active {
  border-color: #ff9a9e;
  background: rgba(255,154,158,0.1);
}

.theme-preview {
  height: 60px;
  border-radius: 8px;
  margin-bottom: 10px;
}

.theme-name {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}
</style>
