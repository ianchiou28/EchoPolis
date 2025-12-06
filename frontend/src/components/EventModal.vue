<template>
  <Teleport to="body">
    <div class="event-overlay" v-if="currentEvent" @click.self="closeIfOptional">
      <div class="event-modal" :class="eventCategoryClass">
        <div class="event-header">
          <span class="event-category">{{ currentEvent.category }}</span>
          <span class="event-probability" v-if="currentEvent.tags">
            {{ currentEvent.tags.includes('high-risk') ? '⚠️ 高风险' : '' }}
          </span>
        </div>
        
        <h2 class="event-title">{{ currentEvent.title }}</h2>
        <p class="event-description">{{ currentEvent.description }}</p>
        
        <div class="event-options">
          <button 
            v-for="(option, index) in currentEvent.options" 
            :key="index"
            class="option-btn"
            :class="{ 'has-risk': option.success_rate && option.success_rate < 1 }"
            @click="selectOption(index)">
            <span class="option-text">{{ option.text }}</span>
            <span class="option-risk" v-if="option.success_rate && option.success_rate < 1">
              成功率: {{ Math.round(option.success_rate * 100) }}%
            </span>
            <div class="option-impacts" v-if="option.impacts && option.impacts.length">
              <span v-for="(impact, i) in option.impacts.slice(0, 2)" :key="i" 
                :class="impact.value >= 0 ? 'positive' : 'negative'">
                {{ formatImpact(impact) }}
              </span>
            </div>
          </button>
        </div>

        <!-- 结果展示 -->
        <div class="event-result" v-if="eventResult">
          <div class="result-status" :class="eventResult.success ? 'success' : 'fail'">
            {{ eventResult.success ? '✅ 成功！' : '❌ 失败...' }}
          </div>
          <div class="result-impacts">
            <div v-for="(impact, i) in eventResult.impacts" :key="i" 
              class="impact-item" :class="impact.value >= 0 ? 'positive' : 'negative'">
              {{ formatResultImpact(impact) }}
            </div>
          </div>
          <button class="continue-btn" @click="handleContinue">继续</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useGameStore } from '../stores/game'
import { buildApiUrl } from '../utils/api'

const gameStore = useGameStore()

const props = defineProps({
  events: { type: Array, default: () => [] }
})

const emit = defineEmits(['event-completed', 'all-events-done'])

const eventQueue = ref([])
const currentEvent = ref(null)
const eventResult = ref(null)

const eventCategoryClass = computed(() => {
  if (!currentEvent.value) return ''
  const cat = currentEvent.value.category || ''
  if (cat.includes('宏观')) return 'macro'
  if (cat.includes('个人')) return 'personal'
  if (cat.includes('投资')) return 'investment'
  if (cat.includes('职业')) return 'career'
  return 'random'
})

const formatImpact = (impact) => {
  const sign = impact.value >= 0 ? '+' : ''
  const suffix = impact.is_percentage ? '%' : ''
  const typeMap = {
    '现金': '💰',
    '资产': '📊',
    '收入': '💵',
    '支出': '💸',
    '健康': '❤️',
    '幸福': '😊',
    '声誉': '⭐',
    '技能': '📚'
  }
  const icon = typeMap[impact.type] || ''
  return `${icon}${sign}${impact.value.toLocaleString()}${suffix}`
}

const formatResultImpact = (impact) => {
  const sign = impact.value >= 0 ? '+' : ''
  const suffix = impact.is_percentage ? '%' : ''
  const duration = impact.duration ? ` (${impact.duration}个月)` : ''
  return `${impact.type}: ${sign}${impact.value.toLocaleString()}${suffix}${duration}`
}

const getSessionId = () => {
  try {
    const char = localStorage.getItem('currentCharacter')
    return char ? JSON.parse(char).id : null
  } catch { return null }
}

const selectOption = async (optionIndex) => {
  if (eventResult.value) return
  
  const sessionId = getSessionId()
  if (!sessionId || !currentEvent.value) return
  
  const option = currentEvent.value.options[optionIndex]
  
  try {
    const res = await fetch(buildApiUrl('/api/events/respond'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        event_id: currentEvent.value.id,
        option_id: option.id,
        player_state: {}  // 可以从 gameStore 获取
      })
    })
    const data = await res.json()
    
    if (data.success && data.result) {
      eventResult.value = data.result
      // 应用影响到游戏状态
      if (data.result.impacts) {
        await applyImpacts(data.result.impacts)
      }
    } else {
      // 后端处理失败，使用本地模拟
      throw new Error(data.error || '响应失败')
    }
    
    emit('event-completed', { event: currentEvent.value, result: data.result })
  } catch (e) {
    console.error('响应事件失败:', e)
    // 模拟结果
    const success = Math.random() < (option.success_rate || 1)
    eventResult.value = {
      success,
      impacts: success ? option.impacts : (option.fail_impacts || [])
    }
    emit('event-completed', { event: currentEvent.value, result: eventResult.value })
  }
}

const applyImpacts = async (impacts) => {
  // 这里可以调用 gameStore 更新玩家状态
  // 简化处理：刷新玩家数据
  await gameStore.loadAvatar()
}

const handleContinue = () => {
  eventResult.value = null
  // 处理队列中的下一个事件
  if (eventQueue.value.length > 0) {
    currentEvent.value = eventQueue.value.shift()
  } else {
    currentEvent.value = null
    emit('all-events-done')
  }
}

const closeIfOptional = () => {
  // 事件必须响应，不能关闭
}

// 添加新事件到队列
const addEvents = (events) => {
  if (!events || events.length === 0) return
  
  eventQueue.value.push(...events)
  if (!currentEvent.value) {
    currentEvent.value = eventQueue.value.shift()
  }
}

// 暴露方法给父组件
defineExpose({ addEvents })

// 监听全局事件
onMounted(() => {
  window.addEventListener('game-events', (e) => {
    if (e.detail && e.detail.events) {
      addEvents(e.detail.events)
    }
  })
})
</script>

<style scoped>
.event-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.event-modal {
  background: var(--term-panel-bg, #fff);
  border: 3px solid var(--term-border, #000);
  max-width: 500px;
  width: 90%;
  padding: 24px;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.event-modal.macro { border-color: #f59e0b; }
.event-modal.personal { border-color: #3b82f6; }
.event-modal.investment { border-color: #10b981; }
.event-modal.career { border-color: #8b5cf6; }

.event-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.event-category {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 8px;
  background: rgba(0,0,0,0.05);
  border: 1px solid var(--term-border);
}

.event-probability {
  font-size: 11px;
  color: #ef4444;
}

.event-title {
  font-size: 22px;
  font-weight: 900;
  margin: 0 0 12px 0;
}

.event-description {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 20px;
  color: var(--term-text-secondary);
}

.event-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 14px 16px;
  border: 2px solid var(--term-border);
  background: var(--term-panel-bg);
  cursor: pointer;
  transition: all 0.15s;
  text-align: left;
}

.option-btn:hover {
  background: var(--term-accent);
  color: #000;
  transform: translateX(4px);
}

.option-btn.has-risk {
  border-style: dashed;
}

.option-text {
  font-weight: 700;
  font-size: 14px;
}

.option-risk {
  font-size: 11px;
  color: #f59e0b;
  margin-top: 4px;
}

.option-impacts {
  display: flex;
  gap: 12px;
  margin-top: 6px;
  font-size: 12px;
}

.option-impacts .positive { color: #10b981; }
.option-impacts .negative { color: #ef4444; }

/* Result */
.event-result {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px dashed var(--term-border);
  animation: fadeIn 0.3s ease;
}

.result-status {
  font-size: 18px;
  font-weight: 900;
  margin-bottom: 12px;
}

.result-status.success { color: #10b981; }
.result-status.fail { color: #ef4444; }

.result-impacts {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.impact-item {
  font-size: 13px;
  padding: 6px 10px;
  background: rgba(0,0,0,0.03);
}

.impact-item.positive { border-left: 3px solid #10b981; }
.impact-item.negative { border-left: 3px solid #ef4444; }

.continue-btn {
  width: 100%;
  padding: 12px;
  font-weight: 800;
  font-size: 14px;
  background: var(--term-accent);
  color: #000;
  border: 2px solid #000;
  cursor: pointer;
}

.continue-btn:hover {
  background: #000;
  color: var(--term-accent);
}
</style>
