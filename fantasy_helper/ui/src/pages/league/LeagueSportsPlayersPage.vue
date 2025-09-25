<script setup>
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { onMounted, computed, ref, watch } from 'vue'
import { useSportsPlayersStore } from '@/stores/sportsPlayers.store'
import Loader from '@/components/Loader.vue'

const route = useRoute()
const sportsPlayersStore = useSportsPlayersStore()
const { sportsPlayers, isLoading: isSportsPlayersLoading, error } = storeToRefs(sportsPlayersStore)
const { showLoader } = useLoaderDelay(isSportsPlayersLoading, 500)

// Filter and sorting state
const selectedTeam = ref('')
const selectedRole = ref('')
const maxPrice = ref(null)

// Sorting state
const sortBy = ref('percent_ownership_diff')
const sortDirection = ref('desc')

// Get unique teams and roles for filter options
const availableTeams = computed(() => {
  if (!sportsPlayers.value) return []
  const teams = [...new Set(sportsPlayers.value.map(player => player.team_name).filter(Boolean))]
  return teams.sort()
})

const availableRoles = computed(() => {
  if (!sportsPlayers.value) return []
  const roles = [...new Set(sportsPlayers.value.map(player => player.role).filter(Boolean))]
  return roles.sort()
})

// Get min and max prices for filter boundaries
const priceBoundaries = computed(() => {
  if (!sportsPlayers.value?.length) return { min: 0, max: 10 }
  
  const prices = sportsPlayers.value
    .map(player => player.price)
    .filter(price => price !== null && price !== undefined)
    
  if (prices.length === 0) return { min: 0, max: 10 }
  
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  
  // Round to nearest 0.5 for better UX
  return {
    min: Math.floor(minPrice * 2) / 2,
    max: Math.ceil(maxPrice * 2) / 2
  }
})

// Filtered sports players
const filteredSportsPlayers = computed(() => {
  if (!sportsPlayers.value) return []
  
  return sportsPlayers.value.filter(player => {
    // Team filter
    if (selectedTeam.value && player.team_name !== selectedTeam.value) {
      return false
    }
    
    // Role filter
    if (selectedRole.value && player.role !== selectedRole.value) {
      return false
    }
    
    // Price filters - ensure we only filter when maxPrice has a valid numeric value
    if (maxPrice.value !== null && maxPrice.value !== undefined && maxPrice.value !== '' && player.price > maxPrice.value) {
      return false
    }
    
    return true
  })
})

// Top 10 most popular players (highest percent_ownership_diff)
const topMostPopularPlayers = computed(() => {
  if (!filteredSportsPlayers.value) return []
  
  return [...filteredSportsPlayers.value]
    .filter(player => player.percent_ownership_diff !== null && player.percent_ownership_diff !== undefined)
    .sort((a, b) => (b.percent_ownership_diff || 0) - (a.percent_ownership_diff || 0))
    .slice(0, 10)
})

// Top 10 less popular players (lowest percent_ownership_diff)
const topLessPopularPlayers = computed(() => {
  if (!filteredSportsPlayers.value) return []
  
  return [...filteredSportsPlayers.value]
    .filter(player => player.percent_ownership_diff !== null && player.percent_ownership_diff !== undefined)
    .sort((a, b) => (a.percent_ownership_diff || 0) - (b.percent_ownership_diff || 0))
    .slice(0, 10)
})

// Sorted and filtered sports players for the table
const sortedSportsPlayers = computed(() => {
  if (!sortBy.value || !filteredSportsPlayers.value) return filteredSportsPlayers.value
  
  return [...filteredSportsPlayers.value].sort((a, b) => {
    const aValue = getSortValue(a)
    const bValue = getSortValue(b)
    
    // Handle null/undefined values
    if (aValue === null || aValue === undefined) return 1
    if (bValue === null || bValue === undefined) return -1
    
    const modifier = sortDirection.value === 'asc' ? 1 : -1
    
    if (typeof aValue === 'string') {
      return aValue.localeCompare(bValue) * modifier
    }
    
    return (aValue - bValue) * modifier
  })
})

function getSortValue(player) {
  return player[sortBy.value] || 0
}

function setSort(column) {
  if (sortBy.value === column) {
    // Toggle direction if same column clicked
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    // New column clicked - reset to descending for stats
    sortBy.value = column
    sortDirection.value = 'desc'
  }
}

async function fetchData() {
  if (route.params.leagueSlug) {
    await sportsPlayersStore.fetchSportsPlayers(route.params.leagueSlug)
  }
}

// Handle input clearing for number inputs
function handleMaxPriceInput(event) {
  if (event.target.value === '') {
    maxPrice.value = null
  }
}

function formatNumber(value) {
  if (value === null || value === undefined) return '-'
  
  if (typeof value === 'number') {
    if (value % 1 === 0) {
      return value.toString()
    } else {
      return value.toFixed(2)
    }
  }
  
  return value.toString()
}

function formatPercentage(value) {
  if (value === null || value === undefined) return '-'
  return `${value.toFixed(1)}%`
}

// Separate watcher for maxPrice to handle empty values
watch(maxPrice, (newValue) => {
  // Convert empty string to null for consistency
  if (newValue === '' || newValue === undefined) {
    maxPrice.value = null
  }
})

watch(
  () => route.params.leagueSlug,
  async (newLeagueSlug) => {
    if (newLeagueSlug) {
      sortBy.value = 'percent_ownership_diff'
      sortDirection.value = 'desc'
      selectedTeam.value = ''
      selectedRole.value = ''
      maxPrice.value = null
      await fetchData()
    }
  },
  { immediate: true }
)

onMounted(async () => {
  try {
    if (!sportsPlayers.value?.length && route.params.leagueSlug) {
      await fetchData()
    }
  } catch (error) {
    console.error('Failed to load sports players:', error)
  }
})
</script>

<template>
  <div class="min-h-screen bg-white">
    <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- Header Section -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">Sports Players Popularity</h1>
        <p class="text-gray-600">Player ownership and popularity trends in fantasy sports</p>
      </div>

      <!-- Loading State -->
      <div v-if="showLoader" class="flex justify-center py-20">
        <Loader />
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="text-center py-20">
        <div class="text-red-400 text-5xl mb-4">⚠️</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Error loading sports players</h3>
        <p class="text-gray-600">{{ error }}</p>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="!sportsPlayers || sportsPlayers.length === 0" class="text-center py-20">
        <div class="text-gray-400 text-5xl mb-4">⚽</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No sports players data available</h3>
        <p class="text-gray-600">Check back later for player updates</p>
      </div>
      
      <!-- Content -->
      <div v-else class="space-y-8">
        <!-- Top Players Summary Cards -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Most Popular Players -->
          <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span class="text-green-500 mr-2">📈</span>
              Top 10 Most Popular Players
            </h3>
            <div class="space-y-3">
              <div v-for="(player, index) in topMostPopularPlayers" :key="'popular-'+index" class="flex items-center justify-between py-2 border-b border-gray-50 last:border-b-0">
                <div class="flex-1">
                  <div class="font-medium text-gray-900">{{ player.name }}</div>
                  <div class="text-sm text-gray-500">
                    {{ player.team_name }} • {{ player.role }} • {{ player.price ? player.price.toFixed(1) : '-' }}
                  </div>
                </div>
                <div class="text-right">
                  <div class="font-semibold text-green-600">+{{ formatNumber(player.percent_ownership_diff) }}%</div>
                  <div class="text-sm text-gray-500">{{ formatPercentage(player.percent_ownership) }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Less Popular Players -->
          <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span class="text-red-500 mr-2">📉</span>
              Top 10 Less Popular Players
            </h3>
            <div class="space-y-3">
              <div v-for="(player, index) in topLessPopularPlayers" :key="'unpopular-'+index" class="flex items-center justify-between py-2 border-b border-gray-50 last:border-b-0">
                <div class="flex-1">
                  <div class="font-medium text-gray-900">{{ player.name }}</div>
                  <div class="text-sm text-gray-500">
                    {{ player.team_name }} • {{ player.role }} • {{ player.price ? player.price.toFixed(1) : '-' }}
                  </div>
                </div>
                <div class="text-right">
                  <div class="font-semibold text-red-600">{{ formatNumber(player.percent_ownership_diff) }}%</div>
                  <div class="text-sm text-gray-500">{{ formatPercentage(player.percent_ownership) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Filters -->
        <div class="mb-8">
          <!-- Combined Filters Card -->
          <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <div class="flex flex-wrap items-center justify-between gap-6">
              <h3 class="text-lg font-semibold text-gray-900">Filters</h3>
              <button
                v-if="selectedTeam || selectedRole || maxPrice !== null"
                @click="selectedTeam = ''; selectedRole = ''; maxPrice = null"
                class="clear-filters-btn"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
                Clear Filters
              </button>
            </div>
            
            <div class="flex flex-wrap gap-6 mt-4">
              <div class="filter-group">
                <label for="teamFilter" class="filter-label">Команда</label>
                <select
                  id="teamFilter"
                  v-model="selectedTeam"
                  class="filter-select min-w-[160px]"
                >
                  <option value="">все</option>
                  <option v-for="team in availableTeams" :key="team" :value="team">
                    {{ team }}
                  </option>
                </select>
              </div>
              
              <div class="filter-group">
                <label for="roleFilter" class="filter-label">Позиция</label>
                <select
                  id="roleFilter"
                  v-model="selectedRole"
                  class="filter-select min-w-[140px]"
                >
                  <option value="">все</option>
                  <option v-for="role in availableRoles" :key="role" :value="role">
                    {{ role }}
                  </option>
                </select>
              </div>
              
              <div class="filter-group">
                <label for="maxPrice" class="filter-label">Макс цена</label>
                <input
                  id="maxPrice"
                  v-model.number="maxPrice"
                  type="number"
                  :min="priceBoundaries.min"
                  :max="priceBoundaries.max"
                  step="0.5"
                  placeholder="нет"
                  class="filter-input"
                  @input="handleMaxPriceInput"
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Full Table -->
        <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
          <div class="px-6 py-4 border-b border-gray-100">
            <h3 class="text-lg font-semibold text-gray-900">All Players</h3>
            <p class="text-sm text-gray-600 mt-1">Complete list of players with ownership data</p>
          </div>
          
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="bg-gray-50">
                  <th
                    @click="setSort('name')"
                    class="sortable-header sticky left-0 bg-gray-50 z-10"
                    :class="{ active: sortBy === 'name' }"
                  >
                    <span class="header-content">
                      <span>Игрок</span>
                      <span class="sort-arrow" v-if="sortBy === 'name'">
                        {{ sortDirection === 'asc' ? '↑' : '↓' }}
                      </span>
                    </span>
                  </th>
                  <th
                    @click="setSort('team_name')"
                    class="sortable-header"
                    :class="{ active: sortBy === 'team_name' }"
                  >
                    <span class="header-content">
                      <span>Команда</span>
                      <span class="sort-arrow" v-if="sortBy === 'team_name'">
                        {{ sortDirection === 'asc' ? '↑' : '↓' }}
                      </span>
                    </span>
                  </th>
                  <th
                    @click="setSort('role')"
                    class="sortable-header"
                    :class="{ active: sortBy === 'role' }"
                  >
                    <span class="header-content">
                      <span>Позиция</span>
                      <span class="sort-arrow" v-if="sortBy === 'role'">
                        {{ sortDirection === 'asc' ? '↑' : '↓' }}
                      </span>
                    </span>
                  </th>
                  <th
                    @click="setSort('price')"
                    class="sortable-header"
                    :class="{ active: sortBy === 'price' }"
                  >
                    <span class="header-content">
                      <span>Цена</span>
                      <span class="sort-arrow" v-if="sortBy === 'price'">
                        {{ sortDirection === 'asc' ? '↑' : '↓' }}
                      </span>
                    </span>
                  </th>
                  <th
                    @click="setSort('percent_ownership')"
                    class="sortable-header"
                    :class="{ active: sortBy === 'percent_ownership' }"
                  >
                    <span class="header-content">
                      <span>Владение (%)</span>
                      <span class="sort-arrow" v-if="sortBy === 'percent_ownership'">
                        {{ sortDirection === 'asc' ? '↑' : '↓' }}
                      </span>
                    </span>
                  </th>
                  <th
                    @click="setSort('percent_ownership_diff')"
                    class="sortable-header"
                    :class="{ active: sortBy === 'percent_ownership_diff' }"
                  >
                    <span class="header-content">
                      <span>Изменение (%)</span>
                      <span class="sort-arrow" v-if="sortBy === 'percent_ownership_diff'">
                        {{ sortDirection === 'asc' ? '↑' : '↓' }}
                      </span>
                    </span>
                  </th>
                </tr>
              </thead>

              <tbody class="divide-y divide-gray-50">
                <tr v-for="(player, index) in sortedSportsPlayers" :key="'player-'+index" class="hover:bg-gray-25 transition-colors">
                  <td class="player-name-cell sticky left-0 bg-white z-10">{{ player.name || '-' }}</td>
                  <td class="data-cell">{{ player.team_name || '-' }}</td>
                  <td class="data-cell">{{ player.role || '-' }}</td>
                  <td class="data-cell">{{ player.price ? player.price.toFixed(1) : '-' }}</td>
                  <td class="data-cell">{{ formatPercentage(player.percent_ownership) }}</td>
                  <td class="data-cell" :class="{
                    'text-green-600': player.percent_ownership_diff > 0,
                    'text-red-600': player.percent_ownership_diff < 0,
                    'text-gray-500': player.percent_ownership_diff === 0 || player.percent_ownership_diff === null || player.percent_ownership_diff === undefined
                  }">
                    {{ player.percent_ownership_diff !== null && player.percent_ownership_diff !== undefined ? formatNumber(player.percent_ownership_diff) + '%' : '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
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
  min-width: 800px;
}

th {
  padding: 12px 8px;
  text-align: center;
  font-weight: 600;
  font-size: 12px;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}

td {
  padding: 12px 8px;
  text-align: center;
  font-size: 12px;
  color: #111827;
  border-bottom: 1px solid #f3f4f6;
}

.sortable-header {
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
  position: relative;
}

.sortable-header.sticky {
  position: sticky;
  left: 0;
  z-index: 11; /* Higher than player cells */
  background: #f9fafb; /* Ensure background covers content when scrolling */
}

.sortable-header:hover {
  background-color: #f3f4f6;
}

.sortable-header.active {
  background-color: #e5e7eb;
  color: #2563eb;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.sort-arrow {
  font-weight: bold;
  color: #2563eb;
  width: 12px;
  text-align: center;
  flex-shrink: 0;
}

.player-name-cell {
  background: white;
  font-weight: 600;
  text-align: left;
  min-width: 150px;
  border-right: 2px solid #9ca3af;
}

/* Sticky header for player name column */
th.sticky {
  position: sticky;
  left: 0;
  z-index: 10;
}

.data-cell {
  min-width: 80px;
}

/* Hover effects */
tbody tr:hover {
  background-color: #f8fafc;
}

tbody tr:hover .player-name-cell {
  background-color: #f1f5f9;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  th, td {
    padding: 8px 6px;
    font-size: 11px;
  }
  
  .player-name-cell {
    min-width: 120px;
  }
  
  .data-cell {
    min-width: 60px;
  }
}

/* Filter styling */
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 120px;
}

.filter-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 2px;
}

.filter-select {
  appearance: none;
  background: white;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 8px center;
  background-repeat: no-repeat;
  background-size: 16px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  padding: 12px 40px 12px 16px;
  font-size: 14px;
  color: #111827;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-select:hover {
  border-color: #9ca3af;
}

.filter-input {
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 14px;
  color: #111827;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  width: 120px;
}

.filter-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-input:hover {
  border-color: #9ca3af;
}

.filter-input::placeholder {
  color: #9ca3af;
}

.clear-filters-btn {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: #f3f4f6;
  color: #6b7280;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-filters-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

/* Responsive adjustments for filters */
@media (max-width: 768px) {
  .filter-group {
    min-width: 100%;
  }
  
  .filter-select {
    min-width: 100%;
  }
  
  .filter-input {
    width: 100%;
  }
}
</style>