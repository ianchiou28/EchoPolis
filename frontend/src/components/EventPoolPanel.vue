<template>
  <div class="event-pool-panel">
    <div class="panel-header">
      <h3>📡 实时事件池</h3>
      <div class="header-actions">
        <button class="refresh-btn" @click="refreshEvents" :disabled="loading">
          {{ loading ? '加载中...' : '🔄 刷新' }}
        </button>
        <button class="init-btn" @click="initSamples" :disabled="loading">
          📥 初始化示例
        </button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-value">{{ stats.memory_pool_size || 0 }}</span>
        <span class="stat-label">内存事件</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.database_count || 0 }}</span>
        <span class="stat-label">数据库事件</span>
      </div>
    </div>

    <!-- 分类筛选 -->
    <div class="category-filter">
      <button 
        v-for="cat in categories" 
        :key="cat.value"
        :class="['filter-btn', { active: selectedCategory === cat.value }]"
        @click="selectCategory(cat.value)"
      >
        {{ cat.icon }} {{ cat.label }}
      </button>
    </div>

    <!-- 事件列表 -->
    <div class="events-list" v-if="events.length > 0">
      <div 
        v-for="event in events" 
        :key="event.id" 
        :class="['event-card', `sentiment-${event.sentiment}`]"
      >
        <div class="event-header">
          <span class="event-category">{{ getCategoryIcon(event.category) }}</span>
          <span class="event-title">{{ event.title }}</span>
          <span :class="['sentiment-badge', event.sentiment]">
            {{ getSentimentLabel(event.sentiment) }}
          </span>
        </div>
        <div class="event-summary">{{ event.summary }}</div>
        <div class="event-meta">
          <span class="event-source">📰 {{ event.source }}</span>
          <span class="event-tags" v-if="event.tags && event.tags.length">
            <span class="tag" v-for="tag in event.tags.slice(0, 3)" :key="tag">
              {{ tag }}
            </span>
          </span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else-if="!loading">
      <p>暂无事件数据</p>
      <button class="init-btn" @click="initSamples">初始化示例事件</button>
    </div>

    <!-- 加载状态 -->
    <div class="loading-state" v-if="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
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

const categories = [
  { value: null, label: '全部', icon: '📋' },
  { value: '市场行情', label: '市场', icon: '📈' },
  { value: '政策法规', label: '政策', icon: '📜' },
  { value: '行业动态', label: '行业', icon: '🏭' },
  { value: '宏观经济', label: '经济', icon: '🌍' },
  { value: '科技创新', label: '科技', icon: '🚀' }
]

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
    const data = await res.json()
    if (data.success) {
      stats.value = data.stats
    }
  } catch (e) {
    console.error('获取统计失败:', e)
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
    const data = await res.json()
    if (data.success) {
      events.value = data.events
    }
  } catch (e) {
    console.error('获取事件失败:', e)
  } finally {
    loading.value = false
  }
}

async function initSamples() {
  loading.value = true
  try {
    const res = await fetch(buildApiUrl('/api/event-pool/init-samples'), {
      method: 'POST'
    })
    const data = await res.json()
    if (data.success) {
      alert(data.message)
      await refreshEvents()
    }
  } catch (e) {
    console.error('初始化失败:', e)
    alert('初始化失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

async function refreshEvents() {
  await fetchStats()
  await fetchEvents()
}

function selectCategory(cat) {
  selectedCategory.value = cat
  fetchEvents()
}

onMounted(() => {
  refreshEvents()
})
</script>

<style scoped>
.event-pool-panel {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.refresh-btn, .init-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.refresh-btn {
  background: #E04F00;
  color: white;
}

.refresh-btn:hover:not(:disabled) {
  background: #c44500;
}

.init-btn {
  background: #f0f0f0;
  color: #333;
}

.init-btn:hover:not(:disabled) {
  background: #e0e0e0;
}

.stats-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f8f8f8;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #E04F00;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

.category-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.filter-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 16px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.filter-btn.active {
  background: #E04F00;
  color: white;
  border-color: #E04F00;
}

.filter-btn:hover:not(.active) {
  border-color: #E04F00;
  color: #E04F00;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
}

.event-card {
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #ccc;
  background: #fafafa;
  transition: all 0.2s;
}

.event-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.event-card.sentiment-positive {
  border-left-color: #52c41a;
  background: #f6ffed;
}

.event-card.sentiment-negative {
  border-left-color: #ff4d4f;
  background: #fff2f0;
}

.event-card.sentiment-neutral {
  border-left-color: #1890ff;
  background: #e6f7ff;
}

.event-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.event-category {
  font-size: 18px;
}

.event-title {
  flex: 1;
  font-weight: 600;
  color: #333;
}

.sentiment-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.sentiment-badge.positive {
  background: #52c41a;
  color: white;
}

.sentiment-badge.negative {
  background: #ff4d4f;
  color: white;
}

.sentiment-badge.neutral {
  background: #1890ff;
  color: white;
}

.event-summary {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 8px;
}

.event-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.event-tags {
  display: flex;
  gap: 4px;
}

.tag {
  padding: 2px 6px;
  background: #f0f0f0;
  border-radius: 4px;
}

.empty-state, .loading-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f0f0f0;
  border-top-color: #E04F00;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
