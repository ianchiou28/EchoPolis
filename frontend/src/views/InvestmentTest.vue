<template>
  <div class="investment-test">
    <div class="test-container">
      <h2>🧪 投资数据测试</h2>
      
      <!-- 用户输入 -->
      <div class="input-section">
        <input 
          v-model="username" 
          placeholder="输入用户名" 
          class="username-input"
        />
        <button @click="fetchData" class="fetch-btn">获取数据</button>
      </div>
      
      <!-- 状态显示 -->
      <div class="status-section">
        <p>状态: {{ status }}</p>
        <p v-if="error" class="error">错误: {{ error }}</p>
      </div>
      
      <!-- 投资面板 -->
      <InvestmentPanel 
        :investments="investments" 
        :transactions="transactions" 
      />
      
      <!-- 原始数据显示 -->
      <div class="raw-data">
        <h3>原始投资数据:</h3>
        <pre>{{ JSON.stringify(investments, null, 2) }}</pre>
        
        <h3>原始交易数据:</h3>
        <pre>{{ JSON.stringify(transactions, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import InvestmentPanel from '../components/InvestmentPanel.vue'

const username = ref('testuser')
const status = ref('等待获取数据')
const error = ref('')
const investments = ref([])
const transactions = ref([])

const fetchData = async () => {
  if (!username.value) {
    error.value = '请输入用户名'
    return
  }
  
  status.value = '正在获取数据...'
  error.value = ''
  
  try {
    // 获取投资数据
    const investmentResponse = await fetch(`http://127.0.0.1:8000/api/investments/${username.value}`)
    if (!investmentResponse.ok) {
      throw new Error(`投资数据获取失败: ${investmentResponse.status}`)
    }
    const investmentData = await investmentResponse.json()
    investments.value = investmentData
    
    // 获取交易数据
    const transactionResponse = await fetch(`http://127.0.0.1:8000/api/transactions/${username.value}`)
    if (!transactionResponse.ok) {
      throw new Error(`交易数据获取失败: ${transactionResponse.status}`)
    }
    const transactionData = await transactionResponse.json()
    transactions.value = transactionData
    
    status.value = `数据获取成功 - 投资: ${investments.value.length}项, 交易: ${transactions.value.length}条`
    
  } catch (err) {
    error.value = err.message
    status.value = '数据获取失败'
    console.error('获取数据失败:', err)
  }
}
</script>

<style scoped>
.investment-test {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.test-container {
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  color: white;
  text-align: center;
  margin-bottom: 30px;
}

.input-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  justify-content: center;
}

.username-input {
  padding: 10px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  min-width: 200px;
}

.fetch-btn {
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.fetch-btn:hover {
  background: #45a049;
}

.status-section {
  background: rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  color: white;
}

.error {
  color: #ff6b6b;
  font-weight: bold;
}

.raw-data {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 8px;
  margin-top: 20px;
  color: white;
}

.raw-data h3 {
  color: #4CAF50;
  margin-bottom: 10px;
}

.raw-data pre {
  background: rgba(0, 0, 0, 0.5);
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}
</style>