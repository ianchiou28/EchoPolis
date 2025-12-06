<template>
  <div class="district-preview-overlay" @click.self="$emit('close')">
    <div class="district-preview" :class="district.id">
      <div class="preview-header">
        <div class="header-left">
          <span class="district-icon">{{ getIcon(district.id) }}</span>
          <div>
            <span class="district-name">{{ district.name }}</span>
            <span class="district-code">{{ getDistrictCode(district.id) }}</span>
          </div>
        </div>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <div class="preview-body">
        <!-- 区域描述 -->
        <p class="district-desc">{{ getDescription(district.id) }}</p>
        
        <!-- 区域指标 -->
        <div class="district-stats">
          <div class="stat-item">
            <div class="stat-label">热度指数</div>
            <div class="stat-bar">
              <div class="stat-fill" :style="{width: (district.heat * 100) + '%'}"></div>
            </div>
            <div class="stat-value">{{ Math.round(district.heat * 100) }}%</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">繁荣度</div>
            <div class="stat-bar">
              <div class="stat-fill prosperity" :style="{width: (district.prosperity * 100) + '%'}"></div>
            </div>
            <div class="stat-value">{{ Math.round(district.prosperity * 100) }}%</div>
          </div>
        </div>

        <!-- 快捷功能预览 -->
        <div class="quick-actions">
          <div class="action-title">可用功能</div>
          <div class="action-list">
            <div v-for="action in getQuickActions(district.id)" :key="action.name" class="action-tag">
              {{ action.icon }} {{ action.name }}
            </div>
          </div>
        </div>

        <!-- 导航按钮 -->
        <button class="enter-btn" @click="navigateToPage">
          <span class="btn-icon">→</span>
          进入 {{ getPageName(district.id) }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  district: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'navigate'])

const getIcon = (id) => {
  const map = {
    finance: '🏦',
    tech: '📈',
    housing: '🏢',
    learning: '🎓',
    leisure: '🎮',
    green: '♻️'
  }
  return map[id] || '📍'
}

const getDistrictCode = (id) => {
  const map = {
    finance: 'BANK_SYS',
    tech: 'TRADE_HUB',
    housing: 'REAL_ESTATE',
    learning: 'SKILL_LAB',
    leisure: 'LIFE_ZONE',
    green: 'ESG_SECTOR'
  }
  return map[id] || 'UNKNOWN'
}

const getDescription = (id) => {
  const map = {
    finance: '城市金融中枢，处理存款、贷款与信用评估。稳健的财务管理从这里开始。',
    tech: '量化交易核心区，股票、基金、期货一站式交易平台。高风险高回报的金融战场。',
    housing: '房地产交易中心，购置房产、管理租赁，构建长期资产配置。',
    learning: '知识引擎驱动的技能中心，职业培训、能力提升、考证认证全覆盖。',
    leisure: '生活消费与社交中心，娱乐休闲、人脉拓展、创业孵化基地。',
    green: 'ESG可持续投资专区，绿色基金、新能源股、碳权交易等环保产业。'
  }
  return map[id] || '未知区域'
}

const getQuickActions = (id) => {
  const actions = {
    finance: [
      { icon: '💰', name: '存取款' },
      { icon: '🏧', name: '贷款' },
      { icon: '📊', name: '信用评估' }
    ],
    tech: [
      { icon: '📈', name: '股票交易' },
      { icon: '📉', name: '基金定投' },
      { icon: '⚡', name: '期货合约' }
    ],
    housing: [
      { icon: '🏠', name: '购置房产' },
      { icon: '🔑', name: '租房管理' },
      { icon: '📊', name: '房贷状态' }
    ],
    learning: [
      { icon: '📚', name: '技能培训' },
      { icon: '💼', name: '职位申请' },
      { icon: '📜', name: '考取证书' }
    ],
    leisure: [
      { icon: '🎮', name: '休闲娱乐' },
      { icon: '🤝', name: '社交活动' },
      { icon: '🚀', name: '创业项目' }
    ],
    green: [
      { icon: '🌱', name: '绿色基金' },
      { icon: '⚡', name: '新能源股' },
      { icon: '🌍', name: '碳权交易' }
    ]
  }
  return actions[id] || []
}

const getPageName = (id) => {
  const map = {
    finance: '银行系统',
    tech: '股票交易',
    housing: '房产中心',
    learning: '职业发展',
    leisure: '生活消费',
    green: '股票交易'
  }
  return map[id] || '详情页面'
}

const getTargetView = (id) => {
  const map = {
    finance: 'banking',
    tech: 'trading',
    housing: 'housing',
    learning: 'career',
    leisure: 'lifestyle',
    green: 'trading'
  }
  return map[id] || 'city'
}

const navigateToPage = () => {
  emit('navigate', getTargetView(props.district.id))
  emit('close')
}
</script>

<style scoped>
.district-preview-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  backdrop-filter: blur(3px);
}

.district-preview {
  width: 380px;
  background: var(--term-panel-bg);
  border: 3px solid var(--term-border);
  box-shadow: 8px 8px 0 rgba(0, 0, 0, 0.2);
}

/* 区域主题色 */
.district-preview.finance { border-color: #f59e0b; }
.district-preview.tech { border-color: #10b981; }
.district-preview.housing { border-color: #3b82f6; }
.district-preview.learning { border-color: #8b5cf6; }
.district-preview.leisure { border-color: #ec4899; }
.district-preview.green { border-color: #22c55e; }

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--term-accent);
  color: #000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.district-icon {
  font-size: 28px;
}

.district-name {
  font-weight: 900;
  font-size: 18px;
  display: block;
}

.district-code {
  font-size: 10px;
  font-family: 'JetBrains Mono', monospace;
  opacity: 0.7;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  color: #000;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.close-btn:hover {
  transform: scale(1.2);
}

.preview-body {
  padding: 20px;
}

.district-desc {
  font-size: 13px;
  line-height: 1.6;
  color: var(--term-text-secondary);
  margin-bottom: 20px;
}

.district-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px dashed var(--term-border);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-label {
  width: 60px;
  font-size: 11px;
  font-weight: 600;
  color: var(--term-text-secondary);
}

.stat-bar {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.1);
  border: 1px solid var(--term-border);
}

.stat-fill {
  height: 100%;
  background: var(--term-accent);
  transition: width 0.5s ease;
}

.stat-fill.prosperity {
  background: #10b981;
}

.stat-value {
  width: 40px;
  font-size: 11px;
  font-weight: 700;
  text-align: right;
}

.quick-actions {
  margin-bottom: 20px;
}

.action-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--term-text-secondary);
  margin-bottom: 10px;
  text-transform: uppercase;
}

.action-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.action-tag {
  padding: 6px 12px;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid var(--term-border);
  font-weight: 600;
}

.enter-btn {
  width: 100%;
  padding: 14px 20px;
  font-size: 14px;
  font-weight: 800;
  background: var(--term-accent);
  color: #000;
  border: 2px solid #000;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.enter-btn:hover {
  background: #000;
  color: var(--term-accent);
  transform: translateX(4px);
}

.btn-icon {
  font-size: 18px;
}
</style>
