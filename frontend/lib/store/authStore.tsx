'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { ReactNode, createContext, useContext } from 'react'
import { apiClient } from '../api/client'

interface User {
  id: string
  username: string
  email: string
  created_at: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null
}

interface AuthActions {
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  clearError: () => void
}

type AuthStore = AuthState & AuthActions

const useAuthStoreBase = create<AuthStore>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      isLoading: false,
      error: null,

      // Actions
      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await apiClient.post('/auth/login', {
            username,
            password,
          })
          
          const { access_token, user } = response.data
          
          set({
            user,
            token: access_token,
            isLoading: false,
            error: null,
          })
          
          // 设置API客户端的默认token
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.response?.data?.detail || '登录失败',
          })
          throw error
        }
      },

      register: async (username: string, email: string, password: string) => {
        set({ isLoading: true, error: null })
        
        try {
          await apiClient.post('/auth/register', {
            username,
            email,
            password,
          })
          
          // 注册成功后自动登录
          await get().login(username, password)
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.response?.data?.detail || '注册失败',
          })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          error: null,
        })
        
        // 清除API客户端的token
        delete apiClient.defaults.headers.common['Authorization']
      },

      checkAuth: async () => {
        const { token } = get()
        
        if (!token) {
          set({ isLoading: false })
          return
        }
        
        set({ isLoading: true })
        
        try {
          // 设置token到API客户端
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
          
          // 验证token有效性（这里可以调用一个验证接口）
          // const response = await apiClient.get('/auth/me')
          
          set({ isLoading: false })
        } catch (error) {
          // Token无效，清除认证状态
          get().logout()
          set({ isLoading: false })
        }
      },

      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'echopolis-auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
      }),
    }
  )
)

// Context for providing the store
const AuthContext = createContext<AuthStore | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const store = useAuthStoreBase()
  
  return (
    <AuthContext.Provider value={store}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuthStore() {
  const store = useContext(AuthContext)
  if (!store) {
    throw new Error('useAuthStore must be used within AuthProvider')
  }
  return store
}