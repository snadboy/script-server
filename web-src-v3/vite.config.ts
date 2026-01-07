import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@shared': resolve(__dirname, './src/shared'),
      '@main': resolve(__dirname, './src/apps/main'),
      '@admin': resolve(__dirname, './src/apps/admin'),
      '@login': resolve(__dirname, './src/apps/login'),
    },
  },
  build: {
    outDir: '../web-v3',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        admin: resolve(__dirname, 'admin.html'),
        login: resolve(__dirname, 'login.html'),
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/scripts': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        ws: true,
      },
      '/executions': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        ws: true,
      },
      '/conf': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '^/login$': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/logout': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/history': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/schedule': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/schedules': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/result_files': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
