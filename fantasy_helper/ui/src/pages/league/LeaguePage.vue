<script setup>
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { onMounted, computed, watch, ref } from 'vue'
import { useLeaguesInfoStore } from '@/stores/leaguesInfo.store'
import { useCoeffStore } from '@/stores/coeffs.store'
import { useCalendarStore } from '@/stores/calendar.store'


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

const calendarStore = useCalendarStore()
const { 
  calendar,
  isLoading: isCalendarLoading 
} = storeToRefs(calendarStore)
const { showCalendarLoader } = useLoaderDelay(isCalendarLoading, 500)


const currentLeague = computed(() => {
  return leagues_info.value?.find(league => 
    league.name === route.params.leagueSlug
  ) || null
})

onMounted(async () => {
  try {
    if (!leagues_info.value?.length) {
      await leaguesInfoStore.fetchLeaguesInfo()
    }
    if (!coeffs.value?.length && route.params.leagueSlug) {
      await coeffStore.fetchCoeffs(route.params.leagueSlug)
    }
    if (!calendar.value?.length && route.params.leagueSlug) {
      await calendarStore.fetchCalendar(route.params.leagueSlug)
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
  { immediate: false }
)

// Get tour names for headers
const tourHeaders = computed(() => {
  // Add comprehensive validation
  try {
    if (!coeffs.value || !Array.isArray(coeffs.value) || coeffs.value.length === 0) {
      return []
    }
    // Safely access tour_names with optional chaining and array check
    const firstRowTours = coeffs.value[0]?.tour_names
    return Array.isArray(firstRowTours) ? firstRowTours : []
  } catch (error) {
    console.error('Failed to get tour headers:', error)
    return []
  }
})

// Get maximum number of tours
const maxTours = computed(() => {
  try {
    if (!coeffs.value || !Array.isArray(coeffs.value) || coeffs.value.length === 0) {
      return 0
    }
    if (!coeffs.value[0]?.tour_names || !Array.isArray(coeffs.value[0]?.tour_names)) {
      return 0
    }
    return coeffs.value[0]?.tour_names.length
  } catch (error) {
    console.error('Failed to get tour headers:', error)
    return 0
  }
})

// Sorting coeff state
const sortCoeffsBy = ref(null)
const sortCoeffsTourIndex = ref(null)
const sortCoeffsDirection = ref('asc')

// Sorted coefficients
const sortedCoeffs = computed(() => {
  if (!sortCoeffsBy.value || sortCoeffsTourIndex.value === null) return coeffs.value
  
  return [...coeffs.value].sort((a, b) => {
    const aValue = getSortValue(a)
    const bValue = getSortValue(b)
    
    const modifier = sortCoeffsDirection.value === 'asc' ? 1 : -1
    return (aValue - bValue) * modifier
  })
})

function getSortValue(row) {
  if (sortCoeffsBy.value === 'attack') {
    return row.tour_attack_coeffs?.[sortCoeffsTourIndex.value] || 0
  }
  else if (sortCoeffsBy.value === 'defence') {
    return row.tour_defence_coeffs?.[sortCoeffsTourIndex.value] || 0
  }
  else if (sortCoeffsBy.value === 'team_name') {
    return row.team_name || 0
  } else {
    return 0 
  }
}

function setSort(type, tourIndex) {
  if (sortCoeffsBy.value === type && sortCoeffsTourIndex.value === tourIndex) {
    // Toggle direction if same column clicked
    sortCoeffsDirection.value = sortCoeffsDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    // New column clicked - reset to ascending
    sortCoeffsBy.value = type
    sortCoeffsTourIndex.value = tourIndex
    sortCoeffsDirection.value = 'asc'
  }
}

const caledarType = ref('points')

// Get tour names for headers
const tourCalendarHeaders = computed(() => {
  // Add comprehensive validation
  try {
    if (!calendar.value || !Array.isArray(calendar.value) || calendar.value.length === 0) {
      return []
    }
    // Safely access tour_names with optional chaining and array check
    const firstRowTours = calendar.value[0]?.tour_names
    return Array.isArray(firstRowTours) ? firstRowTours : []
  } catch (error) {
    console.error('Failed to get tour headers:', error)
    return []
  }
})

// Get maximum number of tours
const maxCalendarTours = computed(() => {
  try {
    if (!calendar.value || !Array.isArray(calendar.value) || calendar.value.length === 0) {
      return 0
    }
    if (!calendar.value[0]?.tour_names || !Array.isArray(calendar.value[0]?.tour_names)) {
      return 0
    }
    return calendar.value[0]?.tour_names.length
  } catch (error) {
    console.error('Failed to get tour headers:', error)
    return 0
  }
})

const getCalendarCellStyle = (row, tourIndex) => {
  const color = {
    points: row.tour_points_colors?.[tourIndex],
    goals: row.tour_goals_colors?.[tourIndex],
    xg: row.tour_xg_colors?.[tourIndex]
  }[caledarType.value]

  return {
    backgroundColor: color || '#ffffff'
  }
}
</script>

<template>
  <Loader v-if="showLeaguesInfoLoader" />
  
  <div v-else-if="currentLeague">
    <h2 class="league-header">League name: {{ currentLeague.name }}</h2>
  </div>

  <Loader v-if="showCoeffsLoader" />
  <h2>Coeffs</h2>

  <div class="coefficients-table">
    <!-- Loading & Error States -->
    <div v-if="isCoeffsLoading" class="status-message">Loading coefficients...</div>
    <div v-else-if="error" class="status-message error">Error: {{ error.message }}</div>

    <!-- Data Table -->
    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <!-- Fixed Columns -->
            <th class="team-column" rowspan="2">Team</th>
            
            <!-- Dynamic Tour Columns -->
            <template v-if="maxTours > 0">
              <th 
                v-for="(tourName, index) in tourHeaders" 
                :key="index" 
                colspan="3"
              >
                {{ tourName || `Tour ${index + 1}` }}
              </th>
            </template>
          </tr>
          <tr>
            <template v-if="maxTours > 0">
              <template v-for="(_, tourIndex) in maxTours" :key="tourIndex">
                <th 
                  class="sub-header"
                  @click="setSort('attack', tourIndex)"
                  :class="{ 
                    active: sortCoeffsBy === 'attack' && sortCoeffsTourIndex === tourIndex 
                  }"
                >
                  Attack
                  <span v-if="sortCoeffsBy === 'attack' && sortCoeffsTourIndex === tourIndex">
                    {{ sortCoeffsDirection === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th 
                  class="sub-header"
                  @click="setSort('defence', tourIndex)"
                  :class="{ 
                    active: sortCoeffsBy === 'defence' && sortCoeffsTourIndex === tourIndex 
                  }"
                >
                  Defence
                  <span v-if="sortCoeffsBy === 'defence' && sortCoeffsTourIndex === tourIndex">
                    {{ sortCoeffsDirection === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th class="sub-header">Rival</th>
              </template>
            </template>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(row, rowIndex) in sortedCoeffs" :key="rowIndex">
            <!-- Fixed Columns -->
            <td class="team-cell">{{ row.team_name }}</td>

            <!-- Dynamic Tour Data -->
            <template v-for="(tour, tourIndex) in maxTours" :key="tourIndex">
              <td :style="{ backgroundColor: row.tour_attack_colors?.[tourIndex] || '#fff' }">
                {{ row.tour_attack_coeffs?.[tourIndex]?.toFixed(2) || '' }}
              </td>
              <td :style="{ backgroundColor: row.tour_defence_colors?.[tourIndex] || '#fff' }">
                {{ row.tour_defence_coeffs?.[tourIndex]?.toFixed(2) || '' }}
              </td>
              <td class="rival-cell">
                {{ row.tour_rivals?.[tourIndex] + " " + row.tour_match_types?.[tourIndex] || '' }}
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <Loader v-if="showCalendarLoader" />
  <h2>Calendar</h2>

  <div class="calendar-table">
    <!-- Loading & Error States -->
    <div v-if="isCalendarLoading" class="status-message">Loading calendar...</div>
    <div v-else-if="error" class="status-message error">Error: {{ error.message }}</div>

    <!-- Data Table -->
    <div v-else class="table-container">
      <!-- Selection Controls -->
      <div class="view-selector">
        <div class="label-group">
          <label for="viewSelect">Display Mode</label>
          <span class="help-text">Calendar type</span>
        </div>
        <select v-model="caledarType">
          <option value="points">Points</option>
          <option value="goals">Goals</option>
          <option value="xg">Expected Goals (xG)</option>
        </select>
      </div>

      <table>
        <thead>
          <tr>
            <!-- Fixed Columns -->
            <th class="team-column" rowspan="2">Team</th>

            <!-- Dynamic Tour Columns -->
            <template v-if="maxCalendarTours > 0">
              <th 
                v-for="(tourName, index) in tourCalendarHeaders" 
                :key="index" 
              >
                {{ tourName || `Tour ${index + 1}` }}
              </th>
            </template>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(row, rowIndex) in calendar" :key="rowIndex">
            <!-- Fixed Columns -->
            <td class="team-cell">{{ row.team_name }}</td>

            <!-- Dynamic Tour Data -->
            <template v-for="(tour, tourIndex) in maxCalendarTours" :key="tourIndex">
              <!-- <td v-for="(_, tourIndex) in maxCalendarTours" :key="tourIndex"> -->
              <td class="calendar-cell" :style="getCalendarCellStyle(row, tourIndex)">
                {{ row.tour_rivals?.[tourIndex] || '' }}
              </td>
              <!-- </td> -->
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
  width: 80%;
  border-collapse: collapse;
  min-width: 600px;
  margin-left: auto;
  margin-right: auto;
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
  cursor: pointer;
  transition: background-color 0.2s;
}

.sub-header:hover {
  background-color: #e9ecef;
}

.sub-header.active {
  background-color: #dee2e6;
}

.sub-header span {
  margin-left: 0.5rem;
  font-weight: bold;
  color: #2c3e50;
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
