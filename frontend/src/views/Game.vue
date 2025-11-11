<template>
  <div class="container">
    <!-- 游戏结束遮罩层 -->
    <div v-if="isGameOver" class="game-over-overlay">
      <div class="game-over-box">
        <h1>💀 你已破产 💀</h1>
        <p>你的现金流已断裂，无法再支撑你的生活。</p>
        <p>最终现金: <span class="final-cash">{{ formatMoney(gameStore.avatar.credits) }}</span> CP</p>
        <button @click="restartGame" class="btn btn-primary">重新开始</button>
      </div>
    </div>

    <!-- AI思考遮罩层 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-box">
        <span class="spinner"></span>
        <h3>🤖 AI 正在思考中...</h3>
        <p>请稍候，这可能需要一点时间</p>
      </div>
    </div>

    <div v-if="!gameStore.avatar" class="card">
      <p>请先创建AI化身</p>
      <router-link to="/" class="btn btn-primary">返回首页</router-link>
    </div>
    
    <div v-else class="game-interface">
      <!-- 月份和事件日志 -->
      <div class="card time-events-panel">
        <div class="month-display">第 <span>{{ gameStore.avatar.current_round || 1 }}</span> 月</div>
        <div v-if="monthlyEvents.length > 0" class="events-log">
          <h4>本月事件:</h4>
          <ul>
            <li v-for="(event, index) in monthlyEvents" :key="index">{{ event }}</li>
          </ul>
        </div>
      </div>

      <!-- 化身状态面板 -->
      <div class="card avatar-status">
        <h3>🤖 {{ gameStore.avatar.name }} ({{ gameStore.avatar.mbti }})</h3>
        <div class="status-grid-finance">
          <div class="finance-item main">
            <span>💰 总资产:</span>
            <span>{{ formatMoney(gameStore.avatar.total_assets || 0) }} CP</span>
          </div>
          <div class="finance-item">
            <span>💵 现金:</span>
            <span>{{ formatMoney(gameStore.avatar.credits || 0) }} CP</span>
          </div>
          <div class="finance-item">
            <span>🏦 投资中资产:</span>
            <span>{{ formatMoney((gameStore.avatar.long_term_investments || 0) + (gameStore.avatar.locked_investments || []).reduce((sum, inv) => sum + (inv.amount || 0), 0)) }} CP</span>
          </div>
        </div>
        <hr class="status-divider">
        <div class="status-grid-personal">
          <div class="status-item-sm"><span>❤️ 健康:</span> <span>{{ gameStore.avatar.health || 100 }}</span></div>
          <div class="status-item-sm"><span>⚡ 精力:</span> <span>{{ gameStore.avatar.energy || 100 }}</span></div>
          <div class="status-item-sm"><span>😊 幸福:</span> <span>{{ gameStore.avatar.happiness || 100 }}</span></div>
          <div class="status-item-sm"><span>🤝 信任:</span> <span>{{ gameStore.avatar.trust_level || 50 }}</span></div>
        </div>
      </div>

      <!-- 投资管理面板 -->
      <InvestmentPanel 
        :investments="gameInvestments" 
        :transactions="gameTransactions" 
      />

      <!-- 当前情况 -->
      <div v-if="currentSituation" class="card situation">
        <h3>📋 当前情况 
          <span class="ai-badge">🤖 AI生成</span>
        </h3>
        <p class="situation-text">{{ currentSituation.situation }}</p>
        <div class="options">
          <h4>可选择的行动:</h4>
          <div v-for="(option, index) in currentSituation.options" :key="index" class="option">
            {{ index + 1 }}. {{ option }}
          </div>
        </div>
      </div>

      <!-- 意识回响输入 -->
      <div class="card echo-input">
        <h3>💭 发送意识回响</h3>
        <textarea 
          v-model="echoText" 
          placeholder="输入你的建议和想法..."
          class="input echo-textarea"
          :disabled="isLoading || isGameOver"
        ></textarea>
        <div class="action-buttons">
          <button @click="sendEcho" :disabled="!echoText.trim() || isLoading || isGameOver" class="btn btn-primary">
            <span v-if="isLoading">🤖 AI 思考中...</span>
            <span v-else>📡 发送回响</span>
          </button>
          <button @click="autoDecision" :disabled="isLoading || isGameOver" class="btn btn-secondary">
            <span v-if="isLoading">🤖 AI 思考中...</span>
            <span v-else>🤖 AI自主决策</span>
          </button>
          <button @click="generateSituation" :disabled="isLoading || isGameOver" class="btn btn-secondary">
            <span v-if="isLoading">🤖 AI 思考中...</span>
            <span v-else>🎲 生成新情况</span>
          </button>
        </div>
      </div>

      <div v-if="history.length > 0" class="card history-list">
        <div class="history-header">
          <h3>📝 历史记录</h3>
          <button class="btn btn-secondary" v-if="history.length" @click="clearHistory">清空</button>
        </div>
        <ul class="timeline">
          <li v-for="(item, idx) in history" :key="idx" class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-meta">
                <span class="badge">决策</span>
                <span class="meta-text">第{{ item.round || (gameStore.avatar?.current_round || 1) }}月</span>
                <span class="meta-text time">{{ formatTime(item.time) }}</span>
              </div>
              <div class="situation-line">📋 {{ item.situation }}</div>
              <div class="choice-line">✅ 选择：<strong>{{ item.data.chosen_option }}</strong></div>
              <div class="impact-line" v-if="item.data.decision_impact">
                <span v-for="(value, key) in item.data.decision_impact" :key="key"
                      v-if="key !== 'investment_item' && value !== 0"
                      class="impact-chip" :class="value > 0 ? 'positive' : 'negative'">
                  {{ formatKey(key) }} {{ value > 0 ? '+' : '' }}{{ value }}
                </span>
              </div>
              <div class="thoughts">
                <div class="thoughts-label">🧠 AI想法：</div>
                <div class="thoughts-text" :class="{ clamped: !expandedHistory[idx] }">{{ item.data.ai_thoughts }}</div>
                <div class="thoughts-actions">
                  <button class="link" @click="expandedHistory[idx] = !expandedHistory[idx]">
                    {{ expandedHistory[idx] ? '收起' : '展开' }}
                  </button>
                  <button class="link" @click="copyThought(item.data.ai_thoughts)">复制</button>
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- AI决策结果 -->
      <div v-if="lastDecision" class="card decision-result">
        <h3>🧠 AI决策结果 
          <span class="ai-badge">🤖 AI驱动</span>
        </h3>
        <div class="decision-content">
          <p><strong>选择:</strong> {{ lastDecision.chosen_option }}</p>
          <p><strong>AI想法:</strong> {{ lastDecision.ai_thoughts }}</p>
          <div v-if="lastDecision.decision_impact" class="changes">
            <div v-for="(value, key) in lastDecision.decision_impact" :key="key">
              <div v-if="key !== 'investment_item' && value !== 0" 
                   class="credit-change" 
                   :class="value > 0 ? 'positive' : 'negative'">
                {{ formatKey(key) }}: {{ value > 0 ? '+' : '' }}{{ value }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'
import InvestmentPanel from '../components/InvestmentPanel.vue'

const router = useRouter()
const gameStore = useGameStore()
const echoText = ref('')
const currentSituation = ref(null)
const lastDecision = ref(null)
const lastEchoAnalysis = ref(null)
const isLoading = ref(false)
const isGameOver = ref(false)
const monthlyEvents = ref([])

// 统一的错误处理
const handleApiError = (action, error) => {
  console.error(`${action}失败:`, error)
  let message = `操作失败: ${action}\n\n`
  if (error.code === "ERR_NETWORK") {
    message += "无法连接到后端服务。请确认后端服务是否正在运行，以及端口是否正确。"
  } else if (error.response) {
    message += `服务器返回错误: ${error.response.status} - ${error.response.data.detail || '未知错误'}`
  } else {
    message += "发生未知错误。请检查浏览器控制台和后端日志获取更多信息。"
  }
  message += "\n\n提示：AI相关功能需要正确配置API Key。"
  alert(message)
}

const history = ref([])
const expandedHistory = ref({})
const processDecisionResult = async (result) => {
  console.log('[DEBUG] 处理决策结果:', result)
  
  // 确保决策结果显示
  if (result.decision) {
    lastDecision.value = {
      ...result.decision,
      ai_powered: result.decision.ai_powered !== false
    }
    history.value.push({
      type: 'decision',
      data: lastDecision.value,
      situation: currentSituation.value ? currentSituation.value.situation : '',
      round: (result.decision && result.decision.current_round) || (result.avatar && result.avatar.current_round) || (gameStore.avatar && gameStore.avatar.current_round) || 1,
      time: Date.now()
    })
    console.log('[DEBUG] 设置决策结果:', lastDecision.value)
  }
  
  lastEchoAnalysis.value = result.echo_analysis || { ai_powered: true }
  monthlyEvents.value = result.monthly_events || []
  
  // 处理自动生成的下一个情况
  if (result.next_situation && result.next_situation.situation) {
    currentSituation.value = {
      situation: result.next_situation.situation,
      options: result.next_situation.options,
      ai_generated: true
    }
  } else {
    // 如果没有下一个情况，自动生成一个
    setTimeout(() => {
      if (!isLoading.value) {
        generateSituation()
      }
    }, 2000)
  }
  
  if (result.game_over || (result.avatar && result.avatar.credits <= 0)) {
    isGameOver.value = true
  }
  
  // 实时更新投资数据
  await loadInvestmentData()
}

onMounted(() => {
  if (!gameStore.avatar) {
    router.push('/')
    return
  }
  // 先用已有 avatar_data 填充，再尝试从API刷新
  fillFromAvatarData()
  generateSituation()
  loadInvestmentData()
})

const generateSituation = async () => {
  if (isLoading.value || isGameOver.value) return
  isLoading.value = true
  try {
    console.log('[DEBUG] 生成情况')
    console.log('[DEBUG] Session ID:', gameStore.user || gameStore.sessionId)
    
    const situation = await gameStore.generateSituation()
    console.log('[DEBUG] 生成的情况:', situation)
    
    currentSituation.value = {
      ...situation,
      ai_generated: true  // 标记为AI生成
    }
    lastDecision.value = null
    lastEchoAnalysis.value = null
  } catch (error) {
    console.error('[ERROR] 生成情况失败:', error)
    handleApiError('生成新情况', error)
  } finally {
    isLoading.value = false
  }
}

const sendEcho = async () => {
  if (!echoText.value.trim() || isLoading.value || isGameOver.value) return
  isLoading.value = true
  try {
    console.log('[DEBUG] 发送回响:', echoText.value)
    console.log('[DEBUG] Session ID:', gameStore.user || gameStore.sessionId)
    
    const result = await gameStore.sendEcho(echoText.value)
    console.log('[DEBUG] 回响结果:', result)
    
    await processDecisionResult(result)
    echoText.value = ''
  } catch (error) {
    console.error('[ERROR] 发送回响失败:', error)
    handleApiError('发送回响', error)
  } finally {
    isLoading.value = false
  }
}

const autoDecision = async () => {
  if (isLoading.value || isGameOver.value) return
  isLoading.value = true
  try {
    console.log('[DEBUG] AI自主决策')
    console.log('[DEBUG] Session ID:', gameStore.user || gameStore.sessionId)
    
    const result = await gameStore.autoDecision()
    console.log('[DEBUG] AI决策结果:', result)
    
    await processDecisionResult(result)
  } catch (error) {
    console.error('[ERROR] AI决策失败:', error)
    handleApiError('AI自主决策', error)
  } finally {
    isLoading.value = false
  }
}

const restartGame = async () => {
  if (isLoading.value) return
  isLoading.value = true
  try {
    await gameStore.resetGame()
    // 重置本地状态
    currentSituation.value = null
    lastDecision.value = null
    lastEchoAnalysis.value = null
    isGameOver.value = false
    monthlyEvents.value = []
    history.value = []
    gameInvestments.value = []
    gameTransactions.value = []
    echoText.value = ''
    // 先关闭加载态以便 generateSituation 不被短路
    isLoading.value = false
    await generateSituation()
    await loadInvestmentData()
  } catch (e) {
    handleApiError('重新开始', e)
  } finally {
    isLoading.value = false
  }
}

const copyThought = async (text) => {
  try {
    await navigator.clipboard.writeText(text || '')
  } catch (e) {
    console.error('复制失败', e)
  }
}

const clearHistory = () => {
  history.value = []
}

const formatMoney = (amount) => {
  if (typeof amount !== 'number') return amount
  return new Intl.NumberFormat('zh-CN').format(amount)
}

const formatKey = (key) => {
  const names = {
    cash_change: '💵 现金',
    invested_assets_change: '🏦 投资资产',
    health_change: '❤️ 健康',
    happiness_change: '😊 幸福',
    stress_change: '🤯 压力',
    trust_change: '🤝 信任'
  }
  return names[key] || key
}

const formatTime = (t) => {
  if (!t) return ''
  try {
    const d = new Date(t)
    return d.toLocaleTimeString('zh-CN', { hour12: false, hour: '2-digit', minute: '2-digit' })
  } catch { return '' }
}

// 投资和交易数据
const gameInvestments = ref([])
const gameTransactions = ref([])

const fillFromAvatarData = () => {
  const a = gameStore.avatar || {}
  const inv = Array.isArray(a.active_investments) ? a.active_investments : []
  gameInvestments.value = inv.map(x => ({
    name: x.name,
    amount: x.amount,
    type: x.type,
    monthlyReturn: x.monthly_return ?? x.monthlyReturn ?? 0,
    remainingMonths: x.remaining_months ?? x.remainingMonths ?? 0
  }))
  const tx = Array.isArray(a.transaction_history) ? a.transaction_history : []
  gameTransactions.value = tx.map((t, i) => ({
    id: i,
    round: t.round,
    type: t.type || '交易',
    amount: t.amount,
    description: t.description
  }))
}

// 从API获取投资和交易数据
const loadInvestmentData = async () => {
  const avatarId = gameStore.currentAvatarId || (gameStore.avatar && gameStore.avatar.avatar_id)
  if (!avatarId) {
    fillFromAvatarData()
    return
  }
  try {
    // 获取投资数据（按化身）
    const investmentResponse = await fetch(`http://127.0.0.1:8000/api/avatar/${avatarId}/investments`)
    if (investmentResponse.ok) {
      const investments = await investmentResponse.json()
      gameInvestments.value = investments.map(inv => ({
        name: inv.name,
        amount: inv.amount,
        type: inv.type,
        monthlyReturn: inv.monthly_return,
        remainingMonths: inv.remaining_months
      }))
    } else {
      // 回退：使用 avatar_data
      fillFromAvatarData()
    }
    // 获取交易数据（按化身）
    const transactionResponse = await fetch(`http://127.0.0.1:8000/api/avatar/${avatarId}/transactions`)
    if (transactionResponse.ok) {
      const transactions = await transactionResponse.json()
      gameTransactions.value = transactions.map((tx, index) => ({
        id: index,
        round: tx.round,
        type: tx.type,
        amount: tx.amount,
        description: tx.description
      }))
    } else {
      // 回退：使用 avatar_data
      fillFromAvatarData()
    }
  } catch (error) {
    console.error('加载投资数据失败:', error)
    fillFromAvatarData()
  }
}

onMounted(() => {
  if (!gameStore.avatar) {
    router.push('/')
    return
  }
  // 先用已有 avatar_data 填充，再尝试从API刷新
  fillFromAvatarData()
  generateSituation()
  loadInvestmentData()
})
</script>

<style scoped>
.game-over-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
  color: white;
  text-align: center;
}
.game-over-box {
  padding: 40px;
  background: #1a1a1a;
  border-radius: 20px;
  box-shadow: 0 0 30px rgba(255, 0, 0, 0.5);
}
.game-over-box h1 {
  color: #dc3545;
  font-size: 3rem;
}
.final-cash {
  color: #dc3545;
  font-weight: bold;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  color: white;
}

.loading-box {
  text-align: center;
  padding: 30px;
  background: #2c3e50;
  border-radius: 15px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}

.spinner {
  display: inline-block;
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { -webkit-transform: rotate(360deg); }
}

.status-divider {
  border: 0;
  height: 1px;
  background-image: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0));
  margin: 20px 0;
}

.status-grid-finance {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  text-align: center;
}

.finance-item span:first-child {
  font-size: 0.9rem;
  opacity: 0.8;
}

.finance-item span:last-child {
  font-size: 1.4rem;
  font-weight: bold;
  display: block;
}

.finance-item.main span:last-child {
  font-size: 1.8rem;
  color: #f9ca24;
}

.status-grid-personal {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
  text-align: center;
}

.status-item-sm {
  font-size: 0.9rem;
}

.status-item-sm span:last-child {
  font-weight: bold;
  margin-left: 8px;
}

.time-events-panel {
  padding: 15px;
  background: #2c3e50;
  color: white;
  border-left: 4px solid #f39c12;
}

.month-display {
  text-align: center;
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.month-display span {
  color: #f39c12;
}

.events-log h4 {
  margin-bottom: 5px;
}

.events-log ul {
  padding-left: 20px;
  margin: 0;
}

.active-investments ul {
  padding-left: 20px;
  margin: 0;
}

.active-investments li {
  padding: 5px 0;
}

.game-interface {
  display: grid;
  gap: 20px;
}

.avatar-status {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.situation-text {
  font-size: 16px;
  line-height: 1.6;
  margin: 15px 0;
}

.options {
  margin-top: 20px;
}

.option {
  padding: 10px;
  margin: 5px 0;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.echo-textarea {
  min-height: 100px;
  resize: vertical;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 15px;
}

.decision-result {
  background: #e8f5e8;
  border-left: 4px solid #28a745;
}

.decision-content p {
  margin: 10px 0;
  line-height: 1.6;
}

.ai-badge {
  font-size: 12px;
  padding: 2px 8px;
  background: #28a745;
  color: white;
  border-radius: 10px;
  margin-left: 10px;
}

.default-badge {
  font-size: 12px;
  padding: 2px 8px;
  background: #6c757d;
  color: white;
  border-radius: 10px;
  margin-left: 10px;
}

.changes {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.trust-change, .credit-change {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 14px;
}

.trust-change {
  background: #007bff;
  color: white;
}

.credit-change.positive {
  background: #28a745;
  color: white;
}

.credit-change.negative {
  background: #dc3545;
  color: white;
}

/* 历史记录时间轴样式 */
.history-list .history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.timeline { position: relative; margin: 0; padding-left: 26px; }
.timeline:before { content: ''; position: absolute; left: 14px; top: 0; bottom: 0; width: 2px; background: #e6e6e6; }
.timeline-item { position: relative; margin: 12px 0; list-style: none; }
.timeline-dot { position: absolute; left: 7px; top: 8px; width: 14px; height: 14px; background: #667eea; border-radius: 50%; box-shadow: 0 0 0 3px rgba(102,126,234,0.2); }
.timeline-content { background: #f8f9fa; border-radius: 10px; padding: 12px 14px; border-left: 4px solid #667eea; }
.timeline-meta { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }
.badge { background: #e9ecef; border-radius: 12px; padding: 2px 8px; font-size: 12px; color: #333; }
.meta-text { color: #666; font-size: 12px; }
.meta-text.time { margin-left: auto; }
.situation-line { font-weight: 600; margin: 4px 0; }
.choice-line { margin: 4px 0; }
.impact-line { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 8px; }
.impact-chip { font-size: 12px; padding: 4px 8px; border-radius: 12px; background: #eef2ff; color: #3b5bdb; }
.impact-chip.positive { background: #e6f4ea; color: #1e7e34; }
.impact-chip.negative { background: #fdecea; color: #b71c1c; }
.thoughts { margin-top: 8px; }
.thoughts-label { font-size: 12px; color: #666; margin-bottom: 4px; }
.thoughts-text { line-height: 1.6; color: #333; }
.thoughts-text.clamped { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.thoughts-actions { margin-top: 4px; display: flex; gap: 10px; }
button.link { border: none; background: none; color: #667eea; cursor: pointer; padding: 0; font-size: 12px; }

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>