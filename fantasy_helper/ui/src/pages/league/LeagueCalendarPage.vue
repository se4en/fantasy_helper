<script setup>
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { onMounted, computed, ref, watch } from 'vue'
import { useCalendarStore } from '@/stores/calendar.store'
import Loader from '@/components/Loader.vue'

const route = useRoute()
const calendarStore = useCalendarStore()
const { calendar, isLoading: isCalendarLoading, error } = storeToRefs(calendarStore)
const { showLoader } = useLoaderDelay(isCalendarLoading, 500)

// Track if we've made the initial data fetch attempt
const hasInitiallyLoaded = ref(false)

const calendarType = ref('points')

// Get tour names for headers
const tourCalendarHeaders = computed(() => {
  try {
    if (!calendar.value || !Array.isArray(calendar.value) || calendar.value.length === 0) {
      return []
    }
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
  }[calendarType.value]

  return {
    backgroundColor: color || '#ffffff'
  }
}

watch(
  () => route.params.leagueSlug,
  async (newLeagueSlug) => {
    if (newLeagueSlug) {
      hasInitiallyLoaded.value = false
      calendarType.value = 'points'
      try {
        await calendarStore.fetchCalendar(newLeagueSlug)
      } finally {
        hasInitiallyLoaded.value = true
      }
    }
  },
  { immediate: true }
)

onMounted(async () => {
  try {
    if (!calendar.value?.length && route.params.leagueSlug) {
      await calendarStore.fetchCalendar(route.params.leagueSlug)
    } else if (calendar.value?.length) {
      hasInitiallyLoaded.value = true
    }
  } catch (error) {
    console.error('Failed to load calendar:', error)
    hasInitiallyLoaded.value = true
  }
})
</script>

<template>
  <div class="min-h-screen bg-white">
    <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- Header Section -->
      <!-- <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">League Calendar</h1>
        <p class="text-gray-600">Team performance across tournament rounds</p>
      </div> -->

      <!-- Loading State -->
      <div v-if="showLoader" class="flex justify-center py-20">
        <Loader />
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="text-center py-20">
        <div class="text-red-400 text-5xl mb-4">⚠️</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Error loading calendar</h3>
        <p class="text-gray-600">{{ error }}</p>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="hasInitiallyLoaded && (!calendar || calendar.length === 0)" class="text-center py-20">
        <div class="text-gray-400 text-5xl mb-4">📅</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No calendar data available</h3>
        <p class="text-gray-600">Check back later for calendar updates</p>
      </div>
      
      <!-- Controls and Table -->
      <div v-else class="space-y-6">
        <!-- Filters -->
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <!-- <div class="flex flex-wrap items-center justify-between gap-6">
            <h3 class="text-lg font-semibold text-gray-900">Filters</h3>
          </div> -->
          
          <div class="flex flex-wrap gap-6 mt-0">
            <div class="filter-group">
              <label for="viewSelect" class="filter-label">Способ подсчета</label>
              <select
                id="viewSelect"
                v-model="calendarType"
                class="filter-select min-w-[200px]"
              >
                <option value="points">Набранные очки</option>
                <option value="goals">Забитые и пропущенные голы</option>
                <option value="xg">Созданные и допущенные xG</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Table -->
        <div class="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="bg-gray-50">
                  <th class="team-column">Команда</th>
                  
                  <template v-for="(tourName, index) in tourCalendarHeaders" :key="'cal-header-'+index">
                    <th class="tour-header">
                      {{ tourName || `Tour ${index + 1}` }}
                    </th>
                  </template>
                </tr>
              </thead>

              <tbody class="divide-y divide-gray-50">
                <tr v-for="(row, rowIndex) in calendar" :key="'cal-row-'+rowIndex" class="hover:bg-gray-25 transition-colors">
                  <td class="team-cell">{{ row.team_name }}</td>
                  
                  <template v-for="(_, tourIndex) in maxCalendarTours" :key="`cal-${rowIndex}-${tourIndex}`">
                    <td :style="getCalendarCellStyle(row, tourIndex)" class="calendar-cell">
                      <div class="rival">{{ row.tour_rivals?.[tourIndex] || '' }}</div>
                      <div class="value" v-if="calendarType === 'points'">
                        {{ row.tour_points?.[tourIndex] !== undefined ? row.tour_points[tourIndex] : '' }}
                      </div>
                      <div class="value" v-else-if="calendarType === 'goals'">
                        {{ row.tour_goals?.[tourIndex] !== undefined ? row.tour_goals[tourIndex] : '' }}
                      </div>
                      <div class="value" v-else-if="calendarType === 'xg'">
                        {{ row.tour_xg?.[tourIndex] !== undefined ? row.tour_xg[tourIndex].toFixed(2) : '' }}
                      </div>
                    </td>
                  </template>
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
  min-width: 90px;
}

.team-cell {
  background: white;
  font-weight: 600;
  color: #111827;
  position: sticky;
  left: 0;
  z-index: 1;
  text-align: left;
  border-right: 1px solid #f3f4f6;
}

.calendar-cell {
  position: relative;
  min-width: 90px;
  padding: 8px 6px;
}

.rival {
  font-size: 11px;
  color: #111827;
  margin-bottom: 2px;
  line-height: 1.2;
}

.value {
  font-weight: 600;
  font-size: 12px;
  color: #111827;
  font-family: 'Monaco', 'Menlo', monospace;
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
  
  .tour-header {
    min-width: 80px;
  }
  
  .calendar-cell {
    min-width: 80px;
    padding: 6px 4px;
  }
  
  .rival {
    font-size: 10px;
  }
  
  .value {
    font-size: 11px;
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

/* Responsive adjustments for filters */
@media (max-width: 768px) {
  .filter-group {
    min-width: 100%;
  }
  
  .filter-select {
    min-width: 100%;
  }
}
</style>
