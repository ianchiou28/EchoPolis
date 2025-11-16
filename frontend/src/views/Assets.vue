<template>
  <GameLayout>
    <template #top-right>
      <div class="page-header">
        <h1>📊 资产分析</h1>
        <button class="btn ghost" @click="$router.push('/home')">返回首页</button>
      </div>
    </template>

    <template #left>
      <!-- 总览卡片 -->
      <div class="overview-cards">
        <div class="stat-card glass-panel">
          <div class="stat-icon">💰</div>
          <div class="stat-info">
            <div class="stat-label">总资产</div>
            <div class="stat-value">¥{{ formatNumber(totalAssets) }}</div>
          </div>
        </div>
        
        <div class="stat-card glass-panel">
          <div class="stat-icon">💵</div>
          <div class="stat-info">
            <div class="stat-label">流动资金</div>
            <div class="stat-value">¥{{ formatNumber(cash) }}</div>
          </div>
        </div>
        
        <div class="stat-card glass-panel">
          <div class="stat-icon">📈</div>
          <div class="stat-info">
            <div class="stat-label">投资资产</div>
            <div class="stat-value">¥{{ formatNumber(invested) }}</div>
          </div>
        </div>
      </div>

      <!-- 投资列表 -->
      <div class="investment-list glass-panel">
        <h3>💼 投资组合</h3>
        <div class="list-scroll">
          <div v-for="inv in investments" :key="inv.id" class="investment-item">
            <div class="inv-header">
              <span class="inv-name">{{ inv.name }}</span>
              <span :class="['inv-return', inv.return_rate >= 0 ? 'positive' : 'negative']">
                {{ inv.return_rate >= 0 ? '+' : '' }}{{ inv.return_rate }}%
              </span>
            </div>
            <div class="inv-detail">
              <span class="inv-amount">¥{{ formatNumber(inv.amount) }}</span>
              <span :class="['inv-type', inv.type]">{{ getTypeLabel(inv.type) }}</span>
            </div>
          </div>
          <div v-if="investments.length === 0" class="empty-state">
            暂无投资数据
          </div>
        </div>
      </div>
    </template>

    <template #center>
      <!-- 资产增长趋势图 -->
      <div class="chart-panel glass-panel">
        <h3>📈 资产增长趋势</h3>
        <v-chart 
          v-if="timelineData.length > 0"
          :option="assetTrendOption" 
          :autoresize="true" 
          class="chart"
        />
        <div v-else class="empty-chart">暂无时间线数据</div>
      </div>
    </template>

    <template #right>
      <!-- 投资组合饼图 -->
      <div class="chart-panel glass-panel">
        <h3>🥧 投资分布</h3>
        <v-chart 
          v-if="portfolioData.length > 0"
          :option="portfolioPieOption" 
          :autoresize="true" 
          class="chart-small"
        />
        <div v-else class="empty-chart">暂无投资分布</div>
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

const portfolioData = computed(() => {
  const typeMap = {}
  investments.value.forEach(inv => {
    if (inv.is_active) {
      typeMap[inv.type] = (typeMap[inv.type] || 0) + inv.amount
    }
  })
  return Object.entries(typeMap).map(([type, amount]) => ({
    name: getTypeLabel(type),
    value: amount
  }))
})

const assetTrendOption = computed(() => {
  const months = timelineData.value.map(t => `${t.month}月`)
  const assetData = timelineData.value.map(t => t.total_assets)
  
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10,14,39,0.95)',
      borderColor: 'rgba(59,130,246,0.5)',
      textStyle: { color: '#e2e8f0' }
    },
    grid: {
      left: '10%',
      right: '5%',
      bottom: '15%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLine: { lineStyle: { color: 'rgba(59,130,246,0.3)' } },
      axisLabel: { color: '#94a3b8' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: 'rgba(59,130,246,0.3)' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: 'rgba(59,130,246,0.1)' } }
    },
    series: [{
      type: 'line',
      data: assetData,
      smooth: true,
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
            { offset: 1, color: 'rgba(59,130,246,0.05)' }
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
      backgroundColor: 'rgba(10,14,39,0.95)',
      borderColor: 'rgba(59,130,246,0.5)',
      textStyle: { color: '#e2e8f0' }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: '#e2e8f0', fontSize: 12 },
      top: 'center'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#0a0e27',
        borderWidth: 2
      },
      label: { show: false },
      emphasis: {
        label: {
          show: true,
          fontSize: 13,
          fontWeight: 'bold',
          color: '#e2e8f0'
        }
      },
      data: portfolioData.value,
      color: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
    }]
  }
})

const formatNumber = (num) => Number(num || 0).toLocaleString('zh-CN')

const getTypeLabel = (type) => {
  const labels = {
    stock: '股票',
    fund: '基金',
    real_estate: '房产',
    startup: '创业'
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
  await loadTimeline()
  checkAchievements()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
}

.overview-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateX(4px);
}

.stat-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2));
  border-radius: 12px;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 12px;
  color: rgba(148,163,184,0.8);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
}

.investment-list {
  margin: 20px;
  padding: 20px;
  max-height: 400px;
}

.investment-list h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: var(--text);
}

.list-scroll {
  max-height: 320px;
  overflow-y: auto;
}

.investment-item {
  padding: 12px;
  margin-bottom: 8px;
  background: rgba(59,130,246,0.05);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.investment-item:hover {
  background: rgba(59,130,246,0.1);
  border-color: rgba(59,130,246,0.4);
}

.inv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.inv-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.inv-return {
  font-size: 14px;
  font-weight: 700;
}

.inv-return.positive {
  color: #10b981;
}

.inv-return.negative {
  color: #ef4444;
}

.inv-detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.inv-amount {
  color: rgba(148,163,184,0.8);
}

.inv-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.inv-type.stock {
  background: rgba(59,130,246,0.2);
  color: #60a5fa;
}

.inv-type.fund {
  background: rgba(139,92,246,0.2);
  color: #a78bfa;
}

.inv-type.real_estate {
  background: rgba(16,185,129,0.2);
  color: #34d399;
}

.chart-panel {
  margin: 20px;
  padding: 20px;
  height: calc(100vh - 140px);
}

.chart-panel h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: var(--text);
}

.chart {
  width: 100%;
  height: calc(100% - 50px);
}

.chart-small {
  width: 100%;
  height: calc(100% - 50px);
}

.empty-state,
.empty-chart {
  text-align: center;
  color: rgba(148,163,184,0.5);
  padding: 40px 20px;
}
</style>
