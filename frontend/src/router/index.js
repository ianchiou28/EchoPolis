import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Assets from '../views/Assets.vue'
import World from '../views/World.vue'
import Profile from '../views/Profile.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/assets',
    name: 'Assets',
    component: Assets
  },
  {
    path: '/world',
    name: 'World',
    component: World
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
