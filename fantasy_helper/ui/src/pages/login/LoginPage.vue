<script>
export default {
  data() {
    return {
      keycloakButtonText: 'Login with Keycloak'
    };
  },
  methods: {
    generateRandomString(length) {
      const array = new Uint8Array(length);
      window.crypto.getRandomValues(array);
      return Array.from(array, b => b.toString(16).padStart(2, '0')).join('').substr(0, length);
    },
    keycloakLogin() {
      const state = this.generateRandomString(16);
      sessionStorage.setItem('keycloak_state', state);
      
      const keycloakUrl = `${import.meta.env.VITE_KEYCLOAK_URL}/realms/${import.meta.env.VITE_KEYCLOAK_REALM}/protocol/openid-connect/auth`;
      const clientId = import.meta.env.VITE_KEYCLOAK_CLIENT_ID;
      const redirectUri = encodeURIComponent(window.location.origin);
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
        Welcome to MyApp
      </h1>

      <div class="login-container">
        <button @click="keycloakLogin" class="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-md">
          {{ keycloakButtonText }}
        </button>
      </div>

      <p class="text-sm text-gray-600 text-center mt-4">
        Secure authentication options
      </p>
    </div>
  </div>
</template>

<style scoped>
</style>
