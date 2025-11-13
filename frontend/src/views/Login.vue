<template>
  <div class="login-page">
    <div class="login-container">
      <h1>🌆 EchoPolis</h1>
      <p class="subtitle">回声都市 - 你的财富人生沙盘</p>

      <div v-if="!showRegister" class="form-box">
        <h2>登录</h2>
        <input v-model="username" type="text" placeholder="用户名" />
        <input v-model="password" type="password" placeholder="密码" @keyup.enter="login" />
        <button @click="login">登录</button>
        <p class="switch-text">还没有账号？<span @click="showRegister = true">立即注册</span></p>
      </div>

      <div v-else class="form-box">
        <h2>注册</h2>
        <input v-model="username" type="text" placeholder="用户名" />
        <input v-model="password" type="password" placeholder="密码" />
        <input v-model="confirmPassword" type="password" placeholder="确认密码" @keyup.enter="register" />
        <button @click="register">注册</button>
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
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.login-container {
  text-align: center;
}

h1 {
  font-size: 48px;
  color: white;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
  margin-bottom: 10px;
}

.subtitle {
  color: white;
  font-size: 18px;
  margin-bottom: 40px;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
}

.form-box {
  background: rgba(255,255,255,0.95);
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  min-width: 350px;
}

.form-box h2 {
  margin-bottom: 30px;
  color: #333;
}

.form-box input {
  width: 100%;
  padding: 15px;
  margin-bottom: 15px;
  border: 2px solid #f0f0f0;
  border-radius: 10px;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.form-box input:focus {
  border-color: #ff9a9e;
}

.form-box button {
  width: 100%;
  padding: 15px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  color: white;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.form-box button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}

.switch-text {
  margin-top: 20px;
  color: #666;
  font-size: 14px;
}

.switch-text span {
  color: #ff9a9e;
  cursor: pointer;
  font-weight: bold;
}

.switch-text span:hover {
  text-decoration: underline;
}
</style>
