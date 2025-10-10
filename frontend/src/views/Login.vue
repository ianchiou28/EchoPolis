<template>
  <div class="login-container">
    <div class="login-box">
      <h1>🌆 Echopolis</h1>
      <p class="subtitle">回声都市 - AI驱动的金融模拟器</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>账号</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="请输入账号"
            required
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label>密码</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="请输入密码"
            required
            class="form-input"
          />
        </div>
        
        <button type="submit" :disabled="isLoading" class="login-btn">
          {{ isLoading ? '登录中...' : '登录' }}
        </button>
        
        <button type="button" @click="handleRegister" :disabled="isLoading" class="register-btn">
          注册新账号
        </button>
      </form>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '../stores/game'

const router = useRouter()
const gameStore = useGameStore()

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入账号和密码'
    return
  }
  
  isLoading.value = true
  error.value = ''
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      // 登录成功，保存用户信息
      gameStore.setUser(result.username)
      router.push('/home')
    } else {
      error.value = result.message
    }
  } catch (err) {
    error.value = '登录失败，请检查网络连接'
    console.error('Login error:', err)
  } finally {
    isLoading.value = false
  }
}

const handleRegister = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入账号和密码'
    return
  }
  
  isLoading.value = true
  error.value = ''
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      // 注册成功，自动登录
      gameStore.setUser(result.username)
      router.push('/home')
    } else {
      error.value = result.message
    }
  } catch (err) {
    error.value = '注册失败，请检查网络连接'
    console.error('Register error:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.login-box {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

h1 {
  color: white;
  font-size: 2.5em;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.subtitle {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 30px;
  font-size: 1.1em;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  text-align: left;
}

.form-group label {
  display: block;
  color: white;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  background: white;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.login-btn, .register-btn {
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.login-btn {
  background: linear-gradient(45deg, #4CAF50, #8BC34A);
  color: white;
}

.register-btn {
  background: linear-gradient(45deg, #2196F3, #3F51B5);
  color: white;
}

.login-btn:hover, .register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.login-btn:disabled, .register-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error-message {
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  padding: 10px;
  border-radius: 8px;
  margin-top: 15px;
  border: 1px solid rgba(255, 107, 107, 0.3);
}
</style>