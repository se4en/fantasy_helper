<script setup>
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { onMounted, computed, watch } from 'vue'
import { useLeaguesInfoStore } from '@/stores/leaguesInfo.store'
import { useCoeffStore } from '@/stores/coeffs.store'

const route = useRoute()
const router = useRouter()

const leaguesInfoStore = useLeaguesInfoStore()
const { 
  leagues_info,
  isLoading: isLeaguesInfoLoading 
} = storeToRefs(leaguesInfoStore)
const { showLeaguesInfoLoader } = useLoaderDelay(isLeaguesInfoLoading, 500)

const coeffStore = useCoeffStore()
const { 
  coeffs,
  isLoading: isCoeffsLoading 
} = storeToRefs(coeffStore)
const { showCoeffsLoader } = useLoaderDelay(isCoeffsLoading, 500)


const currentLeague = computed(() => {
  return leagues_info.value?.find(league => 
    league.name === route.params.leagueSlug
  ) || null
})

const slugify = (str) => {
  return str
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special chars
    .replace(/\s+/g, '-')     // Replace spaces with -
    .replace(/--+/g, '-')     // Replace multiple - with single
    .trim()
}

onMounted(async () => {
  try {
    if (!leagues_info.value?.length) {
      await leaguesInfoStore.fetchLeaguesInfo()
    }
    if (!coeffs.value?.length) {
      await coeffStore.fetchCoeffs(route.params.leagueSlug)
    }
  } catch (error) {
    console.error('Failed to load data:', error)
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
  { immediate: true }
)

// Get maximum number of tours across all rows
const maxTours = computed(() => {
  return Math.max(...coeffs.value.map(row => 
    Math.max(
      row.tour_names?.length || 0,
      row.tour_attack_coeffs?.length || 0,
      row.tour_deffence_coeffs?.length || 0,
      row.tour_rivals?.length || 0
    )
  ))
})

// Get tour names for headers
const tourHeaders = computed(() => {
  if (coeffs.value.length === 0) return []
  return coeffs.value[0].tour_names || []
})
</script>

<template>
  <Loader v-if="showLeaguesInfoLoader" />
  
  <div v-else-if="currentLeague">
    <h2 class="league-header">League name: {{ currentLeague.name }}</h2>
  </div>

  <div class="coefficients-table">
    <!-- Loading & Error States -->
    <div v-if="isLoading" class="status-message">Loading coefficients...</div>
    <div v-else-if="error" class="status-message error">Error: {{ error.message }}</div>

    <!-- Data Table -->
    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <!-- Fixed Columns -->
            <th class="team-column" rowspan="2">Team</th>
            <!-- <th class="league-column" rowspan="2">League</th> -->
            
            <!-- Dynamic Tour Columns -->
            <th 
              v-for="(tourName, index) in tourHeaders" 
              :key="index" 
              colspan="3"
            >
              {{ tourName || `Tour ${index + 1}` }}
            </th>
          </tr>
          <tr>
            <template v-for="(_, tourIndex) in maxTours" :key="tourIndex">
              <th class="sub-header">Attack</th>
              <th class="sub-header">Defence</th>
              <th class="sub-header">Rival</th>
            </template>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(row, rowIndex) in coeffs" :key="rowIndex">
            <!-- Fixed Columns -->
            <td class="team-cell">{{ row.team_name }}</td>
            <!-- <td class="league-cell">{{ row.league_name }}</td> -->

            <!-- Dynamic Tour Data -->
            <template v-for="(tour, tourIndex) in maxTours" :key="tourIndex">
              <td :style="{ backgroundColor: row.tour_attack_colors?.[tourIndex] || '#fff' }">
                {{ row.tour_attack_coeffs?.[tourIndex]?.toFixed(2) || '' }}
              </td>
              <td :style="{ backgroundColor: row.tour_deffence_colors?.[tourIndex] || '#fff' }">
                {{ row.tour_deffence_coeffs?.[tourIndex]?.toFixed(2) || '' }}
              </td>
              <td class="rival-cell">
                {{ row.tour_rivals?.[tourIndex] || '' }}
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

</template>

<style scoped>
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-style: italic;
}

.league-header {
  text-align: center;
  margin: 2rem 0;
  padding: 0.5rem;
  font-size: 1.8rem;
  color: #2c3e50;
}

.coefficients-table {
  overflow-x: auto;
  margin: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

th, td {
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  text-align: center;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.team-column {
  min-width: 150px;
  position: sticky;
  left: 0;
  background: white;
  z-index: 2;
}

.league-column {
  min-width: 120px;
  position: sticky;
  left: 150px;
  background: white;
  z-index: 2;
}

.sub-header {
  min-width: 100px;
  font-weight: normal;
  background-color: #f1f3f5;
}

.team-cell {
  background: white;
  font-weight: 500;
}

.rival-cell {
  background-color: #f8f9fa;
}

tr:nth-child(even) {
  background-color: #fcfcfc;
}

tr:hover {
  background-color: #f5f5f5;
}
</style>
