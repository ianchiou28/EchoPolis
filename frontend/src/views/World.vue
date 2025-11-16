<template>
  <GameLayout>
    <!-- 顶部右侧：当前城市状态简要信息 -->
    <template #top-right>
      <div style="display: flex; align-items: center; gap: 12px;">
        <div class="world-status-chip">
          <span class="dot" />
          <span class="label">Echo City · 原型版本</span>
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
          <h2 class="panel-title">城市网络</h2>
          <p class="panel-sub">在不同城区之间穿梭，触发资产与事件</p>
        </header>
        <CityMapPanel
          :active-zone="activeDistrictId"
          @select="onSelectDistrict"
        />
      </section>
    </template>

    <!-- 中间：城市主视图占位（后续替换为 CityCanvas 等更复杂组件） -->
    <template #center>
      <section class="panel-section panel-section--center">
        <!-- 开场文案渐显层 -->
        <transition name="intro-fade">
          <div v-if="showIntro" class="intro-overlay">
            <div class="intro-panel">
              <p
                v-for="(line, idx) in introLines"
                :key="idx"
                class="intro-line"
                :style="{ 'transition-delay': `${idx * 0.2}s` }"
              >
                {{ line }}
              </p>
              <button class="intro-skip" @click="skipIntro">进入城市</button>
            </div>
          </div>
        </transition>

        <header class="panel-header panel-header--center">
          <div class="panel-header-main">
            <h1 class="city-title">EchoPolis 城市总览</h1>
            <p class="city-sub">在这座城市里，你的每一个决策，都会在天际线和街区里留下痕迹。</p>
          </div>
          <div class="panel-header-meta">
            <span class="meta-pill">当前城区：{{ currentDistrictName }}</span>
          </div>
        </header>

        <div
          class="city-canvas-placeholder"
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
            >
              <div class="city-block__name">{{ district.name }}</div>
              <div class="city-block__tag">{{ district.tagline }}</div>
            </div>
          </div>
          <div class="city-hint">城市主视图原型 · 后续将替换为可缩放、可拖拽的城市画布</div>
        </div>
      </section>
    </template>

    <!-- 右侧：区块详情 / 时间轴占位 -->
    <template #right>
      <section class="panel-section">
        <header class="panel-header">
          <h2 class="panel-title">城区详情</h2>
          <p class="panel-sub">查看当前选中城区的特征与机会</p>
        </header>
        <div class="detail-body">
          <div v-if="activeDistrict">
            <h3 class="detail-name">{{ activeDistrict.name }}</h3>
            <p class="detail-tag">{{ activeDistrict.tagline }}</p>
            <p class="detail-desc">{{ activeDistrict.description }}</p>
            
            <button 
              class="btn-explore" 
              @click="showOperationPanel = true"
              :disabled="!sessionId">
              {{ sessionId ? '进入操作' : '请先选择角色' }}
            </button>
          </div>
          <div v-else class="detail-empty">
            <p>从左侧选择一个城区，开始在城市中探索。</p>
          </div>
        </div>
      </section>

      <section class="panel-section panel-section--timeline">
        <header class="panel-header">
          <h2 class="panel-title">时间轴 · 原型</h2>
          <p class="panel-sub">未来会在这里展示城市事件与资产变化记录</p>
        </header>
        <ul class="timeline-list">
          <li class="timeline-item" v-for="item in mockTimeline" :key="item.id">
            <div class="timeline-dot" />
            <div class="timeline-content">
              <div class="timeline-time">T{{ item.turn }}</div>
              <div class="timeline-text">{{ item.text }}</div>
            </div>
          </li>
        </ul>
      </section>
    </template>

    <!-- 底部：导航 / 提示条占位 -->
    <template #bottom>
      <div class="bottom-bar">
        <div class="bottom-left">
          <span class="hint-label">原型阶段：</span>
          <span class="hint-text">当前为城市主视图骨架，后续将接入真实资产与事件。</span>
        </div>
        <div class="bottom-right">
          <button class="nav-btn" @click="$router.push('/home')">
            ← 返回主页
          </button>
          <button class="nav-btn" @click="$router.push('/assets')">
            📊 资产分析
          </button>
        </div>
      </div>
    </template>
  </GameLayout>
  
  <!-- 操作面板弹窗 (移到最外层) -->
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
import { useGameStore } from '../stores/game'

const gameStore = useGameStore()
const activeDistrictId = ref('finance')
const showOperationPanel = ref(false)
const currentCash = computed(() => gameStore.assets?.cash || 0)
const sessionId = computed(() => {
  try {
    const char = JSON.parse(localStorage.getItem('currentCharacter') || '{}')
    return char.id || null
  } catch {
    return null
  }
})

const districts = [
  { id: 'finance', name: '金融高塔', tagline: '资产配置 / 对冲策略', description: '城市的资本心脏，利率、流动性与风险在此汇聚。' },
  { id: 'tech', name: '未来科创区', tagline: '科技初创 / AI 投资', description: '高风险高回报的实验场，新技术每天都在这里诞生。' },
  { id: 'housing', name: '新星住区', tagline: '地产 / 租赁 / 长期持有', description: '城市居民的栖息地，房价、租金与长期现金流在这里交织。' },
  { id: 'learning', name: '知识穹顶', tagline: '教育 / 个人成长', description: '投资大脑而非只投资资产，长期回报藏在书页之间。' },
  { id: 'leisure', name: '文娱街区', tagline: '消费 / 体验经济', description: '城市的情绪出口，消费与体验塑造了人们的记忆。' },
  { id: 'green', name: '绿色能源港', tagline: '能源 / ESG / 可持续', description: '面向未来的基础设施，环境与收益不再对立。' }
]

const activeDistrict = computed(() => districts.find(d => d.id === activeDistrictId.value))

const currentDistrictName = computed(() => activeDistrict.value?.name || '未选择')

const mockTimeline = [
  { id: 1, turn: 1, text: '你抵达 EchoPolis，城市的灯光在远处缓缓亮起。' },
  { id: 2, turn: 2, text: '金融高塔推送了新的资产配置建议。' },
  { id: 3, turn: 3, text: '未来科创区出现一批高增长但高风险的创业项目。' }
]

const onSelectDistrict = (district) => {
  activeDistrictId.value = district.id
  showOperationPanel.value = true
}

const onOperationComplete = async (result) => {
  // 刷新游戏状态
  await gameStore.loadAvatar()
}

const closeOperationPanel = () => {
  showOperationPanel.value = false
}

const showIntro = ref(true)
const introLines = [
  '夜色落在 EchoPolis 的天际线，资产与选择在暗处流动。',
  '你不是路人，而是这座城市的一部分——每个决策，都会被街区记住。',
  '先选一个城区，从一个小小的切口，开始撬动整座城市。'
]

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
  parallax.value = {
    x: offsetX,
    y: offsetY
  }
}

const resetParallax = () => {
  parallax.value = { x: 0, y: 0 }
}

const skipIntro = () => {
  showIntro.value = false
  localStorage.setItem('echopolis_world_intro_seen', '1')
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

onMounted(async () => {
  if (localStorage.getItem('echopolis_world_intro_seen') === '1') {
    showIntro.value = false
  }
  
  // 加载游戏状态
  await gameStore.loadAvatar()
})
</script>

<style scoped>
.world-status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(15,23,42,0.85);
  border: 1px solid rgba(148,163,184,0.4);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
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
}

.panel-sub {
  font-size: 12px;
  color: rgba(148,163,184,0.9);
}

.city-title {
  font-size: 20px;
  font-weight: 600;
}

.city-sub {
  font-size: 13px;
  color: rgba(148,163,184,0.95);
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  background: rgba(15,23,42,0.85);
  border: 1px solid rgba(59,130,246,0.4);
}

.city-canvas-placeholder {
  position: relative;
  flex: 1;
  margin-top: 12px;
  border-radius: 24px;
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
  border-radius: 18px;
  padding: 12px 14px;
  background: linear-gradient(145deg, rgba(15,23,42,0.9), rgba(15,23,42,0.7));
  border: 1px solid rgba(148,163,184,0.5);
  box-shadow: 0 8px 22px rgba(15,23,42,0.8);
  overflow: hidden;
  transition: box-shadow 200ms ease, border-color 200ms ease, transform 200ms ease;
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
  box-shadow: 0 12px 32px rgba(45,212,191,0.45);
}

.city-block--active::before {
  opacity: 1;
}

.city-block--hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 34px rgba(15,23,42,0.95);
}

.city-block__name {
  font-size: 14px;
  font-weight: 600;
}

.city-block__tag {
  font-size: 11px;
  color: rgba(148,163,184,0.9);
}

.city-hint {
  position: absolute;
  left: 16px;
  bottom: 14px;
  font-size: 11px;
  color: rgba(148,163,184,0.85);
}

.detail-body {
  padding: 10px 4px 4px;
  font-size: 13px;
}

.detail-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}

.detail-tag {
  font-size: 12px;
  color: rgba(96,165,250,0.9);
  margin-bottom: 8px;
}

.detail-desc {
  font-size: 13px;
  color: rgba(148,163,184,0.95);
}

.detail-empty {
  font-size: 13px;
  color: rgba(148,163,184,0.9);
}

.panel-section--timeline {
  margin-top: 14px;
}

.timeline-list {
  list-style: none;
  margin: 8px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.timeline-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.timeline-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  margin-top: 4px;
  background: rgba(96,165,250,0.95);
  box-shadow: 0 0 10px rgba(37,99,235,0.9);
}

.timeline-content {
  flex: 1;
}

.timeline-time {
  font-size: 11px;
  color: rgba(148,163,184,0.95);
}

.timeline-text {
  font-size: 13px;
  color: rgba(226,232,240,0.98);
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
}

.hint-label {
  opacity: 0.85;
}

.hint-text {
  opacity: 0.95;
}

.bottom-right {
  display: flex;
  align-items: center;
}

.nav-btn {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid rgba(148,163,184,0.6);
  background: rgba(15,23,42,0.9);
  font-size: 12px;
  cursor: pointer;
}

.nav-btn:hover {
  border-color: rgba(96,165,250,0.9);
}

.intro-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at 50% 0%, rgba(15,23,42,0.86), rgba(15,23,42,0.98));
  pointer-events: auto;
}

.intro-panel {
  max-width: 520px;
  padding: 28px 30px 22px;
  border-radius: 24px;
  background: rgba(15,23,42,0.96);
  border: 1px solid rgba(148,163,184,0.5);
  box-shadow: 0 24px 60px rgba(15,23,42,0.9);
}

.intro-line {
  font-size: 14px;
  color: rgba(226,232,240,0.96);
  line-height: 1.7;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 420ms ease, transform 420ms ease;
}

.intro-panel .intro-line:nth-child(1),
.intro-panel .intro-line:nth-child(2),
.intro-panel .intro-line:nth-child(3) {
  opacity: 1;
  transform: translateY(0);
}

.intro-skip {
  margin-top: 18px;
  padding: 6px 16px;
  border-radius: 999px;
  border: 1px solid rgba(96,165,250,0.8);
  background: rgba(15,23,42,0.95);
  color: rgba(226,232,240,0.96);
  font-size: 12px;
  cursor: pointer;
}

.intro-fade-enter-active,
.intro-fade-leave-active {
  transition: opacity 300ms ease;
}

.intro-fade-enter-from,
.intro-fade-leave-to {
  opacity: 0;
}

.city-canvas-placeholder {
  position: relative;
  flex: 1;
  margin-top: 12px;
  border-radius: 24px;
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
  border-radius: 18px;
  padding: 12px 14px;
  background: linear-gradient(145deg, rgba(15,23,42,0.9), rgba(15,23,42,0.7));
  border: 1px solid rgba(148,163,184,0.5);
  box-shadow: 0 8px 22px rgba(15,23,42,0.8);
  overflow: hidden;
  transition: box-shadow 200ms ease, border-color 200ms ease, transform 200ms ease;
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
  box-shadow: 0 12px 32px rgba(45,212,191,0.45);
}

.city-block--active::before {
  opacity: 1;
}

.city-block--hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 34px rgba(15,23,42,0.95);
}

.city-block__name {
  font-size: 14px;
  font-weight: 600;
}

.city-block__tag {
  font-size: 11px;
  color: rgba(148,163,184,0.9);
}

.city-hint {
  position: absolute;
  left: 16px;
  bottom: 14px;
  font-size: 11px;
  color: rgba(148,163,184,0.85);
}

.detail-body {
  padding: 10px 4px 4px;
  font-size: 13px;
}

.detail-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}

.detail-tag {
  font-size: 12px;
  color: rgba(96,165,250,0.9);
  margin-bottom: 8px;
}

.detail-desc {
  font-size: 13px;
  color: rgba(148,163,184,0.95);
}

.detail-empty {
  font-size: 13px;
  color: rgba(148,163,184,0.9);
}

.panel-section--timeline {
  margin-top: 14px;
}

.timeline-list {
  list-style: none;
  margin: 8px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.timeline-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.timeline-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  margin-top: 4px;
  background: rgba(96,165,250,0.95);
  box-shadow: 0 0 10px rgba(37,99,235,0.9);
}

.timeline-content {
  flex: 1;
}

.timeline-time {
  font-size: 11px;
  color: rgba(148,163,184,0.95);
}

.timeline-text {
  font-size: 13px;
  color: rgba(226,232,240,0.98);
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
}

.hint-label {
  opacity: 0.85;
}

.hint-text {
  opacity: 0.95;
}

.bottom-right {
  display: flex;
  align-items: center;
}

.nav-btn {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid rgba(148,163,184,0.6);
  background: rgba(15,23,42,0.9);
  font-size: 12px;
  cursor: pointer;
}

.nav-btn:hover {
  border-color: rgba(96,165,250,0.9);
}

.intro-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at 50% 0%, rgba(15,23,42,0.86), rgba(15,23,42,0.98));
  pointer-events: auto;
}

.intro-panel {
  max-width: 520px;
  padding: 28px 30px 22px;
  border-radius: 24px;
  background: rgba(15,23,42,0.96);
  border: 1px solid rgba(148,163,184,0.5);
  box-shadow: 0 24px 60px rgba(15,23,42,0.9);
}

.intro-line {
  font-size: 14px;
  color: rgba(226,232,240,0.96);
  line-height: 1.7;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 420ms ease, transform 420ms ease;
}

.intro-panel .intro-line:nth-child(1),
.intro-panel .intro-line:nth-child(2),
.intro-panel .intro-line:nth-child(3) {
  opacity: 1;
  transform: translateY(0);
}

.intro-skip {
  margin-top: 18px;
  padding: 6px 16px;
  border-radius: 999px;
  border: 1px solid rgba(96,165,250,0.8);
  background: rgba(15,23,42,0.95);
  color: rgba(226,232,240,0.96);
  font-size: 12px;
  cursor: pointer;
}

.intro-fade-enter-active,
.intro-fade-leave-active {
  transition: opacity 300ms ease;
}

.intro-fade-enter-from,
.intro-fade-leave-to {
  opacity: 0;
}

.btn-explore {
  width: 100%;
  margin-top: 16px;
  padding: 12px 20px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border: none;
  color: white;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-explore:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(59,130,246,0.6);
  transform: translateY(-2px);
}

.btn-explore:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(148,163,184,0.3);
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
