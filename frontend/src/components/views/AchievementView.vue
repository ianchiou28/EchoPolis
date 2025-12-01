<template>
  <div class="view-container">
    <div class="view-header">
      <h2>成就系统 // ACHIEVEMENTS</h2>
      <div class="header-line"></div>
    </div>

    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-box">
        <div class="stat-icon">🏆</div>
        <div class="stat-info">
          <div class="stat-val">{{ stats.unlocked }}</div>
          <div class="stat-label">已解锁</div>
        </div>
      </div>
      <div class="stat-box">
        <div class="stat-icon">💰</div>
        <div class="stat-info">
          <div class="stat-val">{{ formatNumber(stats.totalCoins) }}</div>
          <div class="stat-label">金币奖励</div>
        </div>
      </div>
      <div class="stat-box">
        <div class="stat-icon">⭐</div>
        <div class="stat-info">
          <div class="stat-val">{{ formatNumber(stats.totalExp) }}</div>
          <div class="stat-label">经验值</div>
        </div>
      </div>
      <div class="stat-box progress-box">
        <div class="progress-ring">
          <svg viewBox="0 0 36 36">
            <path class="ring-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
            <path class="ring-fill" :stroke-dasharray="`${completionRate}, 100`" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
          </svg>
          <span class="ring-text">{{ completionRate }}%</span>
        </div>
      </div>
    </div>

    <!-- Category Filter -->
    <div class="category-bar">
      <span v-for="cat in categories" :key="cat.id"
        :class="['cat-tab', { active: currentCat === cat.id }]"
        @click="currentCat = cat.id">
        {{ cat.icon }} {{ cat.name }}
      </span>
    </div>

    <!-- Achievements Grid -->
    <div class="achievements-scroll">
      <div class="achievements-grid">
        <div v-for="ach in filteredAchievements" :key="ach.id"
          :class="['ach-card', ach.rarity, { unlocked: ach.unlocked, locked: !ach.unlocked }]"
          @click="showDetail(ach)">
          <div class="ach-icon">{{ ach.unlocked ? ach.icon : '🔒' }}</div>
          <div class="ach-content">
            <div class="ach-name">{{ ach.unlocked ? ach.name : '???' }}</div>
            <div class="ach-desc">{{ ach.unlocked ? ach.description : '未解锁' }}</div>
          </div>
          <div class="ach-footer">
            <span class="rarity-tag">{{ ach.rarity }}</span>
            <span v-if="ach.unlocked" class="unlock-time">M{{ ach.unlocked_month }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="selectedAch" class="modal-overlay" @click="selectedAch = null">
      <div class="modal-card" @click.stop>
        <div class="modal-icon">{{ selectedAch.icon }}</div>
        <h3>{{ selectedAch.name }}</h3>
        <p class="modal-desc">{{ selectedAch.description }}</p>
        <div class="modal-condition">
          <span class="cond-label">解锁条件</span>
          <span>{{ selectedAch.condition }}</span>
        </div>
        <div v-if="selectedAch.unlocked" class="modal-rewards">
          <span v-if="selectedAch.reward_coins">💰 +{{ selectedAch.reward_coins }}</span>
          <span v-if="selectedAch.reward_exp">⭐ +{{ selectedAch.reward_exp }}</span>
        </div>
        <button class="term-btn" @click="selectedAch = null">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from '../../stores/game'

const gameStore = useGameStore()

const achievements = ref([])
const selectedAch = ref(null)
const currentCat = ref('all')

const stats = ref({ unlocked: 0, total: 40, totalCoins: 0, totalExp: 0 })

const categories = [
  { id: 'all', name: '全部', icon: '🎯' },
  { id: '财富里程碑', name: '财富', icon: '💰' },
  { id: '投资成就', name: '投资', icon: '📈' },
  { id: '储蓄成就', name: '储蓄', icon: '🏦' },
  { id: '特殊成就', name: '特殊', icon: '🌟' }
]

const completionRate = computed(() => {
  if (stats.value.total === 0) return 0
  return Math.round((stats.value.unlocked / stats.value.total) * 100)
})

const filteredAchievements = computed(() => {
  let list = achievements.value
  if (currentCat.value !== 'all') {
    list = list.filter(a => a.category === currentCat.value)
  }
  return list.sort((a, b) => (b.unlocked ? 1 : 0) - (a.unlocked ? 1 : 0))
})

const formatNumber = (n) => Number(n || 0).toLocaleString('zh-CN')
const showDetail = (ach) => { if (ach.unlocked || !ach.hidden) selectedAch.value = ach }

const loadAchievements = async () => {
  try {
    const allRes = await fetch('/api/achievements/all')
    const allData = await allRes.json()
    const unlockedRes = await fetch(`/api/achievements/unlocked?avatar_id=${gameStore.avatar?.id}`)
    const unlockedData = await unlockedRes.json()

    if (allData.success) {
      const unlockedSet = new Set(unlockedData.achievements?.map(a => a.achievement_id) || [])
      achievements.value = allData.achievements.map(a => ({
        ...a,
        unlocked: unlockedSet.has(a.id),
        unlocked_month: unlockedData.achievements?.find(u => u.achievement_id === a.id)?.unlocked_month
      }))
      stats.value = {
        unlocked: unlockedData.stats?.unlocked_count || 0,
        total: allData.achievements.length,
        totalCoins: unlockedData.stats?.total_coins || 0,
        totalExp: unlockedData.stats?.total_exp || 0
      }
    }
  } catch (e) {
    achievements.value = [
      { id: 'W10K', name: '小有积蓄', description: '总资产达到1万元', icon: '💰', rarity: '普通', category: '财富里程碑', condition: '总资产 ≥ ¥10,000', unlocked: true, unlocked_month: 2, reward_coins: 100, reward_exp: 50 },
      { id: 'W100K', name: '十万俱乐部', description: '总资产达到10万元', icon: '💎', rarity: '稀有', category: '财富里程碑', condition: '总资产 ≥ ¥100,000', unlocked: false, reward_coins: 500, reward_exp: 200 },
      { id: 'FIRST_STOCK', name: '初入股市', description: '第一次购买股票', icon: '📈', rarity: '普通', category: '投资成就', condition: '购买第一只股票', unlocked: true, unlocked_month: 3, reward_coins: 50, reward_exp: 30 },
      { id: 'DIVERSIFY', name: '分散投资', description: '持有5种不同资产', icon: '🎨', rarity: '稀有', category: '投资成就', condition: '持有5种以上资产', unlocked: false, reward_coins: 500, reward_exp: 200 },
      { id: 'SAVER', name: '储蓄达人', description: '存款超过5万', icon: '🏦', rarity: '普通', category: '储蓄成就', condition: '存款 ≥ ¥50,000', unlocked: false, reward_coins: 200, reward_exp: 100 },
      { id: 'COMEBACK', name: '绝地反击', description: '从负债恢复正资产', icon: '🔥', rarity: '传说', category: '特殊成就', condition: '从负资产恢复', unlocked: false, reward_coins: 3000, reward_exp: 1500, hidden: true }
    ]
    stats.value = { unlocked: 2, total: 6, totalCoins: 150, totalExp: 80 }
  }
}

onMounted(() => loadAchievements())
</script>

<style scoped>
.view-container {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.view-header h2 { font-size: 24px; font-weight: 900; margin: 0 0 8px 0; }
.header-line { height: 2px; background: var(--term-border); margin-bottom: 24px; }

/* Stats Bar */
.stats-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  border: 2px solid var(--term-border);
  background: var(--term-panel-bg);
}

.stat-box { display: flex; align-items: center; gap: 12px; }
.stat-icon { font-size: 24px; }
.stat-val { font-size: 20px; font-weight: 900; }
.stat-label { font-size: 10px; color: var(--term-text-secondary); }

.progress-box { margin-left: auto; }
.progress-ring { position: relative; width: 50px; height: 50px; }
.progress-ring svg { transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: var(--term-border); stroke-width: 3; }
.ring-fill { fill: none; stroke: var(--term-accent); stroke-width: 3; stroke-linecap: round; }
.ring-text { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; }

/* Category Bar */
.category-bar { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
.cat-tab {
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid var(--term-border);
  cursor: pointer;
  transition: all 0.15s;
}
.cat-tab:hover { border-color: var(--term-accent); }
.cat-tab.active { background: var(--term-accent); color: #000; border-color: var(--term-accent); }

/* Achievements Grid */
.achievements-scroll { flex: 1; overflow-y: auto; }
.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.ach-card {
  padding: 16px;
  border: 2px solid var(--term-border);
  cursor: pointer;
  transition: all 0.2s;
  background: var(--term-panel-bg);
}
.ach-card:hover { transform: translateY(-2px); box-shadow: 4px 4px 0 rgba(0,0,0,0.1); }
.ach-card.locked { opacity: 0.5; }
.ach-card.unlocked { border-color: var(--term-accent); }

.ach-icon { font-size: 32px; margin-bottom: 8px; }
.ach-name { font-weight: 800; font-size: 14px; margin-bottom: 4px; }
.ach-desc { font-size: 11px; color: var(--term-text-secondary); line-height: 1.4; }
.ach-footer { display: flex; justify-content: space-between; margin-top: 12px; font-size: 10px; }

.rarity-tag { padding: 2px 6px; border: 1px solid var(--term-border); }
.ach-card.普通 .rarity-tag { color: var(--term-text-secondary); }
.ach-card.稀有 .rarity-tag { background: #3b82f6; color: #fff; border-color: #3b82f6; }
.ach-card.史诗 .rarity-tag { background: #8b5cf6; color: #fff; border-color: #8b5cf6; }
.ach-card.传说 .rarity-tag { background: #f59e0b; color: #000; border-color: #f59e0b; }

.unlock-time { color: var(--term-text-secondary); }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  padding: 32px;
  max-width: 400px;
  text-align: center;
}

.modal-icon { font-size: 48px; margin-bottom: 16px; }
.modal-card h3 { margin: 0 0 8px 0; font-size: 20px; }
.modal-desc { color: var(--term-text-secondary); margin-bottom: 20px; }
.modal-condition { padding: 12px; background: rgba(0,0,0,0.05); margin-bottom: 16px; font-size: 12px; }
.cond-label { display: block; font-size: 10px; color: var(--term-text-secondary); margin-bottom: 4px; }
.modal-rewards { display: flex; justify-content: center; gap: 16px; margin-bottom: 20px; font-size: 14px; color: var(--term-success); }

@media (max-width: 768px) {
  .stats-bar { flex-wrap: wrap; }
  .achievements-grid { grid-template-columns: 1fr; }
  .view-container { overflow-y: auto; }
}
</style>
