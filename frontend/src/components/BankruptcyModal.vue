<template>
  <div class="bankruptcy-modal-overlay" v-if="visible">
    <div class="bankruptcy-modal">
      <div class="modal-icon">💸</div>
      <h2>破产清算</h2>
      <p class="message">
        你的现金流已枯竭，无法继续维持在这个城市的生存。
        <br>
        <span class="sub-message">所有的资产将被清算，你的旅程到此结束。</span>
      </p>
      
      <div class="stats-summary">
        <div class="stat-row">
          <span>最终总资产:</span>
          <span class="value negative">¥{{ formatNumber(finalAssets) }}</span>
        </div>
        <div class="stat-row">
          <span>生存月数:</span>
          <span class="value">{{ survivalMonths }} 个月</span>
        </div>
      </div>

      <div class="actions">
        <button class="btn primary large" @click="handleRestart">
          🔄 重新开始
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useGameStore } from '../stores/game'
import { useRouter } from 'vue-router'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const gameStore = useGameStore()
const router = useRouter()

const finalAssets = computed(() => gameStore.assets.total)
const survivalMonths = computed(() => gameStore.avatar?.current_month || 0)

const formatNumber = (num) => Number(num || 0).toLocaleString('zh-CN')

const handleRestart = async () => {
  // 清除当前角色会话
  const character = gameStore.getCurrentCharacter()
  if (character) {
    try {
      await gameStore.deleteCharacter(character.id)
    } catch (e) {
      console.error('删除角色失败', e)
    }
  }
  
  // 清除本地存储
  localStorage.removeItem('currentCharacter')
  localStorage.removeItem('session_id')
  
  // 重置状态
  gameStore.resetState()
  
  // 跳转到角色选择
  router.push('/character-select')
}
</script>

<style scoped>
.bankruptcy-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.5s ease-out;
}

.bankruptcy-modal {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 2px solid #ef4444;
  border-radius: 20px;
  padding: 40px;
  width: min(500px, 90vw);
  text-align: center;
  box-shadow: 0 0 50px rgba(239, 68, 68, 0.3);
  animation: slideUp 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.modal-icon {
  font-size: 64px;
  margin-bottom: 20px;
  animation: shake 0.8s ease-in-out infinite;
}

h2 {
  color: #ef4444;
  font-size: 32px;
  margin: 0 0 16px 0;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.message {
  color: #e2e8f0;
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 30px;
}

.sub-message {
  color: #94a3b8;
  font-size: 14px;
  display: block;
  margin-top: 8px;
}

.stats-summary {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 15px;
  color: #cbd5e1;
}

.stat-row:last-child {
  margin-bottom: 0;
}

.value {
  font-weight: 700;
  color: #fff;
}

.value.negative {
  color: #ef4444;
}

.actions {
  display: flex;
  justify-content: center;
}

.btn {
  border: none;
  border-radius: 12px;
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn.primary {
  background: #ef4444;
  color: white;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
}

.btn.primary:hover {
  background: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.6);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes shake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
}
</style>
