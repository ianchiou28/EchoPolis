<template>
  <GameLayout>
    <template #top-right>
      <div class="top-controls">
        <div class="macro-ticker" v-if="macroIndicators">
          <span class="ticker-item">
            <span class="label">INFLATION // 通胀</span>
            <span class="value down">{{ macroIndicators.inflation }}%</span>
          </span>
          <span class="ticker-item">
            <span class="label">INTEREST // 利率</span>
            <span class="value">{{ macroIndicators.interest }}%</span>
          </span>
          <span class="ticker-item">
            <span class="label">MARKET // 指数</span>
            <span class="value" :class="macroIndicators.market_trend === 'up' ? 'up' : 'down'">
              {{ macroIndicators.market_idx }} 
              <span class="trend-arrow">{{ macroIndicators.market_trend === 'up' ? '↑' : '↓' }}</span>
            </span>
          </span>
        </div>
        <button class="btn ghost" @click="$router.push('/home')">
          BACK // 返回首页
        </button>
      </div>
    </template>

    <template #left>
      <!-- 总览卡片 -->
      <div class="overview-section">
        <div class="stat-card glass-panel tech-border">
          <div class="stat-header">
            <span class="stat-label">NET WORTH // 净资产</span>
            <span class="stat-icon">💠</span>
          </div>
          <div class="stat-value-lg">¥{{ formatNumber(totalAssets) }}</div>
          <div class="stat-sub">
            <span class="trend positive">▲ 2.4%</span>
            <span class="period">vs last month</span>
          </div>
        </div>
        
        <div class="stat-row">
          <div class="stat-card-small glass-panel">
            <div class="stat-label-sm">LIQUIDITY // 流动资金</div>
            <div class="stat-value-sm">¥{{ formatNumber(cash) }}</div>
          </div>
          <div class="stat-card-small glass-panel">
            <div class="stat-label-sm">INVESTED // 投资总额</div>
            <div class="stat-value-sm">¥{{ formatNumber(invested) }}</div>
          </div>
        </div>
      </div>

      <!-- 投资列表 -->
      <div class="investment-panel glass-panel tech-border">
        <div class="panel-header-small">
          <h3>PORTFOLIO // 投资组合</h3>
          <span class="badge">{{ investments.length }} ITEMS</span>
        </div>
        <div class="list-scroll custom-scrollbar">
          <div v-for="inv in investments" :key="inv.id" class="investment-item">
            <div class="inv-row-top">
              <span class="inv-name">{{ inv.name }}</span>
              <span :class="['inv-return', inv.return_rate >= 0 ? 'positive' : 'negative']">
                {{ inv.return_rate >= 0 ? '+' : '' }}{{ inv.return_rate }}%
              </span>
            </div>
            <div class="inv-row-bottom">
              <span class="inv-amount">¥{{ formatNumber(inv.amount) }}</span>
              <span :class="['inv-type', inv.type]">{{ getTypeLabel(inv.type) }}</span>
            </div>
            <div class="inv-progress-bg">
              <div class="inv-progress-bar" :style="{ width: Math.min(Math.abs(inv.return_rate) * 2, 100) + '%', background: inv.return_rate >= 0 ? '#10b981' : '#ef4444' }"></div>
            </div>
          </div>
          <div v-if="investments.length === 0" class="empty-state">
            NO ACTIVE INVESTMENTS // 暂无投资
          </div>
        </div>
      </div>
    </template>

    <template #center>
      <!-- 资产增长趋势图 -->
      <div class="chart-panel glass-panel tech-border">
        <div class="panel-header-small">
          <h3>WEALTH TREND // 财富增长曲线</h3>
          <div class="chart-legend">
            <span class="legend-dot"></span> NET WORTH
          </div>
        </div>
        <div class="chart-container">
          <v-chart 
            v-if="timelineData.length > 0"
            :option="assetTrendOption" 
            :autoresize="true" 
            class="chart"
          />
          <div v-else class="empty-chart">
            <div class="empty-icon">📊</div>
            <p>AWAITING DATA // 等待数据同步</p>
          </div>
        </div>
      </div>
    </template>

    <template #right>
      <!-- 投资组合饼图 -->
      <div class="chart-panel-small glass-panel tech-border">
        <div class="panel-header-small">
          <h3>ALLOCATION // 资产分布</h3>
        </div>
        <div class="pie-container">
          <v-chart 
            v-if="portfolioData.length > 0"
            :option="portfolioPieOption" 
            :autoresize="true" 
            class="chart-small"
          />
          <div v-else class="empty-chart">
            <div class="empty-icon">🥧</div>
            <p>NO DATA</p>
          </div>
        </div>
      </div>
      
      <!-- 财富等级卡片 -->
      <div class="wealth-level-card glass-panel tech-border">
        <div class="level-header">
          <span class="level-label">WEALTH TIER // 财富等级</span>
          <span class="level-badge">{{ wealthLevel }}</span>
        </div>
        <div class="level-progress">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: wealthProgress + '%' }"></div>
          </div>
          <div class="progress-text">NEXT TIER: ¥{{ formatNumber(nextLevelGap) }} REMAINING</div>
        </div>
      </div>
    </template>
  </GameLayout>

  <!-- 成就弹窗 -->
  <AchievementModal 
    v-if="showAchievement"
    :achievement="currentAchievement"
    @close="showAchievement = false"
  />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import GameLayout from '../components/GameLayout.vue'
import AchievementModal from '../components/AchievementModal.vue'
import { useGameStore } from '../stores/game'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const gameStore = useGameStore()

const timelineData = ref([])
const showAchievement = ref(false)
const currentAchievement = ref(null)

const totalAssets = computed(() => gameStore.assets?.total ?? 0)
const cash = computed(() => gameStore.assets?.cash ?? 0)
const invested = computed(() => gameStore.avatar?.invested_assets ?? 0)
const investments = computed(() => gameStore.assets?.investments || [])
const macroIndicators = computed(() => gameStore.macroIndicators)
const wealthLevel = computed(() => gameStore.wealthLevel)

// 简单的财富等级进度计算
const wealthLevels = [
  { name: '贫困', threshold: 50000 },
  { name: '温饱', threshold: 200000 },
  { name: '小康', threshold: 500000 },
  { name: '富裕', threshold: 1000000 },
  { name: '富豪', threshold: 5000000 },
  { name: '巨富', threshold: Infinity }
]

const nextLevelGap = computed(() => {
  const current = totalAssets.value
  const next = wealthLevels.find(l => l.threshold > current)
  return next ? next.threshold - current : 0
})

const wealthProgress = computed(() => {
  const current = totalAssets.value
  const next = wealthLevels.find(l => l.threshold > current)
  const prev = wealthLevels[[...wealthLevels].reverse().findIndex(l => l.threshold <= current)] || { threshold: 0 }
  
  if (!next) return 100
  const range = next.threshold - (prev ? prev.threshold : 0)
  const progress = current - (prev ? prev.threshold : 0)
  return Math.min(Math.max((progress / range) * 100, 0), 100)
})

const portfolioData = computed(() => {
  const typeMap = {}
  investments.value.forEach(inv => {
    if (inv.is_active) {
      typeMap[inv.type] = (typeMap[inv.type] || 0) + inv.amount
    }
  })
  // 如果有现金，也加入饼图
  if (cash.value > 0) {
    typeMap['cash'] = cash.value
  }
  
  return Object.entries(typeMap).map(([type, amount]) => ({
    name: getTypeLabel(type),
    value: amount
  }))
})

const assetTrendOption = computed(() => {
  if (!timelineData.value || timelineData.value.length === 0) return {}
  
  let data = [...timelineData.value]
  // If only one point, add a starting point for visual continuity
  if (data.length === 1) {
    data.unshift({
      month: 0,
      total_assets: data[0].total_assets,
      current_month: 0
    })
  }

  const months = data.map(t => `M${t.month || t.current_month || 0}`)
  const assetData = data.map(t => t.total_assets || 0)
  
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,23,42,0.9)',
      borderColor: 'rgba(59,130,246,0.3)',
      textStyle: { color: '#e2e8f0' },
      formatter: '{b}<br/>净资产: ¥{c}'
    },
    grid: {
      left: '12%',
      right: '5%',
      bottom: '10%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.2)' } },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: '#64748b', fontSize: 10, formatter: (value) => (value / 10000).toFixed(0) + 'w' },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.1)', type: 'dashed' } }
    },
    series: [{
      type: 'line',
      data: assetData,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#3b82f6', width: 3 },
      itemStyle: { color: '#3b82f6' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(59,130,246,0.3)' },
            { offset: 1, color: 'rgba(59,130,246,0.0)' }
          ]
        }
      }
    }]
  }
})

const portfolioPieOption = computed(() => {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15,23,42,0.9)',
      borderColor: 'rgba(59,130,246,0.3)',
      textStyle: { color: '#e2e8f0' },
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: '0',
      left: 'center',
      itemWidth: 8,
      itemHeight: 8,
      textStyle: { color: '#94a3b8', fontSize: 11 }
    },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#0f172a',
        borderWidth: 3
      },
      label: { show: false },
      emphasis: {
        label: {
          show: true,
          fontSize: 12,
          fontWeight: 'bold',
          color: '#e2e8f0'
        },
        scale: true,
        scaleSize: 5
      },
      data: portfolioData.value,
      color: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#6366f1']
    }]
  }
})

const formatNumber = (num) => Number(num || 0).toLocaleString('zh-CN')

const getTypeLabel = (type) => {
  const labels = {
    stock: '股票',
    fund: '基金',
    real_estate: '房产',
    startup: '创业',
    cash: '现金'
  }
  return labels[type] || type
}

const loadTimeline = async () => {
  try {
    const data = await gameStore.getTimeline(30)
    timelineData.value = data || []
  } catch (error) {
    console.error('加载时间线失败:', error)
  }
}

// 检查成就
const checkAchievements = () => {
  const total = totalAssets.value
  
  if (total >= 100000 && !localStorage.getItem('achievement_100k')) {
    localStorage.setItem('achievement_100k', 'true')
    showAchievement.value = true
    currentAchievement.value = {
      icon: '💰',
      name: '小有资产',
      description: '你的总资产达到了10万元！',
      reward: '+1000 现金',
      rarity: '普通',
      points: 10
    }
  } else if (total >= 500000 && !localStorage.getItem('achievement_500k')) {
    localStorage.setItem('achievement_500k', 'true')
    showAchievement.value = true
    currentAchievement.value = {
      icon: '💎',
      name: '资本家',
      description: '总资产突破50万！你已经是成功人士了！',
      reward: '+5000 现金',
      rarity: '稀有',
      points: 50
    }
  }
}

onMounted(async () => {
  await gameStore.loadAvatar()
  await gameStore.loadMacroIndicators()
  await loadTimeline()
  checkAchievements()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap');

.top-controls {
  display: flex;
  align-items: center;
  gap: 24px;
  font-family: 'Rajdhani', sans-serif;
}

.macro-ticker {
  display: flex;
  gap: 2px;
  padding: 4px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 4px;
  backdrop-filter: blur(4px);
}

.ticker-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: rgba(30, 41, 59, 0.4);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.ticker-item:last-child {
  border-right: none;
}

.ticker-item .label {
  font-size: 10px;
  color: rgba(148, 163, 184, 0.8);
  letter-spacing: 1px;
  font-weight: 600;
}

.ticker-item .value {
  font-size: 14px;
  font-weight: 700;
  color: #e2e8f0;
  font-family: 'Rajdhani', sans-serif;
}

.ticker-item .value.up { color: #10b981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.3); }
.ticker-item .value.down { color: #ef4444; text-shadow: 0 0 10px rgba(239, 68, 68, 0.3); }

.overview-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 12px;
}

.stat-card {
  padding: 20px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
  opacity: 0.5;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.stat-label {
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  color: #94a3b8;
  letter-spacing: 1px;
  font-weight: 600;
}

.stat-value-lg {
  font-family: 'Rajdhani', sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
  margin-bottom: 4px;
}

.stat-sub {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-family: 'Rajdhani', sans-serif;
}

.trend.positive { color: #10b981; }
.period { color: #64748b; }

.stat-row {
  display: flex;
  gap: 12px;
}

.stat-card-small {
  flex: 1;
  padding: 12px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-label-sm {
  font-size: 10px;
  color: #64748b;
  margin-bottom: 4px;
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 0.5px;
}

.stat-value-sm {
  font-size: 16px;
  font-weight: 600;
  color: #e2e8f0;
  font-family: 'Rajdhani', sans-serif;
}

.investment-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 16px;
  background: rgba(15, 23, 42, 0.6);
}

.panel-header-small {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.panel-header-small h3 {
  margin: 0;
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  color: #94a3b8;
  letter-spacing: 1px;
  font-weight: 600;
}

.badge {
  font-size: 10px;
  padding: 2px 6px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border-radius: 2px;
  font-family: 'Rajdhani', sans-serif;
}

.list-scroll {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}

.investment-item {
  position: relative;
  padding: 12px;
  margin-bottom: 8px;
  background: linear-gradient(90deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.4) 100%);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-left: 2px solid transparent;
  transition: all 0.2s ease;
}

.investment-item:hover {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(59, 130, 246, 0.3);
  border-left-color: #3b82f6;
  transform: translateX(2px);
}

.inv-row-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.inv-name {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  font-family: 'Rajdhani', sans-serif;
}

.inv-return {
  font-family: 'Rajdhani', sans-serif;
  font-weight: 700;
  font-size: 13px;
}

.inv-return.positive { color: #10b981; text-shadow: 0 0 5px rgba(16, 185, 129, 0.3); }
.inv-return.negative { color: #ef4444; }

.inv-row-bottom {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #64748b;
  font-family: 'Rajdhani', sans-serif;
}

.inv-type {
  text-transform: uppercase;
  font-size: 9px;
  letter-spacing: 0.5px;
}

.chart-panel {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(15, 23, 42, 0.7);
  position: relative;
}

.chart-container {
  flex: 1;
  width: 100%;
  min-height: 0;
  position: relative;
  background: 
    linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
  background-size: 20px 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.chart {
  width: 100%;
  height: 100%;
}

.chart-panel-small {
  padding: 16px;
  height: 240px;
  display: flex;
  flex-direction: column;
  margin-bottom: 12px;
}

.pie-container {
  flex: 1;
  position: relative;
}

.chart-small {
  width: 100%;
  height: 100%;
}

.wealth-level-card {
  padding: 16px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
}

.level-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.level-label {
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  color: #94a3b8;
  font-weight: 600;
}

.level-badge {
  font-family: 'Rajdhani', sans-serif;
  font-size: 14px;
  font-weight: 700;
  color: #f59e0b;
  text-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
}

.progress-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
}

.progress-text {
  font-family: 'Rajdhani', sans-serif;
  font-size: 10px;
  color: #64748b;
  text-align: right;
  letter-spacing: 0.5px;
}

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

.empty-state, .empty-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(148, 163, 184, 0.4);
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  letter-spacing: 1px;
}
</style>
