<template>
  <div class="world-page">
    <div class="page-header">
      <h1>🌆 沙盘世界</h1>
      <button class="back-btn" @click="$router.push('/')">返回首页</button>
    </div>

    <div class="world-container">
      <div class="city-map">
        <!-- 银行 -->
        <div class="building bank" @click="selectBuilding('bank')">
          <div class="building-icon">🏦</div>
          <div class="building-name">银行</div>
        </div>

        <!-- 证券交易所 -->
        <div class="building stock" @click="selectBuilding('stock')">
          <div class="building-icon">📈</div>
          <div class="building-name">交易所</div>
        </div>

        <!-- 房地产中心 -->
        <div class="building realestate" @click="selectBuilding('realestate')">
          <div class="building-icon">🏢</div>
          <div class="building-name">房产中心</div>
        </div>

        <!-- 商业区 -->
        <div class="building business" @click="selectBuilding('business')">
          <div class="building-icon">🏪</div>
          <div class="building-name">商业区</div>
        </div>

        <!-- 教育机构 -->
        <div class="building education" @click="selectBuilding('education')">
          <div class="building-icon">🎓</div>
          <div class="building-name">教育机构</div>
        </div>

        <!-- 政府 -->
        <div class="building government" @click="selectBuilding('government')">
          <div class="building-icon">🏛️</div>
          <div class="building-name">政府</div>
        </div>
      </div>

      <!-- 详情面板 -->
      <div v-if="selectedBuilding" class="detail-panel">
        <div class="panel-header">
          <h2>{{ buildingInfo[selectedBuilding].icon }} {{ buildingInfo[selectedBuilding].name }}</h2>
          <button class="close-btn" @click="selectedBuilding = null">✕</button>
        </div>
        
        <div class="panel-content">
          <p class="description">{{ buildingInfo[selectedBuilding].description }}</p>
          
          <div class="actions">
            <div 
              v-for="action in buildingInfo[selectedBuilding].actions" 
              :key="action.id"
              class="action-card"
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

const router = useRouter()
const selectedBuilding = ref(null)

const buildingInfo = {
  bank: {
    name: '银行',
    icon: '🏦',
    description: '办理贷款、存款、理财等金融业务',
    actions: [
      { id: 1, name: '申请贷款', price: 0, desc: '获得资金支持，需按月还款' },
      { id: 2, name: '定期存款', price: 10000, desc: '稳定收益，年化3%' },
      { id: 3, name: '购买理财', price: 50000, desc: '中等风险，年化6%' }
    ]
  },
  stock: {
    name: '证券交易所',
    icon: '📈',
    description: '买卖股票、基金等金融产品',
    actions: [
      { id: 1, name: '科技股基金', price: 30000, desc: '高风险高收益，预期年化15%' },
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

const performAction = (action) => {
  console.log('执行操作:', action)
  // TODO: 调用API执行操作
  alert(`执行: ${action.name}`)
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
  color: white;
  font-size: 32px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.back-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  background: rgba(255,255,255,0.9);
  color: #ff9a9e;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: white;
  transform: translateY(-2px);
}

.world-container {
  display: flex;
  gap: 30px;
}

.city-map {
  flex: 1;
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 40px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  min-height: 600px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.building {
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  border-radius: 16px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.building:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

.building-icon {
  font-size: 60px;
  margin-bottom: 15px;
}

.building-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.detail-panel {
  width: 400px;
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  max-height: 600px;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.panel-header h2 {
  font-size: 24px;
  color: #333;
}

.close-btn {
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 50%;
  background: #f0f0f0;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #ff9a9e;
  color: white;
}

.description {
  color: #666;
  margin-bottom: 20px;
  line-height: 1.6;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.action-card {
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  padding: 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.action-card:hover {
  border-color: #ff9a9e;
  transform: translateX(5px);
}

.action-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.action-price {
  font-size: 14px;
  color: #ff9a9e;
  font-weight: bold;
  margin-bottom: 8px;
}

.action-desc {
  font-size: 12px;
  color: #666;
}
</style>
