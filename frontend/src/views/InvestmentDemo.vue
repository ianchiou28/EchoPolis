<template>
  <div class="investment-demo">
    <div class="demo-container">
      <h2>💰 投资管理演示</h2>
      
      <!-- 投资面板 -->
      <InvestmentPanel 
        :investments="sampleInvestments" 
        :transactions="sampleTransactions" 
      />
      
      <!-- 操作按钮 -->
      <div class="demo-actions">
        <button @click="addInvestment" class="action-btn investment-btn">
          📈 新增投资
        </button>
        <button @click="addTransaction" class="action-btn transaction-btn">
          💳 添加交易
        </button>
        <button @click="processReturns" class="action-btn return-btn">
          💰 处理月收益
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import InvestmentPanel from '../components/InvestmentPanel.vue'

// 示例数据
const sampleInvestments = ref([
  {
    name: '投资基金',
    amount: 600000,
    type: 'MONTHLY',
    monthlyReturn: 3616,
    remainingMonths: 30
  },
  {
    name: '股票投资',
    amount: 200000,
    type: 'LONG_TERM',
    monthlyReturn: 0,
    remainingMonths: 18
  }
])

const sampleTransactions = ref([
  {
    id: 1,
    round: 5,
    type: '收益',
    amount: 3616,
    description: '投资基金月收益'
  },
  {
    id: 2,
    round: 4,
    type: '收益',
    amount: 3616,
    description: '投资基金月收益'
  },
  {
    id: 3,
    round: 1,
    type: '投资',
    amount: -600000,
    description: '投资投资基金'
  },
  {
    id: 4,
    round: 1,
    type: '消费',
    amount: -100000,
    description: '购买支出'
  }
])

// 演示方法
const addInvestment = () => {
  const newInvestment = {
    name: '新理财产品',
    amount: Math.floor(Math.random() * 500000) + 50000,
    type: Math.random() > 0.5 ? 'MONTHLY' : 'LONG_TERM',
    monthlyReturn: Math.floor(Math.random() * 2000) + 500,
    remainingMonths: Math.floor(Math.random() * 24) + 6
  }
  sampleInvestments.value.push(newInvestment)
}

const addTransaction = () => {
  const types = ['投资', '消费', '收益', '收入']
  const type = types[Math.floor(Math.random() * types.length)]
  const amount = type === '收益' || type === '收入' 
    ? Math.floor(Math.random() * 10000) + 1000
    : -(Math.floor(Math.random() * 50000) + 5000)
  
  const newTransaction = {
    id: Date.now(),
    round: Math.floor(Math.random() * 10) + 1,
    type,
    amount,
    description: `${type}示例`
  }
  sampleTransactions.value.unshift(newTransaction)
}

const processReturns = () => {
  sampleInvestments.value.forEach(inv => {
    if (inv.remainingMonths > 0) {
      inv.remainingMonths--
      
      if (inv.type === 'MONTHLY' && inv.remainingMonths > 0) {
        const returnTransaction = {
          id: Date.now() + Math.random(),
          round: 6,
          type: '收益',
          amount: inv.monthlyReturn,
          description: `${inv.name}月收益`
        }
        sampleTransactions.value.unshift(returnTransaction)
      }
    }
  })
  
  // 移除到期投资
  sampleInvestments.value = sampleInvestments.value.filter(inv => inv.remainingMonths > 0)
}
</script>

<style scoped>
.investment-demo {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.demo-container {
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  color: white;
  text-align: center;
  margin-bottom: 30px;
  font-size: 2em;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.demo-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  color: white;
  font-size: 1em;
}

.investment-btn {
  background: linear-gradient(45deg, #FF9800, #FF5722);
}

.transaction-btn {
  background: linear-gradient(45deg, #2196F3, #3F51B5);
}

.return-btn {
  background: linear-gradient(45deg, #4CAF50, #8BC34A);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.action-btn:active {
  transform: translateY(0);
}
</style>