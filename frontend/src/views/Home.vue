<template>
  <div class="container">
    <div class="card">
      <h2>🎮 开始你的Echopolis之旅</h2>
      
      <div v-if="!gameStore.avatar" class="create-avatar">
        <h3>创建AI化身</h3>
        <input v-model="avatarName" placeholder="输入化身姓名" class="input" />
        
        <div class="mbti-selection">
          <h4>选择MBTI人格类型:</h4>
          <div class="mbti-grid">
            <button 
              v-for="(info, type) in mbtiTypes" 
              :key="type"
              @click="selectedMBTI = type"
              :class="['btn', selectedMBTI === type ? 'btn-primary' : 'btn-secondary']"
            >
              {{ type }} - {{ info.description }}
            </button>
          </div>
        </div>
        
        <button 
          @click="createAvatar" 
          :disabled="!avatarName || !selectedMBTI"
          class="btn btn-primary"
        >
          🎲 创建化身 (随机命运轮盘)
        </button>
      </div>
      
      <div v-else class="avatar-created">
        <h3>✨ 化身创建成功!</h3>
        <div class="avatar-info">
          <p><strong>姓名:</strong> {{ gameStore.avatar.name }}</p>
          <p><strong>人格:</strong> {{ gameStore.avatar.mbti }}</p>
          <p><strong>命运:</strong> {{ gameStore.avatar.fate }}</p>
          <p><strong>初始资金:</strong> {{ formatMoney(gameStore.avatar.credits) }} CP</p>
        </div>
        <router-link to="/game" class="btn btn-primary">🚀 开始游戏</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useGameStore } from '../stores/game'

const gameStore = useGameStore()
const avatarName = ref('')
const selectedMBTI = ref('')
const mbtiTypes = ref({})

onMounted(async () => {
  await gameStore.loadMBTITypes()
  mbtiTypes.value = gameStore.mbtiTypes
})

const createAvatar = async () => {
  await gameStore.createAvatar(avatarName.value, selectedMBTI.value)
}

const formatMoney = (amount) => {
  return new Intl.NumberFormat('zh-CN').format(amount)
}
</script>

<style scoped>
.create-avatar, .avatar-created {
  text-align: center;
}

.mbti-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 10px;
  margin: 20px 0;
}

.btn-secondary {
  background: #f8f9fa;
  color: #333;
  border: 2px solid #e1e5e9;
}

.btn-secondary:hover {
  background: #e9ecef;
}

.avatar-info {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
  margin: 20px 0;
  text-align: left;
}

.avatar-info p {
  margin: 10px 0;
  font-size: 16px;
}
</style>