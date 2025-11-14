<template>
  <div class="world-page">
    <div class="page-header">
      <h1>🌆 沙盘世界</h1>
      <button class="back-btn btn btn-ghost" @click="$router.push('/home')">返回首页</button>
    </div>

    <div class="world-container">
      <div class="city-map card glass">
        <!-- 银行 -->
        <div class="building card" @click="selectBuilding('bank')">
          <div class="building-icon">🏦</div>
          <div class="building-name">银行</div>
        </div>

        <!-- 证券交易所 -->
        <div class="building card" @click="selectBuilding('stock')">
          <div class="building-icon">📈</div>
          <div class="building-name">交易所</div>
        </div>

        <!-- 房地产中心 -->
        <div class="building card" @click="selectBuilding('realestate')">
          <div class="building-icon">🏢</div>
          <div class="building-name">房产中心</div>
        </div>

        <!-- 商业区 -->
        <div class="building card" @click="selectBuilding('business')">
          <div class="building-icon">🏪</div>
          <div class="building-name">商业区</div>
        </div>

        <!-- 教育机构 -->
        <div class="building card" @click="selectBuilding('education')">
          <div class="building-icon">🎓</div>
          <div class="building-name">教育机构</div>
        </div>

        <!-- 政府 -->
        <div class="building card" @click="selectBuilding('government')">
          <div class="building-icon">🏛️</div>
          <div class="building-name">政府</div>
        </div>
      </div>

      <!-- 详情面板 -->
      <div v-if="selectedBuilding" class="detail-panel card glass">
        <div class="panel-header">
          <h2>{{ buildingInfo[selectedBuilding].icon }} {{ buildingInfo[selectedBuilding].name }}</h2>
          <button class="close-btn btn btn-ghost" @click="selectedBuilding = null">✕</button>
        </div>
        
        <div class="panel-content">
          <p class="description">{{ buildingInfo[selectedBuilding].description }}</p>
          
          <div class="actions">
            <div 
              v-for="action in buildingInfo[selectedBuilding].actions" 
              :key="action.id"
              class="action-card card"
              @click="performAction(action)"
            >
              <div class="action-name">{{ action.name }}</div>
              <div class="action-price">💰 {{ formatNumber(action.price) }}</div>
              <div class="action-desc">{{ action.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const selectedBuilding = ref(null)

const buildingInfo = {
  bank: {
    name: '银行',
    icon: '🏦',
    description: '办理贷款、存款、理财等金融业务',
    actions: [
      { id: 1, name: '申请贷款', price: 0, desc: '获得资金支持，需要按月还款' },
      { id: 2, name: '定期存款', price: 10000, desc: '稳定收益，年利3%' },
      { id: 3, name: '购买理财', price: 50000, desc: '中等风险，年利6%' }
    ]
  },
  stock: {
    name: '证券交易所',
    icon: '📈',
    description: '买卖股票、基金等金融产品',
    actions: [
      { id: 1, name: '科技股基金', price: 30000, desc: '高风险高回报，预期年化15%' },
      { id: 2, name: '蓝筹股组合', price: 50000, desc: '稳健投资，预期年化8%' },
      { id: 3, name: '指数基金', price: 20000, desc: '跟踪市场，预期年化10%' }
    ]
  },
  realestate: {
    name: '房地产中心',
    icon: '🏢',
    description: '购买住宅、商铺等不动产',
    actions: [
      { id: 1, name: '市中心公寓', price: 500000, desc: '升值潜力大，月租金3000' },
      { id: 2, name: '郊区别墅', price: 800000, desc: '居住舒适，月租金5000' },
      { id: 3, name: '商业店铺', price: 300000, desc: '稳定收益，月租金4000' }
    ]
  },
  business: {
    name: '商业区',
    icon: '🏪',
    description: '创业开店、投资商业项目',
    actions: [
      { id: 1, name: '开咖啡店', price: 100000, desc: '初期投入大，月收益8000' },
      { id: 2, name: '开便利店', price: 80000, desc: '稳定经营，月收益6000' },
      { id: 3, name: '投资餐厅', price: 150000, desc: '高风险，月收益12000' }
    ]
  },
  education: {
    name: '教育机构',
    icon: '🎓',
    description: '学习技能、提升能力',
    actions: [
      { id: 1, name: '金融课程', price: 15000, desc: '提升投资能力+20' },
      { id: 2, name: 'MBA课程', price: 50000, desc: '提升管理能力+50' },
      { id: 3, name: '编程培训', price: 20000, desc: '提升技术能力+30' }
    ]
  },
  government: {
    name: '政府',
    icon: '🏛️',
    description: '查看政策、申请补贴',
    actions: [
      { id: 1, name: '查看经济政策', price: 0, desc: '了解当前宏观经济形势' },
      { id: 2, name: '申请创业补贴', price: 0, desc: '符合条件可获得10000补贴' },
      { id: 3, name: '税务咨询', price: 0, desc: '优化税务规划' }
    ]
  }
}

const selectBuilding = (building) => {
  selectedBuilding.value = building
}

const performAction = async (action) => {
  try {
    const currentCharacter = localStorage.getItem('currentCharacter')
    if (!currentCharacter) {
      alert('请先选择角色')
      return
    }
    const char = JSON.parse(currentCharacter)
    
    const res = await axios.post('/api/world/action', {
      action_name: action.name,
      price: action.price,
      building: selectedBuilding.value,
      session_id: char.id
    })
    
    if (res.data.success) {
      alert(`✅ 操作成功\n\n${res.data.message}\n\n🤖 AI评价:\n${res.data.ai_comment}\n\n💰 剩余现金: ￥${formatNumber(res.data.new_balance)}\n📈 总资产: ￥${formatNumber(res.data.total_assets)}`)
      selectedBuilding.value = null
    } else {
      alert(`🤖 AI审核结果\n\n${res.data.message}\n\n${res.data.ai_advice}`)
    }
  } catch (error) {
    console.error('执行操作失败:', error)
    console.error('错误详情:', error.response?.data)
    alert(`操作失败: ${error.response?.data?.detail || error.message}`)
  }
}

const formatNumber = (num) => {
  return num?.toLocaleString('zh-CN') || '0'
}
</script>

<style scoped>
.world-page {
  width: 100%;
  min-height: 100vh;
  padding: 40px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: var(--text);
  font-size: 32px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.world-container {
  display: flex;
  gap: 30px;
}

.city-map {
  flex: 1;
  border-radius: var(--radius-lg);
  padding: 40px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  min-height: 600px;
}

.building {
  background: linear-gradient(135deg, color-mix(in srgb, var(--surface) 60%, transparent), var(--surface));
  border-radius: var(--radius-md);
  padding: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--dur-med) var(--ease-standard);
}

.building:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
  border-color: var(--highlight);
}

.building-icon {
  font-size: 60px;
  margin-bottom: 15px;
}

.building-name {
  font-size: 18px;
  font-weight: bold;
  color: var(--text);
}

.detail-panel {
  width: 400px;
  max-height: 600px;
  overflow-y: auto;
  padding: 25px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border);
}

.panel-header h2 {
  font-size: 24px;
  color: var(--text);
}

.close-btn { }

.description {
  color: var(--muted);
  margin-bottom: 20px;
  line-height: 1.6;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.action-card {
  padding: 20px;
  border-radius: var(--radius-md);
  transition: all var(--dur-fast) var(--ease-standard);
  border: 1px solid var(--border);
}

.action-card:hover {
  border-color: color-mix(in srgb, var(--primary-500) 35%, var(--border));
  transform: translateX(5px);
}

.action-name {
  font-size: 16px;
  font-weight: bold;
  color: var(--text);
  margin-bottom: 8px;
}

.action-price {
  font-size: 14px;
  color: var(--primary-400);
  font-weight: bold;
  margin-bottom: 8px;
}

.action-desc {
  font-size: 12px;
  color: var(--muted);
}
</style>
