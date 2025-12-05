<template>
  <div class="personal-center">
    <!-- 移动端侧边栏遮罩 -->
    <div class="sidebar-overlay" v-if="isSidebarOpen" @click="isSidebarOpen = false"></div>

    <!-- 左侧导航栏 -->
    <nav class="sidebar-nav" :class="{ open: isSidebarOpen }">
      <div class="nav-header">
        <div class="logo-text">EchoPolis</div>
        <div class="sub-header">// 个人中心</div>
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

      <!-- 子导航 -->
      <div class="nav-section sub-nav">
        <div class="section-label">个人中心</div>
        
        <div 
          :class="['nav-item sub', { active: activeTab === 'profile' }]"
          @click="activeTab = 'profile'">
          <span class="icon">📋</span>
          个人档案
        </div>
        
        <div 
          :class="['nav-item sub', { active: activeTab === 'archives' }]"
          @click="activeTab = 'archives'">
          <span class="icon">📖</span>
          系统档案
        </div>
        
        <div 
          :class="['nav-item sub', { active: activeTab === 'leaderboard' }]"
          @click="activeTab = 'leaderboard'">
          <span class="icon">🏆</span>
          排行榜
        </div>
        
        <div 
          :class="['nav-item sub', { active: activeTab === 'achievements' }]"
          @click="activeTab = 'achievements'">
          <span class="icon">🎖️</span>
          成就系统
        </div>
        
        <div 
          :class="['nav-item sub', { active: activeTab === 'tags' }]"
          @click="activeTab = 'tags'">
          <span class="icon">🏷️</span>
          用户标签
        </div>
        
        <div 
          :class="['nav-item sub', { active: activeTab === 'insights' }]"
          @click="activeTab = 'insights'">
          <span class="icon">🧠</span>
          行为洞察
        </div>
      </div>

      <div class="nav-spacer"></div>

      <div class="system-actions">
        <button class="action-btn" @click="showSettings = true">
          <span class="icon">⚙️</span>
          <span class="label">设置</span>
        </button>
        <button class="action-btn danger" @click="logout">
          <span class="icon">🔌</span>
          <span class="label">登出</span>
        </button>
      </div>
    </nav>

    <!-- 设置面板 -->
    <SettingsPanel 
      :isOpen="showSettings" 
      @close="showSettings = false"
    />

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部状态栏 -->
      <header class="top-bar">
        <button class="menu-btn" @click="isSidebarOpen = true">☰</button>
        
        <div class="brand-logo">
          <span class="highlight">EchoPolis</span> // {{ getTabTitle(activeTab) }}
        </div>
        
        <div class="header-right">
          <div class="user-info">
            <span class="user-name">{{ avatar?.name || 'User' }}</span>
            <span class="user-tag">{{ avatar?.mbti_type || 'INTJ' }}</span>
          </div>
        </div>
      </header>

      <!-- 内容区域 -->
      <div class="content-area">
        <!-- 个人档案 -->
        <div v-if="activeTab === 'profile'" class="tab-content">
          <ProfileView />
        </div>

        <!-- 系统档案 -->
        <div v-if="activeTab === 'archives'" class="tab-content">
          <ArchivesView />
        </div>

        <!-- 排行榜 -->
        <div v-if="activeTab === 'leaderboard'" class="tab-content">
          <LeaderboardView />
        </div>

        <!-- 成就系统 -->
        <div v-if="activeTab === 'achievements'" class="tab-content">
          <AchievementView />
        </div>

        <!-- 用户标签 -->
        <div v-if="activeTab === 'tags'" class="tab-content">
          <div class="tags-view">
            <div class="view-header">
              <h2>用户标签 // USER_TAGS</h2>
              <div class="header-line"></div>
            </div>
            
            <div class="tags-content">
              <!-- 标签统计 -->
              <div class="tags-stats">
                <div class="stat-card">
                  <div class="stat-icon">🏷️</div>
                  <div class="stat-info">
                    <div class="stat-value">{{ userTags.length }}</div>
                    <div class="stat-label">总标签数</div>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-icon">⭐</div>
                  <div class="stat-info">
                    <div class="stat-value">{{ topTags.length }}</div>
                    <div class="stat-label">高权重标签</div>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-icon">📈</div>
                  <div class="stat-info">
                    <div class="stat-value">{{ recentTags.length }}</div>
                    <div class="stat-label">近期获得</div>
                  </div>
                </div>
              </div>

              <!-- 标签分类 -->
              <div class="tags-categories">
                <div class="category-section" v-for="category in tagCategories" :key="category.id">
                  <div class="category-header">
                    <span class="category-icon">{{ category.icon }}</span>
                    <span class="category-name">{{ category.name }}</span>
                    <span class="category-count">{{ getCategoryTags(category.id).length }}</span>
                  </div>
                  <div class="category-tags">
                    <div 
                      v-for="tag in getCategoryTags(category.id)" 
                      :key="tag.id" 
                      class="tag-chip"
                      :class="{ 'high-weight': tag.weight > 0.7 }">
                      <span class="tag-icon">{{ tag.icon }}</span>
                      <span class="tag-name">{{ tag.name }}</span>
                      <span class="tag-weight">{{ (tag.weight * 100).toFixed(0) }}%</span>
                    </div>
                    <div v-if="getCategoryTags(category.id).length === 0" class="empty-hint">
                      暂无此类标签
                    </div>
                  </div>
                </div>
              </div>

              <!-- 标签说明 -->
              <div class="tags-info">
                <h4>标签说明</h4>
                <p>用户标签基于您的游戏行为自动生成，用于个性化事件推荐。</p>
                <ul>
                  <li>标签权重越高，相关事件推荐概率越大</li>
                  <li>您的每次选择都会影响标签权重</li>
                  <li>标签会随时间自然衰减</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 行为洞察 -->
        <div v-if="activeTab === 'insights'" class="tab-content">
          <InsightsView />
        </div>
      </div>
    </main>

    <!-- CRT效果 -->
    <div class="crt-overlay"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'
import SettingsPanel from '../components/SettingsPanel.vue'
import ProfileView from '../components/views/ProfileView.vue'
import ArchivesView from '../components/views/ArchivesView.vue'
import LeaderboardView from '../components/views/LeaderboardView.vue'
import AchievementView from '../components/views/AchievementView.vue'
import InsightsView from '../components/views/InsightsView.vue'
import axios from 'axios'

const router = useRouter()
const gameStore = useGameStore()

// 状态
const isSidebarOpen = ref(false)
const showSettings = ref(false)
const activeTab = ref('profile')
const userTags = ref([])

// 标签分类
const tagCategories = [
  { id: 'investment', name: '投资偏好', icon: '📈' },
  { id: 'risk', name: '风险态度', icon: '🎲' },
  { id: 'lifestyle', name: '生活方式', icon: '🏠' },
  { id: 'career', name: '职业倾向', icon: '💼' },
  { id: 'social', name: '社交特征', icon: '👥' },
  { id: 'other', name: '其他标签', icon: '🏷️' }
]

// 计算属性
const avatar = computed(() => gameStore.avatar)

const topTags = computed(() => 
  userTags.value.filter(t => t.weight > 0.7).sort((a, b) => b.weight - a.weight)
)

const recentTags = computed(() => 
  userTags.value.filter(t => t.isRecent).slice(0, 5)
)

// 方法
const getTabTitle = (tab) => {
  const titles = {
    profile: '个人档案',
    archives: '系统档案',
    leaderboard: '排行榜',
    achievements: '成就系统',
    tags: '用户标签',
    insights: '行为洞察'
  }
  return titles[tab] || '个人中心'
}

const getCategoryTags = (categoryId) => {
  return userTags.value.filter(t => t.category === categoryId)
}

const getSessionId = () => {
  try {
    const char = localStorage.getItem('currentCharacter')
    return char ? JSON.parse(char).id : null
  } catch { return null }
}

const loadUserTags = async () => {
  const sessionId = getSessionId()
  if (!sessionId) return

  try {
    const res = await axios.get(`/api/user/tags/${sessionId}`)
    if (res.data.success) {
      userTags.value = res.data.tags || []
    }
  } catch (e) {
    console.error('加载标签失败:', e)
    // 使用模拟数据
    userTags.value = [
      { id: 'moderate', name: '稳健型', icon: '⚖️', category: 'risk', weight: 0.65, isRecent: false },
      { id: 'tech_investor', name: '科技投资者', icon: '💻', category: 'investment', weight: 0.78, isRecent: true },
      { id: 'long_term', name: '长期主义', icon: '⏰', category: 'investment', weight: 0.72, isRecent: false },
      { id: 'career_focused', name: '事业导向', icon: '💼', category: 'career', weight: 0.68, isRecent: false },
      { id: 'conservative', name: '保守型', icon: '🛡️', category: 'risk', weight: 0.45, isRecent: false },
      { id: 'social_active', name: '社交活跃', icon: '👥', category: 'social', weight: 0.62, isRecent: true },
      { id: 'health_conscious', name: '注重健康', icon: '🏃', category: 'lifestyle', weight: 0.55, isRecent: false },
      { id: 'diversified', name: '分散投资', icon: '🎨', category: 'investment', weight: 0.70, isRecent: true }
    ]
  }
}

const logout = () => {
  localStorage.removeItem('currentCharacter')
  localStorage.removeItem('session_id')
  router.push('/character-select')
}

// 初始化
onMounted(async () => {
  await gameStore.loadAvatar()
  await loadUserTags()
})
</script>

<style scoped>
.personal-center {
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
  overflow-y: auto;
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
}

.nav-section.sub-nav {
  border-top: 1px solid var(--term-border, #333);
}

.section-label {
  font-size: 11px;
  color: var(--term-text-dim, #666);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
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

.nav-item.sub {
  padding: 10px 12px;
  font-size: 13px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  background: var(--term-accent, #00ff88);
  color: #000;
}

.nav-item .icon {
  font-size: 16px;
}

.nav-spacer { flex: 1; }

.system-actions {
  padding: 16px;
  border-top: 1px solid var(--term-border, #333);
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 10px;
  background: transparent;
  border: 1px solid var(--term-border, #333);
  color: var(--term-text, #ccc);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}

.action-btn.danger:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
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

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--term-text, #fff);
}

.user-tag {
  padding: 4px 8px;
  background: var(--term-accent, #00ff88);
  color: #000;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
}

/* 内容区域 */
.content-area {
  flex: 1;
  overflow: hidden;
}

.tab-content {
  height: 100%;
  overflow: auto;
}

/* 用户标签视图 */
.tags-view {
  padding: 24px;
  max-width: 1200px;
}

.view-header h2 {
  font-size: 24px;
  font-weight: 900;
  color: var(--term-text, #fff);
  margin: 0 0 8px;
}

.header-line {
  height: 2px;
  background: var(--term-border, #333);
  margin-bottom: 24px;
}

.tags-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 标签统计 */
.tags-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--term-panel-bg, #111);
  border: 1px solid var(--term-border, #333);
  border-radius: 12px;
}

.stat-icon {
  font-size: 32px;
}

.stat-value {
  font-size: 28px;
  font-weight: 900;
  color: var(--term-accent, #00ff88);
}

.stat-label {
  font-size: 12px;
  color: var(--term-text-dim, #666);
}

/* 标签分类 */
.tags-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.category-section {
  background: var(--term-panel-bg, #111);
  border: 1px solid var(--term-border, #333);
  border-radius: 12px;
  overflow: hidden;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid var(--term-border, #333);
}

.category-icon {
  font-size: 18px;
}

.category-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--term-text, #fff);
  flex: 1;
}

.category-count {
  padding: 2px 8px;
  background: var(--term-accent, #00ff88);
  color: #000;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
}

.category-tags {
  padding: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--term-border, #333);
  border-radius: 20px;
  transition: all 0.2s;
}

.tag-chip.high-weight {
  background: rgba(0, 255, 136, 0.1);
  border-color: rgba(0, 255, 136, 0.3);
}

.tag-chip .tag-icon {
  font-size: 14px;
}

.tag-chip .tag-name {
  font-size: 13px;
  color: var(--term-text, #ccc);
}

.tag-chip .tag-weight {
  font-size: 11px;
  color: var(--term-accent, #00ff88);
  padding: 2px 6px;
  background: rgba(0, 255, 136, 0.1);
  border-radius: 4px;
}

.empty-hint {
  font-size: 13px;
  color: var(--term-text-dim, #666);
  padding: 8px;
}

/* 标签说明 */
.tags-info {
  background: var(--term-panel-bg, #111);
  border: 1px solid var(--term-border, #333);
  border-radius: 12px;
  padding: 20px;
}

.tags-info h4 {
  font-size: 14px;
  font-weight: 700;
  color: var(--term-text, #fff);
  margin: 0 0 8px;
}

.tags-info p {
  font-size: 13px;
  color: var(--term-text-dim, #888);
  margin: 0 0 12px;
}

.tags-info ul {
  margin: 0;
  padding-left: 20px;
}

.tags-info li {
  font-size: 12px;
  color: var(--term-text-dim, #666);
  margin-bottom: 4px;
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
  
  .tags-categories {
    grid-template-columns: 1fr;
  }
}
</style>
