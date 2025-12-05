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
              <!-- 标签展示区 -->
              <div v-if="getAllTags.length > 0" class="tags-display">
                <div 
                  v-for="tag in getAllTags" 
                  :key="tag.id" 
                  class="profile-tag"
                  :class="{ 'auto-tag': tag.isAuto, 'custom-tag': tag.isCustom }"
                >
                  <span class="tag-icon">{{ tag.icon }}</span>
                  <span class="tag-text">{{ tag.name }}</span>
                </div>
              </div>
              
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

          <!-- 近期行为统计 -->
          <div v-if="personalData.recent_actions && personalData.recent_actions.total_actions" class="archive-card flex-grow">
            <div class="archive-header">近期行为（3个月）</div>
            <div class="archive-body">
              <div class="stats-row">
                <div class="stat-box">
                  <span class="stat-value accent">{{ personalData.recent_actions.total_actions }}</span>
                  <span class="stat-label">总行为数</span>
                </div>
                <div class="stat-box">
                  <span class="stat-value">{{ (personalData.recent_actions.avg_risk * 100).toFixed(0) }}%</span>
                  <span class="stat-label">平均风险</span>
                </div>
                <div class="stat-box">
                  <span class="stat-value success">{{ (personalData.recent_actions.avg_rationality * 100).toFixed(0) }}%</span>
                  <span class="stat-label">平均理性</span>
                </div>
              </div>
              <div class="category-list">
                <div class="list-title">行为分布</div>
                <div v-for="(count, category) in personalData.recent_actions.by_category" :key="category" class="category-row">
                  <span class="category-name">{{ getCategoryLabel(category) }}</span>
                  <span class="category-count">{{ count }}次</span>
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
      console.log('[Insights] getCurrentCharacter:', character)
      const id = character?.id || null
      console.log('[Insights] sessionId:', id)
      return id
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
    
    // 用户自选标签映射
    const userTagsMap = {
      'student': { name: '在校学生', icon: '🎓' },
      'new_graduate': { name: '应届毕业生', icon: '📜' },
      'working': { name: '职场人士', icon: '💼' },
      'investor_newbie': { name: '投资小白', icon: '🌱' },
      'investor_exp': { name: '有投资经验', icon: '📈' },
      'finance_major': { name: '金融相关专业', icon: '🏦' },
      'tech_major': { name: '理工科背景', icon: '💻' },
      'arts_major': { name: '文科背景', icon: '📚' },
      'risk_lover': { name: '喜欢冒险', icon: '🎲' },
      'risk_averse': { name: '稳健保守', icon: '🛡️' },
      'goal_house': { name: '目标买房', icon: '🏠' },
      'goal_retire': { name: '关注养老', icon: '👴' },
    }
    
    // 自动标签图标映射
    const autoTagIcons = {
      '高风险偏好': '🔥',
      '低风险偏好': '🛡️',
      '稳健投资': '⚖️',
      '理性决策者': '🧠',
      '冲动型投资': '⚡',
      '佛系理财': '🧘',
      '灵活应变': '🔄',
      '损失敏感': '😰',
      '过度自信': '💪',
      '容易跟风': '🐑',
      '善于规划': '📋',
      '活跃投资者': '📊',
      '善用杠杆': '🏗️',
      '关注房产': '🏠',
      '重视保障': '🔒',
      '注重消费': '🛒',
      '高频交易': '⚡',
      '长期持有': '🕐',
    }
    
    // 获取所有标签（用户标签 + 自动标签）
    const getAllTags = computed(() => {
      if (!personalData.value?.profile) return []
      
      const tags = []
      
      // 解析用户自选标签（包括预设标签和自定义标签）
      const userTags = personalData.value.profile.user_tags || ''
      if (userTags) {
        userTags.split(',').forEach(tagId => {
          if (tagId.startsWith('custom:')) {
            // 自定义标签
            const customName = tagId.slice(7)  // 去掉 'custom:' 前缀
            tags.push({
              id: tagId,
              name: customName,
              icon: '🏷️',
              isAuto: false,
              isCustom: true
            })
          } else if (userTagsMap[tagId]) {
            // 预设标签
            tags.push({
              id: tagId,
              name: userTagsMap[tagId].name,
              icon: userTagsMap[tagId].icon,
              isAuto: false,
              isCustom: false
            })
          }
        })
      }
      
      // 解析自动生成标签
      const autoTags = personalData.value.profile.auto_tags || ''
      if (autoTags) {
        autoTags.split(',').forEach(tagName => {
          if (tagName.trim()) {
            tags.push({
              id: `auto_${tagName}`,
              name: tagName.trim(),
              icon: autoTagIcons[tagName.trim()] || '🏷️',
              isAuto: true,
              isCustom: false
            })
          }
        })
      }
      
      return tags
    })

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
        const url = 'http://localhost:8000/api/insights/cohort?limit=20'
        console.log('[Insights] Fetching cohort insights from:', url)
        const response = await fetch(url)
        const result = await response.json()
        console.log('[Insights] Cohort insights result:', result)
        if (result.success) {
          cohortData.value = result.data
          console.log('[Insights] cohortData set:', cohortData.value?.length, 'items')
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
      console.log('[Insights] loadStatistics called, sessionId:', sessionId.value)
      if (!sessionId.value) {
        console.warn('[Insights] No sessionId, skipping loadStatistics')
        return
      }
      
      loading.value = true
      try {
        const url = `http://localhost:8000/api/insights/statistics/${sessionId.value}`
        console.log('[Insights] Fetching statistics from:', url)
        const response = await fetch(url)
        const result = await response.json()
        console.log('[Insights] Statistics result:', result)
        if (result.success) {
          statisticsData.value = result.data
          console.log('[Insights] statisticsData set:', statisticsData.value)
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
      console.log('[Insights] loadWarnings called, sessionId:', sessionId.value)
      if (!sessionId.value) {
        console.warn('[Insights] No sessionId, skipping loadWarnings')
        return
      }
      
      warningsLoading.value = true
      try {
        const url = `http://localhost:8000/api/insights/warnings/${sessionId.value}`
        console.log('[Insights] Fetching warnings from:', url)
        const response = await fetch(url)
        const result = await response.json()
        console.log('[Insights] Warnings result:', result)
        if (result.success) {
          warningsData.value = result.warnings || []
          warningStats.value = result.stats || { total: 0, critical: 0, high: 0, medium: 0, low: 0 }
          console.log('[Insights] warningStats:', warningStats.value)
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
      // 返回像素值，最大高度 80px
      const height = Math.max(8, (count / maxCount) * 80)
      return `${height}px`
    }

    onMounted(() => {
      console.log('[Insights] onMounted, sessionId:', sessionId.value)
      loadPersonalInsights()
      loadCohortInsights()
      loadWarnings()  // 自动加载预警
      loadPeerComparison()  // 自动加载同龄人对比
      loadEvolution()  // 自动加载行为演变
      loadStatistics()  // 自动加载行为统计
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
      getAllTags,
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
.view-container {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--term-bg);
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
  overflow-x: hidden;
  min-height: 0;
  padding-bottom: 20px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  min-height: 0;
}

.col-left, .col-right {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
  overflow: hidden;
}

.flex-grow { flex: 1; min-height: 0; display: flex; flex-direction: column; overflow: hidden; }
.scrollable { flex: 1; overflow-y: auto; }

/* Archive Card 统一样式 */
.archive-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  overflow: hidden;
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

/* 标签展示区 */
.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px dashed var(--term-border);
}

.profile-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(var(--term-accent-rgb), 0.1);
  border: 1px solid var(--term-accent);
  font-size: 12px;
  font-weight: 600;
}

.profile-tag.auto-tag {
  background: rgba(100, 100, 100, 0.1);
  border-color: var(--term-text-secondary);
  border-style: dashed;
}

.profile-tag.custom-tag {
  background: rgba(99, 102, 241, 0.15);
  border-color: #6366f1;
  border-style: solid;
}

.profile-tag .tag-icon {
  font-size: 14px;
}

.profile-tag .tag-text {
  color: var(--term-text);
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

/* 进度条 - 个人画像使用 */
.profile-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.profile-bars .bar-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.profile-bars .bar-label {
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
.profile-stats, .stats-row {
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

.stat-value.accent { color: var(--term-accent); }
.stat-value.success { color: #10b981; }

.stat-label {
  display: block;
  font-size: 10px;
  color: var(--term-text-secondary);
  text-transform: uppercase;
  margin-top: 4px;
}

/* 分类列表 */
.category-list {
  margin-top: 16px;
}

.list-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--term-text-secondary);
  text-transform: uppercase;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px dashed var(--term-border);
}

.category-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  font-size: 12px;
}

.category-count {
  font-weight: 700;
  color: var(--term-accent);
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

/* 旧版样式兼容 - insight-card */
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
}

.card-subtitle {
  font-size: 12px;
  font-weight: 700;
  margin: 16px 0 8px;
  color: var(--term-text-secondary);
}

/* 筛选按钮 */
.insight-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 700;
  background: transparent;
  color: var(--term-text);
  border: 2px solid var(--term-border);
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: var(--term-accent);
}

.filter-btn.active {
  background: var(--term-accent);
  border-color: var(--term-accent);
  color: #000;
}

/* 群体洞察 */
.cohort-insights {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cohort-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cohort-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  padding: 16px;
}

.cohort-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.cohort-tag {
  padding: 4px 10px;
  background: var(--term-accent);
  color: #000;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
}

.cohort-confidence {
  font-size: 11px;
  color: var(--term-text-secondary);
}

.cohort-title {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 8px;
}

.cohort-description {
  font-size: 12px;
  line-height: 1.6;
  color: var(--term-text-secondary);
  margin-bottom: 12px;
}

.cohort-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: var(--term-text-secondary);
  padding-top: 12px;
  border-top: 1px dashed var(--term-border);
}

/* 统计图表 */
.statistics-insights {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.radar-chart {
  display: flex;
  justify-content: center;
  padding: 16px;
}

.radar-svg {
  width: 280px;
  height: 280px;
}

/* 趋势图表 */
.trend-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.trend-line {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trend-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--term-text-secondary);
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 60px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid var(--term-border);
}

.chart-bar {
  flex: 1;
  min-width: 8px;
  max-width: 20px;
  border-radius: 2px 2px 0 0;
  transition: height 0.3s ease;
}

.chart-bar.risk-bar {
  background: #ef4444;
}

.chart-bar.rationality-bar {
  background: #10b981;
}

/* 月度活跃度图表 */
.activity-chart {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  min-height: 120px;
  padding: 16px 12px 8px 12px;
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid var(--term-border);
  overflow-x: auto;
}

.activity-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.activity-bar {
  width: 20px;
  background: var(--term-accent);
  border-radius: 2px 2px 0 0;
  min-height: 8px;
}

.activity-label {
  font-size: 9px;
  color: var(--term-text-secondary);
  white-space: nowrap;
}

/* 柱状图 */
.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 8px 0;
}

.bar-chart .bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-chart .bar-label {
  width: 50px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
  text-align: right;
}

.bar-chart .bar-container {
  flex: 1;
  height: 24px;
  background: var(--term-border);
  border-radius: 4px;
  overflow: hidden;
}

.bar-chart .bar-fill {
  height: 100%;
  background: var(--term-accent);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.bar-chart .bar-value {
  width: 50px;
  font-size: 12px;
  font-weight: 700;
  text-align: left;
  flex-shrink: 0;
}

/* AI 洞察 */
.ai-insights {
  max-width: 800px;
}

.ai-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  padding: 20px;
}

.ai-icon {
  font-size: 20px;
  margin-right: 8px;
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

.ai-alert {
  margin-top: 16px;
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  color: #ef4444;
  font-size: 12px;
  font-weight: 600;
}

.ai-meta {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed var(--term-border);
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--term-text-secondary);
}

.generate-btn, .refresh-btn {
  margin-top: 16px;
  padding: 10px 20px;
  font-size: 12px;
  font-weight: 700;
  background: var(--term-accent);
  color: #000;
  border: 2px solid #000;
  cursor: pointer;
}

.generate-btn:hover, .refresh-btn:hover {
  opacity: 0.9;
}

/* 预警样式 */
.warnings-insights {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.warnings-summary {
  display: flex;
  gap: 16px;
}

.summary-card {
  flex: 1;
  padding: 16px;
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  text-align: center;
}

.summary-card.critical {
  border-color: #ef4444;
}

.summary-value {
  font-size: 28px;
  font-weight: 900;
}

.summary-value.critical { color: #ef4444; }
.summary-value.warning { color: #f59e0b; }

.summary-label {
  font-size: 11px;
  color: var(--term-text-secondary);
  text-transform: uppercase;
  margin-top: 4px;
}

.warnings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.warning-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  padding: 16px;
}

.warning-card.critical {
  border-color: #ef4444;
}

.warning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.warning-type {
  font-size: 12px;
  font-weight: 700;
}

.warning-severity {
  font-size: 10px;
  padding: 3px 8px;
  font-weight: 700;
}

.warning-severity.critical {
  background: #ef4444;
  color: #fff;
}

.warning-severity.warning {
  background: #f59e0b;
  color: #000;
}

.warning-message {
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 12px;
}

.warning-details {
  font-size: 11px;
  color: var(--term-text-secondary);
  padding-top: 8px;
  border-top: 1px dashed var(--term-border);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}

/* 进化图表 */
.evolution-section {
  margin-top: 16px;
}

.section-subtitle {
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--term-text-secondary);
}

.evolution-chart {
  background: rgba(0,0,0,0.02);
  border: 1px solid var(--term-border);
  padding: 16px;
}

.chart-legend {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.risk { background: #ef4444; }
.legend-dot.rationality { background: #10b981; }

/* 里程碑 */
.milestones-section {
  margin-top: 20px;
}

.milestones-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.milestone-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(0,0,0,0.02);
  border: 1px solid var(--term-border);
}

.milestone-icon {
  font-size: 20px;
}

.milestone-content {
  flex: 1;
}

.milestone-title {
  font-size: 12px;
  font-weight: 700;
}

.milestone-desc {
  font-size: 11px;
  color: var(--term-text-secondary);
}

.milestone-month {
  font-size: 11px;
  color: var(--term-accent);
  font-weight: 700;
}

/* 同伴比较 */
.peer-comparison {
  margin-top: 16px;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.comparison-item {
  padding: 12px;
  background: rgba(0,0,0,0.02);
  border: 1px solid var(--term-border);
  text-align: center;
}

.comparison-label {
  font-size: 10px;
  color: var(--term-text-secondary);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.comparison-values {
  display: flex;
  justify-content: center;
  gap: 8px;
  align-items: baseline;
}

.your-value {
  font-size: 18px;
  font-weight: 800;
  color: var(--term-accent);
}

.vs-text {
  font-size: 10px;
  color: var(--term-text-secondary);
}

.peer-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--term-text-secondary);
}

/* 响应式 */
@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .tabs-nav {
    overflow-x: auto;
  }
  
  .comparison-grid {
    grid-template-columns: 1fr;
  }
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
  overflow: hidden;
}

.warning-overview {
  background: rgba(255, 152, 0, 0.05);
  border: 2px solid #ff9800;
}

.warning-stats-grid {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.warning-stat {
  text-align: center;
  padding: 16px 24px;
  border-radius: 8px;
  min-width: 90px;
}

.warning-stat .stat-value {
  font-size: 2.5rem;
  font-weight: 900;
  line-height: 1;
}

.warning-stat .stat-label {
  font-size: 12px;
  margin-top: 6px;
  font-weight: 600;
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
  overflow: hidden;
}

.warning-card {
  border-left-width: 4px;
  transition: border-left-width 0.2s, box-shadow 0.2s;
}

.warning-card:hover {
  border-left-width: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  background: rgba(var(--term-accent-rgb, 0, 255, 0), 0.03);
  border: 2px solid var(--term-accent);
  margin-bottom: 1.5rem;
  padding: 20px;
}

.peer-comparison-card .card-title {
  color: var(--term-accent);
  margin-bottom: 20px;
}

.overall-rank {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.25rem;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid var(--term-border);
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.rank-circle {
  width: 90px;
  height: 90px;
  border: 3px solid var(--term-accent);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(var(--term-accent-rgb, 0, 255, 0), 0.08);
}

.rank-value {
  font-size: 2rem;
  font-weight: 900;
  color: var(--term-accent);
  line-height: 1;
}

.rank-label {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 4px;
}

.rank-hint {
  font-size: 1rem;
  font-weight: 500;
  opacity: 0.85;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  margin-bottom: 1rem;
}

.comparison-item {
  padding: 12px 14px;
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid var(--term-border);
  border-radius: 6px;
}

.comp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comp-label {
  font-weight: 700;
  font-size: 13px;
}

.comp-verdict {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.comp-verdict.positive {
  background: rgba(76, 175, 80, 0.15);
  color: #2e7d32;
}

.comp-verdict.negative {
  background: rgba(244, 67, 54, 0.15);
  color: #c62828;
}

.comp-verdict.neutral {
  background: rgba(158, 158, 158, 0.15);
  color: #616161;
}

.comp-bars {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.comp-bars .bar-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comp-bars .bar-label {
  width: 45px;
  font-size: 12px;
  opacity: 0.8;
  flex-shrink: 0;
}

.comp-bars .bar-container {
  flex: 1;
  height: 10px;
  background: var(--term-border);
  border-radius: 5px;
  overflow: hidden;
}

.comp-bars .bar {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
}

.user-bar {
  background: var(--term-accent);
}

.peer-bar {
  background: rgba(0, 0, 0, 0.25);
}

.comp-bars .bar-value {
  width: 42px;
  font-size: 12px;
  text-align: right;
  font-weight: 700;
  flex-shrink: 0;
}

.refresh-btn {
  display: block;
  width: 100%;
  padding: 10px 16px;
  background: transparent;
  color: var(--term-text);
  border: 2px solid var(--term-border);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;
}

.refresh-btn:hover {
  background: var(--term-accent);
  border-color: var(--term-accent);
  color: #000;
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
