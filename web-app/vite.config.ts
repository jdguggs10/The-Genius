/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import compression from 'vite-plugin-compression'
import { VitePWA, type VitePWAOptions } from 'vite-plugin-pwa'

// Define manifest options for PWA
const manifestForPlugin: Partial<VitePWAOptions> = {
  registerType: 'autoUpdate',
  injectRegister: 'auto',
  devOptions: {
    enabled: true, // Enable in development for testing
    type: 'module',
  },
  selfDestroying: false,
  manifest: {
    name: 'The Genius - AI Sports Assistant',
    short_name: 'TheGenius',
    description: 'AI-Powered Fantasy Sports Advice',
    theme_color: '#1e40af',
    background_color: '#ffffff',
    display: 'standalone',
    scope: '/',
    start_url: '/',
    icons: [
      {
        src: 'icons/pwa-192x192.png',
        sizes: '192x192',
        type: 'image/png',
        purpose: 'any'
      },
      {
        src: 'icons/pwa-512x512.png',
        sizes: '512x512',
        type: 'image/png',
        purpose: 'any'
      },
      {
        src: 'apple-touch-icon.png',
        sizes: '180x180',
        type: 'image/png',
        purpose: 'any'
      },
      {
        src: 'icons/pwa-maskable-192x192.png',
        sizes: '192x192',
        type: 'image/png',
        purpose: 'maskable',
      }
    ],
  },
  workbox: {
    cleanupOutdatedCaches: true,
    globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/fonts\.(?:googleapis|gstatic)\.com\/.*/i,
        handler: 'CacheFirst',
        options: {
          cacheName: 'google-fonts-cache',
          expiration: {
            maxEntries: 10,
            maxAgeSeconds: 60 * 60 * 24 * 365, // 365 days
          },
          cacheableResponse: {
            statuses: [0, 200],
          },
        },
      },
      {
        urlPattern: /^https:\/\/genius-backend.*\.onrender\.com\/.*/i,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          networkTimeoutSeconds: 10,
          expiration: {
            maxEntries: 50,
            maxAgeSeconds: 60 * 60 * 24, // 1 day
          },
          cacheableResponse: {
            statuses: [0, 200],
          },
        },
      },
      {
        urlPattern: /^http:\/\/localhost:8000\/.*/i,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'local-api-cache',
          networkTimeoutSeconds: 5,
          expiration: {
            maxEntries: 20,
            maxAgeSeconds: 60 * 60, // 1 hour for local dev
          },
          cacheableResponse: {
            statuses: [0, 200],
          },
        },
      },
    ],
  },
};

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
    }),
    // Add PWA plugin for both development and production
    VitePWA(manifestForPlugin)
  ];
  
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