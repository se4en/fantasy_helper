<script setup>
import { useRoute } from 'vue-router'

function hasTourData(row, tourIndex) {
  // Check if this team has any data for this specific tour
  return row.tour_names?.length > tourIndex && 
         row.tour_numbers?.length > tourIndex && 
         row.tour_rivals?.length > tourIndex
}
import { storeToRefs } from 'pinia'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { onMounted, computed, ref, watch } from 'vue'
import { useCoeffStore } from '@/stores/coeffs.store'
import Loader from '@/components/Loader.vue'

const route = useRoute()
const coeffStore = useCoeffStore()
const { coeffs, isLoading: isCoeffsLoading, error } = storeToRefs(coeffStore)
const { showLoader } = useLoaderDelay(isCoeffsLoading, 500)

// Track if we've made the initial data fetch attempt
const hasInitiallyLoaded = ref(false)

// Get tour names for headers
const tourHeaders = computed(() => {
  try {
    if (!coeffs.value || !Array.isArray(coeffs.value) || coeffs.value.length === 0) {
      return []
    }
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
    return row.team_name || ''
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

// Helper function to get background color for attack coefficient
function getAttackCellStyle(row, tourIndex) {
  const color = row.tour_attack_colors?.length > tourIndex ? row.tour_attack_colors[tourIndex] : '#f0f0f0'
  return { backgroundColor: color }
}

// Helper function to get background color for defence coefficient
function getDefenceCellStyle(row, tourIndex) {
  const color = row.tour_defence_colors?.length > tourIndex ? row.tour_defence_colors[tourIndex] : '#f0f0f0'
  return { backgroundColor: color }
}

watch(
  () => route.params.leagueSlug,
  async (newLeagueSlug) => {
    if (newLeagueSlug) {
      hasInitiallyLoaded.value = false
      sortCoeffsBy.value = null
      sortCoeffsTourIndex.value = null
      sortCoeffsDirection.value = 'asc'
                                                                                                                                                                                                                                                                                                        
      try {
        await coeffStore.fetchCoeffs(newLeagueSlug)
      } finally {
        hasInitiallyLoaded.value = true
      }
    }
  },
  { immediate: true }
)

onMounted(async () => {
  try {
    if (!coeffs.value?.length && route.params.leagueSlug) {
      await coeffStore.fetchCoeffs(route.params.leagueSlug)
    } else if (coeffs.value?.length) {
      hasInitiallyLoaded.value = true
    }
  } catch (error) {
    console.error('Failed to load coefficients:', error)
    hasInitiallyLoaded.value = true
  }
})
</script>

<template>
  <div class="min-h-screen bg-white">
    <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- Header Section -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">Team Coefficients</h1>
        <p class="text-gray-600">Attack and defense coefficients for upcoming matches</p>
      </div>

      <!-- Loading State -->
      <div v-if="showLoader" class="flex justify-center py-20">
        <Loader />
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="text-center py-20">
        <div class="text-red-400 text-5xl mb-4">⚠️</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Error loading coefficients</h3>
        <p class="text-gray-600">{{ error }}</p>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="hasInitiallyLoaded && (!coeffs || coeffs.length === 0)" class="text-center py-20">
        <div class="text-gray-400 text-5xl mb-4">📊</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No coefficient data available</h3>
        <p class="text-gray-600">Check back later for coefficient updates</p>
      </div>
      
      <!-- Table -->
      <div v-else class="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="bg-gray-50">
                <th rowspan="2" class="team-column">Команда</th>
                
                <template v-for="(tourName, index) in tourHeaders" :key="'header-'+index">
                  <th colspan="3" class="tour-header">
                    {{ tourName || `Tour ${index + 1}` }}
                  </th>
                </template>
              </tr>
              <tr class="bg-gray-50 border-t border-gray-100">
                <template v-for="(_, tourIndex) in maxTours" :key="'subheader-'+tourIndex">
                  <th 
                    @click="setSort('attack', tourIndex)" 
                    class="sub-header attack-header"
                    :class="{ active: sortCoeffsBy === 'attack' && sortCoeffsTourIndex === tourIndex }"
                  >
                    <span class="header-content">
                      <span class="header-text">Атака</span>
                      <span class="sort-arrow" v-if="sortCoeffsBy === 'attack' && sortCoeffsTourIndex === tourIndex">
                        {{ sortCoeffsDirection === 'asc' ? '↑' : '↓' }}
                      </span>
                    </span>
                  </th>
                  <th 
                    @click="setSort('defence', tourIndex)" 
                    class="sub-header defence-header"
                    :class="{ active: sortCoeffsBy === 'defence' && sortCoeffsTourIndex === tourIndex }"
                  >
                    <span class="header-content">
                      <span class="header-text">Защита</span>
                      <span class="sort-arrow" v-if="sortCoeffsBy === 'defence' && sortCoeffsTourIndex === tourIndex">
                        {{ sortCoeffsDirection === 'asc' ? '↑' : '↓' }}
                      </span>
                    </span>
                  </th>
                  <th class="rival-header">Соперник</th>
                </template>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-50">
              <tr v-for="(row, rowIndex) in sortedCoeffs" :key="'row-'+rowIndex" class="hover:bg-gray-25 transition-colors">
                <td class="team-cell">{{ row.team_name }}</td>

                <template v-for="(_, tourIndex) in maxTours" :key="`coeff-${rowIndex}-${tourIndex}`">
                  <td class="attack-cell" :style="getAttackCellStyle(row, tourIndex)">
                    {{ hasTourData(row, tourIndex) ? (row.tour_attack_coeffs?.[tourIndex]?.toFixed(2) || '') : '' }}
                  </td>
                  <td class="defence-cell" :style="getDefenceCellStyle(row, tourIndex)">
                    {{ hasTourData(row, tourIndex) ? (row.tour_defence_coeffs?.[tourIndex]?.toFixed(2) || '') : '' }}
                  </td>
                  <td class="rival-cell">
                    {{ hasTourData(row, tourIndex) ? (row.tour_rivals?.[tourIndex] || '') : '' }} 
                    {{ hasTourData(row, tourIndex) ? (row.tour_match_types?.[tourIndex] || '') : '' }}
                  </td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Table styling */
table {
  border-collapse: separate;
  border-spacing: 0;
  min-width: 600px;
}

th {
  padding: 8px 6px;
  text-align: center;
  font-weight: 600;
  font-size: 12px;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

td {
  padding: 8px 6px;
  text-align: center;
  font-size: 12px;
  color: #111827;
  border-bottom: 1px solid #f3f4f6;
}

.team-column {
  min-width: 150px;
  position: sticky;
  left: 0;
  background: #f9fafb;
  z-index: 2;
  text-align: left;
  font-weight: 600;
  border-right: 1px solid #e5e7eb;
}

.tour-header {
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 700;
  color: #111827;
}

.attack-header,
.defence-header {
  width: 70px;
  min-width: 70px;
  max-width: 70px;
}

.sub-header {
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
}

.sub-header:hover {
  background-color: #f3f4f6;
}

.sub-header.active {
  background-color: #e5e7eb;
  color: #2563eb;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.header-text {
  flex-shrink: 0;
}

.sort-arrow {
  font-weight: bold;
  color: #2563eb;
  width: 12px;
  text-align: center;
  flex-shrink: 0;
}

.team-cell {
  background: white;
  font-weight: 600;
  position: sticky;
  left: 0;
  z-index: 1;
  text-align: left;
  border-right: 1px solid #f3f4f6;
}

.attack-cell,
.defence-cell {
  min-width: 80px;
}

.rival-cell {
  background-color: #f9fafb;
  font-size: 11px;
  color: #6b7280;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Hover effects */
tbody tr:hover {
  background-color: #f8fafc;
}

tbody tr:hover .team-cell {
  background-color: #f1f5f9;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  th, td {
    padding: 6px 4px;
    font-size: 11px;
  }
  
  .team-column {
    min-width: 100px;
  }
  
  .attack-header,
  .defence-header {
    width: 60px;
    min-width: 60px;
    max-width: 60px;
  }
  
  .rival-cell {
    font-size: 10px;
    max-width: 100px;
  }
}
</style>
