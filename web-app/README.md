# The Genius - AI Sports Assistant

A production-ready React web application that provides AI-powered fantasy sports advice using OpenAI GPT-4.1.

## Features

- 🤖 AI-powered fantasy sports advice
- 💬 Real-time chat interface with Server-Sent Events (SSE)
- 📱 Progressive Web App (PWA) support
- 🎨 Modern, responsive UI with **Tailwind CSS v4** and DaisyUI
- 🌙 Dark/Light theme support
- ⚡ **Ultra-fast builds** with Tailwind's new Oxide engine (100×+ faster HMR)
- 🔄 Automatic error recovery and retry logic
- 📊 Real-time streaming responses

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite
- **Styling**: **Tailwind CSS v4** (CSS-first configuration), DaisyUI
- **State Management**: React Hooks
- **Real-time**: Server-Sent Events (SSE)
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
npm install

# Build for production
npm run build

# Preview production build locally
npm run preview

# Start production server
npm start
```

### Deployment Options

#### Render.com (Recommended)
The app is configured for Render.com deployment with the included `render.yaml`:

```yaml
services:
- type: web
  name: genius-frontend
  buildCommand: npm install && npm run build
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

## Development

```bash
# Start development server with local backend
npm run dev

# Start development server with production backend
npm run dev:prod-backend

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix
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
- **Real-time communication** via SSE for streaming responses

## License

Private - All rights reserved