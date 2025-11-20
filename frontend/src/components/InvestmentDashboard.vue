<template>
  <div class="investment-dashboard">
    <!-- 宏观经济指标 (模拟数据，待接入后端 CentralBank) -->
    <div class="macro-indicators glass-panel tech-border-sm">
      <div class="indicator">
        <span class="label">INFLATION // 通胀率</span>
        <span class="value warning">{{ macroIndicators.inflation }}%</span>
      </div>
      <div class="indicator">
        <span class="label">INTEREST // 利率</span>
        <span class="value">{{ macroIndicators.interest }}%</span>
      </div>
      <div class="indicator">
        <span class="label">MARKET IDX // 市场指数</span>
        <span class="value" :class="macroIndicators.market_trend === 'up' ? 'positive' : (macroIndicators.market_trend === 'down' ? 'negative' : '')">
          {{ formatNumber(macroIndicators.market_idx) }} {{ macroIndicators.market_trend === 'up' ? '▲' : (macroIndicators.market_trend === 'down' ? '▼' : '-') }}
        </span>
      </div>
    </div>

    <!-- 总资产卡片 -->
    <div class="total-assets-card glass-panel tech-border">
      <div class="card-decoration top-right"></div>
      <div class="card-header">
        <span class="icon">💠</span>
        <h3>ASSET MONITOR // 资产监控</h3>
      </div>
      
      <div class="main-asset-display">
        <span class="currency">¥</span>
        <span class="value" ref="totalAssetsValue">{{ formatNumber(totalAssets) }}</span>
      </div>

      <div class="asset-composition">
        <div class="comp-row">
          <div class="comp-info">
            <span class="comp-label">CASH LIQUIDITY // 现金流</span>
            <span class="comp-val">¥{{ formatNumber(cash) }}</span>
          </div>
          <div class="comp-bar-bg">
            <div class="comp-bar-fill cash" :style="{ width: cashRatio + '%' }"></div>
          </div>
        </div>
        <div class="comp-row">
          <div class="comp-info">
            <span class="comp-label">INVESTMENTS // 投资额</span>
            <span class="comp-val">¥{{ formatNumber(invested) }}</span>
          </div>
          <div class="comp-bar-bg">
            <div class="comp-bar-fill invested" :style="{ width: investedRatio + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 投资列表 -->
    <div class="investments-list glass-panel tech-border">
      <div class="card-header">
        <span class="icon">📊</span>
        <h3>ACTIVE POSITIONS // 持仓</h3>
      </div>
      <div class="investments-scroll">
        <div 
          v-for="investment in activeInvestments" 
          :key="investment.id"
          class="investment-item">
          <div class="item-header">
            <span class="item-name">{{ investment.name }}</span>
            <span class="item-term">{{ termLabel(investment.term) }}</span>
          </div>
          
          <div class="item-grid">
            <div class="grid-cell">
              <span class="cell-label">PRINCIPAL // 本金</span>
              <span class="cell-val">¥{{ formatNumber(investment.amount) }}</span>
            </div>
            <div class="grid-cell">
              <span class="cell-label">P/L // 盈亏</span>
              <span class="cell-val" :class="investment.profit > 0 ? 'positive' : 'neutral'">
                {{ investment.profit > 0 ? '+' : '' }}¥{{ formatNumber(investment.profit) }}
              </span>
            </div>
          </div>

          <div class="progress-section">
            <div class="progress-label">
              <span>MATURITY // 到期</span>
              <span>{{ investment.duration }} MO REMAINING</span>
            </div>
            <div class="tech-progress-bar">
              <div 
                class="tech-progress-fill" 
                :style="{ width: progressPercent(investment) + '%' }"></div>
            </div>
          </div>
        </div>
        
        <div v-if="activeInvestments.length === 0" class="empty-state">
          <div class="empty-icon">∅</div>
          <p>NO ACTIVE POSITIONS</p>
          <small>AWAITING INVESTMENT PROTOCOLS</small>
        </div>
      </div>
    </div>

    <!-- 月度收益 -->
    <div class="monthly-income glass-panel tech-border-sm">
      <div class="income-content">
        <div class="income-label">
          <span class="icon">⚡</span>
          <h3>PASSIVE INCOME // 被动收入</h3>
        </div>
        <div class="income-value positive">
          <span>+¥</span>
          <span ref="monthlyIncomeValue">{{ formatNumber(monthlyIncome) }}</span>
          <span class="unit">/MO</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  totalAssets: { type: Number, default: 0 },
  cash: { type: Number, default: 0 },
  invested: { type: Number, default: 0 },
  investments: { type: Array, default: () => [] },
  monthlyIncome: { type: Number, default: 0 },
  macroIndicators: { 
    type: Object, 
    default: () => ({
      inflation: 2.4,
      interest: 4.5,
      market_idx: 12450,
      market_trend: 'up'
    }) 
  }
})

const totalAssetsValue = ref(null)
const monthlyIncomeValue = ref(null)

const activeInvestments = computed(() => {
  return props.investments
    .filter(inv => inv.is_active)
    .slice(0, 5)
})

const cashRatio = computed(() => {
  if (props.totalAssets === 0) return 0
  return Math.min(100, (props.cash / props.totalAssets) * 100)
})

const investedRatio = computed(() => {
  if (props.totalAssets === 0) return 0
  return Math.min(100, (props.invested / props.totalAssets) * 100)
})

const formatNumber = (num) => Number(num || 0).toLocaleString('zh-CN')

const termLabel = (term) => {
  const labels = { short: 'SHORT', medium: 'MID', long: 'LONG' }
  return labels[term] || term.toUpperCase()
}

const progressPercent = (investment) => {
  // Mock progress for visual demo
  return 45 
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
    if (progress < 1) requestAnimationFrame(animate)
  }
  requestAnimationFrame(animate)
}

const easeOutQuad = (t) => t * (2 - t)

watch(() => props.totalAssets, (newVal) => {
  if (totalAssetsValue.value) animateNumber(totalAssetsValue.value, newVal)
})

watch(() => props.monthlyIncome, (newVal) => {
  if (monthlyIncomeValue.value) animateNumber(monthlyIncomeValue.value, newVal)
})

onMounted(() => {
  if (totalAssetsValue.value) totalAssetsValue.value.textContent = formatNumber(props.totalAssets)
  if (monthlyIncomeValue.value) monthlyIncomeValue.value.textContent = formatNumber(props.monthlyIncome)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');

.investment-dashboard {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  font-family: 'Rajdhani', sans-serif;
  color: #e2e8f0;
}

/* 通用面板样式 - 高级感升级 */
.glass-panel {
  background: rgba(5, 8, 16, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 
    0 20px 50px rgba(0, 0, 0, 0.5),
    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
  position: relative;
  transition: all 0.3s ease;
  padding: 16px;
}

.glass-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    800px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), 
    rgba(255, 255, 255, 0.03),
    transparent 40%
  );
  pointer-events: none;
  z-index: 0;
}

.tech-border {
  clip-path: polygon(
    0 0, 100% 0, 
    100% calc(100% - 10px), calc(100% - 10px) 100%, 
    0 100%
  );
  border-bottom: 2px solid rgba(59, 130, 246, 0.3);
}

.tech-border-sm {
  border-left: 2px solid rgba(59, 130, 246, 0.5);
}

.card-decoration {
  position: absolute;
  width: 15px;
  height: 15px;
  border: 2px solid rgba(59, 130, 246, 0.5);
  pointer-events: none;
}

.card-decoration.top-right { top: 0; right: 0; border-left: none; border-bottom: none; }

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 8px;
}

.card-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 2px;
  background: linear-gradient(to right, #fff, #94a3b8);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* 宏观指标 */
.macro-indicators {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
}

.indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.indicator .label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 1px;
}

.indicator .value {
  font-size: 16px;
  font-weight: 700;
  font-family: 'Rajdhani', monospace;
  letter-spacing: 1px;
}

.value.warning { color: #f59e0b; }
.value.positive { color: #10b981; }
.value.negative { color: #f87171; }

/* 总资产 */
.main-asset-display {
  margin-bottom: 16px;
}

.main-asset-display .currency {
  font-size: 20px;
  color: rgba(59, 130, 246, 0.8);
  margin-right: 4px;
}

.main-asset-display .value {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.asset-composition {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comp-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.comp-info {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.comp-val {
  font-family: 'Rajdhani', monospace;
  letter-spacing: 0.5px;
  color: #fff;
}

.comp-bar-bg {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  width: 100%;
}

.comp-bar-fill {
  height: 100%;
  box-shadow: 0 0 8px currentColor;
}

.comp-bar-fill.cash { background: #3b82f6; width: 0; transition: width 1s ease; }
.comp-bar-fill.invested { background: #8b5cf6; width: 0; transition: width 1s ease; }

/* 投资列表 */
.investments-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.investments-scroll {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.investment-item {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 12px;
  transition: all 0.2s;
}

.investment-item:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.item-name {
  font-weight: 600;
  font-size: 13px;
  color: #e2e8f0;
}

.item-term {
  font-size: 10px;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 2px;
}

.item-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 8px;
}

.grid-cell {
  display: flex;
  flex-direction: column;
}

.cell-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
}

.cell-val {
  font-family: 'Rajdhani', monospace;
  letter-spacing: 0.5px;
  font-size: 12px;
}

.cell-val.positive { color: #10b981; }
.cell-val.neutral { color: #94a3b8; }

.progress-section {
  margin-top: 4px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 2px;
}

.tech-progress-bar {
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
}

.tech-progress-fill {
  height: 100%;
  background: #3b82f6;
  box-shadow: 0 0 5px #3b82f6;
}

.empty-state {
  text-align: center;
  padding: 30px 0;
  color: rgba(255, 255, 255, 0.3);
}

.empty-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

/* 月度收益 */
.monthly-income {
  display: flex;
  align-items: center;
}

.income-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.income-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.income-label h3 {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

.income-value {
  font-family: 'Rajdhani', monospace;
  letter-spacing: 0.5px;
  font-size: 18px;
  font-weight: 700;
}

.income-value.positive { color: #10b981; }

.unit {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  margin-left: 2px;
}

/* 滚动条 */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.3); }
</style>
