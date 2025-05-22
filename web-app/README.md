# The Genius - Fantasy Sports AI Assistant (Web App)

A modern web chat interface for getting AI-powered fantasy sports advice. This is the frontend companion to your fantasy sports AI assistant that helps users make better decisions about their fantasy teams.

## 🏆 What This App Does

- **Chat Interface**: Clean, modern chat where users ask fantasy sports questions
- **AI Responses**: Powered by your backend API that connects to GPT-4
- **Daily Limits**: Free users get 5 messages per day (encourages iOS app downloads)
- **Smart Features**: Detects when users ask for current stats and enables web search
- **Mobile Friendly**: Works great on phones, tablets, and computers

## 🚀 Quick Start (For Development)

### What You Need First
- **Node.js** (version 18 or newer) - [Download here](https://nodejs.org/)
- **pnpm** (package manager) - Install by running: `npm install -g pnpm`
- Your **backend API** running (the fantasy-backend folder)

### Step 1: Get the Code Running
```bash
# 1. Open your terminal/command prompt
# 2. Navigate to the web-app folder
cd web-app

# 3. Install all the code dependencies
pnpm install

# 4. Start the development server
pnpm run dev
```

### Step 2: Open in Browser
- Open your web browser
- Go to: `http://localhost:5173`
- You should see "Fantasy AI Assistant" with a chat interface

### Step 3: Test It Works
- Type a fantasy sports question like: "Who should I start this week?"
- If your backend is running, you should get an AI response
- If not, you'll see an error message

## 🛠️ Technology Stack (What's Under the Hood)

### Core Technologies
- **React 19** - The main framework that makes the app interactive
- **TypeScript** - Adds type safety to prevent bugs
- **Vite** - Super fast build tool that makes development smooth

### Styling & UI
- **Tailwind CSS** - Utility classes for quick, consistent styling
- **Heroicons** - Beautiful icons (like the send button)
- **Framer Motion** - Smooth animations (like the quota modal)

### Special Features
- **React Markdown** - Converts AI responses with formatting into nice display
- **Daily Quota System** - Tracks message limits using browser storage

## 📁 Project Structure

```
web-app/
├── src/
│   ├── components/           # Reusable UI pieces
│   │   ├── chat.tsx         # Main chat interface
│   │   ├── message.tsx      # Individual chat messages
│   │   └── QuotaModal.tsx   # Daily limit popup
│   ├── hooks/
│   │   └── useDailyQuota.ts # Manages 5-message daily limit
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # App entry point
│   └── index.css            # Global styles
├── public/                  # Static files (icons, etc.)
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Build configuration
├── tailwind.config.js      # Styling configuration
└── render.yaml             # Deployment configuration
```

## 🔧 Available Commands

### Development
```bash
pnpm run dev        # Start development server (with hot reload)
pnpm run build      # Create production build
pnpm run preview    # Preview production build locally
pnpm run lint       # Check code for issues
```

### What Each Command Does
- **dev**: Starts a local server that automatically updates when you change files
- **build**: Creates optimized files ready for deployment
- **preview**: Lets you test the production build before deploying
- **lint**: Checks your code for potential problems

## 🌐 How It Connects to Your Backend

### Development Setup
- When you run `pnpm run dev`, all API calls to `/api/*` automatically forward to your backend
- This is configured in `vite.config.ts` with this line:
  ```typescript
  proxy: { '/api': 'https://genius-backend.onrender.com' }
  ```

### In Production
- The `render.yaml` file tells Render (your hosting service) to forward API calls
- Users visit your frontend, but API calls go to your backend automatically

## 📱 Daily Quota System

### How It Works
1. **Tracking**: Uses browser's localStorage to count messages per day
2. **Limit**: Free users get 5 messages per day
3. **Reset**: Counter resets automatically at midnight
4. **Modal**: After 5 messages, shows popup encouraging iOS app download

### Where the Code Lives
- **Hook**: `src/hooks/useDailyQuota.ts` - Manages the counting logic
- **UI**: `src/components/QuotaModal.tsx` - The popup that appears
- **Integration**: `src/components/chat.tsx` - Uses the hook and shows the modal

## 🚀 Deployment (Getting It Live)

### Automatic Deployment with Render
1. **Connect Repository**: 
   - Go to [Render.com](https://render.com)
   - Click "New" → "Static Site"
   - Connect your GitHub repository
   - Select the `web-app` folder

2. **Configuration** (Render reads from `render.yaml`):
   - **Build Command**: `pnpm install && pnpm run build`
   - **Publish Directory**: `dist`
   - **Auto-Deploy**: Enabled (updates when you push to GitHub)

3. **Custom Domain** (Optional):
   - In Render dashboard, go to your static site
   - Click "Settings" → "Custom Domains"
   - Add your domain and follow DNS instructions

### Manual Deployment
```bash
# Build the production version
pnpm run build

# The 'dist' folder contains your deployable files
# Upload the contents to any static hosting service:
# - Netlify, Vercel, AWS S3, etc.
```

## 🛠️ Development Workflow

### Making Changes
1. **Start Development Server**: `pnpm run dev`
2. **Edit Files**: Changes appear instantly in browser
3. **Test**: Make sure everything works as expected
4. **Build**: `pnpm run build` to test production version
5. **Deploy**: Push to GitHub (auto-deploys if connected to Render)

### Adding New Features
1. **Components**: Add new UI pieces in `src/components/`
2. **Hooks**: Add new logic in `src/hooks/`
3. **Styling**: Use Tailwind classes for consistent design
4. **Testing**: Test thoroughly before deploying

## 🎨 Customization Options

### Changing Colors/Styles
- **Primary Colors**: Edit `tailwind.config.js` to change blue theme
- **Global Styles**: Edit `src/index.css` for app-wide changes
- **Component Styles**: Each component has Tailwind classes you can modify

### Modifying Daily Limit
- **Change Number**: Edit `MAX_DAILY_MESSAGES` in `src/hooks/useDailyQuota.ts`
- **Disable Limit**: Remove quota checks from `src/components/chat.tsx`

### Updating Messages
- **Placeholder Text**: Edit the examples in `src/components/chat.tsx`
- **Modal Text**: Edit `src/components/QuotaModal.tsx` for quota messages

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
# Delete node_modules and reinstall
rm -rf node_modules
pnpm install
```

**API calls not working**
- Check if your backend is running
- Verify the proxy URL in `vite.config.ts` matches your backend
- Open browser developer tools (F12) to see network errors

**Build fails**
```bash
# Check for TypeScript errors
pnpm run lint

# Fix any issues shown, then try building again
pnpm run build
```

**Styles not updating**
- Make sure Tailwind classes are spelled correctly
- Restart the development server: `Ctrl+C` then `pnpm run dev`

### Getting Help
- **TypeScript Errors**: Most IDEs (VS Code recommended) will show red underlines
- **Browser Console**: Press F12 to see JavaScript errors
- **Network Tab**: In browser dev tools, shows if API calls are failing

## 📊 Performance & Best Practices

### What's Already Optimized
- **Code Splitting**: Vite automatically splits code for faster loading
- **Compression**: Gzip compression enabled for smaller file sizes
- **Caching**: Static assets cached for better performance
- **Modern Build Target**: ES2018 for good browser support

### Monitoring Usage
- **Daily Quotas**: Check browser localStorage to see user patterns
- **API Calls**: Monitor your backend for usage statistics
- **Performance**: Use browser dev tools to check loading times

## 🔮 Future Enhancements

### Easy Additions
- **User Accounts**: Add login system to track quotas per user instead of device
- **Payment Integration**: Add Stripe for premium subscriptions
- **More Sports**: Expand beyond fantasy to other sports topics
- **Dark Mode**: Add theme toggle using Tailwind's dark mode features

### Advanced Features
- **Real-time Updates**: Add WebSocket support for live data
- **Voice Input**: Add speech-to-text for voice questions
- **Image Support**: Allow users to upload roster screenshots
- **Export Chats**: Let users save their conversation history

## 📝 Contributing

### For Solo Development
1. **Branch Strategy**: Create feature branches from `main`
2. **Testing**: Test thoroughly before merging
3. **Documentation**: Update this README when adding features
4. **Deployment**: Use automatic deployment for convenience

### Code Style
- **TypeScript**: Use types for better code reliability
- **Components**: Keep components small and focused
- **Hooks**: Extract reusable logic into custom hooks
- **Comments**: Add comments for complex logic

---

## 📄 License & Credits

**Built with AI assistance** - This project leverages AI tools for development efficiency while maintaining high code quality and best practices.

**Solo Developer Project** - Designed for single-developer productivity with modern tooling and clear documentation.

---

*Need help? Check the troubleshooting section above or review the component files for implementation details.*