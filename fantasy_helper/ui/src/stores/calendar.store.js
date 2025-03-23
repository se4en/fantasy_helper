import { defineStore } from 'pinia'
import httpClient from '@/api/httpClient'
import { ENDPOINTS } from '@/api/httpClient'
import { CalendarTableRowSchema } from '@/types/calendar'

export const useCalendarStore = defineStore('calendar', {
  state: () => ({
    calendar: [],
    isLoading: false,
    error: null
  }),

  actions: {
    async fetchCalendar(leagueName) {
      try {
        if (this.isLoading) return
        this.isLoading = true
        this.error = null

        if (!leagueName?.trim()) {
          throw new Error('League name is required')
        }
        
        const response = await httpClient.get(
          ENDPOINTS.CALENDAR,
          {
            params: {
              league_name: leagueName
            }
          }
        )

        const result = CalendarTableRowSchema.array().safeParse(response.data)
        if (!result.success) {
          throw new Error('Invalid data format from API')
        }
        
        this.calendar = result.data
        console.log("this.calendar", this.calendar)
      } catch (error) {
        this.error = error.message
        console.log("fetchCalendar error", this.error)
        throw error 
      } finally {
        this.isLoading = false
      }
    }
  }
})
