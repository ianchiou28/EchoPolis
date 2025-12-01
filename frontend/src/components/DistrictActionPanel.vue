<template>
  <div class="district-panel-overlay" @click.self="$emit('close')">
    <div class="district-panel">
      <div class="panel-header">
        <div class="header-title">
          <span class="icon">{{ getIcon(district.id) }}</span>
          <span class="title">{{ district.name }} // ACTION_MENU</span>
        </div>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <div class="panel-body">
        <div class="district-info">
          <p class="desc">{{ getDescription(district.id) }}</p>
          <div class="stats">
            <div class="stat">
              <label>热度</label>
              <div class="bar"><div class="fill" :style="{width: (district.heat * 100) + '%'}"></div></div>
            </div>
            <div class="stat">
              <label>繁荣度</label>
              <div class="bar"><div class="fill" :style="{width: (district.prosperity * 100) + '%'}"></div></div>
            </div>
          </div>
        </div>

        <div class="action-list">
          <div 
            v-for="action in getActions(district.id)" 
            :key="action.type"
            class="action-item"
            :class="{ disabled: action.price > currentCash && action.type !== 'loan' && action.price > 0 }"
            @click="handleAction(action)"
          >
            <div class="action-main">
              <span class="action-name">{{ action.name }}</span>
              <span class="action-price" :class="{ 'positive': action.type === 'loan', 'free': action.price === 0 }">
                {{ action.price > 0 ? (action.type === 'loan' ? '+' : '-') : '' }}¥{{ action.price.toLocaleString() }}
              </span>
            </div>
            <div class="action-desc">{{ action.desc }}</div>
          </div>
        </div>

        <div class="result-log" v-if="lastResult">
          <div class="log-header">
            <span :class="lastResult.success ? 'success' : 'error'">
              {{ lastResult.success ? '执行成功' : '执行失败' }}
            </span>
          </div>
          <p class="log-message">{{ lastResult.message }}</p>
          <p class="log-ai" v-if="lastResult.ai_comment">
            <span class="prefix">AI:</span> {{ lastResult.ai_comment }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useGameStore } from '../stores/game'

const props = defineProps({
  district: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])
const gameStore = useGameStore()
const lastResult = ref(null)

const currentCash = computed(() => gameStore.assets?.cash || 0)

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

const getDescription = (id) => {
  const map = {
    finance: '处理银行业务，存取款与借贷。',
    tech: '金融市场交易中心，高风险高回报。',
    housing: '房地产交易与租赁管理。',
    learning: '提升个人能力与职业技能。',
    leisure: '放松身心，恢复精力与快乐值。',
    green: '投资可持续发展的新能源项目。'
  }
  return map[id] || '未知区域'
}

const getActions = (id) => {
  const actions = {
    finance: [
      { name: '定期存款', type: 'deposit', price: 5000, desc: '年化4%，稳健增值' },
      { name: '申请贷款', type: 'loan', price: 10000, desc: '获得资金，需按期归还' },
      { name: '信用评估', type: 'credit_check', price: 0, desc: '查看当前信用评分' }
    ],
    tech: [
      { name: '购买股票', type: 'stock_trade', price: 5000, desc: '高波动，预期年化15%' },
      { name: '基金定投', type: 'fund_invest', price: 2000, desc: '中等风险，预期年化10%' },
      { name: '期货合约', type: 'futures', price: 10000, desc: '极高风险，可能翻倍或归零' }
    ],
    housing: [
      { name: '购置房产', type: 'buy_house', price: 50000, desc: '长期资产，抗通胀' },
      { name: '支付房租', type: 'rent', price: 2000, desc: '维持居住，增加快乐' },
      { name: '物业管理', type: 'property_manage', price: 500, desc: '维护房产价值' }
    ],
    learning: [
      { name: '技能课程', type: 'skill_course', price: 3000, desc: '提升工作能力' },
      { name: '金融研修', type: 'finance_course', price: 5000, desc: '提升投资成功率' },
      { name: '考取证书', type: 'certificate', price: 1000, desc: '增加职业竞争力' }
    ],
    leisure: [
      { name: '娱乐消费', type: 'entertainment', price: 500, desc: '恢复少量精力与快乐' },
      { name: '社交聚会', type: 'social', price: 1000, desc: '大幅提升快乐，拓展人脉' },
      { name: '创业项目', type: 'start_business', price: 50000, desc: '高风险高回报的商业尝试' }
    ],
    green: [
      { name: '绿色基金', type: 'green_invest', price: 3000, desc: '环保产业，政策支持' },
      { name: '新能源股', type: 'energy_stock', price: 4000, desc: '热门赛道，中高风险' },
      { name: '碳权交易', type: 'carbon_trade', price: 2000, desc: '新兴市场交易' }
    ]
  }
  return actions[id] || []
}

const handleAction = async (action) => {
  if (action.price > currentCash.value && action.type !== 'loan' && action.price > 0) {
    return // Cannot afford
  }

  try {
    const result = await gameStore.performDistrictAction({
      action_name: action.name,
      action: action.type,
      price: action.price,
      building: props.district.id
    })
    lastResult.value = result
  } catch (e) {
    lastResult.value = {
      success: false,
      message: e.message || '操作失败'
    }
  }
}
</script>

<style scoped>
.district-panel-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  backdrop-filter: blur(2px);
}

.district-panel {
  width: 400px;
  background: var(--term-panel-bg);
  border: 2px solid var(--term-accent);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
}

.panel-header {
  background: var(--term-accent);
  color: #000;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-weight: 900;
  font-family: 'JetBrains Mono', monospace;
  display: flex;
  align-items: center;
  gap: 8px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  color: #000;
  line-height: 1;
}

.panel-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.district-info {
  border-bottom: 1px dashed var(--term-border);
  padding-bottom: 16px;
}

.desc {
  font-size: 12px;
  color: var(--term-text-secondary);
  margin-bottom: 12px;
  line-height: 1.4;
}

.stats {
  display: flex;
  gap: 16px;
}

.stat {
  flex: 1;
  font-size: 10px;
}

.stat label {
  display: block;
  margin-bottom: 4px;
  color: var(--term-text-secondary);
}

.bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  width: 100%;
}

.fill {
  height: 100%;
  background: var(--term-accent);
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-item {
  border: 1px solid var(--term-border);
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(0, 0, 0, 0.2);
}

.action-item:hover:not(.disabled) {
  border-color: var(--term-accent);
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(4px);
}

.action-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #444;
}

.action-main {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-family: 'JetBrains Mono', monospace;
}

.action-name {
  font-weight: bold;
  color: var(--term-text);
}

.action-price {
  color: var(--term-error);
}

.action-price.positive {
  color: var(--term-success);
}

.action-price.free {
  color: var(--term-text-secondary);
}

.action-desc {
  font-size: 10px;
  color: var(--term-text-secondary);
}

.result-log {
  margin-top: 10px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.3);
  border-left: 3px solid var(--term-text);
  font-size: 12px;
}

.log-header {
  font-weight: bold;
  margin-bottom: 4px;
}

.success { color: var(--term-success); }
.error { color: var(--term-error); }

.log-ai {
  margin-top: 8px;
  font-style: italic;
  color: var(--term-accent);
  font-size: 11px;
}

.prefix {
  font-weight: bold;
  font-style: normal;
}
</style>
