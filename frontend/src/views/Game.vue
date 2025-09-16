<template>
  <div class="container">
    <!-- 游戏结束遮罩层 -->
    <div v-if="isGameOver" class="game-over-overlay">
      <div class="game-over-box">
        <h1>💀 你已破产 💀</h1>
        <p>你的现金流已断裂，无法再支撑你的生活。</p>
        <p>最终现金: <span class="final-cash">{{ formatMoney(gameStore.avatar.cash) }}</span> CP</p>
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
      <!-- 化身状态面板 -->
      <div class="card avatar-status">
        <h3>🤖 {{ gameStore.avatar.name }} ({{ gameStore.avatar.mbti }})</h3>
        <div class="status-grid-finance">
          <div class="finance-item main">
            <span>💰 总资产:</span>
            <span>{{ formatMoney(gameStore.avatar.total_assets) }} CP</span>
          </div>
          <div class="finance-item">
            <span>💵 现金:</span>
            <span>{{ formatMoney(gameStore.avatar.cash) }} CP</span>
          </div>
          <div class="finance-item">
            <span>🏦 其它资产:</span>
            <span>{{ formatMoney(gameStore.avatar.other_assets) }} CP</span>
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

      <!-- 当前情况 -->
      <div v-if="currentSituation" class="card situation">
        <h3>📋 当前情况 
          <span v-if="currentSituation.ai_generated" class="ai-badge">🤖 AI生成</span>
          <span v-else class="default-badge">🎲 默认</span>
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

      <!-- AI决策结果 -->
      <div v-if="lastDecision" class="card decision-result">
        <h3>🧠 AI决策结果 
          <span v-if="lastEchoAnalysis && lastEchoAnalysis.ai_powered" class="ai-badge">🤖 AI驱动</span>
          <span v-else class="default-badge">🎲 规则</span>
        </h3>
        <div class="decision-content">
          <p><strong>选择:</strong> {{ lastDecision.chosen_option }}</p>
          <p><strong>AI想法:</strong> {{ lastDecision.ai_thoughts }}</p>
          <div class="changes">
            <div v-if="lastDecision.cash_change" class="credit-change" :class="lastDecision.cash_change > 0 ? 'positive' : 'negative'">
              💵 现金: {{ lastDecision.cash_change > 0 ? '+' : '' }}{{ formatMoney(lastDecision.cash_change) }} CP
            </div>
            <div v-if="lastDecision.other_assets_change" class="credit-change" :class="lastDecision.other_assets_change > 0 ? 'positive' : 'negative'">
              🏦 其它资产: {{ lastDecision.other_assets_change > 0 ? '+' : '' }}{{ formatMoney(lastDecision.other_assets_change) }} CP
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

const router = useRouter()
const gameStore = useGameStore()
const echoText = ref('')
const currentSituation = ref(null)
const lastDecision = ref(null)
const lastEchoAnalysis = ref(null)
const isLoading = ref(false)
const isGameOver = ref(false)

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

const processDecisionResult = (result) => {
  lastDecision.value = result.decision
  lastEchoAnalysis.value = result.echo_analysis || { ai_powered: result.decision.ai_powered }
  if (result.game_over) {
    isGameOver.value = true
  }
}

onMounted(() => {
  if (!gameStore.avatar) {
    router.push('/')
    return
  }
  generateSituation()
})

const generateSituation = async () => {
  if (isLoading.value || isGameOver.value) return
  isLoading.value = true
  try {
    currentSituation.value = await gameStore.generateSituation()
    lastDecision.value = null
    lastEchoAnalysis.value = null
  } catch (error) {
    handleApiError('生成新情况', error)
  } finally {
    isLoading.value = false
  }
}

const sendEcho = async () => {
  if (!echoText.value.trim() || isLoading.value || isGameOver.value) return
  isLoading.value = true
  try {
    const result = await gameStore.sendEcho(echoText.value)
    processDecisionResult(result)
    echoText.value = ''
  } catch (error) {
    handleApiError('发送回响', error)
  } finally {
    isLoading.value = false
  }
}

const autoDecision = async () => {
  if (isLoading.value || isGameOver.value) return
  isLoading.value = true
  try {
    const result = await gameStore.autoDecision()
    processDecisionResult(result)
  } catch (error) {
    handleApiError('AI自主决策', error)
  } finally {
    isLoading.value = false
  }
}

const restartGame = () => {
  gameStore.reset()
  router.push('/')
}

const formatMoney = (amount) => {
  if (typeof amount !== 'number') return amount
  return new Intl.NumberFormat('zh-CN').format(amount)
}
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

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>