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
  // return this.$router.getRoutes()
  return router.options.routes
    .find(r => r.path === '/league/:leagueSlug')
    .children.filter(route => route.meta?.showInSubNavigation)
})
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- Sub Navigation -->
    <nav class="subnav-header">
      <div class="subnav-container">
        <div class="subnav-links">
          <router-link 
            v-for="item in subnavItems" 
            :key="item.name"
            :to="{ name: item.name, params: { leagueSlug: route.params.leagueSlug } }" 
            class="subnav-item"
          >
            {{ item.meta.subNavTitle }}
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="league-content">
      <div v-if="showLeaguesInfoLoader" class="flex justify-center py-20">
        <Loader />
      </div>
      
      <template v-else-if="currentLeague">
        <!-- Router view for child routes -->
        <router-view />
      </template>
      
      <div v-else class="text-center py-20">
        <div class="text-gray-400 text-6xl mb-4">🏆</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">League not found</h3>
        <p class="text-gray-600 mb-6">The league you're looking for doesn't exist or has been removed.</p>
        <router-link 
          to="/leagues"
          class="inline-block bg-gray-900 text-white px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors font-medium"
        >
          Return to leagues list
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.subnav-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 64px; /* Position below main header */
  z-index: 900;
  width: 100%;
}

.subnav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
}

.subnav-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

.subnav-item {
  color: #374151;
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.subnav-item:hover {
  color: #111827;
  background-color: rgba(0, 0, 0, 0.04);
}

.subnav-item.router-link-active,
.subnav-item.router-link-exact-active {
  color: #2563eb;
  background-color: rgba(37, 99, 235, 0.08);
  font-weight: 600;
}

.league-content {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Responsive Design */
@media (max-width: 768px) {
  .subnav-container {
    padding: 0 16px;
    height: 48px;
  }
  
  .subnav-links {
    gap: 4px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .subnav-item {
    font-size: 13px;
    padding: 6px 12px;
    flex-shrink: 0;
  }
  
  .league-content {
    padding: 16px;
  }
}

/* Smooth transitions for all interactive elements */
* {
  transition-property: color, background-color, border-color, transform, box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}
</style>
