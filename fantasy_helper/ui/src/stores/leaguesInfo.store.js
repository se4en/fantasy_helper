import { defineStore } from 'pinia'
import httpClient from '@/api/httpClient'
import { ENDPOINTS } from '@/api/httpClient'


export const useLeaguesInfoStore = defineStore('leaguesInfo', {
  state: () => ({
    leagues_info: [],
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
        this.leagues_info = response.data
        console.log("this.leagues_info", this.leagues_info)
      } catch (error) {
        this.error = error.message
        console.log("fetchLeaguesInfo error", this.error)
        throw error 
      } finally {
        this.isLoading = false
      }
    }
  }
})
