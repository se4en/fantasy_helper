<template>                                                                                                                                                   
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">                                                                                     
    <div class="bg-white p-8 rounded-lg shadow-md w-96 text-center">                                                                                         
      <div v-if="loading">                                                                                                                                   
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>                                                      
        <p class="text-gray-600">Processing login...</p>                                                                                                     
      </div>                                                                                                                                                 
      <div v-else-if="error" class="text-red-600">                                                                                                           
        <p>Login failed: {{ error }}</p>                                                                                                                     
        <button @click="goToLogin" class="mt-4 bg-blue-600 text-white px-4 py-2 rounded">                                                                    
          Try Again                                                                                                                                          
        </button>                                                                                                                                            
      </div>                                                                                                                                                 
    </div>                                                                                                                                                   
  </div>                                                                                                                                                     
</template>                                                                                                                                                  
                                                                                                                                                             
<script>
import { useAuthStore } from '@/stores/auth'

export default {                                                                                                                                             
  name: 'LoginCallback',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {                                                                                                                                                   
    return {                                                                                                                                                 
      loading: true,                                                                                                                                         
      error: null                                                                                                                                            
    };                                                                                                                                                       
  },                                                                                                                                                         
  async mounted() {                                                                                                                                          
    await this.handleCallback();                                                                                                                             
  },                                                                                                                                                         
  methods: {                                                                                                                                                 
    async handleCallback() {                                                                                                                                 
      try {                                                                                                                                                  
        const urlParams = new URLSearchParams(window.location.search);                                                                                       
        const code = urlParams.get('code');                                                                                                                  
        const error = urlParams.get('error');                                                                                                                
        const state = urlParams.get('state');  
        console.warn('code', code);
        console.warn('error', error);
        console.warn('state', state);
                                                                                                                                                             
        if (error) {                                                                                                                                         
          this.error = `Keycloak error: ${error}`;                                                                                                           
          this.loading = false;                                                                                                                              
          return;                                                                                                                                            
        }                                                                                                                                                    
                                                                                                                                                             
        if (!code) {                                                                                                                                         
          this.error = 'No authorization code received';                                                                                                     
          this.loading = false;                                                                                                                              
          return;                                                                                                                                            
        }                                                                                                                                                    
                                                                                                                                                             
        // Verify state parameter                                                                                                                            
        const savedState = sessionStorage.getItem('keycloak_state');                                                                                         
        if (state !== savedState) {                                                                                                                          
          this.error = 'Invalid state parameter';                                                                                                            
          this.loading = false;                                                                                                                              
          return;                                                                                                                                            
        }                                                                                                                                                    
        
        console.warn('backend url', `${import.meta.env.VITE_API_URL}/login/callback/?code=${code}`);
        // Call your backend's login callback endpoint                                                                                                       
        const response = await fetch(`${import.meta.env.VITE_API_URL}/login/callback/?code=${code}`, {                                                       
          method: 'GET',                                                                                                                                     
          credentials: 'include', // Important for cookies                                                                                                   
        });
        console.warn('response', response);
                                                                                                                                                             
        if (response.ok) {                                                                                                                                   
          // Clear the state from session storage
          console.warn('before keycloak_state');                                                                                                      
          sessionStorage.removeItem('keycloak_state');
          console.warn('after keycloak_state');

          // Wait a moment for cookies to be set
          await new Promise(resolve => setTimeout(resolve, 500))

          // Fetch user info to update the auth store
          await this.authStore.fetchUser()

          if (this.authStore.isAuthenticated) {
            // Get redirect URL from session storage or default to home
            const redirectTo = sessionStorage.getItem('redirect_after_login') || '/'
            sessionStorage.removeItem('redirect_after_login')
            
            // Redirect to intended page
            this.$router.push(redirectTo)
          } else {
            this.error = 'Failed to authenticate user'
            this.loading = false
          }                                                                                                                                                             
        } else {                                                                                                                                             
          this.error = 'Login failed on server';                                                                                                             
          this.loading = false;                                                                                                                              
        }                                                                                                                                                    
      } catch (err) {                                                                                                                                        
        console.error('Login callback error:', err);                                                                                                         
        this.error = 'An unexpected error occurred';                                                                                                         
        this.loading = false;                                                                                                                                
      }                                                                                                                                                      
    },                                                                                                                                                       
    goToLogin() {                                                                                                                                            
      this.$router.push('/login');                                                                                                                           
    }                                                                                                                                                        
  }                                                                                                                                                          
};                                                                                                                                                           
</script>
