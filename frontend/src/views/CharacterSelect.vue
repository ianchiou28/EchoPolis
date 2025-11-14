<template>
  <div class="character-page">
    <div class="page-header">
      <h1>👥 选择角色</h1>
      <button class="logout-btn btn btn-ghost" @click="logout">退出登录</button>
    </div>

    <div class="characters-list">
      <div 
        v-for="char in characters" 
        :key="char.id"
        class="character-card card glass"
        @click="selectCharacter(char)"
      >
        <div class="char-avatar">{{ char.name.charAt(0) }}</div>
        <div class="char-info">
          <div class="char-name">{{ char.name }}</div>
          <div class="char-mbti">{{ char.mbti }}</div>
          <div class="char-assets">¥{{ formatNumber(char.assets) }}</div>
        </div>
      </div>

      <div class="character-card create-new card" @click="showCreateModal = true">
        <div class="create-icon">➕</div>
        <div class="create-text">创建新角色</div>
      </div>
    </div>

    <!-- 创建角色弹窗 -->
    <div v-if="showCreateModal" class="modal" @click="showCreateModal = false">
      <div class="modal-content card glass" @click.stop>
        <h2>创建新角色</h2>
        
        <div class="form-group">
          <label>角色名称</label>
          <input v-model="newCharName" type="text" class="input" placeholder="输入角色名称" />
        </div>

        <div class="form-group">
          <label>选择MBTI人格</label>
          <div class="mbti-grid">
            <div 
              v-for="mbti in mbtiTypes" 
              :key="mbti.type"
              class="mbti-option card"
              :class="{ active: newCharMBTI === mbti.type }"
              @click="newCharMBTI = mbti.type"
            >
              <div class="mbti-type">{{ mbti.type }}</div>
              <div class="mbti-name">{{ mbti.name }}</div>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>🎲 命运轮盘</label>
          <button class="spin-btn btn btn-primary" @click="spinWheel" :disabled="hasSpun">
            {{ hasSpun ? '✅ 已转动' : '🎲 转动轮盘' }}
          </button>
          <div v-if="selectedFate" class="fate-result card">
            <div class="fate-title">{{ selectedFate.name }}</div>
            <div class="fate-desc">{{ selectedFate.description }}</div>
            <div class="fate-money">初始资金: ¥{{ formatNumber(selectedFate.initial_money) }}</div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn-primary" @click="createCharacter" :disabled="!canCreate">创建角色</button>
          <button class="btn btn-ghost" @click="showCreateModal = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const characters = ref([])
const showCreateModal = ref(false)
const newCharName = ref('')
const newCharMBTI = ref('')
const selectedFate = ref(null)
const hasSpun = ref(false)

const mbtiTypes = ref([
  { type: 'INTJ', name: '建筑师' },
  { type: 'INTP', name: '逻辑学家' },
  { type: 'ENTJ', name: '指挥官' },
  { type: 'ENTP', name: '辩论家' },
  { type: 'INFJ', name: '提倡者' },
  { type: 'INFP', name: '调停者' },
  { type: 'ENFJ', name: '主人公' },
  { type: 'ENFP', name: '竞选者' },
  { type: 'ISTJ', name: '物流师' },
  { type: 'ISFJ', name: '守护者' },
  { type: 'ESTJ', name: '总经理' },
  { type: 'ESFJ', name: '执政官' },
  { type: 'ISTP', name: '鉴赏家' },
  { type: 'ISFP', name: '探险家' },
  { type: 'ESTP', name: '企业家' },
  { type: 'ESFP', name: '表演者' }
])

const fateWheel = ref([
  { name: '亿万富豪', description: '含着金汤匙出生', initial_money: 10000000 },
  { name: '富裕家庭', description: '衣食无忧的成长环境', initial_money: 1000000 },
  { name: '中产阶级', description: '标准的中产家庭', initial_money: 300000 },
  { name: '小康家庭', description: '生活稳定', initial_money: 150000 },
  { name: '普通家庭', description: '平凡的起点', initial_money: 80000 },
  { name: '温饱家庭', description: '勉强维持', initial_money: 50000 },
  { name: '贫困家庭', description: '艰难的开始', initial_money: 30000 },
  { name: '赤贫家庭', description: '最艰难的起点', initial_money: 10000 }
])

const canCreate = computed(() => {
  return newCharName.value && newCharMBTI.value && selectedFate.value
})

const formatNumber = (num) => {
  return num?.toLocaleString('zh-CN') || '0'
}

const loadCharacters = async () => {
  const username = localStorage.getItem('username')
  if (!username) {
    router.push('/login')
    return
  }

  try {
    const res = await axios.get(`/api/characters/${username}`)
    characters.value = res.data
  } catch (error) {
    console.error('加载角色失败:', error)
  }
}

const selectCharacter = (char) => {
  localStorage.setItem('currentCharacter', JSON.stringify(char))
  router.push('/home')
}

const spinWheel = () => {
  if (hasSpun.value) {
    alert('命运轮盘只能转动一次！')
    return
  }
  const randomIndex = Math.floor(Math.random() * fateWheel.value.length)
  selectedFate.value = fateWheel.value[randomIndex]
  hasSpun.value = true
}

const createCharacter = async () => {
  const username = localStorage.getItem('username')
  
  try {
    const res = await axios.post('/api/characters/create', {
      username,
      name: newCharName.value,
      mbti: newCharMBTI.value,
      fate: selectedFate.value
    })

    if (res.data.success) {
      alert('角色创建成功！')
      showCreateModal.value = false
      newCharName.value = ''
      newCharMBTI.value = ''
      selectedFate.value = null
      hasSpun.value = false
      loadCharacters()
    }
  } catch (error) {
    alert('创建失败：' + error.message)
  }
}

const logout = () => {
  localStorage.removeItem('username')
  localStorage.removeItem('currentCharacter')
  router.push('/login')
}

onMounted(() => {
  loadCharacters()
})
</script>

<style scoped>
.character-page {
  width: 100%;
  min-height: 100vh;
  padding: 40px;
  background: var(--bg-gradient);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.page-header h1 {
  color: var(--text);
  font-size: 36px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.characters-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.character-card {
  padding: 30px;
  cursor: pointer;
  transition: all var(--dur-med) var(--ease-standard);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.character-card:hover { transform: translateY(-5px); }

.char-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: bold;
  color: white;
  margin-bottom: 15px;
  box-shadow: 0 8px 24px var(--primary-glow);
}

.char-info { text-align: center; }

.char-name { font-size: 20px; font-weight: bold; color: var(--text); margin-bottom: 5px; }
.char-mbti { font-size: 14px; color: var(--primary-400); margin-bottom: 10px; }
.char-assets { font-size: 16px; color: var(--muted); }

.create-new { border: 1px dashed var(--primary-400); background: var(--surface); }
.create-icon { font-size: 48px; color: var(--primary-400); margin-bottom: 10px; }
.create-text { font-size: 16px; color: var(--primary-400); font-weight: bold; }

.modal-content h2 { margin-bottom: 30px; color: var(--text); }

.form-group { margin-bottom: 25px; }
.form-group label { display: block; margin-bottom: 10px; font-weight: bold; color: var(--text); }

.mbti-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }

.mbti-option { padding: 15px 10px; border: 1px solid var(--border); border-radius: var(--radius-md); text-align: center; cursor: pointer; transition: all var(--dur-fast) var(--ease-standard); background: var(--surface); }
.mbti-option:hover { border-color: var(--highlight); }
.mbti-option.active { border-color: color-mix(in srgb, var(--primary-500) 35%, var(--border)); background: color-mix(in srgb, var(--primary-500) 10%, var(--surface)); }

.mbti-type { font-weight: bold; color: var(--text); margin-bottom: 5px; }
.mbti-name { font-size: 12px; color: var(--muted); }

.spin-btn { width: 100%; margin-bottom: 15px; }

.fate-result { background: var(--surface); padding: 20px; border-radius: var(--radius-md); border: 1px solid var(--border); }
.fate-title { font-size: 20px; font-weight: bold; color: var(--primary-400); margin-bottom: 10px; }
.fate-desc { color: var(--muted); margin-bottom: 10px; }
.fate-money { font-size: 18px; font-weight: bold; color: var(--text); }

.modal-actions { display: flex; gap: 10px; margin-top: 30px; }
.modal-actions .btn { flex: 1; }
</style>
