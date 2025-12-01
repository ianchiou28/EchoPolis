<template>
  <div class="auto-login-container">
    <div class="loading-text">
      <div class="spinner"></div>
      <div>正在初始化体验环境...</div>
      <div class="sub-text">Creating test session environment</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

onMounted(async () => {
  // 1. Check if already logged in
  const existingUser = localStorage.getItem('username')
  const existingChar = localStorage.getItem('currentCharacter')
  
  if (existingUser && existingChar) {
    console.log('Found existing session, redirecting to home...')
    router.push('/home')
    return
  }

  // 2. Create new guest session
  try {
    const timestamp = Date.now()
    const randomId = Math.floor(Math.random() * 1000)
    const username = `judge_${timestamp}_${randomId}`
    
    console.log('Creating new judge session:', username)
    
    const res = await axios.post('/api/session/start', {
      username: username,
      name: 'Test',
      mbti: 'INTJ' // Default to Architect for judges
    })

    if (res.data && res.data.session_id) {
      // 3. Save session
      const character = {
        id: res.data.session_id,
        name: res.data.name,
        mbti: res.data.mbti,
        assets: res.data.total_assets
      }
      
      localStorage.setItem('username', username)
      localStorage.setItem('currentCharacter', JSON.stringify(character))
      localStorage.setItem('session_id', res.data.session_id)
      
      // 4. Redirect
      console.log('Session created, entering system...')
      router.push('/home')
    } else {
      throw new Error('Invalid response from server')
    }
  } catch (e) {
    console.error('Auto login failed:', e)
    alert('自动登录失败，请联系管理员或尝试刷新页面。\nError: ' + e.message)
    router.push('/login')
  }
})
</script>

<style scoped>
.auto-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #000;
  color: #0f0;
  font-family: 'Courier New', Courier, monospace;
}

.loading-text {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #333;
  border-top: 4px solid #0f0;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}

.sub-text {
  margin-top: 10px;
  font-size: 12px;
  opacity: 0.7;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
