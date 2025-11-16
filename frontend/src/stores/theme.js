import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: (typeof window !== 'undefined' && localStorage.getItem('theme')) || 'slate',
    themes: {
      slate: {
        name: '石墨蓝灰',
        key: 'slate'
      },
      silver: {
        name: '银灰',
        key: 'silver'
      },
      ocean: {
        name: '海雾蓝',
        key: 'ocean'
      },
      emerald: {
        name: '祖母绿',
        key: 'emerald'
      },
      royal: {
        name: '皇家紫',
        key: 'royal'
      },
      pink: {
        name: '少女粉',
        key: 'pink'
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
        try { localStorage.setItem('theme', themeName) } catch {}
        this.applyTheme()
      }
    },

    applyTheme() {
      const key = this.currentTheme || 'slate'
      document.documentElement.setAttribute('data-theme', key)
      // background is controlled by CSS variables now
      document.body.style.background = ''
      document.body.style.color = 'var(--text)'
    }
  }
})
