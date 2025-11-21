<template>
  <div class="terminal-layout" :data-theme="themeStore.isDark ? 'dark' : 'light'">
    <div class="grid-bg"></div>
    <div class="crt-overlay"></div>
    
    <!-- 左侧侧边栏 -->
    <aside class="sidebar">
      <div class="logo-area">
        <div class="logo-icon">◎</div>
        <div class="logo-text">
          <div>PROJECT</div>
          <div class="logo-sub">ECHO</div>
        </div>
      </div>
      
      <div class="classified-tag">// CLASSIFIED LOG</div>

      <nav class="nav-menu">
        <div class="nav-group-title">DIRECTORY</div>
        
        <a v-for="item in menuItems" 
           :key="item.id"
           class="nav-item"
           :class="{ active: currentView === item.id }"
           @click="$emit('change-view', item.id)">
          <span class="icon">{{ item.icon }}</span>
          <span class="label">{{ item.label }}</span>
          <span class="active-indicator" v-if="currentView === item.id">_</span>
        </a>
      </nav>

      <div class="system-config">
        <div class="config-header">SYSTEM CONFIG</div>
        <div class="config-item">
          <span>🔊 BGM</span>
          <div class="status-indicator on">ON</div>
        </div>
        <div class="config-item" @click="themeStore.toggleTheme()">
          <span>☀ MODE</span>
          <div class="status-indicator">{{ themeStore.isDark ? 'DARK' : 'LIGHT' }}</div>
        </div>
      </div>
      
      <div class="version-info">
        STATUS: <span class="status-ok">ARCHIVED</span><br>
        VER: 0.9.5-ALPHA
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <header class="top-bar">
        <div class="breadcrumbs">
          PROJECT ECHO <span class="divider">/</span> THE SINGULARITY LOG
        </div>
        <div class="device-info">
          DEVICE: TERMINAL_01 <span class="blink">_</span>
        </div>
      </header>

      <div class="content-scroll-area custom-scrollbar">
        <slot></slot>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useThemeStore } from '../../stores/theme'

const themeStore = useThemeStore()

defineProps({
  currentView: String
})

defineEmits(['change-view'])

const menuItems = [
  { id: 'profile', label: '大纲 & 人设', icon: '📂' },
  { id: 'dashboard', label: '主角状态', icon: '👤' },
  { id: 'timeline', label: '时间线', icon: '🕒' },
  { id: 'world', label: '世界观构建', icon: '🌐' },
  { id: 'chat', label: '与 ECHO 对话', icon: '💬' }
]
</script>

<style scoped>
.terminal-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  background-color: var(--term-bg);
  color: var(--term-text);
}

/* Sidebar Styles */
.sidebar {
  width: var(--sidebar-width);
  background-color: var(--sidebar-bg);
  color: var(--sidebar-text);
  display: flex;
  flex-direction: column;
  border-right: 4px solid var(--term-accent);
  flex-shrink: 0;
  z-index: 10;
}

.logo-area {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--term-accent);
}

.logo-icon {
  font-size: 32px;
  font-weight: bold;
}

.logo-text {
  font-weight: 800;
  line-height: 1;
  letter-spacing: 1px;
}

.logo-sub {
  font-size: 20px;
}

.classified-tag {
  background: var(--term-accent);
  color: #000;
  font-size: 10px;
  padding: 4px 24px;
  font-weight: bold;
  letter-spacing: 2px;
}

.nav-menu {
  padding: 24px 12px;
  flex: 1;
}

.nav-group-title {
  font-size: 10px;
  text-transform: uppercase;
  margin-bottom: 12px;
  padding-left: 12px;
  opacity: 0.6;
  letter-spacing: 1px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 8px;
  cursor: pointer;
  border: 1px solid rgba(255,255,255,0.1);
  transition: all 0.2s;
  font-size: 13px;
  font-weight: 600;
}

.nav-item:hover {
  border-color: #FFF;
  color: #FFF;
}

.nav-item.active {
  background-color: #FFF;
  color: #000;
  border-color: #FFF;
}

[data-theme='dark'] .nav-item.active {
  background-color: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

/* System Config */
.system-config {
  padding: 20px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.config-header {
  font-size: 10px;
  margin-bottom: 12px;
  opacity: 0.6;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 11px;
  cursor: pointer;
  padding: 4px 0;
}

.status-indicator {
  background: #333;
  padding: 2px 8px;
  border-radius: 2px;
  font-size: 10px;
}

.status-indicator.on {
  background: var(--term-accent);
  color: #000;
}

.version-info {
  padding: 12px 24px;
  font-size: 10px;
  opacity: 0.4;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.status-ok {
  color: #4CAF50;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.top-bar {
  height: 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  font-family: var(--font-mono);
  font-size: 12px;
  border-bottom: 1px solid rgba(0,0,0,0.1);
  background: rgba(255,255,255,0.5);
}

[data-theme='dark'] .top-bar {
  border-bottom-color: var(--term-accent);
  background: rgba(0,0,0,0.2);
}

.divider {
  color: var(--term-accent);
  margin: 0 8px;
}

.blink {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.content-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 40px;
}
</style>
