import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import compression from 'vite-plugin-compression'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), compression()],
  server: {
    proxy: {
      // During development, forward API calls to your backend
      // Replace this URL with your actual Render backend URL once deployed
      '/api': {
        target: 'https://the-genius-backend.onrender.com',  // Your backend URL
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')  // Remove /api prefix
      }
    }
  },
  build: {
    target: 'es2018',
    outDir: 'dist'
  }
})
