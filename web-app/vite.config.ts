/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import compression from 'vite-plugin-compression'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const isDevelopment = mode === 'development';
  const isProduction = mode === 'production';
  
  const plugins = [
    react(),
    tailwindcss(),
    compression({
      algorithm: 'gzip',
      ext: '.gz',
    })
  ];

  // TODO: Re-enable PWA plugin for production later
  // if (isProduction) {
  //   const { VitePWA } = await import('vite-plugin-pwa');
  //   plugins.push(VitePWA({ /* config */ }));
  // }
  
  return {
    plugins,
    define: {
      __DEV__: isDevelopment,
      'process.env.NODE_ENV': JSON.stringify(mode)
    },
    server: {
      proxy: isDevelopment ? {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          secure: false
        }
      } : undefined
    },
    build: {
      target: 'es2018',
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: !isProduction,
      minify: isProduction ? 'esbuild' : false,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            ui: ['framer-motion', 'react-hot-toast']
          }
        }
      }
    },
    optimizeDeps: {
      include: ['react', 'react-dom', 'framer-motion']
    }
  }
})