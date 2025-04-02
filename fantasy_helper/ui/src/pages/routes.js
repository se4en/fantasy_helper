// routes.js
import { createRouter, createWebHistory } from 'vue-router'
import Homepage from './home/Home.vue'
import LeaguePage from './league/LeaguePage.vue'
import LoginPage from './login/LoginPage.vue'

const routes = [
  {
    path: '/login/',
    name: 'Login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: Homepage,
    meta: { requiresAuth: false }

  },
  {
    path: '/league/:leagueSlug',
    name: 'LeaguePage',
    component: LeaguePage,
    props: true,
    meta: { requiresAuth: false }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Authentication guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('access_token');
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' });
  } else if (to.name === 'Login' && isAuthenticated) {
    next({ name: 'Home' });
  } else {
    next();
  }
});

export default router;
