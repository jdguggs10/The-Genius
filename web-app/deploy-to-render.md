# Deploy genius-webapp to Render

## Overview
This guide will help you deploy your web app to Render with the new service name "genius-webapp".

## Prerequisites
1. GitHub repository with your latest code
2. Render account (free tier is fine for testing)

## Deployment Steps

### Option 1: Deploy via Render Dashboard (Recommended)

1. **Go to Render Dashboard**
   - Visit [render.com](https://render.com)
   - Sign in to your account

2. **Create New Static Site**
   - Click "New +" button
   - Select "Static Site"

3. **Connect Repository**
   - Choose "Connect a repository"
   - Select your GitHub repository
   - Choose the branch (usually `main` or `master`)

4. **Configure Build Settings**
   ```
   Name: genius-webapp
   Build Command: pnpm install --frozen-lockfile && pnpm config set auto-install-peers true && pnpm run build
   Publish Directory: dist
   Root Directory: web-app
   ```

5. **Environment Variables**
   Add these environment variables:
   ```
   NODE_VERSION=20
   PNPM_VERSION=9
   NODE_ENV=production
   VITE_BACKEND_URL=https://genius-backend-nhl3.onrender.com
   ```

6. **Deploy**
   - Click "Create Static Site"
   - Wait for the build to complete (usually 2-5 minutes)

### Option 2: Deploy via render.yaml (Blueprint)

1. **Ensure render.yaml is in your repository**
   - The file is already configured in the `web-app` directory

2. **Create New Blueprint**
   - In Render dashboard, click "New +"
   - Select "Blueprint"
   - Connect your repository
   - Point to the `web-app/render.yaml` file

3. **Deploy**
   - Review the configuration
   - Click "Apply"

### Option 3: Deploy via Render CLI

1. **Install Render CLI**
   ```bash
   npm install -g @render/cli
   ```

2. **Login to Render**
   ```bash
   render login
   ```

3. **Deploy from web-app directory**
   ```bash
   cd web-app
   render deploy
   ```

## Expected Deployment URL
Your app will be available at: `https://genius-webapp.onrender.com`

## Build Verification
Before deploying, you can verify the build works locally:

```bash
cd web-app
pnpm install --frozen-lockfile
pnpm config set auto-install-peers true
pnpm run build
pnpm run preview
```

## Troubleshooting

### Common Issues:
1. **Build fails with "command not found: pnpm"**
   - Ensure PNPM_VERSION is set to "9" in environment variables

2. **Build succeeds but app doesn't load**
   - Check that VITE_BACKEND_URL is correctly set
   - Verify the backend service is running

3. **Assets not loading**
   - Check the staticPublishPath is set to "dist"
   - Ensure the build command generates files in the dist folder

4. **TypeScript import errors**
   - Ensure imports don't include file extensions (.tsx, .ts)
   - Check that all imported files exist

### Build Output Verification:
After a successful build, you should see these files in the `dist` folder:
- `index.html`
- `assets/` directory with CSS and JS files
- `sw.js` (service worker)
- `manifest.webmanifest`
- Various PWA icons

## Post-Deployment

1. **Test the deployment**
   - Visit your new URL
   - Test the main functionality
   - Check browser console for any errors

2. **Monitor performance**
   - Use Render's dashboard to monitor build times and performance
   - Check the logs if there are any issues

3. **Update DNS (optional)**
   - If you have a custom domain, update your DNS settings to point to the new Render deployment

## Security Headers
The deployment includes security headers:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin

## Performance Features
- Static asset caching with long max-age
- Gzip compression
- PWA support with service worker
- Chunk splitting for vendor and UI libraries

## Next Steps
1. Deploy the app following one of the methods above
2. Test thoroughly
3. Update any external services that reference the old deployment
4. Delete the old broken deployment once this one is confirmed working 