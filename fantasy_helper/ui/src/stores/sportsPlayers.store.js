import { defineStore } from 'pinia'
import httpClient from '@/api/httpClient'
import { ENDPOINTS } from '@/api/httpClient'
import { SportsPlayerDiffSchema } from '@/types/sportsPlayers'

export const useSportsPlayersStore = defineStore('sportsPlayers', {
  state: () => ({
    sportsPlayers: null,
    isLoading: false,
    error: null
  }),

  actions: {
    async fetchSportsPlayers(leagueName) {
      try {
        if (this.isLoading) return
        this.isLoading = true
        this.error = null

        if (!leagueName?.trim()) {
          throw new Error('League name is required')
        }
        
        const response = await httpClient.get(
          ENDPOINTS.SPORTS_PLAYERS,
          {
            params: {
              league_name: leagueName
            }
          }
        )

        const result = SportsPlayerDiffSchema.array().safeParse(response.data)
        if (!result.success) {
          const errorDetails = {                                                                                                                                              
            message: 'Invalid data format from API',                                                                                                                          
            validationErrors: result.error.issues,  // Zod validation errors                                                                                                  
            receivedData: response.data,           // The actual data that failed                                                                                             
            endpoint: ENDPOINTS.SPORTS_PLAYERS,                                                                                                                                       
            params: { league_name: leagueName }                                                                                                                               
          };                                                                                                                                                                  
          throw new Error(JSON.stringify(errorDetails));
        }
        
        this.sportsPlayers = result.data
      } catch (error) {
        this.error = error.message
        console.log("fetchSportsPlayers error", this.error)
        throw error 
      } finally {
        this.isLoading = false
      }
    }
  }
})