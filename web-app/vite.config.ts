import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import compression from 'vite-plugin-compression'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), compression()],
  server: {
    proxy: {
      // During development, forward API calls to your backend
      '/api': {
        target: 'https://genius-backend.onrender.com',  // Updated backend URL
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
