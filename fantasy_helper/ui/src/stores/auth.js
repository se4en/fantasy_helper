import { defineStore } from 'pinia'
import httpClient from '@/api/httpClient'
import { ENDPOINTS } from '@/api/httpClient'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isLoading: false,
    isInitialized: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    userName: (state) => {
      if (!state.user) return null
      return state.user.name || state.user.preferred_username || state.user.email
    },
    userEmail: (state) => state.user?.email,
    userId: (state) => state.user?.id,
    userGivenName: (state) => state.user?.given_name,
    userFamilyName: (state) => state.user?.family_name,
    userPreferredUsername: (state) => state.user?.preferred_username
  },

  actions: {
    async fetchUser() {
      if (this.isLoading) return
      this.isLoading = true
      try {
        const response = await httpClient.get(ENDPOINTS.ME)
        this.user = response.data
      } catch (error) {
        if (error.response?.status === 401) {
          this.user = null
        } else {
          console.error('Failed to fetch user:', error)
          this.user = null
        }
      } finally {
        this.isLoading = false
        this.isInitialized = true
      }
    },

    async logout() {
      try {
        // Get the logout URL from the backend
        const response = await httpClient.get(ENDPOINTS.LOGOUT)
        
        if (response.status === 200 && response.data?.logout_url) {
          // Clear user state immediately
          this.clearUser()
          
          // Redirect to Keycloak logout URL
          window.location.href = response.data.logout_url
        } else {
          console.error('Invalid logout response:', response)
          // Fallback: just clear user state and redirect to home
          this.clearUser()
          window.location.href = '/'
        }
      } catch (error) {
        console.error('Logout error:', error)
        // Fallback: clear user state and redirect to home
        this.clearUser()
        window.location.href = '/'
      }
    },

    setUser(userData) {
      this.user = userData
    },

    clearUser() {
      this.user = null
    },

    async checkAuthStatus() {
      if (!this.isInitialized) {
        await this.fetchUser()
      }
      return this.isAuthenticated
    }
  }
})
