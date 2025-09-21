import { defineStore } from 'pinia'
import httpClient from '@/api/httpClient'
import { ENDPOINTS } from '@/api/httpClient'
import { PlayersTableRowSchema } from '@/types/playerStats'

export const usePlayersStatsStore = defineStore('playersStats', {
  state: () => ({
    playersStats: null,
    isLoading: false,
    error: null
  }),

  actions: {
    async fetchPlayersStats(leagueName, gamesCount = null, normalizeMinutes = false, normalizeMatches = false, minMinutes = null) {
      try {
        if (this.isLoading) return
        this.isLoading = true
        this.error = null

        if (!leagueName?.trim()) {
          throw new Error('League name is required')
        }
        
        const params = {
          league_name: leagueName,
          normalize_minutes: normalizeMinutes,
          normalize_matches: normalizeMatches
        }

        if (gamesCount !== null && gamesCount !== undefined && gamesCount !== '') {
          params.games_count = gamesCount
        }

        if (minMinutes !== null && minMinutes !== undefined && minMinutes !== '') {
          params.min_minutes = minMinutes
        }

        const response = await httpClient.get(
          ENDPOINTS.PLAYERS_STATS_INFO,
          { params }
        )

        const result = PlayersTableRowSchema.array().safeParse(response.data)
        if (!result.success) {
          const errorDetails = {                                                                                                                                              
            message: 'Invalid data format from API',                                                                                                                          
            validationErrors: result.error.issues,  // Zod validation errors                                                                                                  
            receivedData: response.data,           // The actual data that failed                                                                                             
            endpoint: ENDPOINTS.PLAYERS_STATS_INFO,                                                                                                                                       
            params: params                                                                                                                               
          };                                                                                                                                                                  
          throw new Error(JSON.stringify(errorDetails));
        }
        
        this.playersStats = result.data
      } catch (error) {
        this.error = error.message
        console.log("fetchPlayersStats error", this.error)
        throw error 
      } finally {
        this.isLoading = false
      }
    }
  }
})