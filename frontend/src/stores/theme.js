import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: 'pink',
    themes: {
      pink: {
        name: '少女粉',
        background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
        primary: '#ff9a9e',
        robot: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        robotHappy: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        robotSad: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        button: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)'
      },
      purple: {
        name: '梦幻紫',
        background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
        primary: '#667eea',
        robot: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        robotHappy: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
        robotSad: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        button: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      },
      blue: {
        name: '清新蓝',
        background: 'linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)',
        primary: '#4facfe',
        robot: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        robotHappy: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
        robotSad: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        button: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
      },
      green: {
        name: '薄荷绿',
        background: 'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)',
        primary: '#10b981',
        robot: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        robotHappy: 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)',
        robotSad: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        button: 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)'
      }
    }
  }),

  getters: {
    theme: (state) => state.themes[state.currentTheme]
  },

  actions: {
    setTheme(themeName) {
      if (this.themes[themeName]) {
        this.currentTheme = themeName
        this.applyTheme()
      }
    },

    applyTheme() {
      const theme = this.theme
      document.body.style.background = theme.background
    }
  }
})
