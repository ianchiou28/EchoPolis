<template>
  <div class="login-page">
    <div class="login-container">
      <div class="brand-header">
        <h1>ECHO POLIS</h1>
        <p class="subtitle">WEALTH SIMULATION SYSTEM // 财富人生沙盘</p>
      </div>

      <div v-if="!showRegister" class="form-box glass-panel tech-border">
        <div class="panel-header">
          <h2>SYSTEM ACCESS // 系统接入</h2>
        </div>
        <div class="form-content">
          <div class="form-group">
            <label>IDENTITY // 用户名</label>
            <input v-model="username" type="text" class="input-cyber" placeholder="ENTER USERNAME..." />
          </div>
          <div class="form-group">
            <label>PASSPHRASE // 密码</label>
            <input v-model="password" type="password" class="input-cyber" placeholder="ENTER PASSWORD..." @keyup.enter="login" />
          </div>
          <button class="btn primary full-width" @click="login">
            <span class="btn-content">INITIALIZE LINK // 登录</span>
          </button>
          <p class="switch-text">NO ACCESS ID? <span @click="showRegister = true">REGISTER NEW IDENTITY</span></p>
        </div>
      </div>

      <div v-else class="form-box glass-panel tech-border">
        <div class="panel-header">
          <h2>NEW IDENTITY // 注册新身份</h2>
        </div>
        <div class="form-content">
          <div class="form-group">
            <label>IDENTITY // 用户名</label>
            <input v-model="username" type="text" class="input-cyber" placeholder="CREATE USERNAME..." />
          </div>
          <div class="form-group">
            <label>PASSPHRASE // 密码</label>
            <input v-model="password" type="password" class="input-cyber" placeholder="CREATE PASSWORD..." />
          </div>
          <div class="form-group">
            <label>CONFIRM // 确认密码</label>
            <input v-model="confirmPassword" type="password" class="input-cyber" placeholder="CONFIRM PASSWORD..." @keyup.enter="register" />
          </div>
          <button class="btn primary full-width" @click="register">
            <span class="btn-content">ESTABLISH IDENTITY // 注册</span>
          </button>
          <p class="switch-text">EXISTING ID? <span @click="showRegister = false">ACCESS SYSTEM</span></p>
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
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap');

.login-page {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f172a;
  background-image: 
    radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
    linear-gradient(rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.9)),
    url('/assets/city/bg-tech.jpg'); /* Fallback or texture */
  background-size: cover;
  font-family: 'Rajdhani', sans-serif;
  position: relative;
  overflow: hidden;
}

/* Grid Background Effect */
.login-page::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 200%;
  top: -50%;
  left: -50%;
  background-image: 
    linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  transform: perspective(500px) rotateX(60deg);
  animation: grid-move 20s linear infinite;
  pointer-events: none;
}

@keyframes grid-move {
  0% { transform: perspective(500px) rotateX(60deg) translateY(0); }
  100% { transform: perspective(500px) rotateX(60deg) translateY(40px); }
}

.login-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 420px;
  padding: 20px;
}

.brand-header {
  text-align: center;
  margin-bottom: 40px;
}

.brand-header h1 {
  font-size: 56px;
  font-weight: 700;
  color: #e2e8f0;
  margin: 0;
  letter-spacing: 4px;
  text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
  background: linear-gradient(to bottom, #ffffff, #94a3b8);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #3b82f6;
  font-size: 14px;
  letter-spacing: 2px;
  margin-top: 8px;
  font-weight: 600;
  text-transform: uppercase;
}

.glass-panel {
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(12px);
  padding: 32px;
  position: relative;
}

.panel-header {
  margin-bottom: 24px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  padding-bottom: 16px;
}

.panel-header h2 {
  color: #e2e8f0;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  letter-spacing: 1px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.input-cyber {
  width: 100%;
  padding: 12px 16px;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #e2e8f0;
  font-family: 'Rajdhani', sans-serif;
  font-size: 16px;
  transition: all 0.3s ease;
}

.input-cyber:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
  background: rgba(30, 41, 59, 0.8);
}

.input-cyber::placeholder {
  color: #475569;
  font-size: 14px;
  letter-spacing: 1px;
}

.btn {
  border: none;
  cursor: pointer;
  font-family: 'Rajdhani', sans-serif;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn.primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  padding: 14px;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 1px;
  clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
}

.btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
}

.btn.full-width {
  width: 100%;
}

.switch-text {
  margin-top: 24px;
  text-align: center;
  color: #64748b;
  font-size: 13px;
  letter-spacing: 0.5px;
}

.switch-text span {
  color: #3b82f6;
  cursor: pointer;
  font-weight: 600;
  margin-left: 8px;
  transition: color 0.2s;
}

.switch-text span:hover {
  color: #60a5fa;
  text-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
}

/* Tech Border Effect */
.tech-border {
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
}

.tech-border::after {
  content: '';
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 20px;
  height: 20px;
  border-bottom: 2px solid #3b82f6;
  border-right: 2px solid #3b82f6;
}

.tech-border::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  width: 20px;
  height: 20px;
  border-top: 2px solid #3b82f6;
  border-left: 2px solid #3b82f6;
}
</style>
