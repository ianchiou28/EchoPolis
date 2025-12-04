<template>
  <div class="insights-container">
    <div class="terminal-header">
      <div class="header-tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'personal' }"
          @click="activeTab = 'personal'">
          个人画像
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'statistics' }"
          @click="activeTab = 'statistics'; loadStatistics()">
          行为统计
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'ai' }"
          @click="activeTab = 'ai'">
          AI洞察
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'cohort' }"
          @click="activeTab = 'cohort'">
          群体洞察
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
        <button class="back-btn" @click="goBack">← 返回</button>
      </div>
    </div>

    <!-- 个人画像标签页 -->
    <div v-if="activeTab === 'personal'" class="insights-content">
      <div v-if="loading" class="loading-state">
        <div class="scanline-loader">分析行为数据中...</div>
      </div>

      <div v-else-if="personalData && personalData.profile" class="personal-insights">
        <!-- 行为画像卡片 -->
        <div class="insight-card profile-card">
          <div class="card-title">您的行为画像</div>
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
            <div class="profile-item">
              <span class="item-label">损失厌恶</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (personalData.profile.loss_aversion * 100) + '%' }"></div>
              </div>
              <span class="percent-value">{{ (personalData.profile.loss_aversion * 100).toFixed(0) }}%</span>
            </div>
            <div class="profile-item">
              <span class="item-label">过度自信</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (personalData.profile.overconfidence * 100) + '%' }"></div>
              </div>
              <span class="percent-value">{{ (personalData.profile.overconfidence * 100).toFixed(0) }}%</span>
            </div>
            <div class="profile-item">
              <span class="item-label">羊群倾向</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (personalData.profile.herding_tendency * 100) + '%' }"></div>
              </div>
              <span class="percent-value">{{ (personalData.profile.herding_tendency * 100).toFixed(0) }}%</span>
            </div>
            <div class="profile-item">
              <span class="item-label">规划能力</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (personalData.profile.planning_ability * 100) + '%' }"></div>
              </div>
              <span class="percent-value">{{ (personalData.profile.planning_ability * 100).toFixed(0) }}%</span>
            </div>
          </div>
          <div class="profile-stats">
            <span>行为记录: {{ personalData.profile.action_count }}次</span>
            <span>平均风险: {{ (personalData.profile.avg_risk_score * 100).toFixed(0) }}%</span>
            <span>平均理性: {{ (personalData.profile.avg_rationality * 100).toFixed(0) }}%</span>
          </div>
        </div>

        <!-- 近期行为统计 -->
        <div v-if="personalData.recent_actions && personalData.recent_actions.total_actions" class="insight-card">
          <div class="card-title">近期行为统计（3个月）</div>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ personalData.recent_actions.total_actions }}</div>
              <div class="stat-label">总行为数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ (personalData.recent_actions.avg_risk * 100).toFixed(0) }}%</div>
              <div class="stat-label">平均风险</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ (personalData.recent_actions.avg_rationality * 100).toFixed(0) }}%</div>
              <div class="stat-label">平均理性</div>
            </div>
          </div>
          <div class="category-breakdown">
            <div class="card-subtitle">行为分布</div>
            <div v-for="(count, category) in personalData.recent_actions.by_category" :key="category" class="category-item">
              <span class="category-name">{{ getCategoryLabel(category) }}</span>
              <span class="category-count">{{ count }}次</span>
            </div>
          </div>
        </div>

        <!-- 个性化建议 -->
        <div v-if="personalData.recommendations && personalData.recommendations.length" class="insight-card recommendations">
          <div class="card-title">个性化建议</div>
          <div v-for="(rec, idx) in personalData.recommendations" :key="idx" class="recommendation-item">
            <div class="rec-icon">💡</div>
            <div class="rec-text">{{ rec }}</div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📊</div>
        <div class="empty-text">暂无行为数据</div>
        <div class="empty-hint">继续游戏以生成您的行为画像</div>
      </div>
    </div>

    <!-- 群体洞察标签页 -->
    <div v-if="activeTab === 'cohort'" class="insights-content">
      <div v-if="loading" class="loading-state">
        <div class="scanline-loader">加载群体洞察...</div>
      </div>

      <div v-else class="cohort-insights">
        <!-- 同龄人对比卡片 -->
        <div v-if="peerComparison && peerComparison.comparisons" class="insight-card peer-comparison-card">
          <div class="card-title">📊 与Z世代同龄人对比</div>
          
          <!-- 综合排名 -->
          <div v-if="peerComparison.percentiles" class="overall-rank">
            <div class="rank-circle">
              <span class="rank-value">{{ peerComparison.percentiles.overall || 50 }}</span>
              <span class="rank-label">综合排名</span>
            </div>
            <div class="rank-hint">超过 {{ peerComparison.percentiles.overall || 50 }}% 的同龄人</div>
          </div>

          <!-- 各维度对比 -->
          <div class="comparison-grid">
            <div 
              v-for="comp in peerComparison.comparisons" 
              :key="comp.dimension" 
              class="comparison-item">
              <div class="comp-header">
                <span class="comp-label">{{ comp.dimension_label }}</span>
                <span class="comp-verdict" :class="comp.verdict.color">
                  {{ comp.verdict.icon }} {{ comp.verdict.text }}
                </span>
              </div>
              <div class="comp-bars">
                <div class="bar-row">
                  <span class="bar-label">你</span>
                  <div class="bar-container">
                    <div class="bar user-bar" :style="{ width: (comp.user_value * 100) + '%' }"></div>
                  </div>
                  <span class="bar-value">{{ comp.user_display }}</span>
                </div>
                <div class="bar-row">
                  <span class="bar-label">同龄人</span>
                  <div class="bar-container">
                    <div class="bar peer-bar" :style="{ width: (comp.peer_value * 100) + '%' }"></div>
                  </div>
                  <span class="bar-value">{{ comp.peer_display }}</span>
                </div>
              </div>
            </div>
          </div>

          <button class="refresh-btn" @click="loadPeerComparison">🔄 刷新对比</button>
        </div>

        <!-- 群体洞察筛选 -->
        <div v-if="cohortData && cohortData.length" class="insight-filters">
          <button 
            class="filter-btn" 
            :class="{ active: filterType === null }"
            @click="filterType = null">
            全部
          </button>
          <button 
            class="filter-btn" 
            :class="{ active: filterType === 'risk_profile' }"
            @click="filterType = 'risk_profile'">
            风险画像
          </button>
          <button 
            class="filter-btn" 
            :class="{ active: filterType === 'decision_pattern' }"
            @click="filterType = 'decision_pattern'">
            决策模式
          </button>
          <button 
            class="filter-btn" 
            :class="{ active: filterType === 'behavioral_bias' }"
            @click="filterType = 'behavioral_bias'">
            行为偏差
          </button>
        </div>

        <div v-if="cohortData && cohortData.length" class="cohort-list">
          <div 
            v-for="insight in filteredCohortData" 
            :key="insight.id" 
            class="insight-card cohort-card">
            <div class="cohort-header">
              <span class="cohort-tag">{{ getCategoryLabel(insight.insight_category) }}</span>
              <span class="cohort-confidence">置信度: {{ (insight.confidence_level * 100).toFixed(0) }}%</span>
            </div>
            <div class="cohort-title">{{ insight.title }}</div>
            <div class="cohort-description">{{ insight.description }}</div>
            <div class="cohort-meta">
              <span>样本量: {{ insight.sample_size }}</span>
              <span>生成月份: 第{{ insight.generated_month }}月</span>
            </div>
          </div>
        </div>

        <!-- 空状态提示 -->
        <div v-if="!peerComparison && (!cohortData || !cohortData.length)" class="empty-state">
          <div class="empty-icon">🔍</div>
          <div class="empty-text">暂无群体洞察</div>
          <div class="empty-hint">系统将定期生成Z世代行为洞察</div>
        </div>
      </div>
    </div>

    <!-- 行为统计标签页 -->
    <div v-if="activeTab === 'statistics'" class="insights-content">
      <div v-if="loading" class="loading-state">
        <div class="scanline-loader">加载行为统计...</div>
      </div>

      <div v-else-if="statisticsData" class="statistics-insights">
        <!-- 行为雷达图 -->
        <div v-if="statisticsData.behavior_radar && statisticsData.behavior_radar.length" class="insight-card">
          <div class="card-title">行为特征雷达图</div>
          <div class="radar-chart">
            <svg viewBox="0 0 200 200" class="radar-svg">
              <!-- 背景网格 -->
              <polygon v-for="level in [0.2, 0.4, 0.6, 0.8, 1]" :key="level"
                :points="radarPolygonPoints(level)"
                fill="none" 
                stroke="var(--term-border)" 
                stroke-width="0.5"
                opacity="0.5" />
              <!-- 轴线 -->
              <line v-for="(axis, i) in statisticsData.behavior_radar" :key="'axis-'+i"
                x1="100" y1="100"
                :x2="100 + Math.cos((i * 60 - 90) * Math.PI / 180) * 80"
                :y2="100 + Math.sin((i * 60 - 90) * Math.PI / 180) * 80"
                stroke="var(--term-border)"
                stroke-width="0.5" />
              <!-- 数据多边形 -->
              <polygon 
                :points="radarDataPoints(statisticsData.behavior_radar)"
                fill="var(--term-accent)"
                fill-opacity="0.3"
                stroke="var(--term-accent)"
                stroke-width="2" />
              <!-- 标签 -->
              <text v-for="(axis, i) in statisticsData.behavior_radar" :key="'label-'+i"
                :x="100 + Math.cos((i * 60 - 90) * Math.PI / 180) * 95"
                :y="100 + Math.sin((i * 60 - 90) * Math.PI / 180) * 95"
                text-anchor="middle"
                dominant-baseline="middle"
                fill="var(--term-text)"
                font-size="8">
                {{ axis.axis }}
              </text>
            </svg>
          </div>
        </div>

        <!-- 行为类别分布 -->
        <div v-if="statisticsData.category_distribution && statisticsData.category_distribution.length" class="insight-card">
          <div class="card-title">行为类别分布</div>
          <div class="bar-chart">
            <div v-for="cat in statisticsData.category_distribution" :key="cat.key" class="bar-item">
              <span class="bar-label">{{ cat.category }}</span>
              <div class="bar-container">
                <div class="bar-fill" :style="{ width: getBarWidth(cat.count) }"></div>
              </div>
              <span class="bar-value">{{ cat.count }}次</span>
            </div>
          </div>
        </div>

        <!-- 风险/理性趋势 -->
        <div class="insight-card">
          <div class="card-title">风险与理性度趋势</div>
          <div class="trend-chart">
            <div v-if="statisticsData.risk_trend && statisticsData.risk_trend.length" class="trend-line">
              <div class="trend-label">风险评分趋势</div>
              <div class="mini-chart">
                <span v-for="(point, i) in statisticsData.risk_trend" :key="'risk-'+i" 
                  class="chart-bar risk-bar"
                  :style="{ height: (point.value * 100) + '%' }">
                </span>
              </div>
            </div>
            <div v-if="statisticsData.rationality_trend && statisticsData.rationality_trend.length" class="trend-line">
              <div class="trend-label">理性度趋势</div>
              <div class="mini-chart">
                <span v-for="(point, i) in statisticsData.rationality_trend" :key="'rat-'+i" 
                  class="chart-bar rationality-bar"
                  :style="{ height: (point.value * 100) + '%' }">
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 月度活跃度 -->
        <div v-if="statisticsData.monthly_activity && statisticsData.monthly_activity.length" class="insight-card">
          <div class="card-title">月度行为活跃度</div>
          <div class="activity-chart">
            <div v-for="month in statisticsData.monthly_activity" :key="month.month" class="activity-item">
              <div class="activity-bar" :style="{ height: getActivityHeight(month.count) }"></div>
              <span class="activity-label">{{ month.month }}月</span>
            </div>
          </div>
        </div>

        <!-- 行为演变趋势 -->
        <div v-if="evolutionData && evolutionData.timeline && evolutionData.timeline.length" class="insight-card evolution-card">
          <div class="card-title">📈 行为演变趋势</div>
          
          <!-- 趋势总结 -->
          <div v-if="evolutionData.trend_summary" class="evolution-summary">
            <div class="trend-indicators">
              <div class="trend-item">
                <span class="trend-label">风险趋势</span>
                <span class="trend-value" :class="evolutionData.trend_summary.risk_trend">
                  {{ getTrendIcon(evolutionData.trend_summary.risk_trend) }}
                  {{ getTrendLabel(evolutionData.trend_summary.risk_trend) }}
                  <small v-if="evolutionData.trend_summary.risk_change_pct">
                    ({{ evolutionData.trend_summary.risk_change_pct > 0 ? '+' : '' }}{{ evolutionData.trend_summary.risk_change_pct }}%)
                  </small>
                </span>
              </div>
              <div class="trend-item">
                <span class="trend-label">理性趋势</span>
                <span class="trend-value" :class="evolutionData.trend_summary.rationality_trend">
                  {{ getTrendIcon(evolutionData.trend_summary.rationality_trend) }}
                  {{ getTrendLabel(evolutionData.trend_summary.rationality_trend) }}
                  <small v-if="evolutionData.trend_summary.rationality_change_pct">
                    ({{ evolutionData.trend_summary.rationality_change_pct > 0 ? '+' : '' }}{{ evolutionData.trend_summary.rationality_change_pct }}%)
                  </small>
                </span>
              </div>
            </div>
            <div class="trend-overall">
              {{ evolutionData.trend_summary.overall }}
            </div>
          </div>

          <!-- 演变时间线图表 -->
          <div class="evolution-chart">
            <svg viewBox="0 0 400 120" class="line-chart-svg" preserveAspectRatio="xMidYMid meet">
              <!-- 背景网格 -->
              <line v-for="i in 5" :key="'grid-'+i" 
                x1="40" :y1="10 + i * 20" 
                x2="390" :y2="10 + i * 20"
                stroke="var(--term-border)" stroke-width="0.5" opacity="0.3" />
              
              <!-- Y轴标签 -->
              <text x="35" y="15" fill="var(--term-text)" font-size="8" text-anchor="end">100%</text>
              <text x="35" y="55" fill="var(--term-text)" font-size="8" text-anchor="end">50%</text>
              <text x="35" y="95" fill="var(--term-text)" font-size="8" text-anchor="end">0%</text>
              
              <!-- 风险线 -->
              <polyline 
                :points="evolutionLinePoints('risk')"
                fill="none"
                stroke="#f44336"
                stroke-width="2" />
              
              <!-- 理性线 -->
              <polyline 
                :points="evolutionLinePoints('rationality')"
                fill="none"
                stroke="#4caf50"
                stroke-width="2" />
              
              <!-- 数据点 -->
              <circle v-for="(point, i) in evolutionData.timeline" :key="'risk-dot-'+i"
                :cx="getEvolutionX(i)"
                :cy="90 - point.avg_risk * 80"
                r="3"
                fill="#f44336" />
              <circle v-for="(point, i) in evolutionData.timeline" :key="'rat-dot-'+i"
                :cx="getEvolutionX(i)"
                :cy="90 - point.avg_rationality * 80"
                r="3"
                fill="#4caf50" />
              
              <!-- X轴月份标签 -->
              <text v-for="(point, i) in evolutionData.timeline" :key="'month-'+i"
                :x="getEvolutionX(i)"
                y="115"
                fill="var(--term-text)"
                font-size="7"
                text-anchor="middle">
                {{ point.month }}月
              </text>
            </svg>
            <div class="chart-legend">
              <span class="legend-item"><span class="legend-dot risk"></span>风险</span>
              <span class="legend-item"><span class="legend-dot rationality"></span>理性</span>
            </div>
          </div>

          <!-- 里程碑 -->
          <div v-if="evolutionData.milestones && evolutionData.milestones.length" class="milestones-section">
            <div class="section-subtitle">🏆 行为里程碑</div>
            <div class="milestones-list">
              <div v-for="milestone in evolutionData.milestones" :key="milestone.month + milestone.type" class="milestone-item">
                <span class="milestone-icon">{{ milestone.icon }}</span>
                <div class="milestone-content">
                  <div class="milestone-title">{{ milestone.title }}</div>
                  <div class="milestone-desc">{{ milestone.description }}</div>
                </div>
                <span class="milestone-month">第{{ milestone.month }}月</span>
              </div>
            </div>
          </div>

          <button class="refresh-btn" @click="loadEvolution">🔄 刷新数据</button>
        </div>
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

            <div v-if="aiInsight.risk_alert" class="ai-alert">
              ⚠️ {{ aiInsight.risk_alert }}
            </div>

            <div class="ai-meta">
              <span>生成时间: 第{{ aiInsight.generated_month }}月</span>
              <span>由 AI 分析生成</span>
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

    <!-- 行为预警标签页 -->
    <div v-if="activeTab === 'warnings'" class="insights-content">
      <div v-if="warningsLoading" class="loading-state">
        <div class="scanline-loader">检测行为风险...</div>
      </div>

      <div v-else-if="warningsData && warningsData.length" class="warnings-insights">
        <!-- 预警概览 -->
        <div class="insight-card warning-overview">
          <div class="card-title">⚠️ 风险预警概览</div>
          <div class="warning-stats-grid">
            <div class="warning-stat critical" v-if="warningStats.critical > 0">
              <div class="stat-value">{{ warningStats.critical }}</div>
              <div class="stat-label">紧急</div>
            </div>
            <div class="warning-stat high" v-if="warningStats.high > 0">
              <div class="stat-value">{{ warningStats.high }}</div>
              <div class="stat-label">高风险</div>
            </div>
            <div class="warning-stat medium" v-if="warningStats.medium > 0">
              <div class="stat-value">{{ warningStats.medium }}</div>
              <div class="stat-label">中风险</div>
            </div>
            <div class="warning-stat low" v-if="warningStats.low > 0">
              <div class="stat-value">{{ warningStats.low }}</div>
              <div class="stat-label">低风险</div>
            </div>
            <div class="warning-stat safe" v-if="warningStats.total === 0">
              <div class="stat-value">✓</div>
              <div class="stat-label">安全</div>
            </div>
          </div>
        </div>

        <!-- 预警列表 -->
        <div class="warnings-list">
          <div 
            v-for="warning in warningsData" 
            :key="warning.warning_type"
            class="insight-card warning-card"
            :class="`severity-${warning.severity}`">
            <div class="warning-header">
              <span class="warning-icon">{{ getSeverityIcon(warning.severity) }}</span>
              <span class="warning-type">{{ warning.warning_type_label }}</span>
              <span class="warning-severity" :class="warning.severity">
                {{ getSeverityLabel(warning.severity) }}
              </span>
            </div>
            <div class="warning-message">{{ warning.message }}</div>
            <div v-if="warning.suggestion" class="warning-suggestion">
              <span class="suggestion-icon">💡</span>
              {{ warning.suggestion }}
            </div>
            <div class="warning-details" v-if="warning.details">
              <div v-for="(value, key) in warning.details" :key="key" class="detail-item">
                <span class="detail-key">{{ key }}:</span>
                <span class="detail-value">{{ formatDetailValue(value) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state safe-state">
        <div class="empty-icon">✅</div>
        <div class="empty-text">当前无风险预警</div>
        <div class="empty-hint">您的财务行为表现良好，继续保持！</div>
      </div>

      <button class="refresh-warnings-btn" @click="loadWarnings" :disabled="warningsLoading">
        {{ warningsLoading ? '检测中...' : '🔄 重新检测' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'

export default {
  name: 'InsightsView',
  setup() {
    const router = useRouter()
    const gameStore = useGameStore()
    
    // 从 localStorage 获取当前角色的 session ID
    const getSessionId = () => {
      const character = gameStore.getCurrentCharacter()
      return character?.id || null
    }
    const sessionId = computed(() => getSessionId())

    const activeTab = ref('personal')
    const loading = ref(false)
    const personalData = ref(null)
    const cohortData = ref([])
    const filterType = ref(null)
    const statisticsData = ref(null)
    const aiInsight = ref(null)
    const aiLoading = ref(false)
    
    // 预警相关
    const warningsData = ref([])
    const warningsLoading = ref(false)
    const warningStats = ref({ total: 0, critical: 0, high: 0, medium: 0, low: 0 })
    
    // 同龄人对比
    const peerComparison = ref(null)
    
    // 行为演变
    const evolutionData = ref(null)

    const filteredCohortData = computed(() => {
      if (!filterType.value) return cohortData.value
      return cohortData.value.filter(item => item.insight_type === filterType.value)
    })

    const goBack = () => {
      router.push('/home')
    }

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

    const loadCohortInsights = async () => {
      loading.value = true
      try {
        const response = await fetch('http://localhost:8000/api/insights/cohort?limit=20')
        const result = await response.json()
        if (result.success) {
          cohortData.value = result.data
        }
      } catch (error) {
        console.error('Failed to load cohort insights:', error)
      } finally {
        loading.value = false
      }
    }

    // 加载同龄人对比
    const loadPeerComparison = async () => {
      if (!sessionId.value) return
      
      try {
        const response = await fetch(`http://localhost:8000/api/insights/peer-comparison/${sessionId.value}`)
        const result = await response.json()
        if (result.success) {
          peerComparison.value = result.data
        }
      } catch (error) {
        console.error('Failed to load peer comparison:', error)
      }
    }

    // 加载行为演变数据
    const loadEvolution = async () => {
      if (!sessionId.value) return
      
      try {
        const response = await fetch(`http://localhost:8000/api/insights/evolution/${sessionId.value}`)
        const result = await response.json()
        if (result.success) {
          evolutionData.value = result.data
        }
      } catch (error) {
        console.error('Failed to load evolution data:', error)
      }
    }

    // 演变图表辅助函数
    const getEvolutionX = (index) => {
      const total = evolutionData.value?.timeline?.length || 1
      const spacing = 340 / Math.max(total - 1, 1)
      return 50 + index * spacing
    }

    const evolutionLinePoints = (type) => {
      if (!evolutionData.value?.timeline) return ''
      const points = evolutionData.value.timeline.map((point, i) => {
        const x = getEvolutionX(i)
        const value = type === 'risk' ? point.avg_risk : point.avg_rationality
        const y = 90 - value * 80
        return `${x},${y}`
      })
      return points.join(' ')
    }

    const getTrendIcon = (trend) => {
      const icons = { increasing: '📈', decreasing: '📉', stable: '➡️' }
      return icons[trend] || '➡️'
    }

    const getTrendLabel = (trend) => {
      const labels = { increasing: '上升', decreasing: '下降', stable: '稳定' }
      return labels[trend] || '稳定'
    }

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

    const getCategoryLabel = (category) => {
      const labels = {
        investment: '投资',
        financing: '融资',
        housing: '住房',
        protection: '保障',
        consumption: '消费',
        risk_profile: '风险画像',
        decision_pattern: '决策模式',
        behavioral_bias: '行为偏差',
        behavior: '行为',
        psychology: '心理'
      }
      return labels[category] || category
    }

    // 加载统计数据
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

    // 生成AI洞察
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

    // 加载预警数据
    const loadWarnings = async () => {
      if (!sessionId.value) return
      
      warningsLoading.value = true
      try {
        const response = await fetch(`http://localhost:8000/api/insights/warnings/${sessionId.value}`)
        const result = await response.json()
        if (result.success) {
          warningsData.value = result.warnings || []
          warningStats.value = result.stats || { total: 0, critical: 0, high: 0, medium: 0, low: 0 }
        }
      } catch (error) {
        console.error('Failed to load warnings:', error)
      } finally {
        warningsLoading.value = false
      }
    }

    // 预警辅助函数
    const getSeverityIcon = (severity) => {
      const icons = {
        critical: '🚨',
        high: '⚠️',
        medium: '⚡',
        low: 'ℹ️'
      }
      return icons[severity] || '📋'
    }

    const getSeverityLabel = (severity) => {
      const labels = {
        critical: '紧急',
        high: '高风险',
        medium: '中风险',
        low: '低风险'
      }
      return labels[severity] || severity
    }

    const formatDetailValue = (value) => {
      if (typeof value === 'number') {
        if (value >= 1000000) return `${(value / 10000).toFixed(1)}万`
        if (value >= 10000) return `${(value / 10000).toFixed(2)}万`
        if (value < 1) return `${(value * 100).toFixed(1)}%`
        return value.toFixed(2)
      }
      return value
    }

    // 雷达图辅助函数
    const radarPolygonPoints = (level) => {
      const points = []
      for (let i = 0; i < 6; i++) {
        const angle = (i * 60 - 90) * Math.PI / 180
        const x = 100 + Math.cos(angle) * 80 * level
        const y = 100 + Math.sin(angle) * 80 * level
        points.push(`${x},${y}`)
      }
      return points.join(' ')
    }

    const radarDataPoints = (data) => {
      const points = []
      for (let i = 0; i < data.length; i++) {
        const angle = (i * 60 - 90) * Math.PI / 180
        const value = data[i].value || 0
        const x = 100 + Math.cos(angle) * 80 * value
        const y = 100 + Math.sin(angle) * 80 * value
        points.push(`${x},${y}`)
      }
      return points.join(' ')
    }

    // 柱状图辅助函数
    const getBarWidth = (count) => {
      const maxCount = Math.max(...(statisticsData.value?.category_distribution?.map(c => c.count) || [1]))
      return `${(count / maxCount) * 100}%`
    }

    const getActivityHeight = (count) => {
      const maxCount = Math.max(...(statisticsData.value?.monthly_activity?.map(m => m.count) || [1]))
      return `${(count / maxCount) * 100}%`
    }

    onMounted(() => {
      loadPersonalInsights()
      loadCohortInsights()
      loadWarnings()  // 自动加载预警
      loadPeerComparison()  // 自动加载同龄人对比
      loadEvolution()  // 自动加载行为演变
    })

    return {
      activeTab,
      loading,
      personalData,
      cohortData,
      filterType,
      filteredCohortData,
      statisticsData,
      aiInsight,
      aiLoading,
      warningsData,
      warningsLoading,
      warningStats,
      peerComparison,
      evolutionData,
      goBack,
      getRiskLabel,
      getStyleLabel,
      getCategoryLabel,
      loadStatistics,
      generateAiInsight,
      loadWarnings,
      loadPeerComparison,
      loadEvolution,
      getEvolutionX,
      evolutionLinePoints,
      getTrendIcon,
      getTrendLabel,
      getSeverityIcon,
      getSeverityLabel,
      formatDetailValue,
      radarPolygonPoints,
      radarDataPoints,
      getBarWidth,
      getActivityHeight
    }
  }
}
</script>

<style scoped>
.insights-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--term-bg);
  color: var(--term-text);
}

.terminal-header {
  padding: 1rem;
  border-bottom: 1px solid var(--term-border);
}

.header-tabs {
  display: flex;
  gap: 0.5rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  color: var(--term-text);
  border: 1px solid var(--term-border);
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  background: var(--term-border);
}

.tab-btn.active {
  background: var(--term-accent);
  border-color: var(--term-accent);
}

.insights-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.scanline-loader {
  font-size: 1.2rem;
  opacity: 0.7;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.personal-insights, .cohort-insights {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.insight-card {
  background: rgba(var(--term-accent-rgb, 0, 255, 0), 0.05);
  border: 1px solid var(--term-border);
  padding: 1.5rem;
  border-radius: 4px;
}

.card-title {
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: var(--term-accent);
}

.card-subtitle {
  font-size: 1rem;
  font-weight: bold;
  margin: 1rem 0 0.5rem;
  opacity: 0.8;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.profile-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.item-label {
  font-size: 0.9rem;
  opacity: 0.7;
}

.item-value {
  font-size: 1.1rem;
  font-weight: bold;
}

.risk-conservative {
  color: #4caf50;
}

.risk-moderate {
  color: #ff9800;
}

.risk-aggressive {
  color: #f44336;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--term-accent);
  transition: width 0.5s;
}

.percent-value {
  font-size: 0.9rem;
  opacity: 0.8;
}

.profile-stats {
  display: flex;
  gap: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--term-border);
  font-size: 0.9rem;
  opacity: 0.7;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--term-accent);
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.7;
  margin-top: 0.5rem;
}

.category-breakdown {
  margin-top: 1rem;
}

.category-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.category-name {
  opacity: 0.8;
}

.category-count {
  color: var(--term-accent);
  font-weight: bold;
}

.recommendations {
  background: rgba(var(--term-accent-rgb, 0, 255, 0), 0.08);
}

.recommendation-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  margin-bottom: 0.75rem;
}

.rec-icon {
  font-size: 1.5rem;
}

.rec-text {
  flex: 1;
  line-height: 1.6;
}

.insight-filters {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.4rem 0.8rem;
  background: transparent;
  color: var(--term-text);
  border: 1px solid var(--term-border);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.filter-btn:hover {
  background: var(--term-border);
}

.filter-btn.active {
  background: var(--term-accent);
  border-color: var(--term-accent);
}

.cohort-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cohort-card {
  padding: 1.2rem;
}

.cohort-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.cohort-tag {
  padding: 0.25rem 0.75rem;
  background: var(--term-accent);
  color: var(--term-bg);
  border-radius: 3px;
  font-size: 0.8rem;
  font-weight: bold;
}

.cohort-confidence {
  font-size: 0.85rem;
  opacity: 0.7;
}

.cohort-title {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.75rem;
}

.cohort-description {
  line-height: 1.6;
  opacity: 0.85;
  margin-bottom: 1rem;
}

.cohort-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.85rem;
  opacity: 0.6;
  padding-top: 0.75rem;
  border-top: 1px solid var(--term-border);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  opacity: 0.6;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.empty-hint {
  font-size: 0.95rem;
  opacity: 0.7;
}

/* 返回按钮 */
.back-btn {
  margin-left: auto;
  padding: 0.5rem 1rem;
  background: transparent;
  color: var(--term-text);
  border: 1px solid var(--term-border);
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  background: var(--term-border);
}

/* 行为统计图表样式 */
.statistics-insights {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.radar-chart {
  display: flex;
  justify-content: center;
  padding: 1rem;
}

.radar-svg {
  width: 300px;
  height: 300px;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.bar-label {
  width: 60px;
  font-size: 0.9rem;
}

.bar-container {
  flex: 1;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: var(--term-accent);
  transition: width 0.5s;
}

.bar-value {
  width: 50px;
  text-align: right;
  font-size: 0.9rem;
  color: var(--term-accent);
}

.trend-chart {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.trend-line {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.trend-label {
  font-size: 0.9rem;
  opacity: 0.7;
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 60px;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.chart-bar {
  flex: 1;
  min-height: 4px;
  border-radius: 2px;
  transition: height 0.3s;
}

.risk-bar {
  background: #f44336;
}

.rationality-bar {
  background: #4caf50;
}

.activity-chart {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 120px;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.activity-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.activity-bar {
  width: 100%;
  background: var(--term-accent);
  border-radius: 2px;
  min-height: 4px;
  transition: height 0.3s;
}

.activity-label {
  font-size: 0.75rem;
  opacity: 0.6;
}

/* AI洞察样式 */
.ai-insights {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.ai-card {
  background: rgba(var(--term-accent-rgb, 0, 255, 0), 0.08);
}

.ai-card .card-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.ai-icon {
  font-size: 1.5rem;
}

.ai-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
}

.ai-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--term-border);
  border-top-color: var(--term-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.ai-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ai-title {
  font-size: 1.3rem;
  font-weight: bold;
  color: var(--term-accent);
}

.ai-summary {
  font-size: 1.1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  border-left: 3px solid var(--term-accent);
}

.ai-analysis {
  line-height: 1.7;
  opacity: 0.9;
}

.ai-suggestions {
  padding: 1rem;
  background: rgba(var(--term-accent-rgb, 0, 255, 0), 0.1);
  border-radius: 4px;
}

.suggestions-title {
  font-weight: bold;
  margin-bottom: 0.75rem;
}

.ai-suggestions ul {
  margin: 0;
  padding-left: 1.5rem;
}

.ai-suggestions li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.ai-alert {
  padding: 1rem;
  background: rgba(244, 67, 54, 0.2);
  border: 1px solid #f44336;
  border-radius: 4px;
  color: #ff6b6b;
}

.ai-meta {
  display: flex;
  gap: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--term-border);
  font-size: 0.85rem;
  opacity: 0.6;
}

.ai-empty {
  text-align: center;
  padding: 2rem;
  opacity: 0.7;
}

.ai-empty .hint {
  font-size: 0.9rem;
  opacity: 0.6;
  margin-top: 0.5rem;
}

.ai-generate-btn {
  width: 100%;
  padding: 1rem;
  margin-top: 1rem;
  background: var(--term-accent);
  color: var(--term-bg);
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.ai-generate-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.ai-generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* CRT效果 */
.insights-container::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.05),
    rgba(0, 0, 0, 0.05) 1px,
    transparent 1px,
    transparent 2px
  );
  pointer-events: none;
}

/* ========== 预警样式 ========== */
.warning-tab {
  position: relative;
}

.warning-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  font-size: 0.75rem;
  font-weight: bold;
  background: #ff9800;
  color: #000;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.warning-badge.critical {
  background: #f44336;
  color: #fff;
  animation: pulse-critical 1s infinite;
}

@keyframes pulse-critical {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.warnings-insights {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.warning-overview {
  background: rgba(255, 152, 0, 0.1);
  border-color: #ff9800;
}

.warning-stats-grid {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.warning-stat {
  text-align: center;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  min-width: 80px;
}

.warning-stat .stat-value {
  font-size: 2rem;
  font-weight: bold;
}

.warning-stat .stat-label {
  font-size: 0.85rem;
  margin-top: 0.25rem;
  opacity: 0.8;
}

.warning-stat.critical {
  background: rgba(244, 67, 54, 0.2);
  border: 1px solid #f44336;
}

.warning-stat.critical .stat-value {
  color: #f44336;
}

.warning-stat.high {
  background: rgba(255, 87, 34, 0.2);
  border: 1px solid #ff5722;
}

.warning-stat.high .stat-value {
  color: #ff5722;
}

.warning-stat.medium {
  background: rgba(255, 152, 0, 0.2);
  border: 1px solid #ff9800;
}

.warning-stat.medium .stat-value {
  color: #ff9800;
}

.warning-stat.low {
  background: rgba(255, 193, 7, 0.2);
  border: 1px solid #ffc107;
}

.warning-stat.low .stat-value {
  color: #ffc107;
}

.warning-stat.safe {
  background: rgba(76, 175, 80, 0.2);
  border: 1px solid #4caf50;
}

.warning-stat.safe .stat-value {
  color: #4caf50;
  font-size: 2.5rem;
}

.warnings-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.warning-card {
  border-left-width: 4px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.warning-card:hover {
  transform: translateX(4px);
}

.warning-card.severity-critical {
  border-left-color: #f44336;
  background: rgba(244, 67, 54, 0.1);
}

.warning-card.severity-high {
  border-left-color: #ff5722;
  background: rgba(255, 87, 34, 0.1);
}

.warning-card.severity-medium {
  border-left-color: #ff9800;
  background: rgba(255, 152, 0, 0.1);
}

.warning-card.severity-low {
  border-left-color: #ffc107;
  background: rgba(255, 193, 7, 0.1);
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.warning-icon {
  font-size: 1.5rem;
}

.warning-type {
  flex: 1;
  font-weight: bold;
  font-size: 1.1rem;
}

.warning-severity {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.warning-severity.critical {
  background: #f44336;
  color: #fff;
}

.warning-severity.high {
  background: #ff5722;
  color: #fff;
}

.warning-severity.medium {
  background: #ff9800;
  color: #000;
}

.warning-severity.low {
  background: #ffc107;
  color: #000;
}

.warning-message {
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.warning-suggestion {
  padding: 0.75rem;
  background: rgba(var(--term-accent-rgb, 0, 255, 0), 0.1);
  border-radius: 4px;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.suggestion-icon {
  flex-shrink: 0;
}

.warning-details {
  font-size: 0.9rem;
  opacity: 0.8;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.detail-item {
  display: flex;
  gap: 0.5rem;
}

.detail-key {
  opacity: 0.7;
}

.detail-value {
  font-weight: bold;
  color: var(--term-accent);
}

.safe-state {
  text-align: center;
}

.safe-state .empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.refresh-warnings-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: transparent;
  color: var(--term-text);
  border: 1px solid var(--term-border);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  align-self: center;
}

.refresh-warnings-btn:hover:not(:disabled) {
  background: var(--term-border);
}

.refresh-warnings-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ========== 同龄人对比样式 ========== */
.peer-comparison-card {
  background: rgba(var(--term-accent-rgb, 0, 255, 0), 0.05);
  border-color: var(--term-accent);
  margin-bottom: 1.5rem;
}

.overall-rank {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.rank-circle {
  width: 80px;
  height: 80px;
  border: 3px solid var(--term-accent);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.rank-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: var(--term-accent);
}

.rank-label {
  font-size: 0.7rem;
  opacity: 0.7;
}

.rank-hint {
  font-size: 0.95rem;
  opacity: 0.8;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.comparison-item {
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
}

.comp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.comp-label {
  font-weight: bold;
}

.comp-verdict {
  font-size: 0.85rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.comp-verdict.positive {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.comp-verdict.negative {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.comp-verdict.neutral {
  background: rgba(158, 158, 158, 0.2);
  color: #9e9e9e;
}

.comp-bars {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.bar-label {
  width: 50px;
  font-size: 0.8rem;
  opacity: 0.7;
}

.bar-container {
  flex: 1;
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.bar {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease;
}

.user-bar {
  background: var(--term-accent);
}

.peer-bar {
  background: rgba(255, 255, 255, 0.4);
}

.bar-value {
  width: 45px;
  font-size: 0.85rem;
  text-align: right;
  font-weight: bold;
}

.refresh-btn {
  display: block;
  width: 100%;
  padding: 0.6rem;
  background: transparent;
  color: var(--term-text);
  border: 1px solid var(--term-border);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.refresh-btn:hover {
  background: var(--term-border);
}

/* ========== 行为演变样式 ========== */
.evolution-card {
  background: rgba(var(--term-accent-rgb, 0, 255, 0), 0.03);
}

.evolution-summary {
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.trend-indicators {
  display: flex;
  gap: 2rem;
  margin-bottom: 0.75rem;
}

.trend-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.trend-label {
  font-size: 0.85rem;
  opacity: 0.7;
}

.trend-value {
  font-weight: bold;
  font-size: 1rem;
}

.trend-value small {
  font-weight: normal;
  opacity: 0.7;
}

.trend-value.increasing {
  color: #ff9800;
}

.trend-value.decreasing {
  color: #4caf50;
}

.trend-value.stable {
  color: #9e9e9e;
}

.trend-overall {
  font-size: 0.95rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--term-border);
  opacity: 0.9;
}

.evolution-chart {
  margin: 1rem 0;
}

.line-chart-svg {
  width: 100%;
  height: auto;
  max-height: 150px;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.risk {
  background: #f44336;
}

.legend-dot.rationality {
  background: #4caf50;
}

.milestones-section {
  margin-top: 1rem;
}

.section-subtitle {
  font-weight: bold;
  margin-bottom: 0.75rem;
  font-size: 1rem;
}

.milestones-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.milestone-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.15);
  border-radius: 6px;
  border-left: 3px solid var(--term-accent);
}

.milestone-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.milestone-content {
  flex: 1;
}

.milestone-title {
  font-weight: bold;
  font-size: 0.95rem;
}

.milestone-desc {
  font-size: 0.85rem;
  opacity: 0.7;
  margin-top: 0.2rem;
}

.milestone-month {
  font-size: 0.8rem;
  opacity: 0.6;
  white-space: nowrap;
}
</style>
