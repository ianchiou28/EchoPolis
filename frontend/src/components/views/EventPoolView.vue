<template>
  <div class="view-container">
    <div class="view-header">
      <h2>事件池 // EVENT_POOL</h2>
      <div class="header-line"></div>
    </div>

    <div class="content-grid">
      <!-- Left: Stats & Controls -->
      <div class="col-left">
        <!-- 统计状态 -->
        <div class="archive-card">
          <div class="archive-header">数据状态</div>
          <div class="archive-body">
            <div class="status-bars">
              <div class="status-item">
                <div class="status-label">
                  <span>📊 内存事件</span>
                  <span class="status-value accent">{{ stats.memory_pool_size || 0 }}</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill memory" :style="{width: Math.min((stats.memory_pool_size || 0) / 100 * 100, 100) + '%'}"></div>
                </div>
              </div>
              <div class="status-item">
                <div class="status-label">
                  <span>💾 数据库事件</span>
                  <span class="status-value">{{ stats.database_count || 0 }}</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill database" :style="{width: Math.min((stats.database_count || 0) / 100 * 100, 100) + '%'}"></div>
                </div>
              </div>
              <div class="status-item">
                <div class="status-label">
                  <span>🌐 Wide-Research</span>
                  <span :class="['status-value', wideResearchStatus === 'online' ? 'positive' : 'negative']">
                    {{ wideResearchStatus === 'online' ? '在线' : wideResearchStatus === 'checking' ? '检测中' : '离线' }}
                  </span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill wide-research" :class="wideResearchStatus" :style="{width: wideResearchStatus === 'online' ? '100%' : '0%'}"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作面板 -->
        <div class="archive-card">
          <div class="archive-header">
            <span>数据操作</span>
            <span v-if="loading" class="blink">处理中...</span>
            <span v-if="usingFallback" class="fallback-badge">备用</span>
          </div>
          <div class="archive-body">
            <div class="action-list">
              <button class="action-item primary" @click="fetchLatestEvents" :disabled="loading">
                <span class="action-icon">📡</span>
                <span class="action-text">{{ loading ? '获取中...' : '获取最新事件' }}</span>
              </button>
              <button class="action-item" @click="refreshEvents" :disabled="loading">
                <span class="action-icon">🔄</span>
                <span class="action-text">刷新数据</span>
              </button>
            </div>
            <div v-if="usingFallback" class="fallback-hint">
              ⚠️ Wide-Research 不可用，已使用备用数据
            </div>
          </div>
        </div>

        <!-- 分类筛选 -->
        <div class="archive-card flex-grow">
          <div class="archive-header">分类筛选</div>
          <div class="archive-body">
            <div class="filter-grid">
              <div 
                v-for="cat in categories" 
                :key="cat.value"
                :class="['filter-card', { active: selectedCategory === cat.value }]"
                @click="selectCategory(cat.value)"
              >
                <div class="filter-icon">{{ cat.icon }}</div>
                <div class="filter-name">{{ cat.label }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Event List -->
      <div class="col-right">
        <div class="archive-card flex-grow">
          <div class="archive-header">
            <span>事件列表</span>
            <span class="count-badge">{{ events.length }}</span>
          </div>
          <div class="archive-body scrollable">
            <!-- 加载状态 -->
            <div v-if="loading" class="loading-state">
              <div class="loader-icon">⏳</div>
              <div class="loader-text">加载事件数据中...</div>
            </div>

            <!-- 事件列表 -->
            <div v-else-if="events.length > 0" class="event-list">
              <div 
                v-for="event in events" 
                :key="event.id" 
                :class="['event-item', `sentiment-${event.sentiment}`]"
                @click="showEventDetail(event)"
              >
                <div class="event-main">
                  <div class="event-icon">{{ getCategoryIcon(event.category) }}</div>
                  <div class="event-info">
                    <div class="event-title">{{ event.title }}</div>
                    <div class="event-summary">{{ event.summary }}</div>
                  </div>
                </div>
                <div class="event-right">
                  <span :class="['sentiment-tag', event.sentiment]">
                    {{ getSentimentLabel(event.sentiment) }}
                  </span>
                  <div class="event-source">{{ event.source || 'Wide-Research' }}</div>
                </div>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-else class="empty-state">
              暂无事件数据，请点击获取按钮
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Result Toast -->
    <div class="result-toast" v-if="message" :class="messageType">
      <div class="result-icon">{{ messageType === 'success' ? '✓' : messageType === 'error' ? '✗' : 'ℹ' }}</div>
      <div class="result-text">{{ message }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { buildApiUrl } from '@/utils/api'

const loading = ref(false)
const events = ref([])
const stats = ref({})
const selectedCategory = ref(null)
const wideResearchStatus = ref('checking')
const message = ref('')
const messageType = ref('info')
const usingFallback = ref(false)

const categories = [
  { value: null, label: '全部', icon: '📋' },
  { value: '市场行情', label: '市场', icon: '📈' },
  { value: '政策法规', label: '政策', icon: '📜' },
  { value: '行业动态', label: '行业', icon: '🏭' },
  { value: '宏观经济', label: '经济', icon: '🌍' },
  { value: '科技创新', label: '科技', icon: '🚀' }
]

function showMessage(text, type = 'info') {
  message.value = text
  messageType.value = type
  setTimeout(() => { message.value = '' }, 4000)
}

function getCategoryIcon(category) {
  const icons = {
    '市场行情': '📈',
    '政策法规': '📜',
    '行业动态': '🏭',
    '宏观经济': '🌍',
    '科技创新': '🚀',
    '社会民生': '👥',
    '国际形势': '🌐'
  }
  return icons[category] || '📌'
}

function getSentimentLabel(sentiment) {
  const labels = {
    'positive': '利好',
    'negative': '利空',
    'neutral': '中性'
  }
  return labels[sentiment] || sentiment
}

async function fetchStats() {
  try {
    const res = await fetch(buildApiUrl('/api/event-pool/stats'))
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        stats.value = data.stats
      }
    }
  } catch (e) {
    console.error('获取统计失败:', e)
  }
}

async function checkWideResearchStatus() {
  wideResearchStatus.value = 'checking'
  try {
    const res = await fetch(buildApiUrl('/api/event-pool/wide-research-status'), {
      signal: AbortSignal.timeout(10000)
    })
    if (res.ok) {
      const data = await res.json()
      wideResearchStatus.value = data.status || 'offline'
    } else {
      wideResearchStatus.value = 'offline'
    }
  } catch (e) {
    console.error('检查Wide-Research状态失败:', e)
    wideResearchStatus.value = 'offline'
  }
}

async function fetchEvents() {
  loading.value = true
  try {
    let url = buildApiUrl('/api/event-pool/events?limit=50')
    if (selectedCategory.value) {
      url += `&category=${encodeURIComponent(selectedCategory.value)}`
    }
    const res = await fetch(url)
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        events.value = data.events || []
      }
    }
  } catch (e) {
    console.error('获取事件失败:', e)
  } finally {
    loading.value = false
  }
}

async function fetchLatestEvents() {
  loading.value = true
  usingFallback.value = false
  
  try {
    // 调用后端统一接口，后端会自动处理降级
    const res = await fetch(buildApiUrl('/api/event-pool/fetch-latest'), {
      method: 'POST',
      signal: AbortSignal.timeout(30000)
    })
    if (res.ok) {
      const data = await res.json()
      if (data.success) {
        usingFallback.value = data.used_fallback || false
        if (data.used_fallback) {
          showMessage(`Wide-Research 不可用，已加载 ${data.fetched} 条备用事件`, 'info')
        } else {
          showMessage(`从 Wide-Research 获取了 ${data.fetched} 条事件`, 'success')
        }
        await refreshEvents()
      } else {
        showMessage('获取失败: ' + (data.error || '未知错误'), 'error')
      }
    } else {
      showMessage('服务器响应错误', 'error')
    }
  } catch (e) {
    console.error('获取失败:', e)
    if (e.name === 'TimeoutError') {
      showMessage('请求超时，请重试', 'error')
    } else {
      showMessage('网络错误: ' + e.message, 'error')
    }
  } finally {
    loading.value = false
  }
}

async function refreshEvents() {
  await Promise.all([fetchStats(), checkWideResearchStatus()])
  await fetchEvents()
}

function selectCategory(cat) {
  selectedCategory.value = cat
  fetchEvents()
}

function showEventDetail(event) {
  // 未来可以弹出详情模态框
  console.log('Event detail:', event)
  showMessage(`查看事件: ${event.title}`, 'info')
}

// 页面加载时自动获取数据
onMounted(async () => {
  loading.value = true
  try {
    // 先检查状态和获取现有数据
    await Promise.all([fetchStats(), checkWideResearchStatus()])
    await fetchEvents()
    
    // 如果没有事件，自动获取（后端会处理降级）
    if (events.value.length === 0) {
      showMessage('正在获取最新事件...', 'info')
      await fetchLatestEvents()
    }
  } catch (e) {
    console.error('初始化失败:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* Container & Header - 与LifestyleView统一 */
.view-container {
  padding: 20px;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.view-header { margin-bottom: 16px; }
.view-header h2 { font-size: 1.2rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.05em; margin: 0; }
.header-line { height: 3px; background: var(--term-accent); margin-top: 8px; width: 80px; }

/* Grid Layout - 与LifestyleView相同 */
.content-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 16px;
  min-height: 0;
}

.col-left, .col-right {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

/* Archive Card - 与LifestyleView统一 */
.archive-card { background: var(--term-panel-bg); border: 2px solid var(--term-border); }
.archive-card.flex-grow { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.archive-header { 
  padding: 12px 16px; 
  font-weight: 800; 
  font-size: 12px; 
  border-bottom: 1px solid var(--term-border); 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
}
.archive-body { padding: 16px; }
.archive-body.scrollable { flex: 1; overflow-y: auto; }

/* Status Bars - 与LifestyleView统一 */
.status-bars { display: flex; flex-direction: column; gap: 16px; }
.status-item { }
.status-label { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; }
.status-value { font-weight: 700; }
.status-value.accent { color: var(--term-accent); }
.status-value.positive { color: #10b981; }
.status-value.negative { color: #ef4444; }
.bar-track { height: 8px; background: rgba(0,0,0,0.1); border: 1px solid var(--term-border); }
.bar-fill { height: 100%; transition: width 0.3s; }
.bar-fill.memory { background: var(--term-accent); }
.bar-fill.database { background: #3b82f6; }
.bar-fill.wide-research { background: #10b981; }
.bar-fill.wide-research.offline { background: #ef4444; }
.bar-fill.wide-research.checking { background: #f59e0b; }

/* Action List */
.action-list { display: flex; flex-direction: column; gap: 8px; }
.action-item { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  padding: 12px 16px; 
  border: 1px solid var(--term-border); 
  background: transparent; 
  cursor: pointer; 
  transition: all 0.2s; 
  font-size: 12px;
  font-weight: 600;
}
.action-item:hover:not(:disabled) { border-color: var(--term-accent); }
.action-item.primary { background: var(--term-accent); border-color: var(--term-accent); color: #000; }
.action-item.primary:hover:not(:disabled) { opacity: 0.9; }
.action-item:disabled { opacity: 0.5; cursor: not-allowed; }
.action-icon { font-size: 16px; }
.action-text { flex: 1; }

/* Badges */
.count-badge { background: var(--term-accent); color: #000; padding: 2px 8px; font-size: 10px; font-weight: 900; }
.fallback-badge { background: #f59e0b; color: #000; padding: 2px 8px; font-size: 10px; font-weight: 700; }
.blink { color: var(--term-accent); animation: blink 1s infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

.fallback-hint {
  margin-top: 12px;
  padding: 8px 12px;
  background: rgba(245, 158, 11, 0.1);
  border-left: 3px solid #f59e0b;
  font-size: 11px;
  color: #f59e0b;
}

/* Filter Grid - 与LifestyleView活动卡片类似 */
.filter-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.filter-card { 
  padding: 12px; 
  border: 1px solid var(--term-border); 
  text-align: center; 
  cursor: pointer; 
  transition: all 0.2s; 
}
.filter-card:hover { border-color: var(--term-accent); transform: translateY(-2px); }
.filter-card.active { background: var(--term-accent); border-color: var(--term-accent); color: #000; }
.filter-icon { font-size: 20px; }
.filter-name { font-weight: 700; font-size: 11px; margin-top: 4px; }

/* Event List - 与LifestyleView的activity-item类似 */
.event-list { display: flex; flex-direction: column; gap: 10px; }
.event-item { 
  display: flex; 
  justify-content: space-between; 
  padding: 12px; 
  border: 1px solid var(--term-border); 
  border-left: 3px solid var(--term-border);
  cursor: pointer; 
  transition: all 0.2s;
}
.event-item:hover { border-color: var(--term-accent); }
.event-item.sentiment-positive { border-left-color: #10b981; }
.event-item.sentiment-negative { border-left-color: #ef4444; }
.event-item.sentiment-neutral { border-left-color: #3b82f6; }

.event-main { display: flex; gap: 12px; flex: 1; min-width: 0; }
.event-icon { font-size: 24px; flex-shrink: 0; }
.event-info { flex: 1; min-width: 0; }
.event-title { font-weight: 700; font-size: 13px; margin-bottom: 4px; }
.event-summary { font-size: 11px; color: var(--term-text-secondary); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

.event-right { text-align: right; flex-shrink: 0; display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.sentiment-tag { font-size: 10px; padding: 2px 8px; font-weight: 700; }
.sentiment-tag.positive { background: #10b981; color: #fff; }
.sentiment-tag.negative { background: #ef4444; color: #fff; }
.sentiment-tag.neutral { background: #3b82f6; color: #fff; }
.event-source { font-size: 10px; color: var(--term-text-secondary); }

/* Loading & Empty States */
.loading-state, .empty-state { 
  text-align: center; 
  padding: 40px 20px; 
  color: var(--term-text-secondary); 
}
.loader-icon { font-size: 32px; margin-bottom: 12px; animation: pulse 1s infinite; }
.loader-text { font-size: 12px; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

/* Result Toast - 与LifestyleView统一 */
.result-toast { 
  position: fixed; 
  bottom: 100px; 
  left: 50%; 
  transform: translateX(-50%); 
  padding: 12px 24px; 
  background: var(--term-panel-bg); 
  border: 2px solid var(--term-border); 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  z-index: 1000; 
  animation: slideUp 0.3s; 
}
.result-toast.success { border-color: #10b981; }
.result-toast.error { border-color: #ef4444; }
.result-toast.info { border-color: #3b82f6; }
.result-icon { font-size: 18px; }
.result-toast.success .result-icon { color: #10b981; }
.result-toast.error .result-icon { color: #ef4444; }
.result-toast.info .result-icon { color: #3b82f6; }
.result-text { font-size: 12px; }
@keyframes slideUp { from { transform: translateX(-50%) translateY(20px); opacity: 0; } to { transform: translateX(-50%) translateY(0); opacity: 1; } }

/* Responsive */
@media (max-width: 768px) {
  .view-container {
    height: auto;
    min-height: 100%;
    overflow: visible;
    padding: 16px 8px;
  }
  
  .content-grid { 
    grid-template-columns: 1fr;
    gap: 12px;
    flex: none;
  }
  
  .col-left, .col-right {
    min-height: auto;
    gap: 12px;
  }
  
  .archive-card.flex-grow {
    flex: none;
    min-height: auto;
  }
  
  .filter-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
