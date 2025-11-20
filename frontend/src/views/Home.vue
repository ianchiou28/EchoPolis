<template>
  <div class="home-container">
    <!-- 飘字组件 -->
    <FloatingText ref="floatingTextRef" />
    
    <!-- 俯视城市地图背景 -->
    <CityTopDown />

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

      <!-- AI意识回响区域 -->
      <div class="ai-echo-section">
        <div class="echo-header">
          <span class="echo-icon">🧠</span>
          <h3>意识回响</h3>
        </div>
        <div class="echo-messages" ref="echoMessagesRef">
          <transition-group name="message-fade" tag="div">
            <div 
              v-for="msg in recentChatMessages" 
              :key="msg.timestamp"
              :class="['echo-message', msg.role]">
              <div v-if="msg.role === 'user'" class="user-message">
                <div class="message-content">{{ msg.text }}</div>
              </div>
              <div v-else class="ai-message">
                <div class="ai-response">
                  <div class="response-label">🤖 回应</div>
                  <div class="response-text">{{ msg.text }}</div>
                </div>
                <div v-if="msg.reflection" class="ai-reflection">
                  <div class="reflection-label">💭 反思</div>
                  <div class="reflection-text">{{ msg.reflection }}</div>
                </div>
                <div v-if="msg.monologue" class="ai-monologue">
                  <div class="monologue-label">🌌 独白</div>
                  <div class="monologue-text">{{ msg.monologue }}</div>
                </div>
              </div>
            </div>
          </transition-group>
          <div v-if="gameStore.isChatting" class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
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
    <div class="center-mission-panel glass-panel" :class="{ 'panel-collapsed': isPanelCollapsed }">
      <button class="panel-toggle" @click="isPanelCollapsed = !isPanelCollapsed">
        {{ isPanelCollapsed ? '📋 展开任务' : '✕ 收起' }}
      </button>
      
      <div class="panel-content" v-show="!isPanelCollapsed">
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
    </div>

    <!-- 底部AI对话框 -->
    <div class="bottom-chat-panel glass-panel">
      <div class="chat-status" v-if="gameStore.isChatting">
        <span class="pulse-dot"></span>
        <span class="status-text">AI正在思考...</span>
      </div>
      <form class="chat-form" @submit.prevent="sendChat">
        <div class="input-wrapper">
          <span class="input-icon">🧠</span>
          <input 
            v-model="chatText" 
            type="text" 
            placeholder="向AI城市发送意识回响..." 
            class="chat-input"
            :disabled="gameStore.isChatting"
          />
        </div>
        <button 
          class="btn-send" 
          type="submit"
          :disabled="gameStore.isChatting || !chatText.trim()">
          <span class="send-icon">{{ gameStore.isChatting ? '⏳' : '⚡' }}</span>
          <span class="send-text">{{ gameStore.isChatting ? '思考中' : '发送' }}</span>
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
        🌍 沙盘世界
      </button>
      <button class="btn primary" @click="$router.push('/assets')">
        📊 资产分析
      </button>
      <button class="btn ghost" @click="$router.push('/character-select')">
        🎭 切换角色
      </button>
      <button class="btn ghost" @click="themeStore.toggleTheme()">
        {{ themeStore.isDark ? '☀️' : '🌙' }} 切换主题
      </button>
      <button class="btn ghost" @click="$router.push('/profile')">
        🖥️ 系统终端
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import CityTopDown from '../components/home/CityTopDown.vue'
import InvestmentDashboard from '../components/InvestmentDashboard.vue'
import FloatingText from '../components/FloatingText.vue'
import { useGameStore } from '../stores/game'
import { useThemeStore } from '../stores/theme'

const gameStore = useGameStore()
const themeStore = useThemeStore()
const floatingTextRef = ref(null)

const chatText = ref('')
const echoText = ref('')
const echoType = ref('advisory')
const selectedOption = ref(null)
const lastDecisionImpact = ref(null)
const isPanelCollapsed = ref(false)

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

const recentChatMessages = computed(() => {
  return (gameStore.chatMessages || []).slice(-6) // 只显示最近6条
})

const echoMessagesRef = ref(null)

// 自动滚动到最新消息
watch(() => gameStore.chatMessages?.length, () => {
  nextTick(() => {
    if (echoMessagesRef.value) {
      echoMessagesRef.value.scrollTop = echoMessagesRef.value.scrollHeight
    }
  })
})

const formatNumber = (num) => Number(num || 0).toLocaleString('zh-CN')

const handleAdvance = async () => {
  try {
    // 记录推进前的资产
    const prevCash = assets.value.cash
    const prevHealth = avatar.value?.health || 0
    const prevHappiness = avatar.value?.happiness || 0
    
    const echo = echoText.value.trim() || null
    await gameStore.advanceMonth(echo)
    
    // 等待DOM更新
    await nextTick()
    
    // 显示变化飘字
    if (floatingTextRef.value) {
      const centerX = window.innerWidth / 2
      const centerY = window.innerHeight / 2
      
      const impact = gameStore.currentSituation?.decision_impact
      if (impact) {
        let offsetY = 0
        
        if (impact.cash_change) {
          const type = impact.cash_change > 0 ? 'positive' : 'negative'
          const prefix = impact.cash_change > 0 ? '+' : ''
          floatingTextRef.value.addFloatingText(
            `${prefix}${formatNumber(impact.cash_change)} 💰`,
            centerX - 100,
            centerY + offsetY,
            type
          )
          offsetY += 40
        }
        
        if (impact.health_change) {
          const type = impact.health_change > 0 ? 'positive' : 'negative'
          const prefix = impact.health_change > 0 ? '+' : ''
          floatingTextRef.value.addFloatingText(
            `${prefix}${impact.health_change} ❤️`,
            centerX + 50,
            centerY + offsetY,
            type
          )
          offsetY += 40
        }
        
        if (impact.happiness_change) {
          const type = impact.happiness_change > 0 ? 'positive' : 'negative'
          const prefix = impact.happiness_change > 0 ? '+' : ''
          floatingTextRef.value.addFloatingText(
            `${prefix}${impact.happiness_change} 😊`,
            centerX - 50,
            centerY + offsetY,
            type
          )
        }
      }
    }
    
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
  console.log('[Home] 组件挂载')
  themeStore.applyTheme()
  
  // 加载游戏数据
  await gameStore.bootstrapHome()
  
  console.log('[Home] 加载完成')
})
</script>

<style scoped>
.home-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-dark);
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

/* AI意识回响区域 */
.ai-echo-section {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  height: 320px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(59,130,246,0.15));
  border: 1px solid rgba(139,92,246,0.3);
  overflow: hidden;
}

.echo-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(10,14,39,0.6);
  border-bottom: 1px solid rgba(139,92,246,0.3);
}

.echo-icon {
  font-size: 20px;
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { 
    filter: drop-shadow(0 0 4px rgba(139,92,246,0.6));
    transform: scale(1);
  }
  50% { 
    filter: drop-shadow(0 0 8px rgba(139,92,246,0.9));
    transform: scale(1.1);
  }
}

.echo-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.5px;
}

.echo-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.echo-messages::-webkit-scrollbar {
  width: 4px;
}

.echo-messages::-webkit-scrollbar-track {
  background: rgba(15,23,42,0.5);
}

.echo-messages::-webkit-scrollbar-thumb {
  background: rgba(139,92,246,0.5);
  border-radius: 2px;
}

.echo-message {
  animation: message-slide-in 0.3s ease-out;
}

@keyframes message-slide-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-fade-enter-active {
  transition: all 0.3s ease-out;
}

.message-fade-leave-active {
  transition: all 0.2s ease-in;
}

.message-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.message-fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* 用户消息 */
.user-message {
  align-self: flex-end;
  max-width: 80%;
}

.user-message .message-content {
  background: linear-gradient(135deg, rgba(59,130,246,0.3), rgba(99,102,241,0.3));
  border: 1px solid rgba(59,130,246,0.4);
  padding: 8px 12px;
  border-radius: 12px 12px 2px 12px;
  font-size: 13px;
  color: var(--text);
  line-height: 1.5;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

/* AI消息 */
.ai-message {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 90%;
}

.ai-response {
  background: linear-gradient(135deg, rgba(139,92,246,0.25), rgba(168,85,247,0.25));
  border: 1px solid rgba(139,92,246,0.4);
  border-radius: 12px 12px 12px 2px;
  padding: 10px;
  box-shadow: 0 2px 10px rgba(139,92,246,0.3);
}

.response-label {
  font-size: 10px;
  font-weight: 700;
  color: rgba(168,85,247,1);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.response-text {
  font-size: 13px;
  color: var(--text);
  line-height: 1.6;
}

.ai-reflection {
  background: rgba(20,184,166,0.2);
  border-left: 3px solid rgba(20,184,166,0.6);
  padding: 8px 10px;
  border-radius: 6px;
  margin-left: 12px;
}

.reflection-label {
  font-size: 10px;
  font-weight: 700;
  color: rgba(20,184,166,1);
  margin-bottom: 3px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.reflection-text {
  font-size: 12px;
  color: rgba(255,255,255,0.85);
  line-height: 1.5;
  font-style: italic;
}

.ai-monologue {
  background: rgba(236,72,153,0.15);
  border-left: 3px solid rgba(236,72,153,0.5);
  padding: 8px 10px;
  border-radius: 6px;
  margin-left: 12px;
}

.monologue-label {
  font-size: 10px;
  font-weight: 700;
  color: rgba(236,72,153,1);
  margin-bottom: 3px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.monologue-text {
  font-size: 11px;
  color: rgba(255,255,255,0.75);
  line-height: 1.4;
  font-style: italic;
  opacity: 0.9;
}

/* 打字中指示器 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
  background: rgba(139,92,246,0.2);
  border-radius: 12px;
  width: fit-content;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(139,92,246,0.8);
  animation: typing-bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-bounce {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
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

/* 中央任务面板 - 移到底部 */
.center-mission-panel {
  position: absolute;
  bottom: 90px;
  left: 50%;
  transform: translateX(-50%);
  width: min(720px, 92vw);
  max-height: 55vh;
  overflow-y: auto;
  padding: 24px;
  z-index: 15;
  transition: all 0.3s ease;
  box-shadow: 0 -4px 40px rgba(0,0,0,0.6);
}

.center-mission-panel.panel-collapsed {
  width: auto;
  max-height: none;
  padding: 0;
  background: transparent !important;
  border: none !important;
  backdrop-filter: none !important;
  box-shadow: none !important;
  bottom: 90px;
}

.panel-toggle {
  position: relative;
  z-index: 10;
  padding: 12px 32px;
  border-radius: 24px;
  background: rgba(10,14,39,0.95);
  border: 1px solid rgba(59,130,246,0.4);
  color: var(--text);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

.panel-toggle:hover {
  border-color: rgba(59,130,246,0.8);
  box-shadow: 0 4px 30px rgba(59,130,246,0.4);
  transform: translateY(-2px);
}

.panel-content {
  margin-top: 12px;
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

/* 底部对话框 - 高级设计 */
.bottom-chat-panel {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: min(720px, 90vw);
  padding: 0;
  z-index: 10;
  background: linear-gradient(135deg, rgba(10,14,39,0.95), rgba(30,27,75,0.95));
  border: 1px solid rgba(139,92,246,0.4);
  box-shadow: 0 8px 32px rgba(139,92,246,0.3), 0 0 60px rgba(0,0,0,0.5);
  overflow: hidden;
}

.chat-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(90deg, rgba(139,92,246,0.2), rgba(168,85,247,0.2));
  border-bottom: 1px solid rgba(139,92,246,0.3);
  animation: status-pulse 2s ease-in-out infinite;
}

@keyframes status-pulse {
  0%, 100% { opacity: 0.8; }
  50% { opacity: 1; }
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(168,85,247,1);
  box-shadow: 0 0 10px rgba(168,85,247,0.8);
  animation: pulse-scale 1.5s ease-in-out infinite;
}

@keyframes pulse-scale {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.7; }
}

.status-text {
  font-size: 12px;
  font-weight: 600;
  color: rgba(168,85,247,1);
  letter-spacing: 0.5px;
}

.chat-form {
  display: flex;
  gap: 0;
  padding: 12px;
}

.input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  font-size: 18px;
  opacity: 0.7;
  pointer-events: none;
  animation: icon-float 3s ease-in-out infinite;
}

@keyframes icon-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

.chat-input {
  flex: 1;
  padding: 14px 16px 14px 46px;
  border-radius: 12px 0 0 12px;
  background: rgba(15,23,42,0.9);
  border: 1px solid rgba(139,92,246,0.3);
  border-right: none;
  color: var(--text);
  font-family: inherit;
  font-size: 14px;
  transition: all 0.3s ease;
}

.chat-input:focus {
  outline: none;
  background: rgba(20,20,50,0.95);
  border-color: rgba(139,92,246,0.6);
  box-shadow: inset 0 0 20px rgba(139,92,246,0.1);
}

.chat-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-send {
  padding: 14px 24px;
  border-radius: 0 12px 12px 0;
  background: linear-gradient(135deg, rgba(139,92,246,0.8), rgba(168,85,247,0.8));
  border: 1px solid rgba(139,92,246,0.6);
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn-send::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s ease;
}

.btn-send:hover:not(:disabled)::before {
  left: 100%;
}

.btn-send:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(139,92,246,1), rgba(168,85,247,1));
  box-shadow: 0 0 20px rgba(139,92,246,0.6);
  transform: translateY(-1px);
}

.btn-send:active:not(:disabled) {
  transform: translateY(0);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(100,100,120,0.5);
}

.send-icon {
  font-size: 16px;
}

.btn-send:disabled .send-icon {
  animation: icon-rotate 2s linear infinite;
}

@keyframes icon-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.send-text {
  font-size: 13px;
  letter-spacing: 0.5px;
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

.btn.full {
  width: 100%;
}

.btn.soft {
  background: rgba(148,163,184,0.1);
  border: 1px solid rgba(148,163,184,0.3);
  color: var(--text-primary);
}

/* 弹窗样式 - 统一风格 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.75);
  backdrop-filter: blur(20px) saturate(150%);
  -webkit-backdrop-filter: blur(20px) saturate(150%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
  animation: overlay-fade-in 0.3s ease-out;
}

@keyframes overlay-fade-in {
  from {
    opacity: 0;
    backdrop-filter: blur(0px);
  }
  to {
    opacity: 1;
    backdrop-filter: blur(20px);
  }
}

.character-modal,
.settings-modal {
  width: min(700px, 90vw);
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.95) 100%);
  backdrop-filter: blur(30px) saturate(150%);
  -webkit-backdrop-filter: blur(30px) saturate(150%);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 20px;
  box-shadow: 
    0 25px 60px rgba(0,0,0,0.5),
    0 0 0 1px rgba(59,130,246,0.2),
    inset 0 1px 0 rgba(255,255,255,0.1),
    0 0 40px rgba(59,130,246,0.15);
  position: relative;
  overflow-y: auto;
  animation: modal-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px 32px 24px;
  border-bottom: 1px solid rgba(59,130,246,0.2);
  position: relative;
  z-index: 2;
  background: linear-gradient(180deg, rgba(59,130,246,0.08) 0%, transparent 100%);
}

.modal-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(59,130,246,0.6), transparent);
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.5px;
  text-shadow: 0 2px 8px rgba(59,130,246,0.3);
}

.btn-close {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(148,163,184,0.3);
  background: rgba(15,23,42,0.8);
  color: rgba(148,163,184,0.9);
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.btn-close::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle, rgba(239,68,68,0.3), transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.btn-close:hover {
  border-color: rgba(239,68,68,0.6);
  color: rgb(248,113,113);
  transform: rotate(90deg) scale(1.1);
  box-shadow: 0 0 20px rgba(239,68,68,0.4);
}

.btn-close:hover::before {
  opacity: 1;
}

.modal-body {
  padding: 28px 32px 32px;
  flex: 1;
  overflow-y: auto;
  position: relative;
  z-index: 2;
}

.modal-body::-webkit-scrollbar {
  width: 8px;
}

.modal-body::-webkit-scrollbar-track {
  background: rgba(15,23,42,0.5);
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(59,130,246,0.6), rgba(139,92,246,0.6));
  border-radius: 4px;
  border: 2px solid rgba(15,23,42,0.5);
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(59,130,246,0.8), rgba(139,92,246,0.8));
}

.modal-hint {
  margin: 0 0 24px 0;
  color: rgba(148,163,184,0.9);
  font-size: 14px;
  line-height: 1.6;
  padding: 12px 16px;
  background: rgba(59,130,246,0.08);
  border-left: 3px solid rgba(59,130,246,0.5);
  border-radius: 0 8px 8px 0;
}

/* 角色选择 */
.characters-grid {
  display: grid;
  gap: 16px;
  margin-bottom: 24px;
}

.character-card {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 18px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(15,23,42,0.7), rgba(30,41,59,0.7));
  backdrop-filter: blur(10px);
  border: 1px solid rgba(148,163,184,0.2);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.character-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.character-card:hover {
  border-color: rgba(59,130,246,0.5);
  transform: translateY(-4px);
  box-shadow: 
    0 12px 32px rgba(0,0,0,0.3),
    0 0 30px rgba(59,130,246,0.2);
}

.character-card:hover::before {
  opacity: 1;
}

.character-card.active {
  background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2));
  border-color: rgba(59,130,246,0.6);
  box-shadow: 
    0 8px 24px rgba(59,130,246,0.3),
    inset 0 1px 0 rgba(255,255,255,0.1),
    0 0 40px rgba(59,130,246,0.2);
}

.character-card.active::before {
  opacity: 0.5;
}

.character-avatar {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
}

.avatar-icon {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  color: white;
  box-shadow: 
    0 6px 20px rgba(59,130,246,0.4),
    0 0 0 3px rgba(59,130,246,0.2),
    inset 0 2px 0 rgba(255,255,255,0.2);
  position: relative;
}

.avatar-icon::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  opacity: 0.3;
  filter: blur(8px);
  z-index: -1;
  animation: pulse-ring 3s ease-in-out infinite;
}

@keyframes pulse-ring {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.05);
  }
}

.character-info {
  flex: 1;
}

.character-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.character-info .mbti {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: rgba(59,130,246,0.8);
  font-weight: 600;
}

.character-info .background {
  margin: 0;
  font-size: 13px;
  color: rgba(148,163,184,0.8);
  line-height: 1.5;
}

.character-info .age,
.character-info .assets {
  margin: 0;
  font-size: 13px;
  color: rgba(148,163,184,0.8);
}

/* 当前角色徽章 */
.active-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  padding: 5px 14px;
  border-radius: 14px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  box-shadow: 
    0 4px 12px rgba(59,130,246,0.5),
    0 0 20px rgba(59,130,246,0.3);
  z-index: 3;
  animation: badge-glow 2s ease-in-out infinite;
}

@keyframes badge-glow {
  0%, 100% {
    box-shadow: 
      0 4px 12px rgba(59,130,246,0.5),
      0 0 20px rgba(59,130,246,0.3);
  }
  50% {
    box-shadow: 
      0 4px 16px rgba(59,130,246,0.7),
      0 0 30px rgba(59,130,246,0.5);
  }
}

/* 设置面板样式 */
.settings-section {
  margin-bottom: 28px;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.settings-section h3 {
  margin: 0 0 18px 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.3px;
  position: relative;
  padding-bottom: 10px;
}

.settings-section h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 50px;
  height: 3px;
  background: linear-gradient(90deg, rgba(59,130,246,0.8), transparent);
  border-radius: 2px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid rgba(148,163,184,0.1);
  transition: all 0.2s ease;
}

.setting-item:hover {
  padding-left: 8px;
  border-bottom-color: rgba(59,130,246,0.2);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item > span:first-child {
  font-size: 15px;
  font-weight: 500;
  color: var(--text);
}

.setting-value {
  font-size: 14px;
  color: rgba(148,163,184,0.8);
  font-weight: 600;
}

.about-text {
  margin: 8px 0;
  font-size: 14px;
  color: rgba(148,163,184,0.8);
  line-height: 1.5;
}

/* Toggle开关样式 */
.toggle-btn {
  position: relative;
  width: 54px;
  height: 30px;
  border-radius: 15px;
  background: rgba(148,163,184,0.3);
  border: 1px solid rgba(148,163,184,0.2);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}

.toggle-btn.active {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-color: rgba(59,130,246,0.5);
  box-shadow: 
    0 0 20px rgba(59,130,246,0.4),
    inset 0 1px 0 rgba(255,255,255,0.2);
}

.toggle-slider {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffffff, #f1f5f9);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 2px 8px rgba(0,0,0,0.3),
    0 0 0 1px rgba(255,255,255,0.5);
}

.toggle-btn.active .toggle-slider {
  transform: translateX(24px);
  box-shadow: 
    0 2px 12px rgba(59,130,246,0.5),
    0 0 0 1px rgba(255,255,255,0.8);
}

.toggle-slider {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffffff, #f1f5f9);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 2px 8px rgba(0,0,0,0.3),
    0 0 0 1px rgba(255,255,255,0.5);
}

.toggle-btn.active .toggle-slider {
  transform: translateX(24px);
}

.about-text {
  margin: 8px 0;
  color: rgba(148,163,184,0.8);
  font-size: 14px;
}

/* 弹窗动画 */
@keyframes modal-pop {
  0% {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  60% {
    transform: scale(1.02) translateY(-5px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.character-modal.modal-enter-active,
.settings-modal.modal-enter-active {
  animation: modal-pop 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
</style>
