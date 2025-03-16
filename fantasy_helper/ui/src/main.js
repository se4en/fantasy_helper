// main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './pages/routes.js'  // Updated import

createApp(App)
  .use(router)
  .mount('#app')
