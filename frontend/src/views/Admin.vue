<template>
  <div class="admin-page-wrapper" data-theme="light">
    <div class="grid-bg"></div>

    <!-- 未登录时显示登录框 -->
    <div v-if="!isAuthenticated" class="admin-login-container">
      <div class="archive-card">
        <div class="archive-header">
          <span>ADMIN ACCESS // 管理员登录</span>
        </div>
        <div class="archive-body">
          <div class="form-group">
            <label>ADMIN KEY // 管理密钥</label>
            <input
              v-model="adminKey"
              type="password"
              class="term-input"
              placeholder="ENTER ADMIN KEY..."
              @keyup.enter="login"
            />
          </div>
          <button class="term-btn primary full-width" @click="login">
            AUTHENTICATE // 验证
          </button>
          <p class="switch-text">
            <router-link to="/login" class="accent-link">← RETURN TO LOGIN</router-link>
          </p>
        </div>
      </div>
    </div>

    <!-- 已登录时显示管理面板 -->
    <div v-else class="admin-dashboard">
      <!-- 顶部导航 -->
      <div class="admin-header">
        <div class="header-left">
          <h1 class="brand-logo">ECHOPOLIS</h1>
          <span class="admin-badge">ADMIN PANEL</span>
        </div>
        <div class="header-right">
          <button class="term-btn" @click="refreshData">
            REFRESH // 刷新
          </button>
          <button class="term-btn" @click="logout">
            LOGOUT // 登出
          </button>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_accounts }}</div>
          <div class="stat-label">TOTAL ACCOUNTS // 账户总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_users }}</div>
          <div class="stat-label">TOTAL CHARACTERS // 角色总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.active_sessions }}</div>
          <div class="stat-label">ACTIVE SESSIONS // 活跃会话</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.today_registrations }}</div>
          <div class="stat-label">TODAY REGISTRATIONS // 今日注册</div>
        </div>
      </div>

      <!-- 标签页切换 -->
      <div class="tab-bar">
        <button
          :class="['tab-btn', { active: activeTab === 'accounts' }]"
          @click="activeTab = 'accounts'"
        >
          ACCOUNTS // 账户管理
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'users' }]"
          @click="activeTab = 'users'"
        >
          CHARACTERS // 角色管理
        </button>
      </div>

      <!-- 账户列表 -->
      <div v-if="activeTab === 'accounts'" class="data-section">
        <div class="section-header">
          <h2>ACCOUNTS DATABASE // 账户数据库</h2>
          <div class="search-box">
            <input
              v-model="accountSearch"
              type="text"
              class="term-input small"
              placeholder="SEARCH USERNAME..."
            />
          </div>
        </div>
        <div class="data-table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>USERNAME // 用户名</th>
                <th>CREATED // 创建时间</th>
                <th>ACTIONS // 操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="account in paginatedAccounts" :key="account.id">
                <td>{{ account.id }}</td>
                <td>{{ account.username }}</td>
                <td>{{ formatDate(account.created_at) }}</td>
                <td>
                  <button
                    class="term-btn small danger"
                    @click="confirmDeleteAccount(account)"
                  >
                    DELETE
                  </button>
                </td>
              </tr>
              <tr v-if="filteredAccounts.length === 0">
                <td colspan="4" class="no-data">NO ACCOUNTS FOUND</td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- 账户分页控件 -->
        <div v-if="totalAccountPages > 1" class="pagination">
          <button 
            class="term-btn small" 
            :disabled="accountPage === 1"
            @click="accountPage--"
          >
            ← PREV
          </button>
          <span class="page-info">
            {{ accountPage }} / {{ totalAccountPages }}
            <span class="total-count">({{ filteredAccounts.length }} 条记录)</span>
          </span>
          <button 
            class="term-btn small" 
            :disabled="accountPage === totalAccountPages"
            @click="accountPage++"
          >
            NEXT →
          </button>
        </div>
      </div>

      <!-- 角色列表 -->
      <div v-if="activeTab === 'users'" class="data-section">
        <div class="section-header">
          <h2>CHARACTERS DATABASE // 角色数据库</h2>
          <div class="search-box">
            <input
              v-model="userSearch"
              type="text"
              class="term-input small"
              placeholder="SEARCH NAME OR MBTI..."
            />
          </div>
        </div>
        <div class="data-table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>NAME // 名字</th>
                <th>ACCOUNT // 账户</th>
                <th>MBTI</th>
                <th>FATE // 命运</th>
                <th>CASH // 现金</th>
                <th>MONTH // 月份</th>
                <th>STATUS // 状态</th>
                <th>ACTIONS // 操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in paginatedUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.name }}</td>
                <td>{{ user.username }}</td>
                <td>
                  <span class="mbti-badge">{{ user.mbti }}</span>
                </td>
                <td class="fate-cell">{{ user.fate }}</td>
                <td>
                  <span class="credits-value">{{ formatNumber(user.credits) }}</span>
                </td>
                <td>{{ user.current_month }}</td>
                <td>
                  <div class="status-indicators">
                    <span class="indicator" :title="`Happiness: ${user.happiness}`">
                      😊 {{ user.happiness }}
                    </span>
                    <span class="indicator" :title="`Energy: ${user.energy}`">
                      ⚡ {{ user.energy }}
                    </span>
                    <span class="indicator" :title="`Health: ${user.health}`">
                      ❤️ {{ user.health }}
                    </span>
                  </div>
                </td>
                <td>
                  <div class="action-buttons">
                    <button
                      class="term-btn action-btn"
                      @click="openEditCredits(user)"
                      title="编辑现金"
                    >
                      💰
                    </button>
                    <button
                      class="term-btn action-btn"
                      @click="openEditStatus(user)"
                      title="编辑状态"
                    >
                      📊
                    </button>
                    <button
                      class="term-btn action-btn danger"
                      @click="confirmDeleteUser(user)"
                      title="删除角色"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredUsers.length === 0">
                <td colspan="9" class="no-data">NO CHARACTERS FOUND</td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- 角色分页控件 -->
        <div v-if="totalUserPages > 1" class="pagination">
          <button 
            class="term-btn small" 
            :disabled="userPage === 1"
            @click="userPage--"
          >
            ← PREV
          </button>
          <span class="page-info">
            {{ userPage }} / {{ totalUserPages }}
            <span class="total-count">({{ filteredUsers.length }} 条记录)</span>
          </span>
          <button 
            class="term-btn small" 
            :disabled="userPage === totalUserPages"
            @click="userPage++"
          >
            NEXT →
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑现金弹窗 -->
    <div v-if="showCreditsModal" class="modal-overlay" @click.self="showCreditsModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <span>EDIT CASH // 编辑现金</span>
          <button class="close-btn" @click="showCreditsModal = false">×</button>
        </div>
        <div class="modal-body">
          <p>Character: {{ editingUser?.name }}</p>
          <div class="form-group">
            <label>NEW CASH // 新现金数量</label>
            <input
              v-model.number="newCredits"
              type="number"
              class="term-input"
              placeholder="ENTER NEW CASH..."
            />
          </div>
          <button class="term-btn primary full-width" @click="updateCredits">
            UPDATE // 更新
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑状态弹窗 -->
    <div v-if="showStatusModal" class="modal-overlay" @click.self="showStatusModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <span>EDIT STATUS // 编辑状态</span>
          <button class="close-btn" @click="showStatusModal = false">×</button>
        </div>
        <div class="modal-body">
          <p>Character: {{ editingUser?.name }}</p>
          <div class="form-group">
            <label>HAPPINESS // 快乐值 (0-100)</label>
            <input
              v-model.number="newStatus.happiness"
              type="number"
              min="0"
              max="100"
              class="term-input"
            />
          </div>
          <div class="form-group">
            <label>ENERGY // 能量值 (0-100)</label>
            <input
              v-model.number="newStatus.energy"
              type="number"
              min="0"
              max="100"
              class="term-input"
            />
          </div>
          <div class="form-group">
            <label>HEALTH // 健康值 (0-100)</label>
            <input
              v-model.number="newStatus.health"
              type="number"
              min="0"
              max="100"
              class="term-input"
            />
          </div>
          <button class="term-btn primary full-width" @click="updateStatus">
            UPDATE // 更新
          </button>
        </div>
      </div>
    </div>

    <!-- 确认删除弹窗 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-card danger">
        <div class="modal-header danger">
          <span>⚠️ CONFIRM DELETE // 确认删除</span>
          <button class="close-btn" @click="showDeleteModal = false">×</button>
        </div>
        <div class="modal-body">
          <p class="warning-text">
            {{ deleteType === 'account' 
              ? `确定要删除账户 "${deleteTarget?.username}" 及其所有角色吗？此操作不可撤销！`
              : `确定要删除角色 "${deleteTarget?.name}" 吗？此操作不可撤销！`
            }}
          </p>
          <div class="modal-actions">
            <button class="term-btn" @click="showDeleteModal = false">
              CANCEL // 取消
            </button>
            <button class="term-btn danger" @click="executeDelete">
              DELETE // 删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// 认证状态
const adminKey = ref('')
const isAuthenticated = ref(false)

// 数据
const stats = ref({
  total_accounts: 0,
  total_users: 0,
  active_sessions: 0,
  total_transactions: 0,
  total_investments: 0,
  today_registrations: 0
})
const accounts = ref([])
const users = ref([])

// UI 状态
const activeTab = ref('accounts')
const accountSearch = ref('')
const userSearch = ref('')

// 分页状态
const userPage = ref(1)
const accountPage = ref(1)
const pageSize = 10

// 弹窗状态
const showCreditsModal = ref(false)
const showStatusModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref(null)
const newCredits = ref(0)
const newStatus = ref({ happiness: 70, energy: 75, health: 80 })
const deleteType = ref('')
const deleteTarget = ref(null)

// 过滤后的数据
const filteredAccounts = computed(() => {
  if (!accountSearch.value) return accounts.value
  const search = accountSearch.value.toLowerCase()
  return accounts.value.filter(a => 
    a.username.toLowerCase().includes(search)
  )
})

const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value
  const search = userSearch.value.toLowerCase()
  return users.value.filter(u => 
    u.name.toLowerCase().includes(search) ||
    u.mbti.toLowerCase().includes(search) ||
    u.username.toLowerCase().includes(search)
  )
})

// 分页后的数据
const paginatedUsers = computed(() => {
  const start = (userPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredUsers.value.slice(start, end)
})

const paginatedAccounts = computed(() => {
  const start = (accountPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredAccounts.value.slice(start, end)
})

const totalUserPages = computed(() => Math.ceil(filteredUsers.value.length / pageSize))
const totalAccountPages = computed(() => Math.ceil(filteredAccounts.value.length / pageSize))

// 监听搜索变化，重置页码
import { watch } from 'vue'
watch(userSearch, () => { userPage.value = 1 })
watch(accountSearch, () => { accountPage.value = 1 })

// 登录
async function login() {
  if (!adminKey.value) {
    alert('请输入管理密钥')
    return
  }

  try {
    const res = await axios.post('/api/admin/login', {
      admin_key: adminKey.value
    })

    if (res.data.success) {
      isAuthenticated.value = true
      localStorage.setItem('admin_key', adminKey.value)
      await refreshData()
    } else {
      alert(res.data.message)
    }
  } catch (error) {
    alert('登录失败：' + error.message)
  }
}

// 登出
function logout() {
  isAuthenticated.value = false
  adminKey.value = ''
  localStorage.removeItem('admin_key')
}

// 刷新数据
async function refreshData() {
  const key = adminKey.value || localStorage.getItem('admin_key')
  
  try {
    const [statsRes, accountsRes, usersRes] = await Promise.all([
      axios.get(`/api/admin/stats?admin_key=${key}`),
      axios.get(`/api/admin/accounts?admin_key=${key}`),
      axios.get(`/api/admin/users?admin_key=${key}`)
    ])

    if (statsRes.data.success) stats.value = statsRes.data.stats
    if (accountsRes.data.success) accounts.value = accountsRes.data.accounts
    if (usersRes.data.success) users.value = usersRes.data.users
  } catch (error) {
    console.error('Failed to fetch data:', error)
    if (error.response?.status === 403) {
      logout()
      alert('认证已过期，请重新登录')
    }
  }
}

// 编辑金币
function openEditCredits(user) {
  editingUser.value = user
  newCredits.value = user.credits
  showCreditsModal.value = true
}

async function updateCredits() {
  const key = adminKey.value || localStorage.getItem('admin_key')
  
  try {
    const res = await axios.post(`/api/admin/update-credits?admin_key=${key}`, {
      session_id: editingUser.value.session_id,
      credits: newCredits.value
    })

    if (res.data.success) {
      showCreditsModal.value = false
      await refreshData()
    } else {
      alert(res.data.message)
    }
  } catch (error) {
    alert('更新失败：' + error.message)
  }
}

// 编辑状态
function openEditStatus(user) {
  editingUser.value = user
  newStatus.value = {
    happiness: user.happiness || 70,
    energy: user.energy || 75,
    health: user.health || 80
  }
  showStatusModal.value = true
}

async function updateStatus() {
  const key = adminKey.value || localStorage.getItem('admin_key')
  
  try {
    const res = await axios.post(`/api/admin/update-status?admin_key=${key}`, {
      session_id: editingUser.value.session_id,
      happiness: newStatus.value.happiness,
      energy: newStatus.value.energy,
      health: newStatus.value.health
    })

    if (res.data.success) {
      showStatusModal.value = false
      await refreshData()
    } else {
      alert(res.data.message)
    }
  } catch (error) {
    alert('更新失败：' + error.message)
  }
}

// 删除确认
function confirmDeleteAccount(account) {
  deleteType.value = 'account'
  deleteTarget.value = account
  showDeleteModal.value = true
}

function confirmDeleteUser(user) {
  deleteType.value = 'user'
  deleteTarget.value = user
  showDeleteModal.value = true
}

async function executeDelete() {
  const key = adminKey.value || localStorage.getItem('admin_key')
  
  try {
    let res
    if (deleteType.value === 'account') {
      res = await axios.post(`/api/admin/delete-account?admin_key=${key}`, {
        username: deleteTarget.value.username
      })
    } else {
      res = await axios.post(`/api/admin/delete-user?admin_key=${key}`, {
        session_id: deleteTarget.value.session_id
      })
    }

    if (res.data.success) {
      showDeleteModal.value = false
      await refreshData()
    } else {
      alert(res.data.message)
    }
  } catch (error) {
    alert('删除失败：' + error.message)
  }
}

// 工具函数
function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

function formatNumber(num) {
  if (num === null || num === undefined) return '0'
  return num.toLocaleString()
}

// 初始化
onMounted(() => {
  const savedKey = localStorage.getItem('admin_key')
  if (savedKey) {
    adminKey.value = savedKey
    isAuthenticated.value = true
    refreshData()
  }
})
</script>

<style scoped>
@import '@/styles/terminal-theme.css';

.admin-page-wrapper {
  width: 100%;
  height: 100vh;
  font-family: 'JetBrains Mono', monospace;
  position: relative;
  overflow: hidden;
  background-color: #F2F0E6;
  color: #111111;
}

/* 登录容器 */
.admin-login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}

.admin-login-container .archive-card {
  width: 100%;
  max-width: 450px;
  background: #FFFFFF;
  border: 2px solid #000000;
}

/* 仪表板布局 */
.admin-dashboard {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
  position: relative;
  z-index: 10;
  height: 100vh;
  overflow-y: auto;
  box-sizing: border-box;
}

/* 顶部导航 */
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: #FFFFFF;
  border: 2px solid #000000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.brand-logo {
  font-size: 24px;
  font-weight: 900;
  color: #E04F00;
  margin: 0;
}

.admin-badge {
  background: #E04F00;
  color: #FFFFFF;
  padding: 4px 12px;
  font-size: 10px;
  font-weight: 700;
}

.header-right {
  display: flex;
  gap: 10px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #FFFFFF;
  border: 2px solid #000000;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 36px;
  font-weight: 900;
  color: #E04F00;
}

.stat-label {
  font-size: 10px;
  color: #444444;
  margin-top: 8px;
  text-transform: uppercase;
}

/* 标签栏 */
.tab-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab-btn {
  background: #FFFFFF;
  border: 2px solid #000000;
  color: #111111;
  padding: 12px 24px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  text-transform: uppercase;
}

.tab-btn.active {
  background: #E04F00;
  color: #FFFFFF;
  border-color: #E04F00;
}

.tab-btn:hover:not(.active) {
  border-color: #E04F00;
}

/* 数据区域 */
.data-section {
  background: #FFFFFF;
  border: 2px solid #000000;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 14px;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
}

.search-box .term-input {
  width: 250px;
}

/* 数据表格 */
.data-table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #cccccc;
}

.data-table th {
  background: rgba(224, 79, 0, 0.15);
  font-weight: 700;
  text-transform: uppercase;
  font-size: 10px;
  color: #E04F00;
}

.data-table tr:hover {
  background: rgba(0, 0, 0, 0.02);
}

.no-data {
  text-align: center;
  color: #444444;
  padding: 40px !important;
}

/* 徽章和指示器 */
.mbti-badge {
  background: #E04F00;
  color: #FFFFFF;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 700;
}

.credits-value {
  font-weight: 700;
  color: #b45309;
}

.status-indicators {
  display: flex;
  gap: 8px;
  font-size: 11px;
}

.indicator {
  display: flex;
  align-items: center;
  gap: 2px;
}

.action-buttons {
  display: flex;
  gap: 6px;
  justify-content: flex-start;
}

/* 操作按钮样式 */
.term-btn.action-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  border-radius: 4px;
}

.term-btn.action-btn:hover {
  background: #f0f0f0;
  transform: scale(1.05);
}

.term-btn.action-btn.danger {
  border-color: #dc2626;
}

.term-btn.action-btn.danger:hover {
  background: #fef2f2;
}

.fate-cell {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 按钮变体 */
.term-btn {
  background: #FFFFFF;
  border: 2px solid #000000;
  color: #111111;
  padding: 10px 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  text-transform: uppercase;
}

.term-btn:hover {
  background: #f5f5f5;
}

.term-btn.primary {
  background: #E04F00;
  border-color: #E04F00;
  color: #FFFFFF;
}

.term-btn.primary:hover {
  background: #c44400;
}

.term-btn.small {
  padding: 6px 12px;
  font-size: 10px;
}

.term-btn.danger {
  border-color: #dc2626;
  color: #dc2626;
}

.term-btn.danger:hover {
  background: #dc2626;
  color: #fff;
}

/* 输入框 */
.term-input {
  background: #FFFFFF;
  border: 2px solid #000000;
  color: #111111;
  padding: 10px 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  width: 100%;
  box-sizing: border-box;
}

.term-input:focus {
  outline: none;
  border-color: #E04F00;
}

.term-input.small {
  padding: 8px 10px;
  font-size: 11px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 6px;
  color: #444444;
}

.full-width {
  width: 100%;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: #FFFFFF;
  border: 2px solid #000000;
  width: 100%;
  max-width: 400px;
  margin: 20px;
}

.modal-card.danger {
  border-color: #dc2626;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 2px solid #000000;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 12px;
}

.modal-header.danger {
  background: #dc2626;
  color: #fff;
  border-color: #dc2626;
}

.close-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-body {
  padding: 20px;
}

.modal-body p {
  margin: 0 0 16px;
  font-size: 12px;
}

.warning-text {
  color: #b45309;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.modal-actions .term-btn {
  flex: 1;
}

/* 链接 */
.switch-text {
  text-align: center;
  font-size: 11px;
  margin-top: 16px;
  color: #444444;
}

.accent-link {
  color: #E04F00;
  text-decoration: none;
  cursor: pointer;
}

.accent-link:hover {
  text-decoration: underline;
}

/* 分页控件 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #cccccc;
}

.page-info {
  font-size: 12px;
  font-weight: 700;
  color: #111111;
}

.total-count {
  color: #666666;
  font-weight: 400;
  margin-left: 8px;
}

.pagination .term-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 档案卡片 */
.archive-card {
  background: #FFFFFF;
  border: 2px solid #000000;
}

.archive-header {
  background: #E04F00;
  color: #FFFFFF;
  padding: 12px 16px;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 12px;
}

.archive-body {
  padding: 20px;
}
</style>
