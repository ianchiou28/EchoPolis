<template>
  <div class="view-container">
    <div class="view-header">
      <h2>主体数据 // SUBJECT_DATA</h2>
      <div class="header-line"></div>
    </div>

    <div class="content-grid">
      <!-- Left Column: Basic Info -->
      <div class="col-left">
        <div class="archive-card">
          <div class="archive-header">基础档案</div>
          <div class="archive-body">
            <div class="profile-header">
              <div class="avatar-large">
                <div class="face-matrix">
                  <div class="eye left"></div>
                  <div class="eye right"></div>
                  <div class="mouth"></div>
                </div>
              </div>
              <div class="profile-info">
                <div class="name">{{ avatar?.name || 'Unknown' }}</div>
                <div class="mbti-tag">{{ avatar?.mbti_type || 'N/A' }}</div>
                <div class="level">Level {{ Math.floor((avatar?.current_month || 0)/12) + 1 }}</div>
              </div>
            </div>
            
            <div class="stat-bars">
              <div class="stat-row">
                <label>健康 (Health)</label>
                <div class="progress-bar">
                  <div class="fill green" :style="{ width: (avatar?.health || 0) + '%' }"></div>
                </div>
                <span class="val">{{ avatar?.health || 0 }}%</span>
              </div>
              <div class="stat-row">
                <label>幸福 (Happiness)</label>
                <div class="progress-bar">
                  <div class="fill yellow" :style="{ width: (avatar?.happiness || 0) + '%' }"></div>
                </div>
                <span class="val">{{ avatar?.happiness || 0 }}%</span>
              </div>
              <div class="stat-row">
                <label>精力 (Energy)</label>
                <div class="progress-bar">
                  <div class="fill orange" :style="{ width: (avatar?.energy || 0) + '%' }"></div>
                </div>
                <span class="val">{{ avatar?.energy || 0 }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="archive-card flex-grow">
          <div class="archive-header">资产概览</div>
          <div class="archive-body flex-col">
            <div class="asset-big">
              <div class="label">总资产 (Total Assets)</div>
              <div class="value">¥{{ formatNumber(assets.total) }}</div>
            </div>
            
            <!-- Chart Area -->
            <div class="chart-container">
              <v-chart class="chart" :option="chartOption" autoresize />
            </div>

            <div class="asset-row">
              <span>现金流</span>
              <span>¥{{ formatNumber(assets.cash) }}</span>
            </div>
            <div class="asset-row">
              <span>投资总额</span>
              <span>¥{{ formatNumber(assets.invested_assets || 0) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Investments & Traits -->
      <div class="col-right">
        <div class="archive-card full-height">
          <div class="archive-header">投资组合 // PORTFOLIO</div>
          <div class="archive-body scrollable">
            <div v-if="!investments.length" class="empty-state">
              暂无投资记录
            </div>
            <div v-else class="investment-list">
              <div v-for="inv in investments" :key="inv.id" class="inv-item">
                <div class="inv-icon">{{ getInvIcon(inv.type) }}</div>
                <div class="inv-info">
                  <div class="inv-name">{{ inv.name }}</div>
                  <div class="inv-meta">
                    <span class="type">{{ inv.term === 'short' ? '短期' : (inv.term === 'medium' ? '中期' : '长期') }}</span>
                    <span class="duration">剩余 {{ inv.duration }} 个月</span>
                  </div>
                </div>
                <div class="inv-amount">
                  <div>¥{{ formatNumber(inv.amount) }}</div>
                  <div class="profit-hint" v-if="inv.monthly_return > 0">+¥{{ formatNumber(inv.monthly_return * inv.amount) }}/月</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, provide } from 'vue'
import { useGameStore } from '../../stores/game'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent } from 'echarts/components'
import VChart, { THEME_KEY } from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, TitleComponent])

const gameStore = useGameStore()

const avatar = computed(() => gameStore.avatar)
const assets = computed(() => gameStore.assets)
const investments = computed(() => gameStore.assets.investments || [])
const assetHistory = computed(() => gameStore.assetHistory || [])

const formatNumber = (num) => Number(num || 0).toLocaleString('zh-CN')

const getInvIcon = (type) => {
  if (type === 'stock') return '📈'
  if (type === 'bond') return '📜'
  if (type === 'realestate') return '🏢'
  return '💼'
}

// Chart Option
const chartOption = computed(() => {
  const history = assetHistory.value
  const data = history.map(h => h.total)
  const months = history.map(h => `M${h.month}`)
  
  return {
    backgroundColor: 'transparent',
    grid: {
      top: 10,
      right: 10,
      bottom: 20,
      left: 40,
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#000',
      textStyle: { color: '#000', fontFamily: 'JetBrains Mono' },
      formatter: (params) => {
        const val = params[0].value
        return `Month ${params[0].axisValue}<br/>¥${val.toLocaleString()}`
      }
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLine: { lineStyle: { color: '#666' } },
      axisLabel: { color: '#666', fontFamily: 'JetBrains Mono', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { type: 'dashed', color: 'rgba(0,0,0,0.1)' } },
      axisLabel: { 
        color: '#666', 
        fontFamily: 'JetBrains Mono', 
        fontSize: 10,
        formatter: (value) => {
          if (value >= 10000) return (value/10000).toFixed(0) + 'w'
          return value
        }
      }
    },
    series: [{
      data: data,
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#E04F00', width: 2 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(224, 79, 0, 0.2)' },
            { offset: 1, color: 'rgba(224, 79, 0, 0)' }
          ]
        }
      }
    }]
  }
})
</script>

<style scoped>
.view-container {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.view-header h2 {
  font-size: 24px;
  font-weight: 900;
  margin: 0 0 8px 0;
  color: var(--term-text);
}

.header-line {
  height: 2px;
  background: var(--term-border);
  margin-bottom: 24px;
  flex-shrink: 0;
}

.content-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 24px;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.col-left, .col-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow: hidden;
  min-height: 0;
}

.full-height {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.flex-grow {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.flex-col {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.scrollable {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

/* Chart */
.chart-container {
  flex: 1;
  min-height: 150px;
  margin-bottom: 16px;
  border: 1px solid rgba(0,0,0,0.05);
  background: rgba(255,255,255,0.5);
}

.chart {
  height: 100%;
  width: 100%;
}

/* Profile Styles */
.profile-header {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.avatar-large {
  width: 80px;
  height: 80px;
  background: var(--term-accent);
  border: 2px solid #000;
  position: relative;
}

.face-matrix {
  position: relative;
  width: 100%;
  height: 100%;
}

.eye {
  position: absolute;
  top: 30px;
  width: 10px;
  height: 10px;
  background: #000;
}
.eye.left { left: 18px; }
.eye.right { right: 18px; }
.mouth {
  position: absolute;
  bottom: 18px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 4px;
  background: #000;
}

.profile-info .name {
  font-size: 20px;
  font-weight: 900;
  margin-bottom: 4px;
}

.mbti-tag {
  display: inline-block;
  background: #000;
  color: #fff;
  padding: 2px 6px;
  font-weight: bold;
  font-size: 12px;
  margin-bottom: 4px;
}

.level {
  font-size: 12px;
  color: var(--term-text-secondary);
}

/* Stat Bars */
.stat-row {
  margin-bottom: 12px;
}

.stat-row label {
  display: block;
  font-size: 10px;
  margin-bottom: 4px;
  font-weight: 700;
}

.progress-bar {
  height: 8px;
  background: rgba(0,0,0,0.1);
  border: 1px solid var(--term-border);
  margin-bottom: 2px;
}

.fill {
  height: 100%;
  transition: width 0.3s;
}

.fill.green { background: var(--term-success); }
.fill.yellow { background: var(--term-accent-secondary); }
.fill.orange { background: var(--term-accent); }

.val {
  font-size: 10px;
  float: right;
  margin-top: -14px;
}

/* Assets */
.asset-big {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px dashed var(--term-border);
}

.asset-big .label {
  font-size: 12px;
  color: var(--term-text-secondary);
  margin-bottom: 4px;
}

.asset-big .value {
  font-size: 28px;
  font-weight: 900;
  color: var(--term-accent);
}

.asset-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 8px;
  font-weight: 700;
}

/* Investments */
.investment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.inv-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--term-border);
  background: rgba(0,0,0,0.02);
}

.inv-icon {
  font-size: 24px;
}

.inv-info {
  flex: 1;
}

.inv-name {
  font-weight: 800;
  font-size: 14px;
}

.inv-meta {
  font-size: 10px;
  color: var(--term-text-secondary);
  display: flex;
  gap: 8px;
}

.inv-amount {
  text-align: right;
  font-weight: 700;
  font-size: 14px;
}

.profit-hint {
  font-size: 10px;
  color: var(--term-success);
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--term-text-secondary);
  font-style: italic;
}

@media (max-width: 768px) {
  .view-container {
    padding: 16px;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    height: 100%; /* Ensure it fills the parent to allow scrolling */
    display: block;
  }

  .content-grid {
    display: block; /* Stack columns normally */
    height: auto;
    overflow: visible;
    padding-bottom: 40px; /* Extra space at bottom */
  }

  .col-left, .col-right {
    width: 100%;
    height: auto !important;
    display: block;
    overflow: visible;
    margin-bottom: 24px; /* Space between columns */
  }

  .archive-card {
    margin-bottom: 24px; /* Space between cards */
    height: auto !important;
    min-height: 0;
  }

  /* Reset flex-grow card to normal block */
  .flex-grow {
    flex: none !important;
    display: block !important;
  }

  /* Reset flex-col body to normal block */
  .archive-body.flex-col {
    height: auto !important;
    display: block !important;
  }

  /* Chart container */
  .chart-container {
    height: 250px !important;
    width: 100% !important;
    position: relative;
    overflow: hidden;
    margin-bottom: 16px;
    display: block !important;
    background: rgba(255,255,255,0.5); /* Ensure background is visible */
  }
  
  .chart {
    min-height: 250px;
  }

  /* Portfolio section */
  .full-height {
    height: auto !important;
    flex: none !important;
  }

  .archive-body.scrollable {
    height: 400px; /* Fixed height for the list area */
    overflow-y: auto;
  }

  .profile-header {
    flex-direction: row;
    align-items: center;
  }

  .asset-big .value {
    font-size: 24px;
  }
}
</style>
