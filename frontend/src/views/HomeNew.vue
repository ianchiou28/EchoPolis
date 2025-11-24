<template>
  <div class="project-echo-interface">
    <!-- Mobile Sidebar Overlay -->
    <div class="sidebar-overlay" v-if="isSidebarOpen" @click="isSidebarOpen = false"></div>

    <!-- Left Sidebar: Directory -->
    <nav class="sidebar-nav" :class="{ open: isSidebarOpen }">
      <div class="nav-header">
        <div class="logo-text">FinAI金融模拟沙盘</div>
        <div class="sub-header">// 系统终端</div>
        <button class="close-sidebar-btn" @click="isSidebarOpen = false">×</button>
      </div>
      
      <div class="nav-section">
        <div class="section-label">目录</div>
        <div 
          v-for="item in navItems" 
          :key="item.id"
          :class="['nav-item', { active: currentView === item.id }]"
          @click="handleNavClick(item.id)">
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
          <button class="config-btn green" :class="{ active: isCrtOn }" @click="toggleCrt">
            <span class="icon">📺</span> CRT: {{ isCrtOn ? '开' : '关' }}
          </button>
          <button class="config-btn white" @click="themeStore.toggleTheme">
            <span class="icon">☀</span> 模式: {{ themeStore.isDark ? '暗色' : '亮色' }}
          </button>
          <button class="config-btn yellow">
            <span class="icon">文</span> CN | EN
          </button>
          <button class="config-btn red" @click="exitToSelect">
            <span class="icon">🔌</span> 断开连接
          </button>
        </div>
      </div>
    </nav>

    <!-- Main Content Area -->
    <main class="main-content">
      <!-- Top Header -->
      <header class="top-bar">
        <button class="menu-btn" @click="isSidebarOpen = true">☰</button>
        <div class="brand-logo">
          <span class="highlight">FinAI</span> // 系统
        </div>
        <div class="header-meta">
          <span>{{ currentDate }}</span>
        </div>
      </header>

      <!-- Game View Layer -->
      <div class="game-viewport" v-show="currentView === 'city'">
        
        <!-- Mobile View Switcher -->
        <div class="mobile-view-switch">
          <button 
            :class="['switch-btn', { active: !mobileMapMode }]" 
            @click="mobileMapMode = false">
            📊 仪表盘
          </button>
          <button 
            :class="['switch-btn', { active: mobileMapMode }]" 
            @click="mobileMapMode = true">
            🗺️ 城市地图
          </button>
        </div>

        <!-- City Background (Map) -->
        <section class="city-stage" :class="{ 'mobile-hidden': !mobileMapMode }" @mousemove="onParallax" @mouseleave="resetParallax">
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
            <g v-if="!isMobile" stroke="rgba(0,0,0,0.1)" stroke-width="2" fill="none" stroke-dasharray="4 4">
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

            <g v-else stroke="rgba(0,0,0,0.1)" stroke-width="2" fill="none" stroke-dasharray="4 4">
               <!-- Mobile Hexagon Connections -->
               <path d="M 50% 20% L 25% 38%" />
               <path d="M 50% 20% L 75% 38%" />
               <path d="M 25% 38% L 25% 62%" />
               <path d="M 75% 38% L 75% 62%" />
               <path d="M 25% 62% L 50% 80%" />
               <path d="M 75% 62% L 50% 80%" />
               <path d="M 25% 38% L 75% 38%" />
               <path d="M 25% 62% L 75% 62%" />
            </g>
            
            <!-- Zone Circles -->
            <circle cx="50%" cy="45%" r="120" fill="none" stroke="rgba(0,0,0,0.03)" stroke-width="1" />
            <circle cx="50%" cy="45%" r="250" fill="none" stroke="rgba(0,0,0,0.02)" stroke-width="1" stroke-dasharray="10 5" />
          </svg>

          <!-- District Markers (Pixel Art Buildings) -->
          <div class="district-marker"
               v-for="district in districts"
               :key="district.id"
               :style="pinStyle(district)"
               @click="handleZoneSelect(district)">
            <div class="district-visual">
              <img :src="`/assets/districts/${district.id}.png`" 
                   class="pixel-building" 
                   :style="{ animationDelay: `${(district.id.length % 3) * 0.5}s` }"
                   :alt="district.name"
                   @error="$event.target.style.display='none'" />
              <!-- Fallback Marker if image fails or loading -->
              <div class="marker-box fallback">
                <span class="marker-code">{{ getDistrictCode(district.id) }}</span>
                <div class="marker-corner"></div>
              </div>
            </div>
            <div class="marker-label">
              {{ district.name }}
            </div>
          </div>
        </section>

        <!-- Action Panel Overlay -->
        <DistrictActionPanel 
          v-if="selectedDistrict" 
          :district="selectedDistrict" 
          @close="selectedDistrict = null" 
        />

        <!-- HUD Overlay (Floating Cards) -->
        <div class="hud-overlay" :class="{ 'mobile-hidden': mobileMapMode }">
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
                    :class="{ active: selectedOptionIndex === idx }"
                    @click="handleSelectOption(idx)">
                    [{{ idx + 1 }}] {{ option }}
                  </button>
                </div>

                <div class="control-bar">
                  <button class="term-btn primary full" :disabled="gameStore.isAdvancingMonth || isProcessing" @click="handleAdvance">
                    {{ (gameStore.isAdvancingMonth || isProcessing) ? '处理中...' : '>> 执行下一周期' }}
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
        <div class="chat-dock" :class="{ 'mobile-hidden': mobileMapMode }">
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
            <button class="term-btn small" @click="sendChat">发送</button>
          </div>
        </div>
      </div>

      <!-- Placeholder for other views (Timeline, World, etc.) -->
      <div class="view-placeholder" v-if="currentView !== 'city'">
        <ProfileView v-if="currentView === 'profile'" />
        <TimelineView v-if="currentView === 'timeline'" />
        <ArchivesView v-if="currentView === 'logs'" />
      </div>

    </main>

    <!-- CRT Overlay -->
    <div class="crt-overlay" v-if="isCrtOn"></div>
    <div class="grid-bg"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useGameStore } from '../stores/game'
import { useThemeStore } from '../stores/theme'
import ProfileView from '../components/views/ProfileView.vue'
import TimelineView from '../components/views/TimelineView.vue'
import ArchivesView from '../components/views/ArchivesView.vue'
import DistrictActionPanel from '../components/DistrictActionPanel.vue'
import { useRouter } from 'vue-router'

const gameStore = useGameStore()
const themeStore = useThemeStore()
const router = useRouter()
const currentView = ref('city')
const parallax = ref({ x: 0, y: 0 })
const selectedDistrict = ref(null)
const selectedOptionIndex = ref(null)
const chatText = ref('')
const echoText = ref('')
const echoType = ref('advisory')
const isChatExpanded = ref(true)
const chatBodyRef = ref(null)
const isCrtOn = ref(true)
const isProcessing = ref(false)
const currentDate = ref(new Date().toLocaleDateString('zh-CN').replace(/\//g, '-'))
const isSidebarOpen = ref(false)
const mobileMapMode = ref(true)

const navItems = [
  { id: 'city', label: '城市概览', icon: '⚡' },
  { id: 'profile', label: '主体数据', icon: '👤' },
  { id: 'timeline', label: '时间线', icon: '🕒' },
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

const isMobile = ref(window.innerWidth <= 768)

const updateMobileState = () => {
  isMobile.value = window.innerWidth <= 768
}

const pinStyle = (district) => {
  if (isMobile.value) {
    const mobileLayout = {
      finance: { x: 50, y: 20 },
      learning: { x: 25, y: 38 },
      tech: { x: 75, y: 38 },
      green: { x: 25, y: 62 },
      housing: { x: 75, y: 62 },
      leisure: { x: 50, y: 80 }
    }
    const coords = mobileLayout[district.id] || district.coords || { x: 50, y: 50 }
    return { left: `${coords.x}%`, top: `${coords.y}%` }
  }
  const x = district.coords?.x ?? 50
  const y = district.coords?.y ?? 50
  return { left: `${x}%`, top: `${y}%` }
}

const onParallax = (event) => {
  // Disable parallax on mobile or if map is hidden
  if (window.innerWidth <= 768) return
  
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
const toggleCrt = () => {
  isCrtOn.value = !isCrtOn.value
}

const exitToSelect = () => {
  try {
    gameStore.resetState()
  } catch (e) {
    console.error('Reset state error:', e)
  }
  localStorage.removeItem('currentCharacter')
  router.push('/character-select')
}

const handleNavClick = (viewId) => {
  currentView.value = viewId
  isSidebarOpen.value = false // Close sidebar on mobile selection
}

const handleAdvance = async () => {
  if (isProcessing.value) return
  isProcessing.value = true
  try {
    // Commit decision if selected
    if (selectedOptionIndex.value !== null) {
      await gameStore.makeDecision(selectedOptionIndex.value)
    }

    const text = echoText.value
    echoText.value = '' // Clear immediately
    await gameStore.advanceMonth(text)
    // Add feedback
    // alert('周期推进完成')
  } catch (e) { 
    console.error(e)
    alert('推进失败: ' + e.message)
  } finally {
    isProcessing.value = false
  }
}

const handleSelectOption = (idx) => {
  selectedOptionIndex.value = idx
}

watch(currentSituation, () => {
  selectedOptionIndex.value = null
})

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
  selectedDistrict.value = district
  // gameStore.exploreDistrict(district.id) // Replaced by Action Panel
}

// Auto-scroll chat
watch(chatMessages, async () => {
  await nextTick()
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}, { deep: true })

onMounted(async () => {
  window.addEventListener('resize', updateMobileState)
  themeStore.applyTheme()
  await gameStore.bootstrapHome()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateMobileState)
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
  width: 260px; /* Fixed width to prevent shrinking */
  border-right: 2px solid var(--term-border); /* Add border for separation */
  background: var(--term-panel-bg);
}

.nav-section {
  padding-top: 20px;
  padding-left: 20px; /* Add padding */
  padding-right: 20px;
}

.nav-header {
  /* Removed local styles to use terminal-theme.css */
  padding: 20px; /* Add padding */
  border-bottom: 2px solid var(--term-border);
}

.logo-text {
  /* Removed local styles */
  font-weight: bold;
}

.sub-header {
  /* Removed local styles */
  opacity: 0.7;
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
  position: absolute;
  inset: 0;
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
  gap: 16px; /* Increased gap for larger visuals */
}

.district-visual {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.pixel-building {
  width: 160px; /* Significantly larger size */
  max-width: 25vw; /* Responsive constraint */
  height: auto;
  image-rendering: pixelated; /* Crisp pixels */
  filter: drop-shadow(0 12px 20px rgba(0,0,0,0.5)); /* Deep shadow for pop */
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); /* Bouncy spring transition */
  z-index: 2;
  animation: building-float 6s ease-in-out infinite; /* Alive breathing effect */
  will-change: transform;
}

@keyframes building-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* Hide fallback box when image loads successfully */
.pixel-building:not([style*="display: none"]) + .marker-box.fallback {
  display: none;
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
  font-size: 12px; /* Slightly larger text */
  font-weight: 800;
  color: var(--term-text);
  background: var(--term-panel-bg);
  padding: 6px 12px;
  border: 2px solid var(--term-border); /* Thicker border */
  opacity: 0.9;
  transition: all 0.2s;
  white-space: nowrap;
  box-shadow: 4px 4px 0 rgba(0,0,0,0.2); /* Stronger shadow */
  z-index: 3;
  text-transform: uppercase;
}

/* Hover Effects */
.district-marker:hover .pixel-building {
  transform: scale(1.15) translateY(-15px);
  filter: drop-shadow(0 30px 50px rgba(0,0,0,0.6)) brightness(1.1);
  z-index: 20;
  animation-play-state: paused;
}

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
  color: #000;
  background: var(--term-accent);
  border-color: #000;
  transform: translateY(4px);
  box-shadow: 6px 6px 0 rgba(0,0,0,0.3);
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
  z-index: 50; /* Ensure HUD sits above map markers */
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
  z-index: 100; /* Ensure it is above other elements */
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

.config-btn.orange { background: var(--term-accent); color: var(--config-btn-text); }
.config-btn.green { background: var(--term-success); color: var(--config-btn-text); }
.config-btn.yellow { background: var(--term-accent-secondary); color: var(--config-btn-text); }
.config-btn.white { background: #fff; color: #000; }
.config-btn.red { background: #ef4444; color: #fff; }

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

.term-btn.active {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

.term-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

/* Mobile Responsive Styles */
.menu-btn {
  display: none;
  background: transparent;
  border: none;
  color: var(--term-accent);
  font-size: 24px;
  cursor: pointer;
  padding: 0 10px;
}

.close-sidebar-btn {
  display: none;
  background: transparent;
  border: none;
  color: var(--term-text);
  font-size: 24px;
  cursor: pointer;
  margin-left: auto;
}

.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  backdrop-filter: blur(2px);
}

.mobile-view-switch {
  display: none;
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 60; /* Higher than HUD (50) */
  background: var(--term-panel-bg);
  border: 1px solid var(--term-border);
  padding: 4px;
  gap: 4px;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.switch-btn {
  background: transparent;
  border: none;
  color: var(--term-text-secondary);
  padding: 6px 12px;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  cursor: pointer;
  border-radius: 16px;
}

.switch-btn.active {
  background: var(--term-accent);
  color: #000;
  font-weight: bold;
}

@media (max-width: 768px) {
  .menu-btn {
    display: block;
  }

  .close-sidebar-btn {
    display: block;
  }

  .sidebar-overlay {
    display: block;
  }

  .sidebar-nav {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    width: 80%;
    max-width: 300px;
    /* Remove shadow when closed to prevent bleeding */
    box-shadow: none;
  }

  .sidebar-nav.open {
    transform: translateX(0);
    box-shadow: 10px 0 20px rgba(0,0,0,0.5);
  }

  .nav-header {
    display: flex;
    align-items: center;
  }

  .mobile-view-switch {
    display: flex;
  }

  .hud-overlay {
    position: relative;
    flex-direction: column;
    padding: 60px 10px 10px 10px; /* Top padding for switch button */
    gap: 10px;
    height: calc(100vh - 120px); /* Adjust for header and bottom chat */
    overflow-y: auto;
    pointer-events: auto;
    background: rgba(0, 0, 0, 0.8); /* Dim background */
  }

  .hud-column {
    width: 100%;
    gap: 10px;
  }

  .chat-dock {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    transform: none;
    max-width: 100%;
    padding: 10px;
    background: var(--term-bg);
    border-top: 1px solid var(--term-border);
  }
  
  .chat-history {
    position: fixed;
    bottom: 60px; /* Height of input area */
    left: 10px;
    right: 10px;
    width: auto;
    max-height: 40vh;
    z-index: 101;
  }

  .city-stage {
    position: fixed; /* Keep it fixed as background */
  }

  .mobile-hidden {
    display: none !important;
  }
  
  /* Adjust font sizes for mobile */
  .archive-header {
    font-size: 12px;
  }
  
  .mission-title {
    font-size: 14px;
  }
  
  .mission-desc {
    font-size: 12px;
  }

  /* Allow larger images on mobile */
  .pixel-building {
    max-width: 40vw;
  }
}
</style>
