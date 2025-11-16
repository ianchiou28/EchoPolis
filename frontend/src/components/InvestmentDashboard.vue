<template>
  <div class="investment-dashboard">
    <!-- 总资产卡片 -->
    <div class="total-assets-card glass-panel">
      <div class="card-header">
        <span class="icon">💎</span>
        <h3>总资产</h3>
      </div>
      <div class="asset-amount">
        <span class="currency">¥</span>
        <span class="value" ref="totalAssetsValue">{{ formatNumber(totalAssets) }}</span>
      </div>
      <div class="asset-breakdown">
        <div class="breakdown-item">
          <span class="label">现金</span>
          <span class="value">¥{{ formatNumber(cash) }}</span>
        </div>
        <div class="breakdown-item">
          <span class="label">投资</span>
          <span class="value">¥{{ formatNumber(invested) }}</span>
        </div>
      </div>
    </div>

    <!-- 投资列表 -->
    <div class="investments-list glass-panel">
      <div class="card-header">
        <span class="icon">📊</span>
        <h3>活跃投资</h3>
      </div>
      <div class="investments-scroll">
        <div 
          v-for="investment in activeInvestments" 
          :key="investment.id"
          class="investment-item">
          <div class="investment-info">
            <div class="investment-name">{{ investment.name }}</div>
            <div class="investment-meta">
              <span class="badge" :class="investment.term">{{ termLabel(investment.term) }}</span>
              <span class="duration">剩余 {{ investment.duration }} 月</span>
            </div>
          </div>
          <div class="investment-numbers">
            <div class="amount">¥{{ formatNumber(investment.amount) }}</div>
            <div class="profit" :class="investment.profit > 0 ? 'positive' : 'neutral'">
              +¥{{ formatNumber(investment.profit) }}
            </div>
          </div>
          <div class="investment-progress">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: progressPercent(investment) + '%' }"></div>
            </div>
          </div>
        </div>
        <div v-if="activeInvestments.length === 0" class="empty-state">
          <span class="icon">🌱</span>
          <p>暂无活跃投资</p>
          <small>开始你的财富增值之旅</small>
        </div>
      </div>
    </div>

    <!-- 月度收益 -->
    <div class="monthly-income glass-panel">
      <div class="card-header">
        <span class="icon">💰</span>
        <h3>月度被动收入</h3>
      </div>
      <div class="income-amount positive">
        <span>+¥</span>
        <span ref="monthlyIncomeValue">{{ formatNumber(monthlyIncome) }}</span>
      </div>
      <div class="income-trend">
        <div class="trend-indicator up">
          <span class="arrow">↑</span>
          <span>持续增长</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  totalAssets: {
    type: Number,
    default: 0
  },
  cash: {
    type: Number,
    default: 0
  },
  invested: {
    type: Number,
    default: 0
  },
  investments: {
    type: Array,
    default: () => []
  },
  monthlyIncome: {
    type: Number,
    default: 0
  }
})

const totalAssetsValue = ref(null)
const monthlyIncomeValue = ref(null)

const activeInvestments = computed(() => {
  return props.investments
    .filter(inv => inv.is_active)
    .slice(0, 5) // 只显示前5个
})

const formatNumber = (num) => {
  return Number(num || 0).toLocaleString('zh-CN')
}

const termLabel = (term) => {
  const labels = {
    short: '短期',
    medium: '中期',
    long: '长期'
  }
  return labels[term] || term
}

const progressPercent = (investment) => {
  // 假设初始期限存储在某处,这里简化处理
  const initialDuration = investment.duration + (investment.elapsed || 0)
  return ((initialDuration - investment.duration) / initialDuration) * 100
}

// 数字滚动动画
const animateNumber = (element, target) => {
  if (!element) return
  
  const start = parseFloat(element.textContent.replace(/,/g, '')) || 0
  const duration = 1000
  const startTime = performance.now()
  
  const animate = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    
    const current = start + (target - start) * easeOutQuad(progress)
    element.textContent = formatNumber(Math.round(current))
    
    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }
  
  requestAnimationFrame(animate)
}

const easeOutQuad = (t) => t * (2 - t)

watch(() => props.totalAssets, (newVal) => {
  if (totalAssetsValue.value) {
    animateNumber(totalAssetsValue.value, newVal)
  }
})

watch(() => props.monthlyIncome, (newVal) => {
  if (monthlyIncomeValue.value) {
    animateNumber(monthlyIncomeValue.value, newVal)
  }
})

onMounted(() => {
  if (totalAssetsValue.value) {
    totalAssetsValue.value.textContent = formatNumber(props.totalAssets)
  }
  if (monthlyIncomeValue.value) {
    monthlyIncomeValue.value.textContent = formatNumber(props.monthlyIncome)
  }
})
</script>

<style scoped>
.investment-dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.glass-panel {
  background: rgba(10,14,39,0.75);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 8px 32px rgba(2,6,23,0.6);
  transition: all 0.3s ease;
}

.glass-panel:hover {
  border-color: rgba(59,130,246,0.5);
  box-shadow: 0 12px 40px rgba(59,130,246,0.3);
}

/* 只对不包含滚动内容的面板应用上浮效果 */
.total-assets-card:hover,
.monthly-income:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.card-header .icon {
  font-size: 24px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

/* 总资产卡片 */
.total-assets-card {
  background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(99,102,241,0.2));
}

.asset-amount {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 12px;
}

.asset-amount .currency {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255,255,255,0.7);
}

.asset-amount .value {
  font-size: 32px;
  font-weight: 700;
  color: #ffffff;
  font-family: 'Courier New', monospace;
}

.asset-breakdown {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.breakdown-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  border-radius: 8px;
  background: rgba(15,23,42,0.5);
}

.breakdown-item .label {
  font-size: 12px;
  color: rgba(255,255,255,0.6);
}

.breakdown-item .value {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

/* 投资列表 */
.investments-list {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 防止hover时布局变化 */
}

.investments-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden; /* 防止水平滚动条 */
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 4px; /* 为滚动条留空间 */
}

.investments-scroll::-webkit-scrollbar {
  width: 6px;
}

.investments-scroll::-webkit-scrollbar-track {
  background: rgba(15,23,42,0.5);
  border-radius: 3px;
}

.investments-scroll::-webkit-scrollbar-thumb {
  background: rgba(59,130,246,0.5);
  border-radius: 3px;
  transition: background 0.2s ease;
}

.investments-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(59,130,246,0.8);
}

.investment-item {
  padding: 12px;
  border-radius: 10px;
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(148,163,184,0.2);
  transition: all 0.2s ease;
  will-change: transform; /* 优化动画性能 */
}

.investment-item:hover {
  background: rgba(59,130,246,0.15);
  border-color: rgba(59,130,246,0.5);
  transform: translateX(2px); /* 减小移动距离，防止触发滚动条 */
}

.investment-info {
  margin-bottom: 8px;
}

.investment-name {
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
}

.investment-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 11px;
}

.badge.short {
  background: rgba(34,197,94,0.2);
  color: #22c55e;
}

.badge.medium {
  background: rgba(59,130,246,0.2);
  color: #3b82f6;
}

.badge.long {
  background: rgba(168,85,247,0.2);
  color: #a855f7;
}

.duration {
  color: rgba(255,255,255,0.6);
}

.investment-numbers {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}

.amount {
  font-weight: 600;
  color: var(--text);
}

.profit.positive {
  color: #10b981;
  font-weight: 600;
}

.profit.neutral {
  color: rgba(255,255,255,0.6);
}

.investment-progress {
  margin-top: 8px;
}

.progress-bar {
  height: 4px;
  border-radius: 2px;
  background: rgba(15,23,42,0.8);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  color: rgba(255,255,255,0.5);
}

.empty-state .icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-weight: 600;
}

.empty-state small {
  font-size: 12px;
  opacity: 0.7;
}

/* 月度收益 */
.monthly-income {
  background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(5,150,105,0.2));
}

.income-amount {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  font-family: 'Courier New', monospace;
}

.income-amount.positive {
  color: #10b981;
}

.income-trend {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

.trend-indicator.up {
  background: rgba(16,185,129,0.2);
  color: #10b981;
}

.trend-indicator .arrow {
  font-size: 16px;
}
</style>
