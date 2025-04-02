<script>
import { useRouter } from 'vue-router'
import httpClient from '@/api/httpClient'
import { ENDPOINTS } from '@/api/httpClient'

const router = useRouter();


export default {
  mounted() {
    this.checkTelegramCallback();
    this.loadTelegramWidget();
  },
  data() {
    return {
      botUsername: import.meta.env.VITE_TELEGRAM_BOT_USERNAME,
      isProcessingCallback: false
    };
  },
  methods: {
    checkTelegramCallback() {
      // Check for Telegram auth parameters in URL
      const urlParams = new URLSearchParams(window.location.search);
      
      console.warn("telegram ury params", urlParams);

      if (urlParams.has('id') && urlParams.has('hash')) {
        this.isProcessingCallback = true;
        
        const userData = {
          id: urlParams.get('id'),
          first_name: urlParams.get('first_name'),
          last_name: urlParams.get('last_name'),
          username: urlParams.get('username'),
          photo_url: urlParams.get('photo_url'),
          auth_date: urlParams.get('auth_date'),
          hash: urlParams.get('hash')
          // initData: window.Telegram.WebApp.initData
        };

        this.handleTelegramAuth(userData);
        
        // Clean URL after processing
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    },
    async loadTelegramWidget() {
      if (this.isProcessingCallback) return;

      const script = document.createElement('script');
      script.async = true;
      script.src = `https://telegram.org/js/telegram-widget.js?22`;
      script.dataset.telegramLogin = this.botUsername;
      script.dataset.size = 'large';
      script.dataset.radius = '14';
      script.dataset.requestAccess = 'write';
      script.dataset.authUrl = window.location.href;
      // script.dataset.authUrl = `${window.location.origin}/auth/callback`; // Important for reloads
      
      // Use proper Telegram callback name
      // window.onTelegramAuth = (user) => this.handleTelegramAuth(user);
      
      script.onload = () => {
        window.onTelegramAuth = (user) => {
          this.handleTelegramAuth(user);
          // Force update to clear loading state
          this.$forceUpdate();
        };
      };
      
      // script.onload = () => console.log('Telegram widget loaded with user', user);
      // script.onerror = (e) => console.error('Widget load error:', e);
      
      this.$refs.telegramWidget.appendChild(script);
    },
    async handleTelegramAuth(user) {
      try {
        console.warn('handleTelegramAuth user:', user);

        const response = await httpClient.post(
          ENDPOINTS.TELEGRAM_AUTH, 
          user
        );
        
        // Store authentication data
        // localStorage.setItem('access_token', response.data.access_token);
        // localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Redirect to protected route
        this.$router.push({ name: 'Home' });
      } catch (error) {
        console.error('Authentication failed:', error);
        // alert('Login failed. Please try again.');
        this.isProcessingCallback = false;
        this.loadTelegramWidget(); // Reinitialize widget
      }
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
      
      <!-- <div class="telegram-login-wrapper flex justify-center mb-6">
        <script
          async
          :src="`https://telegram.org/js/telegram-widget.js?${widgetVersion}`"
          :data-telegram-login="botUsername"
          data-size="large"
          data-radius="14"
          data-request-access="write"
          @telegram-auth="handleTelegramAuth"
        ></script>
      </div> -->

      <!-- <div class="login-page">
        <div ref="telegramWidget"></div>
      </div> -->
      <div class="login-container">
        <div v-if="!isProcessingCallback" ref="telegramWidget"></div>
        <div v-else class="loading-message">
          Processing Telegram login...
        </div>
      </div>

      <p class="text-sm text-gray-600 text-center">
        Secure authentication powered by Telegram
      </p>
      
    </div>
  </div>
</template>

<style scoped>
.telegram-login-wrapper {
  min-height: 48px;
  margin: 1.5rem 0;
}

:deep(.telegram-login-button) {
  background-color: #0088cc !important;
  transition: transform 0.2s ease;
}

:deep(.telegram-login-button):hover {
  transform: scale(1.05);
}
</style>
