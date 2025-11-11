<template>
  <div class="container">
    <div class="card">
      <h2>🎮 开始你的Echopolis之旅</h2>

      <div v-if="gameStore.user">
        <div class="avatar-list" v-if="gameStore.avatars.length">
          <h3>选择已有化身</h3>
          <ul>
            <li v-for="a in gameStore.avatars" :key="a.avatar_id" class="avatar-item">
              <div class="info">
                <div class="name">{{ a.name }}（{{ a.mbti }}｜{{ a.fate }}）</div>
                <div class="stats">现金: {{ formatMoney(a.credits) }} CP｜健康: {{ a.health }}｜精力: {{ a.energy }}｜幸福: {{ a.happiness }}｜信任: {{ a.trust_level }}</div>
              </div>
              <div class="actions">
                <button class="btn btn-primary" @click="selectAvatar(a.avatar_id)">使用此化身</button>
                <button class="btn btn-secondary" @click="resetAvatar(a.avatar_id)">重置此化身</button>
              </div>
            </li>
          </ul>
        </div>
      </div>

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
        <h3>✨ 化身已准备好</h3>
        <div class="avatar-info">
          <p><strong>姓名:</strong> {{ gameStore.avatar.name }}</p>
          <p><strong>人格:</strong> {{ gameStore.avatar.mbti }}</p>
          <p><strong>命运:</strong> {{ gameStore.avatar.fate }}</p>
          <p><strong>资金:</strong> {{ formatMoney(gameStore.avatar.credits) }} CP</p>
        </div>
        <router-link to="/game" class="btn btn-primary">🚀 进入游戏</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'

const router = useRouter()
const gameStore = useGameStore()
const avatarName = ref('')
const selectedMBTI = ref('')
const mbtiTypes = ref({})

onMounted(async () => {
  await gameStore.loadMBTITypes()
  mbtiTypes.value = gameStore.mbtiTypes
  if (gameStore.user) {
    await gameStore.fetchAvatars()
  }
})

const createAvatar = async () => {
  await gameStore.createAvatar(avatarName.value, selectedMBTI.value)
}

const selectAvatar = async (avatarId) => {
  await gameStore.selectAvatar(avatarId)
}

const resetAvatar = async (avatarId) => {
  if (confirm('确认要重置该化身到初始状态吗？此操作不可撤销')) {
    await gameStore.resetAvatar(avatarId)
  }
}

const formatMoney = (amount) => new Intl.NumberFormat('zh-CN').format(amount)
</script>

<style scoped>
.create-avatar, .avatar-created {
  text-align: center;
}

.avatar-list ul { list-style: none; padding: 0; }
.avatar-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
.avatar-item .info { flex: 1; }
.avatar-item .name { font-weight: 600; margin-bottom: 4px; }
.avatar-item .stats { color: #666; font-size: 12px; }
.avatar-item .actions { display: flex; gap: 8px; }

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