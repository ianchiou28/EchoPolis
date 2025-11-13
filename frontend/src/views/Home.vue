<template>
  <div class="home-page">
    <!-- 左上角：昵称+人格标签 -->
    <div class="header-info">
      <div class="nickname">{{ avatar?.name || '加载中...' }}</div>
      <div class="mbti-tag">{{ avatar?.mbti_type || 'INTJ' }}</div>
      <button class="theme-btn" @click="showThemeSelector = !showThemeSelector">🎨</button>
    </div>

    <!-- 主题选择器 -->
    <div v-if="showThemeSelector" class="theme-selector">
      <div 
        v-for="(theme, key) in themeStore.themes" 
        :key="key"
        class="theme-option"
        :class="{ active: themeStore.currentTheme === key }"
        @click="selectTheme(key)"
      >
        {{ theme.name }}
      </div>
    </div>

    <!-- 右上角：财富等级和信任值 -->
    <div class="top-right-info">
      <div class="wealth-level">
        <span class="label">财富等级</span>
        <span class="value">{{ wealthLevel }}</span>
      </div>
      <div class="trust-level">
        <span class="label">信任值</span>
        <span class="value">{{ trustLevel }}/100</span>
      </div>
      <button class="nav-btn" @click="$router.push('/assets')">📊 资产分析</button>
      <button class="nav-btn" @click="$router.push('/world')">🌆 沙盘世界</button>
      <button class="nav-btn" @click="$router.push('/profile')">👤 我的</button>
      <button class="nav-btn" @click="$router.push('/character-select')">🔄 切换角色</button>
    </div>

    <!-- 主体区域 -->
    <div class="main-content">
      <!-- 左侧信息面板 -->
      <div class="left-panel">
        <div class="info-card">
          <div class="card-title">💰 总资产</div>
          <div class="card-value">¥{{ formatNumber(assets.total) }}</div>
          <div class="card-sub">现金: ¥{{ formatNumber(assets.cash) }}</div>
          <div class="card-sub" v-if="avatar?.invested_assets">投资: ¥{{ formatNumber(avatar.invested_assets) }}</div>
        </div>

        <div class="info-card">
          <div class="card-title">📈 动态收益</div>
          <div class="card-value">+¥{{ formatNumber(monthlyIncome) }}</div>
          <div class="card-sub">本月预计收益</div>
        </div>

        <div class="info-card">
          <div class="card-title">📊 持有标的</div>
          <div class="card-value">{{ investments.length }}个</div>
          <div class="card-sub">投资项目</div>
        </div>

        <div class="info-card">
          <div class="card-title">🎯 人生阶段</div>
          <div class="card-value">{{ lifeStage }}</div>
          <div class="card-sub">第{{ avatar?.current_month || 0 }}个月</div>
        </div>

        <div class="info-card reflection-card">
          <div class="card-title">🧠 AI反思</div>
          <div class="reflection-text">{{ aiReflection }}</div>
        </div>
      </div>

      <!-- 中间：AI机器人交互区 -->
      <div class="center-area">
        <div class="robot-container">
          <div class="robot" :class="robotMood">
            <div class="robot-face">
              <div class="eye left"></div>
              <div class="eye right"></div>
              <div class="mouth"></div>
            </div>
          </div>
        </div>

        <div class="ai-dialogue">
          <div class="dialogue-header">AI内心独白</div>
          <div class="dialogue-content">
            <p class="asset-summary">📊 资产总计: ¥{{ formatNumber(assets.total) }}</p>
            <p class="reflection">{{ aiReflection }}</p>
            <p class="monologue">{{ aiMonologue }}</p>
          </div>
        </div>

        <div v-if="currentSituation" class="situation-box">
          <div class="situation-header">🎯 当前情况</div>
          <div class="situation-content">{{ currentSituation }}</div>
          <div v-if="situationOptions.length > 0" class="situation-options">
            <div class="option-title">选项：</div>
            <div v-for="(opt, idx) in situationOptions" :key="idx" class="option-item">
              {{ idx + 1 }}. {{ opt }}
            </div>
          </div>
        </div>

        <div v-if="aiResponse" class="ai-response">
          <div class="response-header">🤖 AI回应</div>
          <div class="response-content">{{ aiResponse }}</div>
        </div>

        <div class="input-area">
          <input 
            v-model="userInput" 
            type="text" 
            placeholder="对AI说点什么..."
            @keyup.enter="sendMessage"
          />
          <button @click="sendMessage">发送</button>
          <button class="time-btn" @click="advanceTime">⏩ 推进1个月</button>
          <button class="invest-btn" @click="aiInvest">💰 AI投资</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from '../stores/game'
import { useThemeStore } from '../stores/theme'
import axios from 'axios'

const gameStore = useGameStore()
const themeStore = useThemeStore()
const userInput = ref('')
const showThemeSelector = ref(false)

const avatar = computed(() => gameStore.avatar)
const assets = computed(() => gameStore.assets)
const trustLevel = computed(() => gameStore.trustLevel)
const wealthLevel = computed(() => gameStore.wealthLevel)
const lifeStage = computed(() => gameStore.lifeStage)
const aiReflection = computed(() => gameStore.aiReflection)
const aiMonologue = computed(() => gameStore.aiMonologue)
const aiResponse = computed(() => gameStore.aiResponse)
const currentSituation = computed(() => gameStore.currentSituation)
const situationOptions = computed(() => gameStore.situationOptions)
const investments = computed(() => gameStore.assets.investments || [])
const monthlyIncome = computed(() => {
  return investments.value.reduce((sum, inv) => sum + (inv.monthly_return || 0), 0)
})

const robotMood = computed(() => {
  if (assets.value.total > 1000000) return 'happy'
  if (assets.value.total < 50000) return 'sad'
  return 'neutral'
})

const formatNumber = (num) => {
  return num?.toLocaleString('zh-CN') || '0'
}

const sendMessage = async () => {
  console.log('sendMessage 被调用, 输入:', userInput.value)
  if (!userInput.value.trim()) {
    console.log('输入为空')
    return
  }
  const message = userInput.value
  userInput.value = ''
  gameStore.aiResponse = '正在思考...'
  
  console.log('发送消息:', message)
  try {
    const res = await axios.post('/api/ai/chat', { message })
    console.log('AI响应:', res.data)
    gameStore.aiResponse = res.data.response
    gameStore.aiReflection = res.data.reflection
    gameStore.aiMonologue = res.data.monologue
  } catch (error) {
    console.error('发送消息失败:', error)
    gameStore.aiResponse = '发送失败: ' + error.message
  }
}

const selectTheme = (key) => {
  themeStore.setTheme(key)
  showThemeSelector.value = false
}

const aiInvest = async () => {
  try {
    const currentCharacter = localStorage.getItem('currentCharacter')
    if (!currentCharacter) {
      alert('请先选择角色')
      return
    }
    
    const char = JSON.parse(currentCharacter)
    const res = await axios.post('/api/ai/invest', {
      session_id: char.id,
      name: avatar.value?.name,
      mbti: avatar.value?.mbti_type,
      cash: assets.value.cash
    })
    
    if (res.data.success) {
      const inv = res.data.investment
      alert(`💰 AI投资决策\n\n💼 项目: ${inv.name}\n💵 金额: ￥${formatNumber(inv.amount)}\n⏱️ 期限: ${inv.duration}个月\n📈 预期收益率: ${(inv.return_rate * 100).toFixed(1)}%\n\n🤖 AI思考: ${res.data.ai_thoughts}`)
      gameStore.loadAvatar()
    } else {
      alert(`🤔 ${res.data.message}\n\n${res.data.ai_thoughts}`)
    }
  } catch (error) {
    console.error('AI投资失败:', error)
    alert('AI投资失败: ' + error.message)
  }
}

const advanceTime = async () => {
  try {
    const currentCharacter = localStorage.getItem('currentCharacter')
    if (!currentCharacter) {
      alert('请先选择角色')
      return
    }
    
    const char = JSON.parse(currentCharacter)
    const res = await axios.post('/api/time/advance', {
      session_id: char.id,
      name: avatar.value?.name,
      mbti: avatar.value?.mbti_type,
      cash: assets.value.cash,
      total_assets: assets.value.total
    })
    
    if (res.data.success) {
      // 更新情况显示
      gameStore.currentSituation = res.data.situation
      gameStore.situationOptions = res.data.options || []
      
      // 显示提示
      alert(`⏰ 时间推进1个月\n\n💰 现金: ￥${formatNumber(res.data.new_cash)}\n📈 总资产: ￥${formatNumber(res.data.total_assets)}\n💵 月收入: ￥${formatNumber(res.data.monthly_income)}`)
      
      // 刷新数据
      gameStore.loadAvatar()
    }
  } catch (error) {
    console.error('时间推进失败:', error)
    alert('时间推进失败: ' + error.message)
  }
}

onMounted(() => {
  gameStore.loadAvatar()
  themeStore.applyTheme()
})
</script>

<style scoped>
.home-page {
  width: 100%;
  height: 100vh;
  padding: 20px;
  position: relative;
}

.header-info {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.theme-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(255,255,255,0.9);
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.theme-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.theme-selector {
  position: absolute;
  top: 70px;
  left: 20px;
  background: rgba(255,255,255,0.95);
  padding: 15px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 100;
}

.theme-option {
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: bold;
  color: #666;
}

.theme-option:hover {
  background: rgba(255,154,158,0.2);
  color: #ff9a9e;
}

.theme-option.active {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  color: white;
}

.nickname {
  font-size: 24px;
  font-weight: bold;
  color: white;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.mbti-tag {
  background: rgba(255,255,255,0.9);
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: bold;
  color: #ff9a9e;
  font-size: 14px;
}

.top-right-info {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  background: rgba(255,255,255,0.9);
  color: #ff9a9e;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.nav-btn:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.wealth-level, .trust-level {
  background: rgba(255,255,255,0.95);
  padding: 12px 20px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.wealth-level .label, .trust-level .label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.wealth-level .value, .trust-level .value {
  font-size: 18px;
  font-weight: bold;
  color: #ff9a9e;
}

.main-content {
  display: flex;
  gap: 30px;
  height: calc(100vh - 80px);
  margin-top: 60px;
}

.left-panel {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-card {
  background: rgba(255,255,255,0.95);
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.card-sub {
  font-size: 12px;
  color: #999;
}

.reflection-card {
  background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%);
  border: 2px solid rgba(102,126,234,0.3);
}

.reflection-text {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  font-style: italic;
  margin-top: 10px;
}

.center-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 30px;
}

.robot-container {
  display: flex;
  justify-content: center;
}

.robot {
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.robot:hover {
  transform: scale(1.05);
}

.robot.happy {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.robot.sad {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.robot-face {
  position: relative;
  width: 100px;
  height: 100px;
}

.eye {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 30px;
}

.eye.left {
  left: 20px;
}

.eye.right {
  right: 20px;
}

.mouth {
  width: 40px;
  height: 20px;
  border: 3px solid white;
  border-top: none;
  border-radius: 0 0 40px 40px;
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
}

.robot.happy .mouth {
  border-radius: 0 0 40px 40px;
}

.robot.sad .mouth {
  border-radius: 40px 40px 0 0;
  border-top: 3px solid white;
  border-bottom: none;
}

.ai-dialogue {
  background: rgba(255,255,255,0.95);
  padding: 25px;
  border-radius: 20px;
  width: 600px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

.ai-response {
  background: linear-gradient(135deg, rgba(255,154,158,0.1) 0%, rgba(254,207,239,0.1) 100%);
  padding: 20px;
  border-radius: 20px;
  width: 600px;
  border: 2px solid rgba(255,154,158,0.3);
}

.response-header {
  font-size: 14px;
  font-weight: bold;
  color: #ff9a9e;
  margin-bottom: 10px;
}

.response-content {
  color: #333;
  line-height: 1.6;
  font-size: 15px;
}

.dialogue-header {
  font-size: 16px;
  font-weight: bold;
  color: #ff9a9e;
  margin-bottom: 15px;
  text-align: center;
}

.dialogue-content p {
  margin: 10px 0;
  line-height: 1.6;
  color: #333;
}

.asset-summary {
  font-weight: bold;
  color: #ff9a9e;
}

.reflection {
  font-style: italic;
  color: #666;
}

.monologue {
  color: #333;
}

.input-area {
  display: flex;
  gap: 10px;
  width: 600px;
}

.input-area input {
  flex: 1;
  padding: 15px 20px;
  border: none;
  border-radius: 25px;
  font-size: 14px;
  background: rgba(255,255,255,0.95);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  outline: none;
}

.input-area button {
  padding: 15px 30px;
  border: none;
  border-radius: 25px;
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  color: white;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.input-area button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.3);
}

.time-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

.invest-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
}

.situation-box {
  background: rgba(255,255,255,0.95);
  padding: 25px;
  border-radius: 20px;
  width: 600px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  border: 2px solid #667eea;
}

.situation-header {
  font-size: 16px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 15px;
  text-align: center;
}

.situation-content {
  color: #333;
  line-height: 1.8;
  margin-bottom: 15px;
  font-size: 15px;
}

.situation-options {
  background: rgba(102,126,234,0.05);
  padding: 15px;
  border-radius: 10px;
}

.option-title {
  font-weight: bold;
  color: #667eea;
  margin-bottom: 10px;
}

.option-item {
  padding: 8px 0;
  color: #666;
  border-bottom: 1px solid rgba(102,126,234,0.1);
}

.option-item:last-child {
  border-bottom: none;
}
</style>
