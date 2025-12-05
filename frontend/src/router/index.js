import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import AutoLogin from '../views/AutoLogin.vue'
import CharacterSelect from '../views/CharacterSelect.vue'
// 新的三大模块
import WorldSandbox from '../views/WorldSandbox.vue'
import EventEcho from '../views/EventEcho.vue'
import PersonalCenter from '../views/PersonalCenter.vue'
// 保留旧页面用于兼容
import Home from '../views/HomeNew.vue'
import Assets from '../views/Assets.vue'
import World from '../views/World.vue'
import Profile from '../views/Profile.vue'
import Insights from '../views/Insights.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/character-select',
    name: 'CharacterSelect',
    component: CharacterSelect,
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    name: 'Root',
    component: import.meta.env.VITE_ENABLE_JUDGE_MODE === 'true' ? AutoLogin : undefined,
    redirect: import.meta.env.VITE_ENABLE_JUDGE_MODE === 'true' ? undefined : '/login'
  },
  // ========== 新的三大模块 ==========
  {
    path: '/world-sandbox',
    name: 'WorldSandbox',
    component: WorldSandbox,
    meta: { requiresAuth: true, requiresCharacter: true }
  },
  {
    path: '/event-echo',
    name: 'EventEcho',
    component: EventEcho,
    meta: { requiresAuth: true, requiresCharacter: true }
  },
  {
    path: '/personal-center',
    name: 'PersonalCenter',
    component: PersonalCenter,
    meta: { requiresAuth: true, requiresCharacter: true }
  },
  // ========== 保留旧页面兼容 ==========
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true, requiresCharacter: true }
  },
  {
    path: '/assets',
    name: 'Assets',
    component: Assets,
    meta: { requiresAuth: true, requiresCharacter: true }
  },
  {
    path: '/world',
    name: 'World',
    component: World,
    meta: { requiresAuth: true, requiresCharacter: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true, requiresCharacter: true }
  },
  {
    path: '/insights',
    name: 'Insights',
    component: Insights,
    meta: { requiresAuth: true, requiresCharacter: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const username = localStorage.getItem('username')
  const currentCharacter = localStorage.getItem('currentCharacter')

  if (to.meta.requiresAuth && !username) {
    next('/login')
  } else if (to.meta.requiresCharacter && !currentCharacter) {
    next('/character-select')
  } else if (to.path === '/login' && username) {
    next('/character-select')
  } else if (to.path === '/character-select' && currentCharacter) {
    // 已选择角色后，重定向到世界沙盘
    next('/world-sandbox')
  } else {
    next()
  }
})

export default router
