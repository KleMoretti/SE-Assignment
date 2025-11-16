import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',  // 监听所有网络接口
    port: 3000,
    strictPort: true,  // 如果端口被占用则报错
    open: false,  // 不自动打开浏览器
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        ws: true  // 支持WebSocket
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
