<script setup>
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { onMounted, computed, watch } from 'vue'
import { useLeaguesInfoStore } from '@/stores/leaguesInfo.store'
import Loader from '@/components/Loader.vue'

const route = useRoute()
const router = useRouter()

const leaguesInfoStore = useLeaguesInfoStore()
const { leaguesInfo, isLoading: isLeaguesInfoLoading } = storeToRefs(leaguesInfoStore)
const { showLeaguesInfoLoader } = useLoaderDelay(isLeaguesInfoLoading, 500)

const currentLeague = computed(() => {
  return leaguesInfo.value?.find(league => 
    league.name === route.params.leagueSlug
  ) || null
})

onMounted(async () => {
  try {
    if (!leaguesInfo.value?.length) {
      await leaguesInfoStore.fetchLeaguesInfo()
    }
  } catch (error) {
    console.error('Failed to load league data:', error)
    router.replace('/')
  }
})

watch(
  [currentLeague, isLeaguesInfoLoading],
  ([league, loading]) => {
    if (!loading && !league) {
      router.replace('/')
    }
  },
  { immediate: false }
)

const subnavItems = computed(() => {
  return router.options.routes
    .find(r => r.path === '/league/:leagueSlug')
    .children.filter(route => route.meta?.showInSubNavigation)
})
</script>

<template>
  <div class="wrapper">
    <nav class="subnavbar">
      <div class="subcontainer">
        <ul class="subnav-links">
          <li v-for="item in subnavItems" :key="item.name">
            <router-link :to="{ name: item.name, params: { leagueSlug: route.params.leagueSlug } }" class="subnav-link">
              {{ item.meta.subNavTitle }}
            </router-link>
          </li>
        </ul>
      </div>
    </nav>
  </div>

  <div class="league-page">
    <Loader v-if="showLeaguesInfoLoader" />
    
    <template v-else-if="currentLeague">
      <header class="league-header">
        <h1>{{ currentLeague.ru_name || currentLeague.name }}</h1>
        <div class="league-emoji" v-if="currentLeague.emoji">{{ currentLeague.emoji }}</div>
      </header>

      <!-- Router view for child routes -->
      <router-view />
    </template>
    
    <div v-else class="empty-state">
      <p>League not found.</p>
      <router-link to="/leagues">Return to leagues list</router-link>
    </div>
  </div>
</template>

<style scoped>
.league-page {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.league-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.league-emoji {
  font-size: 2rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-style: italic;
}

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

.subnavbar {
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

.subcontainer {
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

.subnav-links {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 20px;
  border: 0;
}

.subnav-links li {
  margin: 0;
  padding: 0;
  border: 0;
}

.subnav-link {
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
.subnav-link:hover {
  color: #f0ad4e; /* Golden color on hover */
}

/* Active/current page styling */
.subnav-link.router-link-exact-active,
.subnav-link.router-link-active {
  color: #f0ad4e; /* Highlight color for active page */
  font-weight: 800; /* Even bolder for active page */
}

nav, div, ul, li, a {
  border: 0 !important;
  border-width: 0 !important;
  border-style: none !important;
  outline: none !important;
  box-shadow: none !important;
}
</style>
