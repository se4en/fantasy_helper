<script setup>
import { useLeaguesInfoStore } from '@/stores/leaguesInfo.store'
import { storeToRefs } from 'pinia'
import { onMounted } from 'vue'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { useRouter } from 'vue-router'
import Loader from '@/components/Loader.vue'

const leaguesInfoStore = useLeaguesInfoStore()
const router = useRouter()

const { leaguesInfo, isLoading } = storeToRefs(leaguesInfoStore)
const { showLoader } = useLoaderDelay(isLoading, 500)

const leagueRoute = (league) => {
  return {
    name: 'LeagueCoeffs',
    params: {
      leagueSlug: league.name
    }
  }
}

onMounted(async () => {
  try {
    await leaguesInfoStore.fetchLeaguesInfo()
  } catch (error) {
    console.error(error)
  }
})
</script>

<script>                                                                                                                                                                                                                                                                                                                              
// Add this for compatibility                                                                                                                                                                                                                                                                                                         
export default {                                                                                                                                                                                                                                                                                                                      
  name: 'LeaguesPage'                                                                                                                                                                                                                                                                                                                 
}                                                                                                                                                                                                                                                                                                                                     
</script>

<template>
  <div class="min-h-screen bg-white">
    <div class="max-w-6xl mx-auto px-6 py-12">
      <!-- Header Section -->
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Choose Your League
        </h1>
        <p class="text-lg text-gray-600 max-w-2xl mx-auto">
          Select from our supported fantasy leagues to get started with advanced analytics and insights
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="showLoader" class="flex justify-center py-20">
        <Loader />
      </div>

      <!-- Leagues Grid -->
      <div v-else-if="leaguesInfo && leaguesInfo.length" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        <router-link 
          v-for="league in leaguesInfo" 
          :key="league.name"
          :to="leagueRoute(league)" 
          class="group flex flex-col items-center p-6 bg-white rounded-2xl border border-gray-100 hover:border-gray-200 hover:shadow-lg transition-all duration-300"
        >
          <div class="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">
            {{ league.emoji }}
          </div>
          <div class="text-center text-gray-900 font-medium text-sm leading-tight">
            {{ league.ru_name }}
          </div>
        </router-link>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-20">
        <div class="text-gray-400 text-6xl mb-4">🏆</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No leagues available</h3>
        <p class="text-gray-600">Check back later for more fantasy leagues</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom hover effects for league cards */
.group:hover {
  transform: translateY(-2px);
}

/* Smooth transitions for all interactive elements */
* {
  transition-property: color, background-color, border-color, transform, box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}
</style>
