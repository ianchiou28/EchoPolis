<template>
  <div class="view-container">
    <div class="view-header">
      <h2>排行榜 // LEADERBOARD</h2>
      <div class="header-line"></div>
    </div>

    <div class="content-grid">
      <!-- Tabs -->
      <div class="tab-bar">
        <button v-for="tab in tabs" :key="tab.id"
          :class="['tab-btn', { active: currentTab === tab.id }]"
          @click="currentTab = tab.id; loadLeaderboard()">
          {{ tab.icon }} {{ tab.name }}
        </button>
      </div>

      <!-- My Ranking -->
      <div class="archive-card my-ranking" v-if="myRanking">
        <div class="ranking-label">我的排名</div>
        <div class="ranking-content">
          <div class="rank-number">#{{ myRanking.rank || '---' }}</div>
          <div class="rank-stats">
            <span class="rank-name">{{ myRanking.name || '未知' }}</span>
            <span class="rank-value">{{ formatValue(myRanking.value) }}</span>
          </div>
        </div>
      </div>

      <!-- Leaderboard -->
      <div class="archive-card flex-grow">
        <div class="archive-header">
          <span>{{ currentTabName }} TOP 50</span>
          <button class="refresh-btn" @click="loadLeaderboard">刷新</button>
        </div>
        <div class="archive-body scrollable">
          <div v-if="leaderboard.length === 0" class="empty-state">
            <div class="empty-icon">📊</div>
            <div>暂无排行数据</div>
            <div class="empty-hint">快去交易、投资，登上排行榜吧！</div>
          </div>
          <div v-for="(player, index) in leaderboard" :key="player.session_id || index"
            :class="['rank-row', { 'top-3': index < 3, 'is-me': player.is_me }]">
            <div class="rank-pos">
              <span v-if="index === 0" class="medal gold">🥇</span>
              <span v-else-if="index === 1" class="medal silver">🥈</span>
              <span v-else-if="index === 2" class="medal bronze">🥉</span>
              <span v-else class="rank-num">{{ index + 1 }}</span>
            </div>
            <div class="rank-info">
              <div class="player-name">{{ player.name }}</div>
              <div class="player-detail" v-if="currentTab === 'assets'">
                增长: {{ player.growth_rate?.toFixed(1) || 0 }}%
              </div>
              <div class="player-detail" v-else-if="currentTab === 'achievements'">
                稀有成就: {{ player.rare_count || 0 }}
              </div>
            </div>
            <div class="rank-value">
              {{ formatValue(player.value) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { buildApiUrl } from '../../utils/api'

const currentTab = ref('assets')
const leaderboard = ref([])
const myRanking = ref(null)

const tabs = [
  { id: 'assets', name: '资产榜', icon: '💰' },
  { id: 'growth', name: '增长榜', icon: '📈' },
  { id: 'roi', name: '回报榜', icon: '🎯' },
  { id: 'achievements', name: '成就榜', icon: '🏆' }
]

const currentTabName = computed(() => {
  const tab = tabs.find(t => t.id === currentTab.value)
  return tab ? tab.name : ''
})

const formatValue = (value) => {
  if (currentTab.value === 'growth' || currentTab.value === 'roi') {
    return `${(value || 0).toFixed(2)}%`
  }
  if (currentTab.value === 'achievements') {
    return `${value || 0} 个`
  }
  // Assets
  const num = Number(value) || 0
  if (num >= 100000000) return `¥${(num / 100000000).toFixed(2)}亿`
  if (num >= 10000) return `¥${(num / 10000).toFixed(2)}万`
  return `¥${num.toLocaleString('zh-CN')}`
}

const getSessionId = () => {
  try {
    const char = localStorage.getItem('currentCharacter')
    return char ? JSON.parse(char).id : null
  } catch { return null }
}

const loadLeaderboard = async () => {
  const sessionId = getSessionId()
  
  try {
    // Load leaderboard by type
    const endpoint = `/api/leaderboard/${currentTab.value}`
    const res = await fetch(endpoint)
    const data = await res.json()
    
    if (data.success && data.leaderboard && data.leaderboard.length > 0) {
      leaderboard.value = data.leaderboard.map(p => ({
        ...p,
        value: currentTab.value === 'assets' ? p.total_assets :
               currentTab.value === 'growth' ? p.growth_rate :
               currentTab.value === 'roi' ? p.total_profit :
               p.achievement_count,
        is_me: p.session_id === sessionId
      }))
    } else {
      // 数据库为空时显示提示
      leaderboard.value = []
    }
  } catch (e) {
    console.error('加载排行榜失败:', e)
    leaderboard.value = []
  }
  
  // Load my ranking
  if (sessionId) {
    try {
      const res = await fetch(buildApiUrl(`/api/leaderboard/player/${sessionId}`))
      const data = await res.json()
      if (data.success && data.ranking) {
        myRanking.value = {
          rank: data.ranking[currentTab.value + '_rank'] || null,
          name: data.ranking.name,
          value: currentTab.value === 'assets' ? data.ranking.total_assets :
                 currentTab.value === 'growth' ? data.ranking.growth_rate :
                 currentTab.value === 'roi' ? data.ranking.roi :
                 data.ranking.achievement_count
        }
      } else {
        myRanking.value = null
      }
    } catch (e) {
      myRanking.value = null
    }
  }
}

onMounted(() => {
  loadLeaderboard()
})
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

.content-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

.flex-grow { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.scrollable { flex: 1; overflow-y: auto; }

/* Tab Bar */
.tab-bar {
  display: flex;
  gap: 8px;
}
.tab-btn {
  flex: 1;
  padding: 12px 16px;
  font-weight: 700;
  border: 2px solid var(--term-border);
  background: var(--term-panel-bg);
  color: var(--term-text);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
}
.tab-btn:hover { border-color: var(--term-accent); }
.tab-btn.active {
  background: var(--term-accent);
  color: #000;
  border-color: var(--term-accent);
}

/* My Ranking */
.my-ranking {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(16, 185, 129, 0.1));
  border: 2px solid var(--term-accent);
}
.ranking-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--term-text-secondary);
  text-transform: uppercase;
}
.ranking-content {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}
.rank-number {
  font-size: 32px;
  font-weight: 900;
  color: var(--term-accent);
}
.rank-stats { display: flex; flex-direction: column; }
.rank-name { font-weight: 700; }
.rank-value { font-size: 18px; font-weight: 700; color: var(--term-success); }

/* Archive Card */
.archive-card { background: var(--term-panel-bg); border: 2px solid var(--term-border); }
.archive-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; background: rgba(0,0,0,0.03);
  border-bottom: 1px solid var(--term-border);
  font-weight: 700; font-size: 12px; text-transform: uppercase;
}
.archive-body { padding: 16px; }

.refresh-btn {
  padding: 4px 12px;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid var(--term-border);
  background: transparent;
  color: var(--term-text);
  cursor: pointer;
}
.refresh-btn:hover { background: var(--term-accent); color: #000; }

/* Rank Row */
.rank-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border: 1px solid var(--term-border);
  margin-bottom: 8px;
  transition: all 0.15s;
}
.rank-row:hover { background: rgba(0,0,0,0.03); }
.rank-row.top-3 { border-width: 2px; }
.rank-row.is-me {
  background: rgba(245, 158, 11, 0.1);
  border-color: var(--term-accent);
}

.rank-pos {
  width: 40px;
  text-align: center;
}
.medal { font-size: 24px; }
.rank-num {
  font-size: 16px;
  font-weight: 700;
  color: var(--term-text-secondary);
}

.rank-info { flex: 1; }
.player-name { font-weight: 700; font-size: 14px; }
.player-detail { font-size: 11px; color: var(--term-text-secondary); }

.rank-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--term-success);
}

.empty-state { text-align: center; padding: 60px 20px; color: var(--term-text-secondary); }
.empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
.empty-hint { font-size: 12px; margin-top: 8px; opacity: 0.7; }

@media (max-width: 768px) {
  .tab-bar { flex-wrap: wrap; }
  .tab-btn { flex: 1 1 45%; }
}
</style>
