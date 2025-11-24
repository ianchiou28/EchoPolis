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

  return [...events, ...transactions].sort((a, b) => b.timestamp - a.timestamp)
})

onMounted(async () => {
  try {
    console.log('Loading timeline events...')
    await Promise.all([
      gameStore.loadCityState(),
      gameStore.loadTransactions()
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
</style>
