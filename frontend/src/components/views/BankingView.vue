<template>
  <div class="view-container">
    <div class="view-header">
      <h2>银行系统 // BANKING_SYS</h2>
      <div class="header-line"></div>
    </div>

    <div class="content-grid">
      <!-- Left: Account Overview -->
      <div class="col-left">
        <div class="archive-card">
          <div class="archive-header">账户总览</div>
          <div class="archive-body">
            <div class="account-summary">
              <div class="account-item">
                <span class="account-label">现金余额</span>
                <span class="account-value cash">¥{{ formatNumber(cash) }}</span>
              </div>
              <div class="account-item">
                <span class="account-label">定期存款</span>
                <span class="account-value">¥{{ formatNumber(deposits) }}</span>
              </div>
              <div class="account-item">
                <span class="account-label">存款利息</span>
                <span class="account-value positive">+¥{{ formatNumber(monthlyInterest) }}/月</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Credit Score -->
        <div class="archive-card">
          <div class="archive-header">信用评估</div>
          <div class="archive-body">
            <div class="credit-display">
              <div class="credit-score" :class="creditLevel">
                {{ creditScore }}
              </div>
              <div class="credit-label">信用评分</div>
              <div class="credit-level">{{ creditLevelText }}</div>
            </div>
            <div class="credit-factors">
              <div class="factor">
                <span>还款记录</span>
                <span class="stars">{{ '★'.repeat(paymentHistory) }}{{ '☆'.repeat(5-paymentHistory) }}</span>
              </div>
              <div class="factor">
                <span>负债比例</span>
                <span class="stars">{{ '★'.repeat(debtRatio) }}{{ '☆'.repeat(5-debtRatio) }}</span>
              </div>
              <div class="factor">
                <span>资产规模</span>
                <span class="stars">{{ '★'.repeat(assetScale) }}{{ '☆'.repeat(5-assetScale) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Loan Status -->
        <div class="archive-card flex-grow">
          <div class="archive-header">贷款状态</div>
          <div class="archive-body scrollable">
            <div v-if="loans.length === 0" class="empty-state">
              暂无贷款记录
            </div>
            <div v-for="loan in loans" :key="loan.id" class="loan-item">
              <div class="loan-header">
                <span class="loan-type">{{ loan.type }}</span>
                <span class="loan-status" :class="loan.status">{{ loan.statusText }}</span>
              </div>
              <div class="loan-details">
                <div class="detail">
                  <span>本金</span>
                  <span>¥{{ formatNumber(loan.principal) }}</span>
                </div>
                <div class="detail">
                  <span>剩余</span>
                  <span>¥{{ formatNumber(loan.remaining) }}</span>
                </div>
                <div class="detail">
                  <span>月供</span>
                  <span class="negative">-¥{{ formatNumber(loan.monthlyPayment) }}</span>
                </div>
              </div>
              <div class="loan-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{width: ((1 - loan.remaining/loan.principal) * 100) + '%'}"></div>
                </div>
                <span class="progress-text">{{ loan.remainingMonths }}个月</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Banking Actions -->
      <div class="col-right">
        <!-- Deposit -->
        <div class="archive-card">
          <div class="archive-header">存款业务</div>
          <div class="archive-body">
            <div class="deposit-types">
              <div v-for="type in depositTypes" :key="type.id" 
                class="deposit-option"
                :class="{ selected: selectedDeposit === type.id }"
                @click="selectedDeposit = type.id">
                <div class="option-main">
                  <span class="option-name">{{ type.name }}</span>
                  <span class="option-rate">{{ type.rate }}%年化</span>
                </div>
                <div class="option-desc">{{ type.desc }}</div>
              </div>
            </div>
            <div class="action-row">
              <input type="number" v-model="depositAmount" placeholder="存款金额" class="amount-input" />
              <button class="term-btn" @click="makeDeposit" :disabled="!depositAmount || depositAmount > cash">
                存入
              </button>
            </div>
          </div>
        </div>

        <!-- Loan Application -->
        <div class="archive-card flex-grow">
          <div class="archive-header">贷款申请</div>
          <div class="archive-body">
            <div class="loan-types">
              <div v-for="type in loanTypes" :key="type.id"
                class="loan-option"
                :class="{ selected: selectedLoan === type.id, disabled: !canApplyLoan(type) }"
                @click="selectLoanType(type)">
                <div class="option-header">
                  <span class="option-name">{{ type.name }}</span>
                  <span class="option-limit">最高 ¥{{ formatNumber(type.maxAmount) }}</span>
                </div>
                <div class="option-details">
                  <span>利率: {{ type.rate }}%</span>
                  <span>期限: {{ type.termMonths }}个月</span>
                </div>
                <div class="option-req">{{ type.requirement }}</div>
              </div>
            </div>
            
            <div class="loan-calculator" v-if="selectedLoan">
              <div class="calc-row">
                <label>贷款金额</label>
                <input type="number" v-model="loanAmount" :max="selectedLoanType?.maxAmount" class="amount-input" />
              </div>
              <div class="calc-preview" v-if="loanAmount">
                <div class="preview-item">
                  <span>月供</span>
                  <span class="negative">-¥{{ formatNumber(calculatedMonthly) }}</span>
                </div>
                <div class="preview-item">
                  <span>总利息</span>
                  <span class="negative">-¥{{ formatNumber(calculatedInterest) }}</span>
                </div>
              </div>
              <button class="term-btn primary" @click="applyLoan" :disabled="!loanAmount">
                申请贷款
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Result Modal -->
    <div class="result-modal" v-if="showResult">
      <div class="result-content">
        <div class="result-icon" :class="resultData.success ? 'success' : 'error'">
          {{ resultData.success ? '✓' : '✗' }}
        </div>
        <div class="result-title">{{ resultData.title }}</div>
        <div class="result-message">{{ resultData.message }}</div>
        <button class="term-btn" @click="showResult = false">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from '../../stores/game'

const gameStore = useGameStore()

// 账户数据
const cash = computed(() => gameStore.assets?.cash || 0)
const deposits = ref(0)
const monthlyInterest = ref(0)

// 信用评分
const creditScore = ref(680)
const paymentHistory = ref(4)
const debtRatio = ref(3)
const assetScale = ref(3)

const creditLevel = computed(() => {
  if (creditScore.value >= 800) return 'excellent'
  if (creditScore.value >= 700) return 'good'
  if (creditScore.value >= 600) return 'fair'
  return 'poor'
})

const creditLevelText = computed(() => {
  if (creditScore.value >= 800) return '信用极好'
  if (creditScore.value >= 700) return '信用良好'
  if (creditScore.value >= 600) return '信用一般'
  return '信用较差'
})

// 贷款列表
const loans = ref([])

// 存款业务
const depositTypes = [
  { id: 'demand', name: '活期存款', rate: 0.35, desc: '随存随取，灵活方便' },
  { id: 'fixed_3m', name: '3个月定期', rate: 1.5, desc: '短期定存，略高收益' },
  { id: 'fixed_1y', name: '1年定期', rate: 2.5, desc: '中期定存，稳定增值' },
  { id: 'fixed_3y', name: '3年定期', rate: 3.5, desc: '长期定存，最高收益' }
]
const selectedDeposit = ref('demand')
const depositAmount = ref(null)

// 贷款业务
const loanTypes = [
  { id: 'personal', name: '个人消费贷', rate: 8, maxAmount: 50000, termMonths: 12, requirement: '信用分≥600' },
  { id: 'business', name: '创业贷款', rate: 6, maxAmount: 200000, termMonths: 36, requirement: '信用分≥700' },
  { id: 'mortgage', name: '房屋贷款', rate: 4.5, maxAmount: 1000000, termMonths: 360, requirement: '需有房产抵押' },
  { id: 'emergency', name: '应急借款', rate: 15, maxAmount: 10000, termMonths: 6, requirement: '无限制' }
]
const selectedLoan = ref(null)
const selectedLoanType = computed(() => loanTypes.find(l => l.id === selectedLoan.value))
const loanAmount = ref(null)

const calculatedMonthly = computed(() => {
  if (!selectedLoanType.value || !loanAmount.value) return 0
  const p = loanAmount.value
  const r = selectedLoanType.value.rate / 100 / 12
  const n = selectedLoanType.value.termMonths
  return Math.round((p * r * Math.pow(1+r, n)) / (Math.pow(1+r, n) - 1))
})

const calculatedInterest = computed(() => {
  if (!selectedLoanType.value || !loanAmount.value) return 0
  return calculatedMonthly.value * selectedLoanType.value.termMonths - loanAmount.value
})

// 结果弹窗
const showResult = ref(false)
const resultData = ref({})

const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num?.toLocaleString() || '0'
}

const canApplyLoan = (type) => {
  if (type.id === 'emergency') return true
  if (type.id === 'personal') return creditScore.value >= 600
  if (type.id === 'business') return creditScore.value >= 700
  if (type.id === 'mortgage') return false // 需要房产
  return false
}

const selectLoanType = (type) => {
  if (canApplyLoan(type)) {
    selectedLoan.value = type.id
    loanAmount.value = null
  }
}

const getSessionId = () => {
  try {
    const char = localStorage.getItem('currentCharacter')
    return char ? JSON.parse(char).id : null
  } catch { return null }
}

const makeDeposit = async () => {
  if (!depositAmount.value || depositAmount.value > cash.value) return
  
  try {
    const res = await fetch('/api/banking/deposit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: getSessionId(),
        amount: depositAmount.value,
        type: selectedDeposit.value
      })
    })
    const data = await res.json()
    
    if (data.success) {
      resultData.value = {
        success: true,
        title: '存款成功',
        message: `已存入 ¥${depositAmount.value.toLocaleString()}`
      }
      depositAmount.value = null
      await gameStore.loadAvatar()
      await loadBankingData()
    } else {
      throw new Error(data.error)
    }
  } catch (e) {
    resultData.value = {
      success: false,
      title: '存款失败',
      message: e.message || '请稍后重试'
    }
  }
  showResult.value = true
}

const applyLoan = async () => {
  if (!loanAmount.value || !selectedLoan.value) return
  
  try {
    const res = await fetch('/api/banking/loan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: getSessionId(),
        amount: loanAmount.value,
        type: selectedLoan.value,
        term_months: selectedLoanType.value.termMonths
      })
    })
    const data = await res.json()
    
    if (data.success) {
      resultData.value = {
        success: true,
        title: '贷款批准',
        message: `已放款 ¥${loanAmount.value.toLocaleString()}，月供 ¥${calculatedMonthly.value.toLocaleString()}`
      }
      loanAmount.value = null
      selectedLoan.value = null
      await gameStore.loadAvatar()
      await loadBankingData()
    } else {
      throw new Error(data.error)
    }
  } catch (e) {
    resultData.value = {
      success: false,
      title: '贷款申请失败',
      message: e.message || '请检查资质条件'
    }
  }
  showResult.value = true
}

const loadBankingData = async () => {
  const sessionId = getSessionId()
  if (!sessionId) return
  
  try {
    const [depositRes, loanRes, creditRes] = await Promise.all([
      fetch(`/api/banking/deposits/${sessionId}`).then(r => r.json()),
      fetch(`/api/banking/loans/${sessionId}`).then(r => r.json()),
      fetch(`/api/banking/credit/${sessionId}`).then(r => r.json())
    ])
    
    if (depositRes.success) {
      deposits.value = depositRes.total || 0
      monthlyInterest.value = depositRes.monthly_interest || 0
    }
    
    if (loanRes.success) {
      loans.value = loanRes.loans || []
    }
    
    if (creditRes.success) {
      creditScore.value = creditRes.score || 680
    }
  } catch (e) {
    console.error('加载银行数据失败:', e)
  }
}

onMounted(() => {
  loadBankingData()
})
</script>

<style scoped>
.view-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
}

.view-header {
  margin-bottom: 16px;
  flex-shrink: 0;
}

.view-header h2 {
  font-size: 24px;
  font-weight: 900;
  margin: 0 0 8px 0;
}

.header-line {
  height: 3px;
  background: var(--term-accent);
  width: 60px;
}

.content-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  overflow: hidden;
  min-height: 0;
}

.col-left, .col-right {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  min-height: 0;
}

.archive-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  flex-shrink: 0;
}

.archive-card.flex-grow {
  flex: 1 1 auto;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 120px;
}

.archive-header {
  padding: 10px 14px;
  font-weight: 800;
  font-size: 12px;
  border-bottom: 1px solid var(--term-border);
  background: rgba(0,0,0,0.02);
  flex-shrink: 0;
}

.archive-body {
  padding: 14px;
  flex: 1;
  overflow-y: auto;
}

.archive-body.scrollable {
  flex: 1;
  overflow-y: auto;
}

/* Account Summary */
.account-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.account-label {
  font-size: 12px;
  color: var(--term-text-secondary);
}

.account-value {
  font-size: 18px;
  font-weight: 800;
  font-family: 'JetBrains Mono', monospace;
}

.account-value.cash {
  color: var(--term-accent);
}

.account-value.positive {
  color: #10b981;
}

/* Credit Score */
.credit-display {
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px dashed var(--term-border);
  margin-bottom: 16px;
}

.credit-score {
  font-size: 48px;
  font-weight: 900;
  font-family: 'JetBrains Mono', monospace;
}

.credit-score.excellent { color: #10b981; }
.credit-score.good { color: #3b82f6; }
.credit-score.fair { color: #f59e0b; }
.credit-score.poor { color: #ef4444; }

.credit-label {
  font-size: 11px;
  color: var(--term-text-secondary);
  margin-top: 4px;
}

.credit-level {
  font-size: 14px;
  font-weight: 700;
  margin-top: 8px;
}

.credit-factors {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.factor {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.stars {
  color: #f59e0b;
  letter-spacing: 2px;
}

/* Loans */
.loan-item {
  padding: 12px;
  border: 1px solid var(--term-border);
  margin-bottom: 12px;
}

.loan-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.loan-type {
  font-weight: 700;
}

.loan-status {
  font-size: 10px;
  padding: 2px 6px;
  border: 1px solid;
}

.loan-status.active { color: #3b82f6; border-color: #3b82f6; }
.loan-status.overdue { color: #ef4444; border-color: #ef4444; }

.loan-details {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.detail {
  display: flex;
  flex-direction: column;
  font-size: 11px;
}

.detail span:first-child {
  color: var(--term-text-secondary);
}

.negative { color: #ef4444; }

.loan-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: rgba(0,0,0,0.1);
}

.progress-fill {
  height: 100%;
  background: var(--term-accent);
}

.progress-text {
  font-size: 10px;
  color: var(--term-text-secondary);
}

/* Deposit Options */
.deposit-types {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.deposit-option, .loan-option {
  padding: 10px;
  border: 1px solid var(--term-border);
  cursor: pointer;
  transition: all 0.2s;
}

.deposit-option:hover, .loan-option:hover:not(.disabled) {
  border-color: var(--term-accent);
}

.deposit-option.selected, .loan-option.selected {
  border-color: var(--term-accent);
  background: rgba(0,0,0,0.03);
}

.loan-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.option-main, .option-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.option-name {
  font-weight: 700;
}

.option-rate, .option-limit {
  font-size: 11px;
  color: var(--term-accent);
}

.option-desc, .option-req {
  font-size: 11px;
  color: var(--term-text-secondary);
}

.option-details {
  display: flex;
  gap: 12px;
  font-size: 11px;
  margin-bottom: 4px;
}

/* Action Row */
.action-row {
  display: flex;
  gap: 8px;
}

.amount-input {
  flex: 1;
  padding: 10px;
  border: 2px solid var(--term-border);
  background: var(--term-bg);
  font-family: 'JetBrains Mono', monospace;
  color: #000;
}

.term-btn {
  padding: 10px 20px;
  font-weight: 700;
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  cursor: pointer;
}

.term-btn:hover:not(:disabled) {
  background: var(--term-accent);
  color: #000;
}

.term-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.term-btn.primary {
  background: var(--term-accent);
  color: #000;
  width: 100%;
  margin-top: 12px;
}

/* Loan Calculator */
.loan-calculator {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed var(--term-border);
}

.calc-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.calc-row label {
  font-size: 11px;
  color: var(--term-text-secondary);
}

.calc-preview {
  display: flex;
  justify-content: space-around;
  padding: 12px;
  background: rgba(0,0,0,0.03);
  margin-bottom: 12px;
}

.preview-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 12px;
}

.preview-item span:last-child {
  font-weight: 700;
  font-size: 14px;
}

/* Result Modal */
.result-modal {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.result-content {
  background: var(--term-panel-bg);
  border: 3px solid var(--term-border);
  padding: 32px;
  text-align: center;
  min-width: 300px;
}

.result-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.result-icon.success { color: #10b981; }
.result-icon.error { color: #ef4444; }

.result-title {
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 8px;
}

.result-message {
  font-size: 14px;
  color: var(--term-text-secondary);
  margin-bottom: 20px;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: var(--term-text-secondary);
  font-size: 12px;
}

/* Loan Types */
.loan-types {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 280px;
  overflow-y: auto;
}
</style>
