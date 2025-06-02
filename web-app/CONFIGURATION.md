# Configuration Guide

## Automatic Environment Detection

Your web app is now configured to automatically detect the correct backend URL based on the environment:

### Development Mode (`npm run dev`)
- **Automatically uses**: Vite proxy to `http://localhost:8000`
- **Requirement**: Make sure your backend is running on port 8000
- **No configuration needed**: Just run `npm run dev` and it will work with your local backend

### Production Build (`npm run build`)
- **Automatically uses**: `https://genius-backend-nhl3.onrender.com`
- **No configuration needed**: Deploy to Render and it will automatically connect to your production backend

## Optional Overrides

If you need to override the automatic detection, you can use these commands:

### Testing Against Production Backend Locally
```bash
npm run dev:prod-backend
```
This runs development mode but connects to your production backend on Render.

### Building for Local Backend
```bash
npm run build:local
```
This creates a production build that connects to your local backend.

## Environment Variables

You can create a `.env.local` file to override the backend URL:

```bash
# .env.local
VITE_BACKEND_URL=https://your-custom-backend.onrender.com
```

## No More Switching!

With this setup, you should never need to manually switch configurations:

1. **Local Development**: `npm run dev` (connects to localhost:8000)
2. **Production Deployment**: `npm run build` (connects to Render backend)
3. **Testing Production Backend**: `npm run dev:prod-backend` (if needed)

The app automatically detects the environment and chooses the correct backend URL.

## Debugging

Check the browser console when the app loads - you'll see API configuration logs like:
```
🔧 API Configuration: {
  environment: 'development',
  baseUrl: '/api',
  health_url: '/api/health',
  advice_url: '/api/advice'
}
``` 