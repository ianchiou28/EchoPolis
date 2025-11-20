<template>
  <div class="home-container">
    <!-- 飘字组件 -->
    <FloatingText ref="floatingTextRef" />

    <!-- Canvas城市背景 -->
    <CityTopDown 
      :districts="districts" 
      :selected-district-id="activeZone"
      :echo-trigger="echoTrigger"
      @district-click="handleDistrictClick" 
    />

    <!-- 左侧角色面板 -->
    <aside class="left-panel glass-panel tech-border">
      <div class="panel-decoration top-left"></div>
      <div class="panel-decoration bottom-right"></div>
      
      <div class="avatar-section">
        <div class="avatar-portrait-container">
          <div class="avatar-portrait">
            <div class="digital-core">
              <div class="core-ring inner"></div>
              <div class="core-ring outer"></div>
              <div class="core-dot"></div>
            </div>
          </div>
          <div class="portrait-ring"></div>
        </div>
        <div class="avatar-info">
          <div class="info-header">
            <h2>{{ avatar?.name || 'Echo' }}</h2>
            <span class="mbti-tag">{{ avatar?.mbti_type || 'INTJ' }}</span>
          </div>
          <p class="month-indicator">CYCLE: {{ currentMonthDisplay.toString().padStart(3, '0') }} // SYSTEM_ACTIVE</p>
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
          <span class="trust-label">NEURAL SYNC RATE // 神经同步率</span>
          <span class="trust-value">{{ trustLevel }}%</span>
        </div>
        <div class="trust-visual">
          <svg viewBox="0 0 100 10" class="trust-bar-svg">
            <rect x="0" y="0" width="100" height="10" fill="rgba(255,255,255,0.1)" rx="2" />
            <rect 
              x="0" y="0" 
              :width="trustLevel" 
              height="10" 
              fill="url(#trust-gradient)" 
              rx="2"
              class="trust-fill-anim"
            />
            <defs>
              <linearGradient id="trust-gradient" x1="0" x2="1" y1="0" y2="0">
                <stop offset="0%" stop-color="#3b82f6" />
                <stop offset="100%" stop-color="#8b5cf6" />
              </linearGradient>
            </defs>
          </svg>
          <div class="trust-markers">
            <span v-for="i in 5" :key="i" class="marker" :style="{ left: (i * 20) + '%' }"></span>
          </div>
        </div>
      </div>

      <!-- 聊天记录区域 (恢复功能) -->
      <div class="comm-log-section">
        <div class="comm-header">
          <span class="icon">📡</span> SYSTEM LOGS // 系统日志
        </div>
        <div class="comm-messages custom-scrollbar" ref="echoMessagesRef">
          <transition-group name="msg-fade">
            <div 
              v-for="msg in recentChatMessages" 
              :key="msg.timestamp"
              :class="['comm-message', msg.role]">
              <div class="msg-content">
                <span class="msg-role">{{ msg.role === 'user' ? 'USER' : 'CORE' }} >></span>
                {{ msg.text }}
              </div>
            </div>
          </transition-group>
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
        :macro-indicators="macroIndicators"
      />
    </aside>

    <!-- 中央任务面板 (位置调整 + 可折叠) -->
    <div class="center-panel-container" :class="{ 'collapsed': isPanelCollapsed }">
      <button class="collapse-btn" @click="isPanelCollapsed = !isPanelCollapsed">
        {{ isPanelCollapsed ? 'EXPAND TACTICAL VIEW // 展开战术视图 ▲' : 'MINIMIZE // 最小化 ▼' }}
      </button>

      <div class="center-mission-panel glass-panel tech-border">
        <div class="panel-decoration top-right"></div>
        <div class="panel-decoration bottom-left"></div>

        <div class="panel-content custom-scrollbar">
        <header class="mission-header">
          <div class="header-content">
            <p class="eyebrow">TACTICAL OVERVIEW // 战术概览</p>
            <h3>{{ currentSituation?.title || '等待指令输入...' }}</h3>
          </div>
          <button 
            class="btn primary ai-btn"
            :disabled="gameStore.isAiInvesting" 
            @click="handleAiInvest">
            <span class="btn-icon">🤖</span>
            {{ gameStore.isAiInvesting ? 'AI 运算中…' : 'AI 决策辅助' }}
          </button>
        </header>

        <div class="terminal-display">
          <p class="story-text">{{ currentSituation?.description || '城市系统待机中。请选择区域接入或推进时间线。' }}</p>
        </div>

        <!-- AI思考过程 -->
        <div class="ai-thoughts" v-if="currentSituation?.ai_thoughts">
          <div class="thoughts-header">
            <span class="icon-pulse"></span>
            <strong>AI CORE ANALYSIS</strong>
          </div>
          <p class="typing-effect">{{ currentSituation.ai_thoughts }}</p>
        </div>

        <!-- 决策影响展示 -->
        <div class="decision-impact" v-if="lastDecisionImpact">
          <div class="impact-grid">
            <div class="impact-item" v-if="lastDecisionImpact.cash_change">
              <span class="icon">CREDITS</span>
              <span :class="['value', lastDecisionImpact.cash_change > 0 ? 'positive' : 'negative']">
                {{ lastDecisionImpact.cash_change > 0 ? '▲' : '▼' }}{{ formatNumber(Math.abs(lastDecisionImpact.cash_change)) }}
              </span>
            </div>
            <div class="impact-item" v-if="lastDecisionImpact.happiness_change">
              <span class="icon">MORALE</span>
              <span :class="['value', lastDecisionImpact.happiness_change > 0 ? 'positive' : 'negative']">
                {{ lastDecisionImpact.happiness_change > 0 ? '▲' : '▼' }}{{ Math.abs(lastDecisionImpact.happiness_change) }}
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
            <div class="option-header">
              <span class="option-id">OPT-{{ idx + 1 }}</span>
              <div class="selection-indicator"></div>
            </div>
            <p>{{ option }}</p>
          </div>
        </div>

        <!-- 意识回响输入区 -->
        <div class="echo-zone">
          <div class="echo-header">
            <span class="echo-title">NEURAL UPLINK // 意识上传</span>
            <div class="echo-types">
              <button 
                v-for="type in echoTypes" 
                :key="type.value"
                @click="echoType = type.value"
                :class="['type-btn', { 'active': echoType === type.value }]">
                {{ type.label }}
              </button>
            </div>
          </div>
          <div class="echo-input-group">
            <span class="prompt-char">></span>
            <textarea 
              v-model="echoText" 
              placeholder="输入指令以干预系统演化..."
              rows="1"
              class="echo-textarea"
              @keydown.enter.prevent="handleAdvance"
            ></textarea>
            <button class="transmit-btn" @click="handleAdvance" :disabled="gameStore.isAdvancingMonth">
              TRANSMIT
            </button>
          </div>
        </div>
        </div>
      </div>
    </div>

    <!-- 底部AI对话框 -->
    <div class="bottom-chat-panel glass-panel tech-border">
      <form class="chat-form" @submit.prevent="sendChat">
        <span class="chat-prompt">AI_CORE:~$</span>
        <input 
          v-model="chatText" 
          type="text" 
          placeholder="建立直接通讯链路..." 
          class="chat-input"
        />
      </form>
    </div>

    <!-- 顶部控制按钮 (恢复功能) -->
    <div class="top-controls">
      <button 
        class="btn ghost" 
        :disabled="gameStore.isAdvancingMonth" 
        @click="handleAdvance">
        {{ gameStore.isAdvancingMonth ? 'PROCESSING...' : 'NEXT CYCLE // 下个周期 >>' }}
      </button>
      <button class="btn primary" @click="$router.push('/world')">
        WORLD MAP // 世界地图
      </button>
      <button class="btn ghost" @click="$router.push('/assets')">
        ASSETS // 资产管理
      </button>
      <button class="btn ghost" @click="showCharacterSelect = true">
        CHARACTERS // 角色档案
      </button>
      <button class="btn ghost" @click="$router.push('/profile')">
        SYSTEM TERMINAL // 系统终端
      </button>
    </div>

    <!-- 角色选择弹窗 (恢复) -->
    <Teleport to="body">
      <transition name="modal">
        <div v-if="showCharacterSelect" class="modal-overlay" @click="showCharacterSelect = false">
          <div class="character-modal glass-panel" @click.stop>
            <div class="modal-header">
              <h2>IDENTITY SELECT // 身份切换</h2>
              <button class="btn-close" @click="showCharacterSelect = false">✕</button>
            </div>
            <div class="modal-body custom-scrollbar">
              <div class="characters-grid">
                <div 
                  v-for="char in availableCharacters" 
                  :key="char.id"
                  @click="switchCharacter(char)"
                  :class="['character-card', { active: char.id === currentCharacterId }]">
                  <div class="character-avatar">
                    <div class="avatar-icon">{{ (char.mbti || char.mbti_type || 'IN').substring(0, 2) }}</div>
                  </div>
                  <div class="character-info">
                    <h4>{{ char.name }}</h4>
                    <p class="mbti">{{ char.mbti || char.mbti_type || 'INTJ' }}</p>
                    <p class="assets">ASSETS: ¥{{ formatNumber(char.assets || 0) }}</p>
                  </div>
                </div>
              </div>
              <button class="btn primary full" @click="$router.push('/character-select')">
                + INITIALIZE NEW IDENTITY
              </button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>

    <!-- 设置弹窗 (恢复) -->
    <Teleport to="body">
      <transition name="modal">
        <div v-if="showSettings" class="modal-overlay" @click="showSettings = false">
          <div class="settings-modal glass-panel" @click.stop>
            <div class="modal-header">
              <h2>SYSTEM CONFIG // 系统设置</h2>
              <button class="btn-close" @click="showSettings = false">✕</button>
            </div>
            <div class="modal-body custom-scrollbar">
              <div class="settings-section">
                <h3>AUDIO</h3>
                <div class="setting-item">
                  <span>BGM</span>
                  <button @click="toggleMusic" :class="['toggle-btn', { active: musicEnabled }]">
                    <span class="toggle-slider"></span>
                  </button>
                </div>
                <div class="setting-item">
                  <span>SFX</span>
                  <button @click="toggleSound" :class="['toggle-btn', { active: soundEnabled }]">
                    <span class="toggle-slider"></span>
                  </button>
                </div>
              </div>
              <div class="settings-section">
                <h3>ACCOUNT</h3>
                <div class="setting-item">
                  <span>USER</span>
                  <span class="setting-value">{{ username }}</span>
                </div>
                <button class="btn ghost full" @click="handleLogout">
                  LOGOUT
                </button>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
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
const echoMessagesRef = ref(null)

const chatText = ref('')
const echoText = ref('')
const echoType = ref('advisory')
const selectedOption = ref(null)
const lastDecisionImpact = ref(null)
const echoTrigger = ref(null)
const isPanelCollapsed = ref(false)
const showCharacterSelect = ref(false)
const showSettings = ref(false)
const availableCharacters = ref([])
const musicEnabled = ref(false)
const soundEnabled = ref(true)

const username = computed(() => localStorage.getItem('username') || 'COMMANDER')
const currentCharacterId = computed(() => {
  try {
    const char = JSON.parse(localStorage.getItem('currentCharacter') || '{}')
    return char.id
  } catch {
    return null
  }
})

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
  { label: 'NET WORTH // 净资产', value: `¥${formatNumber(assets.value.total)}` },
  { label: 'LIQUIDITY // 流动资金', value: `¥${formatNumber(assets.value.cash)}` },
  { label: 'ASSETS // 总资产', value: `¥${formatNumber(avatar.value?.invested_assets || 0)}` },
  { label: 'PASSIVE INC // 被动收入', value: `+¥${formatNumber(monthlyIncome.value)}` }
])

const macroIndicators = computed(() => gameStore.macroIndicators || {
  inflation: 2.4,
  interest: 4.5,
  market_idx: 12450,
  market_trend: 'up'
})

const recentChatMessages = computed(() => {
  return (gameStore.chatMessages || []).slice(-6)
})

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
    const echo = echoText.value.trim() || null
    
    // 触发视觉特效
    if (echo) {
      echoTrigger.value = { 
        timestamp: Date.now(),
        districtId: activeZone.value || 1 
      }
    }

    await gameStore.advanceMonth(echo)
    
    // 飘字效果
    await nextTick()
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
            `${prefix}${formatNumber(impact.cash_change)} CR`,
            centerX - 100,
            centerY + offsetY,
            type
          )
          offsetY += 40
        }
        if (impact.happiness_change) {
          const type = impact.happiness_change > 0 ? 'positive' : 'negative'
          const prefix = impact.happiness_change > 0 ? '+' : ''
          floatingTextRef.value.addFloatingText(
            `${prefix}${impact.happiness_change} MORALE`,
            centerX + 50,
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

const switchCharacter = async (character) => {
  try {
    const characterData = {
      id: character.id,
      name: character.name,
      mbti: character.mbti,
      assets: character.assets
    }
    localStorage.setItem('currentCharacter', JSON.stringify(characterData))
    localStorage.setItem('session_id', character.id)
    
    showCharacterSelect.value = false
    await gameStore.loadAvatar()
    location.reload()
  } catch (error) {
    alert('切换角色失败: ' + error.message)
  }
}

const loadAvailableCharacters = async () => {
  try {
    const username = localStorage.getItem('username')
    if (!username) return
    
    const response = await fetch(`/api/characters/${username}`)
    if (response.ok) {
      availableCharacters.value = await response.json()
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
  }
}

const toggleMusic = () => {
  musicEnabled.value = !musicEnabled.value
  localStorage.setItem('musicEnabled', musicEnabled.value)
}

const toggleSound = () => {
  soundEnabled.value = !soundEnabled.value
  localStorage.setItem('soundEnabled', soundEnabled.value)
}

const handleLogout = () => {
  if (confirm('TERMINATE SESSION?')) {
    localStorage.removeItem('username')
    localStorage.removeItem('currentCharacter')
    localStorage.removeItem('session_id')
    location.href = '/login'
  }
}

onMounted(async () => {
  themeStore.applyTheme()
  musicEnabled.value = localStorage.getItem('musicEnabled') === 'true'
  soundEnabled.value = localStorage.getItem('soundEnabled') !== 'false'
  
  await gameStore.bootstrapHome()
  await loadAvailableCharacters()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');

.home-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-dark);
  font-family: 'Rajdhani', sans-serif;
  color: var(--text-primary);
}

/* 通用面板样式 - 高级感升级 */
/* .glass-panel 样式已移至全局 game-theme.css */

.glass-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 16px;
  background: radial-gradient(
    800px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), 
    rgba(255, 255, 255, 0.03),
    transparent 40%
  );
  pointer-events: none;
  z-index: 0;
}

.tech-border {
  /* 移除切角效果，改回圆角 */
  border-radius: 16px;
}

.tech-border::after {
  display: none;
}

.panel-decoration {
  display: none; /* 移除装饰线 */
}

/* 左侧面板 */
.left-panel {
  position: absolute;
  left: 24px;
  top: 80px;
  width: 320px;
  height: calc(100vh - 160px);
  padding: 24px;
  z-index: 20; /* 提高层级，确保在地图之上 */
  display: flex;
  flex-direction: column;
}

.avatar-section {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  align-items: center;
  flex-shrink: 0;
}

.avatar-portrait-container {
  position: relative;
  width: 70px;
  height: 70px;
}

.avatar-portrait {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(59, 130, 246, 0.5);
  background: #0f172a;
}

.portrait-ring {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 1px dashed rgba(59, 130, 246, 0.3);
  animation: spin 20s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.info-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  background: linear-gradient(to right, #fff, #94a3b8);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
}

.mbti-tag {
  font-size: 12px;
  background: rgba(59, 130, 246, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  color: #60a5fa;
  font-weight: 600;
}

.month-indicator {
  margin: 4px 0 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  font-family: monospace;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 24px;
  flex-shrink: 0;
}

.stat-item {
  background: rgba(255, 255, 255, 0.03);
  padding: 10px;
  border-left: 2px solid rgba(59, 130, 246, 0.3);
}

.stat-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  font-family: 'Rajdhani', monospace;
  letter-spacing: 1px;
  color: var(--text-primary);
  text-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

.trust-section {
  background: rgba(59, 130, 246, 0.05);
  padding: 16px;
  border: 1px solid rgba(59, 130, 246, 0.1);
  margin-bottom: 20px;
  flex-shrink: 0;
}

.trust-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 600;
}

.trust-value {
  color: #60a5fa;
  font-family: monospace;
}

.trust-visual {
  position: relative;
  height: 10px;
}

.trust-bar-svg {
  width: 100%;
  height: 100%;
}

.trust-markers {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.marker {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(0, 0, 0, 0.5);
}

/* 聊天记录区域 */
.comm-log-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.comm-header {
  padding: 8px 12px;
  background: rgba(59, 130, 246, 0.1);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #93c5fd;
  border-bottom: 1px solid rgba(59, 130, 246, 0.1);
}

.comm-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comm-message {
  font-size: 12px;
  line-height: 1.4;
  padding: 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.03);
}

.comm-message.user {
  border-left: 2px solid #10b981;
}

.comm-message.assistant {
  border-left: 2px solid #3b82f6;
}

.msg-role {
  font-weight: 700;
  font-size: 10px;
  opacity: 0.7;
  margin-right: 4px;
}

/* 右侧面板 */
.right-panel {
  position: absolute;
  right: 24px;
  top: 80px;
  width: 360px;
  height: calc(100vh - 160px);
  z-index: 20; /* 提高层级 */
}

/* 中央面板容器 - 负责定位 */
.center-panel-container {
  position: absolute;
  bottom: 90px; /* 位于聊天栏上方 */
  left: 50%;
  transform: translateX(-50%);
  width: min(700px, 90vw);
  z-index: 25; /* 比左右面板更高 */
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* 内部面板 - 负责外观 */
.center-mission-panel {
  width: 100%;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
  transition: all 0.4s ease;
  /* 确保圆角不被内容溢出破坏 */
  overflow: hidden; 
}

.panel-content {
  padding: 24px;
  overflow-y: auto;
  /* 减去头部和底部留白 */
  max-height: 55vh; 
}

/* 按钮样式 - 位于面板上方 */
.collapse-btn {
  position: relative;
  margin-bottom: -2px; /* 稍微覆盖面板边框 */
  background: rgba(5, 8, 16, 0.95);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-bottom: none;
  color: #60a5fa;
  font-size: 10px;
  padding: 6px 24px;
  border-radius: 8px 8px 0 0;
  cursor: pointer;
  z-index: 20;
  letter-spacing: 1px;
  font-weight: 600;
  box-shadow: 0 -5px 15px rgba(0,0,0,0.3);
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  background: rgba(59, 130, 246, 0.1);
  color: #fff;
}

/* 折叠状态 */
.center-panel-container.collapsed {
  /* 仅水平居中，不再下移，避免遮挡底部聊天框 */
  transform: translateX(-50%); 
}

/* 折叠时完全隐藏面板内容 */
.center-panel-container.collapsed .center-mission-panel {
  max-height: 0;
  opacity: 0;
  margin: 0;
  padding: 0;
  border: none;
  pointer-events: none;
}

.mission-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 12px;
}

.eyebrow {
  font-size: 10px;
  letter-spacing: 2px;
  color: #60a5fa;
  margin-bottom: 6px;
}

.mission-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  text-transform: uppercase;
}

.ai-btn {
  font-size: 12px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.terminal-display {
  font-family: monospace;
  background: rgba(0, 0, 0, 0.3);
  padding: 16px;
  border-left: 2px solid #60a5fa;
  margin-bottom: 20px;
}

.story-text {
  line-height: 1.6;
  color: #cbd5e1;
  font-size: 14px;
}

.ai-thoughts {
  margin: 20px 0;
  padding: 16px;
  background: rgba(139, 92, 246, 0.05);
  border: 1px dashed rgba(139, 92, 246, 0.3);
}

.thoughts-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #a78bfa;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.icon-pulse {
  width: 6px;
  height: 6px;
  background: #a78bfa;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.decision-impact {
  margin: 16px 0;
  animation: slideIn 0.4s ease-out;
}

.impact-grid {
  display: flex;
  gap: 16px;
}

.impact-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
}

.impact-item .icon {
  color: rgba(255, 255, 255, 0.5);
  font-size: 10px;
}

.impact-item .value.positive { color: #34d399; }
.impact-item .value.negative { color: #f87171; }

.options-grid {
  display: grid;
  gap: 12px;
  margin: 24px 0;
}

.option-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.option-card:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
}

.option-card.selected {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
}

.option-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.option-id {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  font-family: monospace;
}

.selection-indicator {
  width: 8px;
  height: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
}

.option-card.selected .selection-indicator {
  background: #3b82f6;
  border-color: #3b82f6;
  box-shadow: 0 0 8px #3b82f6;
}

.echo-zone {
  margin-top: 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 20px;
}

.echo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.echo-title {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 1px;
}

.type-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.6);
  padding: 4px 10px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn.active {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
  color: #fff;
}

.echo-input-group {
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 4px;
}

.prompt-char {
  padding: 0 12px;
  color: #3b82f6;
  font-weight: bold;
}

.echo-textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  padding: 12px 0;
  font-family: monospace;
  resize: none;
}

.echo-textarea:focus {
  outline: none;
}

.transmit-btn {
  background: #3b82f6;
  color: #000;
  border: none;
  padding: 8px 16px;
  font-weight: 700;
  font-size: 11px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s;
}

.transmit-btn:hover:not(:disabled) {
  background: #60a5fa;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
}

/* 底部对话框 */
.bottom-chat-panel {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  width: min(600px, 90vw);
  padding: 12px 20px;
  z-index: 10;
}

.chat-form {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-prompt {
  color: #10b981;
  font-family: monospace;
  font-size: 13px;
}

.chat-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-family: monospace;
  font-size: 14px;
}

.chat-input:focus {
  outline: none;
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

/* .btn 样式已移至全局 game-theme.css */
.btn {
  font-family: 'Rajdhani', sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Digital Core Styles */
.digital-core {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 70%);
}

.core-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(59, 130, 246, 0.6);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
}

.core-ring.inner {
  width: 40%;
  height: 40%;
  border-left-color: transparent;
  border-right-color: transparent;
  animation: spin 4s linear infinite;
}

.core-ring.outer {
  width: 70%;
  height: 70%;
  border-top-color: transparent;
  border-bottom-color: transparent;
  animation: spin 8s linear infinite reverse;
  opacity: 0.7;
}

.core-dot {
  width: 6px;
  height: 6px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 0 10px #fff, 0 0 20px #3b82f6;
  animation: pulse 2s infinite;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.character-modal, .settings-modal {
  width: min(600px, 90vw);
  max-height: 80vh;
  overflow-y: auto;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  letter-spacing: 1px;
}

.btn-close {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.characters-grid {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.character-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.character-card:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
}

.character-card.active {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.2);
}

.avatar-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.character-info h4 {
  margin: 0 0 4px 0;
}

.character-info p {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.settings-section {
  margin-bottom: 24px;
}

.settings-section h3 {
  font-size: 12px;
  color: #60a5fa;
  margin-bottom: 12px;
  letter-spacing: 1px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.toggle-btn {
  width: 40px;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  position: relative;
  border: none;
  cursor: pointer;
}

.toggle-btn.active {
  background: #3b82f6;
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.2s;
}

.toggle-btn.active .toggle-slider {
  transform: translateX(20px);
}

.btn.full {
  width: 100%;
  margin-top: 12px;
}

/* 滚动条样式已移至全局 game-theme.css */
</style>
