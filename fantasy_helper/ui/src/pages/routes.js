// routes.js
import { createRouter, createWebHistory } from 'vue-router'
import HomePage from './home/HomePage.vue'
import LeaguesPage from './leagues/LeaguesPage.vue'
import LeaguePage from './league/LeaguePage.vue'
import LoginPage from './login/LoginPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: {
      requiresAuth: false,
      showInNavigation: false,
      navTitle: 'Home'
    }
  },
  {
    path: '/leagues/',
    name: 'Leagues',
    component: LeaguesPage,
    meta: {
      requiresAuth: false,
      showInNavigation: true,
      navTitle: 'Leafues'
    }
  },
  {
    path: '/league/:leagueSlug',
    name: 'League',
    component: LeaguePage,
    props: true,
    meta: {
      requiresAuth: false,
      showInNavigation: false,
      navTitle: 'League'
    }
  },
  {
    path: '/login/',
    name: 'Login',
    component: LoginPage,
    meta: { 
      requiresAuth: false,
      showInNavigation: false,
      navTitle: 'Login'
    }
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
