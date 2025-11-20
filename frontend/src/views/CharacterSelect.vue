<template>
  <div class="character-page">
    <div class="game-bg"></div>
    <div class="page-header">
      <div class="header-content">
        <h1>IDENTITY ACCESS // 身份接入</h1>
        <p class="subtitle">SELECT AVATAR // 选择你的数字替身</p>
      </div>
      <button class="logout-btn btn ghost" @click="logout">
        <span class="icon">🔌</span> DISCONNECT // 断开连接
      </button>
    </div>

    <div class="characters-list">
      <div 
        v-for="char in characters" 
        :key="char.id"
        class="character-card glass-panel tech-border"
        @click="selectCharacter(char)"
      >
        <div class="char-avatar-wrapper">
          <div class="char-avatar">{{ char.name.charAt(0) }}</div>
          <div class="status-dot online"></div>
        </div>
        <div class="char-info">
          <div class="char-name">{{ char.name }}</div>
          <div class="char-meta">
            <span class="tag mbti">{{ char.mbti }}</span>
            <span class="tag assets">¥{{ formatNumber(char.assets) }}</span>
          </div>
        </div>
        <div class="hover-effect"></div>
      </div>

      <div class="character-card create-new glass-panel tech-border" @click="showCreateModal = true">
        <div class="create-icon">
          <span class="plus">+</span>
        </div>
        <div class="create-text">NEW IDENTITY // 创建新身份</div>
      </div>
    </div>

    <!-- 创建角色弹窗 -->
    <transition name="modal-fade">
      <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
        <div class="modal-content glass-panel tech-border" @click.stop>
          <div class="modal-header">
            <h2>INITIALIZE IDENTITY // 构建新身份</h2>
            <p>DEFINE CORE PERSONALITY // 定义核心人格</p>
          </div>
          
          <div class="form-section">
            <div class="form-group">
              <label>CODENAME // 代号</label>
              <input v-model="newCharName" type="text" class="input-cyber" placeholder="ENTER CODENAME..." />
            </div>

            <div class="form-group">
              <label>PERSONALITY MATRIX // 人格矩阵 (MBTI)</label>
              <div class="mbti-grid custom-scrollbar">
                <div 
                  v-for="mbti in mbtiTypes" 
                  :key="mbti.type"
                  class="mbti-option"
                  :class="{ active: newCharMBTI === mbti.type, [getMbtiGroup(mbti.type)]: true }"
                  @click="newCharMBTI = mbti.type"
                >
                  <div class="mbti-type">{{ mbti.type }}</div>
                  <div class="mbti-name">{{ mbti.name }}</div>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>FATE WHEEL // 命运轮盘</label>
              <div class="fate-section">
                <button 
                  class="spin-btn" 
                  :class="{ 'spinning': isSpinning, 'done': hasSpun }"
                  @click="spinWheel" 
                  :disabled="hasSpun || isSpinning"
                >
                  <span class="spin-icon">{{ hasSpun ? '✅' : '🎲' }}</span>
                  <span class="spin-text">{{ getSpinButtonText() }}</span>
                </button>
                
                <transition name="fade-slide">
                  <div v-if="selectedFate" class="fate-result">
                    <div class="fate-header">
                      <span class="fate-title">{{ selectedFate.name }}</span>
                      <span class="fate-money">¥{{ formatNumber(selectedFate.initial_money) }}</span>
                    </div>
                    <div class="fate-desc">{{ selectedFate.description }}</div>
                  </div>
                </transition>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button class="btn ghost" @click="showCreateModal = false">CANCEL // 取消</button>
            <button class="btn primary" @click="createCharacter" :disabled="!canCreate">
              CONFIRM ACCESS // 确认接入
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'

const router = useRouter()
const gameStore = useGameStore()
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

const getMbtiGroup = (type) => {
  if (type.includes('NT')) return 'analysts'
  if (type.includes('NF')) return 'diplomats'
  if (type.includes('SJ')) return 'sentinels'
  if (type.includes('SP')) return 'explorers'
  return ''
}

const getSpinButtonText = () => {
  if (isSpinning.value) return '命运流转中...'
  if (hasSpun.value) return '命运已定'
  return '启动命运轮盘'
}

const loadCharacters = async () => {
  const username = localStorage.getItem('username')
  if (!username) {
    router.push('/login')
    return
  }

  try {
    const data = await gameStore.fetchCharacters(username)
    characters.value = data
  } catch (error) {
    console.error('加载角色失败:', error)
  }
}

const selectCharacter = (char) => {
  localStorage.setItem('currentCharacter', JSON.stringify(char))
  router.push('/home')
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
      // 最终结果（加权随机，这里简化为均匀随机，实际可调整）
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
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap');

.character-page {
  width: 100%;
  min-height: 100vh;
  padding: 40px;
  position: relative;
  overflow-x: hidden;
  font-family: 'Rajdhani', sans-serif;
}

.page-header {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 40px;
  z-index: 1;
}

.header-content h1 {
  color: #e2e8f0;
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: 0.05em;
  font-family: 'Rajdhani', sans-serif;
}

.subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 1px;
}

.characters-list {
  position: relative;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  z-index: 1;
}

.character-card {
  position: relative;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.6);
}

.character-card:hover {
  transform: translateY(-4px);
  border-color: rgba(59,130,246,0.4);
  box-shadow: 0 12px 30px rgba(59,130,246,0.15);
}

.char-avatar-wrapper {
  position: relative;
  margin-bottom: 16px;
}

.char-avatar {
  width: 72px;
  height: 72px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
  color: white;
  box-shadow: 0 8px 16px rgba(59,130,246,0.3);
  font-family: 'Rajdhani', sans-serif;
}

.status-dot {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #1e293b;
}

.status-dot.online { background: #10b981; box-shadow: 0 0 8px #10b981; }

.char-info { text-align: center; width: 100%; }

.char-name {
  font-size: 20px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 12px;
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 1px;
}

.char-meta {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.tag {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 2px;
  font-weight: 600;
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 0.5px;
}

.tag.mbti { background: rgba(139,92,246,0.15); color: #a78bfa; border: 1px solid rgba(139,92,246,0.2); }
.tag.assets { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }

.create-new {
  border: 1px dashed rgba(148,163,184,0.3);
  background: rgba(30,41,59,0.3);
  justify-content: center;
  min-height: 200px;
}

.create-new:hover {
  border-color: #3b82f6;
  background: rgba(30,41,59,0.5);
}

.create-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(59,130,246,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.create-new:hover .create-icon {
  background: #3b82f6;
  color: white;
  transform: scale(1.1);
}

.create-text {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 600;
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 1px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-content {
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 32px;
  background: #1e293b;
  border: 1px solid rgba(59,130,246,0.2);
}

.modal-header { margin-bottom: 24px; }
.modal-header h2 { margin: 0 0 8px 0; color: #e2e8f0; font-size: 24px; font-family: 'Rajdhani', sans-serif; }
.modal-header p { margin: 0; color: #94a3b8; font-size: 14px; font-family: 'Rajdhani', sans-serif; letter-spacing: 1px; }

.form-group { margin-bottom: 24px; }
.form-group label { display: block; margin-bottom: 8px; font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-family: 'Rajdhani', sans-serif; font-weight: 600; }

.input-cyber {
  width: 100%;
  padding: 12px 16px;
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(148,163,184,0.2);
  border-radius: 4px;
  color: #e2e8f0;
  font-size: 14px;
  transition: all 0.2s;
  font-family: 'Rajdhani', sans-serif;
}

.input-cyber:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.2);
}

.mbti-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 4px;
}

.mbti-option {
  padding: 10px;
  border-radius: 4px;
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(148,163,184,0.1);
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
}

.mbti-option:hover { background: rgba(30,41,59,0.8); }
.mbti-option.active { border-color: #3b82f6; background: rgba(59,130,246,0.1); box-shadow: 0 0 12px rgba(59,130,246,0.2); }

.mbti-type { font-weight: 700; font-size: 14px; color: #e2e8f0; font-family: 'Rajdhani', sans-serif; }
.mbti-name { font-size: 11px; color: #94a3b8; font-family: 'Rajdhani', sans-serif; }

/* MBTI Group Colors */
.analysts .mbti-type { color: #a78bfa; }
.diplomats .mbti-type { color: #34d399; }
.sentinels .mbti-type { color: #60a5fa; }
.explorers .mbti-type { color: #f59e0b; }

.spin-btn {
  width: 100%;
  padding: 16px;
  border-radius: 4px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  color: white;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.spin-btn:disabled { opacity: 0.7; cursor: not-allowed; filter: grayscale(0.5); }
.spin-btn.done { background: #10b981; }

.fate-result {
  margin-top: 16px;
  padding: 16px;
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(245,158,11,0.3);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.fate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.fate-title { font-weight: 700; color: #f59e0b; font-family: 'Rajdhani', sans-serif; font-size: 16px; }
.fate-money { font-family: 'Rajdhani', sans-serif; color: #e2e8f0; font-weight: 600; font-size: 16px; }
.fate-desc { font-size: 13px; color: #94a3b8; line-height: 1.5; font-family: 'Rajdhani', sans-serif; }

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.btn.primary { flex: 1; }

/* Tech Border Effect */
.tech-border {
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
  position: relative;
}

.tech-border::after {
  content: '';
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 10px;
  height: 10px;
  border-bottom: 2px solid #3b82f6;
  border-right: 2px solid #3b82f6;
}

.tech-border::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  width: 10px;
  height: 10px;
  border-top: 2px solid #3b82f6;
  border-left: 2px solid #3b82f6;
}

/* Transitions */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.4s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(10px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
