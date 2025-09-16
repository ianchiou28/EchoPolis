import { defineStore } from 'pinia'
import axios from 'axios'

// 设置API基础URL
axios.defaults.baseURL = 'http://localhost:8008'

export const useGameStore = defineStore('game', {
  state: () => ({
    avatar: null,
    mbtiTypes: {},
    sessionId: null
  }),

  actions: {
    generateSessionId() {
      this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
      return this.sessionId
    },

    reset() {
      this.avatar = null
      this.sessionId = null
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
      try {
        const sessionId = this.generateSessionId()
        const response = await axios.post('/api/create-avatar', {
          name,
          mbti,
          session_id: sessionId
        })
        
        if (response.data.success) {
          this.avatar = response.data.avatar
          return response.data.avatar
        }
      } catch (error) {
        console.error('Failed to create avatar:', error)
        throw error
      }
    },

    async generateSituation(context = '') {
      try {
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
          this.avatar = { ...this.avatar, ...response.data.avatar }
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
          this.avatar = { ...this.avatar, ...response.data.avatar }
        }
        
        return response.data
      } catch (error) {
        console.error('Failed to auto decision:', error)
        throw error
      }
    }
  }
})