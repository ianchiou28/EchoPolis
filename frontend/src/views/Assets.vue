<template>
  <div class="assets-page">
    <div class="page-header">
      <h1>📊 资产分析</h1>
      <div class="header-actions">
        <button class="refresh-btn btn btn-soft" @click="loadInvestments">🔄 刷新</button>
        <button class="back-btn btn btn-ghost" @click="$router.push('/home')">返回首页</button>
      </div>
    </div>

    <div class="summary-cards">
      <div class="summary-card card glass">
        <div class="card-label">总资产</div>
        <div class="card-value">¥{{ formatNumber(totalAssets) }}</div>
      </div>
      <div class="summary-card card glass">
        <div class="card-label">总收益</div>
        <div class="card-value" :class="totalProfit >= 0 ? 'text-profit' : 'text-loss'">
          {{ totalProfit >= 0 ? '+' : '' }}¥{{ formatNumber(totalProfit) }}
        </div>
      </div>
      <div class="summary-card card glass">
        <div class="card-label">收益率</div>
        <div class="card-value" :class="totalReturn >= 0 ? 'text-profit' : 'text-loss'">
          {{ totalReturn >= 0 ? '+' : '' }}{{ totalReturn.toFixed(2) }}%
        </div>
      </div>
    </div>

    <div class="assets-table table-wrapper">
      <table class="table">
        <thead>
          <tr>
            <th>资产名称</th>
            <th>类型</th>
            <th class="num">买入价格</th>
            <th class="num">当前价值</th>
            <th class="num">收益</th>
            <th class="num">收益率</th>
            <th>期限</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="asset in investments" :key="asset.id">
            <td class="asset-name">{{ asset.name }}</td>
            <td>
              <span class="type-badge badge" :class="asset.term">
                {{ getTermLabel(asset.term) }}
              </span>
            </td>
            <td class="num">¥{{ formatNumber(asset.amount) }}</td>
            <td class="num">¥{{ formatNumber(asset.current_value) }}</td>
            <td class="num" :class="asset.profit >= 0 ? 'text-profit' : 'text-loss'">
              {{ asset.profit >= 0 ? '+' : '' }}¥{{ formatNumber(asset.profit) }}
            </td>
            <td class="num" :class="asset.return_rate >= 0 ? 'text-profit' : 'text-loss'">
              {{ asset.return_rate >= 0 ? '+' : '' }}{{ asset.return_rate.toFixed(2) }}%
            </td>
            <td>{{ asset.duration }}个月</td>
            <td>
              <span class="status-badge badge" :class="asset.status">
                {{ asset.status === 'active' ? '持有中' : '已结束' }}
              </span>
            </td>
          </tr>
          <tr v-if="investments.length === 0">
            <td colspan="8" class="empty">暂无投资资产</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const investments = ref([])

const totalAssets = computed(() => {
  return investments.value.reduce((sum, inv) => sum + inv.current_value, 0)
})

const totalProfit = computed(() => {
  return investments.value.reduce((sum, inv) => sum + inv.profit, 0)
})

const totalReturn = computed(() => {
  const totalInvested = investments.value.reduce((sum, inv) => sum + inv.amount, 0)
  return totalInvested > 0 ? (totalProfit.value / totalInvested) * 100 : 0
})

const formatNumber = (num) => {
  return num?.toLocaleString('zh-CN') || '0'
}

const getTermLabel = (term) => {
  if (term === 'short') return '短期'
  if (term === 'medium') return '中期'
  if (term === 'long') return '长期'
  return term
}

const loadInvestments = async () => {
  try {
    const currentCharacter = localStorage.getItem('currentCharacter')
    if (!currentCharacter) {
      console.log('未选择角色')
      return
    }
    
    const char = JSON.parse(currentCharacter)
    const res = await axios.get('/api/investments', {
      params: { session_id: char.id }
    })
    
    investments.value = res.data.map(inv => ({
      ...inv,
      current_value: inv.amount + (inv.profit || 0),
      profit: inv.profit || 0,
      return_rate: inv.amount > 0 ? ((inv.profit || 0) / inv.amount) * 100 : 0,
      status: inv.is_active ? 'active' : 'completed'
    }))
  } catch (error) {
    console.error('加载投资失败:', error)
  }
}

onMounted(() => {
  loadInvestments()
  // 每30秒自动刷新
  const interval = setInterval(loadInvestments, 30000)
  // 组件销毁时清除定时器
  onUnmounted(() => clearInterval(interval))
})
</script>

<style scoped>
.assets-page {
  width: 100%;
  min-height: 100vh;
  padding: 40px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: var(--text);
  font-size: 32px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.summary-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  flex: 1;
  padding: 25px;
}

.card-label {
  font-size: 14px;
  color: var(--muted);
  margin-bottom: 8px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text);
}

.assets-table {
  border-radius: var(--radius-lg);
}

.table th, .table td { white-space: nowrap; }
.table .num { text-align: right; font-variant-numeric: tabular-nums; }

.asset-name { font-weight: bold; color: var(--text); }

.type-badge.short { background: #dbeafe33; color: #93c5fd; border-color: #60a5fa55; }
.type-badge.medium { background: #fef3c733; color: #fbbf24; border-color: #f59e0b55; }
.type-badge.long { background: #dcfce733; color: #34d399; border-color: #10b98155; }

.status-badge.active { background: #dcfce733; color: #16a34a; border-color: #22c55e55; }
.status-badge.completed { background: #f3f4f633; color: #9ca3af; border-color: #6b728055; }

.empty {
  text-align: center;
  color: var(--muted);
  padding: 40px;
}
</style>
