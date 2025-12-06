<template>
  <div class="project-echo-interface">
    <!-- Mobile Sidebar Overlay -->
    <div class="sidebar-overlay" v-if="isSidebarOpen" @click="isSidebarOpen = false"></div>

    <!-- Left Sidebar: Directory -->
    <nav class="sidebar-nav" :class="{ open: isSidebarOpen }">
      <div class="nav-header">
        <div class="logo-text">EchoPolis金融模拟沙盘</div>
        <div class="sub-header">// 系统终端</div>
        <button class="close-sidebar-btn" @click="isSidebarOpen = false">×</button>
      </div>
      
      <div class="nav-section">
        <div class="section-label">导航</div>
        
        <!-- 主页按钮 -->
        <div 
          :class="['nav-item', { active: currentView === 'city' && !activeGroup }]"
          @click="goToCity">
          <span class="icon">🏠</span>
          主页
        </div>

        <!-- 分组导航 -->
        <div 
          v-for="group in navGroups" 
          :key="group.id"
          :class="['nav-item', { active: activeGroup === group.id }]"
          @click="selectGroup(group.id)">
          <span class="icon">{{ group.icon }}</span>
          {{ group.label }}
          <span class="arrow">›</span>
        </div>

        <!-- 排行榜单独导航 -->
        <div 
          :class="['nav-item', { active: currentView === 'leaderboard' }]"
          @click="openView('leaderboard')">
          <span class="icon">🏅</span>
          排行榜
        </div>
      </div>

      <div class="nav-spacer"></div>

      <!-- 底部操作按钮 -->
      <div class="system-actions">
        <button class="action-btn settings-btn" @click="showSettings = true">
          <span class="icon">⚙️</span>
          <span class="label">设置</span>
        </button>
        <button class="action-btn exit-btn" @click="exitToSelect">
          <span class="icon">🔌</span>
          <span class="label">断开</span>
        </button>
      </div>
    </nav>

    <!-- 设置面板 -->
    <SettingsPanel 
      :isOpen="showSettings" 
      @close="showSettings = false"
      @bgmToggle="handleBgmToggle"
      @crtToggle="handleCrtToggle"
    />

    <!-- Main Content Area -->
    <main class="main-content">
      <!-- Top Header -->
      <header class="top-bar">
        <button class="menu-btn" @click="isSidebarOpen = true">☰</button>
        
        <!-- 返回按钮（当在子页面时显示） -->
        <button 
          v-if="(activeGroup && !currentView) || (currentView && currentView !== 'city')" 
          class="header-back-btn" 
          @click="handleBack">
          ← 返回
        </button>
        
        <div class="brand-logo">
          <span class="highlight">EchoPolis</span> // 系统
        </div>
        <div class="header-right">
          <div class="header-meta">
            <span>{{ currentDate }}</span>
          </div>
          <MusicPlayer ref="musicPlayerRef" @stateChange="isBgmPlaying = $event" />
        </div>
      </header>

      <!-- Game View Layer -->
      <div class="game-viewport" v-show="currentView === 'city' && !activeGroup">
        
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
              <line x1="30%" y1="35%" x2="50%" y2="45%" /> <!-- Learning -> Finance -->
              <line x1="70%" y1="35%" x2="50%" y2="45%" /> <!-- Tech -> Finance -->
              <line x1="30%" y1="65%" x2="50%" y2="45%" /> <!-- Green -> Finance -->
              <line x1="70%" y1="65%" x2="50%" y2="45%" /> <!-- Housing -> Finance -->
              <line x1="50%" y1="70%" x2="50%" y2="45%" /> <!-- Leisure -> Finance -->
              
              <!-- Outer Ring -->
              <line x1="30%" y1="35%" x2="70%" y2="35%" /> <!-- Learning -> Tech -->
              <line x1="30%" y1="65%" x2="50%" y2="70%" /> <!-- Green -> Leisure -->
              <line x1="50%" y1="70%" x2="70%" y2="65%" /> <!-- Leisure -> Housing -->
              <line x1="30%" y1="35%" x2="30%" y2="65%" /> <!-- Learning -> Green -->
              <line x1="70%" y1="35%" x2="70%" y2="65%" /> <!-- Tech -> Housing -->
            </g>

            <g v-else stroke="rgba(0,0,0,0.1)" stroke-width="2" fill="none" stroke-dasharray="4 4">
               <!-- Mobile Hexagon Connections -->
               <line x1="50%" y1="28%" x2="25%" y2="45%" />
               <line x1="50%" y1="28%" x2="75%" y2="45%" />
               <line x1="25%" y1="45%" x2="25%" y2="65%" />
               <line x1="75%" y1="45%" x2="75%" y2="65%" />
               <line x1="25%" y1="65%" x2="50%" y2="82%" />
               <line x1="75%" y1="65%" x2="50%" y2="82%" />
               <line x1="25%" y1="45%" x2="75%" y2="45%" />
               <line x1="25%" y1="65%" x2="75%" y2="65%" />
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
              <img :src="buildAssetUrl(`assets/districts/${district.id}.png`)" 
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

        <!-- District Preview Panel -->
        <DistrictPreviewPanel 
          v-if="selectedDistrict" 
          :district="selectedDistrict" 
          @close="selectedDistrict = null"
          @navigate="handleDistrictNavigate"
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
                  <div class="avatar-face user-avatar" 
                    :style="{ backgroundColor: userAvatarInfo?.color || '#ff8c00' }"
                    @click="openView('avatar-shop')">
                    <span class="avatar-emoji">{{ userAvatarInfo?.emoji || '🎭' }}</span>
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
            
            <!-- 活跃效果提示 -->
            <div class="archive-card" v-if="activeEffects.length > 0">
              <div class="archive-header">
                <span>⚡ 活跃效果</span>
                <span class="count">{{ activeEffects.length }}</span>
              </div>
              <div class="archive-body">
                <div class="effect-list">
                  <div v-for="(effect, i) in activeEffects.slice(0, 3)" :key="i" 
                    class="effect-item" :class="effect.value >= 0 ? 'positive' : 'negative'">
                    <span class="effect-source">{{ effect.source }}</span>
                    <span class="effect-value">
                      {{ effect.value >= 0 ? '+' : '' }}{{ effect.value }}
                      {{ effect.type === 'income' ? '收入' : effect.type === 'expense' ? '支出' : effect.type }}
                    </span>
                    <span class="effect-duration">{{ effect.remaining_months }}个月</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: Mission Control -->
          <div class="hud-column right">
            <div class="archive-card highlight flex-grow-card command-panel" :class="{ expanded: isCommandPanelExpanded }">
              <div class="archive-header">
                <span>当前指令</span>
                <div class="header-actions">
                  <span class="blink">执行中</span>
                  <button class="expand-btn" @click="isCommandPanelExpanded = !isCommandPanelExpanded" :title="isCommandPanelExpanded ? '收起面板' : '展开面板'">
                    {{ isCommandPanelExpanded ? '▶' : '◀' }}
                  </button>
                </div>
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
                  <button 
                    class="term-btn primary full" 
                    :class="{ 'is-loading': gameStore.isAdvancingMonth || isProcessing, 'is-disabled': !canAdvance }"
                    :disabled="!canAdvance || gameStore.isAdvancingMonth || isProcessing" 
                    @click="handleAdvance">
                    <span v-if="gameStore.isAdvancingMonth || isProcessing" class="loading-content">
                      <span class="spinner"></span>
                      <span>处理中，请稍候...</span>
                    </span>
                    <span v-else-if="!canAdvance">⏳ 等待事件生成...</span>
                    <span v-else>>> 执行下一周期</span>
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

      <!-- 分组卡片选择面板 -->
      <div class="group-cards-panel" v-if="activeGroup && !currentView">
        <div class="cards-header">
          <button class="back-btn" @click="goToCity">
            <span>←</span> 返回主页
          </button>
          <h2 class="cards-title">{{ getGroupLabel(activeGroup) }}</h2>
        </div>
        <div class="cards-grid">
          <div 
            v-for="item in getGroupItems(activeGroup)" 
            :key="item.id"
            class="view-card"
            @click="openView(item.id)"
          >
            <div class="card-icon">{{ item.icon }}</div>
            <div class="card-label">{{ item.label }}</div>
            <div class="card-desc">{{ item.desc }}</div>
          </div>
        </div>
      </div>

      <!-- Placeholder for other views (Timeline, World, etc.) -->
      <div class="view-placeholder" v-if="currentView && currentView !== 'city'">
        <ProfileView v-if="currentView === 'profile'" />
        <BankingView v-if="currentView === 'banking'" />
        <HousingView v-if="currentView === 'housing'" />
        <LifestyleView v-if="currentView === 'lifestyle'" />
        <ArchivesView v-if="currentView === 'logs'" />
        <TimelineView v-if="currentView === 'timeline'" />
        <TradingView v-if="currentView === 'trading'" />
        <CareerView v-if="currentView === 'career'" />
        <LeaderboardView v-if="currentView === 'leaderboard'" />
        <AchievementView v-if="currentView === 'achievements'" />
        <InsightsView v-if="currentView === 'insights'" />
        <AvatarShopView v-if="currentView === 'avatar-shop'" @avatar-changed="onAvatarChanged" />
        <EventPoolView v-if="currentView === 'event-pool'" />
      </div>

    </main>

    <!-- CRT Overlay -->
    <div class="crt-overlay" v-if="isCrtOn"></div>
    <div class="grid-bg"></div>
    
    <!-- 事件弹窗 -->
    <EventModal 
      ref="eventModalRef"
      @event-completed="onEventCompleted"
      @all-events-done="onAllEventsDone"
    />
    
    <!-- 推进成功提示 -->
    <Transition name="toast">
      <div v-if="advanceSuccessToast.show" class="advance-success-toast">
        <span class="toast-icon">✓</span>
        <span class="toast-message">{{ advanceSuccessToast.message }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useGameStore } from '../stores/game'
import { useThemeStore } from '../stores/theme'
import { buildAssetUrl, buildApiUrl } from '../utils/api'
import ProfileView from '../components/views/ProfileView.vue'
import TimelineView from '../components/views/TimelineView.vue'
import ArchivesView from '../components/views/ArchivesView.vue'
import TradingView from '../components/views/TradingView.vue'
import AchievementView from '../components/views/AchievementView.vue'
import CareerView from '../components/views/CareerView.vue'
import LeaderboardView from '../components/views/LeaderboardView.vue'
import BankingView from '../components/views/BankingView.vue'
import HousingView from '../components/views/HousingView.vue'
import LifestyleView from '../components/views/LifestyleView.vue'
import InsightsView from '../components/views/InsightsView.vue'
import AvatarShopView from '../components/views/AvatarShopView.vue'
import EventPoolView from '../components/views/EventPoolView.vue'
import DistrictPreviewPanel from '../components/DistrictPreviewPanel.vue'
import EventModal from '../components/EventModal.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
import SettingsPanel from '../components/SettingsPanel.vue'
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
const isCommandPanelExpanded = ref(false)  // 当前指令面板展开状态

// 音乐播放器和设置面板
const musicPlayerRef = ref(null)
const showSettings = ref(false)
const isBgmPlaying = ref(false)

// 事件系统
const eventModalRef = ref(null)
const pendingEvents = ref([])
const activeEffects = ref([])
const activeGroup = ref(null)

// 导航分组
const navGroups = [
  { id: 'personal', label: '个人中心', icon: '👤' },
  { id: 'finance', label: '金融服务', icon: '💰' },
  { id: 'life', label: '生活规划', icon: '🏠' },
  { id: 'system', label: '系统档案', icon: '📊' }
]

// 分组内的页面项
const groupItems = {
  personal: [
    { id: 'profile', label: '主体数据', icon: '👤', desc: '查看角色属性与状态' },
    { id: 'insights', label: '行为洞察', icon: '🧠', desc: 'AI分析你的决策模式' },
    { id: 'achievements', label: '成就系统', icon: '🏆', desc: '解锁的成就与里程碑' },
    { id: 'avatar-shop', label: '头像商店', icon: '🎭', desc: '用成就金币购买头像' }
  ],
  finance: [
    { id: 'banking', label: '银行系统', icon: '🏦', desc: '存款、贷款与理财' },
    { id: 'trading', label: '股票交易', icon: '📈', desc: '股票投资与交易' }
  ],
  life: [
    { id: 'career', label: '职业发展', icon: '💼', desc: '工作与职业规划' },
    { id: 'housing', label: '房产管理', icon: '🏘️', desc: '房产购买与投资' },
    { id: 'lifestyle', label: '生活方式', icon: '🎯', desc: '消费与生活品质' }
  ],
  system: [
    { id: 'logs', label: '档案库', icon: '📖', desc: '历史记录与存档' },
    { id: 'timeline', label: '时间线', icon: '🕒', desc: '人生轨迹回顾' },
    { id: 'event-pool', label: '事件池', icon: '📡', desc: '实时新闻与市场动态' }
  ]
}

// 旧的 navItems 保留兼容
const navItems = [
  { id: 'city', label: '城市概览', icon: '⚡' },
  { id: 'profile', label: '主体数据', icon: '👤' },
  { id: 'banking', label: '银行系统', icon: '🏦' },
  { id: 'trading', label: '股票交易', icon: '📈' },
  { id: 'career', label: '职业发展', icon: '💼' },
  { id: 'insights', label: '行为洞察', icon: '🧠' },
  { id: 'logs', label: '档案库', icon: '📖' },
  { id: 'timeline', label: '时间线', icon: '🕒' },
  { id: 'leaderboard', label: '排行榜', icon: '🏅' },
  { id: 'achievements', label: '成就系统', icon: '🏆' }
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

// 是否可以推进下一周期（需要有事件生成）
const canAdvance = computed(() => {
  return currentSituation.value && currentSituation.value.description && situationOptions.value?.length > 0
})
const chatMessages = computed(() => gameStore.chatMessages)

// 用户头像信息
const userAvatarInfo = ref({ emoji: '🎭', color: '#ff8c00', name: '默认头像' })

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
      finance: { x: 50, y: 28 },
      learning: { x: 25, y: 45 },
      tech: { x: 75, y: 45 },
      green: { x: 25, y: 65 },
      housing: { x: 75, y: 65 },
      leisure: { x: 50, y: 82 }
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

// 处理设置面板的BGM切换
const handleBgmToggle = (enabled) => {
  if (musicPlayerRef.value) {
    if (enabled && !isBgmPlaying.value) {
      musicPlayerRef.value.togglePlay()
    } else if (!enabled && isBgmPlaying.value) {
      musicPlayerRef.value.togglePlay()
    }
  }
}

// 处理设置面板的CRT切换
const handleCrtToggle = (enabled) => {
  isCrtOn.value = enabled
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
  // 如果是行为洞察，跳转到新路由
  if (viewId === 'insights') {
    router.push('/insights')
    return
  }
  currentView.value = viewId
  isSidebarOpen.value = false // Close sidebar on mobile selection
}

// 新的分组导航函数
const goToCity = () => {
  activeGroup.value = null
  currentView.value = 'city'
  isSidebarOpen.value = false
}

const selectGroup = (groupId) => {
  activeGroup.value = groupId
  currentView.value = null
  isSidebarOpen.value = false
}

const getGroupLabel = (groupId) => {
  const group = navGroups.find(g => g.id === groupId)
  return group ? group.label : ''
}

const getGroupItems = (groupId) => {
  return groupItems[groupId] || []
}

const openView = (viewId) => {
  // 如果是排行榜，清除分组选中状态
  if (viewId === 'leaderboard') {
    activeGroup.value = null
  }
  currentView.value = viewId
  isSidebarOpen.value = false
}

const backToCards = () => {
  if (activeGroup.value) {
    // 有分组，返回卡片选择
    currentView.value = null
  } else {
    // 没有分组，返回主页
    currentView.value = 'city'
  }
}

// 全局返回按钮处理
const handleBack = () => {
  if (currentView.value && currentView.value !== 'city') {
    // 在具体页面，返回到卡片或主页
    backToCards()
  } else if (activeGroup.value) {
    // 在卡片面板，返回主页
    goToCity()
  }
}

const handleAdvance = async () => {
  if (isProcessing.value || !canAdvance.value) return
  isProcessing.value = true
  
  // 记录当前月份用于提示
  const currentMonth = gameStore.avatar?.current_month || 1
  
  try {
    // Commit decision if selected
    if (selectedOptionIndex.value !== null) {
      await gameStore.makeDecision(selectedOptionIndex.value)
    }

    const text = echoText.value
    echoText.value = '' // Clear immediately
    await gameStore.advanceMonth(text)
    
    // 时间推进后触发随机事件
    await triggerRandomEvents()
    
    // 更新活跃效果
    await updateActiveEffects()
    
    // 处理完成提示
    const newMonth = gameStore.avatar?.current_month || currentMonth + 1
    showAdvanceSuccessToast(currentMonth, newMonth)
    
  } catch (e) { 
    console.error(e)
    alert('推进失败: ' + e.message)
  } finally {
    isProcessing.value = false
  }
}

// 显示推进成功提示
const advanceSuccessToast = ref({ show: false, message: '' })
const showAdvanceSuccessToast = (fromMonth, toMonth) => {
  advanceSuccessToast.value = {
    show: true,
    message: `周期推进完成：第 ${fromMonth} 月 → 第 ${toMonth} 月`
  }
  setTimeout(() => {
    advanceSuccessToast.value.show = false
  }, 3000)
}

// 获取当前会话ID
const getSessionId = () => {
  try {
    const char = localStorage.getItem('currentCharacter')
    return char ? JSON.parse(char).id : null
  } catch { return null }
}

// 触发随机事件
const triggerRandomEvents = async () => {
  const sessionId = getSessionId()
  if (!sessionId) return
  
  try {
    const res = await fetch(buildApiUrl('/api/events/generate'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        player_state: {
          assets: gameStore.assets?.total || 0,
          cash: gameStore.assets?.cash || 0,
          job: gameStore.avatar?.job || null,
          month: gameStore.avatar?.month || 1
        },
        count: 1  // 每月最多1个事件
      })
    })
    const data = await res.json()
    
    if (data.success && data.events && data.events.length > 0) {
      // 通过 ref 调用 EventModal 的 addEvents 方法
      if (eventModalRef.value) {
        eventModalRef.value.addEvents(data.events)
      }
    }
  } catch (e) {
    console.error('生成事件失败:', e)
  }
}

// 更新活跃效果
const updateActiveEffects = async () => {
  const sessionId = getSessionId()
  if (!sessionId) return
  
  try {
    const res = await fetch(buildApiUrl('/api/events/update-effects'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    })
    const data = await res.json()
    
    if (data.success && data.active_effects) {
      activeEffects.value = data.active_effects
      // 应用效果到游戏状态（如收入加成、支出增加等）
      // 这里可以扩展处理逻辑
    }
  } catch (e) {
    console.error('更新效果失败:', e)
  }
}

// 事件完成回调
const onEventCompleted = (payload) => {
  console.log('事件完成:', payload)
  // 刷新玩家状态
  gameStore.loadAvatar()
}

// 所有事件处理完成
const onAllEventsDone = () => {
  console.log('所有事件处理完成')
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
}

// 区域导航到对应页面
const handleDistrictNavigate = (viewId) => {
  currentView.value = viewId
  selectedDistrict.value = null
}

// Auto-scroll chat
watch(chatMessages, async () => {
  await nextTick()
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}, { deep: true })

onMounted(() => {
  console.log('[HomeNew] onMounted 开始执行')
  window.addEventListener('resize', updateMobileState)
  themeStore.applyTheme()
  
  // 后台加载，不阻塞页面渲染
  console.log('[HomeNew] 开始后台加载数据')
  gameStore.bootstrapHome()
  
  // 加载活跃效果（后台执行）
  loadActiveEffects()
  
  // 加载用户头像信息
  loadUserAvatar()
  
  console.log('[HomeNew] onMounted 执行完毕，页面应该已经渲染')
})

// 加载用户头像
const loadUserAvatar = async () => {
  const sessionId = getSessionId()
  console.log('[HomeNew] loadUserAvatar called, sessionId:', sessionId)
  if (!sessionId) return
  
  try {
    const url = buildApiUrl(`/api/avatar/user/${sessionId}`)
    console.log('[HomeNew] Fetching avatar from:', url)
    const res = await fetch(url)
    const data = await res.json()
    console.log('[HomeNew] Avatar API response:', data)
    if (data.success && data.current_avatar_info) {
      userAvatarInfo.value = data.current_avatar_info
      console.log('[HomeNew] Updated userAvatarInfo:', userAvatarInfo.value)
    }
  } catch (e) {
    console.error('加载头像信息失败:', e)
  }
}

// 头像更换时更新显示
const onAvatarChanged = (newAvatar) => {
  console.log('[HomeNew] Avatar changed:', newAvatar)
  userAvatarInfo.value = newAvatar
}

// 加载活跃效果
const loadActiveEffects = async () => {
  const sessionId = getSessionId()
  if (!sessionId) return
  
  try {
    const res = await fetch(buildApiUrl(`/api/events/active-effects/${sessionId}`))
    const data = await res.json()
    if (data.success && data.effects) {
      activeEffects.value = data.effects
    }
  } catch (e) {
    console.error('加载活跃效果失败:', e)
  }
}

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
  width: 260px;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
  border-right: 2px solid var(--term-border);
  background: var(--term-panel-bg);
}

.nav-section {
  flex-shrink: 0;
  padding: 16px;
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
  flex: 1 1 0; /* 可扩展也可收缩到0 */
  min-height: 0;
}

/* 导航项箭头 */
.nav-item .arrow {
  margin-left: auto;
  font-size: 16px;
  opacity: 0.5;
  transition: transform 0.2s;
}

.nav-item:hover .arrow {
  transform: translateX(3px);
  opacity: 1;
}

/* 分组卡片面板 */
.group-cards-panel {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.cards-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.cards-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--term-accent);
  margin: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: 2px solid var(--term-border);
  color: var(--term-text);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.view-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 4px 4px 0 rgba(0,0,0,0.1);
}

.view-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 rgba(0,0,0,0.15);
  border-color: var(--term-accent);
}

.card-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.card-label {
  font-size: 16px;
  font-weight: 700;
  color: var(--term-text);
  margin-bottom: 8px;
}

.card-desc {
  font-size: 12px;
  color: var(--term-dim);
  line-height: 1.4;
}

/* 顶栏返回按钮 */
.header-back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: transparent;
  border: 2px solid var(--term-border);
  color: var(--term-text);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 12px;
}

.header-back-btn:hover {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

/* 底部操作按钮 */
.system-actions {
  flex-shrink: 0;
  display: flex;
  gap: 8px;
  padding: 10px;
  border-top: 2px solid var(--term-border);
  background: var(--term-panel-bg); /* 确保背景色 */
  margin-top: auto; /* 推到底部 */
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  border: 2px solid var(--term-border);
  background: var(--term-panel-bg);
  color: var(--term-text);
  font-weight: 700;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

.action-btn .icon {
  font-size: 14px;
}

.action-btn.exit-btn {
  border-color: #ef4444;
  color: #ef4444;
}

.action-btn.exit-btn:hover {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
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

/* 顶栏右侧区域 */
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
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

.hud-column.right {
  z-index: 60; /* 高于底部聊天框 */
}

/* 当前指令面板展开样式 */
.command-panel {
  transition: all 0.3s ease;
  position: relative;
  z-index: 100;
}

.command-panel.expanded {
  position: fixed;
  top: 80px;
  right: 40px;
  bottom: 100px;
  width: 700px;
  max-height: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 3px solid var(--term-accent);
}

.command-panel.expanded .archive-body.scrollable-body {
  max-height: none;
  overflow-y: auto;
}

.command-panel.expanded .mission-title {
  font-size: 24px;
  margin-bottom: 16px;
}

.command-panel.expanded .mission-desc {
  font-size: 16px;
  line-height: 1.8;
}

.command-panel.expanded .action-grid {
  gap: 12px;
}

.command-panel.expanded .term-btn {
  padding: 16px 20px;
  font-size: 15px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.expand-btn {
  background: var(--term-accent);
  border: 2px solid #000;
  color: #000;
  width: 28px;
  height: 28px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.expand-btn:hover {
  background: #000;
  color: var(--term-accent);
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

.avatar-face.user-avatar {
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.avatar-face.user-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
}

.avatar-emoji {
  font-size: 32px;
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

/* Active Effects Styles */
.effect-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.effect-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  padding: 6px 8px;
  border-left: 3px solid var(--term-border);
  background: rgba(0,0,0,0.03);
}

.effect-item.positive {
  border-left-color: #10b981;
}

.effect-item.negative {
  border-left-color: #ef4444;
}

.effect-source {
  font-weight: 700;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100px;
}

.effect-value {
  font-weight: 600;
  margin: 0 8px;
}

.effect-item.positive .effect-value {
  color: #10b981;
}

.effect-item.negative .effect-value {
  color: #ef4444;
}

.effect-duration {
  font-size: 10px;
  color: var(--term-text-secondary);
  background: rgba(0,0,0,0.05);
  padding: 2px 6px;
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

@media (max-width: 768px) {
  .view-placeholder {
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
  }
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
  .top-bar {
    padding: 0 8px;
    gap: 8px;
  }
  
  .brand-logo {
    font-size: 20px;
    white-space: nowrap;
  }
  
  .header-right {
    gap: 8px;
  }
  
  .header-meta {
    font-size: 10px;
    gap: 8px;
  }
  
  .header-back-btn {
    padding: 4px 8px;
    font-size: 11px;
    margin-right: 8px;
  }
  
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

/* 推进按钮加载状态 */
.term-btn.is-loading {
  background: #666 !important;
  cursor: wait !important;
  pointer-events: none;
}

.term-btn.is-disabled {
  background: #444 !important;
  color: #888 !important;
  cursor: not-allowed !important;
  border-color: #555 !important;
}

.term-btn.is-disabled:hover {
  transform: none !important;
  box-shadow: 2px 2px 0px rgba(0,0,0,0.1) !important;
}

.loading-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #333;
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 推进成功提示 Toast */
.advance-success-toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
  color: #fff;
  padding: 12px 24px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  z-index: 9999;
  border: 2px solid #4caf50;
}

.toast-icon {
  background: #4caf50;
  color: #fff;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.toast-message {
  white-space: nowrap;
}

/* Toast 动画 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}
</style>
