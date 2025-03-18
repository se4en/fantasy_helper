// routes.js
import { createRouter, createWebHistory } from 'vue-router'
import Homepage from './home/Home.vue'
import LeaguePage from './league/LeaguePage.vue'

const routes = [
  {
    path: '/',
    component: Homepage
  },
  {
    path: '/league/:leagueSlug',
    name: 'LeaguePage',
    component: LeaguePage,
    props: true
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
