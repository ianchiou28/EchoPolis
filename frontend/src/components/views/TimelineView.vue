<template>
  <div class="view-container">
    <div class="view-header">
      <h2>时间线 // TIMELINE</h2>
      <div class="header-line"></div>
    </div>

    <!-- 筛选标签 -->
    <div class="filter-tabs">
      <button 
        v-for="tab in filterTabs" 
        :key="tab.id"
        :class="['filter-tab', { active: activeFilter === tab.id }]"
        @click="activeFilter = tab.id">
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>

    <div class="timeline-content">
      <div class="archive-card full-height">
        <div class="archive-body scrollable">
          <div v-if="loading" class="loading-state">
            加载中...
          </div>
          <div v-else-if="!filteredItems.length" class="empty-state">
            暂无历史记录
          </div>
          <div v-else class="timeline-list">
            <div v-for="(item, index) in filteredItems" :key="index" class="timeline-item">
              <div class="time-marker">
                <div class="dot" :class="item.type"></div>
                <div class="line" v-if="index !== filteredItems.length - 1"></div>
              </div>
              
              <!-- 通用事件卡片 -->
              <div class="event-card" :class="item.type">
                <div class="event-header">
                  <span class="event-type" :class="item.category">
                    {{ item.icon }} {{ getTypeLabel(item.type) }}
                  </span>
                  <span class="event-time">
                    第{{ item.month || '?' }}月 · {{ formatDate(item.timestamp) }}
                  </span>
                </div>
                
                <div class="event-title">{{ item.title }}</div>
                
                <!-- 金额显示 -->
                <div class="amount-row" v-if="item.amount !== undefined && item.amount !== null">
                  <span class="amount" :class="item.amount >= 0 ? 'pos' : 'neg'">
                    {{ item.amount >= 0 ? '+' : '' }}¥{{ Math.abs(item.amount).toLocaleString() }}
                  </span>
                </div>
                
                <!-- 描述/详情 -->
                <div class="event-desc" v-if="item.description">{{ item.description }}</div>
                
                <!-- AI想法 -->
                <div class="ai-thoughts" v-if="item.ai_thoughts">
                  <span class="ai-label">🤖 AI想法:</span>
                  {{ item.ai_thoughts }}
                </div>
                
                <!-- 行为评分 -->
                <div class="behavior-scores" v-if="item.risk_score !== undefined">
                  <span class="score-item">
                    <span class="score-label">风险</span>
                    <span class="score-value" :class="getRiskLevel(item.risk_score)">
                      {{ ((item.risk_score || 0) * 100).toFixed(0) }}%
                    </span>
                  </span>
                  <span class="score-item">
                    <span class="score-label">理性</span>
                    <span class="score-value" :class="getRationalityLevel(item.rationality_score)">
                      {{ ((item.rationality_score || 0) * 100).toFixed(0) }}%
                    </span>
                  </span>
                </div>
                
                <!-- 资产变化 -->
                <div class="asset-change" v-if="item.type === 'snapshot' && item.change">
                  <div class="change-row">
                    <span>总资产</span>
                    <span class="value">¥{{ item.total_assets?.toLocaleString() }}</span>
                  </div>
                  <div class="change-row">
                    <span>变化</span>
                    <span class="value" :class="item.change >= 0 ? 'pos' : 'neg'">
                      {{ item.change >= 0 ? '+' : '' }}¥{{ Math.abs(item.change).toLocaleString() }}
                    </span>
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
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from '../../stores/game'

const gameStore = useGameStore()
const loading = ref(true)
const timelineItems = ref([])
const activeFilter = ref('all')

const filterTabs = [
  { id: 'all', label: '全部', icon: '📋' },
  { id: 'cash_flow', label: '现金流', icon: '💰' },
  { id: 'asset_change', label: '资产变化', icon: '📊' }
]

// 获取 session ID
const getSessionId = () => {
  const character = gameStore.getCurrentCharacter()
  return character?.id || null
}

// 加载时间线数据
const loadTimeline = async () => {
  const sessionId = getSessionId()
  if (!sessionId) {
    loading.value = false
    return
  }
  
  try {
    const response = await fetch(`/api/timeline/${sessionId}?limit=100`)
    const result = await response.json()
    if (result.success) {
      timelineItems.value = result.items || []
    }
  } catch (error) {
    console.error('Failed to load timeline:', error)
  } finally {
    loading.value = false
  }
}

// 筛选后的项目
const filteredItems = computed(() => {
  if (activeFilter.value === 'all') {
    return timelineItems.value
  }
  return timelineItems.value.filter(item => item.category === activeFilter.value)
})

const getTypeLabel = (type) => {
  const labels = {
    'transaction': '交易',
    'event': '事件',
    'behavior': '行为',
    'deposit': '存款',
    'loan': '贷款',
    'investment': '投资',
    'snapshot': '月度总结'
  }
  return labels[type] || type
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

onMounted(() => {
  loadTimeline()
})
</script>

<style scoped>
.view-container {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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
  margin-bottom: 16px;
}

/* 筛选标签 */
.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 6px 12px;
  border: 1px solid var(--term-border);
  background: transparent;
  color: var(--term-text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab:hover {
  background: rgba(0,0,0,0.05);
}

.filter-tab.active {
  background: var(--term-text);
  color: #fff;
  border-color: var(--term-text);
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
  padding: 16px;
}

.timeline-list {
  display: flex;
  flex-direction: column;
}

.timeline-item {
  display: flex;
  gap: 16px;
  position: relative;
  padding-bottom: 24px;
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

.dot.transaction, .dot.deposit, .dot.loan { 
  background: #4CAF50; 
  border-radius: 50%; 
}
.dot.investment { 
  background: #2196F3; 
}
.dot.behavior { 
  background: #9C27B0; 
  border-radius: 50%; 
}
.dot.event { 
  background: #FF9800; 
}
.dot.snapshot { 
  background: #607D8B; 
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
  padding: 14px;
  position: relative;
  top: -6px;
}

.event-card.transaction { border-left: 4px solid #4CAF50; }
.event-card.deposit { border-left: 4px solid #4CAF50; }
.event-card.loan { border-left: 4px solid #FF5722; }
.event-card.investment { border-left: 4px solid #2196F3; }
.event-card.behavior { border-left: 4px solid #9C27B0; }
.event-card.event { border-left: 4px solid #FF9800; }
.event-card.snapshot { border-left: 4px solid #607D8B; }

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
  padding: 2px 6px;
  background: var(--term-border);
  color: #fff;
}

.event-type.cash_flow { background: #4CAF50; }
.event-type.asset_change { background: #2196F3; }
.event-type.subject { background: #9C27B0; }
.event-type.environment { background: #FF9800; }

.event-title {
  font-weight: 900;
  font-size: 15px;
  margin-bottom: 6px;
  color: var(--term-text);
}

.amount-row {
  margin: 8px 0;
}

.amount {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 900;
  font-size: 16px;
}

.event-desc {
  font-size: 12px;
  line-height: 1.5;
  color: var(--term-text-secondary);
  margin-top: 6px;
}

.ai-thoughts {
  margin-top: 10px;
  padding: 8px;
  background: rgba(156, 39, 176, 0.08);
  border-left: 3px solid #9C27B0;
  font-size: 12px;
  font-style: italic;
  color: var(--term-text-secondary);
}

.ai-label {
  font-weight: 700;
  color: #9C27B0;
  margin-right: 4px;
}

.behavior-scores {
  display: flex;
  gap: 16px;
  margin-top: 10px;
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
  font-size: 13px;
  padding: 2px 8px;
  border-radius: 4px;
}

.score-value.high-risk { background: rgba(244, 67, 54, 0.2); color: #f44336; }
.score-value.medium-risk { background: rgba(255, 152, 0, 0.2); color: #ff9800; }
.score-value.low-risk { background: rgba(76, 175, 80, 0.2); color: #4caf50; }
.score-value.high-rationality { background: rgba(76, 175, 80, 0.2); color: #4caf50; }
.score-value.medium-rationality { background: rgba(255, 193, 7, 0.2); color: #ffc107; }
.score-value.low-rationality { background: rgba(244, 67, 54, 0.2); color: #f44336; }

.asset-change {
  margin-top: 10px;
  padding: 8px;
  background: rgba(0,0,0,0.03);
}

.change-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding: 4px 0;
}

.change-row .value {
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
}

.pos { color: #4CAF50; }
.neg { color: #F44336; }

.empty-state, .loading-state {
  text-align: center;
  padding: 40px;
  color: var(--term-text-secondary);
}
</style>
