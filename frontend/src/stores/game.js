import { defineStore } from 'pinia'
import axios from 'axios'

export const DISTRICT_META = {
  finance: {
    id: 'finance',
    name: '中央银行群',
    tagline: '银行 · 流动性中枢',
    spectrum: 'blue',
    icon: '🏦',
    coords: { x: 50, y: 45 }
  },
  tech: {
    id: 'tech',
    name: '量化交易所',
    tagline: '交易所 · 算法驱动',
    spectrum: 'violet',
    icon: '💹',
    coords: { x: 70, y: 35 }
  },
  housing: {
    id: 'housing',
    name: '房产中枢',
    tagline: '房产中心 · 城市更新',
    spectrum: 'amber',
    icon: '🏙️',
    coords: { x: 70, y: 65 }
  },
  learning: {
    id: 'learning',
    name: '知识引擎院',
    tagline: '教育 · 成长设计',
    spectrum: 'teal',
    icon: '📚',
    coords: { x: 30, y: 35 }
  },
  leisure: {
    id: 'leisure',
    name: '文娱漫游区',
    tagline: '文娱 · 体验经济',
    spectrum: 'rose',
    icon: '🎭',
    coords: { x: 50, y: 70 }
  },
  green: {
    id: 'green',
    name: '绿色能源港',
    tagline: '能源 · 可持续',
    spectrum: 'emerald',
    icon: '⚡',
    coords: { x: 30, y: 65 }
  }
}

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
    isBankrupt: false,
    aiReflection: '正在思考当前的财务状况...',
    aiMonologue: '我需要更谨慎地规划未来的投资方向。',
    aiResponse: '',
    currentSituation: '',
    situationOptions: [],
    assetHistory: [], // [{month, total, cash}]
    maxEquity: 0, // for drawdown
    decisionLog: [],
    districts: Object.values(DISTRICT_META),
    selectedDistrictId: null,
    cityEvents: [],
    transactions: [],
    chatMessages: [],
    isChatting: false,
    isLoadingDistrict: false,
    isAdvancingMonth: false,
    isAiInvesting: false,
    macroIndicators: {
      inflation: 2.4,
      interest: 4.5,
      market_idx: 12450,
      market_trend: 'up'
    }
  }),

  getters: {
    mood(state) {
      const n = state.assetHistory.length
      const total = state.assets.total
      if (n === 0) return 'neutral'
      const prev = state.assetHistory[n - 1].total
      const mom = total - prev // month-over-month change
      const maxEq = Math.max(state.maxEquity || 0, ...state.assetHistory.map(p => p.total), total)
      const drawdown = maxEq > 0 ? (total - maxEq) / maxEq : 0

      const scale = Math.max(1, maxEq || total || 1)
      const momRatio = mom / scale

      if (momRatio > 0.05 && drawdown > -0.02) return 'ecstatic'
      if (momRatio > 0.01 && drawdown > -0.05) return 'happy'
      if (momRatio < -0.05 || drawdown < -0.15) return 'despair'
      if (momRatio < -0.01 || drawdown < -0.08) return 'sad'
      if (momRatio < 0) return 'worried'
      return 'neutral'
    }
  },

  actions: {
    async loadAvatar() {
      try {
        const currentCharacter = localStorage.getItem('currentCharacter')
        if (!currentCharacter) {
          console.warn('[Game Store] 没有当前角色')
          return
        }
        const char = JSON.parse(currentCharacter)
        console.log('[Game Store] 加载角色状态:', char.id)
        
        // 使用统一的会话状态接口
        const res = await axios.get('/api/session/state', { 
          params: { 
            session_id: char.id,
            _t: Date.now() 
          } 
        })
        console.log('[Game Store] API返回数据:', res.data)
        
        // 映射返回的数据到avatar格式
        this.avatar = {
          name: res.data.name,
          mbti_type: res.data.mbti,
          current_month: res.data.current_month || 0,
          total_assets: res.data.total_assets || 0,
          cash: res.data.cash || 0,
          invested_assets: res.data.invested_assets || 0,
          trust_level: res.data.trust_level || 50,
          health: res.data.health || 80,
          happiness: res.data.happiness || 70,
          energy: res.data.energy || 75
        }
        
        // 加载投资数据
        const invRes = await axios.get('/api/investments', { 
          params: { 
            session_id: char.id,
            _t: Date.now()
          } 
        })
        this.assets.investments = Array.isArray(invRes.data) ? invRes.data : []
        console.log('[Game Store] 投资数据:', this.assets.investments)
        
        this.updateAssets()
        this.pushAssetSnapshot()
      } catch (error) {
        console.error('[Game Store] 加载化身失败:', error)
        // 如果会话不存在或无效(400/404)，自动清理并重定向
        if (error.response && (error.response.status === 400 || error.response.status === 404)) {
          console.warn('[Game Store] 会话无效，重置状态...')
          localStorage.removeItem('currentCharacter')
          localStorage.removeItem('session_id')
          localStorage.removeItem('username') // 也要清除username
          window.location.href = '/'
        }
      }
    },

    async loadCityState() {
      const character = this.getCurrentCharacter()
      if (!character) return
      // 移除阻塞的 loadAvatar 调用，让 bootstrapHome 并行处理
      const res = await axios.get('/api/city/state', { 
        params: { 
          session_id: character.id,
          _t: Date.now()
        } 
      })
      const backendStates = res.data?.districts || []
      this.districts = backendStates.map(state => ({
        ...DISTRICT_META[state.district_id] || DISTRICT_META[state.id] || {},
        ...state
      }))
      this.cityEvents = res.data?.events?.map(evt => ({
        id: evt.id,
        districtId: evt.district_id,
        timestamp: new Date(evt.created_at).getTime(),
        title: evt.title,
        description: evt.description,
        type: evt.type
      })) || this.cityEvents
    },

    updateAssets() {
      if (this.avatar) {
        this.assets.total = this.avatar.total_assets
        this.assets.cash = this.avatar.cash
        this.trustLevel = this.avatar.trust_level
        this.calculateWealthLevel()
        this.calculateLifeStage()
        this.checkBankruptcy()
      }
    },

    checkBankruptcy() {
      if (this.assets.cash < 0) {
        this.isBankrupt = true
      } else {
        this.isBankrupt = false
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
    },

    pushAssetSnapshot() {
      const month = this.avatar?.current_month ?? (this.assetHistory.length + 1)
      const total = this.assets.total
      const cash = this.assets.cash
      this.assetHistory.push({ month, total, cash })
      if (this.assetHistory.length > 36) this.assetHistory.shift()
      this.maxEquity = Math.max(this.maxEquity || 0, total)
    },

    getCurrentCharacter() {
      try {
        const raw = localStorage.getItem('currentCharacter')
        return raw ? JSON.parse(raw) : null
      } catch (error) {
        console.warn('[Game Store] 解析 currentCharacter 失败:', error)
        return null
      }
    },

    appendCityEvent(event) {
      const payload = {
        id: event.id || crypto.randomUUID?.() || `${Date.now()}`,
        timestamp: event.timestamp || Date.now(),
        districtId: event.districtId || this.selectedDistrictId,
        title: event.title,
        description: event.description,
        type: event.type || 'story'
      }
      this.cityEvents.unshift(payload)
      if (this.cityEvents.length > 12) {
        this.cityEvents.pop()
      }
    },

    appendChatMessage(message) {
      this.chatMessages.push(message)
      if (this.chatMessages.length > 50) this.chatMessages.shift()
    },

    async talkToAI(text) {
      if (!text?.trim()) return
      this.isChatting = true
      this.appendChatMessage({ role: 'user', text, timestamp: Date.now() })
      try {
        const character = this.getCurrentCharacter()
        const res = await axios.post('/api/ai/chat', {
          session_id: character?.id,
          message: text
        })
        this.appendChatMessage({
          role: 'ai',
          text: res.data.response,
          reflection: res.data.reflection,
          monologue: res.data.monologue,
          timestamp: Date.now()
        })
        this.aiReflection = res.data.reflection
        this.aiMonologue = res.data.monologue
      } catch (error) {
        console.error('[Game Store] AI chat failed:', error)
        this.appendChatMessage({ role: 'system', text: 'AI 暂时无法响应，请稍后重试。', timestamp: Date.now() })
      } finally {
        this.isChatting = false
      }
    },

    async advanceMonth(echoText = null) {
      if (this.isAdvancingMonth) return
      const character = this.getCurrentCharacter()
      if (!character) throw new Error('请先选择角色，再推进时间。')

      this.isAdvancingMonth = true
      try {
        // 使用统一的会话推进接口
        const res = await axios.post('/api/session/advance', {
          session_id: character.id,
          echo_text: echoText
        })
        if (res.data?.success) {
          const data = res.data
          
          // 更新情境
          const storyline = {
            title: `第${data.new_month}月 · 城市脉搏`,
            description: data.situation,
            options: data.options || [],
            ai_generated: data.ai_generated,
            income_breakdown: data.income_breakdown,
            expense_breakdown: data.expense_breakdown
          }
          this.currentSituation = storyline
          this.situationOptions = storyline.options
          
          // 更新宏观经济数据
          if (data.macro_economy) {
            this.macroIndicators = data.macro_economy
          }

          // 记录市场变化事件
          if (data.market_report) {
            const mr = data.market_report
            const marketDesc = mr.index_change > 0 
              ? `📈 市场上涨 ${mr.index_change}%` 
              : mr.index_change < 0 
                ? `📉 市场下跌 ${Math.abs(mr.index_change)}%`
                : '📊 市场横盘'
            this.appendCityEvent({
              type: 'market',
              title: '股市月报',
              description: `${marketDesc} | 领涨: ${mr.gainers?.[0]?.[1] || '无'} | 领跌: ${mr.losers?.[0]?.[1] || '无'}`
            })
          }

          // 记录事件
          this.appendCityEvent({
            districtId: this.selectedDistrictId,
            title: '月度结算',
            description: `收入¥${data.income_breakdown?.total?.toLocaleString() || 0} | 支出¥${data.expense_breakdown?.total?.toLocaleString() || 0} | 净现金流¥${data.net_cashflow?.toLocaleString() || 0}`,
            type: 'timeline'
          })

          // 直接从响应更新avatar状态
          if (this.avatar) {
            this.avatar.current_month = data.new_month
            this.avatar.cash = data.cash
            this.avatar.total_assets = data.total_assets
            this.avatar.invested_assets = data.invested_assets
            
            // 更新生活状态
            if (data.life_status) {
              this.avatar.happiness = data.life_status.happiness
              this.avatar.energy = data.life_status.energy
              this.avatar.health = data.life_status.health
            }
          }
          this.updateAssets()
          this.pushAssetSnapshot()
          
          // 更新 AI 思考
          if (data.reflection) {
            this.aiReflection = data.reflection
          }
          
          // 处理触发的事件
          if (data.events && data.events.length > 0) {
            for (const event of data.events) {
              this.appendCityEvent({
                type: 'event',
                title: event.title,
                description: event.description
              })
            }
            // 存储事件供EventModal使用
            this.pendingEvents = data.events
          }
          
          // 处理新成就
          if (data.achievements && data.achievements.length > 0) {
            for (const ach of data.achievements) {
              this.appendCityEvent({
                type: 'achievement',
                title: `🏆 ${ach.achievement?.name || '成就解锁'}`,
                description: ach.achievement?.description || ''
              })
            }
            this.newAchievements = data.achievements
          }
          
          // 异步刷新确保数据同步
          setTimeout(async () => {
            await this.loadAvatar()
          }, 100)
          
          return data
        }
      } finally {
        this.isAdvancingMonth = false
      }
    },

    async exploreDistrict(districtId) {
      this.selectedDistrictId = districtId
      const character = this.getCurrentCharacter()
      if (!character) {
        this.currentSituation = {
          title: '尚未选择角色',
          description: '从角色界面挑选一个身份，城市才会回应你。'
        }
        this.situationOptions = []
        return
      }

      this.isLoadingDistrict = true
      try {
        // 使用专门的区域事件接口
        const res = await axios.post(`/api/city/district/${districtId}`, {
          session_id: character.id,
          context: 'exploration'
        })
        
        const districtName = this.districts.find(d => d.id === districtId)?.name || '未知城区'
        const payload = {
          title: `${districtName} · 事件`,
          description: res.data.description || res.data.situation,
          options: res.data.options || []
        }
        
        this.currentSituation = payload
        this.situationOptions = payload.options
        this.appendCityEvent({
          districtId,
          title: payload.title,
          description: payload.description,
          type: 'story' // 区域事件通常是故事性的
        })
        await this.loadCityState()
      } catch (error) {
        console.error('[Game Store] exploreDistrict 失败:', error)
        this.currentSituation = {
          title: '连接中断',
          description: '无法接入该区域的数据流。',
          options: ['重试']
        }
      } finally {
        this.isLoadingDistrict = false
      }
    },

    async performDistrictAction(payload) {
      const character = this.getCurrentCharacter()
      if (!character) throw new Error('请先选择角色')

      try {
        const res = await axios.post('/api/world/action', {
          ...payload,
          session_id: character.id
        })
        
        if (res.data.success) {
          // Refresh data
          await Promise.all([this.loadAvatar(), this.loadCityState()])
          
          // Add to event log
          this.appendCityEvent({
            districtId: payload.building,
            title: payload.action_name,
            description: res.data.message,
            type: 'action'
          })
        }
        return res.data
      } catch (error) {
        console.error('[Game Store] 执行区域动作失败:', error)
        throw error.response?.data?.detail ? new Error(error.response.data.detail) : error
      }
    },

    async requestAiInvestment() {
      if (this.isAiInvesting) return
      const character = this.getCurrentCharacter()
      if (!character) throw new Error('请先选择角色，再请求 AI 投资建议。')

      this.isAiInvesting = true
      try {
        const res = await axios.post('/api/ai/invest', {
          session_id: character.id,
          name: this.avatar?.name,
          mbti: this.avatar?.mbti_type,
          cash: this.assets.cash
        })
        if (res.data.success && res.data.investment) {
          const { investment } = res.data
          this.appendCityEvent({
            type: 'ai',
            title: `AI 投资 · ${investment.name}`,
            description: `金额 ¥${investment.amount?.toLocaleString?.('zh-CN') || investment.amount} · 期限 ${investment.duration} 个月`
          })
          await Promise.all([this.loadAvatar(), this.loadCityState()])
        } else {
          this.appendCityEvent({
            type: 'ai',
            title: 'AI 暂无投资动作',
            description: res.data.message || 'AI 认为当下保持观望更稳妥。'
          })
        }
      } finally {
        this.isAiInvesting = false
      }
    },

    async generateSituation() {
      const character = this.getCurrentCharacter()
      if (!character) {
        this.currentSituation = {
          title: '尚未选择角色',
          description: '请先选择或创建角色'
        }
        this.situationOptions = []
        return
      }
      
      try {
        const res = await axios.post('/api/generate-situation', {
          session_id: character.id,
          context: this.selectedDistrictId || ''
        })
        
        this.currentSituation = {
          title: '当前情况',
          description: res.data.situation || '城市正等待你的探索',
          options: res.data.options || [],
          ai_thoughts: res.data.ai_thoughts
        }
        this.situationOptions = this.currentSituation.options
      } catch (error) {
        console.error('[Game Store] 生成情况失败:', error)
        this.currentSituation = {
          title: '加载失败',
          description: '无法生成新情况，请稍后重试'
        }
        this.situationOptions = []
      }
    },

    async loadTransactions() {
      const character = this.getCurrentCharacter()
      if (!character) return
      try {
        const res = await axios.get(`/api/session/transactions`, {
          params: { session_id: character.id, limit: 50 }
        })
        this.transactions = res.data || []
      } catch (error) {
        console.error('[Game Store] 加载交易记录失败:', error)
        this.transactions = []
      }
    },

    async bootstrapHome() {
      console.log('[Game Store] bootstrapHome 开始')
      // 检查并修复旧的localStorage数据（数字id → session_id）
      const character = this.getCurrentCharacter()
      if (character && typeof character.id === 'number') {
        console.log('[Game Store] 检测到旧的数字ID格式，尝试自动迁移...')
        const username = localStorage.getItem('username')
        if (username) {
          try {
            // 重新获取角色列表，获取正确的session_id
            const res = await axios.get(`/api/characters/${username}`)
            const characters = res.data || []
            // 尝试找到同名角色
            const matchedChar = characters.find(c => c.name === character.name)
            if (matchedChar) {
              console.log(`[Game Store] 找到匹配角色，从 id=${character.id} 迁移到 session_id=${matchedChar.id}`)
              localStorage.setItem('currentCharacter', JSON.stringify(matchedChar))
              localStorage.setItem('session_id', matchedChar.id)
              // 迁移成功，继续加载
            } else {
              console.warn('[Game Store] 未找到匹配角色，清理旧数据')
              localStorage.removeItem('currentCharacter')
              localStorage.removeItem('session_id')
              return
            }
          } catch (error) {
            console.error('[Game Store] 迁移失败:', error)
            localStorage.removeItem('currentCharacter')
            localStorage.removeItem('session_id')
            return
          }
        } else {
          console.warn('[Game Store] 无username信息，清理旧数据')
          localStorage.removeItem('currentCharacter')
          localStorage.removeItem('session_id')
          return
        }
      }
      
      console.log('[Game Store] 开始并行加载数据（非阻塞）')
      
      // 并行加载核心数据（不阻塞页面渲染）
      // 使用独立的 Promise，不等待完成
      this.loadAvatar().catch(err => console.error('[Game Store] loadAvatar 失败:', err))
      this.loadCityState().catch(err => console.error('[Game Store] loadCityState 失败:', err))
      this.loadTransactions().catch(err => console.error('[Game Store] loadTransactions 失败:', err))
      this.loadMacroIndicators().catch(err => console.error('[Game Store] loadMacroIndicators 失败:', err))
      
      // 情境生成放在后台，不阻塞
      if (!this.currentSituation) {
        console.log('[Game Store] 开始后台生成情境')
        this.generateSituation().catch(err => {
          console.error('[Game Store] 情境生成失败:', err)
        })
      }
      
      console.log('[Game Store] bootstrapHome 立即返回（数据在后台加载）')
    },

    async sendEcho(echoText, echoType = 'advisory') {
      const character = this.getCurrentCharacter()
      if (!character) throw new Error('请先选择角色')
      
      try {
        const res = await axios.post('/api/echo', {
          session_id: character.id,
          echo_text: echoText,
          echo_type: echoType
        })
        return res.data
      } catch (error) {
        console.error('[Game Store] 发送回响失败:', error)
        throw error
      }
    },

    async makeDecision(optionIndex) {
      const character = this.getCurrentCharacter()
      if (!character) throw new Error('请先选择角色')
      
      const optionText = this.situationOptions[optionIndex] || ''

      try {
        const res = await axios.post('/api/decide', {
          session_id: character.id,
          option_index: optionIndex,
          option_text: optionText
        })
        
        // 更新当前状态
        if (res.data.decision_impact) {
          this.appendCityEvent({
            type: 'decision',
            title: '决策结果',
            description: res.data.ai_thoughts || '决策已执行',
            impact: res.data.decision_impact
          })
        }
        
        await this.loadAvatar()
        return res.data
      } catch (error) {
        console.error('[Game Store] 决策失败:', error)
        throw error
      }
    },

    async finishSession() {
      const character = this.getCurrentCharacter()
      if (!character) throw new Error('请先选择角色')
      
      try {
        const res = await axios.post('/api/session/finish', {
          session_id: character.id
        })
        return res.data
      } catch (error) {
        console.error('[Game Store] 结束会话失败:', error)
        throw error
      }
    },

    async getTimeline(limit = 36) {
      const character = this.getCurrentCharacter()
      if (!character) return []
      
      try {
        const res = await axios.get('/api/session/timeline', {
          params: { session_id: character.id, limit }
        })
        return res.data
      } catch (error) {
        console.error('[Game Store] 获取时间轴失败:', error)
        return []
      }
    },

    async loadMacroIndicators() {
      try {
        const res = await axios.get('/api/macro/indicators')
        if (res.data) {
          this.macroIndicators = res.data
        }
      } catch (error) {
        console.error('[Game Store] 加载宏观指标失败:', error)
      }
    },

    async fetchCharacters(username) {
      try {
        const res = await axios.get(`/api/characters/${username}`)
        return res.data
      } catch (error) {
        console.error('[Game Store] 获取角色列表失败:', error)
        throw error
      }
    },

    async createCharacter(payload) {
      try {
        const res = await axios.post('/api/characters/create', payload)
        return res.data
      } catch (error) {
        console.error('[Game Store] 创建角色失败:', error)
        throw error
      }
    },

    async deleteCharacter(sessionId) {
      try {
        const res = await axios.delete(`/api/characters/session/${sessionId}`)
        return res.data
      } catch (error) {
        console.error('[Game Store] 删除角色失败:', error)
        throw error
      }
    },

    resetState() {
      this.avatar = null
      this.assets = { total: 0, cash: 0, investments: [] }
      this.trustLevel = 50
      this.wealthLevel = '贫困'
      this.lifeStage = '起步期'
      this.isBankrupt = false
      this.aiReflection = '正在思考当前的财务状况...',
      this.aiMonologue = '我需要更谨慎地规划未来的投资方向。'
      this.aiResponse = ''
      this.currentSituation = ''
      this.situationOptions = []
      this.assetHistory = []
      this.maxEquity = 0
      this.decisionLog = []
      this.selectedDistrictId = null
      this.cityEvents = []
      this.chatMessages = []
      this.isChatting = false
      this.isLoadingDistrict = false
      this.isAdvancingMonth = false
      this.isAiInvesting = false
    }
  }
})
