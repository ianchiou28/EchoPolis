<template>
  <div class="operation-panel glass-panel">
    <div class="panel-header">
      <div class="header-left">
        <span class="icon">{{ districtIcon }}</span>
        <div>
          <h3>{{ districtName }}</h3>
          <p class="subtitle">{{ districtTagline }}</p>
        </div>
      </div>
      <button class="btn-close" @click="$emit('close')">✕</button>
    </div>

    <div class="panel-body">
      <!-- 金融区操作 -->
      <div v-if="districtId === 'finance'" class="operations-grid">
        <div class="operation-card" @click.stop="handleOperation('deposit')">
          <div class="card-icon">💰</div>
          <h4>定期存款</h4>
          <p>稳健收益，保本保息</p>
          <div class="card-meta">
            <span class="badge success">低风险</span>
            <span class="rate">3-5% 年化</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('loan')">
          <div class="card-icon">💳</div>
          <h4>银行贷款</h4>
          <p>获取资金支持</p>
          <div class="card-meta">
            <span class="badge warning">需审核</span>
            <span class="rate">6-12% 利率</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('credit_check')">
          <div class="card-icon">📊</div>
          <h4>信用查询</h4>
          <p>查看当前信用分</p>
          <div class="card-meta">
            <span class="badge info">免费</span>
          </div>
        </div>
      </div>

      <!-- 交易所操作 -->
      <div v-if="districtId === 'tech'" class="operations-grid">
        <div class="operation-card" @click.stop="handleOperation('stock_trade')">
          <div class="card-icon">📈</div>
          <h4>股票交易</h4>
          <p>买卖上市公司股票</p>
          <div class="card-meta">
            <span class="badge danger">高风险</span>
            <span class="rate">±20% 波动</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('fund_invest')">
          <div class="card-icon">📊</div>
          <h4>基金申购</h4>
          <p>专业团队管理</p>
          <div class="card-meta">
            <span class="badge warning">中风险</span>
            <span class="rate">8-15% 年化</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('futures')">
          <div class="card-icon">⚡</div>
          <h4>期货合约</h4>
          <p>杠杆交易，高收益</p>
          <div class="card-meta">
            <span class="badge danger">极高风险</span>
            <span class="rate">10x 杠杆</span>
          </div>
        </div>
      </div>

      <!-- 房产中心操作 -->
      <div v-if="districtId === 'housing'" class="operations-grid">
        <div class="operation-card" @click.stop="handleOperation('buy_house')">
          <div class="card-icon">🏠</div>
          <h4>购买房产</h4>
          <p>长期保值增值</p>
          <div class="card-meta">
            <span class="badge success">优质资产</span>
            <span class="rate">5-10% 年增</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('rent')">
          <div class="card-icon">🔑</div>
          <h4>租赁房屋</h4>
          <p>灵活居住选择</p>
          <div class="card-meta">
            <span class="badge info">月付</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('property_manage')">
          <div class="card-icon">🏢</div>
          <h4>物业管理</h4>
          <p>查看持有房产</p>
          <div class="card-meta">
            <span class="badge info">管理</span>
          </div>
        </div>
      </div>

      <!-- 教育区操作 -->
      <div v-if="districtId === 'learning'" class="operations-grid">
        <div class="operation-card" @click.stop="handleOperation('skill_course')">
          <div class="card-icon">📚</div>
          <h4>技能培训</h4>
          <p>提升职业技能</p>
          <div class="card-meta">
            <span class="badge success">长期受益</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('finance_course')">
          <div class="card-icon">💡</div>
          <h4>金融课程</h4>
          <p>学习投资知识</p>
          <div class="card-meta">
            <span class="badge info">提升理财能力</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('certificate')">
          <div class="card-icon">🎓</div>
          <h4>考取证书</h4>
          <p>获得专业认证</p>
          <div class="card-meta">
            <span class="badge warning">需考试</span>
          </div>
        </div>
      </div>

      <!-- 文娱区操作 -->
      <div v-if="districtId === 'leisure'" class="operations-grid">
        <div class="operation-card" @click.stop="handleOperation('entertainment')">
          <div class="card-icon">🎬</div>
          <h4>休闲娱乐</h4>
          <p>放松身心，恢复精力</p>
          <div class="card-meta">
            <span class="badge success">+精力</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('social')">
          <div class="card-icon">🤝</div>
          <h4>社交活动</h4>
          <p>拓展人脉关系</p>
          <div class="card-meta">
            <span class="badge info">+人脉</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('luxury')">
          <div class="card-icon">💎</div>
          <h4>奢侈消费</h4>
          <p>提升幸福感</p>
          <div class="card-meta">
            <span class="badge warning">高消费</span>
          </div>
        </div>
      </div>

      <!-- 能源区操作 -->
      <div v-if="districtId === 'green'" class="operations-grid">
        <div class="operation-card" @click.stop="handleOperation('green_invest')">
          <div class="card-icon">🌱</div>
          <h4>绿色投资</h4>
          <p>ESG可持续项目</p>
          <div class="card-meta">
            <span class="badge success">环保</span>
            <span class="rate">6-10% 年化</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('energy_stock')">
          <div class="card-icon">⚡</div>
          <h4>新能源股票</h4>
          <p>投资清洁能源</p>
          <div class="card-meta">
            <span class="badge warning">中高风险</span>
          </div>
        </div>
        
        <div class="operation-card" @click.stop="handleOperation('carbon_trade')">
          <div class="card-icon">🌍</div>
          <h4>碳交易</h4>
          <p>碳排放权交易</p>
          <div class="card-meta">
            <span class="badge info">新兴市场</span>
          </div>
        </div>
      </div>
    </div>

  </div>

  <!-- 操作详情弹窗 - 使用Teleport移到body独立显示 -->
  <Teleport to="body">
    <transition name="modal">
      <div v-if="showOperationModal" class="operation-modal-standalone" @click="closeOperationModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>{{ currentOperation?.title }}</h3>
            <button class="btn-close" @click="closeOperationModal">✕</button>
          </div>
          <div class="modal-body">
            <p>{{ currentOperation?.description }}</p>
            
            <div class="input-group" v-if="currentOperation?.needsAmount">
              <label>金额</label>
              <input 
                v-model.number="operationAmount" 
                type="number" 
                placeholder="请输入金额"
                class="input"
              />
            </div>

            <div class="operation-info">
              <div class="info-item">
                <span>预计成本</span>
                <span class="value">¥{{ formatNumber(operationAmount || currentOperation?.defaultAmount || 0) }}</span>
              </div>
              <div class="info-item" v-if="currentOperation?.expectedReturn">
                <span>预期收益</span>
                <span class="value positive">+{{ currentOperation.expectedReturn }}</span>
              </div>
              <div class="info-item" v-if="currentOperation?.riskLevel">
                <span>风险等级</span>
                <span :class="['badge', currentOperation.riskLevel]">
                  {{ riskLevelText(currentOperation.riskLevel) }}
                </span>
              </div>
            </div>

            <div class="ai-advice" v-if="aiAdvice">
              <div class="advice-header">
                <span class="icon">🤖</span>
                <strong>AI 建议</strong>
              </div>
              <p>{{ aiAdvice }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn ghost" @click="closeOperationModal">取消</button>
            <button 
              class="btn primary" 
              @click="confirmOperation"
              :disabled="isExecuting">
              {{ isExecuting ? '执行中...' : '确认执行' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

const props = defineProps({
  districtId: {
    type: String,
    required: true
  },
  districtName: String,
  districtTagline: String,
  districtIcon: String,
  sessionId: String,
  currentCash: Number
})

const emit = defineEmits(['close', 'operation-complete'])

const showOperationModal = ref(false)
const currentOperation = ref(null)
const operationAmount = ref(0)
const aiAdvice = ref('')
const isExecuting = ref(false)

const operationConfigs = {
  // 金融区
  deposit: { 
    title: '定期存款', 
    description: '存入资金获取稳定利息收益',
    needsAmount: true,
    defaultAmount: 10000,
    expectedReturn: '3-5% 年化',
    riskLevel: 'success'
  },
  loan: { 
    title: '银行贷款', 
    description: '向银行申请贷款，需要支付利息',
    needsAmount: true,
    defaultAmount: 50000,
    riskLevel: 'warning'
  },
  credit_check: { 
    title: '信用查询', 
    description: '查看当前信用评分和借贷能力',
    needsAmount: false
  },
  
  // 交易所
  stock_trade: { 
    title: '股票交易', 
    description: '买入或卖出股票，获取价差收益',
    needsAmount: true,
    defaultAmount: 20000,
    expectedReturn: '±20%',
    riskLevel: 'danger'
  },
  fund_invest: { 
    title: '基金申购', 
    description: '购买基金份额，由专业团队管理',
    needsAmount: true,
    defaultAmount: 30000,
    expectedReturn: '8-15% 年化',
    riskLevel: 'warning'
  },
  futures: { 
    title: '期货合约', 
    description: '杠杆交易期货，高风险高收益',
    needsAmount: true,
    defaultAmount: 50000,
    expectedReturn: '±100%',
    riskLevel: 'danger'
  },
  
  // 房产中心
  buy_house: { 
    title: '购买房产', 
    description: '购买住宅或商业地产',
    needsAmount: true,
    defaultAmount: 500000,
    expectedReturn: '5-10% 年增',
    riskLevel: 'success'
  },
  rent: { 
    title: '租赁房屋', 
    description: '支付月租，获得居住权',
    needsAmount: true,
    defaultAmount: 3000
  },
  property_manage: { 
    title: '物业管理', 
    description: '查看和管理持有的房产',
    needsAmount: false
  },
  
  // 教育区
  skill_course: { 
    title: '技能培训', 
    description: '学习新技能提升职业能力',
    needsAmount: true,
    defaultAmount: 5000,
    expectedReturn: '提升收入潜力'
  },
  finance_course: { 
    title: '金融课程', 
    description: '学习投资理财知识',
    needsAmount: true,
    defaultAmount: 3000,
    expectedReturn: '提升投资能力'
  },
  certificate: { 
    title: '考取证书', 
    description: '获得专业资格认证',
    needsAmount: true,
    defaultAmount: 8000
  },
  
  // 文娱区
  entertainment: { 
    title: '休闲娱乐', 
    description: '看电影、旅游等放松活动',
    needsAmount: true,
    defaultAmount: 2000,
    expectedReturn: '+10 精力'
  },
  social: { 
    title: '社交活动', 
    description: '参加聚会，拓展人脉',
    needsAmount: true,
    defaultAmount: 1500,
    expectedReturn: '+5 人脉值'
  },
  luxury: { 
    title: '奢侈消费', 
    description: '购买奢侈品提升幸福感',
    needsAmount: true,
    defaultAmount: 10000,
    expectedReturn: '+20 幸福感'
  },
  
  // 能源区
  green_invest: { 
    title: '绿色投资', 
    description: '投资环保可持续项目',
    needsAmount: true,
    defaultAmount: 40000,
    expectedReturn: '6-10% 年化',
    riskLevel: 'success'
  },
  energy_stock: { 
    title: '新能源股票', 
    description: '投资清洁能源公司股票',
    needsAmount: true,
    defaultAmount: 25000,
    expectedReturn: '10-20%',
    riskLevel: 'warning'
  },
  carbon_trade: { 
    title: '碳交易', 
    description: '参与碳排放权交易',
    needsAmount: true,
    defaultAmount: 15000,
    riskLevel: 'info'
  }
}

const handleOperation = (operationType) => {
  console.log('handleOperation called:', operationType)
  currentOperation.value = {
    type: operationType,
    ...operationConfigs[operationType]
  }
  operationAmount.value = currentOperation.value.defaultAmount || 0
  showOperationModal.value = true
  console.log('showOperationModal set to:', showOperationModal.value)
  
  // 获取AI建议
  fetchAIAdvice(operationType)
}

const fetchAIAdvice = async (operationType) => {
  aiAdvice.value = '正在获取AI建议...'
  
  // 模拟AI建议
  setTimeout(() => {
    const advices = {
      deposit: '根据当前市场利率，建议存入中长期定期以获取更高收益',
      loan: '您的信用良好，可以申请贷款。建议用于投资而非消费',
      stock_trade: '当前市场波动较大，建议谨慎操作，设置止损线',
      buy_house: '该区域房价处于合理区间，适合长期持有',
      skill_course: '投资教育是最稳定的投资，建议选择市场需求大的技能'
    }
    aiAdvice.value = advices[operationType] || '这是一个不错的选择，符合您当前的财务状况'
  }, 800)
}

const confirmOperation = async () => {
  if (currentOperation.value.needsAmount && (!operationAmount.value || operationAmount.value <= 0)) {
    alert('请输入有效金额')
    return
  }

  if (currentOperation.value.needsAmount && operationAmount.value > props.currentCash) {
    alert('现金不足，无法执行此操作')
    return
  }

  isExecuting.value = true

  try {
    const response = await axios.post('/api/world/action', {
      session_id: props.sessionId,
      action_name: currentOperation.value.title,
      action: currentOperation.value.type,
      price: operationAmount.value || 0,
      building: props.districtId
    })

    if (response.data.success) {
      alert(`操作成功！\n${response.data.message}\n${response.data.ai_comment || ''}`)
      emit('operation-complete', response.data)
      closeOperationModal()
      emit('close')
    } else {
      alert(`操作失败：${response.data.message}\n${response.data.ai_advice || ''}`)
    }
  } catch (error) {
    console.error('操作执行失败:', error)
    alert('操作失败：' + (error.response?.data?.detail || error.message))
  } finally {
    isExecuting.value = false
  }
}

const closeOperationModal = () => {
  showOperationModal.value = false
  currentOperation.value = null
  operationAmount.value = 0
  aiAdvice.value = ''
}

const formatNumber = (num) => {
  return Number(num || 0).toLocaleString('zh-CN')
}

const riskLevelText = (level) => {
  const map = {
    success: '低风险',
    info: '极低风险',
    warning: '中等风险',
    danger: '高风险'
  }
  return map[level] || '未知'
}
</script>

<style scoped>
.operation-panel {
  background: rgba(10,14,39,0.85);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(59,130,246,0.4);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(2,6,23,0.9);
  position: relative;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(59,130,246,0.2);
  background: rgba(59,130,246,0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left .icon {
  font-size: 40px;
}

.header-left h3 {
  margin: 0 0 4px 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--text);
}

.subtitle {
  margin: 0;
  font-size: 13px;
  color: rgba(255,255,255,0.6);
}

.btn-close {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(148,163,184,0.3);
  background: rgba(15,23,42,0.8);
  color: var(--text);
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: rgba(239,68,68,0.3);
  border-color: #ef4444;
  transform: rotate(90deg);
}

.panel-body {
  padding: 24px;
  max-height: calc(80vh - 100px);
  overflow-y: auto;
}

.operations-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

@media (max-width: 768px) {
  .operations-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .operations-grid {
    grid-template-columns: 1fr;
  }
}

.operation-card {
  padding: 20px;
  border-radius: 14px;
  background: rgba(15,23,42,0.7);
  border: 1px solid rgba(148,163,184,0.3);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.operation-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(59,130,246,0.3), transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.operation-card:hover {
  border-color: rgba(59,130,246,0.6);
  background: rgba(59,130,246,0.15);
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(59,130,246,0.4);
}

.operation-card:hover::before {
  opacity: 1;
}

.card-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.operation-card h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.operation-card p {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: rgba(255,255,255,0.7);
  line-height: 1.5;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
}

.badge.success {
  background: rgba(34,197,94,0.2);
  color: #22c55e;
}

.badge.info {
  background: rgba(59,130,246,0.2);
  color: #3b82f6;
}

.badge.warning {
  background: rgba(251,191,36,0.2);
  color: #fbbf24;
}

.badge.danger {
  background: rgba(239,68,68,0.2);
  color: #ef4444;
}

.rate {
  font-size: 12px;
  color: rgba(255,255,255,0.6);
}

/* 操作弹窗 - 独立弹窗通过Teleport渲染到body */
.operation-modal-standalone {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.85);
  backdrop-filter: blur(10px);
  padding: 20px;
  overflow-y: auto;
}

.modal-content {
  width: min(500px, 90vw);
  max-height: 90vh;
  background: rgba(10,14,39,0.95);
  border: 1px solid rgba(59,130,246,0.4);
  border-radius: 20px;
  box-shadow: 0 25px 70px rgba(0,0,0,0.8);
  display: flex;
  flex-direction: column;
  margin: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(59,130,246,0.2);
  background: rgba(59,130,246,0.1);
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-body > p {
  margin: 0 0 20px 0;
  color: rgba(255,255,255,0.8);
  line-height: 1.6;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(15,23,42,0.8);
  border: 1px solid rgba(148,163,184,0.3);
  color: var(--text);
  font-size: 16px;
  font-family: inherit;
}

.input:focus {
  outline: none;
  border-color: rgb(59,130,246);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.2);
}

.operation-info {
  padding: 16px;
  border-radius: 12px;
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(148,163,184,0.2);
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
}

.info-item:not(:last-child) {
  border-bottom: 1px solid rgba(148,163,184,0.1);
}

.info-item .value {
  font-weight: 600;
}

.info-item .value.positive {
  color: #10b981;
}

.ai-advice {
  padding: 16px;
  border-radius: 12px;
  background: rgba(99,102,241,0.15);
  border: 1px solid rgba(99,102,241,0.4);
}

.advice-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
  color: rgb(167,139,250);
}

.ai-advice p {
  margin: 0;
  font-size: 13px;
  color: rgba(255,255,255,0.85);
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid rgba(59,130,246,0.2);
  background: rgba(15,23,42,0.5);
}

.btn {
  flex: 1;
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn.primary {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  border: none;
}

.btn.primary:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(59,130,246,0.6);
  transform: translateY(-2px);
}

.btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.ghost {
  background: rgba(15,23,42,0.8);
  border: 1px solid rgba(148,163,184,0.3);
  color: var(--text);
}

.btn.ghost:hover {
  background: rgba(148,163,184,0.2);
  border-color: rgba(148,163,184,0.5);
}

/* 动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content {
  transform: scale(0.9) translateY(20px);
}

.modal-leave-to .modal-content {
  transform: scale(0.9) translateY(20px);
}
</style>
