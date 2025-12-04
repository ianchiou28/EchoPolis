<template>
  <div class="view-container">
    <div class="view-header">
      <h2>行为洞察 // BEHAVIOR_INSIGHTS</h2>
      <div class="header-line"></div>
    </div>

    <!-- 标签页导航 -->
    <div class="tabs-nav">
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'personal' }"
        @click="activeTab = 'personal'">
        📊 个人画像
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'statistics' }"
        @click="activeTab = 'statistics'; loadStatistics()">
        📈 行为统计
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'ai' }"
        @click="activeTab = 'ai'">
        🤖 AI洞察
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'cohort' }"
        @click="activeTab = 'cohort'">
        👥 群体洞察
      </button>
      <button 
        class="tab-btn warning-tab" 
        :class="{ active: activeTab === 'warnings' }"
        @click="activeTab = 'warnings'; loadWarnings()">
        ⚠️ 预警
        <span v-if="warningStats.critical > 0" class="warning-badge critical">
          {{ warningStats.critical }}
        </span>
        <span v-else-if="warningStats.total > 0" class="warning-badge">
          {{ warningStats.total }}
        </span>
      </button>
    </div>

    <!-- 个人画像标签页 -->
    <div v-if="activeTab === 'personal'" class="insights-content">
      <div v-if="loading" class="loading-state">
        <div class="scanline-loader">分析行为数据中...</div>
      </div>

      <div v-else-if="personalData && personalData.profile" class="content-grid">
        <!-- 左列：行为画像 -->
        <div class="col-left">
          <div class="archive-card">
            <div class="archive-header">行为画像</div>
            <div class="archive-body">
              <div class="profile-grid">
                <div class="profile-item">
                  <span class="item-label">风险偏好</span>
                  <span class="item-value" :class="`risk-${personalData.profile.risk_preference}`">
                    {{ getRiskLabel(personalData.profile.risk_preference) }}
                  </span>
                </div>
                <div class="profile-item">
                  <span class="item-label">决策风格</span>
                  <span class="item-value">{{ getStyleLabel(personalData.profile.decision_style) }}</span>
                </div>
              </div>
              
              <div class="profile-bars">
                <div class="bar-item">
                  <div class="bar-label">
                    <span>损失厌恶</span>
                    <span>{{ (personalData.profile.loss_aversion * 100).toFixed(0) }}%</span>
                  </div>
                  <div class="bar-track">
                    <div class="bar-fill" :style="{ width: (personalData.profile.loss_aversion * 100) + '%' }"></div>
                  </div>
                </div>
                <div class="bar-item">
                  <div class="bar-label">
                    <span>过度自信</span>
                    <span>{{ (personalData.profile.overconfidence * 100).toFixed(0) }}%</span>
                  </div>
                  <div class="bar-track">
                    <div class="bar-fill warning" :style="{ width: (personalData.profile.overconfidence * 100) + '%' }"></div>
                  </div>
                </div>
                <div class="bar-item">
                  <div class="bar-label">
                    <span>羊群倾向</span>
                    <span>{{ (personalData.profile.herding_tendency * 100).toFixed(0) }}%</span>
                  </div>
                  <div class="bar-track">
                    <div class="bar-fill" :style="{ width: (personalData.profile.herding_tendency * 100) + '%' }"></div>
                  </div>
                </div>
                <div class="bar-item">
                  <div class="bar-label">
                    <span>规划能力</span>
                    <span>{{ (personalData.profile.planning_ability * 100).toFixed(0) }}%</span>
                  </div>
                  <div class="bar-track">
                    <div class="bar-fill success" :style="{ width: (personalData.profile.planning_ability * 100) + '%' }"></div>
                  </div>
                </div>
              </div>
              
              <div class="profile-stats">
                <div class="stat-box">
                  <span class="stat-value">{{ personalData.profile.action_count }}</span>
                  <span class="stat-label">行为记录</span>
                </div>
                <div class="stat-box">
                  <span class="stat-value">{{ (personalData.profile.avg_risk_score * 100).toFixed(0) }}%</span>
                  <span class="stat-label">平均风险</span>
                </div>
                <div class="stat-box">
                  <span class="stat-value">{{ (personalData.profile.avg_rationality * 100).toFixed(0) }}%</span>
                  <span class="stat-label">平均理性</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右列：个性化建议 -->
        <div class="col-right">
          <div v-if="personalData.recommendations && personalData.recommendations.length" class="archive-card flex-grow">
            <div class="archive-header">💡 个性化建议</div>
            <div class="archive-body scrollable">
              <div v-for="(rec, idx) in personalData.recommendations" :key="idx" class="recommendation-item">
                <div class="rec-number">{{ idx + 1 }}</div>
                <div class="rec-text">{{ rec }}</div>
              </div>
            </div>
          </div>
          <div v-else class="archive-card flex-grow">
            <div class="archive-header">💡 个性化建议</div>
            <div class="archive-body">
              <div class="empty-state-small">暂无建议，继续游戏获取更多数据</div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📊</div>
        <div class="empty-text">暂无行为数据</div>
        <div class="empty-hint">继续游戏以生成您的行为画像</div>
      </div>
    </div>

    <!-- 行为统计标签页 -->
    <div v-if="activeTab === 'statistics'" class="insights-content">
      <div v-if="loading" class="loading-state">
        <div class="scanline-loader">加载行为统计...</div>
      </div>
      <div v-else class="empty-state">
        <div class="empty-icon">📊</div>
        <div class="empty-text">暂无统计数据</div>
        <div class="empty-hint">继续游戏以生成行为统计</div>
      </div>
    </div>

    <!-- AI洞察标签页 -->
    <div v-if="activeTab === 'ai'" class="insights-content">
      <div class="ai-insights">
        <div class="insight-card ai-card">
          <div class="card-title">
            <span class="ai-icon">🤖</span>
            AI 个性化分析
          </div>
          
          <div v-if="aiLoading" class="ai-loading">
            <div class="ai-spinner"></div>
            <span>AI 正在分析您的行为数据...</span>
          </div>

          <div v-else-if="aiInsight" class="ai-content">
            <div class="ai-title">{{ aiInsight.title }}</div>
            <div class="ai-summary">{{ aiInsight.summary }}</div>
            <div class="ai-analysis">{{ aiInsight.analysis }}</div>
            
            <div v-if="aiInsight.suggestions && aiInsight.suggestions.length" class="ai-suggestions">
              <div class="suggestions-title">💡 AI建议</div>
              <ul>
                <li v-for="(suggestion, i) in aiInsight.suggestions" :key="i">{{ suggestion }}</li>
              </ul>
            </div>
          </div>

          <div v-else class="ai-empty">
            <p>点击下方按钮获取AI个性化分析报告</p>
            <p class="hint">需要足够的行为数据才能生成分析</p>
          </div>

          <button class="ai-generate-btn" @click="generateAiInsight" :disabled="aiLoading">
            {{ aiLoading ? '分析中...' : '生成AI分析报告' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 群体洞察标签页 -->
    <div v-if="activeTab === 'cohort'" class="insights-content">
      <div v-if="loading" class="loading-state">
        <div class="scanline-loader">加载群体洞察...</div>
      </div>
      <div v-else class="empty-state">
        <div class="empty-icon">🔍</div>
        <div class="empty-text">暂无群体洞察</div>
        <div class="empty-hint">系统将定期生成Z世代行为洞察</div>
      </div>
    </div>

    <!-- 预警标签页 -->
    <div v-if="activeTab === 'warnings'" class="insights-content">
      <div v-if="warningsLoading" class="loading-state">
        <div class="scanline-loader">检测行为风险...</div>
      </div>
      <div v-else class="empty-state safe-state">
        <div class="empty-icon">✅</div>
        <div class="empty-text">当前无风险预警</div>
        <div class="empty-hint">您的财务行为表现良好，继续保持！</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from '@/stores/game'

const gameStore = useGameStore()

// 状态
const activeTab = ref('personal')
const loading = ref(false)
const personalData = ref(null)
const statisticsData = ref(null)
const aiInsight = ref(null)
const aiLoading = ref(false)
const warningsLoading = ref(false)
const warningStats = ref({ total: 0, critical: 0, high: 0, medium: 0, low: 0 })

// 获取 session ID
const getSessionId = () => {
  const character = gameStore.getCurrentCharacter()
  return character?.id || null
}

const sessionId = computed(() => getSessionId())

// 辅助函数
const getRiskLabel = (risk) => {
  const labels = {
    conservative: '保守型',
    moderate: '稳健型',
    aggressive: '激进型'
  }
  return labels[risk] || risk
}

const getStyleLabel = (style) => {
  const labels = {
    rational: '理性规划型',
    impulsive: '冲动跟风型',
    passive: '被动随缘型',
    adaptive: '灵活应变型'
  }
  return labels[style] || style
}

// API 调用
const loadPersonalInsights = async () => {
  if (!sessionId.value) return
  
  loading.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/insights/personal/${sessionId.value}`)
    const result = await response.json()
    if (result.success) {
      personalData.value = result.data
    }
  } catch (error) {
    console.error('Failed to load personal insights:', error)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  if (!sessionId.value) return
  
  loading.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/insights/statistics/${sessionId.value}`)
    const result = await response.json()
    if (result.success) {
      statisticsData.value = result.data
    }
  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    loading.value = false
  }
}

const generateAiInsight = async () => {
  if (!sessionId.value) return
  
  aiLoading.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/insights/ai/${sessionId.value}`)
    const result = await response.json()
    if (result.success) {
      aiInsight.value = result.data
    } else {
      alert(result.error || '无法生成AI洞察')
    }
  } catch (error) {
    console.error('Failed to generate AI insight:', error)
    alert('生成AI洞察失败')
  } finally {
    aiLoading.value = false
  }
}

const loadWarnings = async () => {
  if (!sessionId.value) return
  
  warningsLoading.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/insights/warnings/${sessionId.value}`)
    const result = await response.json()
    if (result.success) {
      warningStats.value = result.stats || { total: 0, critical: 0, high: 0, medium: 0, low: 0 }
    }
  } catch (error) {
    console.error('Failed to load warnings:', error)
  } finally {
    warningsLoading.value = false
  }
}

onMounted(() => {
  loadPersonalInsights()
  loadWarnings()
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
  margin-bottom: 16px;
}

/* 标签页导航 */
.tabs-nav {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 700;
  border: 2px solid var(--term-border);
  background: transparent;
  color: var(--term-text);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  border-color: var(--term-accent);
}

.tab-btn.active {
  background: var(--term-accent);
  border-color: var(--term-accent);
  color: #000;
}

.warning-tab {
  position: relative;
}

.warning-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background: var(--term-accent);
  color: #000;
  border-radius: 9px;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.warning-badge.critical {
  background: #ef4444;
  color: #fff;
}

/* 内容区域 */
.insights-content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  height: 100%;
}

.col-left, .col-right {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.flex-grow { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.scrollable { flex: 1; overflow-y: auto; }

/* Archive Card */
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

/* 画像样式 */
.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.profile-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-label {
  font-size: 11px;
  color: var(--term-text-secondary);
  text-transform: uppercase;
}

.item-value {
  font-size: 16px;
  font-weight: 800;
}

.risk-conservative { color: #10b981; }
.risk-moderate { color: var(--term-accent); }
.risk-aggressive { color: #ef4444; }

/* 进度条 */
.profile-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.bar-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bar-label {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 600;
}

.bar-track {
  height: 8px;
  background: var(--term-border);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: var(--term-accent);
  transition: width 0.5s;
}

.bar-fill.success { background: #10b981; }
.bar-fill.warning { background: #f59e0b; }

/* 统计盒子 */
.profile-stats {
  display: flex;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px dashed var(--term-border);
}

.stat-box {
  flex: 1;
  text-align: center;
  padding: 12px;
  background: rgba(0,0,0,0.02);
  border: 1px solid var(--term-border);
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 900;
}

.stat-label {
  display: block;
  font-size: 10px;
  color: var(--term-text-secondary);
  text-transform: uppercase;
  margin-top: 4px;
}

/* 建议列表 */
.recommendation-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(0,0,0,0.02);
  border: 1px solid var(--term-border);
  margin-bottom: 8px;
}

.rec-number {
  width: 24px;
  height: 24px;
  background: var(--term-accent);
  color: #000;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.rec-text {
  flex: 1;
  font-size: 13px;
  line-height: 1.5;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 13px;
  color: var(--term-text-secondary);
}

.empty-state-small {
  text-align: center;
  padding: 40px 20px;
  color: var(--term-text-secondary);
  font-size: 13px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.scanline-loader {
  font-size: 14px;
  color: var(--term-text-secondary);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* AI洞察 */
.ai-insights {
  max-width: 800px;
}

.insight-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  padding: 16px;
}

.card-title {
  font-size: 14px;
  font-weight: 800;
  margin-bottom: 16px;
  color: var(--term-accent);
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-icon {
  font-size: 20px;
}

.ai-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 40px;
  justify-content: center;
  color: var(--term-text-secondary);
}

.ai-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--term-border);
  border-top-color: var(--term-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.ai-content {
  margin-top: 16px;
}

.ai-title {
  font-size: 16px;
  font-weight: 800;
  margin-bottom: 12px;
}

.ai-summary {
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(0,0,0,0.03);
  border-left: 3px solid var(--term-accent);
}

.ai-analysis {
  font-size: 13px;
  line-height: 1.7;
  margin-bottom: 16px;
}

.ai-suggestions {
  margin-top: 16px;
  padding: 16px;
  background: rgba(0,0,0,0.02);
  border: 1px solid var(--term-border);
}

.suggestions-title {
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 12px;
}

.ai-suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.ai-suggestions li {
  font-size: 12px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.ai-empty {
  text-align: center;
  padding: 24px;
  color: var(--term-text-secondary);
}

.ai-empty .hint {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 8px;
}

.ai-generate-btn {
  width: 100%;
  padding: 12px;
  margin-top: 16px;
  background: var(--term-accent);
  color: #000;
  border: 2px solid #000;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.ai-generate-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.ai-generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式 */
@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
