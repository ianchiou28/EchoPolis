<template>
  <div class="view-container">
    <div class="view-header">
      <h2>头像商店 // AVATAR SHOP</h2>
      <div class="header-line"></div>
    </div>

    <!-- Coins Bar -->
    <div class="coins-bar">
      <div class="coins-display">
        <span class="coins-icon">🪙</span>
        <span class="coins-amount">{{ formatNumber(avatarCoins) }}</span>
        <span class="coins-label">成就金币</span>
      </div>
      <div class="current-avatar-display">
        <span class="current-label">当前头像</span>
        <div class="current-avatar-preview" :style="{ backgroundColor: currentAvatarInfo?.color }">
          {{ currentAvatarInfo?.emoji || '🎭' }}
        </div>
        <span class="current-name">{{ currentAvatarInfo?.name || '默认' }}</span>
      </div>
    </div>

    <!-- Rarity Filter -->
    <div class="rarity-bar">
      <span v-for="r in rarities" :key="r.id"
        :class="['rarity-tab', r.id, { active: currentRarity === r.id }]"
        @click="currentRarity = r.id">
        {{ r.name }} <span class="count">({{ getRarityCount(r.id) }})</span>
      </span>
    </div>

    <!-- Avatar Grid -->
    <div class="avatar-scroll">
      <div class="avatar-grid">
        <div v-for="avatar in filteredAvatars" :key="avatar.id"
          :class="['avatar-card', avatar.rarity.toLowerCase(), { 
            owned: ownedAvatars.includes(avatar.id),
            equipped: currentAvatar === avatar.id,
            locked: avatar.required_achievement && !achievementIds.includes(avatar.required_achievement)
          }]"
          @click="showAvatarDetail(avatar)">
          
          <div class="avatar-preview" :style="{ backgroundColor: avatar.color }">
            {{ avatar.emoji }}
          </div>
          
          <div class="avatar-info">
            <div class="avatar-name">{{ avatar.name }}</div>
            <div class="avatar-rarity">{{ avatar.rarity }}</div>
          </div>
          
          <div class="avatar-footer">
            <template v-if="ownedAvatars.includes(avatar.id)">
              <span v-if="currentAvatar === avatar.id" class="equipped-tag">✓ 使用中</span>
              <span v-else class="owned-tag">已拥有</span>
            </template>
            <template v-else>
              <span class="price-tag">🪙 {{ formatNumber(avatar.price) }}</span>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="selectedAvatar" class="modal-overlay" @click="selectedAvatar = null">
      <div class="modal-card avatar-modal" @click.stop>
        <div class="modal-avatar-preview" :style="{ backgroundColor: selectedAvatar.color }">
          {{ selectedAvatar.emoji }}
        </div>
        <h3>{{ selectedAvatar.name }}</h3>
        <p class="modal-desc">{{ selectedAvatar.description }}</p>
        
        <div :class="['modal-rarity', selectedAvatar.rarity.toLowerCase()]">
          {{ selectedAvatar.rarity }}
        </div>
        
        <div v-if="selectedAvatar.required_achievement" class="modal-requirement">
          <span class="req-label">🔐 需要成就</span>
          <span :class="{ unlocked: achievementIds.includes(selectedAvatar.required_achievement) }">
            {{ getAchievementName(selectedAvatar.required_achievement) }}
            <span v-if="achievementIds.includes(selectedAvatar.required_achievement)" class="check">✓</span>
          </span>
        </div>
        
        <div v-if="selectedAvatar.required_count" class="modal-requirement">
          <span class="req-label">🏆 需要成就数</span>
          <span :class="{ unlocked: achievementCount >= selectedAvatar.required_count }">
            {{ achievementCount }} / {{ selectedAvatar.required_count }}
          </span>
        </div>
        
        <div class="modal-price">
          <span class="price-label">价格</span>
          <span class="price-value">🪙 {{ formatNumber(selectedAvatar.price) }}</span>
        </div>
        
        <div class="modal-actions">
          <template v-if="ownedAvatars.includes(selectedAvatar.id)">
            <button v-if="currentAvatar !== selectedAvatar.id" class="term-btn primary" @click="equipAvatar">
              装备头像
            </button>
            <button v-else class="term-btn" disabled>当前使用中</button>
          </template>
          <template v-else>
            <button 
              class="term-btn primary" 
              :disabled="!canPurchase(selectedAvatar)"
              @click="purchaseAvatar">
              {{ getPurchaseButtonText(selectedAvatar) }}
            </button>
          </template>
          <button class="term-btn" @click="selectedAvatar = null">关闭</button>
        </div>
      </div>
    </div>
    
    <!-- Toast Message -->
    <div v-if="toast" :class="['toast', toast.type]">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from '../../stores/game'
import { buildApiUrl } from '../../utils/api'

const emit = defineEmits(['avatar-changed'])

const gameStore = useGameStore()

// 获取当前会话ID
const getSessionId = () => {
  try {
    const char = localStorage.getItem('currentCharacter')
    return char ? JSON.parse(char).id : null
  } catch { return null }
}

const allAvatars = ref([])
const ownedAvatars = ref(['default_orange'])
const currentAvatar = ref('default_orange')
const currentAvatarInfo = ref(null)
const avatarCoins = ref(0)
const achievementCount = ref(0)
const achievementIds = ref([])
const selectedAvatar = ref(null)
const currentRarity = ref('all')
const toast = ref(null)

const rarities = [
  { id: 'all', name: '全部' },
  { id: 'common', name: '普通' },
  { id: 'rare', name: '稀有' },
  { id: 'epic', name: '史诗' },
  { id: 'legendary', name: '传说' }
]

const achievementNameMap = {
  'COMEBACK': '绝地反击',
  'W1M': '百万富翁',
  'W10M': '千万富翁',
  'W100M': '亿万富翁',
  'FIRST_STOCK': '初入股市'
}

const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toLocaleString()
}

const getRarityCount = (rarity) => {
  if (rarity === 'all') return allAvatars.value.length
  return allAvatars.value.filter(a => a.rarity.toLowerCase() === rarity).length
}

const filteredAvatars = computed(() => {
  if (currentRarity.value === 'all') return allAvatars.value
  return allAvatars.value.filter(a => a.rarity.toLowerCase() === currentRarity.value)
})

const showAvatarDetail = (avatar) => {
  selectedAvatar.value = avatar
}

const getAchievementName = (achId) => {
  return achievementNameMap[achId] || achId
}

const canPurchase = (avatar) => {
  // 检查金币
  if (avatarCoins.value < avatar.price) return false
  
  // 检查成就要求
  if (avatar.required_achievement && !achievementIds.value.includes(avatar.required_achievement)) {
    return false
  }
  
  // 检查成就数量要求
  if (avatar.required_count && achievementCount.value < avatar.required_count) {
    return false
  }
  
  return true
}

const getPurchaseButtonText = (avatar) => {
  if (avatarCoins.value < avatar.price) {
    return `金币不足 (需要 ${formatNumber(avatar.price)})`
  }
  if (avatar.required_achievement && !achievementIds.value.includes(avatar.required_achievement)) {
    return `需要成就: ${getAchievementName(avatar.required_achievement)}`
  }
  if (avatar.required_count && achievementCount.value < avatar.required_count) {
    return `需要 ${avatar.required_count} 个成就`
  }
  return `购买 (🪙 ${formatNumber(avatar.price)})`
}

const showToast = (message, type = 'success') => {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3000)
}

const purchaseAvatar = async () => {
  if (!selectedAvatar.value || !canPurchase(selectedAvatar.value)) return
  
  const sessionId = getSessionId()
  if (!sessionId) {
    showToast('请先登录', 'error')
    return
  }
  
  try {
    const response = await fetch(buildApiUrl('/api/avatar/purchase'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        avatar_id: selectedAvatar.value.id
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      showToast(data.message, 'success')
      ownedAvatars.value.push(selectedAvatar.value.id)
      avatarCoins.value = data.new_coins
      selectedAvatar.value = null
    } else {
      showToast(data.error || '购买失败', 'error')
    }
  } catch (error) {
    console.error('Purchase error:', error)
    showToast('购买失败', 'error')
  }
}

const equipAvatar = async () => {
  if (!selectedAvatar.value) return
  
  const sessionId = getSessionId()
  if (!sessionId) {
    showToast('请先登录', 'error')
    return
  }
  
  try {
    const response = await fetch(buildApiUrl('/api/avatar/equip'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        avatar_id: selectedAvatar.value.id
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      showToast(data.message, 'success')
      currentAvatar.value = selectedAvatar.value.id
      currentAvatarInfo.value = selectedAvatar.value
      // 通知父组件头像已更改
      emit('avatar-changed', selectedAvatar.value)
      selectedAvatar.value = null
    } else {
      showToast(data.error || '装备失败', 'error')
    }
  } catch (error) {
    console.error('Equip error:', error)
    showToast('装备失败', 'error')
  }
}

const loadShopData = async () => {
  const sessionId = getSessionId()
  if (!sessionId) {
    console.log('No session ID found')
    return
  }
  
  try {
    // 获取商店列表
    const shopRes = await fetch(buildApiUrl('/api/avatar/shop'))
    const shopData = await shopRes.json()
    if (shopData.success) {
      allAvatars.value = shopData.avatars
    }
    
    // 获取用户头像信息
    const userRes = await fetch(buildApiUrl(`/api/avatar/user/${sessionId}`))
    const userData = await userRes.json()
    if (userData.success) {
      avatarCoins.value = userData.coins || 0
      ownedAvatars.value = userData.owned_avatars || ['default_orange']
      currentAvatar.value = userData.current_avatar || 'default_orange'
      currentAvatarInfo.value = userData.current_avatar_info
      achievementCount.value = userData.achievement_count || 0
      achievementIds.value = userData.achievement_ids || []
    }
  } catch (error) {
    console.error('Load shop data error:', error)
  }
}

onMounted(() => {
  loadShopData()
})
</script>

<style scoped>
.view-container {
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.view-header {
  margin-bottom: 1rem;
}

.view-header h2 {
  color: var(--term-accent);
  font-size: 1.5rem;
  margin: 0;
  font-weight: 900;
}

.header-line {
  height: 2px;
  background: linear-gradient(90deg, var(--term-accent), transparent);
  margin-top: 0.5rem;
}

/* Coins Bar */
.coins-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  border-radius: 8px;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
}

.coins-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.coins-icon {
  font-size: 2rem;
}

.coins-amount {
  font-size: 1.75rem;
  color: #ffd700;
  font-weight: 900;
}

.coins-label {
  color: var(--term-text-secondary);
  font-size: 0.9rem;
}

.current-avatar-display {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.current-label {
  color: var(--term-text-secondary);
  font-size: 0.9rem;
}

.current-avatar-preview {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  border: 3px solid var(--term-accent);
  box-shadow: 0 0 10px var(--term-accent-glow);
}

.current-name {
  color: var(--term-accent);
  font-weight: 700;
  font-size: 1rem;
}

/* Rarity Bar */
.rarity-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.rarity-tab {
  padding: 0.5rem 1rem;
  border: 2px solid var(--term-border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
  font-weight: 700;
  background: var(--term-panel-bg);
  color: var(--term-text);
}

.rarity-tab:hover {
  border-color: var(--term-accent);
}

.rarity-tab.active {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

.rarity-tab .count {
  opacity: 0.7;
  font-weight: 400;
}

/* Avatar Grid */
.avatar-scroll {
  flex: 1;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 1rem;
  padding-bottom: 1rem;
}

.avatar-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.avatar-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
  border-color: var(--term-accent);
}

.avatar-card.owned {
  border-color: var(--term-success);
}

.avatar-card.equipped {
  border-color: #ffd700;
  box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
}

.avatar-card.locked {
  opacity: 0.5;
}

/* Rarity colors */
.avatar-card.common { border-color: var(--term-text-secondary); }
.avatar-card.common:hover { border-color: var(--term-text); }

.avatar-card.rare { border-color: #3b82f6; }
.avatar-card.rare:hover { border-color: #60a5fa; box-shadow: 0 0 15px rgba(59, 130, 246, 0.3); }

.avatar-card.epic { border-color: #a855f7; }
.avatar-card.epic:hover { border-color: #c084fc; box-shadow: 0 0 15px rgba(168, 85, 247, 0.3); }

.avatar-card.legendary { border-color: #ffd700; }
.avatar-card.legendary:hover { box-shadow: 0 0 20px rgba(255, 215, 0, 0.4); }

.avatar-preview {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  border: 3px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.avatar-info {
  text-align: center;
  width: 100%;
}

.avatar-name {
  font-size: 0.9rem;
  color: var(--term-text);
  font-weight: 700;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.avatar-rarity {
  font-size: 0.75rem;
  color: var(--term-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.avatar-footer {
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid var(--term-border);
  width: 100%;
  text-align: center;
}

.price-tag {
  color: #e6a700;
  font-size: 0.9rem;
  font-weight: 700;
}

.owned-tag {
  color: var(--term-success);
  font-size: 0.85rem;
  font-weight: 600;
}

.equipped-tag {
  color: var(--term-accent);
  font-size: 0.85rem;
  font-weight: 700;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-accent);
  border-radius: 16px;
  padding: 2rem;
  max-width: 380px;
  width: 100%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.modal-avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3.5rem;
  margin: 0 auto 1.5rem;
  border: 4px solid var(--term-accent);
  box-shadow: 0 0 30px var(--term-accent-glow);
}

.modal-card h3 {
  color: var(--term-accent);
  margin: 0 0 0.75rem;
  font-size: 1.5rem;
  font-weight: 900;
}

.modal-desc {
  color: var(--term-text);
  font-size: 1rem;
  margin-bottom: 1.25rem;
  line-height: 1.5;
}

.modal-rarity {
  display: inline-block;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.modal-rarity.common { background: var(--term-border); color: var(--term-text-secondary); }
.modal-rarity.rare { background: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid #3b82f6; }
.modal-rarity.epic { background: rgba(168, 85, 247, 0.2); color: #a855f7; border: 1px solid #a855f7; }
.modal-rarity.legendary { background: rgba(255, 215, 0, 0.2); color: #d4a200; border: 1px solid #ffd700; }

.modal-requirement {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--term-bg);
  border: 1px solid var(--term-border);
  border-radius: 8px;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
}

.req-label {
  color: var(--term-text-secondary);
}

.modal-requirement .unlocked {
  color: var(--term-success);
}

.modal-requirement .check {
  margin-left: 0.25rem;
}

.modal-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 215, 0, 0.1);
  border: 2px solid rgba(255, 215, 0, 0.4);
  border-radius: 8px;
  margin: 1.25rem 0;
}

.price-label {
  color: var(--term-text-secondary);
  font-size: 0.95rem;
}

.price-value {
  color: #d4a200;
  font-weight: 900;
  font-size: 1.25rem;
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.term-btn {
  padding: 0.875rem 1.25rem;
  border: 2px solid var(--term-accent);
  background: transparent;
  color: var(--term-accent);
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  font-size: 1rem;
  font-weight: 700;
}

.term-btn:hover:not(:disabled) {
  background: var(--term-accent);
  color: #fff;
}

.term-btn.primary {
  background: var(--term-accent);
  color: #fff;
}

.term-btn.primary:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.term-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 1rem 2rem;
  border-radius: 10px;
  z-index: 2000;
  animation: fadeIn 0.3s;
  font-weight: 700;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.toast.success {
  background: var(--term-success);
  color: #fff;
}

.toast.error {
  background: #ef4444;
  color: #fff;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-50%) translateY(10px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .view-container {
    padding: 1rem;
  }
  
  .coins-bar {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .avatar-grid {
    grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
    gap: 0.75rem;
  }
  
  .avatar-card {
    padding: 0.75rem;
  }
  
  .avatar-preview {
    width: 56px;
    height: 56px;
    font-size: 2rem;
  }
  
  .avatar-name {
    font-size: 0.8rem;
  }
  
  .rarity-bar {
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 0.5rem;
  }
  
  .rarity-tab {
    white-space: nowrap;
    flex-shrink: 0;
  }
  
  .modal-card {
    padding: 1.5rem;
    margin: 0.5rem;
  }
}
</style>
