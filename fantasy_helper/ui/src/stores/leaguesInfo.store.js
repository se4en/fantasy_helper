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
      this.isLoading = true
      try {
        const response = await httpClient.get(
          ENDPOINTS.LEAGUES_INFO
        )
        this.leagues_info = response.data
        console.log("STORE: leagues_info response", response)
      } catch (error) {
        this.error = error.message
        console.log("STORE: error", this.error)
        throw error // Propagate error to components
      } finally {
        this.isLoading = false
      }
    }
  },

  // getters: {
  //   sortedPosts: (state) => [...state.posts].sort((a, b) => b.id - a.id)
  // }
})
