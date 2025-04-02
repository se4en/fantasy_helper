import { defineStore } from 'pinia'
import httpClient from '@/api/httpClient'
import { ENDPOINTS } from '@/api/httpClient'


export const useLeaguesInfoStore = defineStore('leaguesInfo', {
  state: () => ({
    leaguesInfo: null,
    isLoading: false,
    error: null
  }),
  actions: {
    async fetchLeaguesInfo() {
      try {
        if (this.isLoading) return
        this.isLoading = true

        const response = await httpClient.get(
          ENDPOINTS.LEAGUES_INFO
        )
        this.leaguesInfo = response.data
      } catch (error) {
        this.error = error.message
        throw error 
      } finally {
        this.isLoading = false
      }
    }
  }
})
