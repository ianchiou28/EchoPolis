<template>
  <div class="view-container">
    <div class="view-header">
      <h2>生活消费 // LIFESTYLE</h2>
      <div class="header-line"></div>
    </div>

    <div class="content-grid">
      <!-- Left: Status & Activities -->
      <div class="col-left">
        <div class="archive-card">
          <div class="archive-header">生活状态</div>
          <div class="archive-body">
            <div class="status-bars">
              <div class="status-bar">
                <div class="bar-label">
                  <span>😊 幸福度</span>
                  <span>{{ happiness }}/100</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill happiness" :style="{width: happiness + '%'}"></div>
                </div>
              </div>
              <div class="status-bar">
                <div class="bar-label">
                  <span>⚡ 精力值</span>
                  <span>{{ energy }}/100</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill energy" :style="{width: energy + '%'}"></div>
                </div>
              </div>
              <div class="status-bar">
                <div class="bar-label">
                  <span>❤️ 健康度</span>
                  <span>{{ health }}/100</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill health" :style="{width: health + '%'}"></div>
                </div>
              </div>
              <div class="status-bar">
                <div class="bar-label">
                  <span>🤝 人脉值</span>
                  <span>{{ social }}/100</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill social" :style="{width: social + '%'}"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activities -->
        <div class="archive-card flex-grow">
          <div class="archive-header">近期活动</div>
          <div class="archive-body scrollable">
            <div v-if="recentActivities.length === 0" class="empty-state">
              暂无活动记录
            </div>
            <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
              <div class="activity-icon">{{ activity.icon }}</div>
              <div class="activity-info">
                <div class="activity-name">{{ activity.name }}</div>
                <div class="activity-time">{{ activity.time }}</div>
              </div>
              <div class="activity-effects">
                <span v-for="(val, key) in activity.effects" :key="key" 
                  :class="val >= 0 ? 'positive' : 'negative'">
                  {{ val >= 0 ? '+' : '' }}{{ val }} {{ effectLabels[key] }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Activities & Business (Accordion) -->
      <div class="col-right accordion-column">
        <!-- 休闲娱乐 -->
        <div 
          class="accordion-card" 
          :class="{ expanded: rightPanel === 'entertainment', collapsed: rightPanel && rightPanel !== 'entertainment' }"
          @click="rightPanel !== 'entertainment' && (rightPanel = 'entertainment')"
        >
          <div class="accordion-header">
            <span class="accordion-icon">🎮</span>
            <span class="accordion-title">休闲娱乐</span>
            <span class="cash-display" v-if="rightPanel === 'entertainment'">💰 ¥{{ formatNumber(cash) }}</span>
            <span class="accordion-arrow">{{ rightPanel === 'entertainment' ? '▼' : '▶' }}</span>
          </div>
          <div class="accordion-body" v-show="rightPanel === 'entertainment'">
            <div class="activity-grid">
              <div v-for="act in entertainments" :key="act.id" 
                class="activity-card"
                :class="{ disabled: cash < act.cost }"
                @click.stop="doActivity(act)">
                <div class="card-icon">{{ act.icon }}</div>
                <div class="card-name">{{ act.name }}</div>
                <div class="card-cost">¥{{ act.cost }}</div>
                <div class="card-effects">
                  <span v-if="act.happiness" class="positive">+{{ act.happiness }}😊</span>
                  <span v-if="act.energy" :class="act.energy > 0 ? 'positive' : 'negative'">{{ act.energy > 0 ? '+' : '' }}{{ act.energy }}⚡</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 社交活动 -->
        <div 
          class="accordion-card" 
          :class="{ expanded: rightPanel === 'social', collapsed: rightPanel && rightPanel !== 'social' }"
          @click="rightPanel !== 'social' && (rightPanel = 'social')"
        >
          <div class="accordion-header">
            <span class="accordion-icon">🤝</span>
            <span class="accordion-title">社交活动</span>
            <span class="accordion-arrow">{{ rightPanel === 'social' ? '▼' : '▶' }}</span>
          </div>
          <div class="accordion-body" v-show="rightPanel === 'social'">
            <div class="social-list">
              <div v-for="act in socialActivities" :key="act.id" 
                class="social-item"
                :class="{ disabled: cash < act.cost }"
                @click.stop="doActivity(act)">
                <div class="social-main">
                  <div class="social-icon">{{ act.icon }}</div>
                  <div class="social-info">
                    <div class="social-name">{{ act.name }}</div>
                    <div class="social-desc">{{ act.description }}</div>
                  </div>
                </div>
                <div class="social-right">
                  <div class="social-cost">¥{{ formatNumber(act.cost) }}</div>
                  <div class="social-effects">
                    <span v-if="act.social" class="positive">+{{ act.social }}🤝</span>
                    <span v-if="act.happiness" class="positive">+{{ act.happiness }}😊</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 创业项目 -->
        <div 
          class="accordion-card" 
          :class="{ expanded: rightPanel === 'business', collapsed: rightPanel && rightPanel !== 'business' }"
          @click="rightPanel !== 'business' && (rightPanel = 'business')"
        >
          <div class="accordion-header">
            <span class="accordion-icon">🚀</span>
            <span class="accordion-title">创业项目</span>
            <span class="accordion-arrow">{{ rightPanel === 'business' ? '▼' : '▶' }}</span>
          </div>
          <div class="accordion-body" v-show="rightPanel === 'business'">
            <div v-for="biz in businesses" :key="biz.id" class="business-card">
              <div class="biz-header">
                <span class="biz-icon">{{ biz.icon }}</span>
                <span class="biz-name">{{ biz.name }}</span>
                <span class="biz-status" :class="biz.status">{{ biz.statusText }}</span>
              </div>
              <div class="biz-desc">{{ biz.description }}</div>
              <div class="biz-stats">
                <div class="biz-stat">
                  <span class="label">启动资金</span>
                  <span class="value">¥{{ formatNumber(biz.investment) }}</span>
                </div>
                <div class="biz-stat">
                  <span class="label">预期收益</span>
                  <span class="value positive">¥{{ formatNumber(biz.expectedReturn) }}/月</span>
                </div>
                <div class="biz-stat">
                  <span class="label">风险等级</span>
                  <span class="value" :class="'risk-' + biz.risk">{{ biz.riskText }}</span>
                </div>
              </div>
              <button class="term-btn" @click.stop="startBusiness(biz)" 
                :disabled="cash < biz.investment || biz.status === 'running'">
                {{ biz.status === 'running' ? '运营中' : '启动项目' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Activity Result -->
    <div class="result-toast" v-if="showResult" :class="resultType">
      <div class="result-icon">{{ resultType === 'success' ? '✓' : '!' }}</div>
      <div class="result-text">{{ resultMessage }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useGameStore } from '../../stores/game'

const gameStore = useGameStore()
const cash = computed(() => gameStore.assets?.cash || 0)

// 右侧面板切换
const rightPanel = ref('entertainment')  // 'entertainment', 'social', or 'business'

// 从store同步生活状态
const happiness = computed(() => gameStore.avatar?.happiness || 60)
const energy = computed(() => gameStore.avatar?.energy || 75)
const health = computed(() => gameStore.avatar?.health || 80)
const social = ref(50)

const effectLabels = {
  happiness: '幸福',
  energy: '精力',
  health: '健康',
  social: '人脉',
  cash: '金钱'
}

// 近期活动
const recentActivities = ref([])

// 休闲娱乐
const entertainments = ref([
  { id: 'movie', name: '看电影', icon: '🎬', cost: 100, happiness: 5, energy: -5 },
  { id: 'game', name: '打游戏', icon: '🎮', cost: 50, happiness: 8, energy: -10 },
  { id: 'gym', name: '健身房', icon: '💪', cost: 200, happiness: 3, energy: 10, health: 5 },
  { id: 'spa', name: 'SPA按摩', icon: '🧖', cost: 500, happiness: 10, energy: 20, health: 3 },
  { id: 'travel', name: '周末游', icon: '✈️', cost: 2000, happiness: 20, energy: -15 },
  { id: 'concert', name: '演唱会', icon: '🎤', cost: 800, happiness: 15, energy: -10, social: 5 }
])

// 社交活动
const socialActivities = ref([
  { id: 'coffee', name: '约人喝咖啡', icon: '☕', cost: 100, social: 5, happiness: 3, description: '轻松交流，拓展人脉' },
  { id: 'dinner', name: '商务饭局', icon: '🍽️', cost: 500, social: 15, happiness: 5, description: '高端社交，结识大佬' },
  { id: 'party', name: '派对聚会', icon: '🎉', cost: 300, social: 10, happiness: 12, description: '结识新朋友，放松心情' },
  { id: 'club', name: '俱乐部活动', icon: '🏌️', cost: 1000, social: 20, happiness: 8, description: '高尔夫、品酒等高端活动' }
])

// 创业项目
const businesses = ref([
  { id: 'shop', name: '网店经营', icon: '🛒', investment: 10000, expectedReturn: 2000, risk: 'low', riskText: '低风险', status: 'available', statusText: '可启动', description: '开设网店，销售商品' },
  { id: 'content', name: '自媒体创业', icon: '📱', investment: 5000, expectedReturn: 3000, risk: 'medium', riskText: '中风险', status: 'available', statusText: '可启动', description: '视频/直播带货，内容变现' },
  { id: 'restaurant', name: '餐饮加盟', icon: '🍜', investment: 100000, expectedReturn: 15000, risk: 'medium', riskText: '中风险', status: 'available', statusText: '可启动', description: '加盟连锁餐饮品牌' },
  { id: 'tech', name: '科技初创', icon: '🚀', investment: 500000, expectedReturn: 50000, risk: 'high', riskText: '高风险', status: 'available', statusText: '可启动', description: '高风险高回报的技术创业' }
])

// 结果提示
const showResult = ref(false)
const resultMessage = ref('')
const resultType = ref('success')

const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toLocaleString()
}

const getSessionId = () => {
  try {
    return JSON.parse(localStorage.getItem('currentCharacter'))?.id
  } catch { return null }
}

const doActivity = async (activity) => {
  if (cash.value < activity.cost) return
  
  const sessionId = getSessionId()
  if (!sessionId) return
  
  try {
    const res = await fetch('/api/lifestyle/activity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        activity_id: activity.id,
        cost: activity.cost,
        effects: {
          happiness: activity.happiness || 0,
          energy: activity.energy || 0,
          health: activity.health || 0,
          social: activity.social || 0
        }
      })
    })
    const data = await res.json()
    
    if (data.success) {
      // 更新本地状态（从响应）
      if (data.new_status) {
        if (gameStore.avatar) {
          gameStore.avatar.happiness = data.new_status.happiness
          gameStore.avatar.energy = data.new_status.energy
          gameStore.avatar.health = data.new_status.health
          gameStore.avatar.cash = data.new_status.cash
        }
        gameStore.updateAssets()
      }
      
      // 添加到活动记录
      recentActivities.value.unshift({
        id: Date.now(),
        name: activity.name,
        icon: activity.icon,
        time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
        effects: { happiness: activity.happiness, energy: activity.energy, health: activity.health, social: activity.social }
      })
      if (recentActivities.value.length > 10) recentActivities.value.pop()
      
      // 显示结果
      showResultToast(`${activity.name} 完成！花费 ¥${activity.cost}`, 'success')
      
      // 刷新全局状态
      await gameStore.loadAvatar()
    } else {
      showResultToast(data.error || '操作失败', 'error')
    }
  } catch (e) {
    showResultToast('操作失败', 'error')
  }
}

const startBusiness = async (biz) => {
  if (cash.value < biz.investment) return
  
  const sessionId = getSessionId()
  if (!sessionId) return
  
  try {
    const res = await fetch('/api/lifestyle/business', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        business_id: biz.id,
        investment: biz.investment
      })
    })
    const data = await res.json()
    
    if (data.success) {
      biz.status = 'running'
      biz.statusText = '运营中'
      showResultToast(`${biz.name} 启动成功！`, 'success')
      await gameStore.loadAvatar()
    } else {
      showResultToast(data.error || '启动失败', 'error')
    }
  } catch (e) {
    showResultToast('操作失败', 'error')
  }
}

const showResultToast = (message, type) => {
  resultMessage.value = message
  resultType.value = type
  showResult.value = true
  setTimeout(() => { showResult.value = false }, 2000)
}

const loadBusinesses = async () => {
  const sessionId = getSessionId()
  if (!sessionId) return
  
  try {
    const res = await fetch(`/api/lifestyle/businesses/${sessionId}`)
    const data = await res.json()
    if (data.success && data.businesses) {
      // 更新已运行的副业状态
      for (const runningBiz of data.businesses) {
        const biz = businesses.value.find(b => b.id === runningBiz.id)
        if (biz) {
          biz.status = 'running'
          biz.statusText = '运营中'
        }
      }
    }
  } catch (e) {
    console.error('Load businesses failed:', e)
  }
}

onMounted(async () => {
  await loadBusinesses()
})
</script>

<style scoped>
.view-container { height: 100%; display: flex; flex-direction: column; padding: 20px; overflow: hidden; }
.view-header h2 { font-size: 24px; font-weight: 900; margin: 0 0 8px; }
.header-line { height: 3px; background: var(--term-accent); width: 60px; margin-bottom: 20px; }
.content-grid { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; overflow: hidden; }
.col-left, .col-right { display: flex; flex-direction: column; gap: 16px; overflow: hidden; }

.archive-card { background: var(--term-panel-bg); border: 2px solid var(--term-border); }
.archive-card.flex-grow { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.archive-header { padding: 12px 16px; font-weight: 800; font-size: 12px; border-bottom: 1px solid var(--term-border); display: flex; justify-content: space-between; align-items: center; }
.archive-body { padding: 16px; }
.archive-body.scrollable { flex: 1; overflow-y: auto; }

.cash-display { font-family: monospace; color: var(--term-accent); }

/* Status Bars */
.status-bars { display: flex; flex-direction: column; gap: 16px; }
.status-bar { }
.bar-label { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; }
.bar-track { height: 8px; background: rgba(0,0,0,0.1); border: 1px solid var(--term-border); }
.bar-fill { height: 100%; transition: width 0.3s; }
.bar-fill.happiness { background: #f59e0b; }
.bar-fill.energy { background: #3b82f6; }
.bar-fill.health { background: #ef4444; }
.bar-fill.social { background: #8b5cf6; }

/* Activity Item */
.activity-item { display: flex; gap: 12px; align-items: center; padding: 10px; border-bottom: 1px dashed var(--term-border); }
.activity-icon { font-size: 20px; }
.activity-info { flex: 1; }
.activity-name { font-weight: 600; }
.activity-time { font-size: 10px; color: var(--term-text-secondary); }
.activity-effects { display: flex; gap: 8px; font-size: 11px; }

/* Activity Grid */
.activity-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.activity-card { padding: 12px; border: 1px solid var(--term-border); text-align: center; cursor: pointer; transition: all 0.2s; }
.activity-card:hover:not(.disabled) { border-color: var(--term-accent); transform: translateY(-2px); }
.activity-card.disabled { opacity: 0.5; cursor: not-allowed; }
.card-icon { font-size: 24px; }
.card-name { font-weight: 700; font-size: 12px; margin: 4px 0; }
.card-cost { font-size: 11px; color: var(--term-text-secondary); }
.card-effects { font-size: 10px; margin-top: 4px; }

/* Social List */
.social-list { display: flex; flex-direction: column; gap: 10px; }
.social-item { display: flex; justify-content: space-between; padding: 12px; border: 1px solid var(--term-border); cursor: pointer; }
.social-item:hover:not(.disabled) { border-color: var(--term-accent); }
.social-item.disabled { opacity: 0.5; cursor: not-allowed; }
.social-main { display: flex; gap: 12px; }
.social-icon { font-size: 24px; }
.social-name { font-weight: 700; }
.social-desc { font-size: 11px; color: var(--term-text-secondary); }
.social-right { text-align: right; }
.social-cost { font-weight: 700; }
.social-effects { font-size: 11px; }

/* Business Card */
.business-card { padding: 16px; border: 1px solid var(--term-border); margin-bottom: 12px; }
.biz-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.biz-icon { font-size: 20px; }
.biz-name { font-weight: 700; flex: 1; }
.biz-status { font-size: 10px; padding: 2px 8px; border: 1px solid; }
.biz-status.available { color: #10b981; border-color: #10b981; }
.biz-status.running { color: #3b82f6; border-color: #3b82f6; }
.biz-desc { font-size: 12px; color: var(--term-text-secondary); margin-bottom: 12px; }
.biz-stats { display: flex; gap: 16px; margin-bottom: 12px; }
.biz-stat { display: flex; flex-direction: column; }
.biz-stat .label { font-size: 10px; color: var(--term-text-secondary); }
.biz-stat .value { font-weight: 700; }
.risk-low { color: #10b981; }
.risk-medium { color: #f59e0b; }
.risk-high { color: #ef4444; }

/* Result Toast */
.result-toast { position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); padding: 12px 24px; background: var(--term-panel-bg); border: 2px solid var(--term-border); display: flex; align-items: center; gap: 8px; z-index: 1000; animation: slideUp 0.3s; }
.result-toast.success { border-color: #10b981; }
.result-toast.error { border-color: #ef4444; }
.result-icon { font-size: 18px; }
.result-toast.success .result-icon { color: #10b981; }
.result-toast.error .result-icon { color: #ef4444; }

@keyframes slideUp { from { transform: translateX(-50%) translateY(20px); opacity: 0; } to { transform: translateX(-50%) translateY(0); opacity: 1; } }

.term-btn { padding: 8px 16px; font-weight: 700; border: 2px solid var(--term-border); background: var(--term-panel-bg); cursor: pointer; width: 100%; }
.term-btn:hover:not(:disabled) { background: var(--term-accent); color: #000; }
.term-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.positive { color: #10b981; }
.negative { color: #ef4444; }
.empty-state { text-align: center; padding: 30px; color: var(--term-text-secondary); }

/* Accordion Styles */
.accordion-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.accordion-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.accordion-card.expanded { flex: 1; }
.accordion-card.collapsed { flex: 0 0 auto; cursor: pointer; }
.accordion-card.collapsed:hover { border-color: var(--term-accent); }

.accordion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(0,0,0,0.03);
  border-bottom: 1px solid var(--term-border);
  font-weight: 700;
}

.accordion-icon { font-size: 16px; }
.accordion-title { flex: 1; font-size: 12px; text-transform: uppercase; }
.accordion-arrow { font-size: 10px; color: var(--term-text-secondary); }
.accordion-body { flex: 1; overflow-y: auto; padding: 16px; }
</style>
