/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import compression from 'vite-plugin-compression'
import { VitePWA, VitePWAOptions } from 'vite-plugin-pwa'

// Define manifest options (can be partial, plugin completes it)
const manifestForPlugin: Partial<VitePWAOptions> = {
  registerType: 'autoUpdate', // Prompt for update or auto update
  injectRegister: 'auto', // or 'script' or null
  devOptions: {
    enabled: true, // Enable PWA in development for testing
    type: 'module',
  },
  manifest: {
    name: 'The Genius - AI Sports Assistant',
    short_name: 'TheGenius',
    description: 'AI-Powered Fantasy Sports Advice',
    theme_color: '#1e40af', // Example: blue-700 Tailwind
    background_color: '#ffffff', // Light background for splash screen
    display: 'standalone',
    scope: '/',
    start_url: '/',
    icons: [
      {
        src: 'icons/pwa-192x192.png', // Path in public folder
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: 'icons/pwa-512x512.png', // Path in public folder
        sizes: '512x512',
        type: 'image/png',
      },
      {
        src: 'icons/apple-touch-icon.png', // Path in public folder
        sizes: '180x180',
        type: 'image/png',
        purpose: 'apple touch icon',
      },
      {
        src: 'icons/pwa-maskable-192x192.png', // Maskable icon
        sizes: '192x192',
        type: 'image/png',
        purpose: 'maskable',
      }
    ],
  },
  workbox: {
    globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'], // Cache these app shell assets
    runtimeCaching: [
      {
        // Match any request that starts with https://fonts.googleapis.com/
        // or https://fonts.gstatic.com/
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
        // Example for API calls - adjust urlPattern as needed
        // This app primarily uses WebSockets for real-time chat, which aren't cached this way.
        // This rule would apply to any other HTTP API calls (e.g., fetching initial model name).
        // It's set to NetworkFirst, so it tries network, then cache.
        // It's a generic example; for POST requests or specific GETs, more tailored strategies might be needed.
        urlPattern: ({ url, request }) => {
          const isBackendApi = request.destination === 'fetch' && url.origin !== self.location.origin;
          // Customize further if your backend URL is known and stable, e.g., by checking url.hostname
          // const backendHostname = import.meta.env.VITE_BACKEND_HOSTNAME || "your-backend-host.com";
          // return isBackendApi && url.hostname.includes(backendHostname);
          return isBackendApi; // Catches any cross-origin fetch requests
        },
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          networkTimeoutSeconds: 10, // Timeout for network request
          expiration: {
            maxEntries: 20,
            maxAgeSeconds: 60 * 60 * 24, // 1 day
          },
          cacheableResponse: {
            statuses: [0, 200], // Cache opaque and successful responses
          },
        },
      },
    ],
  },
};

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), compression(), VitePWA(manifestForPlugin)],
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
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
  }
})