<template>
  <div class="view-container">
    <div class="view-header">
      <h2>时间线 // TIMELINE</h2>
      <div class="header-line"></div>
    </div>

    <div class="timeline-content">
      <div class="archive-card full-height">
        <div class="archive-body scrollable">
          <div v-if="loading" class="loading-state">
            加载中...
          </div>
          <div v-else-if="!timelineItems.length" class="empty-state">
            暂无历史记录
          </div>
          <div v-else class="timeline-list">
            <div v-for="(item, index) in timelineItems" :key="index" class="timeline-item">
              <div class="time-marker">
                <div class="dot" :class="item.source"></div>
                <div class="line" v-if="index !== timelineItems.length - 1"></div>
              </div>
              
              <!-- 交易记录样式 -->
              <div v-if="item.source === 'transaction'" class="event-card transaction">
                <div class="event-header">
                  <span class="event-type">交易</span>
                  <span class="event-time">{{ formatDate(item.timestamp) }}</span>
                </div>
                <div class="trans-row">
                  <div class="trans-info">
                    <div class="event-title">{{ item.title }}</div>
                    <div class="event-desc" v-if="item.description">{{ item.description }}</div>
                  </div>
                  <div class="trans-amount" :class="item.amount > 0 ? 'pos' : 'neg'">
                    {{ item.amount > 0 ? '+' : '' }}¥{{ item.amount.toLocaleString() }}
                  </div>
                </div>
              </div>

              <!-- 行为日志样式 -->
              <div v-else-if="item.source === 'behavior'" class="event-card behavior">
                <div class="event-header">
                  <span class="event-type behavior-type">🧠 行为</span>
                  <span class="event-time">第{{ item.game_month }}月</span>
                </div>
                <div class="behavior-content">
                  <div class="event-title">{{ item.title }}</div>
                  <div class="behavior-scores">
                    <span class="score-item">
                      <span class="score-label">风险</span>
                      <span class="score-value" :class="getRiskLevel(item.risk_score)">
                        {{ (item.risk_score * 100).toFixed(0) }}%
                      </span>
                    </span>
                    <span class="score-item">
                      <span class="score-label">理性</span>
                      <span class="score-value" :class="getRationalityLevel(item.rationality_score)">
                        {{ (item.rationality_score * 100).toFixed(0) }}%
                      </span>
                    </span>
                  </div>
                </div>
              </div>

              <!-- 事件记录样式 -->
              <div v-else class="event-card event">
                <div class="event-header">
                  <span class="event-type">{{ getEventType(item.type) }}</span>
                  <span class="event-time">{{ formatDate(item.timestamp) }}</span>
                </div>
                <div class="event-title">{{ item.title }}</div>
                <div class="event-desc">{{ item.description }}</div>
                <div class="event-impact" v-if="item.impact">
                  <div v-if="item.impact.cash_change" :class="item.impact.cash_change > 0 ? 'pos' : 'neg'">
                    {{ item.impact.cash_change > 0 ? '+' : '' }}¥{{ item.impact.cash_change.toLocaleString() }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useGameStore } from '../../stores/game'

const gameStore = useGameStore()
const loading = ref(true)
const behaviorLogs = ref([])
const showBehavior = ref(true)  // 是否显示行为日志

// 获取 session ID
const getSessionId = () => {
  const character = gameStore.getCurrentCharacter()
  return character?.id || null
}

// 加载行为日志
const loadBehaviorLogs = async () => {
  const sessionId = getSessionId()
  if (!sessionId) return
  
  try {
    const response = await fetch(`http://localhost:8000/api/insights/statistics/${sessionId}`)
    const result = await response.json()
    if (result.success && result.data) {
      // 从统计数据中获取行为日志
      // 这里简化处理，实际可以新增专门的行为日志API
    }
  } catch (error) {
    console.error('Failed to load behavior logs:', error)
  }
  
  // 直接从数据库获取行为日志
  try {
    const response = await fetch(`http://localhost:8000/api/behavior-logs/${sessionId}`)
    const result = await response.json()
    if (result.success) {
      behaviorLogs.value = result.data || []
    }
  } catch (error) {
    // 如果API不存在，使用空数组
    behaviorLogs.value = []
  }
}

// 合并并排序所有时间线项目
const timelineItems = computed(() => {
  const events = (gameStore.cityEvents || []).map(e => ({
    ...e,
    source: 'event',
    timestamp: new Date(e.timestamp).getTime()
  }))
  
  const transactions = (gameStore.transactions || []).map(t => ({
    ...t,
    source: 'transaction',
    timestamp: new Date(t.timestamp).getTime(),
    // 确保 description 存在
    description: t.description || t.ai_thoughts || ''
  }))

  // 添加行为日志
  const behaviors = showBehavior.value ? behaviorLogs.value.map(b => ({
    ...b,
    source: 'behavior',
    timestamp: new Date(b.created_at || Date.now()).getTime(),
    title: getCategoryLabel(b.action_category),
    description: b.action_data ? JSON.stringify(b.action_data).slice(0, 100) : ''
  })) : []

  return [...events, ...transactions, ...behaviors].sort((a, b) => b.timestamp - a.timestamp)
})

onMounted(async () => {
  try {
    console.log('Loading timeline events...')
    await Promise.all([
      gameStore.loadCityState(),
      gameStore.loadTransactions(),
      loadBehaviorLogs()
    ])
  } catch (e) {
    console.error('Failed to load timeline:', e)
  } finally {
    loading.value = false
  }
})

const getEventType = (type) => {
  const map = {
    'story': '事件',
    'decision': '决策',
    'ai': 'AI操作',
    'timeline': '周期',
    'action': '行动'
  }
  return map[type] || '记录'
}

const getCategoryLabel = (category) => {
  const labels = {
    'stock_buy': '买入股票',
    'stock_sell': '卖出股票',
    'loan_apply': '申请贷款',
    'loan_repay': '偿还贷款',
    'insurance_buy': '购买保险',
    'house_buy': '购买房产',
    'house_rent': '租房',
    'lifestyle_change': '生活方式变更',
    'deposit': '存款',
    'investment': '投资决策'
  }
  return labels[category] || category || '行为'
}

const getRiskLevel = (score) => {
  if (score >= 0.7) return 'high-risk'
  if (score >= 0.4) return 'medium-risk'
  return 'low-risk'
}

const getRationalityLevel = (score) => {
  if (score >= 0.7) return 'high-rationality'
  if (score >= 0.4) return 'medium-rationality'
  return 'low-rationality'
}

const formatDate = (ts) => {
  if (!ts) return ''
  return new Date(ts).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.view-container {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.view-header h2 {
  font-size: 24px;
  font-weight: 900;
  margin: 0 0 8px 0;
  color: var(--term-text);
}

.header-line {
  height: 2px;
  background: var(--term-border);
  margin-bottom: 24px;
}

.timeline-content {
  flex: 1;
  overflow: hidden;
}

.full-height {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.scrollable {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.timeline-item {
  display: flex;
  gap: 20px;
  position: relative;
  padding-bottom: 30px;
}

.time-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
}

.dot {
  width: 12px;
  height: 12px;
  background: var(--term-accent);
  border: 2px solid #000;
  z-index: 2;
}

.dot.transaction {
  background: var(--term-success);
  border-radius: 50%;
}

.line {
  flex: 1;
  width: 2px;
  background: var(--term-border);
  margin-top: 4px;
}

.event-card {
  flex: 1;
  background: rgba(0,0,0,0.02);
  border: 1px solid var(--term-border);
  padding: 16px;
  position: relative;
  top: -6px;
}

.event-card.transaction {
  border-left: 4px solid var(--term-success);
}

.event-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 10px;
  color: var(--term-text-secondary);
  text-transform: uppercase;
  font-weight: 700;
}

.event-type {
  background: var(--term-border);
  color: #fff;
  padding: 2px 6px;
}

.event-title {
  font-weight: 900;
  font-size: 16px;
  margin-bottom: 4px;
  color: var(--term-text);
}

.event-desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--term-text-secondary);
}

.trans-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.trans-amount {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 900;
  font-size: 16px;
}

.event-impact {
  margin-top: 12px;
  font-weight: bold;
  font-size: 12px;
}

.pos { color: var(--term-success); }
.neg { color: #F44336; }

.empty-state, .loading-state {
  text-align: center;
  padding: 40px;
  color: var(--term-text-secondary);
}

/* 行为日志样式 */
.dot.behavior {
  background: #9c27b0;
  border-radius: 50%;
}

.event-card.behavior {
  border-left: 4px solid #9c27b0;
  background: rgba(156, 39, 176, 0.05);
}

.behavior-type {
  background: #9c27b0 !important;
}

.behavior-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.behavior-scores {
  display: flex;
  gap: 16px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.score-label {
  font-size: 11px;
  opacity: 0.7;
}

.score-value {
  font-weight: 900;
  font-size: 14px;
  padding: 2px 8px;
  border-radius: 4px;
}

.score-value.high-risk {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.score-value.medium-risk {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
}

.score-value.low-risk {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.score-value.high-rationality {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.score-value.medium-rationality {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.score-value.low-rationality {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}
</style>
