// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './pages/routes.js'  // Updated import

createApp(App)
  .use(router)
  .use(createPinia())
  .mount('#app');
