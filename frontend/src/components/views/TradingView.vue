<template>
  <div class="view-container">
    <div class="view-header">
      <h2>股票交易 // STOCK_TRADING</h2>
      <div class="header-line"></div>
    </div>

    <div class="content-grid">
      <!-- Left: Market Overview & Stock List -->
      <div class="col-left">
        <div class="archive-card">
          <div class="archive-header">市场指数</div>
          <div class="archive-body">
            <div class="index-display">
              <div class="index-value" :class="marketTrend">
                {{ marketIndex.toFixed(2) }}
              </div>
              <div class="index-change" :class="marketTrend">
                {{ marketTrend === 'up' ? '▲' : '▼' }} {{ Math.abs(marketChange).toFixed(2) }}%
              </div>
            </div>
            <div class="mood-row">
              <span class="label">市场情绪</span>
              <span class="mood-tag" :class="marketMood">{{ moodLabel }}</span>
            </div>
          </div>
        </div>

        <!-- Stock List -->
        <div class="archive-card flex-grow">
          <div class="archive-header">
            <span>股票列表</span>
            <div class="filter-tabs">
              <span v-for="s in sectors" :key="s.id" 
                :class="['tab', { active: currentSector === s.id }]"
                @click="currentSector = s.id">{{ s.name }}</span>
            </div>
          </div>
          <div class="archive-body scrollable">
            <div v-for="stock in filteredStocks" :key="stock.id"
              :class="['stock-row', { selected: selectedStock?.id === stock.id }]"
              @click="selectStock(stock)">
              <div class="stock-info">
                <div class="stock-name">{{ stock.name }}</div>
                <div class="stock-code">{{ stock.id }}</div>
              </div>
              <div class="stock-price">
                <div class="price">¥{{ stock.price.toFixed(2) }}</div>
                <div class="change" :class="stock.change >= 0 ? 'up' : 'down'">
                  {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Collapsible Trade Panel & Holdings -->
      <div class="col-right accordion-column">
        <!-- 交易面板 (含K线图) -->
        <div 
          class="accordion-card" 
          :class="{ expanded: rightPanel === 'trade', collapsed: rightPanel && rightPanel !== 'trade' }"
          @click="rightPanel !== 'trade' && (rightPanel = 'trade')"
        >
          <div class="accordion-header">
            <span class="accordion-icon">📈</span>
            <span class="accordion-title">交易面板</span>
            <span class="accordion-arrow">{{ rightPanel === 'trade' ? '▼' : '▶' }}</span>
          </div>
          <div class="accordion-body" v-show="rightPanel === 'trade'">
            <template v-if="selectedStock">
              <!-- K线图区域 -->
              <div class="kline-section">
                <div class="kline-header">
                  <span class="kline-title">{{ selectedStock.name }} K线图</span>
                  <div class="filter-tabs" @click.stop>
                    <span v-for="p in klinePeriods" :key="p.id"
                      :class="['tab', { active: currentPeriod === p.id }]"
                      @click="currentPeriod = p.id; loadKlineData()">{{ p.name }}</span>
                  </div>
                </div>
                <div class="chart-container" v-if="klineData.length > 0">
                  <v-chart :option="klineOption" autoresize class="chart" :key="selectedStock.id + currentPeriod" />
                </div>
                <div class="chart-loading" v-else>加载中...</div>
              </div>

              <!-- 交易信息区域 -->
              <div class="trade-section">
                <div class="selected-info">
                  <h3>{{ selectedStock.name }}</h3>
                  <div class="price-big">¥{{ selectedStock.price.toFixed(2) }}</div>
                  <div class="change-tag" :class="selectedStock.change >= 0 ? 'up' : 'down'">
                    {{ selectedStock.change >= 0 ? '▲' : '▼' }}
                    {{ Math.abs(selectedStock.change).toFixed(2) }}%
                  </div>
                </div>

                <!-- Technical Indicators -->
                <div class="tech-indicators" v-if="technicalData">
                  <div class="indicator">
                    <span class="ind-label">MA5</span>
                    <span class="ind-value">{{ technicalData.ma5?.toFixed(2) || '-' }}</span>
                  </div>
                  <div class="indicator">
                    <span class="ind-label">MA20</span>
                    <span class="ind-value">{{ technicalData.ma20?.toFixed(2) || '-' }}</span>
                  </div>
                  <div class="indicator">
                    <span class="ind-label">趋势</span>
                    <span class="ind-value" :class="technicalData.trend">{{ trendLabel }}</span>
                  </div>
                </div>

                <div class="form-row">
                  <label>交易数量</label>
                  <div class="qty-input" @click.stop>
                    <button class="qty-btn" @click="tradeQty = Math.max(100, tradeQty - 100)">-</button>
                    <input type="number" v-model.number="tradeQty" min="100" step="100" />
                    <button class="qty-btn" @click="tradeQty += 100">+</button>
                  </div>
                </div>

                <div class="form-row">
                  <label>交易金额</label>
                  <span class="amount-val">¥{{ formatNumber(tradeAmount) }}</span>
                </div>

                <div class="trade-actions" @click.stop>
                  <button class="term-btn buy" @click="executeTrade('buy')" :disabled="!canBuy">
                    买入 BUY
                  </button>
                  <button class="term-btn sell" @click="executeTrade('sell')" :disabled="!canSell">
                    卖出 SELL
                  </button>
                </div>
              </div>
            </template>
            <div v-else class="empty-state">← 选择股票开始交易</div>
          </div>
        </div>

        <!-- 我的持仓 -->
        <div 
          class="accordion-card" 
          :class="{ expanded: rightPanel === 'holdings', collapsed: rightPanel && rightPanel !== 'holdings' }"
          @click="rightPanel !== 'holdings' && (rightPanel = 'holdings')"
        >
          <div class="accordion-header">
            <span class="accordion-icon">💼</span>
            <span class="accordion-title">我的持仓</span>
            <span class="accordion-arrow">{{ rightPanel === 'holdings' ? '▼' : '▶' }}</span>
          </div>
          <div class="accordion-body" v-show="rightPanel === 'holdings'">
            <div v-if="holdings.length === 0" class="empty-state">暂无持仓</div>
            <div v-for="h in holdings" :key="h.stock_id" class="holding-row">
              <div class="holding-info">
                <div class="holding-name">{{ h.stock_name }}</div>
                <div class="holding-shares">{{ h.shares }} 股</div>
              </div>
              <div class="holding-value">
                <div class="market-val">¥{{ formatNumber(h.market_value) }}</div>
                <div class="profit" :class="h.profit >= 0 ? 'up' : 'down'">
                  {{ h.profit >= 0 ? '+' : '' }}{{ formatNumber(h.profit) }}
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
import { ref, computed, onMounted, watch } from 'vue'
import { useGameStore } from '../../stores/game'
import { buildApiUrl } from '../../utils/api'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { CandlestickChart, LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'

use([CanvasRenderer, CandlestickChart, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent])

const gameStore = useGameStore()

const stocks = ref([])
const holdings = ref([])
const selectedStock = ref(null)
const tradeQty = ref(100)
const currentSector = ref('all')
const currentPeriod = ref('day')
const marketIndex = ref(3250.45)
const marketChange = ref(1.25)
const marketMood = ref('bullish')
const klineData = ref([])
const technicalData = ref(null)
const rightPanel = ref('trade')  // 'trade' or 'holdings'

const sectors = [
  { id: 'all', name: '全部' },
  { id: '科技', name: '科技' },
  { id: '金融', name: '金融' },
  { id: '消费', name: '消费' },
  { id: '医疗', name: '医疗' },
  { id: '能源', name: '能源' },
  { id: '房地产', name: '房产' }
]

const klinePeriods = [
  { id: 'day', name: '日K' },
  { id: 'week', name: '周K' },
  { id: 'month', name: '月K' }
]

const cash = computed(() => gameStore.assets?.cash || 0)
const marketTrend = computed(() => marketChange.value >= 0 ? 'up' : 'down')
const moodLabel = computed(() => ({ bullish: '乐观', bearish: '悲观', neutral: '中性' }[marketMood.value]))
const trendLabel = computed(() => {
  if (!technicalData.value?.trend) return '-'
  return { up: '▲ 上涨', down: '▼ 下跌', sideways: '→ 横盘' }[technicalData.value.trend] || '-'
})

const filteredStocks = computed(() => {
  if (currentSector.value === 'all') return stocks.value
  return stocks.value.filter(s => s.sector === currentSector.value)
})

const tradeAmount = computed(() => selectedStock.value ? selectedStock.value.price * tradeQty.value : 0)
const canBuy = computed(() => tradeQty.value > 0 && tradeAmount.value <= cash.value)
const canSell = computed(() => {
  if (!selectedStock.value) return false
  const h = holdings.value.find(x => x.stock_id === selectedStock.value.id)
  return h && h.shares >= tradeQty.value
})

// K-line chart configuration
const klineOption = computed(() => {
  const data = klineData.value
  const dates = data.map(d => d.date)
  const ohlc = data.map(d => [d.open, d.close, d.low, d.high])
  const volumes = data.map(d => d.volume)
  const ma5 = calculateMA(5, data)
  const ma20 = calculateMA(20, data)

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: 'rgba(0,0,0,0.8)',
      borderColor: 'var(--term-accent)',
      textStyle: { color: '#fff', fontSize: 11 }
    },
    legend: {
      data: ['K线', 'MA5', 'MA20'],
      textStyle: { color: 'var(--term-text)', fontSize: 10 },
      top: 0
    },
    grid: [
      { left: 50, right: 20, top: 40, height: '55%' },
      { left: 50, right: 20, top: '72%', height: '15%' }
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, axisLabel: { fontSize: 9 } },
      { type: 'category', data: dates, gridIndex: 1, axisLabel: { show: false } }
    ],
    yAxis: [
      { scale: true, gridIndex: 0, splitLine: { lineStyle: { color: 'rgba(128,128,128,0.2)' } } },
      { scale: true, gridIndex: 1, splitLine: { show: false }, axisLabel: { show: false } }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: ohlc,
        xAxisIndex: 0,
        yAxisIndex: 0,
        itemStyle: {
          color: '#10b981',
          color0: '#ef4444',
          borderColor: '#10b981',
          borderColor0: '#ef4444'
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: ma5,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 1, color: '#f59e0b' },
        xAxisIndex: 0,
        yAxisIndex: 0
      },
      {
        name: 'MA20',
        type: 'line',
        data: ma20,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 1, color: '#3b82f6' },
        xAxisIndex: 0,
        yAxisIndex: 0
      },
      {
        name: '成交量',
        type: 'bar',
        data: volumes,
        xAxisIndex: 1,
        yAxisIndex: 1,
        itemStyle: {
          color: (params) => {
            const idx = params.dataIndex
            return data[idx]?.close >= data[idx]?.open ? '#10b981' : '#ef4444'
          }
        }
      }
    ]
  }
})

const formatNumber = (n) => Number(n || 0).toLocaleString('zh-CN')

const calculateMA = (period, data) => {
  const result = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null)
    } else {
      let sum = 0
      for (let j = 0; j < period; j++) {
        sum += data[i - j].close
      }
      result.push((sum / period).toFixed(2))
    }
  }
  return result
}

const selectStock = (s) => {
  selectedStock.value = s
  tradeQty.value = 100
  loadKlineData()
}

const getSessionId = () => {
  try {
    const char = localStorage.getItem('currentCharacter')
    return char ? JSON.parse(char).id : null
  } catch { return null }
}

const loadKlineData = async () => {
  if (!selectedStock.value) return
  try {
    const res = await fetch(buildApiUrl(`/api/market/kline/${selectedStock.value.id}?period=${currentPeriod.value}`))
    const data = await res.json()
    if (data.success && data.kline && data.kline.length > 0) {
      klineData.value = data.kline
      // Calculate technical indicators
      const closes = data.kline.map(d => d.close)
      const ma5 = closes.slice(-5).reduce((a, b) => a + b, 0) / 5
      const ma20 = closes.length >= 20 ? closes.slice(-20).reduce((a, b) => a + b, 0) / 20 : null
      const lastClose = closes[closes.length - 1]
      const prevClose = closes.length > 1 ? closes[closes.length - 2] : lastClose
      
      technicalData.value = {
        ma5,
        ma20,
        trend: lastClose > prevClose ? 'up' : lastClose < prevClose ? 'down' : 'sideways'
      }
    } else {
      // API returned empty data, generate sample
      generateSampleKline()
    }
  } catch (e) {
    console.error('加载K线数据失败:', e)
    // Generate sample kline data
    generateSampleKline()
  }
}

const generateSampleKline = () => {
  if (!selectedStock.value) return
  const data = []
  let price = selectedStock.value.price
  const now = new Date()
  
  for (let i = 59; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    const volatility = 0.03
    const change = (Math.random() - 0.5) * 2 * volatility
    const open = price
    const close = price * (1 + change)
    const high = Math.max(open, close) * (1 + Math.random() * 0.015)
    const low = Math.min(open, close) * (1 - Math.random() * 0.015)
    const volume = Math.floor(Math.random() * 1000000 + 500000)
    
    data.push({
      date: `${date.getMonth() + 1}/${date.getDate()}`,
      open: +open.toFixed(2),
      close: +close.toFixed(2),
      high: +high.toFixed(2),
      low: +low.toFixed(2),
      volume
    })
    price = close
  }
  klineData.value = data
  
  const closes = data.map(d => d.close)
  technicalData.value = {
    ma5: closes.slice(-5).reduce((a, b) => a + b, 0) / 5,
    ma20: closes.slice(-20).reduce((a, b) => a + b, 0) / 20,
    trend: closes[closes.length - 1] > closes[closes.length - 2] ? 'up' : 'down'
  }
}

const executeTrade = async (action) => {
  if (!selectedStock.value) return
  const sessionId = getSessionId()
  if (!sessionId) {
    alert('请先选择角色')
    return
  }
  try {
    const res = await fetch(buildApiUrl(`/api/stock/${action}`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        stock_id: selectedStock.value.id,
        shares: tradeQty.value
      })
    })
    const data = await res.json()
    if (data.success) {
      await loadHoldings()
      await gameStore.loadAvatar()
    } else {
      alert(data.message || '交易失败')
    }
  } catch (e) {
    console.error(e)
  }
}

const loadStocks = async () => {
  try {
    const res = await fetch(buildApiUrl('/api/market/stocks'))
    const data = await res.json()
    if (data.success && data.stocks) {
      stocks.value = data.stocks.map(s => ({
        id: s.code,
        name: s.name,
        price: s.price,
        change: s.change_pct,
        sector: s.sector?.toLowerCase() || 'other'
      }))
      loadMarketState()
    }
  } catch (e) {
    console.error('加载股票列表失败:', e)
    stocks.value = [
      { id: 'ECHO01', name: '回声科技', price: 45.20, change: 2.35, sector: '科技' },
      { id: 'ECHO04', name: '汇通银行', price: 25.00, change: -0.85, sector: '金融' },
      { id: 'ECHO07', name: '国民饮品', price: 180.00, change: 1.50, sector: '消费' },
      { id: 'ECHO10', name: '康健医药', price: 95.00, change: 0.80, sector: '医疗' },
      { id: 'ECHO13', name: '绿能科技', price: 78.00, change: -1.25, sector: '能源' },
      { id: 'ECHO16', name: '安居地产', price: 12.00, change: -0.50, sector: '房地产' }
    ]
  }
}

const loadMarketState = async () => {
  try {
    const res = await fetch(buildApiUrl('/api/market/state'))
    const data = await res.json()
    if (data.success && data.state) {
      marketIndex.value = data.state.index_value || 3000
      const advancing = data.state.advancing || 0
      const declining = data.state.declining || 0
      if (advancing > declining) {
        marketMood.value = 'bullish'
        marketChange.value = Math.abs((advancing - declining) / (advancing + declining || 1) * 3)
      } else if (declining > advancing) {
        marketMood.value = 'bearish'
        marketChange.value = -Math.abs((declining - advancing) / (advancing + declining || 1) * 3)
      } else {
        marketMood.value = 'neutral'
        marketChange.value = 0
      }
    }
  } catch (e) {
    console.error('加载市场状态失败:', e)
  }
}

const loadHoldings = async () => {
  const sessionId = getSessionId()
  if (!sessionId) return
  try {
    const res = await fetch(buildApiUrl(`/api/stock/holdings?session_id=${sessionId}`))
    const data = await res.json()
    if (data.success) holdings.value = data.holdings
  } catch (e) {
    holdings.value = []
  }
}

onMounted(() => {
  loadStocks()
  loadHoldings()
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

.view-header h2 {
  font-size: 24px;
  font-weight: 900;
  margin: 0 0 8px 0;
}

.header-line {
  height: 2px;
  background: var(--term-border);
  margin-bottom: 24px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  flex: 1;
  min-height: 0;
}

.col-left, .col-right {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.flex-grow { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.scrollable { flex: 1; overflow-y: auto; }

/* Index Display */
.index-display { text-align: center; margin-bottom: 16px; }
.index-value { font-size: 32px; font-weight: 900; }
.index-value.up { color: var(--term-success); }
.index-value.down { color: #ef4444; }
.index-change { font-size: 14px; font-weight: 700; }
.index-change.up { color: var(--term-success); }
.index-change.down { color: #ef4444; }

.mood-row { display: flex; justify-content: space-between; font-size: 12px; }
.mood-tag { padding: 2px 8px; font-weight: 700; }
.mood-tag.bullish { background: var(--term-success); color: #000; }
.mood-tag.bearish { background: #ef4444; color: #fff; }
.mood-tag.neutral { background: var(--term-border); }

/* Filter Tabs */
.filter-tabs { display: flex; gap: 4px; }
.tab { font-size: 10px; padding: 2px 6px; cursor: pointer; border: 1px solid var(--term-border); }
.tab.active { background: var(--term-accent); color: #000; border-color: var(--term-accent); }

/* Chart Container */
.chart-container { height: 220px; padding: 8px 0; }
.chart { width: 100%; height: 100%; }
.chart-loading { height: 220px; display: flex; align-items: center; justify-content: center; color: var(--term-text-secondary); }
.clickable { cursor: pointer; }
.header-actions { display: flex; align-items: center; gap: 12px; }
.toggle-icon { font-size: 10px; color: var(--term-text-secondary); }

/* Technical Indicators */
.tech-indicators {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(0,0,0,0.03);
  border: 1px solid var(--term-border);
  margin-bottom: 16px;
}
.indicator { flex: 1; text-align: center; }
.ind-label { display: block; font-size: 10px; color: var(--term-text-secondary); margin-bottom: 4px; }
.ind-value { font-size: 14px; font-weight: 700; }
.ind-value.up { color: var(--term-success); }
.ind-value.down { color: #ef4444; }
.ind-value.sideways { color: var(--term-accent); }

/* Stock Row */
.stock-row {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  border: 1px solid var(--term-border);
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.15s;
}
.stock-row:hover, .stock-row.selected {
  background: rgba(0,0,0,0.05);
  border-color: var(--term-accent);
}
.stock-name { font-weight: 700; font-size: 14px; }
.stock-code { font-size: 10px; color: var(--term-text-secondary); }
.stock-price { text-align: right; }
.price { font-weight: 700; }
.change { font-size: 11px; }
.change.up { color: var(--term-success); }
.change.down { color: #ef4444; }

/* Trade Panel */
.selected-info { text-align: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px dashed var(--term-border); }
.selected-info h3 { margin: 0 0 8px 0; font-size: 18px; }
.price-big { font-size: 28px; font-weight: 900; }
.change-tag { display: inline-block; padding: 4px 8px; font-size: 12px; font-weight: 700; margin-top: 4px; }
.change-tag.up { background: var(--term-success); color: #000; }
.change-tag.down { background: #ef4444; color: #fff; }

.form-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.form-row label { font-size: 12px; font-weight: 700; }
.qty-input { display: flex; align-items: center; gap: 8px; }
.qty-input input { width: 80px; text-align: center; padding: 6px; border: 1px solid var(--term-border); font-family: inherit; }
.qty-btn { width: 28px; height: 28px; border: 1px solid var(--term-border); background: var(--term-panel-bg); cursor: pointer; font-weight: 700; }
.qty-btn:hover { background: var(--term-accent); color: #000; }
.amount-val { font-size: 18px; font-weight: 700; color: var(--term-accent); }

.trade-actions { display: flex; gap: 12px; }
.term-btn.buy { flex: 1; background: var(--term-success); color: #000; border: 2px solid #000; padding: 12px; font-weight: 800; }
.term-btn.sell { flex: 1; background: #ef4444; color: #fff; border: 2px solid #000; padding: 12px; font-weight: 800; }
.term-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* Holdings */
.holding-row { display: flex; justify-content: space-between; padding: 12px; border: 1px solid var(--term-border); margin-bottom: 8px; }
.holding-name { font-weight: 700; }
.holding-shares { font-size: 11px; color: var(--term-text-secondary); }
.holding-value { text-align: right; }
.market-val { font-weight: 700; }
.profit { font-size: 11px; }
.profit.up { color: var(--term-success); }
.profit.down { color: #ef4444; }

.empty-state { text-align: center; padding: 40px 20px; color: var(--term-text-secondary); }

/* Archive Card Base */
.archive-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
}
.archive-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(0,0,0,0.03);
  border-bottom: 1px solid var(--term-border);
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
}
.archive-body {
  padding: 16px;
}

/* Accordion Styles */
.accordion-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.accordion-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.accordion-card.expanded {
  flex: 1;
}

.accordion-card.collapsed {
  flex: 0 0 auto;
  cursor: pointer;
}

.accordion-card.collapsed:hover {
  border-color: var(--term-accent);
}

.accordion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(0,0,0,0.03);
  border-bottom: 1px solid var(--term-border);
  font-weight: 700;
}

.accordion-icon {
  font-size: 16px;
}

.accordion-title {
  flex: 1;
  font-size: 12px;
  text-transform: uppercase;
}

.accordion-arrow {
  font-size: 10px;
  color: var(--term-text-secondary);
}

.accordion-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* K-line Section inside Trading Panel */
.kline-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px dashed var(--term-border);
}

.kline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.kline-title {
  font-weight: 700;
  font-size: 12px;
}

.trade-section {
  /* Keep existing trade content styling */
}

@media (max-width: 768px) {
  .content-grid { grid-template-columns: 1fr; }
  .view-container { overflow-y: auto; }
  .chart-container { height: 200px; }
}
</style>
