<template>
  <div class="view-container">
    <div class="view-header">
      <h2>时间线 // TIMELINE</h2>
      <div class="header-line"></div>
    </div>

    <div class="timeline-content">
      <div class="archive-card full-height">
        <div class="archive-body scrollable">
          <div v-if="!events.length" class="empty-state">
            暂无历史记录
          </div>
          <div v-else class="timeline-list">
            <div v-for="(event, index) in events" :key="index" class="timeline-item">
              <div class="time-marker">
                <div class="dot"></div>
                <div class="line" v-if="index !== events.length - 1"></div>
              </div>
              <div class="event-card">
                <div class="event-header">
                  <span class="event-type">{{ getEventType(event.type) }}</span>
                  <span class="event-time">{{ formatDate(event.timestamp) }}</span>
                </div>
                <div class="event-title">{{ event.title }}</div>
                <div class="event-desc">{{ event.description }}</div>
                <div class="event-impact" v-if="event.impact">
                  <div v-if="event.impact.cash_change" :class="event.impact.cash_change > 0 ? 'pos' : 'neg'">
                    {{ event.impact.cash_change > 0 ? '+' : '' }}¥{{ event.impact.cash_change }}
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
import { ref, onMounted } from 'vue'
import { useGameStore } from '../../stores/game'

const gameStore = useGameStore()
const events = ref([])

onMounted(async () => {
  events.value = await gameStore.getTimeline(50)
})

const getEventType = (type) => {
  const map = {
    'story': '事件',
    'decision': '决策',
    'ai': 'AI操作',
    'timeline': '周期'
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
  margin-bottom: 8px;
  color: var(--term-text);
}

.event-desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--term-text-secondary);
}

.event-impact {
  margin-top: 12px;
  font-weight: bold;
  font-size: 12px;
}

.pos { color: var(--term-success); }
.neg { color: #F44336; }

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--term-text-secondary);
}
</style>
