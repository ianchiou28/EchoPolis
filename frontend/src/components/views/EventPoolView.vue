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

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

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
    const res = await fetch(`${API_BASE}/api/event-pool/stats`)
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
    const res = await fetch(`${API_BASE}/api/event-pool/wide-research-status`, {
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
    let url = `${API_BASE}/api/event-pool/events?limit=50`
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
    const res = await fetch(`${API_BASE}/api/event-pool/fetch-latest`, {
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
.view-container {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.view-header {
  margin-bottom: 8px;
}

.view-header h2 {
  font-size: 1.5rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.header-line {
  height: 3px;
  background: var(--term-accent, #E04F00);
  margin-top: 8px;
  width: 80px;
}

/* 统计卡片 */
.stats-summary {
  display: flex;
  gap: 12px;
}

.stat-box {
  flex: 1;
  padding: 16px;
  background: var(--term-panel-bg, rgba(0,0,0,0.3));
  border: 2px solid var(--term-border, rgba(255,255,255,0.1));
  text-align: center;
}

.stat-box.online {
  border-color: #52c41a;
}

.stat-box.offline {
  border-color: #ff4d4f;
}

.stat-value {
  display: block;
  font-size: 1.75rem;
  font-weight: 900;
}

.stat-value.accent {
  color: var(--term-accent, #E04F00);
}

.stat-value.success {
  color: #52c41a;
}

.stat-value.error {
  color: #ff4d4f;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--term-text-secondary, #888);
  text-transform: uppercase;
  margin-top: 4px;
  letter-spacing: 0.05em;
}

/* Archive Card 样式 */
.archive-card {
  background: var(--term-panel-bg, rgba(0,0,0,0.3));
  border: 2px solid var(--term-border, rgba(255,255,255,0.1));
}

.archive-card.flex-grow {
  flex: 1;
  min-height: 300px;
  display: flex;
  flex-direction: column;
}

.archive-header {
  padding: 12px 16px;
  background: rgba(0,0,0,0.2);
  border-bottom: 1px solid var(--term-border, rgba(255,255,255,0.1));
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.archive-header .count {
  background: var(--term-accent, #E04F00);
  color: #000;
  padding: 2px 8px;
  font-size: 0.7rem;
  font-weight: 900;
}

.archive-header .blink {
  color: var(--term-accent, #E04F00);
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.archive-body {
  padding: 16px;
}

.archive-body.scrollable-body {
  flex: 1;
  overflow-y: auto;
  max-height: calc(100vh - 500px);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.term-btn {
  padding: 10px 20px;
  background: transparent;
  border: 2px solid var(--term-border, rgba(255,255,255,0.2));
  color: var(--term-text, #fff);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.term-btn:hover:not(:disabled) {
  background: rgba(255,255,255,0.1);
  border-color: var(--term-accent, #E04F00);
}

.term-btn.primary {
  background: var(--term-accent, #E04F00);
  border-color: var(--term-accent, #E04F00);
  color: #000;
}

.term-btn.primary:hover:not(:disabled) {
  opacity: 0.9;
}

.term-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 备用数据提示 */
.fallback-badge {
  background: #f59e0b;
  color: #000;
  padding: 2px 8px;
  font-size: 0.7rem;
  font-weight: 700;
}

.fallback-hint {
  margin-top: 12px;
  padding: 8px 12px;
  background: rgba(245, 158, 11, 0.15);
  border-left: 3px solid #f59e0b;
  font-size: 0.85rem;
  color: #f59e0b;
}

/* 筛选标签 */
.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-tag {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--term-border, rgba(255,255,255,0.2));
  color: var(--term-text-secondary, #888);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tag:hover {
  border-color: var(--term-accent, #E04F00);
  color: var(--term-text, #fff);
}

.filter-tag.active {
  background: var(--term-accent, #E04F00);
  border-color: var(--term-accent, #E04F00);
  color: #000;
  font-weight: 600;
}

/* 事件列表 */
.events-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-item {
  display: flex;
  gap: 12px;
  padding: 14px;
  background: rgba(0,0,0,0.15);
  border-left: 3px solid var(--term-border, rgba(255,255,255,0.2));
  cursor: pointer;
  transition: all 0.2s;
}

.event-item:hover {
  background: rgba(255,255,255,0.05);
}

.event-item.sentiment-positive {
  border-left-color: #52c41a;
}

.event-item.sentiment-negative {
  border-left-color: #ff4d4f;
}

.event-item.sentiment-neutral {
  border-left-color: #1890ff;
}

.event-left {
  flex-shrink: 0;
}

.event-icon {
  font-size: 1.5rem;
}

.event-content {
  flex: 1;
  min-width: 0;
}

.event-title {
  font-weight: 700;
  font-size: 0.95rem;
  margin-bottom: 6px;
  line-height: 1.3;
}

.event-summary {
  color: var(--term-text-secondary, #888);
  font-size: 0.85rem;
  line-height: 1.5;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.event-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.75rem;
  color: var(--term-text-secondary, #666);
}

.meta-tags {
  display: flex;
  gap: 4px;
}

.tag {
  padding: 2px 6px;
  background: rgba(255,255,255,0.1);
  font-size: 0.7rem;
}

.event-right {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
}

.sentiment-badge {
  padding: 4px 8px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

.sentiment-badge.positive {
  background: #52c41a;
  color: #fff;
}

.sentiment-badge.negative {
  background: #ff4d4f;
  color: #fff;
}

.sentiment-badge.neutral {
  background: #1890ff;
  color: #fff;
}

/* 空状态和加载状态 */
.empty-state, .loading-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--term-text-secondary, #666);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 0.85rem;
  opacity: 0.7;
}

.scanline-loader {
  padding: 20px;
  background: linear-gradient(90deg, transparent, rgba(var(--term-accent-rgb, 224, 79, 0), 0.2), transparent);
  background-size: 200% 100%;
  animation: scanline 1.5s linear infinite;
  font-size: 0.9rem;
}

@keyframes scanline {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 消息提示 */
.message-toast {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  background: #333;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
  z-index: 1000;
  border: 2px solid var(--term-border, rgba(255,255,255,0.2));
}

.message-toast.success {
  background: #52c41a;
  border-color: #52c41a;
  color: #fff;
}

.message-toast.error {
  background: #ff4d4f;
  border-color: #ff4d4f;
  color: #fff;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-summary {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .term-btn {
    width: 100%;
  }
  
  .event-item {
    flex-direction: column;
  }
  
  .event-right {
    align-self: flex-start;
  }
}
</style>
