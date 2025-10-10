import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import Game from '../views/Game.vue'
import InvestmentTest from '../views/InvestmentTest.vue'
import InvestmentDemo from '../views/InvestmentDemo.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/home',
    name: 'Home',
    component: Home
  },
  {
    path: '/game',
    name: 'Game',
    component: Game
  },
  {
    path: '/investment-test',
    name: 'InvestmentTest',
    component: InvestmentTest
  },
  {
    path: '/investment-demo',
    name: 'InvestmentDemo',
    component: InvestmentDemo
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router