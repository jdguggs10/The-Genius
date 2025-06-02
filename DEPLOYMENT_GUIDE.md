# 🚀 Deployment Guide - No More Manual Configuration Switching!

## ✅ Problem Solved!

You no longer need to manually switch configurations between local development and production deployment. Your codebase now automatically detects the environment and uses the appropriate backend URL.

## 📱 Web App (Auto-Configuration)

### Local Development
```bash
cd web-app
npm run dev
```
- **Automatically connects to**: `http://localhost:8000` (via proxy)
- **Requirements**: Backend running on port 8000
- **No configuration needed**

### Production Deployment
```bash
npm run build
```
- **Automatically connects to**: `https://genius-backend-nhl3.onrender.com`
- **Deploy to Render**: Automatically works

### Optional Overrides
- **Test against production backend locally**: `npm run dev:prod-backend`
- **Build for local backend**: `npm run build:local`

## 📱 iOS App (Simple Toggle)

### Current Default: Production Backend
The iOS app uses production backend (`https://genius-backend-nhl3.onrender.com`) by default.

### Switch to Local Development
1. Open `ios-app/ios-app/ApiConfiguration.swift`
2. In `getBackendBaseURL()`, uncomment:
   ```swift
   return localBackendURL
   ```
3. Comment out:
   ```swift
   // return productionBackendURL
   ```

## 🔧 Backend (Works with Both)

Your FastAPI backend in `backend/app/main.py` already supports both environments with proper CORS:

```python
origins = [
    "http://localhost:3000",  # React dev
    "http://localhost:5173",  # Vite dev
    "https://genius-frontend.onrender.com",  # Production
    "*"  # Temporarily open for debugging
]
```

### Local Development
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
- **Render**: Automatically deploys via `render.yaml`
- **Uses**: Docker container with proper port binding

## 🎯 Your New Workflow

### Option 1: All Local Development
1. **Backend**: `cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. **Web App**: `cd web-app && npm run dev` (auto-connects via proxy)
3. **iOS App**: Toggle to local backend in `ApiConfiguration.swift`

### Option 2: Local Frontend + Production Backend
1. **Web App**: `cd web-app && npm run dev:prod-backend`
2. **iOS App**: Keep production backend (default)
3. **Backend**: Not needed locally

### Option 3: Production Deployment
1. **Backend**: Push to GitHub → Auto-deploys to Render
2. **Web App**: `npm run build` → Deploy to Render → Auto-connects to production backend
3. **iOS App**: Keep production backend (default) → Archive for App Store

## 🐛 Debugging

### Web App
Check browser console for:
```
🔧 API Configuration: {
  environment: 'development',
  baseUrl: '/api',
  advice_url: '/api/advice'
}
```

### iOS App
Check Xcode console for:
```
🔧 iOS API Configuration:
   Environment: DEBUG
   Backend Base URL: https://genius-backend-nhl3.onrender.com
   Advice URL: https://genius-backend-nhl3.onrender.com/advice
```

## 📁 Configuration Files

- **Web App**: `web-app/src/utils/api.ts` (automatic detection)
- **iOS App**: `ios-app/ios-app/ApiConfiguration.swift` (simple toggle)
- **Backend**: `backend/app/main.py` (supports both environments)

## 🎉 Benefits

✅ **No more manual URL switching**  
✅ **Environment auto-detection**  
✅ **Consistent configuration across platforms**  
✅ **Easy debugging with configuration logs**  
✅ **Deployment-ready out of the box**

## 📝 Configuration Reference

### Web App Scripts
```json
{
  "dev": "vite",                    // Auto-connects to localhost:8000
  "dev:prod-backend": "...",        // Connects to production backend
  "build": "...",                   // Production build (auto-connects to production)
  "build:local": "..."              // Local backend build
}
```

### Environment Variables
- **VITE_BACKEND_URL**: Optional override for web app
- **No environment variables needed for iOS app**

You're all set! 🚀 