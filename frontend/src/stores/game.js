import { defineStore } from 'pinia'
import axios from 'axios'

export const useGameStore = defineStore('game', {
  state: () => ({
    avatar: null,
    assets: {
      total: 0,
      cash: 0,
      investments: []
    },
    trustLevel: 50,
    wealthLevel: '贫困',
    lifeStage: '起步期',
    aiReflection: '正在思考当前的财务状况...',
    aiMonologue: '我需要更谨慎地规划未来的投资方向。',
    aiResponse: '',
    currentSituation: '',
    situationOptions: []
  }),

  actions: {
    async loadAvatar() {
      try {
        const currentCharacter = localStorage.getItem('currentCharacter')
        console.log('[Game Store] currentCharacter:', currentCharacter)
        
        if (!currentCharacter) {
          console.log('[Game Store] 未选择角色')
          return
        }
        
        const char = JSON.parse(currentCharacter)
        console.log('[Game Store] 角色数据:', char)
        console.log('[Game Store] session_id:', char.id)
        
        const res = await axios.get('/api/avatar/status', {
          params: { session_id: char.id }
        })
        console.log('[Game Store] API响应:', res.data)
        
        this.avatar = res.data
        this.updateAssets()
      } catch (error) {
        console.error('[Game Store] 加载化身失败:', error)
      }
    },

    updateAssets() {
      if (this.avatar) {
        this.assets.total = this.avatar.total_assets
        this.assets.cash = this.avatar.cash
        this.trustLevel = this.avatar.trust_level
        this.calculateWealthLevel()
        this.calculateLifeStage()
      }
    },

    calculateWealthLevel() {
      const total = this.assets.total
      if (total < 50000) this.wealthLevel = '贫困'
      else if (total < 200000) this.wealthLevel = '温饱'
      else if (total < 500000) this.wealthLevel = '小康'
      else if (total < 1000000) this.wealthLevel = '富裕'
      else if (total < 5000000) this.wealthLevel = '富豪'
      else this.wealthLevel = '巨富'
    },

    calculateLifeStage() {
      if (!this.avatar) return
      const month = this.avatar.current_month
      if (month <= 12) this.lifeStage = '起步期'
      else if (month <= 36) this.lifeStage = '成长期'
      else if (month <= 60) this.lifeStage = '稳定期'
      else this.lifeStage = '成熟期'
    }
  }
})
