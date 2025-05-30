<script setup>
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { onMounted, computed, ref } from 'vue'
import { useCalendarStore } from '@/stores/calendar.store'
import Loader from '@/components/Loader.vue'

const route = useRoute()
const calendarStore = useCalendarStore()
const { calendar, isLoading: isCalendarLoading, error } = storeToRefs(calendarStore)
const { showLoader } = useLoaderDelay(isCalendarLoading, 500)

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

onMounted(async () => {
  try {
    if (!calendar.value?.length && route.params.leagueSlug) {
      await calendarStore.fetchCalendar(route.params.leagueSlug)
    }
  } catch (error) {
    console.error('Failed to load calendar:', error)
  }
})
</script>

<template>
  <div class="calendar-page">
    <!-- <h2 class="section-title">League Calendar</h2> -->

    <Loader v-if="showLoader" />
    
    <div v-else-if="error" class="error-message">
      <p>Error loading calendar: {{ error }}</p>
    </div>
    
    <div v-else-if="!calendar || calendar.length === 0" class="empty-state">
      <p>No calendar data available for this league.</p>
    </div>
    
    <div v-else class="calendar-container">
      <div class="view-options">
        <div class="form-group">
          <label for="viewSelect">Display Mode:</label>
          <select id="viewSelect" v-model="calendarType" class="form-select">
            <option value="points">Points</option>
            <option value="goals">Goals</option>
            <option value="xg">Expected Goals (xG)</option>
          </select>
        </div>
      </div>

      <div class="calendar-table">
        <table>
          <thead>
            <tr>
              <th class="team-column">Team</th>
              
              <template v-for="(tourName, index) in tourCalendarHeaders" :key="'cal-header-'+index">
                <th>
                  {{ tourName || `Tour ${index + 1}` }}
                </th>
              </template>
            </tr>
          </thead>

          <tbody>
            <tr v-for="(row, rowIndex) in calendar" :key="'cal-row-'+rowIndex">
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
</template>

<style scoped>
.calendar-page {
  padding: 1rem;
}

.section-title {
  text-align: center;
  margin: 1rem 0 2rem;
  color: #2c3e50;
}

.view-options {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
}

.form-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-select {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: white;
}

.calendar-table {
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

.team-cell {
  background: white !important;
  font-weight: 500;
  position: sticky;
  left: 0;
  z-index: 1;
}

.calendar-cell {
  position: relative;
  padding: 0.5rem;
  min-width: 80px;
}

.rival {
  /* font-size: 0.8rem; */
  margin-bottom: 0.25rem;
}

.value {
  font-weight: bold;
  font-size: 1.1rem;
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
