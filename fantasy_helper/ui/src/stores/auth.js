import { defineStore } from 'pinia'

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
        const response = await fetch('/api/me', { 
          credentials: 'include',
          headers: { 'Accept': 'application/json' }
        })
        
        if (response.ok) {
          this.user = await response.json()
        } else if (response.status === 401) {
          this.user = null
        } else {
          console.error('Failed to fetch user:', response.status, response.statusText)
          this.user = null
        }
      } catch (error) {
        console.error('Failed to fetch user:', error)
        this.user = null
      } finally {
        this.isLoading = false
        this.isInitialized = true
      }
    },

    async logout() {
      try {
        const response = await fetch('/api/logout', { 
          credentials: 'include',
          method: 'GET'
        })
        
        if (response.ok) {
          this.user = null
          window.location.href = '/login'
        } else {
          console.error('Logout failed:', response.status, response.statusText)
        }
      } catch (error) {
        console.error('Logout failed:', error)
        // Clear user anyway and redirect
        this.user = null
        window.location.href = '/login'
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
