import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import router from './router'
import App from './App.vue'
// import design system first so app styles can override when needed
import './styles/design-system.css'
import './styles/game-theme.css'
import './style.css'
import './styles/terminal-theme.css'

// 配置 axios baseURL，生产环境使用子路径
axios.defaults.baseURL = import.meta.env.PROD ? '/echopolis' : ''

// set a default theme early (can be overridden by store later)
document.documentElement.setAttribute('data-theme', 'beige')

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
