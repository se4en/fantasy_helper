// routes.js
import { createRouter, createWebHistory } from 'vue-router'
import Homepage from './home/Home.vue'

const routes = [
  {
    path: '/',
    component: Homepage
  },
  {
    path: '/league/:leagueSlug',
    // path: '/',
    name: 'LeaguePage',
    // component: () => import('@/views/LeaguePage.vue'),
    component: Homepage,
    // props: true
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
