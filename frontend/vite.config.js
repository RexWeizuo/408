import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 4080,
    proxy: {
      '/api': {
        target: 'http://localhost:4081',
        changeOrigin: true
      }
    }
  }
})
