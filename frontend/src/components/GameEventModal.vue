<template>
  <div class="game-event-overlay" v-if="visible" @click.self="close">
    <div class="game-event-modal">
      <div class="modal-header">
        <span class="event-icon">{{ getEventIcon(currentEvent?.event_type) }}</span>
        <h2>{{ currentEvent?.game_title }}</h2>
        <button class="close-btn" @click="close">✕</button>
      </div>

      <div class="modal-body">
        <!-- 事件描述 -->
        <div class="event-description">
          <p>{{ currentEvent?.game_description }}</p>
        </div>

        <!-- 事件来源标签 -->
        <div class="event-source-tag" v-if="currentEvent?.is_from_real_event">
          <span class="real-tag">📡 基于真实事件</span>
          <span class="original-title">{{ currentEvent?.original_title }}</span>
        </div>

        <!-- 潜在影响 -->
        <div class="potential-impact" v-if="currentEvent?.potential_impact">
          <h4>💡 潜在影响</h4>
          <div class="impact-grid">
            <div 
              v-for="(value, key) in currentEvent.potential_impact" 
              :key="key"
              :class="['impact-item', value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral']"
            >
              <span class="impact-label">{{ formatImpactKey(key) }}</span>
              <span class="impact-value">{{ formatImpactValue(value) }}</span>
            </div>
          </div>
        </div>

        <!-- 选项按钮 -->
        <div class="options-section">
          <h4>🎯 你的选择</h4>
          <div class="options-list">
            <button 
              v-for="(option, index) in currentEvent?.options" 
              :key="index"
              :class="['option-btn', { selected: selectedOption === index }]"
              @click="selectOption(index)"
              :disabled="responded"
            >
              <span class="option-icon">{{ getOptionIcon(index) }}</span>
              <span class="option-text">{{ option }}</span>
            </button>
          </div>
        </div>

        <!-- 已回应状态 -->
        <div class="response-result" v-if="responded">
          <div class="result-icon">✅</div>
          <p>你的选择已记录！这将影响你的角色发展...</p>
        </div>
      </div>

      <div class="modal-footer">
        <button 
          class="confirm-btn" 
          @click="submitResponse" 
          :disabled="selectedOption === null || responded || submitting"
        >
          {{ submitting ? '提交中...' : responded ? '已完成' : '确认选择' }}
        </button>
        <button class="skip-btn" @click="skipEvent" :disabled="responded">
          跳过此事件
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useGameStore } from '../stores/game'
import { buildApiUrl } from '@/utils/api'

const props = defineProps({
  visible: Boolean,
  event: Object,
  personId: String
})

const emit = defineEmits(['close', 'responded'])

const gameStore = useGameStore()

const currentEvent = computed(() => props.event)
const selectedOption = ref(null)
const responded = ref(false)
const submitting = ref(false)

watch(() => props.visible, (newVal) => {
  if (newVal) {
    // 重置状态
    selectedOption.value = null
    responded.value = false
  }
})

function getEventIcon(type) {
  const icons = {
    'economic': '💰',
    'policy': '📜',
    'market': '📈',
    'career': '💼',
    'social': '👥',
    'tech': '🚀',
    'crisis': '⚠️',
    'opportunity': '🌟'
  }
  return icons[type] || '📌'
}

function getOptionIcon(index) {
  const icons = ['🅰️', '🅱️', '🅲️', '🅳️']
  return icons[index] || '◯'
}

function formatImpactKey(key) {
  const labels = {
    'wealth': '财富',
    'happiness': '幸福',
    'health': '健康',
    'career': '事业',
    'social': '社交',
    'stress': '压力',
    'reputation': '声望'
  }
  return labels[key] || key
}

function formatImpactValue(value) {
  if (value > 0) return `+${value}`
  return value.toString()
}

function selectOption(index) {
  if (!responded.value) {
    selectedOption.value = index
  }
}

async function submitResponse() {
  if (selectedOption.value === null || responded.value) return
  
  submitting.value = true
  try {
    const response = await fetch(buildApiUrl('/api/event-pool/respond'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        person_id: props.personId || gameStore.currentPerson?.id || 'unknown',
        event_id: currentEvent.value.game_event_id,
        response_choice: selectedOption.value,
        response_text: currentEvent.value.options[selectedOption.value]
      })
    })
    
    const data = await response.json()
    if (data.success) {
      responded.value = true
      emit('responded', {
        eventId: currentEvent.value.game_event_id,
        choice: selectedOption.value,
        option: currentEvent.value.options[selectedOption.value]
      })
    } else {
      alert('提交失败: ' + data.message)
    }
  } catch (e) {
    console.error('提交回应失败:', e)
    alert('网络错误，请重试')
  } finally {
    submitting.value = false
  }
}

function skipEvent() {
  emit('close')
}

function close() {
  emit('close')
}
</script>

<style scoped>
.game-event-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.game-event-modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 520px;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s;
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: linear-gradient(135deg, #E04F00, #ff7a33);
  color: white;
}

.event-icon {
  font-size: 32px;
}

.modal-header h2 {
  flex: 1;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.event-description {
  background: #f8f8f8;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.event-description p {
  margin: 0;
  line-height: 1.6;
  color: #333;
}

.event-source-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #e6f7ff;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 13px;
}

.real-tag {
  color: #1890ff;
  font-weight: 500;
}

.original-title {
  color: #666;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.potential-impact {
  margin-bottom: 20px;
}

.potential-impact h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
}

.impact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
}

.impact-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  border-radius: 6px;
  background: #f5f5f5;
}

.impact-item.positive {
  background: #f6ffed;
  color: #52c41a;
}

.impact-item.negative {
  background: #fff2f0;
  color: #ff4d4f;
}

.impact-label {
  font-size: 12px;
  color: #999;
}

.impact-value {
  font-size: 18px;
  font-weight: bold;
}

.options-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  background: white;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.option-btn:hover:not(:disabled) {
  border-color: #E04F00;
  background: #fff8f5;
}

.option-btn.selected {
  border-color: #E04F00;
  background: #E04F00;
  color: white;
}

.option-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.option-icon {
  font-size: 20px;
}

.option-text {
  flex: 1;
  font-size: 14px;
}

.response-result {
  text-align: center;
  padding: 20px;
  background: #f6ffed;
  border-radius: 8px;
  margin-top: 16px;
}

.result-icon {
  font-size: 40px;
  margin-bottom: 8px;
}

.response-result p {
  margin: 0;
  color: #52c41a;
  font-weight: 500;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
}

.confirm-btn, .skip-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn {
  background: #E04F00;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background: #c44500;
}

.confirm-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.skip-btn {
  background: #f0f0f0;
  color: #666;
}

.skip-btn:hover:not(:disabled) {
  background: #e0e0e0;
}

.skip-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
