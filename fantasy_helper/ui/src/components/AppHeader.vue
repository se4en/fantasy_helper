<script>
  import { useLeaguesInfoStore } from '@/stores/leaguesInfo.store'
  import { useAuthStore } from '@/stores/auth'
  import { storeToRefs } from 'pinia'

  export default {
    setup() {
      const leaguesInfoStore = useLeaguesInfoStore()
      const { leaguesInfo } = storeToRefs(leaguesInfoStore)
      
      const authStore = useAuthStore()
      const { isAuthenticated, user } = storeToRefs(authStore)
      
      // Wait for auth before fetching leagues
      if (!authStore.isInitialized) {
        authStore.fetchUser()
      }

      return { 
        leaguesInfoStore,
        leaguesInfo,
        authStore,
        isAuthenticated,
        user
      }
    },
    async mounted() {
      // Ensure leagues info is loaded when the header mounts
      if (!this.leaguesInfo?.length) {
        try {
          await this.leaguesInfoStore.fetchLeaguesInfo()
        } catch (error) {
          console.error('Failed to load leagues info in header:', error)
        }
      }
    },
    computed: {
      availableRoutes() {
        // return this.$router.getRoutes().filter(route => 
        return this.$router.options.routes.filter(route => 
          route.meta?.showInNavigation && 
          !route.meta?.requiresAuth && 
          route.name &&
          route.name !== 'Home' &&
          route.name !== 'Login'
        )
      },
      // Get current league if we're on a league page
      currentLeague() {
        const leagueSlug = this.$route.params.leagueSlug;
        if (!leagueSlug) {
          return null;
        }

        if (!this.leaguesInfo) {
          return null;
        }

        // Fix: Access leaguesInfo directly, not .value since it's already a ref
        const leagues = this.leaguesInfo || [];
        return leagues.find(league => league.name === leagueSlug) || null;
      },
      // Determine if we should show league title
      showLeagueTitle() {
        return this.$route.path.includes('/league/') && this.currentLeague
      },
      // Get the text for the login/user button
      loginButtonText() {
        if (this.isAuthenticated && this.user?.given_name) {
          return this.user.given_name
        }
        return 'Войти'
      }
    },
    watch: {
      // Watch for route changes to ensure league info is available
      '$route'(to, from) {
        if (to.path.includes('/league/') && !this.leaguesInfo?.length) {
          this.leaguesInfoStore.fetchLeaguesInfo()
        }
      }
    }
  }
</script>

<template>
  <header class="header">
    <nav class="nav-container">
      <!-- Left Navigation -->
      <div class="nav-left">
        <router-link :to="{ name: 'Home' }" class="nav-item nav-home">
          Старт
        </router-link>
        
        <router-link 
          v-for="route in availableRoutes" 
          :key="route.name"
          :to="{ name: route.name }" 
          class="nav-item"
        >
          {{ route.meta?.navTitle || route.name }}
        </router-link>
      </div>

      <!-- Center Title -->
      <div class="nav-center">
        <h1 class="site-title">
          <template v-if="showLeagueTitle">
            {{ currentLeague.ru_name || currentLeague.name }}
            <span v-if="currentLeague.emoji" class="league-emoji">{{ currentLeague.emoji }}</span>
          </template>
          <template v-else>Fantasy Helper</template>
        </h1>
      </div>

      <!-- Right Navigation -->
      <div class="nav-right">
        <router-link :to="{ name: 'Login' }" class="nav-item login-button">
          {{ loginButtonText }}
        </router-link>
      </div>
    </nav>
  </header>
</template>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 1000;
  width: 100%;
}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
}

.nav-left,
.nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
}

.nav-item {
  color: #374151;
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.nav-item:hover {
  color: #111827;
  background-color: rgba(0, 0, 0, 0.04);
}

.nav-item.router-link-active,
.nav-item.router-link-exact-active {
  color: #2563eb;
  background-color: rgba(37, 99, 235, 0.08);
  font-weight: 600;
}

.nav-home {
  font-weight: 600;
  color: #111827;
}

.login-button {
  background-color: #2563eb;
  color: white;
  font-weight: 600;
  border-radius: 8px;
  padding: 8px 16px;
}

.login-button:hover {
  background-color: #1d4ed8;
  color: white;
}

.login-button.router-link-active,
.login-button.router-link-exact-active {
  background-color: #1d4ed8;
  color: white;
}

.site-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin: 0;
  white-space: nowrap;
  letter-spacing: -0.025em;
}

.league-emoji {
  font-size: 22px;
  margin-left: 8px;
  vertical-align: middle;
}

/* Responsive Design */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 16px;
    height: 56px;
  }
  
  .nav-left,
  .nav-right {
    gap: 4px;
  }
  
  .nav-item {
    font-size: 13px;
    padding: 6px 8px;
  }
  
  .site-title {
    font-size: 18px;
  }
  
  .league-emoji {
    font-size: 20px;
    margin-left: 6px;
  }
}

@media (max-width: 640px) {
  .nav-container {
    flex-direction: column;
    height: auto;
    padding: 12px 16px;
    gap: 12px;
  }
  
  .nav-center {
    position: static;
    transform: none;
    order: -1;
  }
  
  .nav-left,
  .nav-right {
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>
