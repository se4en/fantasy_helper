import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'url'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue()
  ],
  // server: {
  //   proxy: {
  //     '/api': {
  //       target: 'http://api:8000',
  //       changeOrigin: true
  //     }
  //   }
  // },
  // define: {
  //   VITE_API_URL: process.env.VITE_API_URL,
  // },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    minify: false, // Disable minification
    terserOptions: {
      compress: {
        drop_console: false // Keep console logs
      }
    }
  }
})
