'use client'

import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import { ReactNode, createContext, useContext, useEffect } from 'react'
import { apiClient } from '../api/client'

// 类型定义
interface PersonalityProfile {
  openness: number
  conscientiousness: number
  extraversion: number
  agreeableness: number
  neuroticism: number
}

interface AgentState {
  health: number
  energy: number
  credit_score: number
  happiness: number
  stress: number
  credit_points: number
  insight_crystals: number
  net_worth: number
  monthly_income: number
  monthly_expenses: number
  relationship_status: string
  social_connections: number
  job_title: string
  job_satisfaction: number
  fq_level: number
  experience_points: number
}

interface AgentStatus {
  agent_id: string
  state: AgentState
  personality: PersonalityProfile
  traits: string[]
  trust_level: number
  current_age: number
  life_stage: string
  last_updated: string
}

interface EconomicIndicators {
  base_interest_rate: number
  inflation_rate: number
  unemployment_rate: number
  gdp_growth_rate: number
  consumer_price_index: number
  market_sentiment: number
}

interface NewsItem {
  id: string
  headline: string
  content: string
  category: string
  timestamp: string
  importance: number
  related_events: string[]
}

interface GameState {
  // Agent相关
  agentStatus: AgentStatus | null
  
  // 经济数据
  economicIndicators: EconomicIndicators | null
  marketData: any
  
  // 新闻和事件
  newsItems: NewsItem[]
  currentEvents: any[]
  
  // UI状态
  isGamePaused: boolean
  selectedTab: string
  
  // 加载状态
  isLoading: boolean
  error: string | null
}

interface GameActions {
  // Agent操作
  fetchAgentStatus: () => Promise<void>
  sendIntervention: (message: string, type: string) => Promise<any>
  
  // 数据获取
  fetchEconomicData: () => Promise<void>
  fetchNews: () => Promise<void>
  fetchEvents: () => Promise<void>
  
  // 游戏控制
  pauseGame: () => Promise<void>
  resumeGame: () => Promise<void>
  
  // UI控制
  setSelectedTab: (tab: string) => void
  clearError: () => void
}

type GameStore = GameState & GameActions

const useGameStoreBase = create<GameStore>()(
  subscribeWithSelector((set, get) => ({
    // Initial State
    agentStatus: null,
    economicIndicators: null,
    marketData: null,
    newsItems: [],
    currentEvents: [],
    isGamePaused: false,
    selectedTab: 'dashboard',
    isLoading: false,
    error: null,

    // Actions
    fetchAgentStatus: async () => {
      set({ isLoading: true, error: null })
      
      try {
        const response = await apiClient.get('/agent/status')
        set({
          agentStatus: response.data,
          isLoading: false,
        })
      } catch (error: any) {
        set({
          error: error.response?.data?.detail || '获取化身状态失败',
          isLoading: false,
        })
      }
    },

    sendIntervention: async (message: string, type: string) => {
      try {
        const response = await apiClient.post('/agent/intervention', {
          message,
          intervention_type: type,
        })
        
        // 发送干预后刷新化身状态
        await get().fetchAgentStatus()
        
        return response.data
      } catch (error: any) {
        set({
          error: error.response?.data?.detail || '发送回响失败',
        })
        throw error
      }
    },

    fetchEconomicData: async () => {
      try {
        const [indicatorsResponse, marketResponse] = await Promise.all([
          apiClient.get('/economy/indicators'),
          apiClient.get('/economy/market'),
        ])
        
        set({
          economicIndicators: indicatorsResponse.data.indicators,
          marketData: marketResponse.data.market_data,
        })
      } catch (error: any) {
        set({
          error: error.response?.data?.detail || '获取经济数据失败',
        })
      }
    },

    fetchNews: async () => {
      try {
        const response = await apiClient.get('/news/feed?limit=20')
        set({
          newsItems: response.data,
        })
      } catch (error: any) {
        set({
          error: error.response?.data?.detail || '获取新闻失败',
        })
      }
    },

    fetchEvents: async () => {
      try {
        const response = await apiClient.get('/events/current')
        set({
          currentEvents: response.data,
        })
      } catch (error: any) {
        set({
          error: error.response?.data?.detail || '获取事件失败',
        })
      }
    },

    pauseGame: async () => {
      try {
        await apiClient.post('/game/pause')
        set({ isGamePaused: true })
      } catch (error: any) {
        set({
          error: error.response?.data?.detail || '暂停游戏失败',
        })
      }
    },

    resumeGame: async () => {
      try {
        await apiClient.post('/game/resume')
        set({ isGamePaused: false })
      } catch (error: any) {
        set({
          error: error.response?.data?.detail || '恢复游戏失败',
        })
      }
    },

    setSelectedTab: (tab: string) => {
      set({ selectedTab: tab })
    },

    clearError: () => {
      set({ error: null })
    },
  }))
)

// Context Provider
const GameContext = createContext<GameStore | null>(null)

export function GameStateProvider({ children }: { children: ReactNode }) {
  const store = useGameStoreBase()
  
  // 自动数据刷新
  useEffect(() => {
    const interval = setInterval(() => {
      if (store.agentStatus) {
        store.fetchAgentStatus()
        store.fetchEconomicData()
        store.fetchNews()
        store.fetchEvents()
      }
    }, 30000) // 每30秒刷新一次
    
    return () => clearInterval(interval)
  }, [store])
  
  return (
    <GameContext.Provider value={store}>
      {children}
    </GameContext.Provider>
  )
}

export function useGameStore() {
  const store = useContext(GameContext)
  if (!store) {
    throw new Error('useGameStore must be used within GameStateProvider')
  }
  return store
}

// 选择器钩子
export function useAgentState() {
  return useGameStore().agentStatus?.state
}

export function useEconomicIndicators() {
  return useGameStore().economicIndicators
}

export function useNewsItems() {
  return useGameStore().newsItems
}