<template>
  <div class="investment-panel">
    <!-- 投资摘要折叠面板 -->
    <div class="collapsible-section">
      <div class="section-header" @click="toggleInvestments">
        <h3>📊 投资组合</h3>
        <span class="toggle-icon">{{ showInvestments ? '▼' : '▶' }}</span>
      </div>
      <div v-if="showInvestments" class="section-content">
        <div v-if="investments.length === 0" class="empty-state">
          暂无投资
        </div>
        <div v-else>
          <div v-for="investment in investments" :key="investment.name" class="investment-item">
            <div class="investment-header">
              <span class="investment-name">{{ investment.name }}</span>
              <span class="investment-amount">{{ formatCurrency(investment.amount) }}</span>
            </div>
            <div class="investment-details">
              <span v-if="investment.type === 'MONTHLY'" class="monthly-return">
                +{{ formatCurrency(investment.monthlyReturn) }}/月
              </span>
              <span class="remaining-time">剩余{{ investment.remainingMonths }}月</span>
            </div>
          </div>
          <div class="investment-summary">
            <div class="summary-item">
              <span>总投资:</span>
              <span>{{ formatCurrency(totalInvested) }}</span>
            </div>
            <div class="summary-item">
              <span>月收益:</span>
              <span>{{ formatCurrency(monthlyIncome) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 交易记录折叠面板 -->
    <div class="collapsible-section">
      <div class="section-header" @click="toggleTransactions">
        <h3>📋 交易记录</h3>
        <span class="toggle-icon">{{ showTransactions ? '▼' : '▶' }}</span>
      </div>
      <div v-if="showTransactions" class="section-content">
        <div v-if="transactions.length === 0" class="empty-state">
          暂无交易记录
        </div>
        <div v-else class="transaction-list">
          <div v-for="transaction in transactions" :key="transaction.id" class="transaction-item">
            <div class="transaction-header">
              <span class="transaction-round">第{{ transaction.round }}回合</span>
              <span class="transaction-type" :class="getTransactionTypeClass(transaction.type)">
                {{ transaction.type }}
              </span>
            </div>
            <div class="transaction-details">
              <span class="transaction-amount" :class="transaction.amount > 0 ? 'positive' : 'negative'">
                {{ transaction.amount > 0 ? '+' : '' }}{{ formatCurrency(transaction.amount) }}
              </span>
              <span class="transaction-desc">{{ transaction.description }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  investments: {
    type: Array,
    default: () => []
  },
  transactions: {
    type: Array,
    default: () => []
  }
})

// 折叠状态
const showInvestments = ref(true)
const showTransactions = ref(false)

// 计算属性
const totalInvested = computed(() => {
  return props.investments.reduce((sum, inv) => sum + inv.amount, 0)
})

const monthlyIncome = computed(() => {
  return props.investments
    .filter(inv => inv.type === 'MONTHLY')
    .reduce((sum, inv) => sum + inv.monthlyReturn, 0)
})

// 方法
const toggleInvestments = () => {
  showInvestments.value = !showInvestments.value
}

const toggleTransactions = () => {
  showTransactions.value = !showTransactions.value
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('zh-CN').format(amount) + ' CP'
}

const getTransactionTypeClass = (type) => {
  const typeMap = {
    '投资': 'investment',
    '消费': 'expense',
    '收益': 'income',
    '储蓄': 'savings',
    '收入': 'income',
    '其他': 'other'
  }
  return typeMap[type] || 'other'
}
</script>

<style scoped>
.investment-panel {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.collapsible-section {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: background 0.2s;
}

.section-header:hover {
  background: rgba(255, 255, 255, 0.15);
}

.section-header h3 {
  margin: 0;
  color: white;
  font-size: 1.1em;
}

.toggle-icon {
  color: white;
  font-size: 1.2em;
  transition: transform 0.2s;
}

.section-content {
  padding: 12px;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.empty-state {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  padding: 20px;
  font-style: italic;
}

.investment-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 8px;
  border-left: 3px solid #4CAF50;
}

.investment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.investment-name {
  color: white;
  font-weight: bold;
}

.investment-amount {
  color: #4CAF50;
  font-weight: bold;
}

.investment-details {
  display: flex;
  gap: 12px;
  font-size: 0.9em;
}

.monthly-return {
  color: #81C784;
}

.remaining-time {
  color: rgba(255, 255, 255, 0.7);
}

.investment-summary {
  margin-top: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  color: white;
  margin-bottom: 4px;
}

.transaction-list {
  max-height: 300px;
  overflow-y: auto;
}

.transaction-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 6px;
  border-left: 3px solid #2196F3;
}

.transaction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.transaction-round {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9em;
}

.transaction-type {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: bold;
}

.transaction-type.investment { background: #FF9800; color: white; }
.transaction-type.expense { background: #F44336; color: white; }
.transaction-type.income { background: #4CAF50; color: white; }
.transaction-type.savings { background: #2196F3; color: white; }
.transaction-type.other { background: #9E9E9E; color: white; }

.transaction-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.transaction-amount {
  font-weight: bold;
}

.transaction-amount.positive {
  color: #4CAF50;
}

.transaction-amount.negative {
  color: #F44336;
}

.transaction-desc {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9em;
}
</style>