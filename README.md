# The Genius - AI-Powered Fantasy Sports Assistant

> **Your Personal Fantasy Sports Expert** - Get AI-powered advice to dominate your leagues!

The Genius is a comprehensive fantasy sports platform that combines artificial intelligence with real sports data to help you make better fantasy decisions. Available as a web app and native iOS app, whether you're struggling with lineup choices, trade decisions, or waiver wire pickups, The Genius has you covered.

## 🏆 What Does This Do?

Think of The Genius as your personal fantasy sports consultant that:

- **Answers Questions**: "Should I start Josh Allen or Patrick Mahomes this week?"
- **Provides Analysis**: Get detailed breakdowns of player matchups and trends
- **Helps with Trades**: "Is this trade worth it?" - get unbiased AI analysis
- **Finds Sleepers**: Discover hidden gems on the waiver wire
- **Works 24/7**: Available whenever you need fantasy advice
- **Cross-Platform**: Use the web app or native iOS app

### Who Is This For?

- **Fantasy Sports Players** who want an edge over their competition
- **Casual Fans** who need help setting lineups each week
- **Serious Players** who want data-driven analysis
- **League Commissioners** who want to add value for their members

## 🛠 How It's Built

Your project has **four main parts** that work together:

```
The Genius Project
├── 🌐 Web App (React)
│   └── Chat interface for web browsers
├── 📱 iOS App (SwiftUI)
│   └── Native iOS app with real-time streaming
├── 🧠 Backend API (FastAPI + Python)
│   └── Connects to OpenAI's GPT-4.1 for smart answers
└── 📊 ESPN Integration (Python)
    └── Fetches real fantasy sports information
```

### 1. Web App (`/web-app`)
- **What it is**: The website people visit
- **What it does**: Provides a clean chat interface with web search capabilities
- **Technology**: React with TypeScript and Vite
- **Special features**: 
  - Daily message limits for free users
  - Real-time streaming responses
  - Web search integration with "search:" prefix

### 2. iOS App (`/ios-app`)
- **What it is**: Native iOS application
- **What it does**: Full-featured mobile experience with SwiftUI
- **Technology**: Swift 5.5+, SwiftUI, iOS 15+
- **Special features**:
  - Real-time streaming responses
  - Structured advice display with confidence scores
  - Native iOS design following Apple HIG
  - Conversation management
  - Share functionality
  - iPad optimized layouts

### 3. Backend API (`/backend`)  
- **What it is**: The server that powers everything
- **What it does**: Takes questions and sends them to OpenAI's AI
- **Technology**: Python with FastAPI
- **Special features**: 
  - Uses OpenAI GPT-4.1 with Structured Responses API
  - Server-Sent Events (SSE) for real-time streaming
  - CORS configured for cross-platform access

### 4. ESPN Integration (`/espn-api-util`)
- **What it is**: Tools to get real fantasy data
- **What it does**: Connects to ESPN to get player stats, rosters, etc.
- **Technology**: Python with ESPN API and MCP protocol
- **Special feature**: Works with private leagues (with authentication)

## 🚀 Quick Start Guide

### Option 1: Just Want to See It Work?
If you just want to test the existing deployment:

**Web App**: https://genius-frontend.onrender.com
**iOS App**: Build and run from Xcode (see iOS setup below)

### Option 2: Want to Run It Yourself?

#### Step 1: Get the Code
```bash
git clone https://github.com/your-username/the-genius.git
cd the-genius
```

#### Step 2: Set Up the Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and add your OpenAI API key
```

#### Step 3: Set Up the Web App
```bash
cd web-app
npm install -g pnpm  # Install pnpm for faster installs
pnpm install
# Create .env file with VITE_BACKEND_URL=http://localhost:8000
pnpm run dev
```

#### Step 4: Set Up the iOS App
```bash
cd ios-app
# Open ios-app.xcodeproj in Xcode
# Update backend URL in ChatViewModel.swift if needed
# Build and run on iOS Simulator or device
```

#### Step 5: Test Everything
1. **Backend**: Visit http://localhost:8000 - should show "API is running"
2. **Frontend**: Visit http://localhost:5173 - should show the chat interface
3. **iOS App**: Launch from Xcode - should show native iOS interface
4. **Test Chat**: Ask "Hello" - should get an AI response

## 📁 Project Structure

```
the-genius/
├── 📱 ios-app/                    # Native iOS application
│   ├── ios-app/                   # Main app source
│   │   ├── ChatViewModel.swift    # Core chat logic & SSE handling
│   │   ├── ContentView.swift      # Main app interface
│   │   ├── MessageBubble.swift    # Chat message UI component
│   │   ├── NetworkModels.swift    # API data models
│   │   ├── Message.swift          # Core message data structure
│   │   └── ...                    # Other UI components
│   ├── ios-app.xcodeproj/         # Xcode project file
│   └── README.md                  # iOS-specific instructions
│
├── 🌐 web-app/                    # React web application
│   ├── src/components/            # Reusable UI components
│   ├── src/hooks/                 # React hooks for logic
│   ├── src/types/                 # TypeScript type definitions
│   ├── package.json               # Dependencies and scripts
│   └── README.md                  # Web app instructions
│
├── 🔧 backend/                    # FastAPI Python server  
│   ├── app/                       # Main application code
│   │   ├── services/              # OpenAI integration
│   │   ├── models.py              # Pydantic data models
│   │   └── main.py                # FastAPI server
│   ├── requirements.txt           # Python dependencies
│   └── README.md                  # Backend setup guide
│
├── 📊 espn-api-util/             # ESPN fantasy sports integration
│   ├── baseball_mcp/              # Baseball-specific tools
│   ├── espn_fantasy_server.py     # Main ESPN server
│   └── README.md                  # ESPN integration guide
│
├── 🔄 shared-resources/          # Shared assets and configs
└── 📖 README.md                   # This overview file
```

## 🌟 Key Features

### Cross-Platform Experience
- **Web App**: Full-featured browser experience
- **iOS App**: Native mobile experience with SwiftUI
- **Consistent API**: Same backend powers both platforms

### Real-Time Streaming
- **Live Responses**: See AI typing in real-time
- **Server-Sent Events**: Efficient streaming protocol
- **Progress Indicators**: Status updates during processing

### Structured Advice Display
- **Confidence Scores**: AI provides confidence ratings
- **Alternative Options**: Multiple player suggestions
- **Detailed Reasoning**: Explanations for recommendations
- **Model Attribution**: Shows which AI model provided advice

### Smart Data Integration
- **Web Search**: AI can search for current information
- **ESPN Integration**: Real fantasy sports data
- **Context Awareness**: Remembers conversation history

## 🔧 Requirements

### For Users
- **Web**: Any modern browser
- **iOS**: iOS 15.0+, iPhone or iPad

### For Development
- **Python 3.11+**: Backend development
- **Node.js 18+**: Web app development  
- **Xcode 14+**: iOS development
- **OpenAI API Key**: For AI functionality

## 💡 Usage Examples

### General Fantasy Questions
- "Should I start Josh Allen or Lamar Jackson this week?"
- "Who are the best waiver wire pickups?"
- "Is this trade worth it: my Derrick Henry for their Cooper Kupp?"

### With Web Search (use "search:" prefix)
- "search: Who got injured in today's NFL games?"
- "search: Latest news on Ja'Marr Chase injury status"
- "search: Current weather forecast for Sunday's outdoor games"

### iOS App Features
- **Long Press**: Share any message
- **Conversation History**: Browse past conversations
- **Structured Advice**: Tap to expand detailed analysis
- **Confidence Indicators**: See AI's confidence level

## 🚀 Deployment

### Current Live Deployments
- **Backend**: https://genius-backend-nhl3.onrender.com
- **Web App**: https://genius-frontend.onrender.com
- **iOS App**: Build locally with Xcode

### Deploy Your Own
1. **Backend**: Deploy to Render, Railway, or similar
2. **Web App**: Deploy to Vercel, Netlify, or Render
3. **iOS App**: Deploy to App Store via Xcode

## 🔄 Development Workflow

### Making Changes
1. **Backend Changes**: Update Python code, test locally, deploy
2. **Web Changes**: Update React code, test locally, deploy
3. **iOS Changes**: Update Swift code, test in simulator/device, archive for App Store

### Testing
- **Backend**: FastAPI provides automatic API docs at `/docs`
- **Web**: React dev server with hot reload
- **iOS**: Xcode simulator and device testing

## 📈 Scaling Considerations

- **Rate Limiting**: Implement per-user API limits
- **Caching**: Cache frequent responses to reduce costs
- **Analytics**: Track usage patterns and popular queries
- **Error Handling**: Comprehensive error reporting and recovery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly across platforms
5. Submit a pull request

## 📄 License

[Add your license information here]

---

**The Genius** - Making fantasy sports decisions easier, one AI-powered conversation at a time. 🏆