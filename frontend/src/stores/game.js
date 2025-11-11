import { defineStore } from 'pinia'
import axios from 'axios'

// 设置API基础URL
axios.defaults.baseURL = 'http://127.0.0.1:8000'

export const useGameStore = defineStore('game', {
  state: () => ({
    user: null,
    avatar: null,          // 当前活动化身数据
    avatars: [],           // 账号下所有化身简要列表
    currentAvatarId: null, // 当前化身ID
    mbtiTypes: {},
    sessionId: null
  }),

  actions: {
    setUser(username) {
      this.user = username
      if (!this.sessionId) {
        this.generateSessionId()
      }
    },

    generateSessionId() {
      this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
      return this.sessionId
    },

    resetSessionOnly() {
      // 保留当前账号与化身选择，只重置会话ID
      this.generateSessionId()
    },

    clearAvatarLocal() {
      this.avatar = null
      this.currentAvatarId = null
    },

    async loadMBTITypes() {
      try {
        const response = await axios.get('/api/mbti-types')
        this.mbtiTypes = response.data
      } catch (error) {
        console.error('Failed to load MBTI types:', error)
        // Fallback to default types
        this.mbtiTypes = {
          'INTP': { description: '逻辑学家 - 创新的发明家' },
          'ENTJ': { description: '指挥官 - 大胆的领导者' },
          'ISFJ': { description: '守护者 - 温暖的保护者' },
          'ESFP': { description: '表演者 - 自发的娱乐者' }
        }
      }
    },

    async createAvatar(name, mbti) {
      if (!this.user) throw new Error('请先登录账号')
      try {
        if (!this.sessionId) this.generateSessionId()
        const response = await axios.post('/api/create-avatar', {
          name,
          mbti,
            session_id: this.sessionId,
          username: this.user
        })
        if (response.data.success) {
          this.avatar = response.data.avatar
          this.currentAvatarId = this.avatar.avatar_id
          // 重新加载列表
          await this.fetchAvatars()
          return this.avatar
        }
        throw new Error(response.data.detail || '创建化身失败')
      } catch (error) {
        console.error('Failed to create avatar:', error)
        throw error
      }
    },

    async fetchAvatars() {
      if (!this.user) return []
      try {
        const res = await axios.get(`/api/avatars/${this.user}`)
        if (res.data.success) {
          this.avatars = res.data.avatars
          return this.avatars
        }
        return []
      } catch (e) {
        console.error('获取化身列表失败', e)
        return []
      }
    },

    async selectAvatar(avatarId) {
      // 根据化身ID获取详细数据并建立新会话
      try {
        // 1. 获取化身详情
        const res = await axios.get(`/api/avatar/${avatarId}`)
        if (!res.data.success) throw new Error('化身不存在')
        this.avatar = res.data.avatar
        this.currentAvatarId = avatarId
        // 2. 使用新会话启动后端session
        this.resetSessionOnly()
        const start = await axios.post('/api/start-session', {
          avatar_id: avatarId,
          session_id: this.sessionId
        })
        if (start.data && start.data.success) {
          this.avatar = start.data.avatar
          return this.avatar
        }
        throw new Error('建立会话失败')
      } catch (e) {
        console.error('选择化身失败', e)
        throw e
      }
    },

    async resetAvatar(avatarId) {
      try {
        const res = await axios.post(`/api/avatar/${avatarId}/reset`)
        if (res.data.success) {
          // 重置后重新获取化身数据与列表
          this.avatar = res.data.avatar
          this.currentAvatarId = avatarId
          await this.fetchAvatars()
          // 重置后也建立新会话，防止旧状态残留
          this.resetSessionOnly()
          const start = await axios.post('/api/start-session', {
            avatar_id: avatarId,
            session_id: this.sessionId
          })
          if (start.data && start.data.success) {
            this.avatar = start.data.avatar
          }
          return this.avatar
        }
        throw new Error('重置失败')
      } catch (e) {
        console.error('重置化身失败', e)
        throw e
      }
    },

    async generateSituation(context = '') {
      try {
        if (!this.sessionId) this.generateSessionId()
        const response = await axios.post('/api/generate-situation', {
          session_id: this.sessionId,
          context
        })
        return response.data
      } catch (error) {
        console.error('Failed to generate situation:', error)
        throw error
      }
    },

    async sendEcho(echoText) {
      try {
        const response = await axios.post('/api/echo', {
          session_id: this.sessionId,
          echo_text: echoText
        })
        if (response.data.avatar) {
          this.avatar = response.data.avatar
        }
        return response.data
      } catch (error) {
        console.error('Failed to send echo:', error)
        throw error
      }
    },

    async autoDecision() {
      try {
        const response = await axios.post('/api/auto-decision', {
          session_id: this.sessionId
        })
        if (response.data.avatar) {
          this.avatar = response.data.avatar
        }

        return response.data
      } catch (error) {
        console.error('Failed to auto decision:', error)
        throw error
      }
    },

    async reset() {
      try {
        const avatarId = this.currentAvatarId || (this.avatar && this.avatar.avatar_id)
        if (avatarId) {
          await this.resetAvatar(avatarId)
        } else {
          this.clearAvatarLocal()
          this.resetSessionOnly()
        }
      } catch (e) {
        console.error('重置失败', e)
        throw e
      }
    },
    async resetGame() { // 新增别名，避免某些环境中 reset 被覆盖
      return this.reset()
    }
  }
})