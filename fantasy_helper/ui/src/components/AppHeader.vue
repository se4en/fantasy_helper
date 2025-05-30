<script>
  import { useLeaguesInfoStore } from '@/stores/leaguesInfo.store'
  import { storeToRefs } from 'pinia'

  export default {
    setup() {
      const leaguesInfoStore = useLeaguesInfoStore()
      const { leaguesInfo } = storeToRefs(leaguesInfoStore)
      return { 
        leaguesInfoStore,
        leaguesInfo
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
  <div class="wrapper">
    <nav class="navbar">
      <div class="container">
        <!-- <div class="logo">
          <router-link :to="{ name: 'Home' }">
            <img src="/your-logo.png" alt="Logo" class="navbar-logo" />
          </router-link>
        </div>
         -->
        <ul class="nav-links">
          <li>
            <router-link :to="{ name: 'Home' }" class="nav-link">
              Home
            </router-link>
          </li>
          
          <li v-for="route in availableRoutes" :key="route.name">
            <router-link :to="{ name: route.name }" class="nav-link">
              {{ route.meta?.label || route.name }}
            </router-link>
          </li>
        </ul>

        <div class="nav-center">
          <h1 class="site-title">
            <template v-if="showLeagueTitle">{{ currentLeague.ru_name || currentLeague.name }} <span class="league-emoji" v-if="currentLeague.emoji">{{ currentLeague.emoji }}</span></template>
            <template v-else>Fantasy Helper</template>
          </h1>
        </div>

        <ul class="nav-links-right">
          <li>
            <router-link :to="{ name: 'Login' }" class="nav-link">
              Login
            </router-link>
          </li>
        </ul>
      </div>
    </nav>
  </div>
</template>

<style scoped>
/* CSS Reset specifically for navigation elements */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  border: 0;
}

/* Your existing styles with some modifications */
.wrapper {
  width: 100vw; /* Use viewport width to ensure full width */
  margin: 0;
  padding: 0;
  overflow-x: hidden; /* Prevent horizontal scrollbar */
  border: 0;
  border-width: 0;
  outline: none;
}

.navbar {
  background-color: rgba(0, 0, 0, 0.8);
  position: sticky;
  top: 0;
  z-index: 2100;
  width: 100%;
  margin: 0;
  padding: 0;
  border: 0 !important;
  border-width: 0 !important;
  outline: none;
  box-shadow: none !important;
}

.container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin: 0;
  padding: 0;
  height: 60px;
  border: 0 !important;
  border-width: 0 !important;
}

.nav-links, .nav-links-right {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 20px;
  border: 0;
}

.nav-links li, .nav-links-right li {
  margin: 0;
  padding: 0;
  border: 0;
}

.nav-link {
  color: white; /* Change text color to white */
  font-weight: 700; /* Make text bold (700 is bold) */
  text-decoration: none;
  padding: 8px 12px;
  transition: all 0.2s ease; /* Transition all changing properties */
  border: 0;
  outline: none;
  position: relative; /* For positioning the underline indicator */
}

/* Hover effect - you can adjust this color as needed */
.nav-link:hover {
  color: #f0ad4e; /* Golden color on hover */
}

/* Active/current page styling */
.nav-link.router-link-exact-active,
.nav-link.router-link-active {
  color: #f0ad4e; /* Highlight color for active page */
  font-weight: 800; /* Even bolder for active page */
}

/* Center title styling */
.nav-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  text-align: center;
  height: 100%;
}

.league-title {
  margin: 0;
  padding: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.league-emoji {
  font-size: 1.4rem;
  margin-left: 8px;
}

.site-title {
  margin: 0;
  padding: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* @media (max-width: 768px) {
  .container {
    flex-direction: column;
    height: auto;
    padding: 10px 15px;
  }
  
  .nav-links, .nav-links-right {
    width: 100%;
    justify-content: center;
  }

  .nav-links-right {
    margin-top: 10px;
  }
} */

/* Add overrides for any potential framework styles */
nav, div, ul, li, a {
  border: 0 !important;
  border-width: 0 !important;
  border-style: none !important;
  outline: none !important;
  box-shadow: none !important;
}
</style>
