// routes.js
import { createRouter, createWebHistory } from 'vue-router'
import HomePage from './home/HomePage.vue'
import LeaguesPage from './leagues/LeaguesPage.vue'
import LeaguePage from './league/LeaguePage.vue'
import LeagueCoeffsPage from './league/LeagueCoeffsPage.vue'
import LeagueCalendarPage from './league/LeagueCalendarPage.vue'
import LoginPage from './login/LoginPage.vue'
import LoginCallback from './login/LoginCallback.vue'; 

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
    },
    children: [
      {
        path: '', // Default child route
        name: 'League',
        redirect: to => {
          return { 
            name: 'LeagueCoeffs', 
            params: { 
              leagueSlug: to.params.leagueSlug
            }
          }
        }
      },
      {
        path: 'coeffs',
        name: 'LeagueCoeffs',
        component: LeagueCoeffsPage,
        meta: {
          requiresAuth: false,
          showInSubNavigation: true,
          subNavTitle: 'Coefficients'
        }
      },
      {
        path: 'calendar',
        name: 'LeagueCalendar',
        component: LeagueCalendarPage,
        meta: {
          requiresAuth: false,
          showInSubNavigation: true,
          subNavTitle: 'Calendar'
        }
      }
    ]
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
  {                                                                                                                                                          
    path: '/login/callback',                                                                                                                                 
    name: 'LoginCallback',                                                                                                                                   
    component: LoginCallback,                                                                                                                                
    meta: {                                                                                                                                                  
      requiresAuth: false,                                                                                                                                   
      showInNavigation: false                                                                                                                                
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
