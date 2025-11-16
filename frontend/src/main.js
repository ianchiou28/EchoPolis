import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
// import design system first so app styles can override when needed
import './styles/design-system.css'
import './styles/game-theme.css'
import './style.css'

// set a default theme early (can be overridden by store later)
document.documentElement.setAttribute('data-theme', 'slate')

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
