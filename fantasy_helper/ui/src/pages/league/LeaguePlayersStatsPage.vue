<script setup>
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { onMounted, computed, ref, watch } from 'vue'
import { usePlayersStatsStore } from '@/stores/playersStats.store'
import Loader from '@/components/Loader.vue'

const route = useRoute()
const playersStatsStore = usePlayersStatsStore()
const { playersStats, isLoading: isPlayersStatsLoading, error } = storeToRefs(playersStatsStore)
const { showLoader } = useLoaderDelay(isPlayersStatsLoading, 500)

// Filter and sorting state
const gamesCount = ref(null)
const minMinutes = ref(null)
const selectedTeam = ref('')
const selectedRole = ref('')
const normalizationType = ref('')
const maxPrice = ref(null)

// Sorting state
const sortBy = ref(null)
const sortDirection = ref('desc')

// Get unique teams and roles for filter options
const availableTeams = computed(() => {
  if (!playersStats.value) return []
  const teams = [...new Set(playersStats.value.map(player => player.team_name).filter(Boolean))]
  return teams.sort()
})

const availableRoles = computed(() => {
  if (!playersStats.value) return []
  const roles = [...new Set(playersStats.value.map(player => player.role).filter(Boolean))]
  return roles.sort()
})

// Get min and max prices for filter boundaries
const priceBoundaries = computed(() => {
  if (!playersStats.value?.length) return { min: 0, max: 10 }
  
  const prices = playersStats.value
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

// Filtered players stats
const filteredPlayersStats = computed(() => {
  if (!playersStats.value) return []
  
  return playersStats.value.filter(player => {
    // Team filter
    if (selectedTeam.value && player.team_name !== selectedTeam.value) {
      return false
    }
    
    // Role filter
    if (selectedRole.value && player.role !== selectedRole.value) {
      return false
    }
    
    // Price filters
    if (maxPrice.value !== null && player.price > maxPrice.value) {
      return false
    }
    
    return true
  })
})

// Sorted and filtered players stats
const sortedPlayersStats = computed(() => {
  if (!sortBy.value || !filteredPlayersStats.value) return filteredPlayersStats.value
  
  return [...filteredPlayersStats.value].sort((a, b) => {
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
    await playersStatsStore.fetchPlayersStats(
      route.params.leagueSlug,
      gamesCount.value,
      normalizationType.value === 'minutes',
      normalizationType.value === 'matches',
      minMinutes.value
    )
  }
}

function formatIntStat(value) {
  if (value === null || value === undefined || value === 0) return '-'
  
  if (value % 1 === 0) {
    return value.toString()
  } else {
    return value.toFixed(2)
  }
}

// Watch for parameter changes
watch([gamesCount, normalizationType, minMinutes, maxPrice], () => {
  fetchData()
})

watch(
  () => route.params.leagueSlug,
  async (newLeagueSlug) => {
    if (newLeagueSlug) {
      sortBy.value = null
      sortDirection.value = 'desc'
      selectedTeam.value = ''
      selectedRole.value = ''
      maxPrice.value = null
      normalizationType.value = ''
      await fetchData()
    }
  },
  { immediate: true }
)

onMounted(async () => {
  try {
    if (!playersStats.value?.length && route.params.leagueSlug) {
      await fetchData()
    }
  } catch (error) {
    console.error('Failed to load players stats:', error)
  }
})
</script>

<template>
  <div class="min-h-screen bg-white">
    <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- Header Section -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">Player Statistics</h1>
        <p class="text-gray-600">Performance statistics for players in the league</p>
        
        <!-- Filters -->
        <div class="mt-6">
          <!-- Combined Filters Card -->
          <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <div class="flex flex-wrap items-center justify-between gap-6">
              <h3 class="text-lg font-semibold text-gray-900">Filters</h3>
              <button
                v-if="selectedTeam || selectedRole || gamesCount !== null || maxPrice !== null || normalizationType || minMinutes !== null"
                @click="selectedTeam = ''; selectedRole = ''; gamesCount = null; maxPrice = null; normalizationType = ''; minMinutes = null"
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
                <label for="gamesCount" class="filter-label">Кол-во матчей</label>
                <input
                  id="gamesCount"
                  v-model.number="gamesCount"
                  type="number"
                  placeholder="все"
                  class="filter-input"
                >
              </div>
              
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
                >
              </div>
              
              <div class="filter-group">
                <label for="normalizationFilter" class="filter-label">Усреднение</label>
                <select
                  id="normalizationFilter"
                  v-model="normalizationType"
                  class="filter-select min-w-[160px]"
                >
                  <option value="">нет</option>
                  <option value="minutes">по минутам (90)</option>
                  <option value="matches">по матчам</option>
                </select>
              </div>
              
              <div class="filter-group">
                <label for="minMinutes" class="filter-label">Мин минут</label>
                <input
                  id="minMinutes"
                  v-model.number="minMinutes"
                  type="number"
                  placeholder="нет"
                  class="filter-input"
                >
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="showLoader" class="flex justify-center py-20">
        <Loader />
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="text-center py-20">
        <div class="text-red-400 text-5xl mb-4">⚠️</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Error loading player statistics</h3>
        <p class="text-gray-600">{{ error }}</p>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="!playersStats || playersStats.length === 0" class="text-center py-20">
        <div class="text-gray-400 text-5xl mb-4">⚽</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No player statistics available</h3>
        <p class="text-gray-600">Check back later for player stats updates</p>
      </div>
      
      <!-- Table -->
      <div v-else class="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
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
                  @click="setSort('games')" 
                  class="sortable-header"
                  :class="{ active: sortBy === 'games' }"
                >
                  <span class="header-content">
                    <span>Матчи</span>
                    <span class="sort-arrow" v-if="sortBy === 'games'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th 
                  @click="setSort('minutes')" 
                  class="sortable-header"
                  :class="{ active: sortBy === 'minutes' }"
                >
                  <span class="header-content">
                    <span>Минуты</span>
                    <span class="sort-arrow" v-if="sortBy === 'minutes'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th 
                  @click="setSort('goals')" 
                  class="sortable-header"
                  :class="{ active: sortBy === 'goals' }"
                >
                  <span class="header-content">
                    <span>Голы</span>
                    <span class="sort-arrow" v-if="sortBy === 'goals'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th 
                  @click="setSort('assists')" 
                  class="sortable-header"
                  :class="{ active: sortBy === 'assists' }"
                >
                  <span class="header-content">
                    <span>Ассисты</span>
                    <span class="sort-arrow" v-if="sortBy === 'assists'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th 
                  @click="setSort('shots')" 
                  class="sortable-header"
                  :class="{ active: sortBy === 'shots' }"
                >
                  <span class="header-content">
                    <span>Удары</span>
                    <span class="sort-arrow" v-if="sortBy === 'shots'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('shots_on_target')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'shots_on_target' }"
                >
                  <span class="header-content">
                    <span>Удары в ств.</span>
                    <span class="sort-arrow" v-if="sortBy === 'shots_on_target'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th 
                  @click="setSort('xg')" 
                  class="sortable-header"
                  :class="{ active: sortBy === 'xg' }"
                >
                  <span class="header-content">
                    <span>xG</span>
                    <span class="sort-arrow" v-if="sortBy === 'xg'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th 
                  @click="setSort('xa')" 
                  class="sortable-header"
                  :class="{ active: sortBy === 'xa' }"
                >
                  <span class="header-content">
                    <span>xA</span>
                    <span class="sort-arrow" v-if="sortBy === 'xa'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('xg_xa')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'xg_xa' }"
                >
                  <span class="header-content">
                    <span>xG+xA</span>
                    <span class="sort-arrow" v-if="sortBy === 'xg_xa'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('xg_np')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'xg_np' }"
                >
                  <span class="header-content">
                    <span>xGnp</span>
                    <span class="sort-arrow" v-if="sortBy === 'xg_np'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('xg_np_xa')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'xg_np_xa' }"
                >
                  <span class="header-content">
                    <span>xGnp+xA</span>
                    <span class="sort-arrow" v-if="sortBy === 'xg_np_xa'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('passes_into_penalty_area')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'passes_into_penalty_area' }"
                >
                  <span class="header-content">
                    <span>ПерПен</span>
                    <span class="sort-arrow" v-if="sortBy === 'passes_into_penalty_area'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('crosses_into_penalty_area')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'crosses_into_penalty_area' }"
                >
                  <span class="header-content">
                    <span>КросыПен</span>
                    <span class="sort-arrow" v-if="sortBy === 'crosses_into_penalty_area'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('touches_in_attacking_third')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'touches_in_attacking_third' }"
                >
                  <span class="header-content">
                    <span>КасТреть</span>
                    <span class="sort-arrow" v-if="sortBy === 'touches_in_attacking_third'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('touches_in_attacking_penalty_area')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'touches_in_attacking_penalty_area' }"
                >
                  <span class="header-content">
                    <span>КасПен</span>
                    <span class="sort-arrow" v-if="sortBy === 'touches_in_attacking_penalty_area'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('carries_in_attacking_third')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'carries_in_attacking_third' }"
                >
                  <span class="header-content">
                    <span>ПродвТреть</span>
                    <span class="sort-arrow" v-if="sortBy === 'carries_in_attacking_third'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('carries_in_attacking_penalty_area')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'carries_in_attacking_penalty_area' }"
                >
                  <span class="header-content">
                    <span>ПродвПен</span>
                    <span class="sort-arrow" v-if="sortBy === 'carries_in_attacking_penalty_area'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('sca')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'sca' }"
                >
                  <span class="header-content">
                    <span>SCA</span>
                    <span class="sort-arrow" v-if="sortBy === 'sca'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
                <th
                  @click="setSort('gca')"
                  class="sortable-header"
                  :class="{ active: sortBy === 'gca' }"
                >
                  <span class="header-content">
                    <span>GCA</span>
                    <span class="sort-arrow" v-if="sortBy === 'gca'">
                      {{ sortDirection === 'asc' ? '↑' : '↓' }}
                    </span>
                  </span>
                </th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-50">
              <tr v-for="(player, index) in sortedPlayersStats" :key="'player-'+index" class="hover:bg-gray-25 transition-colors">
                <td class="player-name-cell sticky left-0 bg-white z-10">{{ player.name || '-' }}</td>
                <td class="data-cell">{{ player.team_name || '-' }}</td>
                <td class="data-cell">{{ player.role || '-' }}</td>
                <td class="data-cell">{{ player.price ? player.price.toFixed(1) : '-' }}</td>
                <td class="data-cell">{{ player.games || '-' }}</td>
                <td class="data-cell">{{ player.minutes || '-' }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.goals) }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.assists) }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.shots) }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.shots_on_target) }}</td>
                <td class="data-cell stat-cell">{{ player.xg ? player.xg.toFixed(2) : '-' }}</td>
                <td class="data-cell stat-cell">{{ player.xa ? player.xa.toFixed(2) : '-' }}</td>
                <td class="data-cell stat-cell">{{ player.xg_xa ? player.xg_xa.toFixed(2) : '-' }}</td>
                <td class="data-cell stat-cell">{{ player.xg_np ? player.xg_np.toFixed(2) : '-' }}</td>
                <td class="data-cell stat-cell">{{ player.xg_np_xa ? player.xg_np_xa.toFixed(2) : '-' }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.passes_into_penalty_area) }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.crosses_into_penalty_area) }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.touches_in_attacking_third) }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.touches_in_attacking_penalty_area) }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.carries_in_attacking_third) }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.carries_in_attacking_penalty_area) }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.sca) }}</td>
                <td class="data-cell stat-cell">{{ formatIntStat(player.gca) }}</td>
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

.stat-cell {
  font-weight: 600;
  font-family: 'Monaco', 'Menlo', monospace;
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

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-checkbox-input {
  width: 16px;
  height: 16px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  transition: all 0.2s ease;
  accent-color: #3b82f6;
}

.filter-checkbox-input:checked {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.filter-checkbox-input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-checkbox-label {
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  user-select: none;
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

.filter-summary {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.filter-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
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