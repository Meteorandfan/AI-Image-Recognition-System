import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite 配置：通过代理将 /api 转发到后端
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
