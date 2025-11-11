<template>
  <div class="assets-page">
    <div class="page-header">
      <h1>📊 资产分析</h1>
      <button class="back-btn" @click="$router.push('/')">返回首页</button>
    </div>

    <div class="summary-cards">
      <div class="summary-card">
        <div class="card-label">总资产</div>
        <div class="card-value">¥{{ formatNumber(totalAssets) }}</div>
      </div>
      <div class="summary-card">
        <div class="card-label">总收益</div>
        <div class="card-value" :class="totalProfit >= 0 ? 'profit' : 'loss'">
          {{ totalProfit >= 0 ? '+' : '' }}¥{{ formatNumber(totalProfit) }}
        </div>
      </div>
      <div class="summary-card">
        <div class="card-label">收益率</div>
        <div class="card-value" :class="totalReturn >= 0 ? 'profit' : 'loss'">
          {{ totalReturn >= 0 ? '+' : '' }}{{ totalReturn.toFixed(2) }}%
        </div>
      </div>
    </div>

    <div class="assets-table">
      <table>
        <thead>
          <tr>
            <th>资产名称</th>
            <th>类型</th>
            <th>买入价格</th>
            <th>当前价值</th>
            <th>收益</th>
            <th>收益率</th>
            <th>期限</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="asset in investments" :key="asset.id">
            <td class="asset-name">{{ asset.name }}</td>
            <td>
              <span class="type-badge" :class="asset.term">
                {{ getTermLabel(asset.term) }}
              </span>
            </td>
            <td>¥{{ formatNumber(asset.amount) }}</td>
            <td>¥{{ formatNumber(asset.current_value) }}</td>
            <td :class="asset.profit >= 0 ? 'profit' : 'loss'">
              {{ asset.profit >= 0 ? '+' : '' }}¥{{ formatNumber(asset.profit) }}
            </td>
            <td :class="asset.return_rate >= 0 ? 'profit' : 'loss'">
              {{ asset.return_rate >= 0 ? '+' : '' }}{{ asset.return_rate.toFixed(2) }}%
            </td>
            <td>{{ asset.duration }}个月</td>
            <td>
              <span class="status-badge" :class="asset.status">
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
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from '../stores/game'
import axios from 'axios'

const gameStore = useGameStore()
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
    const res = await axios.get('/api/investments')
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
  color: white;
  font-size: 32px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.back-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  background: rgba(255,255,255,0.9);
  color: #ff9a9e;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: white;
  transform: translateY(-2px);
}

.summary-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  flex: 1;
  background: rgba(255,255,255,0.95);
  padding: 25px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.card-value.profit {
  color: #10b981;
}

.card-value.loss {
  color: #ef4444;
}

.assets-table {
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8f9fa;
}

th {
  padding: 15px;
  text-align: left;
  font-weight: bold;
  color: #333;
  border-bottom: 2px solid #e5e7eb;
}

td {
  padding: 15px;
  border-bottom: 1px solid #e5e7eb;
  color: #666;
}

.asset-name {
  font-weight: bold;
  color: #333;
}

.type-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.type-badge.short {
  background: #dbeafe;
  color: #1e40af;
}

.type-badge.medium {
  background: #fef3c7;
  color: #92400e;
}

.type-badge.long {
  background: #dcfce7;
  color: #166534;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.active {
  background: #dcfce7;
  color: #166534;
}

.status-badge.completed {
  background: #f3f4f6;
  color: #6b7280;
}

.profit {
  color: #10b981;
  font-weight: bold;
}

.loss {
  color: #ef4444;
  font-weight: bold;
}

.empty {
  text-align: center;
  color: #999;
  padding: 40px;
}
</style>
