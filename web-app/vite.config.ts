import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import compression from 'vite-plugin-compression'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), compression()],
  server: {
    proxy: {
      '/api': 'https://genius-backend.onrender.com'
    }
  },
  build: {
    target: 'es2018',
    outDir: 'dist'
  }
})
