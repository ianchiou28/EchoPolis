<template>
  <GameLayout>
    <!-- 顶部右侧：当前城市状态简要信息 -->
    <template #top-right>
      <div style="display: flex; align-items: center; gap: 12px;">
        <div class="world-status-chip">
          <span class="dot" :class="{ 'online': isConnected }" />
          <span class="label">Echo City · {{ isConnected ? 'ONLINE' : 'OFFLINE' }}</span>
        </div>
        <button class="btn ghost small" @click="$router.push('/home')" style="padding: 8px 16px;">
          ← 返回主页
        </button>
      </div>
    </template>

    <!-- 左侧：玩家 / 城市区块选择 -->
    <template #left>
      <section class="panel-section">
        <header class="panel-header">
          <h2 class="panel-title">CITY NETWORK // 城市网络</h2>
          <p class="panel-sub">NAVIGATE DISTRICTS // 区域导航</p>
        </header>
        <CityMapPanel
          :active-zone="activeDistrictId"
          @select="onSelectDistrict"
          class="tech-border"
        />
      </section>
    </template>

    <!-- 中间：城市主视图 -->
    <template #center>
      <section class="panel-section panel-section--center">
        <header class="panel-header panel-header--center">
          <div class="panel-header-main">
            <h1 class="city-title">FinAI金融模拟沙盘 // 城市总览</h1>
            <p class="city-sub">YOUR DECISIONS SHAPE THE SKYLINE // 你的决策塑造天际线</p>
          </div>
          <div class="panel-header-meta">
            <span class="meta-pill">CURRENT DISTRICT: {{ currentDistrictName }}</span>
          </div>
        </header>

        <div
          class="city-canvas-placeholder tech-border"
          @mousemove="onCanvasMouseMove"
          @mouseleave="resetParallax"
        >
          <div
            class="city-layer city-layer--bg"
            :style="bgParallaxStyle"
          />
          <div
            class="city-layer city-layer--grid"
            :style="gridParallaxStyle"
          />
          <div class="city-layer city-layer--blocks">
            <div
              v-for="district in districts"
              :key="district.id"
              class="city-block"
              :class="{
                'city-block--active': district.id === activeDistrictId,
                'city-block--hover': hoverDistrictId === district.id
              }"
              @mouseenter="hoverDistrictId = district.id"
              @mouseleave="hoverDistrictId = null"
              @click="onSelectDistrict(district)"
            >
              <div class="city-block__icon">{{ getDistrictIcon(district.id) }}</div>
              <div class="city-block__content">
                <div class="city-block__name">{{ district.name }}</div>
                <div class="city-block__tag">{{ district.tagline }}</div>
                <!-- 动态数据展示 -->
                <div class="city-block__stats" v-if="district.stats">
                  <div class="stat-mini">
                    <span class="label">热度</span>
                    <div class="bar"><div class="fill" :style="{ width: (district.stats.heat || 0) * 100 + '%' }"></div></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- 右侧：区块详情 / 时间轴 -->
    <template #right>
      <section class="panel-section" style="z-index: 10; position: relative;">
        <header class="panel-header">
          <h2 class="panel-title">DISTRICT DATA // 城区详情</h2>
          <p class="panel-sub">ANALYSIS & OPPORTUNITIES // 分析与机会</p>
        </header>
        <div class="detail-body glass-panel tech-border">
          <div v-if="activeDistrict">
            <div class="detail-header">
              <span class="detail-icon">{{ getDistrictIcon(activeDistrict.id) }}</span>
              <div>
                <h3 class="detail-name">{{ activeDistrict.name }}</h3>
                <p class="detail-tag">{{ activeDistrict.tagline }}</p>
              </div>
            </div>
            <p class="detail-desc">{{ activeDistrict.description }}</p>
            
            <div class="detail-stats" v-if="activeDistrict.stats">
              <div class="stat-row">
                <span>INFLUENCE // 影响力</span>
                <span class="val">{{ (activeDistrict.stats.influence * 100).toFixed(0) }}%</span>
              </div>
              <div class="stat-row">
                <span>PROSPERITY // 繁荣度</span>
                <span class="val">{{ (activeDistrict.stats.prosperity * 100).toFixed(0) }}%</span>
              </div>
            </div>

            <button 
              class="btn primary full-width" 
              @click="showOperationPanel = true"
              :disabled="!sessionId">
              {{ sessionId ? 'ACCESS OPERATIONS // 进入操作' : 'SELECT CHARACTER // 请先选择角色' }}
            </button>
          </div>
          <div v-else class="detail-empty">
            <p>SELECT A DISTRICT // 请选择城区</p>
          </div>
        </div>
      </section>

      <section class="panel-section panel-section--timeline" style="z-index: 10; position: relative;">
        <header class="panel-header">
          <h2 class="panel-title">EVENT STREAM // 城市事件流</h2>
          <p class="panel-sub">REAL-TIME MONITORING // 实时监控</p>
        </header>
        <div class="glass-panel tech-border" style="flex: 1; padding: 12px; overflow: hidden; display: flex; flex-direction: column; background: rgba(15, 23, 42, 0.8);">
          <ul class="timeline-list custom-scrollbar" style="flex: 1; overflow-y: auto;">
            <li class="timeline-item" v-for="item in recentEvents" :key="item.id">
              <div class="timeline-dot" :class="item.type" />
              <div class="timeline-content">
                <div class="timeline-time">{{ formatTime(item.timestamp) }}</div>
                <div class="timeline-title">{{ item.title }}</div>
                <div class="timeline-text">{{ item.description }}</div>
              </div>
            </li>
            <li v-if="recentEvents.length === 0" class="timeline-empty">
              NO RECENT EVENTS // 暂无事件
            </li>
          </ul>
        </div>
      </section>
    </template>

    <!-- 底部：导航 -->
    <template #bottom>
      <div class="bottom-bar">
        <div class="bottom-left">
          <span class="hint-label">SYSTEM:</span>
          <span class="hint-text">城市网络连接正常。数据实时同步中。</span>
        </div>
        <div class="bottom-right">
          <button class="btn ghost" @click="$router.push('/home')">
            ← 返回主页
          </button>
          <button class="btn ghost" @click="$router.push('/assets')">
            📊 资产分析
          </button>
        </div>
      </div>
    </template>
  </GameLayout>
  
  <!-- 操作面板弹窗 -->
  <transition name="modal-fade">
    <div v-if="showOperationPanel" class="operation-modal-overlay" @click="closeOperationPanel">
      <transition name="panel-slide">
        <WorldOperationPanel
          v-if="showOperationPanel && activeDistrict"
          :district-id="activeDistrict.id"
          :district-name="activeDistrict.name"
          :district-tagline="activeDistrict.tagline"
          :district-icon="getDistrictIcon(activeDistrict.id)"
          :session-id="sessionId"
          :current-cash="currentCash"
          @close="closeOperationPanel"
          @operation-complete="onOperationComplete"
          class="world-operation-panel"
          @click.stop
        />
      </transition>
    </div>
  </transition>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import GameLayout from '../components/GameLayout.vue'
import CityMapPanel from '../components/CityMapPanel.vue'
import WorldOperationPanel from '../components/WorldOperationPanel.vue'
import { useGameStore, DISTRICT_META } from '../stores/game'

const gameStore = useGameStore()
const activeDistrictId = ref('finance')
const showOperationPanel = ref(false)
const isConnected = ref(true)

const currentCash = computed(() => gameStore.assets?.cash || 0)
const sessionId = computed(() => {
  try {
    const char = JSON.parse(localStorage.getItem('currentCharacter') || '{}')
    return char.id || null
  } catch {
    return null
  }
})

// 从 Store 获取真实区域数据，并确保包含所有元数据
const districts = computed(() => {
  const storeDistricts = gameStore.districts || []
  return Object.values(DISTRICT_META).map(meta => {
    // 尝试匹配 store 中的数据
    const storeData = storeDistricts.find(d => d.id === meta.id || d.district_id === meta.id) || {}
    return {
      ...meta,
      ...storeData,
      stats: {
        heat: storeData.heat || 0.5,
        influence: storeData.influence || 0.5,
        prosperity: storeData.prosperity || 0.5
      }
    }
  })
})

const activeDistrict = computed(() => districts.value.find(d => d.id === activeDistrictId.value))
const currentDistrictName = computed(() => activeDistrict.value?.name || '未选择')

// 获取最近事件
const recentEvents = computed(() => {
  return (gameStore.cityEvents || []).slice().reverse().slice(0, 10)
})

const onSelectDistrict = (district) => {
  activeDistrictId.value = district.id
  // 自动打开面板
  showOperationPanel.value = true 
}

const onOperationComplete = async (result) => {
  await gameStore.loadAvatar()
  await gameStore.loadCityState()
}

const closeOperationPanel = () => {
  showOperationPanel.value = false
}

const hoverDistrictId = ref(null)
const parallax = ref({ x: 0, y: 0 })

const bgParallaxStyle = computed(() => ({
  transform: `translate3d(${parallax.value.x * 6}px, ${parallax.value.y * 6}px, 0)`
}))

const gridParallaxStyle = computed(() => ({
  transform: `translate3d(${parallax.value.x * 10}px, ${parallax.value.y * 10}px, 0)`
}))

const onCanvasMouseMove = (event) => {
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

const getDistrictIcon = (districtId) => {
  const icons = {
    finance: '🏦',
    tech: '💹',
    housing: '🏙️',
    learning: '📚',
    leisure: '🎭',
    green: '⚡'
  }
  return icons[districtId] || '🏢'
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

onMounted(async () => {
  try {
    await gameStore.loadAvatar()
    await gameStore.loadCityState()
  } catch (e) {
    console.error('Failed to load world data:', e)
  }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap');

.world-status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 4px;
  background: rgba(15,23,42,0.85);
  border: 1px solid rgba(148,163,184,0.4);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 600;
}

.world-status-chip .dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34,197,94,0.8);
}

.panel-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-section--center {
  height: 100%;
}

.panel-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.panel-header--center {
  margin-bottom: 12px;
}

.panel-header-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.panel-header-meta {
  margin-top: 6px;
}

.panel-title {
  font-size: 14px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(226,232,240,0.95);
  font-family: 'Rajdhani', sans-serif;
  font-weight: 700;
}

.panel-sub {
  font-size: 10px;
  color: rgba(148,163,184,0.9);
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.city-title {
  font-size: 24px;
  font-weight: 700;
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 2px;
  text-transform: uppercase;
  background: linear-gradient(90deg, #fff, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.city-sub {
  font-size: 12px;
  color: rgba(148,163,184,0.95);
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 1px;
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 2px;
  font-size: 11px;
  background: rgba(15,23,42,0.85);
  border: 1px solid rgba(59,130,246,0.4);
  font-family: 'Rajdhani', sans-serif;
  color: #3b82f6;
  font-weight: 600;
}

.city-canvas-placeholder {
  position: relative;
  flex: 1;
  margin-top: 12px;
  border-radius: 4px;
  overflow: hidden;
  background: radial-gradient(circle at 10% 0%, rgba(56,189,248,0.16), transparent 60%),
              radial-gradient(circle at 90% 100%, rgba(94,234,212,0.16), transparent 55%),
              linear-gradient(180deg, rgba(15,23,42,0.96), rgba(15,23,42,0.9));
  border: 1px solid rgba(30,64,175,0.6);
  box-shadow: 0 18px 45px rgba(15,23,42,0.9);
  padding: 18px;
  display: flex;
  align-items: stretch;
  justify-content: center;
}

.city-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.city-layer--bg {
  background-image: radial-gradient(circle at 50% -10%, rgba(59,130,246,0.35), transparent 55%);
  opacity: 0.7;
}

.city-layer--grid {
  background-image: linear-gradient(rgba(15,23,42,0.95) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(15,23,42,0.95) 1px, transparent 1px);
  background-size: 40px 40px;
  mix-blend-mode: soft-light;
  opacity: 0.7;
}

.city-layer--blocks {
  position: relative;
  padding: 8px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  align-content: center;
}

.city-block {
  position: relative;
  border-radius: 4px;
  padding: 12px 14px;
  background: linear-gradient(145deg, rgba(15,23,42,0.9), rgba(15,23,42,0.7));
  border: 1px solid rgba(148,163,184,0.2);
  box-shadow: 0 8px 22px rgba(15,23,42,0.8);
  overflow: hidden;
  transition: all 0.2s ease;
}

.city-block::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(circle at 10% 0%, rgba(59,130,246,0.4), transparent 55%);
  opacity: 0;
  transition: opacity 200ms ease;
}

.city-block--active {
  border-color: rgba(94,234,212,0.9);
  box-shadow: 0 0 20px rgba(45,212,191,0.2);
}

.city-block--active::before {
  opacity: 1;
}

.city-block--hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 34px rgba(15,23,42,0.95);
  border-color: rgba(59,130,246,0.5);
}

.city-block__name {
  font-size: 14px;
  font-weight: 700;
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.city-block__tag {
  font-size: 10px;
  color: rgba(148,163,184,0.9);
  font-family: 'Rajdhani', sans-serif;
}

.detail-body {
  padding: 16px;
  font-size: 13px;
  background: rgba(15, 23, 42, 0.6);
}

.detail-name {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 4px;
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 1px;
  color: #fff;
}

.detail-tag {
  font-size: 12px;
  color: #60a5fa;
  margin-bottom: 12px;
  font-family: 'Rajdhani', sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.detail-desc {
  font-size: 13px;
  color: rgba(148,163,184,0.95);
  line-height: 1.6;
  margin-bottom: 16px;
}

.detail-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(30, 41, 59, 0.4);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  color: #94a3b8;
}

.stat-row .val {
  color: #e2e8f0;
  font-weight: 700;
}

.detail-empty {
  font-size: 13px;
  color: rgba(148,163,184,0.9);
  font-family: 'Rajdhani', sans-serif;
  text-align: center;
  padding: 20px 0;
}

.panel-section--timeline {
  margin-top: 14px;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.timeline-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.timeline-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.timeline-item:last-child {
  border-bottom: none;
}

.timeline-dot {
  width: 6px;
  height: 6px;
  border-radius: 2px;
  margin-top: 6px;
  background: #3b82f6;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
}

.timeline-content {
  flex: 1;
}

.timeline-time {
  font-size: 10px;
  color: rgba(148,163,184,0.6);
  font-family: 'Rajdhani', sans-serif;
  margin-bottom: 2px;
}

.timeline-title {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 2px;
  font-family: 'Rajdhani', sans-serif;
}

.timeline-text {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.8);
  line-height: 1.4;
}

.bottom-bar {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.bottom-left {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 12px;
  font-family: 'Rajdhani', sans-serif;
}

.hint-label {
  opacity: 0.85;
  color: #3b82f6;
  font-weight: 700;
}

.hint-text {
  opacity: 0.95;
  color: #94a3b8;
}

.bottom-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

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

.full-width {
  width: 100%;
  margin-top: 16px;
}

.operation-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.75);
  backdrop-filter: blur(8px);
  z-index: 1500;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow-y: auto;
}

.world-operation-panel {
  position: relative;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  margin: auto;
}

.world-operation-panel::-webkit-scrollbar {
  width: 8px;
}

.world-operation-panel::-webkit-scrollbar-track {
  background: rgba(15,23,42,0.5);
  border-radius: 4px;
}

.world-operation-panel::-webkit-scrollbar-thumb {
  background: rgba(59,130,246,0.5);
  border-radius: 4px;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.panel-slide-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(-20px);
}

.panel-slide-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}
</style>
