<template>
  <div class="home-container">
    <!-- Canvas城市背景 -->
    <CityCanvasEnhanced 
      :districts="districts" 
      :selected-district-id="activeZone"
      @district-click="handleDistrictClick" 
    />

    <!-- 左侧角色面板 -->
    <aside class="left-panel glass-panel">
      <div class="avatar-section">
        <div class="avatar-portrait">
          <div class="face-outline">
            <div class="eye left" />
            <div class="eye right" />
            <div class="mouth" />
          </div>
        </div>
        <div class="avatar-info">
          <h2>{{ avatar?.name || 'Echo' }}</h2>
          <p class="mbti">{{ avatar?.mbti_type || 'INTJ' }}</p>
          <p class="month">第 {{ currentMonthDisplay }} 月</p>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-item" v-for="stat in coreStats" :key="stat.label">
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-value">{{ stat.value }}</div>
        </div>
      </div>

      <div class="trust-section">
        <div class="trust-header">
          <span>🤝 信任度</span>
          <span class="trust-value">{{ trustLevel }}%</span>
        </div>
        <div class="trust-bar">
          <div class="trust-fill" :style="{ width: trustLevel + '%' }"></div>
        </div>
      </div>
    </aside>

    <!-- 右侧投资数据看板 -->
    <aside class="right-panel">
      <InvestmentDashboard
        :total-assets="assets.total"
        :cash="assets.cash"
        :invested="avatar?.invested_assets || 0"
        :investments="assets.investments"
        :monthly-income="monthlyIncome"
      />
    </aside>

    <!-- 中央任务面板 -->
    <div class="center-mission-panel glass-panel">
      <header class="mission-header">
        <div>
          <p class="eyebrow">MISSION LOG</p>
          <h3>{{ currentSituation?.title || '选择城区开始冒险' }}</h3>
        </div>
        <button 
          class="btn primary"
          :disabled="gameStore.isAiInvesting" 
          @click="handleAiInvest">
          {{ gameStore.isAiInvesting ? 'AI 思考中…' : '🤖 AI 投资建议' }}
        </button>
      </header>

      <p class="story-text">{{ currentSituation?.description || '城市正等待你的指令。' }}</p>

      <!-- AI思考过程 -->
      <div class="ai-thoughts" v-if="currentSituation?.ai_thoughts">
        <div class="thoughts-header">
          <span class="icon">🤔</span>
          <strong>AI 的思考</strong>
        </div>
        <p>{{ currentSituation.ai_thoughts }}</p>
      </div>

      <!-- 决策影响展示 -->
      <div class="decision-impact" v-if="lastDecisionImpact">
        <div class="impact-grid">
          <div class="impact-item" v-if="lastDecisionImpact.cash_change">
            <span class="icon">💰</span>
            <span :class="['value', lastDecisionImpact.cash_change > 0 ? 'positive' : 'negative']">
              {{ lastDecisionImpact.cash_change > 0 ? '+' : '' }}{{ formatNumber(lastDecisionImpact.cash_change) }}
            </span>
          </div>
          <div class="impact-item" v-if="lastDecisionImpact.happiness_change">
            <span class="icon">😊</span>
            <span :class="['value', lastDecisionImpact.happiness_change > 0 ? 'positive' : 'negative']">
              {{ lastDecisionImpact.happiness_change > 0 ? '+' : '' }}{{ lastDecisionImpact.happiness_change }}
            </span>
          </div>
          <div class="impact-item" v-if="lastDecisionImpact.health_change">
            <span class="icon">❤️</span>
            <span :class="['value', lastDecisionImpact.health_change > 0 ? 'positive' : 'negative']">
              {{ lastDecisionImpact.health_change > 0 ? '+' : '' }}{{ lastDecisionImpact.health_change }}
            </span>
          </div>
        </div>
      </div>

      <!-- 选项选择 -->
      <div class="options-grid" v-if="situationOptions?.length">
        <div 
          v-for="(option, idx) in situationOptions" 
          :key="idx"
          @click="handleSelectOption(idx)"
          :class="['option-card', { 'selected': selectedOption === idx }]">
          <span class="chip">选项 {{ idx + 1 }}</span>
          <p>{{ option }}</p>
        </div>
      </div>

      <!-- 意识回响输入区 -->
      <div class="echo-zone">
        <div class="echo-types">
          <button 
            v-for="type in echoTypes" 
            :key="type.value"
            @click="echoType = type.value"
            :class="['btn', 'soft', 'small', { 'active': echoType === type.value }]">
            {{ type.icon }} {{ type.label }}
          </button>
        </div>
        <div class="echo-input-group">
          <textarea 
            v-model="echoText" 
            placeholder="输入你的建议影响AI决策..."
            rows="2"
            class="echo-textarea"></textarea>
        </div>
      </div>
    </div>

    <!-- 底部AI对话框 -->
    <div class="bottom-chat-panel glass-panel">
      <form class="chat-form" @submit.prevent="sendChat">
        <input 
          v-model="chatText" 
          type="text" 
          placeholder="与 AI 城市对话..." 
          class="chat-input"
        />
        <button 
          class="btn primary" 
          type="submit"
          :disabled="gameStore.isChatting || !chatText.trim()">
          {{ gameStore.isChatting ? '发送中...' : '发送' }}
        </button>
      </form>
    </div>

    <!-- 顶部控制按钮 -->
    <div class="top-controls">
      <button 
        class="btn ghost" 
        :disabled="gameStore.isAdvancingMonth" 
        @click="handleAdvance">
        {{ gameStore.isAdvancingMonth ? '推进中…' : '⏭️ 推进一月' }}
      </button>
      <button class="btn primary" @click="$router.push('/world')">
        🌍 进入沙盘世界
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import CityCanvasEnhanced from '../components/home/CityCanvasEnhanced.vue'
import InvestmentDashboard from '../components/InvestmentDashboard.vue'
import { useGameStore } from '../stores/game'
import { useThemeStore } from '../stores/theme'

const gameStore = useGameStore()
const themeStore = useThemeStore()

const chatText = ref('')
const echoText = ref('')
const echoType = ref('advisory')
const selectedOption = ref(null)
const lastDecisionImpact = ref(null)

const echoTypes = [
  { value: 'inspirational', label: '启发', icon: '💡' },
  { value: 'advisory', label: '建议', icon: '📋' },
  { value: 'directive', label: '指令', icon: '⚡' },
  { value: 'emotional', label: '情感', icon: '❤️' }
]

const avatar = computed(() => gameStore.avatar)
const assets = computed(() => ({
  total: gameStore.assets?.total ?? 0,
  cash: gameStore.assets?.cash ?? 0,
  investments: Array.isArray(gameStore.assets?.investments) ? gameStore.assets.investments : []
}))
const districts = computed(() => gameStore.districts)
const currentSituation = computed(() => gameStore.currentSituation)
const situationOptions = computed(() => gameStore.situationOptions)
const activeZone = computed(() => gameStore.selectedDistrictId)
const trustLevel = computed(() => gameStore.trustLevel || 50)

const monthlyIncome = computed(() => 
  assets.value.investments.reduce((sum, inv) => sum + (inv.monthly_return || 0), 0)
)

const currentMonthDisplay = computed(() => avatar.value?.current_month ?? 0)

const coreStats = computed(() => [
  { label: '总资产', value: `¥${formatNumber(assets.value.total)}` },
  { label: '现金', value: `¥${formatNumber(assets.value.cash)}` },
  { label: '投资', value: `¥${formatNumber(avatar.value?.invested_assets || 0)}` },
  { label: '被动收入', value: `+¥${formatNumber(monthlyIncome.value)}/月` }
])

const formatNumber = (num) => Number(num || 0).toLocaleString('zh-CN')

const handleAdvance = async () => {
  try {
    const echo = echoText.value.trim() || null
    await gameStore.advanceMonth(echo)
    
    echoText.value = ''
    selectedOption.value = null
    
    if (gameStore.currentSituation?.decision_impact) {
      lastDecisionImpact.value = gameStore.currentSituation.decision_impact
      setTimeout(() => {
        lastDecisionImpact.value = null
      }, 5000)
    }
  } catch (error) {
    alert(error.message)
  }
}

const handleSelectOption = (index) => {
  selectedOption.value = index
}

const handleDistrictClick = (district) => {
  gameStore.exploreDistrict(district.id)
}

const handleAiInvest = async () => {
  try {
    await gameStore.requestAiInvestment()
  } catch (error) {
    alert(error.message)
  }
}

const sendChat = async () => {
  const text = chatText.value.trim()
  if (!text) return
  
  chatText.value = ''
  await gameStore.talkToAI(text)
}

onMounted(async () => {
  themeStore.applyTheme()
  await gameStore.bootstrapHome()
})
</script>

<style scoped>
.home-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #030712;
}

.glass-panel {
  background: rgba(10,14,39,0.75);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(2,6,23,0.8);
}

/* 左侧面板 */
.left-panel {
  position: absolute;
  left: 24px;
  top: 80px;
  width: 280px;
  padding: 20px;
  z-index: 10;
}

.avatar-section {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.avatar-portrait {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.face-outline {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #feb48c, #f59e7b);
  border: 3px solid rgba(255,255,255,0.3);
  position: relative;
}

.eye {
  position: absolute;
  top: 30px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #0f172a;
}

.eye.left { left: 22px; }
.eye.right { right: 22px; }

.mouth {
  position: absolute;
  bottom: 22px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 8px;
  border-radius: 0 0 15px 15px;
  background: rgba(15,23,42,0.6);
}

.avatar-info h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
}

.avatar-info .mbti {
  margin: 0;
  font-size: 14px;
  color: rgba(59,130,246,1);
  font-weight: 600;
}

.avatar-info .month {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: rgba(255,255,255,0.6);
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.stat-item {
  padding: 10px;
  border-radius: 8px;
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(148,163,184,0.2);
}

.stat-label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
}

.trust-section {
  padding: 12px;
  border-radius: 10px;
  background: rgba(59,130,246,0.1);
}

.trust-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
}

.trust-value {
  color: rgba(59,130,246,1);
}

.trust-bar {
  height: 6px;
  border-radius: 3px;
  background: rgba(15,23,42,0.8);
  overflow: hidden;
}

.trust-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 3px;
  transition: width 0.5s ease;
}

/* 右侧面板 */
.right-panel {
  position: absolute;
  right: 24px;
  top: 80px;
  width: 340px;
  height: calc(100vh - 240px);
  z-index: 10;
}

/* 中央任务面板 */
.center-mission-panel {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: min(600px, 90vw);
  max-height: 70vh;
  overflow-y: auto;
  padding: 24px;
  z-index: 15;
}

.center-mission-panel::-webkit-scrollbar {
  width: 8px;
}

.center-mission-panel::-webkit-scrollbar-track {
  background: rgba(15,23,42,0.5);
  border-radius: 4px;
}

.center-mission-panel::-webkit-scrollbar-thumb {
  background: rgba(59,130,246,0.5);
  border-radius: 4px;
}

.mission-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 16px;
}

.eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  color: rgba(59,130,246,0.8);
  margin-bottom: 4px;
}

.mission-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
}

.story-text {
  line-height: 1.7;
  color: rgba(255,255,255,0.85);
  margin-bottom: 20px;
}

.ai-thoughts {
  margin: 16px 0;
  padding: 16px;
  border-radius: 12px;
  background: rgba(99,102,241,0.15);
  border: 1px solid rgba(99,102,241,0.4);
}

.thoughts-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
  color: rgb(167,139,250);
}

.decision-impact {
  margin: 16px 0;
  padding: 16px;
  border-radius: 12px;
  background: rgba(16,185,129,0.15);
  border: 1px solid rgba(16,185,129,0.4);
  animation: slideIn 0.5s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
}

.impact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 12px;
}

.impact-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.impact-item .value.positive { color: #10b981; }
.impact-item .value.negative { color: #ef4444; }

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin: 20px 0;
}

.option-card {
  padding: 14px;
  border-radius: 10px;
  border: 1px solid rgba(148,163,184,0.3);
  background: rgba(15,23,42,0.6);
  cursor: pointer;
  transition: all 0.3s ease;
}

.option-card:hover {
  border-color: rgba(59,130,246,0.6);
  background: rgba(59,130,246,0.15);
  transform: translateY(-2px);
}

.option-card.selected {
  border-color: rgb(59,130,246);
  background: rgba(59,130,246,0.3);
  box-shadow: 0 0 20px rgba(59,130,246,0.4);
}

.chip {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  background: rgba(59,130,246,0.3);
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 6px;
}

.echo-zone {
  margin-top: 20px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(15,23,42,0.8);
  border: 1px solid rgba(59,130,246,0.4);
}

.echo-types {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.btn.small {
  padding: 6px 12px;
  font-size: 12px;
}

.btn.active {
  background: rgba(59,130,246,0.4);
  border-color: rgb(59,130,246);
  box-shadow: 0 0 12px rgba(59,130,246,0.5);
}

.echo-textarea {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  background: rgba(15,23,42,0.7);
  border: 1px solid rgba(148,163,184,0.3);
  color: var(--text);
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
}

.echo-textarea:focus {
  outline: none;
  border-color: rgb(59,130,246);
  box-shadow: 0 0 0 2px rgba(59,130,246,0.3);
}

/* 底部对话框 */
.bottom-chat-panel {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  width: min(800px, 90vw);
  padding: 16px;
  z-index: 10;
}

.chat-form {
  display: flex;
  gap: 12px;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(15,23,42,0.8);
  border: 1px solid rgba(148,163,184,0.3);
  color: var(--text);
  font-family: inherit;
  font-size: 14px;
}

.chat-input:focus {
  outline: none;
  border-color: rgb(59,130,246);
  box-shadow: 0 0 0 2px rgba(59,130,246,0.3);
}

/* 顶部控制 */
.top-controls {
  position: absolute;
  top: 24px;
  right: 24px;
  display: flex;
  gap: 12px;
  z-index: 20;
}

.btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn.primary {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  border: none;
}

.btn.primary:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(59,130,246,0.6);
  transform: translateY(-2px);
}

.btn.ghost {
  background: rgba(15,23,42,0.8);
  border: 1px solid rgba(59,130,246,0.5);
  color: var(--text);
}

.btn.ghost:hover:not(:disabled) {
  background: rgba(59,130,246,0.2);
  border-color: rgb(59,130,246);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.soft {
  background: rgba(148,163,184,0.1);
  border: 1px solid rgba(148,163,184,0.3);
  color: var(--text);
}
</style>
