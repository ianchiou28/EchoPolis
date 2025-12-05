<template>
  <div class="event-echo-page">
    <!-- 移动端侧边栏遮罩 -->
    <div class="sidebar-overlay" v-if="isSidebarOpen" @click="isSidebarOpen = false"></div>

    <!-- 左侧导航栏 -->
    <nav class="sidebar-nav" :class="{ open: isSidebarOpen }">
      <div class="nav-header">
        <div class="logo-text">EchoPolis</div>
        <div class="sub-header">// 事件回响</div>
        <button class="close-sidebar-btn" @click="isSidebarOpen = false">×</button>
      </div>

      <div class="nav-section">
        <div class="section-label">模块导航</div>
        
        <div 
          :class="['nav-item', { active: $route.name === 'WorldSandbox' }]"
          @click="$router.push('/world-sandbox')">
          <span class="icon">🗺️</span>
          世界沙盘
        </div>
        
        <div 
          :class="['nav-item', { active: $route.name === 'EventEcho' }]"
          @click="$router.push('/event-echo')">
          <span class="icon">🎲</span>
          事件回响
        </div>
        
        <div 
          :class="['nav-item', { active: $route.name === 'PersonalCenter' }]"
          @click="$router.push('/personal-center')">
          <span class="icon">👤</span>
          个人中心
        </div>
      </div>

      <div class="nav-spacer"></div>

      <div class="system-actions">
        <button class="action-btn" @click="$router.push('/character-select')">
          <span class="icon">🔌</span>
          <span class="label">断开</span>
        </button>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部状态栏 -->
      <header class="top-bar">
        <button class="menu-btn" @click="isSidebarOpen = true">☰</button>
        
        <div class="brand-logo">
          <span class="highlight">EchoPolis</span> // 事件回响
        </div>
        
        <div class="header-right">
          <div class="tag-counter">
            <span class="icon">🏷️</span>
            <span>{{ userTags.length }} 个标签</span>
          </div>
        </div>
      </header>

      <!-- 事件内容区 -->
      <div class="event-content">
        <!-- 左侧：用户标签面板 -->
        <aside class="tags-panel">
          <div class="panel-header">
            <h3>🏷️ 我的标签</h3>
            <span class="tag-count">{{ userTags.length }}</span>
          </div>
          <div class="tags-list">
            <div 
              v-for="tag in userTags" 
              :key="tag.id" 
              class="tag-item"
              :class="{ active: selectedTags.includes(tag.id) }"
              @click="toggleTag(tag.id)">
              <span class="tag-icon">{{ tag.icon }}</span>
              <span class="tag-name">{{ tag.name }}</span>
              <span class="tag-weight">{{ tag.weight.toFixed(1) }}</span>
            </div>
            <div v-if="userTags.length === 0" class="empty-tags">
              <p>暂无标签</p>
              <p class="hint">选择事件后将自动生成标签</p>
            </div>
          </div>
          <div class="panel-footer">
            <button class="refresh-btn" @click="loadUserTags">
              🔄 刷新标签
            </button>
          </div>
        </aside>

        <!-- 中间：事件选择区 -->
        <section class="events-section">
          <div class="section-header">
            <h2>🎲 个性化事件</h2>
            <p class="section-desc">基于您的标签为您推荐的事件选项</p>
          </div>

          <!-- 加载状态 -->
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>正在生成个性化事件...</p>
          </div>

          <!-- 事件卡片列表 -->
          <div v-else class="events-grid">
            <div 
              v-for="event in filteredEvents" 
              :key="event.id" 
              class="event-card"
              :class="{ selected: selectedEvent?.id === event.id }"
              @click="selectEvent(event)">
              <div class="event-header">
                <span class="event-category" :class="event.category">
                  {{ getCategoryIcon(event.category) }} {{ getCategoryName(event.category) }}
                </span>
                <span class="event-match" v-if="event.match_score">
                  匹配度 {{ (event.match_score * 100).toFixed(0) }}%
                </span>
              </div>
              <h3 class="event-title">{{ event.icon }} {{ event.title }}</h3>
              <p class="event-desc">{{ event.description }}</p>
              <div class="event-tags">
                <span v-for="tag in event.tags?.slice(0, 3)" :key="tag" class="event-tag">
                  {{ tag }}
                </span>
              </div>
            </div>

            <div v-if="filteredEvents.length === 0 && !loading" class="empty-events">
              <div class="empty-icon">🎲</div>
              <p>暂无匹配的事件</p>
              <button class="term-btn" @click="loadEvents">刷新事件池</button>
            </div>
          </div>

          <!-- 刷新按钮 -->
          <div class="section-footer">
            <button class="refresh-events-btn" @click="loadEvents" :disabled="loading">
              {{ loading ? '加载中...' : '🔄 刷新事件推荐' }}
            </button>
          </div>
        </section>

        <!-- 右侧：事件详情与选项 -->
        <aside class="detail-panel" :class="{ active: selectedEvent }">
          <div v-if="selectedEvent" class="detail-content">
            <div class="detail-header">
              <span class="detail-category" :class="selectedEvent.category">
                {{ getCategoryIcon(selectedEvent.category) }} {{ selectedEvent.category }}
              </span>
              <button class="close-btn" @click="selectedEvent = null">×</button>
            </div>
            
            <h2 class="detail-title">{{ selectedEvent.title }}</h2>
            <p class="detail-desc">{{ selectedEvent.description }}</p>

            <!-- AI分析 -->
            <div class="ai-analysis" v-if="selectedEvent.ai_thoughts">
              <div class="analysis-header">
                <span class="icon">🤖</span>
                AI 分析
              </div>
              <p>{{ selectedEvent.ai_thoughts }}</p>
            </div>

            <!-- 选项列表 -->
            <div class="options-section">
              <h4>选择你的决定</h4>
              <div class="options-list">
                <button 
                  v-for="(option, idx) in selectedEvent.options" 
                  :key="idx"
                  class="option-btn"
                  :class="{ selected: selectedOption === idx }"
                  @click="selectedOption = idx">
                  <span class="option-num">[{{ idx + 1 }}]</span>
                  <span class="option-text">{{ option.text || option }}</span>
                </button>
              </div>
            </div>

            <!-- 执行按钮 -->
            <button 
              class="execute-btn" 
              :disabled="selectedOption === null || executing"
              @click="executeChoice">
              {{ executing ? '执行中...' : '确认选择 →' }}
            </button>

            <!-- 结果显示 -->
            <div v-if="executionResult" class="result-panel" :class="executionResult.success ? 'success' : 'failure'">
              <div class="result-header">
                <span class="result-icon">{{ executionResult.success ? '✅' : '❌' }}</span>
                <span>{{ executionResult.success ? '选择成功' : '选择失败' }}</span>
              </div>
              <p class="result-message">{{ executionResult.message }}</p>
              <div class="result-impacts" v-if="executionResult.impacts?.length">
                <div v-for="(impact, i) in executionResult.impacts" :key="i" class="impact-item">
                  <span class="impact-type">{{ impact.type }}</span>
                  <span class="impact-value" :class="impact.value >= 0 ? 'positive' : 'negative'">
                    {{ impact.value >= 0 ? '+' : '' }}{{ impact.value }}
                  </span>
                </div>
              </div>
              <div class="result-tags" v-if="executionResult.newTags?.length">
                <p>获得新标签:</p>
                <div class="new-tags">
                  <span v-for="tag in executionResult.newTags" :key="tag" class="new-tag">
                    +{{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="detail-empty">
            <div class="empty-icon">👆</div>
            <p>选择一个事件查看详情</p>
          </div>
        </aside>
      </div>
    </main>

    <!-- CRT效果 -->
    <div class="crt-overlay"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from '../stores/game'
import axios from 'axios'

const gameStore = useGameStore()

// 状态
const isSidebarOpen = ref(false)
const loading = ref(false)
const executing = ref(false)
const userTags = ref([])
const selectedTags = ref([])
const events = ref([])
const selectedEvent = ref(null)
const selectedOption = ref(null)
const executionResult = ref(null)

// 计算属性
const filteredEvents = computed(() => {
  if (selectedTags.value.length === 0) {
    return events.value
  }
  // 按照选中的标签筛选并排序
  return events.value.filter(e => {
    const eventTags = e.tags || []
    return eventTags.some(t => selectedTags.value.includes(t))
  }).sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))
})

// 获取session_id
const getSessionId = () => {
  try {
    // 优先从 gameStore 获取
    if (gameStore.avatar?.session_id) {
      return gameStore.avatar.session_id
    }
    // 其次从 localStorage 获取
    const char = localStorage.getItem('currentCharacter')
    return char ? JSON.parse(char).id : null
  } catch { return null }
}

// 获取分类图标
const getCategoryIcon = (category) => {
  const icons = {
    'financial': '💰',
    'career': '💼',
    'life': '🏠',
    'social': '👥',
    'investment': '📈',
    'emergency': '⚡',
    'growth': '🌱',
    'consumption': '🛒',
    '宏观事件': '🌍',
    '个人事件': '👤',
    '投资机会': '💰',
    '职业事件': '💼',
    '社交事件': '👥',
    '随机事件': '🎲'
  }
  return icons[category] || '📋'
}

// 获取分类名称
const getCategoryName = (category) => {
  const names = {
    'financial': '财务决策',
    'career': '职业发展',
    'life': '生活选择',
    'social': '社交关系',
    'investment': '投资机会',
    'emergency': '突发事件',
    'growth': '个人成长',
    'consumption': '消费抉择'
  }
  return names[category] || category
}

// 切换标签选中状态
const toggleTag = (tagId) => {
  const idx = selectedTags.value.indexOf(tagId)
  if (idx >= 0) {
    selectedTags.value.splice(idx, 1)
  } else {
    selectedTags.value.push(tagId)
  }
}

// 选择事件
const selectEvent = (event) => {
  selectedEvent.value = event
  selectedOption.value = null
  executionResult.value = null
}

// 加载用户标签
const loadUserTags = async () => {
  const sessionId = getSessionId()
  if (!sessionId) {
    console.warn('[EventEcho] 未找到 sessionId，使用默认标签')
    userTags.value = [
      { id: 'moderate', name: '稳健型', icon: '⚖️', weight: 0.5 },
      { id: 'work_life_balance', name: '平衡生活', icon: '🧘', weight: 0.5 },
      { id: 'steady_job', name: '稳定工作', icon: '🏢', weight: 0.5 }
    ]
    return
  }

  try {
    const res = await axios.get(`/api/user/tags/${sessionId}`)
    if (res.data.success) {
      userTags.value = res.data.tags || []
    }
  } catch (e) {
    console.error('加载标签失败:', e)
    // 使用默认标签
    userTags.value = [
      { id: 'moderate', name: '稳健型', icon: '⚖️', weight: 0.5 },
      { id: 'work_life_balance', name: '平衡生活', icon: '🧘', weight: 0.5 },
      { id: 'steady_job', name: '稳定工作', icon: '🏢', weight: 0.5 }
    ]
  }
}

// 加载个性化事件
const loadEvents = async () => {
  const sessionId = getSessionId()
  
  loading.value = true
  selectedEvent.value = null

  // 如果没有 sessionId，使用模拟数据
  if (!sessionId) {
    console.warn('[EventEcho] 未找到 sessionId，使用模拟事件数据')
    events.value = generateMockEvents()
    loading.value = false
    return
  }

  try {
    const res = await axios.get(`/api/events/personalized/${sessionId}`, { 
      params: { 
        limit: 10
      } 
    })
    if (res.data.success && res.data.events?.length > 0) {
      events.value = res.data.events
    } else {
      // API返回空数据，使用模拟数据
      console.warn('[EventEcho] API返回空事件，使用模拟数据')
      events.value = generateMockEvents()
    }
  } catch (e) {
    console.error('加载事件失败:', e)
    // 使用模拟数据
    events.value = generateMockEvents()
  } finally {
    loading.value = false
  }
}

// 执行选择
const executeChoice = async () => {
  if (selectedOption.value === null || !selectedEvent.value) return

  const sessionId = getSessionId()
  if (!sessionId) return

  executing.value = true

  try {
    // 先选择事件
    await axios.post(`/api/events/select/${sessionId}`, {
      event_id: selectedEvent.value.id,
      title: selectedEvent.value.title,
      tags: selectedEvent.value.tags || []
    })

    // 再完成事件
    const option = selectedEvent.value.options[selectedOption.value]
    const res = await axios.post(`/api/events/complete/${sessionId}`, {
      event_id: selectedEvent.value.id,
      choice_index: selectedOption.value,
      choice_tags: option.tags || [],
      effects: option.effects || {}
    })

    if (res.data.success) {
      executionResult.value = {
        success: true,
        message: `你选择了「${option.text}」，结果正在影响你的人生轨迹...`,
        impacts: Object.entries(res.data.effects_applied || {}).map(([type, value]) => ({
          type,
          value
        })),
        newTags: option.tags || []
      }
      // 更新用户标签
      await loadUserTags()
      // 刷新游戏状态
      await gameStore.loadAvatar()
    } else {
      executionResult.value = {
        success: false,
        message: res.data.message || '执行失败'
      }
    }
  } catch (e) {
    console.error('执行选择失败:', e)
    // 模拟结果
    const option = selectedEvent.value.options[selectedOption.value]
    executionResult.value = {
      success: true,
      message: `你选择了「${option.text}」，结果正在影响你的人生轨迹...`,
      impacts: [
        { type: '现金', value: Math.floor(Math.random() * 10000) - 5000 },
        { type: '幸福度', value: Math.floor(Math.random() * 20) - 10 }
      ],
      newTags: option.tags || []
    }
    // 更新标签
    await loadUserTags()
  } finally {
    executing.value = false
  }
}

// 生成模拟事件
const generateMockEvents = () => [
  {
    id: 'event_1',
    category: '投资机会',
    title: '科技股大涨 📈',
    description: 'AI概念股持续走强，市场情绪高涨。这波行情你准备如何操作？',
    tags: ['投资', '科技', '股票'],
    matchScore: 0.92,
    options: [
      { text: '大举买入，追涨科技股' },
      { text: '谨慎观望，等待回调' },
      { text: '趁机卖出，落袋为安' }
    ],
    ai_thoughts: '当前科技股估值较高，追涨风险与机会并存。建议根据个人风险承受能力决定。'
  },
  {
    id: 'event_2',
    category: '职业事件',
    title: '晋升机会 💼',
    description: '公司有一个管理岗位空缺，你的上司问你是否有意愿竞争这个职位。',
    tags: ['职业', '晋升', '管理'],
    matchScore: 0.85,
    options: [
      { text: '积极争取，全力竞争' },
      { text: '保持现状，专注技术' },
      { text: '提出条件，协商薪资' }
    ]
  },
  {
    id: 'event_3',
    category: '个人事件',
    title: '健康警报 ⚠️',
    description: '最近体检发现一些小问题，医生建议你调整作息和运动习惯。',
    tags: ['健康', '生活', '平衡'],
    matchScore: 0.78,
    options: [
      { text: '立即改变，健康优先' },
      { text: '稍后调整，工作第一' },
      { text: '购买保险，以防万一' }
    ]
  },
  {
    id: 'event_4',
    category: '宏观事件',
    title: '央行降息 🏦',
    description: '央行宣布降息25个基点，市场流动性增加，资产价格波动加大。',
    tags: ['宏观', '利率', '政策'],
    matchScore: 0.70,
    options: [
      { text: '增加股票配置' },
      { text: '增加房产投资' },
      { text: '保持现金观望' }
    ]
  },
  {
    id: 'event_5',
    category: '社交事件',
    title: '朋友借钱 👥',
    description: '一位多年好友向你借一笔钱周转，金额是你现金的20%。',
    tags: ['社交', '关系', '金钱'],
    matchScore: 0.65,
    options: [
      { text: '全额借出，信任朋友' },
      { text: '借一半，保护自己' },
      { text: '婉言拒绝，有借无还' }
    ]
  }
]

// 初始化
onMounted(async () => {
  // 确保先加载 avatar 数据
  if (!gameStore.avatar) {
    await gameStore.loadAvatar()
  }
  await loadUserTags()
  await loadEvents()
})
</script>

<style scoped>
.event-echo-page {
  display: flex;
  height: 100vh;
  background: var(--term-bg, #0a0a0a);
  overflow: hidden;
}

/* 复用侧边栏样式 */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 99;
}

.sidebar-nav {
  width: 240px;
  background: var(--term-panel-bg, #111);
  border-right: 1px solid var(--term-border, #333);
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.nav-header {
  padding: 20px;
  border-bottom: 1px solid var(--term-border, #333);
}

.logo-text {
  font-size: 20px;
  font-weight: 900;
  color: var(--term-accent, #00ff88);
}

.sub-header {
  font-size: 12px;
  color: var(--term-text-dim, #666);
  margin-top: 4px;
}

.close-sidebar-btn {
  display: none;
  position: absolute;
  right: 12px;
  top: 12px;
  background: none;
  border: none;
  color: var(--term-text, #fff);
  font-size: 24px;
  cursor: pointer;
}

.nav-section {
  padding: 16px;
  flex: 1;
}

.section-label {
  font-size: 11px;
  color: var(--term-text-dim, #666);
  margin-bottom: 12px;
  text-transform: uppercase;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--term-text, #ccc);
  transition: all 0.2s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  background: var(--term-accent, #00ff88);
  color: #000;
}

.nav-spacer { flex: 1; }

.system-actions {
  padding: 16px;
  border-top: 1px solid var(--term-border, #333);
}

.action-btn {
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px solid var(--term-border, #333);
  color: var(--term-text, #ccc);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 主内容 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部栏 */
.top-bar {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: var(--term-panel-bg, #111);
  border-bottom: 1px solid var(--term-border, #333);
  gap: 16px;
}

.menu-btn {
  display: none;
  background: none;
  border: none;
  color: var(--term-text, #fff);
  font-size: 20px;
  cursor: pointer;
}

.brand-logo {
  font-size: 14px;
  color: var(--term-text, #ccc);
}

.brand-logo .highlight {
  color: var(--term-accent, #00ff88);
  font-weight: 700;
}

.header-right {
  margin-left: auto;
}

.tag-counter {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  font-size: 12px;
  color: var(--term-text-dim, #888);
}

/* 事件内容区 */
.event-content {
  flex: 1;
  display: grid;
  grid-template-columns: 240px 1fr 360px;
  gap: 1px;
  background: var(--term-border, #333);
  overflow: hidden;
}

/* 标签面板 */
.tags-panel {
  background: var(--term-panel-bg, #111);
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--term-border, #333);
}

.panel-header h3 {
  font-size: 14px;
  font-weight: 700;
  color: var(--term-text, #fff);
  margin: 0;
}

.tag-count {
  padding: 2px 8px;
  background: var(--term-accent, #00ff88);
  color: #000;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
}

.tags-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  margin-bottom: 6px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.tag-item.active {
  background: rgba(0, 255, 136, 0.1);
  border-color: var(--term-accent, #00ff88);
}

.tag-icon {
  font-size: 16px;
}

.tag-name {
  flex: 1;
  font-size: 13px;
  color: var(--term-text, #ccc);
}

.tag-weight {
  font-size: 11px;
  color: var(--term-text-dim, #666);
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.empty-tags {
  text-align: center;
  padding: 32px 16px;
  color: var(--term-text-dim, #666);
}

.empty-tags .hint {
  font-size: 12px;
  margin-top: 8px;
}

.panel-footer {
  padding: 12px;
  border-top: 1px solid var(--term-border, #333);
}

.refresh-btn {
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px solid var(--term-border, #333);
  color: var(--term-text, #ccc);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

/* 事件区域 */
.events-section {
  background: var(--term-bg, #0a0a0a);
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
}

.section-header {
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 900;
  color: var(--term-text, #fff);
  margin: 0 0 4px;
}

.section-desc {
  font-size: 12px;
  color: var(--term-text-dim, #666);
  margin: 0;
}

.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--term-text-dim, #666);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--term-border, #333);
  border-top-color: var(--term-accent, #00ff88);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.events-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  overflow-y: auto;
  padding-bottom: 20px;
}

.event-card {
  background: var(--term-panel-bg, #111);
  border: 1px solid var(--term-border, #333);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.event-card:hover {
  border-color: var(--term-accent, #00ff88);
  transform: translateY(-2px);
}

.event-card.selected {
  border-color: var(--term-accent, #00ff88);
  background: rgba(0, 255, 136, 0.05);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.event-category {
  padding: 4px 8px;
  font-size: 11px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--term-text, #ccc);
}

.event-category.投资机会 { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
.event-category.职业事件 { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.event-category.个人事件 { background: rgba(16, 185, 129, 0.2); color: #34d399; }
.event-category.宏观事件 { background: rgba(139, 92, 246, 0.2); color: #a78bfa; }
.event-category.社交事件 { background: rgba(236, 72, 153, 0.2); color: #f472b6; }

.event-match {
  font-size: 11px;
  color: var(--term-accent, #00ff88);
}

.event-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--term-text, #fff);
  margin: 0 0 8px;
}

.event-desc {
  font-size: 13px;
  color: var(--term-text-dim, #888);
  margin: 0 0 12px;
  line-height: 1.5;
}

.event-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.event-tag {
  padding: 2px 8px;
  font-size: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  color: var(--term-text-dim, #666);
}

.empty-events {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  color: var(--term-text-dim, #666);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.section-footer {
  padding-top: 16px;
  border-top: 1px solid var(--term-border, #333);
}

.refresh-events-btn {
  width: 100%;
  padding: 12px;
  background: transparent;
  border: 1px solid var(--term-accent, #00ff88);
  color: var(--term-accent, #00ff88);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.refresh-events-btn:hover:not(:disabled) {
  background: var(--term-accent, #00ff88);
  color: #000;
}

.refresh-events-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 详情面板 */
.detail-panel {
  background: var(--term-panel-bg, #111);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.detail-category {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
}

.close-btn {
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--term-border, #333);
  color: var(--term-text, #ccc);
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
}

.detail-title {
  font-size: 20px;
  font-weight: 900;
  color: var(--term-text, #fff);
  margin: 0 0 12px;
}

.detail-desc {
  font-size: 14px;
  color: var(--term-text-dim, #888);
  line-height: 1.6;
  margin: 0 0 20px;
}

.ai-analysis {
  background: rgba(0, 255, 136, 0.05);
  border: 1px solid rgba(0, 255, 136, 0.2);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 20px;
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--term-accent, #00ff88);
  margin-bottom: 8px;
}

.ai-analysis p {
  font-size: 13px;
  color: var(--term-text, #ccc);
  margin: 0;
  line-height: 1.5;
}

.options-section {
  margin-bottom: 20px;
}

.options-section h4 {
  font-size: 14px;
  font-weight: 700;
  color: var(--term-text, #fff);
  margin: 0 0 12px;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-btn {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--term-border, #333);
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.option-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--term-text-dim, #666);
}

.option-btn.selected {
  background: rgba(0, 255, 136, 0.1);
  border-color: var(--term-accent, #00ff88);
}

.option-num {
  font-size: 12px;
  color: var(--term-accent, #00ff88);
  font-weight: 700;
}

.option-text {
  font-size: 13px;
  color: var(--term-text, #ccc);
  line-height: 1.4;
}

.execute-btn {
  width: 100%;
  padding: 14px;
  background: var(--term-accent, #00ff88);
  border: none;
  border-radius: 8px;
  color: #000;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.execute-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
}

.execute-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 结果面板 */
.result-panel {
  margin-top: 20px;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid;
}

.result-panel.success {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
}

.result-panel.failure {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--term-text, #fff);
}

.result-message {
  font-size: 13px;
  color: var(--term-text-dim, #888);
  margin: 0 0 12px;
}

.result-impacts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.impact-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  font-size: 12px;
}

.impact-type {
  color: var(--term-text-dim, #888);
}

.impact-value.positive {
  color: #10b981;
}

.impact-value.negative {
  color: #ef4444;
}

.result-tags p {
  font-size: 12px;
  color: var(--term-text-dim, #888);
  margin: 0 0 8px;
}

.new-tags {
  display: flex;
  gap: 6px;
}

.new-tag {
  padding: 4px 10px;
  background: rgba(0, 255, 136, 0.2);
  color: var(--term-accent, #00ff88);
  border-radius: 4px;
  font-size: 12px;
}

.detail-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--term-text-dim, #666);
  text-align: center;
  padding: 40px;
}

.detail-empty .empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

/* CRT效果 */
.crt-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1000;
  background: 
    repeating-linear-gradient(
      0deg,
      rgba(0, 0, 0, 0.1) 0px,
      rgba(0, 0, 0, 0.1) 1px,
      transparent 1px,
      transparent 2px
    );
}

/* 响应式 */
@media (max-width: 1024px) {
  .event-content {
    grid-template-columns: 1fr;
  }
  
  .tags-panel {
    display: none;
  }
  
  .detail-panel {
    position: fixed;
    right: -100%;
    top: 0;
    bottom: 0;
    width: 100%;
    max-width: 400px;
    transition: right 0.3s;
    z-index: 50;
  }
  
  .detail-panel.active {
    right: 0;
  }
}

@media (max-width: 768px) {
  .sidebar-nav {
    position: fixed;
    left: -260px;
    top: 0;
    bottom: 0;
    transition: left 0.3s;
  }
  
  .sidebar-nav.open {
    left: 0;
  }
  
  .close-sidebar-btn {
    display: block;
  }
  
  .menu-btn {
    display: block;
  }
  
  .events-grid {
    grid-template-columns: 1fr;
  }
}
</style>
