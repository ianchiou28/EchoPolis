import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: (typeof window !== 'undefined' && localStorage.getItem('theme')) || 'beige',
    themes: {
      orange: {
        name: '琥珀橙 (Amber)',
        key: 'orange'
      },
      black: {
        name: '深空黑 (Void)',
        key: 'black'
      },
      beige: {
        name: '羊皮纸 (Beige)',
        key: 'beige'
      }
    }
  }),

  getters: {
    theme: (state) => state.themes[state.currentTheme],
    isDark: (state) => state.currentTheme !== 'beige'
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
      const key = this.currentTheme || 'orange'
      document.documentElement.setAttribute('data-theme', key)
      // background is controlled by CSS variables now
      document.body.style.background = ''
      document.body.style.color = 'var(--term-text)'
    },

    toggleTheme() {
      this.setTheme(this.isDark ? 'beige' : 'orange')
    }
  }
})
