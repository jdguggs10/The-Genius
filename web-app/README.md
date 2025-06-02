# The Genius - AI Sports Assistant

A production-ready React web application that provides AI-powered fantasy sports advice using OpenAI GPT-4.1.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Recent Updates](#recent-updates)
- [Production Deployment](#production-deployment)
- [Configuration](#configuration)
- [Development](#development)
- [Browser Support](#browser-support)
- [PWA Features](#pwa-features)
- [Architecture](#architecture)
- [License](#license)

## Features

- 🤖 AI-powered fantasy sports advice
- 💬 Real-time chat interface with **Server-Sent Events (SSE) streaming**
- 📱 Progressive Web App (PWA) support
- 🎨 Modern, responsive UI with **Tailwind CSS v4** and DaisyUI
- ✨ Smooth animations with **Framer Motion**
- 🔔 Toast notifications for user feedback (e.g., using **react-hot-toast**)
- 📄 Markdown rendering for formatted content display (via **react-markdown**)
- 🌙 Dark/Light theme support
- ⚡ **Ultra-fast builds** with Tailwind's new Oxide engine (100×+ faster HMR)
- 🔄 Automatic error recovery and retry logic
- 📊 **Real-time streaming responses** via SSE

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite
- **Styling**: **Tailwind CSS v4** (CSS-first configuration), DaisyUI
- **State Management**: React Hooks
- **Animation**: Framer Motion
- **Notifications**: React Hot Toast
- **Markdown Rendering**: React Markdown
- **Data Validation**: AJV (for schema validation, if used on frontend)
- **Virtualization**: React Window (for efficient rendering of large lists, if applicable)
- **Real-time Communication**: **Server-Sent Events (SSE)** for streaming responses
- **PWA**: Vite PWA Plugin with Workbox
- **Build**: Vite with compression and optimization

## Recent Updates

### 🚀 Tailwind CSS v4 Migration
This project has been upgraded to Tailwind CSS v4, featuring:
- **3-5× faster full builds** with the new Oxide engine
- **100×+ faster HMR** for lightning-fast development
- **CSS-first configuration** for better maintainability
- **Automatic content discovery** (no `content` array needed)
- **Modern CSS primitives** with Lightning CSS

See [TAILWIND_V4_MIGRATION.md](./TAILWIND_V4_MIGRATION.md) for complete migration details.

## Production Deployment

### Environment Variables

Set the following environment variable for production:

```bash
VITE_BACKEND_URL=https://genius-backend-nhl3.onrender.com
```

### Build Commands

```bash
# Install dependencies
pnpm install

# Build for production
pnpm run build

# Preview production build locally
pnpm run preview

# Preview production build locally on port 3000
pnpm start
```

### Deployment Options

#### Render.com (Recommended)
The app is configured for Render.com deployment with the included `render.yaml`:

```yaml
services:
- type: web
  name: genius-frontend
  buildCommand: pnpm install --frozen-lockfile && pnpm run build
  staticPublishPath: dist
```

#### Other Static Hosts
The built files in the `dist/` directory can be deployed to any static hosting service:
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

### Performance Optimizations

- **Code Splitting**: Vendor and UI libraries are split into separate chunks
- **Compression**: Gzip compression enabled for all assets
- **PWA Caching**: Intelligent caching strategy for fonts and API calls
- **Tree Shaking**: Unused code is automatically removed
- **Minification**: Production builds are minified with esbuild

## Configuration

### Automatic Environment Detection

Your web app is now configured to automatically detect the correct backend URL based on the environment:

#### Development Mode (`pnpm run dev`)
- **Automatically uses**: Vite proxy to `http://localhost:8000`
- **Requirement**: Make sure your backend is running on port 8000
- **No configuration needed**: Just run `pnpm run dev` and it will work with your local backend

#### Production Build (`pnpm run build`)
- **Automatically uses**: `https://genius-backend-nhl3.onrender.com`
- **No configuration needed**: Deploy to Render and it will automatically connect to your production backend

### Optional Overrides

If you need to override the automatic detection, you can use these commands:

#### Testing Against Production Backend Locally
```bash
pnpm run dev:prod-backend
```
This runs development mode but connects to your production backend on Render.

#### Building for Local Backend
```bash
pnpm run build:local
```
This creates a production build that connects to your local backend.

### Environment Variables

You can create a `.env.local` file to override the backend URL:

```bash
# .env.local
VITE_BACKEND_URL=https://your-custom-backend.onrender.com
```

### No More Switching!

With this setup, you should never need to manually switch configurations:

1. **Local Development**: `pnpm run dev` (connects to localhost:8000)
2. **Production Deployment**: `pnpm run build` (connects to Render backend)
3. **Testing Production Backend**: `pnpm run dev:prod-backend` (if needed)

The app automatically detects the environment and chooses the correct backend URL.

### Debugging

Check the browser console when the app loads - you'll see API configuration logs like:
```text
🔧 API Configuration: {
  environment: 'development',
  baseUrl: '/api',
  health_url: '/api/health',
  advice_url: '/api/advice'
}
```

## Development

```bash
# Start development server with local backend
pnpm run dev

# Start development server with production backend
pnpm run dev:prod-backend

# Lint code
pnpm run lint

# Fix linting issues
pnpm run lint:fix
```

### Utility Scripts

```bash
# Builds the project including a specific safelist for Tailwind CSS
pnpm run build:safelist

# Builds the project and previews it using a local backend configuration
pnpm run preview:local-backend

# Generates a JSON file of Tailwind CSS design tokens
pnpm run tailwind:tokens

# Checks the Tailwind CSS output against a safelist without generating a full build
pnpm run tailwind:safelist-check
```

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers with ES2018 support

## PWA Features

- Offline capability for cached content
- Install prompt for mobile/desktop
- Background sync for improved performance
- Automatic updates when new versions are available

## Architecture

The application follows a modern React architecture with:

- **Component-based design** with TypeScript
- **Custom hooks** for state management and side effects
- **Error boundaries** for graceful error handling
- **Responsive design** with mobile-first approach
- **Server-Sent Events (SSE) streaming** for real-time AI responses with robust parsing and buffering

## License

Private - All rights reserved