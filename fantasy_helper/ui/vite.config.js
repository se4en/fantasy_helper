import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'url'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'

const certKeyPath = './certs/dev.fantasy-helper.ru-key.pem'                                                                                                                                                                                                                                                                  
const certPath = './certs/dev.fantasy-helper.ru.pem'                                                                                                                                                                                                                                                                         
const certsExist = fs.existsSync(certKeyPath) && fs.existsSync(certPath)

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
    ...(certsExist && {                                                                                                                                                                                                                                                                                                      
      https: {                                                                                                                                                                                                                                                                                                               
        key: fs.readFileSync(certKeyPath),                                                                                                                                                                                                                                                                                   
        cert: fs.readFileSync(certPath)                                                                                                                                                                                                                                                                                      
      }                                                                                                                                                                                                                                                                                                                      
    }),
    // https: {
    //   key: fs.readFileSync('./certs/dev.fantasy-helper.ru-key.pem'),
    //   cert: fs.readFileSync('./certs/dev.fantasy-helper.ru.pem')
    // },
    host: '0.0.0.0',
    port: 4173,
    strictPort: true,
    // hmr: {
    //   protocol: 'wss',
    //   host: 'dev.fantasy-helper.ru',
    //   clientPort: 443 // Required for Cloudflare Tunnel
    // }
    // Only configure HMR for HTTPS if certificates exist                                                                                                                                                                                                                                                                    
    ...(certsExist && {                                                                                                                                                                                                                                                                                                      
      hmr: {                                                                                                                                                                                                                                                                                                                 
        protocol: 'wss',                                                                                                                                                                                                                                                                                                     
        host: 'dev.fantasy-helper.ru',                                                                                                                                                                                                                                                                                       
        clientPort: 443 // Required for Cloudflare Tunnel                                                                                                                                                                                                                                                                    
      }                                                                                                                                                                                                                                                                                                                      
    })
  },
  proxy: {
    '/': {
      // target: 'https://dev.fantasy-helper.ru',
      target: 'https://fantasy-helper.ru',
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
})
