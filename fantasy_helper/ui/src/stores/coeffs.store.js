import { defineStore } from 'pinia'
import httpClient from '@/api/httpClient'
import { ENDPOINTS } from '@/api/httpClient'
import { CoeffTableRowSchema } from '@/types/coeff'

export const useCoeffStore = defineStore('coeffs', {
  state: () => ({
    coeffs: null,
    isLoading: false,
    error: null
  }),

  actions: {
    async fetchCoeffs(leagueName) {
      try {
        if (this.isLoading) return
        this.isLoading = true
        this.error = null

        if (!leagueName?.trim()) {
          throw new Error('League name is required')
        }
        
        const response = await httpClient.get(
          ENDPOINTS.COEFFS,
          {
            params: {
              league_name: leagueName
            }
          }
        )

        const result = CoeffTableRowSchema.array().safeParse(response.data)
        if (!result.success) {
          // throw new Error('Invalid data format from API')
          const errorDetails = {                                                                                                                                              
            message: 'Invalid data format from API',                                                                                                                          
            validationErrors: result.error.issues,  // Zod validation errors                                                                                                  
            receivedData: response.data,           // The actual data that failed                                                                                             
            endpoint: ENDPOINTS.COEFFS,                                                                                                                                       
            params: { league_name: leagueName }                                                                                                                               
          };                                                                                                                                                                  
          throw new Error(JSON.stringify(errorDetails));
        }
        
        this.coeffs = result.data
      } catch (error) {
        this.error = error.message
        console.log("fetchCoeffs error", this.error)
        throw error 
      } finally {
        this.isLoading = false
      }
    }
  },

  // getters: {
  //   activeCoeffs(state) {
  //     return state.coeffs.filter(coeff => 
  //       (coeff.tour_attack_coeffs?.length || coeff.tour_deffence_coeffs?.length)
  //     )
  //   }
  // }
})
