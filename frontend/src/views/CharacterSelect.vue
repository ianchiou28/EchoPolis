<template>
  <div class="terminal-page-wrapper">
    <div class="grid-bg"></div>
    <div class="crt-overlay"></div>

    <div class="content-container">
      <div class="page-header">
        <div class="header-left">
          <h1>IDENTITY ACCESS // 身份接入</h1>
          <p class="subtitle">SELECT AVATAR // 选择你的数字替身</p>
        </div>
        <button class="term-btn" @click="logout">
          DISCONNECT // 断开连接
        </button>
      </div>

      <div class="characters-grid">
        <div 
          v-for="char in characters" 
          :key="char.id"
          class="archive-card character-card"
          @click="selectCharacter(char)"
        >
          <div class="archive-header">
            <span>{{ char.mbti }}</span>
            <div class="header-actions">
              <span class="status-indicator online">ONLINE</span>
              <button class="delete-btn" @click.stop="confirmDelete(char)">[DEL]</button>
            </div>
          </div>
          <div class="archive-body">
            <div class="char-avatar-placeholder">
              {{ char.name.charAt(0) }}
            </div>
            <div class="char-details">
              <h3 class="char-name">{{ char.name }}</h3>
              <div class="char-assets">
                <span class="label">ASSETS:</span>
                <span class="value">¥{{ formatNumber(char.assets) }}</span>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <span class="access-text">>> ACCESS GRANTED</span>
          </div>
        </div>

        <!-- Create New Card -->
        <div class="archive-card create-card" @click="showCreateModal = true">
          <div class="create-content">
            <span class="plus-icon">+</span>
            <span class="create-text">INITIALIZE NEW IDENTITY // 创建新身份</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Character Modal -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="archive-card modal-card">
        <div class="archive-header">
          <span>INITIALIZE IDENTITY // 构建新身份</span>
          <span class="close-btn" @click="showCreateModal = false">[X]</span>
        </div>
        
        <div class="archive-body">
          <div class="form-group">
            <label>CODENAME // 代号</label>
            <input v-model="newCharName" type="text" class="term-input" placeholder="ENTER CODENAME..." />
          </div>

          <div class="form-group">
            <label>PERSONALITY MATRIX // 人格矩阵 (MBTI)</label>
            <div class="mbti-grid">
              <div 
                v-for="mbti in mbtiTypes" 
                :key="mbti.type"
                class="mbti-option"
                :class="{ active: newCharMBTI === mbti.type }"
                @click="newCharMBTI = mbti.type"
              >
                <span class="type-code">{{ mbti.type }}</span>
                <span class="type-name">{{ mbti.name }}</span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>FATE WHEEL // 命运轮盘</label>
            <div class="fate-section">
              <button 
                class="term-btn full-width" 
                :class="{ 'disabled': hasSpun || isSpinning }"
                @click="spinWheel" 
                :disabled="hasSpun || isSpinning"
              >
                {{ getSpinButtonText() }}
              </button>
              
              <div v-if="selectedFate" class="fate-result-box">
                <div class="result-header">
                  <span class="fate-name">{{ selectedFate.name }}</span>
                  <span class="fate-value">¥{{ formatNumber(selectedFate.initial_money) }}</span>
                </div>
                <p class="fate-desc">{{ selectedFate.description }}</p>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button class="term-btn" @click="showCreateModal = false">CANCEL // 取消</button>
            <button class="term-btn primary" @click="createCharacter" :disabled="!canCreate">
              CONFIRM ACCESS // 确认接入
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'
import { useThemeStore } from '../stores/theme'
import axios from 'axios'

const router = useRouter()
const gameStore = useGameStore()
const themeStore = useThemeStore()

const characters = ref([])
const showCreateModal = ref(false)
const newCharName = ref('')
const newCharMBTI = ref('')
const selectedFate = ref(null)
const hasSpun = ref(false)
const isSpinning = ref(false)

const mbtiTypes = ref([
  { type: 'INTJ', name: '建筑师' }, { type: 'INTP', name: '逻辑学家' },
  { type: 'ENTJ', name: '指挥官' }, { type: 'ENTP', name: '辩论家' },
  { type: 'INFJ', name: '提倡者' }, { type: 'INFP', name: '调停者' },
  { type: 'ENFJ', name: '主人公' }, { type: 'ENFP', name: '竞选者' },
  { type: 'ISTJ', name: '物流师' }, { type: 'ISFJ', name: '守护者' },
  { type: 'ESTJ', name: '总经理' }, { type: 'ESFJ', name: '执政官' },
  { type: 'ISTP', name: '鉴赏家' }, { type: 'ISFP', name: '探险家' },
  { type: 'ESTP', name: '企业家' }, { type: 'ESFP', name: '表演者' }
])

const fateWheel = ref([
  { name: '亿万富豪', description: '含着金汤匙出生，拥有顶级的资源与视野。', initial_money: 10000000 },
  { name: '富裕家庭', description: '衣食无忧，有足够的试错成本。', initial_money: 1000000 },
  { name: '中产阶级', description: '受过良好教育，生活稳定但有上升焦虑。', initial_money: 300000 },
  { name: '小康家庭', description: '比上不足比下有余，追求稳健。', initial_money: 150000 },
  { name: '普通家庭', description: '平凡的起点，每一分钱都来之不易。', initial_money: 80000 },
  { name: '温饱家庭', description: '生活拮据，必须精打细算。', initial_money: 50000 },
  { name: '贫困家庭', description: '艰难的开局，唯有奋斗才能改变命运。', initial_money: 30000 },
  { name: '赤贫家庭', description: '一无所有，除了梦想与勇气。', initial_money: 10000 }
])

const canCreate = computed(() => {
  return newCharName.value && newCharMBTI.value && selectedFate.value && !isSpinning.value
})

const formatNumber = (num) => {
  return num?.toLocaleString('zh-CN') || '0'
}

const getSpinButtonText = () => {
  if (isSpinning.value) return 'CALCULATING FATE... // 命运流转中'
  if (hasSpun.value) return 'FATE DETERMINED // 命运已定'
  return 'INITIATE FATE WHEEL // 启动命运轮盘'
}

const loadCharacters = async () => {
  const username = localStorage.getItem('username')
  console.log('[CharacterSelect] Loading characters for:', username)
  if (!username) {
    router.push('/login')
    return
  }

  try {
    const data = await gameStore.fetchCharacters(username)
    console.log('[CharacterSelect] Characters loaded:', data)
    characters.value = data
  } catch (error) {
    console.error('加载角色失败:', error)
    alert('加载角色失败，请重试')
  }
}

const selectCharacter = (char) => {
  console.log('[CharacterSelect] Selecting character:', char)
  // 切换角色前重置状态
  try {
    gameStore.resetState()
    localStorage.setItem('currentCharacter', JSON.stringify(char))
    router.push('/home')
  } catch (e) {
    console.error('Select character error:', e)
  }
}

const spinWheel = async () => {
  if (hasSpun.value || isSpinning.value) return
  
  isSpinning.value = true
  
  // 模拟轮盘转动效果
  const duration = 1500
  const interval = 100
  let elapsed = 0
  
  const timer = setInterval(() => {
    const randomIndex = Math.floor(Math.random() * fateWheel.value.length)
    selectedFate.value = fateWheel.value[randomIndex]
    elapsed += interval
    if (elapsed >= duration) {
      clearInterval(timer)
      // 最终结果
      const finalIndex = Math.floor(Math.random() * fateWheel.value.length)
      selectedFate.value = fateWheel.value[finalIndex]
      isSpinning.value = false
      hasSpun.value = true
    }
  }, interval)
}

const createCharacter = async () => {
  const username = localStorage.getItem('username')
  
  try {
    const res = await gameStore.createCharacter({
      username,
      name: newCharName.value,
      mbti: newCharMBTI.value,
      fate: selectedFate.value
    })

    if (res.success) {
      showCreateModal.value = false
      newCharName.value = ''
      newCharMBTI.value = ''
      selectedFate.value = null
      hasSpun.value = false
      loadCharacters()
    }
  } catch (error) {
    alert('创建失败：' + (error.response?.data?.detail || error.message))
  }
}

const confirmDelete = async (char) => {
  if (confirm(`Are you sure you want to delete character "${char.name}"? This action cannot be undone.`)) {
    try {
      await gameStore.deleteCharacter(char.id)
      await loadCharacters()
    } catch (error) {
      alert('Failed to delete character: ' + (error.response?.data?.detail || error.message))
    }
  }
}

const logout = () => {
  console.log('[CharacterSelect] Logging out...')
  try {
    gameStore.resetState()
  } catch (e) {
    console.error('Reset state error:', e)
  }
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('currentCharacter')
  // Keep username? No, logout should clear identity.
  // But Login.vue sets 'username'.
  // If we want to fully logout, we should clear 'username' too.
  localStorage.removeItem('username') 
  router.push('/login')
}

onMounted(() => {
  try {
    themeStore.applyTheme()
  } catch (e) {
    console.error('Theme apply error:', e)
  }
  loadCharacters()
})
</script>

<style scoped>
@import '@/styles/terminal-theme.css';

.terminal-page-wrapper {
  width: 100%;
  min-height: 100vh;
  padding: 40px;
  font-family: 'JetBrains Mono', monospace;
  position: relative;
  overflow-x: hidden;
  background-color: var(--term-bg);
  color: var(--term-text);
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 40px;
  border-bottom: 2px solid var(--term-border);
  padding-bottom: 20px;
}

.header-left h1 {
  font-size: 32px;
  font-weight: 900;
  color: var(--term-text);
  margin: 0 0 8px 0;
  text-transform: uppercase;
}

.subtitle {
  color: var(--term-text-secondary);
  font-size: 14px;
  margin: 0;
  letter-spacing: 1px;
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.character-card {
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.character-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 8px 8px 0px rgba(0,0,0,0.2);
  border-color: var(--term-accent);
}

.character-card:hover .archive-header {
  background: var(--term-accent);
  color: #000;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.delete-btn {
  background: transparent;
  border: none;
  color: #ff4444;
  font-family: inherit;
  font-size: 10px;
  cursor: pointer;
  padding: 0;
  font-weight: bold;
}

.delete-btn:hover {
  text-decoration: underline;
  color: #ff0000;
}

.character-card:hover .delete-btn {
  color: #5a0000;
}

.status-indicator {
  font-size: 10px;
  color: var(--term-success);
}

.character-card:hover .status-indicator {
  color: #000;
}

.char-avatar-placeholder {
  width: 60px;
  height: 60px;
  background: var(--term-border);
  color: var(--term-text);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 900;
  margin-bottom: 16px;
}

.char-name {
  font-size: 20px;
  font-weight: 900;
  margin: 0 0 8px 0;
  color: var(--term-text);
}

.char-assets {
  font-size: 14px;
  display: flex;
  gap: 8px;
}

.char-assets .label {
  color: var(--term-text-secondary);
}

.char-assets .value {
  color: var(--term-accent);
  font-weight: bold;
}

.card-footer {
  padding: 10px 20px;
  border-top: 2px solid var(--term-border);
  font-size: 10px;
  color: var(--term-text-secondary);
  text-align: right;
}

.create-card {
  border-style: dashed;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  cursor: pointer;
  background: transparent;
}

.create-card:hover {
  border-style: solid;
  border-color: var(--term-accent);
  background: rgba(255, 85, 0, 0.05);
}

.create-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--term-text-secondary);
}

.plus-icon {
  font-size: 48px;
  font-weight: 100;
}

.create-text {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.8);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-card {
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  margin: 0;
}

.close-btn {
  cursor: pointer;
}

.close-btn:hover {
  color: var(--term-accent);
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  color: var(--term-text-secondary);
  font-size: 11px;
  font-weight: 700;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.term-input {
  width: 100%;
  padding: 12px;
  background: var(--term-bg);
  border: 2px solid var(--term-border);
  color: var(--term-text);
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
}

.term-input:focus {
  outline: none;
  border-color: var(--term-accent);
}

.mbti-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 4px;
}

.mbti-option {
  border: 1px solid var(--term-border);
  padding: 8px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.mbti-option:hover {
  border-color: var(--term-text);
}

.mbti-option.active {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

.type-code {
  font-weight: 900;
  font-size: 14px;
}

.type-name {
  font-size: 10px;
  opacity: 0.8;
}

.fate-section {
  border: 1px solid var(--term-border);
  padding: 16px;
}

.fate-result-box {
  margin-top: 16px;
  border-top: 1px dashed var(--term-border);
  padding-top: 16px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-weight: 900;
  color: var(--term-accent);
}

.fate-desc {
  font-size: 12px;
  color: var(--term-text-secondary);
  margin: 0;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.full-width {
  width: 100%;
}

.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
