# Deployment Checklist for genius-webapp

## Pre-Deployment ✅

- [x] Build tested and working locally
- [x] Updated render.yaml with new service name "genius-webapp"
- [x] All dependencies properly configured in package.json
- [x] Environment variables defined
- [x] Build command includes `pnpm approve-builds`
- [x] PWA assets generated correctly
- [x] Security headers configured

## Deployment Steps

### Step 1: Commit Changes
```bash
git add .
git commit -m "feat: prepare fresh deployment as genius-webapp"
git push origin main
```

### Step 2: Deploy to Render (Choose One Method)

#### Method A: Via Render Dashboard (Easiest)
- [ ] Go to [render.com](https://render.com)
- [ ] Click "New +" → "Static Site"
- [ ] Connect GitHub repository
- [ ] Configure:
  - Name: `genius-webapp`
  - Build Command: `pnpm install --frozen-lockfile && pnpm approve-builds && pnpm run build`
  - Publish Directory: `dist`
  - Root Directory: `web-app`
- [ ] Add Environment Variables:
  - `NODE_VERSION=20`
  - `PNPM_VERSION=9`
  - `NODE_ENV=production`
  - `VITE_BACKEND_URL=https://genius-backend-nhl3.onrender.com`
- [ ] Click "Create Static Site"

#### Method B: Via Blueprint (render.yaml)
- [ ] In Render: "New +" → "Blueprint"
- [ ] Connect repository
- [ ] Point to `web-app/render.yaml`
- [ ] Review and apply

### Step 3: Monitor Deployment
- [ ] Build starts successfully
- [ ] Build completes without errors (2-5 minutes)
- [ ] Site becomes accessible at `https://genius-webapp.onrender.com`

### Step 4: Test Deployment
- [ ] Site loads correctly
- [ ] API calls work (check browser network tab)
- [ ] PWA features work (try installing as app)
- [ ] No console errors
- [ ] Responsive design works on mobile

### Step 5: Update References
- [ ] Update any external services pointing to old deployment
- [ ] Update documentation with new URL
- [ ] Update any environment variables in other services

### Step 6: Cleanup
- [ ] Test new deployment thoroughly for 24-48 hours
- [ ] Delete old broken deployment
- [ ] Remove old service references

## Expected Results

✅ **Deployment URL**: `https://genius-webapp.onrender.com`
✅ **Build Time**: ~2-5 minutes
✅ **Bundle Size**: ~800KB (with compression)
✅ **Performance**: Static site with edge caching

## Troubleshooting

If deployment fails:
1. Check build logs in Render dashboard
2. Verify environment variables are set correctly
3. Ensure pnpm version is specified
4. Check that backend service is running

## Success Criteria

- [ ] Site loads in under 3 seconds
- [ ] All major features work
- [ ] No console errors
- [ ] Mobile responsive
- [ ] PWA installation works
- [ ] API integration functional

---

**Note**: This deployment replaces your previous broken deployment. Once confirmed working, you can safely delete the old deployment. 