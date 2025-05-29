<script setup>
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { onMounted, computed, ref } from 'vue'
import { useCoeffStore } from '@/stores/coeffs.store'
import Loader from '@/components/Loader.vue'

const route = useRoute()
const coeffStore = useCoeffStore()
const { coeffs, isLoading: isCoeffsLoading, error } = storeToRefs(coeffStore)
const { showLoader } = useLoaderDelay(isCoeffsLoading, 500)

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

// Helper function to get background color for attack coefficient
function getAttackCellStyle(row, tourIndex) {
  const color = row.tour_attack_colors?.[tourIndex]
  return color ? { backgroundColor: color } : {}
}

// Helper function to get background color for defence coefficient
function getDefenceCellStyle(row, tourIndex) {
  const color = row.tour_defence_colors?.[tourIndex]
  return color ? { backgroundColor: color } : {}
}

onMounted(async () => {
  try {
    if (!coeffs.value?.length && route.params.leagueSlug) {
      await coeffStore.fetchCoeffs(route.params.leagueSlug)
    }
  } catch (error) {
    console.error('Failed to load coefficients:', error)
  }
})
</script>

<template>
  <div class="coeffs-page">
    <h2 class="section-title">Team Coefficients</h2>

    <Loader v-if="showLoader" />
    
    <div v-else-if="error" class="error-message">
      <p>Error loading coefficients: {{ error }}</p>
    </div>
    
    <div v-else-if="!coeffs || coeffs.length === 0" class="empty-state">
      <p>No coefficient data available for this league.</p>
    </div>
    
    <div v-else class="coefficients-table">
      <table>
        <thead>
          <tr>
            <th rowspan="2" class="team-column">Team</th>
            
            <template v-for="(tourName, index) in tourHeaders" :key="'header-'+index">
              <th colspan="3" class="tour-header">
                {{ tourName || `Tour ${index + 1}` }}
              </th>
            </template>
          </tr>
          <tr>
            <template v-for="(_, tourIndex) in maxTours" :key="'subheader-'+tourIndex">
              <th 
                @click="setSort('attack', tourIndex)" 
                class="sub-header attack-header"
                :class="{ active: sortCoeffsBy === 'attack' && sortCoeffsTourIndex === tourIndex }"
              >
                <span class="header-content">
                  <span class="header-text">Attack</span>
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
                  <span class="header-text">Defence</span>
                  <span class="sort-arrow" v-if="sortCoeffsBy === 'defence' && sortCoeffsTourIndex === tourIndex">
                    {{ sortCoeffsDirection === 'asc' ? '↑' : '↓' }}
                  </span>
                </span>
              </th>
              <th class="rival-header">Rival</th>
            </template>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(row, rowIndex) in sortedCoeffs" :key="'row-'+rowIndex">
            <td class="team-cell">{{ row.team_name }}</td>

            <template v-for="(tour, tourIndex) in maxTours" :key="`coeff-${rowIndex}-${tourIndex}`">
              <td class="attack-cell" :style="getAttackCellStyle(row, tourIndex)">
                {{ row.tour_attack_coeffs?.[tourIndex]?.toFixed(2) || '' }}
              </td>
              <td class="defence-cell" :style="getDefenceCellStyle(row, tourIndex)">
                {{ row.tour_defence_coeffs?.[tourIndex]?.toFixed(2) || '' }}
              </td>
              <td class="rival-cell">
                {{ row.tour_rivals?.[tourIndex] }} {{ row.tour_match_types?.[tourIndex] || '' }}
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.coeffs-page {
  padding: 1rem;
}

.section-title {
  text-align: center;
  margin: 1rem 0 2rem;
  color: #2c3e50;
}

.coefficients-table {
  overflow-x: auto;
  margin: 1rem 0;
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

.tour-header {
  background-color: #f0f0f0;
}

.attack-header {
  width: 100px;
  min-width: 100px;
  max-width: 100px;
}

.defence-header {
  width: 100px;
  min-width: 100px;
  max-width: 100px;
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

.header-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.header-text {
  flex-shrink: 0;
}

.sort-arrow {
  font-weight: bold;
  color: #2c3e50;
  width: 12px;
  text-align: center;
  flex-shrink: 0;
}

.team-cell {
  background: white;
  font-weight: 500;
  position: sticky;
  left: 0;
  z-index: 1;
}

.attack-cell {
  /* Background color will be set dynamically via :style */
}

.defence-cell {
  /* Background color will be set dynamically via :style */
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

.empty-state, .error-message {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error-message {
  color: #d9534f;
}
</style>
