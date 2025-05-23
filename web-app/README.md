# The Genius - Fantasy Sports AI Web App

> **The Face of Your AI Assistant** - A modern, clean chat interface where users get expert fantasy sports advice

This is the frontend web application that users interact with. It provides a beautiful, mobile-friendly chat interface where people can ask fantasy sports questions and get intelligent AI responses. Think of it as the "face" of your AI assistant that makes everything user-friendly.

## 🌟 What This Does

This web app provides:
- **Clean Chat Interface**: Simple, WhatsApp-style messaging
- **Smart AI Responses**: Connects to your backend API for GPT-4.1 powered advice
- **Daily Usage Limits**: Free users get 5 messages per day (encourages premium upgrades)
- **Web Search Detection**: Automatically enables web search when users ask for current stats
- **Mobile Friendly**: Works perfectly on phones, tablets, and computers
- **Instant Responses**: Fast, responsive interface with loading indicators

## 🎯 Who Uses This

- **Fantasy Sports Players**: People who want quick advice on lineups, trades, pickups
- **Casual Fans**: Users who need help understanding complex fantasy decisions  
- **Mobile Users**: Anyone who prefers a simple chat interface over complex apps
- **Your Website Visitors**: The main way people interact with your AI assistant

## 🔧 Technology Stack (What's Under the Hood)

### Core Technologies
- **React 19**: Latest version of the most popular web framework
- **TypeScript**: Adds type safety to prevent bugs and improve development
- **Vite**: Super fast build tool that makes development smooth and quick

### Styling & UI
- **Tailwind CSS**: Utility-first CSS framework for consistent, beautiful styling
- **Heroicons**: Clean, professional icons (like the send button)
- **Framer Motion**: Smooth animations (like the quota modal popup)

### Special Features
- **React Markdown**: Converts AI responses with formatting into nice, readable display
- **Daily Quota System**: Tracks message limits using browser's local storage
- **Responsive Design**: Automatically adapts to any screen size

## 📁 Project Structure

```
web-app/
├── src/                           # All the source code
│   ├── components/               # Reusable UI pieces
│   │   ├── chat.tsx             # Main chat interface (the heart of the app)
│   │   ├── message.tsx          # Individual chat message bubbles
│   │   └── QuotaModal.tsx       # Daily limit popup modal
│   ├── hooks/                   # Custom React logic
│   │   └── useDailyQuota.ts     # Manages 5-message daily limit
│   ├── App.tsx                  # Main app component that brings everything together
│   ├── main.tsx                 # App entry point (starts everything)
│   └── index.css                # Global styles and Tailwind imports
├── public/                      # Static files (icons, images, etc.)
├── package.json                 # Lists all dependencies and scripts
├── vite.config.ts              # Build tool configuration
├── tailwind.config.js          # Styling framework configuration
├── render.yaml                 # Deployment configuration for Render.com
└── README.md                   # This detailed guide
```

## 🚀 Quick Start Guide

### Step 1: Get Your Environment Ready

**Install Node.js** (if you don't have it):
1. Go to [nodejs.org](https://nodejs.org)
2. Download the "LTS" version (recommended for most users)
3. Install it (follow the installer instructions)
4. Open a terminal/command prompt and verify:
   ```bash
   node --version  # Should show v18 or higher
   npm --version   # Should show 8 or higher
   ```

**Install pnpm** (faster than npm):
```bash
# Install pnpm globally
npm install -g pnpm

# Verify it works
pnpm --version  # Should show version number
```

### Step 2: Get the Code and Install Dependencies

```bash
# 1. Navigate to the web-app folder
cd web-app

# 2. Install all required packages (this takes a few minutes the first time)
pnpm install

# You should see it download lots of packages - this is normal!
```

### Step 3: Configure the Backend Connection

**Check the backend URL** in `src/components/chat.tsx`:
```typescript
// Look for this line around line 44:
const response = await fetch('https://genius-backend-nhl3.onrender.com/advice', {
```

**If you're running your own backend**, change the URL to match:
```typescript
// For local development:
const response = await fetch('http://localhost:8000/advice', {

// For your own deployed backend:
const response = await fetch('https://your-backend-url.com/advice', {
```

### Step 4: Start the Development Server

```bash
# Start the development server
pnpm run dev

# You should see output like:
# VITE v5.x.x ready in xxx ms
# ➜ Local:   http://localhost:5173/
# ➜ Network: use --host to expose
```

### Step 5: Test Everything Works

1. **Open your browser** and go to: `http://localhost:5173`
2. **Should see**: "The Genius" header and chat interface
3. **Test the chat**: Type "Hello" and press Enter or click send
4. **Should get**: An AI response (if your backend is working)
5. **Check daily counter**: Should show "1 of 5 messages used today"

## 🎨 Features Deep Dive

### Chat Interface (`src/components/chat.tsx`)

**What it does**:
- Handles all user interactions (typing, sending messages)
- Connects to your backend API to get AI responses
- Manages conversation history and display
- Controls daily message limits

**Key features**:
- **Auto-scroll**: Always shows the latest message
- **Loading indicators**: Shows "AI is thinking..." while waiting
- **Error handling**: Shows helpful error messages if something goes wrong
- **Smart web search**: Automatically enables web search for questions about "stats", "current", or "latest"

**Message flow**:
```
User types → Press Enter → Send to backend → Get AI response → Display in chat
```

### Daily Quota System (`src/hooks/useDailyQuota.ts`)

**How it works**:
1. **Tracks daily usage**: Stores count in browser's localStorage
2. **Resets automatically**: Counter resets at midnight each day
3. **Enforces limits**: Blocks new messages after 5 per day
4. **Shows modal**: Encourages users to get the mobile app for unlimited access

**Storage format**:
```javascript
// In browser localStorage:
"quota-2024-03-15": "3"  // Used 3 messages on March 15, 2024
```

### Message Components (`src/components/message.tsx`)

**User messages**: 
- Blue bubbles on the right side
- Simple text display

**AI responses**:
- Gray bubbles on the left side  
- Supports Markdown formatting (bold, italics, lists, etc.)
- Automatically formats longer responses nicely

### Quota Modal (`src/components/QuotaModal.tsx`)

**When it appears**: After user hits 5 message limit
**What it shows**: 
- "Daily Limit Reached" message
- Explanation of the 5-message limit
- Encouragement to download mobile app
- Close button to dismiss

## 🛠 Development Guide

### Available Commands

```bash
# Development (with hot reload - changes appear instantly)
pnpm run dev

# Build for production (creates optimized files)
pnpm run build

# Preview production build locally (test before deploying)
pnpm run preview

# Check code for issues (find potential problems)
pnpm run lint
```

### Making Changes

**To modify the chat interface**:
1. Open `src/components/chat.tsx` in your text editor
2. Make your changes (add features, change styling, etc.)
3. Save the file
4. Changes appear instantly in your browser (hot reload)

**To change colors/styling**:
1. **Global changes**: Edit `src/index.css`
2. **Component styling**: Look for `className=` in component files
3. **Tailwind classes**: Use classes like `bg-blue-500`, `text-white`, etc.

**To modify daily limits**:
1. Open `src/hooks/useDailyQuota.ts`
2. Change `MAX_DAILY_MESSAGES = 5` to your desired number
3. Save and test

### Adding New Features

**Example: Add a "Clear Chat" button**

1. **Add to chat component** (`src/components/chat.tsx`):
```typescript
// Add this function inside the Chat component:
const clearChat = () => {
  setMessages([]);
};

// Add this button in the JSX (around line 140):
<button 
  onClick={clearChat}
  className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm"
>
  Clear Chat
</button>
```

2. **Test it works**: Click the button, chat should clear

3. **Style it nicely**: Adjust the Tailwind classes as needed

### Working with the Backend

**API call structure** (in `src/components/chat.tsx`):
```typescript
const response = await fetch('your-backend-url/advice', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({ 
    conversation: [{ role: 'user', content: 'user question' }],
    enable_web_search: false  // or true for current stats
  })
});
```

**Expected response format**:
```json
{
  "reply": "AI's response text",
  "model": "gpt-4.1"
}
```

### Error Handling

The app handles these error scenarios:
- **Network errors**: "Unable to connect to AI service"
- **Backend errors**: Shows specific error message from server
- **Invalid responses**: "Invalid response format from backend"
- **Quota exceeded**: Shows quota modal instead of sending request

## 🌐 Deployment Guide

### Deploy to Render.com (Recommended - Easy)

**Step 1: Prepare Your Code**
1. Make sure your code is saved and pushed to GitHub
2. Test locally to ensure everything works
3. Verify `render.yaml` exists in your web-app folder

**Step 2: Set Up Render**
1. Go to [render.com](https://render.com) and create account
2. Click "New" → "Static Site"
3. Connect your GitHub repository
4. Select your repository from the list

**Step 3: Configure the Service**
- **Name**: `genius-frontend` (or whatever you prefer)
- **Branch**: `main` (or your main branch)
- **Root Directory**: `web-app` (important!)
- **Build Command**: `pnpm install && pnpm run build`
- **Publish Directory**: `dist`

**Step 4: Configure Backend Routing**
Render will automatically read your `render.yaml` file which includes:
```yaml
routes:
  - type: rewrite
    source: /api/*
    destination: https://genius-backend-nhl3.onrender.com/:splat
```

This makes sure API calls from your frontend reach your backend.

**Step 5: Deploy**
1. Click "Create Static Site"
2. Wait for deployment (takes 3-5 minutes)
3. Test your deployed site at the provided URL
4. Future updates deploy automatically when you push to GitHub

### Deploy to Netlify (Alternative)

1. **Connect repository**: Link your GitHub repo
2. **Set build settings**:
   - Build command: `cd web-app && npm install && npm run build`
   - Publish directory: `web-app/dist`
3. **Add redirect rules** in `web-app/public/_redirects`:
   ```
   /api/* https://your-backend-url.com/:splat 200
   /* /index.html 200
   ```

### Deploy to Vercel (Alternative)

1. **Connect repository**: Import from GitHub
2. **Configure project**:
   - Framework preset: Vite
   - Root directory: `web-app`
   - Build command: `pnpm run build`
   - Output directory: `dist`
3. **Add environment variables** if needed

### Manual Deployment

**Build the production version**:
```bash
# From the web-app folder
pnpm run build

# Creates a 'dist' folder with optimized files
# Upload contents of 'dist' folder to any web hosting:
# - AWS S3 + CloudFront
# - Google Cloud Storage
# - Any web hosting service
```

## 🎨 Customization Guide

### Changing Colors and Appearance

**Main color scheme** (in `src/components/chat.tsx`):
```typescript
// User messages (currently blue):
className="bg-blue-500 text-white"  // Change blue-500 to any color

// AI messages (currently gray):
className="bg-gray-100 text-gray-800"  // Change colors as desired

// Send button:
className="bg-blue-500 hover:bg-blue-600"  // Change blue to any color
```

**Available Tailwind colors**:
- `red-500`, `green-500`, `yellow-500`, `purple-500`, `pink-500`
- `indigo-500`, `cyan-500`, `teal-500`, `lime-500`, `orange-500`
- Numbers: 100 (lightest) to 900 (darkest)

### Changing Text and Messages

**App title** (in `src/App.tsx`):
```typescript
<h1>The Genius</h1>  // Change to your preferred title
```

**Chat placeholder examples** (in `src/components/chat.tsx`):
```typescript
// Around line 85, change these examples:
<li>"Should I start Patrick Mahomes or Josh Allen this week?"</li>
<li>"Who are the top sleeper picks for fantasy baseball?"</li>
<li>"Is Christian McCaffrey worth trading for?"</li>
```

**Quota modal text** (in `src/components/QuotaModal.tsx`):
```typescript
<h2>Daily Limit Reached</h2>  // Change title
<p>You've reached your 5 message daily limit...</p>  // Change description
```

### Changing Daily Limits

**Modify the limit** (in `src/hooks/useDailyQuota.ts`):
```typescript
const MAX_DAILY_MESSAGES = 5;  // Change 5 to any number you want
```

**Disable limits completely**:
1. In `src/components/chat.tsx`, find this line:
   ```typescript
   if (!input.trim() || isLoading || isLimitReached) return;
   ```
2. Change to:
   ```typescript
   if (!input.trim() || isLoading) return;  // Remove isLimitReached
   ```
3. Hide the quota counter by removing this section:
   ```typescript
   <div className="text-center text-sm text-gray-500 mt-2">
     {count} of {5} messages used today
   </div>
   ```

### Adding Your Own Branding

**Logo/Image** (add to `public/` folder):
```typescript
// In src/App.tsx:
<img src="/your-logo.png" alt="Your Logo" className="h-12 w-auto" />
```

**Custom CSS** (in `src/index.css`):
```css
/* Add custom styles at the end */
.your-custom-class {
  background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
  color: white;
}
```

## 🐛 Troubleshooting

### Common Issues

**"Node.js not found" or "Command not found"**
```bash
# Install Node.js from nodejs.org
# Then restart your terminal and try again
node --version  # Should show v18+
```

**"pnpm not found"**
```bash
# Install pnpm globally
npm install -g pnpm

# Or use npm instead of pnpm throughout this guide
npm install  # instead of: pnpm install
npm run dev  # instead of: pnpm run dev
```

**"Module not found" errors**
```bash
# Delete node_modules and reinstall
rm -rf node_modules
pnpm install

# On Windows:
rmdir /s node_modules
pnpm install
```

**Web app loads but can't connect to backend**
1. **Check the backend URL** in `src/components/chat.tsx`
2. **Verify backend is running** by visiting its health endpoint
3. **Look at browser console** (press F12 → Console tab) for error messages
4. **Check CORS settings** in your backend

**Styling not working or looks wrong**
```bash
# Restart the development server  
# Press Ctrl+C to stop, then:
pnpm run dev
```

**Build fails**
```bash
# Check for TypeScript errors
pnpm run lint

# Fix any errors shown, then try building again
pnpm run build
```

### Debug Mode

**Enable verbose logging** (in `src/components/chat.tsx`):
```typescript
// Add more console.log statements:
console.log('Sending request:', { conversation: [userMessage] });
console.log('Response received:', response);
console.log('Parsed data:', data);
```

**Check browser developer tools**:
1. Press `F12` to open developer tools
2. **Console tab**: See JavaScript errors and log messages
3. **Network tab**: See API requests and responses
4. **Application tab**: Check localStorage for quota data

### Performance Issues

**Slow loading**:
- Check your internet connection
- Verify backend is responding quickly
- Consider using a CDN for static assets

**Memory issues**:
- Clear browser cache and cookies
- Restart browser
- Close other tabs/applications

## 📊 Analytics & Monitoring

### User Behavior Tracking

**Basic usage analytics** (add to `src/components/chat.tsx`):
```typescript
// Track when users send messages
const handleSend = async () => {
  // ... existing code ...
  
  // Simple analytics tracking:
  console.log('Message sent:', {
    timestamp: new Date().toISOString(),
    messageLength: input.length,
    dailyCount: count + 1
  });
};
```

**Quota tracking**:
```typescript
// In useDailyQuota.ts, add tracking:
const increment = () => {
  const newCount = count + 1;
  localStorage.setItem(storageKey, String(newCount));
  setCount(newCount);
  
  // Track quota usage
  if (newCount === MAX_DAILY_MESSAGES) {
    console.log('User hit daily limit');
  }
};
```

### Performance Monitoring

**Measure response times**:
```typescript
// In chat.tsx, around the API call:
const startTime = Date.now();
const response = await fetch(/* ... */);
const responseTime = Date.now() - startTime;
console.log(`Backend response time: ${responseTime}ms`);
```

### Error Tracking

**Track errors systematically**:
```typescript
// Add this to chat.tsx:
const trackError = (error: Error, context: string) => {
  console.error(`Error in ${context}:`, error);
  // In production, send to error tracking service:
  // errorTracker.capture(error, { context });
};

// Use in error handling:
} catch (error) {
  trackError(error as Error, 'API_REQUEST');
  // ... existing error handling
}
```

## 🔄 Updates & Maintenance

### Updating Dependencies

**Check for updates**:
```bash
# See outdated packages
pnpm outdated

# Update specific package
pnpm update react

# Update all packages (be careful!)
pnpm update
```

**Major version updates**:
```bash
# Update React to next major version
pnpm install react@latest react-dom@latest

# Update TypeScript
pnpm install -D typescript@latest
```

### Framework Updates

**Vite updates**:
- Check [Vite changelog](https://github.com/vitejs/vite/blob/main/packages/vite/CHANGELOG.md)
- Test thoroughly after updates
- Update vite.config.ts if needed

**React updates**:
- Follow [React upgrade guide](https://react.dev/blog)
- Test all components after major updates
- Update TypeScript types if needed

### Security Updates

**Regular maintenance**:
```bash
# Check for security vulnerabilities
pnpm audit

# Fix automatically fixable issues
pnpm audit --fix

# Update packages with known vulnerabilities
pnpm update
```

### Content Updates

**Regularly update**:
- Example questions in the chat interface
- Placeholder text and help messages
- Links to mobile app or premium features
- Terms of service or privacy policy links

## 🚀 Advanced Features

### Adding User Authentication

**Basic structure** (you'll need backend changes too):
1. **Add auth context** (`src/contexts/AuthContext.tsx`)
2. **Add login/signup forms** 
3. **Store user tokens** in localStorage
4. **Send tokens** with API requests
5. **Handle token expiration**

### Adding Payment Integration

**For premium features**:
1. **Install Stripe**: `pnpm install @stripe/stripe-js`
2. **Add payment components**
3. **Handle subscription status**
4. **Remove daily limits for paid users**

### Real-time Features

**WebSocket connection** for live updates:
1. **Install socket.io**: `pnpm install socket.io-client`
2. **Connect to WebSocket server**
3. **Handle real-time messages**
4. **Show typing indicators**

### PWA (Progressive Web App)

**Make it installable**:
1. **Add PWA plugin**: `pnpm install -D vite-plugin-pwa`
2. **Configure service worker**
3. **Add app manifest**
4. **Enable offline functionality**

---

## 📞 Support & Contributing

### Getting Help

1. **Check this README** for solutions to common problems
2. **Look at browser console** (F12) for error messages  
3. **Test each component separately** to isolate issues
4. **Check the backend connection** first if chat isn't working

### Contributing

**To add features or fix bugs**:
1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes and test thoroughly**
4. **Update this README** if you add new features
5. **Submit a pull request** with clear description

### Code Style Guidelines

- **Use TypeScript**: Add types for better code safety
- **Follow React best practices**: Use hooks, functional components
- **Keep components small**: Break large components into smaller pieces
- **Use meaningful names**: Variables and functions should be descriptive
- **Add comments**: Explain complex logic or unusual code
- **Test your changes**: Make sure everything works before submitting

### Reporting Issues

**When reporting bugs, include**:
1. **Steps to reproduce** the problem
2. **Expected vs actual behavior**
3. **Browser and version** (Chrome 120, Safari 17, etc.)
4. **Console errors** (from F12 developer tools)
5. **Screenshots** if the issue is visual

---

**🎨 Ready to create an amazing chat experience? Let's make your frontend shine!**

*Your users will love the clean, fast interface for getting fantasy sports advice!*