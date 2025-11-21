<template>
  <div class="project-echo-interface">
    <!-- Left Sidebar: Directory -->
    <nav class="sidebar-nav">
      <div class="nav-header">
        <div class="logo-text">ECHOPOLIS</div>
        <div class="sub-header">// 系统终端</div>
      </div>
      
      <div class="nav-section">
        <div class="section-label">目录</div>
        <div 
          v-for="item in navItems" 
          :key="item.id"
          :class="['nav-item', { active: currentView === item.id }]"
          @click="currentView = item.id">
          <span class="icon">{{ item.icon }}</span>
          {{ item.label }}
        </div>
      </div>

      <div class="nav-spacer"></div>

      <div class="system-config">
        <div class="section-label">系统配置</div>
        <div class="config-grid">
          <button class="config-btn orange active">
            <span class="icon">🔊</span> BGM: 开
          </button>
          <button class="config-btn green active">
            <span class="icon">📺</span> CRT: 开
          </button>
          <button class="config-btn white" @click="themeStore.toggleTheme">
            <span class="icon">☀</span> 模式: {{ themeStore.isDark ? '暗色' : '亮色' }}
          </button>
          <button class="config-btn yellow">
            <span class="icon">文</span> CN | EN
          </button>
        </div>
      </div>
    </nav>

    <!-- Main Content Area -->
    <main class="main-content">
      <!-- Top Header -->
      <header class="top-bar">
        <div class="brand-logo">
          <span class="highlight">ECHOPOLIS</span> // 系统
        </div>
        <div class="header-meta">
          <span>记录日期: 2025-11-22</span>
        </div>
      </header>

      <!-- Game View Layer -->
      <div class="game-viewport" v-show="currentView === 'city'">
        <!-- City Background -->
        <section class="city-stage" @mousemove="onParallax" @mouseleave="resetParallax">
          <div class="city-sky" :style="parallaxStyles.sky" />
          <div class="city-grid" :style="parallaxStyles.grid" />
          
          <!-- Map Decorations (SVG Layer) -->
          <svg class="city-connections" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(0,0,0,0.05)" stroke-width="1"/>
              </pattern>
            </defs>
            <!-- Connection Lines -->
            <g stroke="rgba(0,0,0,0.1)" stroke-width="2" fill="none" stroke-dasharray="4 4">
              <!-- Central Hub Connections -->
              <path d="M 30% 35% L 50% 45%" /> <!-- Learning -> Finance -->
              <path d="M 70% 35% L 50% 45%" /> <!-- Tech -> Finance -->
              <path d="M 30% 65% L 50% 45%" /> <!-- Green -> Finance -->
              <path d="M 70% 65% L 50% 45%" /> <!-- Housing -> Finance -->
              <path d="M 50% 70% L 50% 45%" /> <!-- Leisure -> Finance -->
              
              <!-- Outer Ring -->
              <path d="M 30% 35% L 70% 35%" /> <!-- Learning -> Tech -->
              <path d="M 30% 65% L 50% 70% L 70% 65%" /> <!-- Green -> Leisure -> Housing -->
              <path d="M 30% 35% L 30% 65%" /> <!-- Learning -> Green -->
              <path d="M 70% 35% L 70% 65%" /> <!-- Tech -> Housing -->
            </g>
            
            <!-- Zone Circles -->
            <circle cx="50%" cy="45%" r="120" fill="none" stroke="rgba(0,0,0,0.03)" stroke-width="1" />
            <circle cx="50%" cy="45%" r="250" fill="none" stroke="rgba(0,0,0,0.02)" stroke-width="1" stroke-dasharray="10 5" />
          </svg>

          <div class="city-layer city-layer--far" :style="parallaxStyles.far" />
          <div class="city-layer city-layer--mid" :style="parallaxStyles.mid" />
          <div class="city-layer city-layer--front" :style="parallaxStyles.front" />
          
          <!-- District Markers -->
          <div class="district-marker"
               v-for="district in districts"
               :key="district.id"
               :style="pinStyle(district)"
               @click="handleZoneSelect(district)">
            <div class="marker-box">
              <span class="marker-code">{{ getDistrictCode(district.id) }}</span>
              <div class="marker-corner"></div>
            </div>
            <div class="marker-label">
              {{ district.name }}
            </div>
          </div>
        </section>

        <!-- HUD Overlay (Floating Cards) -->
        <div class="hud-overlay">
          <!-- Left: Avatar Status -->
          <div class="hud-column left">
            <div class="archive-card">
              <div class="archive-header">
                <span>主体状态</span>
                <span>ID_001</span>
              </div>
              <div class="archive-body">
                <div class="avatar-row">
                  <div class="avatar-face">
                    <div class="eye left"></div>
                    <div class="eye right"></div>
                    <div class="mouth"></div>
                  </div>
                  <div class="avatar-details">
                    <h3>{{ avatar?.name || 'Echo' }}</h3>
                    <div class="tags">
                      <span class="tag">{{ avatar?.mbti_type || 'INTJ' }}</span>
                      <span class="tag">Lv.{{ Math.floor((avatar?.current_month || 0)/12) + 1 }}</span>
                    </div>
                  </div>
                </div>
                <div class="stat-list">
                  <div class="stat-item">
                    <label>总资产</label>
                    <span class="value">¥{{ formatNumber(assets.total) }}</span>
                  </div>
                  <div class="stat-item">
                    <label>现金流</label>
                    <span class="value">¥{{ formatNumber(assets.cash) }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="archive-card">
              <div class="archive-header">AI 思考</div>
              <div class="archive-body">
                <p class="mono-text">{{ aiReflection || '系统等待输入...' }}</p>
              </div>
            </div>
          </div>

          <!-- Right: Mission Control -->
          <div class="hud-column right">
            <div class="archive-card highlight flex-grow-card">
              <div class="archive-header">
                <span>当前指令</span>
                <span class="blink">执行中</span>
              </div>
              <div class="archive-body scrollable-body">
                <h3 class="mission-title">{{ currentSituation?.title || '等待事件' }}</h3>
                <p class="mission-desc">{{ currentSituation?.description || '当前扇区未检测到异常活动。' }}</p>
                
                <div class="ai-log" v-if="currentSituation?.ai_thoughts">
                  <span class="prefix">> AI 分析:</span> {{ currentSituation.ai_thoughts }}
                </div>

                <div class="action-grid" v-if="situationOptions?.length">
                  <button 
                    v-for="(option, idx) in situationOptions" 
                    :key="idx"
                    class="term-btn"
                    @click="handleSelectOption(idx)">
                    [{{ idx + 1 }}] {{ option }}
                  </button>
                </div>

                <div class="control-bar">
                  <button class="term-btn primary full" :disabled="gameStore.isAdvancingMonth" @click="handleAdvance">
                    {{ gameStore.isAdvancingMonth ? '处理中...' : '>> 执行下一周期' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Echo Input -->
            <div class="archive-card fixed-height-card">
              <div class="archive-header">
                <span>注入意识</span>
                <span class="help-icon" title="向AI植入潜意识，影响其性格与决策倾向">?</span>
              </div>
              <div class="archive-body">
                <div class="echo-types">
                  <span 
                    v-for="type in echoTypes" 
                    :key="type.value"
                    @click="echoType = type.value"
                    :class="['type-tag', { active: echoType === type.value }]">
                    {{ type.label }}
                  </span>
                </div>
                <textarea 
                  v-model="echoText" 
                  class="term-input" 
                  placeholder="输入引导参数 (例如: '激进一点', '关注科技股')..."></textarea>
                <button class="term-btn full" @click="handleSendEcho">发送指引 // UPLOAD</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Bottom: Chat -->
        <div class="chat-dock">
          <!-- Chat History Panel -->
          <div class="chat-history" v-if="chatMessages.length > 0" :class="{ collapsed: !isChatExpanded }">
             <div class="chat-header" @click="isChatExpanded = !isChatExpanded">
               <span>通讯记录 // COMMS_LOG</span>
               <span class="toggle-icon">{{ isChatExpanded ? '▼' : '▲' }}</span>
             </div>
             <div class="chat-body" ref="chatBodyRef">
               <div v-for="(msg, idx) in chatMessages" :key="idx" :class="['chat-msg', msg.role]">
                  <span class="role">[{{ msg.role === 'user' ? 'USER' : 'ECHO' }}]:</span>
                  <span class="text">{{ msg.text }}</span>
               </div>
             </div>
          </div>

          <div class="cmd-interface">
            <span class="prompt">用户@ECHO:~$</span>
            <input 
              v-model="chatText" 
              type="text" 
              class="cmd-input" 
              placeholder="输入指令..." 
              @keyup.enter="sendChat"
            />
          </div>
        </div>
      </div>

      <!-- Placeholder for other views (Timeline, World, etc.) -->
      <div class="view-placeholder" v-if="currentView !== 'city'">
        <ProfileView v-if="currentView === 'profile'" />
        <TimelineView v-if="currentView === 'timeline'" />
        <WorldView v-if="currentView === 'world'" />
        <ArchivesView v-if="currentView === 'logs'" />
      </div>

    </main>

    <!-- CRT Overlay -->
    <div class="crt-overlay"></div>
    <div class="grid-bg"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useGameStore } from '../stores/game'
import { useThemeStore } from '../stores/theme'
import ProfileView from '../components/views/ProfileView.vue'
import TimelineView from '../components/views/TimelineView.vue'
import WorldView from '../components/views/WorldView.vue'
import ArchivesView from '../components/views/ArchivesView.vue'

const gameStore = useGameStore()
const themeStore = useThemeStore()
const currentView = ref('city')
const parallax = ref({ x: 0, y: 0 })
const chatText = ref('')
const echoText = ref('')
const echoType = ref('advisory')
const isChatExpanded = ref(true)
const chatBodyRef = ref(null)

const navItems = [
  { id: 'city', label: '城市概览', icon: '⚡' },
  { id: 'profile', label: '主体数据', icon: '👤' },
  { id: 'timeline', label: '时间线', icon: '🕒' },
  { id: 'world', label: '世界构建', icon: '🌐' },
  { id: 'logs', label: '档案库', icon: '📖' }
]

const echoTypes = [
  { value: 'inspirational', label: '激励' },
  { value: 'advisory', label: '建议' },
  { value: 'directive', label: '指令' },
  { value: 'emotional', label: '共情' }
]

// Data Mapping
const avatar = computed(() => gameStore.avatar)
const assets = computed(() => ({
  total: gameStore.assets?.total ?? 0,
  cash: gameStore.assets?.cash ?? 0
}))
const districts = computed(() => gameStore.districts)
const aiReflection = computed(() => gameStore.aiReflection)
const currentSituation = computed(() => gameStore.currentSituation)
const situationOptions = computed(() => gameStore.situationOptions)
const chatMessages = computed(() => gameStore.chatMessages)

const formatNumber = (num) => Number(num || 0).toLocaleString('zh-CN')

const getDistrictCode = (id) => {
  const map = {
    finance: 'FIN',
    tech: 'TEC',
    housing: 'EST',
    learning: 'EDU',
    leisure: 'ENT',
    green: 'NRG'
  }
  return map[id] || 'UNK'
}

// Parallax Logic
const parallaxStyles = computed(() => {
  const { x, y } = parallax.value
  const make = (mult) => ({ transform: `translate3d(${x * mult}px, ${y * mult}px, 0)` })
  return {
    sky: make(10),
    grid: make(15),
    far: make(20),
    mid: make(30),
    front: make(40)
  }
})

const pinStyle = (district) => {
  const x = district.coords?.x ?? 50
  const y = district.coords?.y ?? 50
  return { left: `${x}%`, top: `${y}%` }
}

const onParallax = (event) => {
  const rect = event.currentTarget.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 2
  const offsetX = (event.clientX - centerX) / rect.width
  const offsetY = (event.clientY - centerY) / rect.height
  parallax.value = { x: offsetX, y: offsetY }
}

const resetParallax = () => {
  parallax.value = { x: 0, y: 0 }
}

// Actions
const handleAdvance = async () => {
  try {
    const text = echoText.value
    echoText.value = '' // Clear immediately
    await gameStore.advanceMonth(text)
  } catch (e) { console.error(e) }
}

const handleSelectOption = async (idx) => {
  await gameStore.makeDecision(idx)
}

const handleSendEcho = async () => {
  if (!echoText.value) return
  const text = echoText.value
  echoText.value = '' // Clear immediately
  await gameStore.sendEcho(text, echoType.value)
}

const sendChat = async () => {
  if (!chatText.value) return
  const text = chatText.value
  chatText.value = '' // Clear immediately
  await gameStore.talkToAI(text)
}

const handleZoneSelect = (district) => {
  gameStore.exploreDistrict(district.id)
}

// Auto-scroll chat
watch(chatMessages, async () => {
  await nextTick()
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}, { deep: true })

onMounted(async () => {
  themeStore.applyTheme()
  await gameStore.bootstrapHome()
})
</script>

<style scoped>
.project-echo-interface {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: var(--term-bg);
  color: var(--term-text);
}

/* Sidebar */
.sidebar-nav {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.nav-section {
  padding-top: 20px;
}

.nav-header {
  /* Removed local styles to use terminal-theme.css */
}

.logo-text {
  /* Removed local styles */
}

.sub-header {
  /* Removed local styles */
}

.nav-spacer {
  flex: 1;
}

.system-config {
  padding: 24px;
  border-top: 2px solid var(--term-border);
}

.config-header {
  font-size: 10px;
  margin-bottom: 12px;
  color: var(--term-text-secondary);
}

.config-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 11px;
  font-weight: 700;
}

.config-row.clickable {
  cursor: pointer;
}

.config-row.clickable:hover {
  color: var(--term-accent);
}

.status-badge {
  background: #333;
  color: #fff;
  padding: 2px 6px;
  font-size: 10px;
}

.status-badge.on {
  background: var(--term-accent);
  color: #000;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.header-meta {
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  display: flex;
  gap: 20px;
  opacity: 0.7;
}

/* Game Viewport */
.game-viewport {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.city-stage {
  position: absolute;
  inset: 0;
  background: transparent;
}

/* Reusing city styles */
.city-sky { 
  /* Placeholder for sky styles if needed */
}
.city-grid {
  position: absolute;
  inset: -50%;
  width: 200%;
  height: 200%;
  background-image: 
    linear-gradient(var(--term-accent-glow) 1px, transparent 1px),
    linear-gradient(90deg, var(--term-accent-glow) 1px, transparent 1px);
  background-size: 80px 80px;
  transform: perspective(500px) rotateX(60deg);
  opacity: 0.4;
}

.city-layer {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
}

.city-connections {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

/* District Markers */
.district-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.marker-box {
  width: 42px;
  height: 42px;
  background: var(--term-bg);
  border: 2px solid var(--term-text);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  box-shadow: 4px 4px 0 rgba(0,0,0,0.1);
}

.marker-code {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 900;
  font-size: 12px;
  color: var(--term-text);
  letter-spacing: 1px;
}

.marker-corner {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 6px;
  height: 6px;
  background: var(--term-text);
  transition: background 0.2s;
}

.marker-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  color: var(--term-text-secondary);
  background: var(--term-panel-bg);
  padding: 4px 8px;
  border: 1px solid var(--term-border);
  opacity: 0.9;
  transition: all 0.2s;
  white-space: nowrap;
  box-shadow: 2px 2px 0 rgba(0,0,0,0.05);
}

/* Hover Effects */
.district-marker:hover .marker-box {
  background: var(--term-accent);
  border-color: var(--term-text);
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 rgba(0,0,0,0.2);
}

.district-marker:hover .marker-code {
  color: #000;
}

.district-marker:hover .marker-corner {
  background: #000;
}

.district-marker:hover .marker-label {
  opacity: 1;
  color: var(--term-text);
  border-color: var(--term-accent);
  transform: translateY(2px);
}

/* HUD Overlay */
.hud-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  padding: 32px 40px;
  display: flex;
  justify-content: space-between;
}

.hud-column {
  width: 320px;
  pointer-events: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-height: 100%; /* Ensure column doesn't exceed parent height */
}

.flex-grow-card {
  flex: 1;
  min-height: 0; /* Allow shrinking */
  display: flex;
  flex-direction: column;
}

.fixed-height-card {
  flex-shrink: 0; /* Prevent shrinking */
}

.scrollable-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px; /* Move padding here from .archive-body */
}

/* Avatar Styles */
.avatar-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.avatar-face {
  width: 64px;
  height: 64px;
  background: var(--term-accent);
  border: 2px solid #000;
  position: relative;
}

.avatar-face .eye {
  position: absolute;
  top: 24px;
  width: 8px;
  height: 8px;
  background: #000;
}
.avatar-face .eye.left { left: 14px; }
.avatar-face .eye.right { right: 14px; }
.avatar-face .mouth {
  position: absolute;
  bottom: 14px;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 4px;
  background: #000;
}

.avatar-details h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 900;
}

.tags {
  display: flex;
  gap: 8px;
}

.tag {
  background: var(--term-border);
  color: var(--term-bg);
  padding: 2px 6px;
  font-size: 10px;
  font-weight: bold;
}

.stat-list {
  display: grid;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  border-bottom: 1px dashed var(--term-border);
  padding-bottom: 4px;
}

.stat-item label {
  font-weight: 700;
  color: var(--term-text-secondary);
}

/* Mission Styles */
.mission-title {
  font-size: 16px;
  font-weight: 900;
  margin: 0 0 8px 0;
  color: var(--term-accent);
}

.mission-desc {
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 16px;
}

.ai-log {
  background: rgba(0,0,0,0.05);
  border-left: 4px solid var(--term-accent);
  padding: 10px;
  font-size: 11px;
  margin-bottom: 16px;
  font-style: italic;
}

.prefix {
  font-weight: bold;
  color: var(--term-accent);
  font-style: normal;
}

.action-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.full {
  width: 100%;
}

/* Echo Input */
.echo-types {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.type-tag {
  border: 1px solid var(--term-border);
  padding: 4px 8px;
  font-size: 10px;
  cursor: pointer;
  font-weight: 700;
}

.type-tag.active {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

.term-input {
  width: 100%;
  background: transparent;
  border: 2px solid var(--term-border);
  padding: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  margin-bottom: 8px;
  min-height: 60px;
  color: var(--term-text);
}

/* Chat Dock */
.chat-dock {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  max-width: 90%;
  pointer-events: auto;
  display: flex;
  flex-direction: column;
  gap: 12px; /* Add gap between history and input */
}

.chat-history {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  box-shadow: 6px 6px 0px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  transition: height 0.3s ease;
  height: 200px;
  overflow: hidden;
}

.chat-history.collapsed {
  height: 36px; /* Only header height */
  border-bottom: 2px solid var(--term-border);
}

.chat-header {
  background: transparent;
  border-bottom: 2px solid var(--term-border);
  padding: 8px 12px;
  font-weight: 800;
  font-size: 10px;
  color: var(--term-text-secondary);
  text-transform: uppercase;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
}

.chat-header:hover {
  background: rgba(0,0,0,0.05);
}

.toggle-icon {
  font-size: 10px;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.help-icon {
  cursor: help;
  border: 1px solid var(--term-text-secondary);
  border-radius: 50%;
  width: 14px;
  height: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--term-text-secondary);
}

.chat-msg {
  line-height: 1.4;
  word-break: break-word;
}

.chat-msg .role {
  font-weight: bold;
  margin-right: 8px;
  opacity: 0.7;
}

.chat-msg.user {
  color: var(--term-text-secondary);
}

.chat-msg.ai {
  color: var(--term-accent);
}

.chat-msg.system {
  color: var(--term-error);
}

.cmd-interface {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  padding: 12px;
  display: flex;
  align-items: center;
  box-shadow: 6px 6px 0px rgba(0,0,0,0.15);
  z-index: 20;
}

.prompt {
  color: var(--term-accent);
  font-weight: 900;
  margin-right: 12px;
}

.cmd-input {
  flex: 1;
  background: transparent;
  border: none;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  color: var(--term-text);
}

.cmd-input:focus {
  outline: none;
}

.view-placeholder {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.blink {
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

/* Sidebar Updates */
.section-label {
  font-size: 10px;
  font-weight: 900;
  color: var(--term-text-secondary);
  margin-bottom: 8px;
  padding-left: 4px;
}

.config-grid {
  display: grid;
  gap: 8px;
}

.config-btn {
  border: 2px solid var(--term-border);
  padding: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  text-transform: uppercase;
  box-shadow: 2px 2px 0px rgba(0,0,0,0.1);
  transition: all 0.1s;
}

.config-btn:hover {
  transform: translate(-1px, -1px);
  box-shadow: 4px 4px 0px rgba(0,0,0,0.1);
}

.config-btn:active {
  transform: translate(1px, 1px);
  box-shadow: 0px 0px 0px;
}

.config-btn.orange { background: var(--term-accent); color: #000; }
.config-btn.green { background: var(--term-success); color: #000; }
.config-btn.yellow { background: var(--term-accent-secondary); color: #000; }
.config-btn.white { background: #fff; color: #000; }

/* Header Updates */
.meta-tag {
  padding: 4px 8px;
  font-weight: 800;
  font-size: 10px;
  border: 2px solid var(--term-border);
  box-shadow: 2px 2px 0px rgba(0,0,0,0.1);
}

.meta-tag.yellow {
  background: var(--term-accent-secondary);
  color: #000;
}
</style>
