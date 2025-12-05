<template>
  <div class="world-sandbox">
    <!-- 移动端侧边栏遮罩 -->
    <div class="sidebar-overlay" v-if="isSidebarOpen" @click="isSidebarOpen = false"></div>

    <!-- 左侧导航栏 -->
    <nav class="sidebar-nav" :class="{ open: isSidebarOpen }">
      <div class="nav-header">
        <div class="logo-text">EchoPolis</div>
        <div class="sub-header">// 世界沙盘</div>
        <button class="close-sidebar-btn" @click="isSidebarOpen = false">×</button>
      </div>

      <div class="nav-section">
        <div class="section-label">模块导航</div>
        
        <div 
          :class="['nav-item', { active: $route.name === 'WorldSandbox' }]"
          @click="$router.push('/world-sandbox')">
          <span class="icon">🗺️</span>
          世界沙盘
        </div>
        
        <div 
          :class="['nav-item', { active: $route.name === 'EventEcho' }]"
          @click="$router.push('/event-echo')">
          <span class="icon">🎲</span>
          事件回响
        </div>
        
        <div 
          :class="['nav-item', { active: $route.name === 'PersonalCenter' }]"
          @click="$router.push('/personal-center')">
          <span class="icon">👤</span>
          个人中心
        </div>
      </div>

      <div class="nav-spacer"></div>

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
    />

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部状态栏 -->
      <header class="top-bar">
        <button class="menu-btn" @click="isSidebarOpen = true">☰</button>
        
        <button 
          v-if="activeBuilding" 
          class="header-back-btn" 
          @click="closeBuilding">
          ← 返回地图
        </button>
        
        <div class="brand-logo">
          <span class="highlight">EchoPolis</span> // {{ activeBuilding ? getBuildingName(activeBuilding) : '世界沙盘' }}
        </div>
        
        <div class="header-right">
          <div class="header-meta">
            <span class="date-time">🕐 {{ currentDateTime }}</span>
          </div>
          <MusicPlayer ref="musicPlayerRef" />
        </div>
      </header>

      <!-- 地图视图 (首页) -->
      <div class="map-viewport" v-show="!activeBuilding">
        <!-- 状态概览卡片 -->
        <div class="status-overlay">
          <div class="status-card">
            <div class="card-header">
              <span>主体状态</span>
              <span class="id">ID_{{ avatar?.session_id?.slice(0, 4) || '0000' }}</span>
            </div>
            <div class="card-body">
              <div class="avatar-info">
                <div class="avatar-face">
                  <div class="eye left"></div>
                  <div class="eye right"></div>
                  <div class="mouth"></div>
                </div>
                <div class="avatar-details">
                  <h3>{{ avatar?.name || 'Echo' }}</h3>
                  <div class="tags">
                    <span class="tag mbti">{{ avatar?.mbti_type || 'INTJ' }}</span>
                    <span class="tag level">Lv.{{ Math.floor((avatar?.current_month || 0)/12) + 1 }}</span>
                  </div>
                </div>
              </div>
              <div class="stat-list">
                <div class="stat-item">
                  <label>总资产</label>
                  <span class="value">¥{{ formatNumber(assets.total) }}</span>
                </div>
                <div class="stat-item">
                  <label>现金</label>
                  <span class="value">¥{{ formatNumber(assets.cash) }}</span>
                </div>
              </div>
              <div class="stat-bars">
                <div class="bar-row">
                  <span class="bar-label">健康</span>
                  <div class="bar"><div class="fill green" :style="{ width: (avatar?.health || 80) + '%' }"></div></div>
                </div>
                <div class="bar-row">
                  <span class="bar-label">幸福</span>
                  <div class="bar"><div class="fill yellow" :style="{ width: (avatar?.happiness || 70) + '%' }"></div></div>
                </div>
                <div class="bar-row">
                  <span class="bar-label">精力</span>
                  <div class="bar"><div class="fill orange" :style="{ width: (avatar?.energy || 75) + '%' }"></div></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 城市地图 -->
        <div class="city-map" @mousemove="onParallax" @mouseleave="resetParallax">
          <div class="city-sky" :style="parallaxStyles.sky" />
          <div class="city-grid" :style="parallaxStyles.grid" />
          
          <!-- 建筑标记 -->
          <div 
            v-for="building in buildings"
            :key="building.id"
            class="building-marker"
            :style="getBuildingPosition(building)"
            @click="enterBuilding(building.view)">
            <div class="building-visual">
              <img 
                :src="`/assets/districts/${building.id}.png`" 
                class="building-img"
                :alt="building.name"
                @error="$event.target.style.display='none'" />
              <div class="marker-box fallback">
                <span class="marker-icon">{{ building.icon }}</span>
              </div>
            </div>
            <div class="building-label">{{ building.name }}</div>
            <div class="building-tag">{{ building.tagline }}</div>
          </div>
        </div>
      </div>

      <!-- 建筑内部视图 (子页面) -->
      <div class="building-view" v-if="activeBuilding">
        <BankingView v-if="activeBuilding === 'banking'" />
        <TradingView v-if="activeBuilding === 'trading'" />
        <CareerView v-if="activeBuilding === 'career'" />
        <HousingView v-if="activeBuilding === 'housing'" />
        <LifestyleView v-if="activeBuilding === 'lifestyle'" />
        <LearningView v-if="activeBuilding === 'learning'" />
      </div>
    </main>

    <!-- CRT效果 -->
    <div class="crt-overlay" v-if="isCrtOn"></div>
    <div class="grid-bg"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'
import SettingsPanel from '../components/SettingsPanel.vue'
import MusicPlayer from '../components/MusicPlayer.vue'
import BankingView from '../components/views/BankingView.vue'
import TradingView from '../components/views/TradingView.vue'
import CareerView from '../components/views/CareerView.vue'
import HousingView from '../components/views/HousingView.vue'
import LifestyleView from '../components/views/LifestyleView.vue'

// 新增学习视图（暂时使用占位）
const LearningView = {
  template: `
    <div class="view-container">
      <div class="view-header">
        <h2>知识学院 // LEARNING_CENTER</h2>
        <div class="header-line"></div>
      </div>
      <div class="empty-state">
        <div class="empty-icon">📚</div>
        <p>学习模块开发中...</p>
      </div>
    </div>
  `
}

const router = useRouter()
const gameStore = useGameStore()

// 状态
const isSidebarOpen = ref(false)
const showSettings = ref(false)
const activeBuilding = ref(null)
const parallax = ref({ x: 0, y: 0 })
const isCrtOn = ref(true)
const musicPlayerRef = ref(null)
// 真实北京时间
const currentDateTime = ref('')
let timeInterval = null

const updateTime = () => {
  const now = new Date()
  const options = {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }
  currentDateTime.value = now.toLocaleString('zh-CN', options).replace(/\//g, '-')
}

// 建筑配置 - 使用与图片文件匹配的ID
const buildings = [
  { id: 'finance', name: '中央银行', icon: '🏦', tagline: '存贷款服务', coords: { x: 50, y: 35 }, view: 'banking' },
  { id: 'tech', name: '量化交易所', icon: '📈', tagline: '股票投资', coords: { x: 75, y: 25 }, view: 'trading' },
  { id: 'green', name: '人才中心', icon: '💼', tagline: '职业发展', coords: { x: 25, y: 25 }, view: 'career' },
  { id: 'housing', name: '房产中枢', icon: '🏠', tagline: '房产管理', coords: { x: 80, y: 55 }, view: 'housing' },
  { id: 'leisure', name: '生活广场', icon: '🎯', tagline: '消费生活', coords: { x: 50, y: 65 }, view: 'lifestyle' },
  { id: 'learning', name: '知识学院', icon: '📚', tagline: '技能学习', coords: { x: 20, y: 55 }, view: 'learning' }
]

// 计算属性
const avatar = computed(() => gameStore.avatar)
const assets = computed(() => ({
  total: gameStore.assets?.total ?? 0,
  cash: gameStore.assets?.cash ?? 0
}))



// 视差效果
const parallaxStyles = computed(() => {
  const { x, y } = parallax.value
  const make = (mult) => ({ transform: `translate3d(${x * mult}px, ${y * mult}px, 0)` })
  return {
    sky: make(10),
    grid: make(15)
  }
})

// 方法
const formatNumber = (num) => Number(num || 0).toLocaleString('zh-CN')

const getBuildingPosition = (building) => ({
  left: `${building.coords.x}%`,
  top: `${building.coords.y}%`
})

const getBuildingName = (viewId) => {
  const building = buildings.find(b => b.view === viewId)
  return building ? building.name : ''
}

const enterBuilding = (buildingId) => {
  activeBuilding.value = buildingId
}

const closeBuilding = () => {
  activeBuilding.value = null
}

const onParallax = (event) => {
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

const exitToSelect = () => {
  if (timeInterval) clearInterval(timeInterval)
  router.push('/character-select')
}

// 生命周期
onMounted(async () => {
  await gameStore.loadAvatar()
  // 启动真实时间更新
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  // 组件销毁时停止计时器
  if (timeInterval) clearInterval(timeInterval)
})
</script>

<style scoped>
.world-sandbox {
  display: flex;
  height: 100vh;
  background: var(--term-bg);
  overflow: hidden;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
}

/* 侧边栏 */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 99;
}

.sidebar-nav {
  width: 260px;
  background: var(--term-panel-bg);
  border-right: 2px solid var(--term-border);
  display: flex;
  flex-direction: column;
  z-index: 100;
  flex-shrink: 0;
}

.nav-header {
  padding: 20px;
  border-bottom: 2px solid var(--term-border);
  position: relative;
}

.logo-text {
  font-size: 18px;
  font-weight: 900;
  color: var(--term-accent);
  letter-spacing: 0.05em;
}

.sub-header {
  font-size: 11px;
  color: var(--term-text-secondary);
  margin-top: 4px;
  font-family: 'JetBrains Mono', monospace;
}

.close-sidebar-btn {
  display: none;
  position: absolute;
  right: 12px;
  top: 12px;
  background: none;
  border: none;
  color: var(--term-text);
  font-size: 24px;
  cursor: pointer;
}

.nav-section {
  padding: 16px;
  flex: 1;
}

.section-label {
  font-size: 10px;
  color: var(--term-text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 700;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 4px;
  cursor: pointer;
  color: var(--term-text);
  transition: all 0.2s;
  border: 2px solid transparent;
  font-weight: 600;
  font-size: 13px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--term-border);
}

.nav-item.active {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

.nav-item .icon {
  font-size: 16px;
}

.nav-spacer {
  flex: 1;
}

.system-actions {
  padding: 16px;
  border-top: 2px solid var(--term-border);
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 10px;
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  color: var(--term-text);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 700;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

.action-btn .icon {
  font-size: 16px;
}

/* 主内容 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* 顶部栏 */
.top-bar {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: var(--term-panel-bg);
  border-bottom: 2px solid var(--term-border);
  gap: 16px;
  z-index: 10;
}

.menu-btn {
  display: none;
  background: none;
  border: none;
  color: var(--term-text);
  font-size: 20px;
  cursor: pointer;
}

.header-back-btn {
  padding: 6px 12px;
  background: transparent;
  border: 2px solid var(--term-border);
  color: var(--term-text);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
}

.header-back-btn:hover {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

.brand-logo {
  font-size: 14px;
  color: var(--term-text);
  font-weight: 700;
}

.brand-logo .highlight {
  color: var(--term-accent);
  font-weight: 900;
}

.header-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--term-text-secondary);
  font-family: 'JetBrains Mono', monospace;
}

.date-time {
  padding: 6px 12px;
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid var(--term-accent);
  color: var(--term-accent);
  font-weight: 600;
  font-size: 12px;
}

/* 地图视图 */
.map-viewport {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.status-overlay {
  position: absolute;
  left: 32px;
  top: 32px;
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 16px;
  pointer-events: auto;
}

.status-card {
  width: 300px;
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  padding: 10px 14px;
  background: rgba(0, 0, 0, 0.3);
  font-size: 11px;
  font-weight: 700;
  color: var(--term-text);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.card-header .id {
  color: var(--term-accent);
  font-family: 'JetBrains Mono', monospace;
}

.card-body {
  padding: 14px;
}

.avatar-info {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}

.avatar-face {
  width: 48px;
  height: 48px;
  background: var(--term-accent);
  position: relative;
  flex-shrink: 0;
}

.avatar-face .eye {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #000;
  top: 14px;
}

.avatar-face .eye.left { left: 10px; }
.avatar-face .eye.right { right: 10px; }

.avatar-face .mouth {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 18px;
  height: 3px;
  background: #000;
}

.avatar-details h3 {
  margin: 0 0 6px;
  font-size: 16px;
  font-weight: 800;
  color: var(--term-text);
}

.tags {
  display: flex;
  gap: 6px;
}

.tag {
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 700;
  background: var(--term-border);
  color: var(--term-text);
}

.tag.mbti {
  background: var(--term-accent);
  color: #000;
}

.stat-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-item label {
  font-size: 10px;
  color: var(--term-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-item .value {
  font-size: 15px;
  font-weight: 800;
  color: var(--term-accent);
  font-family: 'JetBrains Mono', monospace;
}

.stat-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-label {
  font-size: 10px;
  color: var(--term-text-secondary);
  width: 36px;
  text-transform: uppercase;
}

.bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.bar .fill {
  height: 100%;
  transition: width 0.3s;
}

.bar .fill.green { background: var(--term-accent); }
.bar .fill.yellow { background: #f59e0b; }
.bar .fill.orange { background: #f97316; }

/* 城市地图 */
.city-map {
  position: absolute;
  inset: 0;
  background: var(--term-bg);
  overflow: hidden;
}

.city-sky {
  position: absolute;
  inset: 0;
}

.city-grid {
  position: absolute;
  inset: -50%;
  width: 200%;
  height: 200%;
  background-image: 
    linear-gradient(var(--term-accent-glow, rgba(0, 255, 136, 0.1)) 1px, transparent 1px),
    linear-gradient(90deg, var(--term-accent-glow, rgba(0, 255, 136, 0.1)) 1px, transparent 1px);
  background-size: 80px 80px;
  transform: perspective(500px) rotateX(60deg);
  opacity: 0.4;
}

/* 建筑标记 */
.building-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.building-visual {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.building-img {
  width: 140px;
  max-width: 20vw;
  height: auto;
  image-rendering: pixelated;
  filter: drop-shadow(0 12px 20px rgba(0,0,0,0.5));
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 2;
  animation: building-float 6s ease-in-out infinite;
}

@keyframes building-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* 当图片加载失败时显示fallback */
.building-img:not([style*="display: none"]) + .marker-box.fallback {
  display: none;
}

.marker-box {
  width: 50px;
  height: 50px;
  background: var(--term-bg);
  border: 2px solid var(--term-text);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  box-shadow: 4px 4px 0 rgba(0,0,0,0.1);
}

.marker-icon {
  font-size: 24px;
}

.building-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 800;
  color: var(--term-text);
  background: var(--term-panel-bg);
  padding: 6px 12px;
  border: 2px solid var(--term-border);
  opacity: 0.9;
  transition: all 0.2s;
  white-space: nowrap;
  box-shadow: 4px 4px 0 rgba(0,0,0,0.2);
  text-transform: uppercase;
}

.building-tag {
  font-size: 10px;
  color: var(--term-text-secondary);
  display: none;
}

/* Hover Effects */
.building-marker:hover .building-img {
  transform: scale(1.15) translateY(-12px);
  filter: drop-shadow(0 30px 50px rgba(0,0,0,0.6)) brightness(1.1);
  animation-play-state: paused;
}

.building-marker:hover .marker-box {
  background: var(--term-accent);
  border-color: var(--term-text);
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 rgba(0,0,0,0.2);
}

.building-marker:hover .marker-icon {
  color: #000;
}

.building-marker:hover .building-label {
  opacity: 1;
  color: #000;
  background: var(--term-accent);
  border-color: #000;
  transform: translateY(4px);
  box-shadow: 6px 6px 0 rgba(0,0,0,0.3);
}

/* 建筑视图 */
.building-view {
  flex: 1;
  overflow: auto;
}

/* CRT效果 */
.crt-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1000;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.15) 0px,
    rgba(0, 0, 0, 0.15) 1px,
    transparent 1px,
    transparent 2px
  );
}

.grid-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: -1;
  background-image: radial-gradient(circle, var(--term-accent-glow, rgba(0, 255, 136, 0.03)) 1px, transparent 1px);
  background-size: 20px 20px;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar-nav {
    position: fixed;
    left: -280px;
    top: 0;
    bottom: 0;
    transition: left 0.3s;
  }
  
  .sidebar-nav.open {
    left: 0;
  }
  
  .close-sidebar-btn {
    display: block;
  }
  
  .menu-btn {
    display: block;
  }
  
  .status-overlay {
    position: fixed;
    left: 10px;
    top: 70px;
    right: 10px;
  }
  
  .status-card {
    width: 100%;
  }
  
  .building-img {
    width: 80px;
  }
  
  .building-label {
    font-size: 10px;
    padding: 4px 8px;
  }
}
</style>
