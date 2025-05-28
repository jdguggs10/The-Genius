# The Genius - AI-Powered Fantasy Sports Assistant

> **Your Personal Fantasy Sports Expert** - Get AI-powered advice to dominate your leagues!

The Genius is a complete fantasy sports platform that combines artificial intelligence with real sports data to help you make better fantasy decisions. Whether you're struggling with lineup choices, trade decisions, or waiver wire pickups, The Genius has you covered.

## 🏆 What Does This Do?

Think of The Genius as your personal fantasy sports consultant that:

- **Answers Questions**: "Should I start Josh Allen or Patrick Mahomes this week?"
- **Provides Analysis**: Get detailed breakdowns of player matchups and trends
- **Helps with Trades**: "Is this trade worth it?" - get unbiased AI analysis
- **Finds Sleepers**: Discover hidden gems on the waiver wire
- **Works 24/7**: Available whenever you need fantasy advice

### Who Is This For?

- **Fantasy Sports Players** who want an edge over their competition
- **Casual Fans** who need help setting lineups each week
- **Serious Players** who want data-driven analysis
- **League Commissioners** who want to add value for their members

## 🛠 How It's Built (The Simple Version)

Your project has **three main parts** that work together:

```
The Genius Project
├── 🌐 Web App (what users see)
│   └── Chat interface where people ask questions
├── 🧠 Backend API (the brain)
│   └── Connects to OpenAI's GPT-4.1 for smart answers
└── 📊 ESPN Integration (the data)
    └── Fetches real fantasy sports information
```

### 1. Web App (`/web-app`)
- **What it is**: The website people visit
- **What it does**: Provides a clean chat interface. Users can prefix messages with "search:" or use keywords like "stats", "current", "today" to have the AI perform a web search for up-to-date information.
- **Technology**: React (modern web framework)
- **Special feature**: Limits free users to 5 messages per day

### 2. Backend API (`/backend`)  
- **What it is**: The server that powers everything
- **What it does**: Takes questions and sends them to OpenAI's AI
- **Technology**: Python with FastAPI
- **Special feature**: Uses GPT-4.1 (the latest model)

### 3. ESPN Integration (`/espn-api-util`)
- **What it is**: Tools to get real fantasy data
- **What it does**: Connects to ESPN to get player stats, rosters, etc.
- **Technology**: Python with special ESPN API tools
- **Special feature**: Works with private leagues (with authentication)

## 🚀 Quick Start Guide

### Option 1: Just Want to See It Work?
If you just want to test the existing deployment:

1. **Visit the Web App**: https://genius-frontend.onrender.com
2. **Ask a Question**: "Who should I start at QB this week?"
3. **Get AI Response**: The system will analyze and respond

### Option 2: Want to Run It Yourself?
Follow these steps to get everything running on your computer:

#### Step 1: Get the Code
```bash
# 1. Download the project (if you haven't already)
git clone https://github.com/your-username/the-genius.git
cd the-genius
```

#### Step 2: Set Up the Backend
```bash
# 1. Go to the backend folder
cd backend

# 2. Create a virtual environment (keeps Python organized)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required packages
pip install -r requirements.txt

# 4. Create your environment file
cp .env.example .env
# Edit .env file and add your OpenAI API key
```

#### Step 3: Set Up the Web App
```bash
# 1. Go to the web app folder (open a new terminal)
cd web-app

# 2. Install web dependencies (one-time setup)
# Recommended: Use pnpm for faster installs
npm install -g pnpm # Install pnpm if you haven't already
pnpm install

# Alternative: If you prefer npm
# npm install

# 3. Create your environment file for the web app
# In the web-app directory, create a .env file (e.g., by copying .env.example if it exists)
# Add the following line, adjusting the URL if your backend is not local:
# VITE_BACKEND_URL=http://localhost:8000/advice
# Refer to web-app/README.md for more details on .env setup.

# 4. Start the development server
pnpm run dev # or npm run dev
```

#### Step 4: Test Everything
1. **Backend**: Visit http://localhost:8000 - should show "API is running"
2. **Frontend**: Visit http://localhost:5173 - should show the chat interface
3. **Test Chat**: Ask "Hello" - should get an AI response

## 📁 Project Structure Explained

```
the-genius/
├── 📱 web-app/                    # The website users interact with
│   ├── src/components/            # Reusable pieces (chat, messages, etc.)
│   ├── src/hooks/                 # Special logic (like daily limits)
│   ├── package.json               # Lists what the website needs
│   └── README.md                  # Detailed web app instructions
│
├── 🔧 backend/                    # The server that powers everything  
│   ├── app/                       # Main application code
│   │   ├── services/              # Connects to OpenAI
│   │   ├── models.py              # Defines data structures
│   │   └── main.py                # Main server file
│   ├── requirements.txt           # Lists what Python needs
│   └── README.md                  # Detailed backend instructions
│
├── 📊 espn-api-util/             # ESPN fantasy sports integration
│   ├── baseball_mcp/              # Baseball-specific tools
│   ├── espn_fantasy_server.py     # Main ESPN integration server
│   └── README.md                  # ESPN integration instructions
│
├── 🔄 shared-resources/          # Files used by multiple parts
└── 📖 README.md                   # This file - project overview
```

## 🌟 Key Features

### For Users
- **Chat Interface**: Simple, clean way to ask questions
- **Smart Responses**: AI analyzes your question and provides detailed advice
- **Real Data**: Pulls actual fantasy sports statistics when needed
- **Daily Limits**: Free users get 5 questions per day (encourages mobile app downloads)

### For Developers
- **Modern Stack**: React, FastAPI, OpenAI GPT-4.1
- **Easy Deployment**: Ready for Render.com hosting
- **Modular Design**: Each component can be updated independently
- **Good Documentation**: Each folder has detailed setup instructions

## 🔧 What You Need

### To Use the App
- **Nothing!** Just visit the website and start asking questions

### To Run It Yourself
- **Computer**: Mac, Windows, or Linux
- **OpenAI Account**: For the AI features (costs ~$5-20/month depending on usage)
- **Optional**: ESPN account (only needed for private league data)

### To Modify/Develop
- **Python 3.11+**: For the backend server
- **Node.js 18+**: For the web interface
- **Git**: For downloading and managing code changes
- **Text Editor**: VS Code, Cursor, or similar

## 💡 Common Use Cases

### For Fantasy Football
- "Should I start [Player A] or [Player B] at flex?"
- "Who are the best waiver wire pickups this week?"
- "Is trading my [Player X] for [Player Y] worth it?"
- "What's my team's biggest weakness?"

### For Fantasy Baseball
- "Which pitcher should I stream today?"
- "Who are the best stolen base targets on waivers?"
- "Is [Player] due for regression?"
- "Help me set my daily lineup"

## 🚀 Deployment (Making It Live)

Your project is already set up for easy deployment:

### Current Deployments
- **Backend**: https://genius-backend-nhl3.onrender.com
- **Frontend**: https://genius-frontend.onrender.com

### Deploy Your Own Version
1. **Create Render Account**: Go to render.com and sign up
2. **Connect GitHub**: Link your repository
3. **Deploy Backend**: Use the render.yaml file in /backend
4. **Deploy Frontend**: Use the render.yaml file in /web-app
5. **Add Environment Variables**: Add your OpenAI API key in Render dashboard

## 🔐 Environment Variables Needed

### For Backend (Required)
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### For ESPN Integration (Optional)
```env
ESPN_S2=your_espn_s2_cookie  # Only needed for private leagues
SWID=your_swid_cookie        # Only needed for private leagues
```

## 🆘 Troubleshooting

### Common Issues

**"Can't connect to backend"**
- Make sure the backend server is running
- Check that the URL in the web app matches your backend
- Look for error messages in the browser console (F12)

**"OpenAI API errors"**  
- Verify your API key is correct
- Check you have credits in your OpenAI account
- Make sure you're using GPT-4.1 (not older models)

**"ESPN data not working"**
- Public leagues work without authentication
- Private leagues need ESPN_S2 and SWID cookies
- Make sure league ID is correct

**"Web app won't load"**
- Try refreshing the page
- Clear browser cache
- Check if backend is running
- Look for JavaScript errors in console (F12)

### Getting Help
1. **Check the specific README** in each folder (backend/, web-app/, espn-api-util/)
2. **Look at error messages** - they usually tell you what's wrong
3. **Check the logs** - both backend and frontend show helpful information
4. **Test each part separately** - isolate where the problem is

## 📈 Usage & Costs

### OpenAI Costs (Approximate)
- **Light usage** (100 questions/day): ~$5-10/month
- **Moderate usage** (500 questions/day): ~$15-25/month  
- **Heavy usage** (1000+ questions/day): ~$30-50/month

### Hosting Costs (Render.com)
- **Free tier**: Good for testing and light usage
- **Paid tier**: $7-25/month for production apps

## 🔮 Future Ideas

### Easy Additions
- **User Accounts**: Let people save their questions and get more messages
- **More Sports**: Add basketball, hockey, soccer fantasy support
- **Mobile App**: Native iOS/Android apps
- **Premium Features**: Advanced analytics for paid users

### Advanced Features
- **Real-time Updates**: Live player news and injury reports
- **League Integration**: Directly connect to your fantasy leagues
- **Custom Strategies**: AI learns your preferences over time
- **Social Features**: Share advice with league mates

## 📄 License

This project is open source and available under the MIT License. Feel free to use, modify, and distribute as needed.

## 🏗 Contributing

This is designed as a solo developer project, but contributions are welcome:

1. **Fork the repository**
2. **Create a feature branch** 
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

## 📞 Support

For questions or issues:
1. Check the README in the specific folder you're working with
2. Look at the troubleshooting section above
3. Check the GitHub issues page
4. Contact the maintainer

---

**Built with ❤️ for fantasy sports enthusiasts everywhere!**

*Ready to dominate your leagues? Let's get started!*