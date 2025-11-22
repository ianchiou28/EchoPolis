<template>
  <div class="login-page-wrapper">
    <div class="grid-bg"></div>
    <div class="crt-overlay"></div>

    <div class="login-container">
      <div class="brand-header">
        <h1 class="brand-logo">ECHO<span class="highlight">POLIS</span></h1>
        <p class="subtitle">WEALTH SIMULATION SYSTEM // 财富人生沙盘</p>
      </div>

      <div v-if="!showRegister" class="archive-card">
        <div class="archive-header">
          <span>SYSTEM ACCESS // 系统接入</span>
        </div>
        <div class="archive-body">
          <div class="form-group">
            <label>IDENTITY // 用户名</label>
            <input v-model="username" type="text" class="term-input" placeholder="ENTER USERNAME..." />
          </div>
          <div class="form-group">
            <label>PASSPHRASE // 密码</label>
            <input v-model="password" type="password" class="term-input" placeholder="ENTER PASSWORD..." @keyup.enter="login" />
          </div>
          <button class="term-btn primary full-width" @click="login">
            INITIALIZE LINK // 登录
          </button>
          <p class="switch-text">
            NO ACCESS ID? <span @click="showRegister = true" class="accent-link">REGISTER NEW IDENTITY</span>
          </p>
        </div>
      </div>

      <div v-else class="archive-card">
        <div class="archive-header">
          <span>NEW IDENTITY // 注册新身份</span>
        </div>
        <div class="archive-body">
          <div class="form-group">
            <label>IDENTITY // 用户名</label>
            <input v-model="username" type="text" class="term-input" placeholder="CREATE USERNAME..." />
          </div>
          <div class="form-group">
            <label>PASSPHRASE // 密码</label>
            <input v-model="password" type="password" class="term-input" placeholder="CREATE PASSWORD..." />
          </div>
          <div class="form-group">
            <label>CONFIRM // 确认密码</label>
            <input v-model="confirmPassword" type="password" class="term-input" placeholder="CONFIRM PASSWORD..." @keyup.enter="register" />
          </div>
          <button class="term-btn primary full-width" @click="register">
            ESTABLISH IDENTITY // 注册
          </button>
          <p class="switch-text">
            EXISTING ID? <span @click="showRegister = false" class="accent-link">ACCESS SYSTEM</span>
          </p>
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
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const showRegister = ref(false)

const login = async () => {
  if (!username.value || !password.value) {
    alert('请输入用户名和密码')
    return
  }

  try {
    const res = await axios.post('/api/login', {
      username: username.value,
      password: password.value
    })

    if (res.data.success) {
      localStorage.setItem('username', username.value)
      router.push('/character-select')
    } else {
      alert(res.data.message)
    }
  } catch (error) {
    alert('登录失败：' + error.message)
  }
}

const register = async () => {
  if (!username.value || !password.value) {
    alert('请输入用户名和密码')
    return
  }

  if (password.value !== confirmPassword.value) {
    alert('两次密码不一致')
    return
  }

  try {
    const res = await axios.post('/api/register', {
      username: username.value,
      password: password.value
    })

    if (res.data.success) {
      alert('注册成功！')
      showRegister.value = false
    } else {
      alert(res.data.message)
    }
  } catch (error) {
    alert('注册失败：' + error.message)
  }
}
</script>

<style scoped>
@import '@/styles/terminal-theme.css';

.login-page-wrapper {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'JetBrains Mono', monospace;
  position: relative;
  overflow: hidden;
}

.login-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 450px;
  padding: 20px;
}

.brand-header {
  text-align: center;
  margin-bottom: 40px;
}

.brand-logo {
  font-weight: 900;
  font-size: 56px;
  letter-spacing: -1px;
  text-transform: uppercase;
  color: var(--term-text);
  margin: 0;
}

.brand-logo .highlight {
  color: var(--term-accent);
}

.subtitle {
  color: var(--term-text-secondary);
  font-size: 14px;
  letter-spacing: 2px;
  margin-top: 8px;
  font-weight: 700;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  color: var(--term-text-secondary);
  font-size: 11px;
  font-weight: 700;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.term-input {
  width: 100%;
  padding: 14px;
  background: var(--term-bg);
  border: 2px solid var(--term-border);
  color: var(--term-text);
  font-family: 'JetBrains Mono', monospace;
  font-size: 16px;
  transition: all 0.2s;
  border-radius: 0;
}

.term-input:focus {
  outline: none;
  border-color: var(--term-accent);
  background: #0a0a0a;
  color: #ffffff; /* Ensure text is white on dark background */
  box-shadow: 0 0 10px var(--term-accent-glow);
}

.term-input::placeholder {
  color: var(--term-text-secondary);
  opacity: 0.6;
}

.full-width {
  width: 100%;
}

.switch-text {
  margin-top: 24px;
  text-align: center;
  color: var(--term-text-secondary);
  font-size: 13px;
}

.accent-link {
  color: var(--term-accent);
  cursor: pointer;
  font-weight: 700;
  margin-left: 8px;
  transition: all 0.2s;
}

.accent-link:hover {
  text-decoration: underline;
  text-shadow: 0 0 8px var(--term-accent-glow);
}
</style>
