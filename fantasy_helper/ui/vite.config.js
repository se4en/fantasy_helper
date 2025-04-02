import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'url'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag === 'telegram-widget'
        }
      }
    })
  ],
  server: {
    https: {
      key: fs.readFileSync('./certs/dev.fantasy-helper.ru-key.pem'),
      cert: fs.readFileSync('./certs/dev.fantasy-helper.ru.pem')
    },
    host: '0.0.0.0',
    port: 4173,
    strictPort: true,
    hmr: {
      protocol: 'wss',
      host: 'dev.fantasy-helper.ru',
      clientPort: 443 // Required for Cloudflare Tunnel
    }
  },
  proxy: {
    '/': {
      target: 'https://dev.fantasy-helper.ru',
      ws: true,
      changeOrigin: true
    }
  },
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
    },
    sourcemap: true,
  }
  // base: './',
})
