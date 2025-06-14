<script>
import { useAuthStore } from '@/stores/auth'

export default {
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      keycloakButtonText: 'Login with Keycloak',
      errorMessage: null
    };
  },
  mounted() {
    // Check for error in URL params
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.get('error') === 'auth_failed') {
      this.errorMessage = 'Authentication failed. Please try again.'
    }
  },
  methods: {
    generateRandomString(length) {
      const array = new Uint8Array(length);
      window.crypto.getRandomValues(array);
      return Array.from(array, b => b.toString(16).padStart(2, '0')).join('').substr(0, length);
    },
    keycloakLogin() {
      // Store current route for redirect after login
      const intendedRoute = this.$route.query.redirect || '/'
      sessionStorage.setItem('redirect_after_login', intendedRoute)

      const state = this.generateRandomString(16);
      sessionStorage.setItem('keycloak_state', state);
      
      const keycloakUrl = `${import.meta.env.VITE_KEYCLOAK_URL}/realms/${import.meta.env.VITE_KEYCLOAK_REALM}/protocol/openid-connect/auth`;
      const clientId = import.meta.env.VITE_KEYCLOAK_CLIENT_ID;
      const redirectUri = encodeURIComponent(`${window.location.origin}/login/callback`);
      const scope = 'openid';

      const loginUrl = `${keycloakUrl}?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&state=${state}`;
      window.location.href = loginUrl;
    }
  }
};
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="bg-white p-8 rounded-lg shadow-md w-96">
      <h1 class="text-2xl font-bold text-gray-800 mb-6 text-center">
        Welcome to Fantasy Helper
      </h1>

      <!-- Error message -->
      <div v-if="errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {{ errorMessage }}
      </div>

      <div class="login-container">
        <button 
          @click="keycloakLogin" 
          :disabled="authStore.isLoading"
          class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
        >
          <span v-if="authStore.isLoading">Logging in...</span>
          <span v-else>{{ keycloakButtonText }}</span>
        </button>
      </div>

      <p class="text-sm text-gray-600 text-center mt-6">
        Secure authentication powered by Keycloak
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  margin-bottom: 1rem;
}
</style>
