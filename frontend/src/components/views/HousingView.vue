<template>
  <div class="view-container">
    <div class="view-header">
      <h2>房产中心 // REAL_ESTATE</h2>
      <div class="header-line"></div>
    </div>

    <div class="content-grid">
      <!-- Left: My Properties -->
      <div class="col-left">
        <div class="archive-card">
          <div class="archive-header">我的房产</div>
          <div class="archive-body">
            <div v-if="myProperties.length === 0" class="empty-state">
              <div class="empty-icon">🏠</div>
              <p>暂无房产，可在下方市场购置</p>
            </div>
            <div v-for="prop in myProperties" :key="prop.id" class="property-card owned">
              <div class="prop-image">{{ prop.icon }}</div>
              <div class="prop-info">
                <div class="prop-name">{{ prop.name }}</div>
                <div class="prop-type">{{ prop.type }}</div>
                <div class="prop-stats">
                  <span class="stat">购入价: ¥{{ formatNumber(prop.purchasePrice) }}</span>
                  <span class="stat">当前估值: ¥{{ formatNumber(prop.currentValue) }}</span>
                </div>
                <div class="prop-income" v-if="prop.monthlyRent">
                  <span class="positive">+¥{{ formatNumber(prop.monthlyRent) }}/月 租金</span>
                </div>
              </div>
              <div class="prop-actions">
                <button class="term-btn small" @click="sellProperty(prop)" v-if="!prop.isRented">
                  出售
                </button>
                <button class="term-btn small" @click="rentOut(prop)" v-if="!prop.isRented && !prop.isSelfLiving">
                  出租
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Living Status -->
        <div class="archive-card">
          <div class="archive-header">居住状态</div>
          <div class="archive-body">
            <div class="living-status">
              <div class="status-icon">{{ livingStatus.icon }}</div>
              <div class="status-info">
                <div class="status-type">{{ livingStatus.type }}</div>
                <div class="status-detail">{{ livingStatus.detail }}</div>
                <div class="status-cost" :class="livingStatus.cost > 0 ? 'negative' : 'positive'">
                  {{ livingStatus.cost > 0 ? '-' : '' }}¥{{ formatNumber(Math.abs(livingStatus.cost)) }}/月
                </div>
              </div>
            </div>
            <div class="living-effects">
              <div class="effect">
                <span class="label">幸福度影响</span>
                <span class="value" :class="livingStatus.happiness >= 0 ? 'positive' : 'negative'">
                  {{ livingStatus.happiness >= 0 ? '+' : '' }}{{ livingStatus.happiness }}
                </span>
              </div>
              <div class="effect">
                <span class="label">社会地位</span>
                <span class="value">{{ livingStatus.status }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Mortgage -->
        <div class="archive-card flex-grow">
          <div class="archive-header">房贷状态</div>
          <div class="archive-body scrollable">
            <div v-if="mortgages.length === 0" class="empty-state">
              暂无房贷
            </div>
            <div v-for="m in mortgages" :key="m.id" class="mortgage-item">
              <div class="mortgage-header">
                <span>{{ m.propertyName }}</span>
                <span class="rate">{{ m.rate }}%</span>
              </div>
              <div class="mortgage-details">
                <div class="detail-row">
                  <span>贷款总额</span>
                  <span>¥{{ formatNumber(m.total) }}</span>
                </div>
                <div class="detail-row">
                  <span>已还本金</span>
                  <span>¥{{ formatNumber(m.paid) }}</span>
                </div>
                <div class="detail-row">
                  <span>剩余本金</span>
                  <span>¥{{ formatNumber(m.remaining) }}</span>
                </div>
                <div class="detail-row highlight">
                  <span>月供</span>
                  <span class="negative">-¥{{ formatNumber(m.monthly) }}</span>
                </div>
              </div>
              <div class="mortgage-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{width: (m.paid / m.total * 100) + '%'}"></div>
                </div>
                <span>{{ m.remainingMonths }}个月</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Property Market (Accordion) -->
      <div class="col-right accordion-column">
        <!-- 房产市场 -->
        <div 
          class="accordion-card" 
          :class="{ expanded: rightPanel === 'buy', collapsed: rightPanel && rightPanel !== 'buy' }"
          @click="rightPanel !== 'buy' && (rightPanel = 'buy')"
        >
          <div class="accordion-header">
            <span class="accordion-icon">🏠</span>
            <span class="accordion-title">房产市场</span>
            <div class="filter-tabs" v-if="rightPanel === 'buy'" @click.stop>
              <span v-for="t in propertyTypes" :key="t.id"
                :class="['tab', { active: currentType === t.id }]"
                @click="currentType = t.id">{{ t.name }}</span>
            </div>
            <span class="accordion-arrow">{{ rightPanel === 'buy' ? '▼' : '▶' }}</span>
          </div>
          <div class="accordion-body" v-show="rightPanel === 'buy'">
            <div v-for="prop in filteredProperties" :key="prop.id" class="property-listing">
              <div class="listing-main">
                <div class="listing-icon">{{ prop.icon }}</div>
                <div class="listing-info">
                  <div class="listing-name">{{ prop.name }}</div>
                  <div class="listing-desc">{{ prop.description }}</div>
                  <div class="listing-tags">
                    <span class="tag">{{ prop.area }}㎡</span>
                    <span class="tag">{{ prop.location }}</span>
                    <span class="tag rent" v-if="prop.expectedRent">租金 ¥{{ formatNumber(prop.expectedRent) }}/月</span>
                  </div>
                </div>
              </div>
              <div class="listing-price">
                <div class="price">¥{{ formatNumber(prop.price) }}</div>
                <div class="price-per">{{ formatNumber(Math.round(prop.price / prop.area)) }}/㎡</div>
                <button class="term-btn" @click.stop="buyProperty(prop)" :disabled="cash < prop.price * 0.3">
                  购买
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 租房市场 -->
        <div 
          class="accordion-card" 
          :class="{ expanded: rightPanel === 'rent', collapsed: rightPanel && rightPanel !== 'rent' }"
          @click="rightPanel !== 'rent' && (rightPanel = 'rent')"
        >
          <div class="accordion-header">
            <span class="accordion-icon">🔑</span>
            <span class="accordion-title">租房市场</span>
            <span class="accordion-arrow">{{ rightPanel === 'rent' ? '▼' : '▶' }}</span>
          </div>
          <div class="accordion-body" v-show="rightPanel === 'rent'">
            <div v-for="rent in rentalOptions" :key="rent.id" class="rental-option"
              :class="{ current: currentRental?.id === rent.id }">
              <div class="rental-main">
                <div class="rental-icon">{{ rent.icon }}</div>
                <div class="rental-info">
                  <div class="rental-name">{{ rent.name }}</div>
                  <div class="rental-desc">{{ rent.description }}</div>
                </div>
              </div>
              <div class="rental-price">
                <div class="monthly">¥{{ formatNumber(rent.monthly) }}/月</div>
                <div class="effects">
                  <span :class="rent.happiness >= 0 ? 'positive' : 'negative'">
                    幸福{{ rent.happiness >= 0 ? '+' : '' }}{{ rent.happiness }}
                  </span>
                </div>
                <button class="term-btn small" @click.stop="rentHouse(rent)" 
                  :disabled="currentRental?.id === rent.id">
                  {{ currentRental?.id === rent.id ? '当前' : '租住' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Purchase Modal -->
    <div class="modal-overlay" v-if="showPurchaseModal">
      <div class="modal-content">
        <div class="modal-header">购买房产</div>
        <div class="modal-body">
          <div class="purchase-info">
            <div class="info-row">
              <span>房产</span>
              <span>{{ selectedProperty?.name }}</span>
            </div>
            <div class="info-row">
              <span>总价</span>
              <span>¥{{ formatNumber(selectedProperty?.price) }}</span>
            </div>
          </div>
          <div class="payment-options">
            <div class="option" :class="{ selected: paymentMethod === 'full' }" @click="paymentMethod = 'full'">
              <div class="option-title">全款购买</div>
              <div class="option-desc">一次性支付全部房款</div>
              <div class="option-amount">¥{{ formatNumber(selectedProperty?.price) }}</div>
            </div>
            <div class="option" :class="{ selected: paymentMethod === 'mortgage' }" @click="paymentMethod = 'mortgage'">
              <div class="option-title">贷款购买</div>
              <div class="option-desc">首付30% + 房贷</div>
              <div class="option-amount">首付 ¥{{ formatNumber(Math.round(selectedProperty?.price * 0.3)) }}</div>
            </div>
          </div>
          <div class="mortgage-calc" v-if="paymentMethod === 'mortgage'">
            <div class="calc-row">
              <span>贷款金额</span>
              <span>¥{{ formatNumber(Math.round(selectedProperty?.price * 0.7)) }}</span>
            </div>
            <div class="calc-row">
              <span>贷款期限</span>
              <select v-model="mortgageTerm">
                <option :value="120">10年</option>
                <option :value="240">20年</option>
                <option :value="360">30年</option>
              </select>
            </div>
            <div class="calc-row">
              <span>预估月供</span>
              <span class="highlight">¥{{ formatNumber(estimatedMonthly) }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="term-btn" @click="showPurchaseModal = false">取消</button>
          <button class="term-btn primary" @click="confirmPurchase">确认购买</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from '../../stores/game'

const gameStore = useGameStore()
const cash = computed(() => gameStore.assets?.cash || 0)

// 我的房产
const myProperties = ref([])

// 居住状态
const livingStatus = ref({
  icon: '🏢',
  type: '租房居住',
  detail: '城中村单间',
  cost: 800,
  happiness: -5,
  status: '普通'
})

// 房贷
const mortgages = ref([])

// 当前租住
const currentRental = ref({ id: 'basic' })

// 右侧面板切换
const rightPanel = ref('buy')  // 'buy' or 'rent'

// 房产类型筛选
const propertyTypes = [
  { id: 'all', name: '全部' },
  { id: 'apartment', name: '公寓' },
  { id: 'house', name: '住宅' },
  { id: 'villa', name: '别墅' }
]
const currentType = ref('all')

// 市场房源
const marketProperties = ref([
  { id: 'apt1', name: '城郊小公寓', type: 'apartment', icon: '🏢', price: 500000, area: 45, location: '郊区', description: '紧凑实用，适合单身', expectedRent: 1500 },
  { id: 'apt2', name: '市区精装公寓', type: 'apartment', icon: '🏢', price: 1200000, area: 70, location: '市区', description: '交通便利，配套完善', expectedRent: 3500 },
  { id: 'house1', name: '花园洋房', type: 'house', icon: '🏠', price: 2500000, area: 120, location: '新区', description: '三室两厅，带小花园', expectedRent: 6000 },
  { id: 'house2', name: '学区房', type: 'house', icon: '🏠', price: 4000000, area: 90, location: '核心区', description: '优质学区，升值潜力大', expectedRent: 8000 },
  { id: 'villa1', name: '郊外别墅', type: 'villa', icon: '🏡', price: 8000000, area: 300, location: '郊区', description: '独栋带院，环境清幽', expectedRent: 15000 }
])

const filteredProperties = computed(() => {
  if (currentType.value === 'all') return marketProperties.value
  return marketProperties.value.filter(p => p.type === currentType.value)
})

// 租房选项
const rentalOptions = ref([
  { id: 'basic', name: '城中村单间', icon: '🚪', monthly: 800, happiness: -5, description: '基本居住，环境一般' },
  { id: 'shared', name: '合租公寓', icon: '🛋️', monthly: 1500, happiness: 0, description: '与人合租，节省开支' },
  { id: 'studio', name: '独立公寓', icon: '🏢', monthly: 3000, happiness: 5, description: '个人空间，生活品质' },
  { id: 'premium', name: '高档公寓', icon: '🌆', monthly: 6000, happiness: 15, description: '豪华装修，尊贵享受' }
])

// 购买模态框
const showPurchaseModal = ref(false)
const selectedProperty = ref(null)
const paymentMethod = ref('mortgage')
const mortgageTerm = ref(360)

const estimatedMonthly = computed(() => {
  if (!selectedProperty.value) return 0
  const principal = selectedProperty.value.price * 0.7
  const monthlyRate = 0.045 / 12
  const n = mortgageTerm.value
  return Math.round((principal * monthlyRate * Math.pow(1 + monthlyRate, n)) / (Math.pow(1 + monthlyRate, n) - 1))
})

const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toLocaleString()
}

const getSessionId = () => {
  try {
    return JSON.parse(localStorage.getItem('currentCharacter'))?.id
  } catch { return null }
}

const buyProperty = (prop) => {
  selectedProperty.value = prop
  showPurchaseModal.value = true
}

const confirmPurchase = async () => {
  const sessionId = getSessionId()
  if (!sessionId) return

  try {
    const res = await fetch('/api/housing/buy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        property_id: selectedProperty.value.id,
        payment_method: paymentMethod.value,
        mortgage_term: mortgageTerm.value
      })
    })
    const data = await res.json()
    if (data.success) {
      alert('购买成功！')
      showPurchaseModal.value = false
      await loadHousingData()
      await gameStore.loadAvatar()
    } else {
      alert(data.error || '购买失败')
    }
  } catch (e) {
    console.error(e)
  }
}

const sellProperty = async (prop) => {
  if (!confirm(`确定要出售 ${prop.name} 吗？当前估值 ¥${formatNumber(prop.currentValue)}`)) return
  
  const sessionId = getSessionId()
  if (!sessionId) return
  
  try {
    const res = await fetch('/api/housing/sell', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        property_id: prop.id
      })
    })
    const data = await res.json()
    if (data.success) {
      alert(`出售成功！获得 ¥${formatNumber(data.sale_price)}`)
      await loadHousingData()
      await gameStore.loadAvatar()
    } else {
      alert(data.error || '出售失败')
    }
  } catch (e) {
    console.error(e)
    alert('操作失败')
  }
}

const rentOut = async (prop) => {
  if (!confirm(`确定要将 ${prop.name} 出租吗？预计月租金 ¥${formatNumber(prop.expectedRent || prop.monthlyRent)}`)) return
  
  const sessionId = getSessionId()
  if (!sessionId) return
  
  try {
    const res = await fetch('/api/housing/rentout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        property_id: prop.id
      })
    })
    const data = await res.json()
    if (data.success) {
      alert(`出租成功！每月可获得 ¥${formatNumber(data.monthly_rent)} 租金`)
      await loadHousingData()
    } else {
      alert(data.error || '出租失败')
    }
  } catch (e) {
    console.error(e)
    alert('操作失败')
  }
}

const rentHouse = async (rent) => {
  const sessionId = getSessionId()
  if (!sessionId) return

  try {
    const res = await fetch('/api/housing/rent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        rental_id: rent.id,
        monthly_cost: rent.monthly,
        happiness_effect: rent.happiness
      })
    })
    const data = await res.json()
    if (data.success) {
      currentRental.value = rent
      livingStatus.value = {
        icon: rent.icon,
        type: '租房居住',
        detail: rent.name,
        cost: rent.monthly,
        happiness: rent.happiness,
        status: rent.monthly >= 3000 ? '中产' : '普通'
      }
      await gameStore.loadAvatar()
    }
  } catch (e) {
    console.error(e)
  }
}

const loadHousingData = async () => {
  const sessionId = getSessionId()
  if (!sessionId) return
  
  try {
    // 加载我的房产
    const propRes = await fetch(`/api/housing/properties/${sessionId}`)
    const propData = await propRes.json()
    if (propData.success && propData.properties) {
      myProperties.value = propData.properties.map(p => ({
        id: p.id,
        name: p.name,
        type: p.type,
        icon: p.type === 'villa' ? '🏡' : p.type === 'house' ? '🏠' : '🏢',
        purchasePrice: p.purchase_price,
        currentValue: p.current_value,
        monthlyRent: p.is_rented ? p.rent_income : (p.expected_rent || 0),
        isRented: p.is_rented,
        isSelfLiving: p.is_self_living
      }))
    }
    
    // 加载居住状态
    const statusRes = await fetch(`/api/housing/status/${sessionId}`)
    const statusData = await statusRes.json()
    if (statusData.success && statusData.status) {
      const s = statusData.status
      // 找到对应的租房选项获取icon
      const rentalMatch = rentalOptions.value.find(r => r.id === s.rental_id)
      livingStatus.value = {
        icon: rentalMatch?.icon || '🏢',
        type: s.living_type || '租房居住',
        detail: s.living_detail || '城中村单间',
        cost: s.monthly_cost || 800,
        happiness: s.happiness_effect || -5,
        status: (s.monthly_cost || 800) >= 3000 ? '中产' : '普通'
      }
      if (rentalMatch) {
        currentRental.value = rentalMatch
      }
    }
    
    // 加载房贷
    const mortRes = await fetch(`/api/housing/mortgages/${sessionId}`)
    const mortData = await mortRes.json()
    if (mortData.success && mortData.mortgages) {
      mortgages.value = mortData.mortgages.map(m => ({
        id: m.id,
        propertyName: m.property_name,
        rate: m.rate || 4.5,
        total: m.total_amount,
        paid: m.paid_amount,
        remaining: m.remaining_amount,
        monthly: m.monthly_payment,
        remainingMonths: m.remaining_months
      }))
    }
  } catch (e) {
    console.error('Load housing data failed:', e)
  }
}

onMounted(() => {
  loadHousingData()
})
</script>

<style scoped>
.view-container { height: 100%; display: flex; flex-direction: column; padding: 20px; overflow: hidden; }
.view-header h2 { font-size: 24px; font-weight: 900; margin: 0 0 8px; }
.header-line { height: 3px; background: var(--term-accent); width: 60px; margin-bottom: 20px; }
.content-grid { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; overflow: hidden; }
.col-left, .col-right { display: flex; flex-direction: column; gap: 16px; overflow: hidden; }

.archive-card { background: var(--term-panel-bg); border: 2px solid var(--term-border); }
.archive-card.flex-grow { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.archive-header { padding: 12px 16px; font-weight: 800; font-size: 12px; border-bottom: 1px solid var(--term-border); display: flex; justify-content: space-between; align-items: center; }
.archive-body { padding: 16px; }
.archive-body.scrollable { flex: 1; overflow-y: auto; }

.empty-state { text-align: center; padding: 30px; color: var(--term-text-secondary); }
.empty-icon { font-size: 48px; margin-bottom: 12px; }

.filter-tabs { display: flex; gap: 8px; }
.tab { font-size: 10px; padding: 4px 8px; cursor: pointer; border: 1px solid var(--term-border); }
.tab.active { background: var(--term-accent); color: #000; }

/* Property Card */
.property-card { display: flex; gap: 12px; padding: 12px; border: 1px solid var(--term-border); margin-bottom: 12px; }
.prop-image { font-size: 32px; }
.prop-info { flex: 1; }
.prop-name { font-weight: 700; }
.prop-type { font-size: 11px; color: var(--term-text-secondary); }
.prop-stats { display: flex; gap: 12px; font-size: 11px; margin-top: 4px; }
.prop-income { font-size: 12px; margin-top: 4px; }
.prop-actions { display: flex; flex-direction: column; gap: 4px; }

/* Living Status */
.living-status { display: flex; gap: 16px; padding-bottom: 12px; border-bottom: 1px dashed var(--term-border); }
.status-icon { font-size: 40px; }
.status-type { font-weight: 700; font-size: 16px; }
.status-detail { font-size: 12px; color: var(--term-text-secondary); }
.status-cost { font-size: 14px; font-weight: 700; margin-top: 4px; }

.living-effects { display: flex; gap: 20px; margin-top: 12px; }
.effect { display: flex; flex-direction: column; }
.effect .label { font-size: 10px; color: var(--term-text-secondary); }
.effect .value { font-weight: 700; }

/* Mortgage */
.mortgage-item { padding: 12px; border: 1px solid var(--term-border); margin-bottom: 12px; }
.mortgage-header { display: flex; justify-content: space-between; font-weight: 700; margin-bottom: 8px; }
.mortgage-details { font-size: 12px; }
.detail-row { display: flex; justify-content: space-between; padding: 4px 0; }
.detail-row.highlight { border-top: 1px dashed var(--term-border); margin-top: 8px; padding-top: 8px; }
.mortgage-progress { display: flex; align-items: center; gap: 8px; margin-top: 8px; font-size: 10px; }
.progress-bar { flex: 1; height: 4px; background: rgba(0,0,0,0.1); }
.progress-fill { height: 100%; background: var(--term-accent); }

/* Property Listing */
.property-listing { display: flex; justify-content: space-between; padding: 12px; border: 1px solid var(--term-border); margin-bottom: 8px; }
.listing-main { display: flex; gap: 12px; }
.listing-icon { font-size: 28px; }
.listing-name { font-weight: 700; }
.listing-desc { font-size: 11px; color: var(--term-text-secondary); }
.listing-tags { display: flex; gap: 6px; margin-top: 6px; }
.listing-tags .tag { font-size: 10px; padding: 2px 6px; background: rgba(0,0,0,0.05); border: 1px solid var(--term-border); }
.listing-tags .tag.rent { color: var(--term-accent); }
.listing-price { text-align: right; }
.listing-price .price { font-size: 16px; font-weight: 800; color: var(--term-accent); }
.listing-price .price-per { font-size: 10px; color: var(--term-text-secondary); }

/* Rental Option */
.rental-option { display: flex; justify-content: space-between; padding: 12px; border: 1px solid var(--term-border); margin-bottom: 8px; }
.rental-option.current { border-color: var(--term-accent); background: rgba(0,0,0,0.02); }
.rental-main { display: flex; gap: 12px; }
.rental-icon { font-size: 24px; }
.rental-name { font-weight: 700; }
.rental-desc { font-size: 11px; color: var(--term-text-secondary); }
.rental-price { text-align: right; }
.rental-price .monthly { font-weight: 700; }
.rental-price .effects { font-size: 11px; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--term-panel-bg); border: 3px solid var(--term-border); width: 450px; }
.modal-header { padding: 16px; font-weight: 800; border-bottom: 2px solid var(--term-border); }
.modal-body { padding: 20px; }
.modal-footer { padding: 16px; border-top: 2px solid var(--term-border); display: flex; justify-content: flex-end; gap: 8px; }

.purchase-info { margin-bottom: 16px; }
.info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed var(--term-border); }

.payment-options { display: flex; gap: 12px; margin-bottom: 16px; }
.option { flex: 1; padding: 12px; border: 2px solid var(--term-border); cursor: pointer; }
.option.selected { border-color: var(--term-accent); }
.option-title { font-weight: 700; }
.option-desc { font-size: 11px; color: var(--term-text-secondary); }
.option-amount { font-size: 14px; font-weight: 700; margin-top: 8px; color: var(--term-accent); }

.mortgage-calc { padding: 12px; background: rgba(0,0,0,0.03); }
.calc-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; }
.calc-row select { padding: 4px 8px; border: 1px solid var(--term-border); }
.highlight { color: var(--term-accent); font-weight: 700; }

.term-btn { padding: 8px 16px; font-weight: 700; border: 2px solid var(--term-border); background: var(--term-panel-bg); cursor: pointer; }
.term-btn:hover:not(:disabled) { background: var(--term-accent); color: #000; }
.term-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.term-btn.primary { background: var(--term-accent); color: #000; }
.term-btn.small { padding: 4px 10px; font-size: 11px; }

.positive { color: #10b981; }
.negative { color: #ef4444; }

/* Accordion Styles */
.accordion-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.accordion-card {
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.accordion-card.expanded { flex: 1; }
.accordion-card.collapsed { flex: 0 0 auto; cursor: pointer; }
.accordion-card.collapsed:hover { border-color: var(--term-accent); }

.accordion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(0,0,0,0.03);
  border-bottom: 1px solid var(--term-border);
  font-weight: 700;
}

.accordion-icon { font-size: 16px; }
.accordion-title { flex: 1; font-size: 12px; text-transform: uppercase; }
.accordion-arrow { font-size: 10px; color: var(--term-text-secondary); }
.accordion-body { flex: 1; overflow-y: auto; padding: 16px; }

/* Filter Tabs */
.filter-tabs { display: flex; gap: 4px; }
.tab { font-size: 10px; padding: 2px 6px; cursor: pointer; border: 1px solid var(--term-border); }
.tab.active { background: var(--term-accent); color: #000; border-color: var(--term-accent); }
</style>
