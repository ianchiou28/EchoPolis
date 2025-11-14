<template>
  <div class="login-page">
    <div class="login-container">
      <h1>🌆 EchoPolis</h1>
      <p class="subtitle">回声都市 - 你的财富人生沙盘</p>

      <div v-if="!showRegister" class="form-box card glass">
        <h2>登录</h2>
        <input v-model="username" type="text" class="input" placeholder="用户名" />
        <input v-model="password" type="password" class="input" placeholder="密码" @keyup.enter="login" />
        <button class="btn btn-primary" @click="login">登录</button>
        <p class="switch-text">还没有账号？<span @click="showRegister = true">立即注册</span></p>
      </div>

      <div v-else class="form-box card glass">
        <h2>注册</h2>
        <input v-model="username" type="text" class="input" placeholder="用户名" />
        <input v-model="password" type="password" class="input" placeholder="密码" />
        <input v-model="confirmPassword" type="password" class="input" placeholder="确认密码" @keyup.enter="register" />
        <button class="btn btn-primary" @click="register">注册</button>
        <p class="switch-text">已有账号？<span @click="showRegister = false">立即登录</span></p>
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
.login-page {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-gradient);
}

.login-container {
  text-align: center;
}

h1 {
  font-size: 48px;
  color: var(--text);
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
  margin-bottom: 10px;
}

.subtitle {
  color: var(--text);
  opacity: 0.9;
  font-size: 18px;
  margin-bottom: 40px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.form-box {
  padding: 40px;
  border-radius: var(--radius-lg);
  min-width: 350px;
}

.form-box h2 {
  margin-bottom: 30px;
  color: var(--text);
}

.form-box .input {
  width: 100%;
  margin-bottom: 15px;
}

.form-box .btn {
  width: 100%;
}

.switch-text {
  margin-top: 20px;
  color: var(--muted);
  font-size: 14px;
}

.switch-text span {
  color: var(--primary-400);
  cursor: pointer;
  font-weight: bold;
}

.switch-text span:hover { text-decoration: underline; }
</style>
