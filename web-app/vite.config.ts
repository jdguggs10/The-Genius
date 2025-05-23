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
        target: 'https://genius-backend-nhl3.onrender.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),  // Remove /api prefix
        secure: true
      }
    }
  },
  build: {
    target: 'es2018',
    outDir: 'dist'
  }
})