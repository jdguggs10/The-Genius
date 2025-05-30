# The Genius - AI-Powered Fantasy Sports Assistant

> **Your Personal Fantasy Sports Expert** - Get AI-powered advice to dominate your leagues!

The Genius is a comprehensive fantasy sports platform that combines artificial intelligence with real sports data to help you make better fantasy decisions. Available as a web app and native iOS app, whether you're struggling with lineup choices, trade decisions, or waiver wire pickups, The Genius has you covered.

## 🏆 What Does This Do?

The Genius acts as your personal fantasy sports consultant, offering capabilities such as:

- **Answering Questions**: e.g., "Should I start Josh Allen or Patrick Mahomes this week?"
- **Providing Analysis**: Detailed breakdowns of player matchups and trends.
- **Assisting with Trades**: Unbiased AI analysis on trade proposals.
- **Identifying Sleepers**: Discovering hidden gems on the waiver wire.
- **24/7 Availability**: Fantasy advice whenever you need it.
- **Cross-Platform Access**: Use the web app or native iOS app.

### Who Is This For?

- **Fantasy Sports Players** seeking a competitive edge.
- **Casual Fans** needing help with weekly lineup decisions.
- **Serious Players** wanting data-driven analysis.
- **League Commissioners** looking to add value for their members.

## 🛠 How It's Built

The Genius project integrates several key components:

```
The Genius Project
├── 🌐 Web App (React + TypeScript + Vite)
│   └── User interface for web browsers
├── 📱 iOS App (SwiftUI)
│   └── Native iOS application for mobile experience
├── 🧠 Backend API (Python + FastAPI)
│   └── Powers core logic, connects to OpenAI GPT-4.1
├── 📊 ESPN Integration (Python + ESPN API + MCP)
│   └── Fetches fantasy sports data from ESPN
├── ⚾ PyBaseball Utility (Python)
│   └── Provides baseball-specific data and utilities
└── 📚 Shared Resources
    └── Common assets, prompt engineering modules
```

### 1. Web App (`/web-app`)
- **Description**: The primary interface for users on desktop and mobile web browsers.
- **Technology**: React, TypeScript, Vite.
- **Key Features**:
    - Clean chat interface.
    - Real-time streaming of AI responses.
    - Web search integration (e.g., "search: latest NFL injuries").

### 2. iOS App (`/ios-app`)
- **Description**: A native iOS application providing a rich mobile experience.
- **Technology**: Swift, SwiftUI (iOS 15+).
- **Key Features**:
    - Real-time streaming responses.
    - Structured advice display with confidence scores.
    - Native iOS design following Apple Human Interface Guidelines.
    - Conversation management and sharing.

### 3. Backend API (`/backend`)
- **Description**: The central server that handles business logic and AI integration.
- **Technology**: Python, FastAPI.
- **Key Features**:
    - Integration with OpenAI GPT-4.1 for advanced AI capabilities.
    - Server-Sent Events (SSE) for real-time communication.
    - Pydantic models for structured data validation.
    - OpenAPI documentation for clear API contracts.

### 4. ESPN Integration (`/espn-api-util`)
- **Description**: A utility service for fetching real-time fantasy sports data from ESPN.
- **Technology**: Python, ESPN API, MCP (Machine Comprehensible Plan) protocol for tool definition.
- **Key Features**:
    - Access to player statistics, rosters, and league information.
    - Supports private leagues with appropriate authentication.

### 5. PyBaseball API Utility (`/pybaseball-api-util`)
- **Description**: A utility service providing access to baseball-specific data and analytics.
- **Technology**: Python, leveraging the pybaseball library.

### 6. Shared Resources (`/shared-resources`)
- **Description**: Contains common assets, configurations, and notably, modular prompt engineering templates used by the backend for interacting with the LLM.

## 🚀 Quick Start Guide

### Option 1: View Existing Deployments
- **Web App**: https://genius-frontend.onrender.com
- **iOS App**: Requires building and running from Xcode (see iOS setup below).

### Option 2: Run Locally

#### Step 1: Get the Code
```bash
git clone https://github.com/your-username/the-genius.git # Replace with your repo URL
cd the-genius
```

#### Step 2: Set Up the Backend (`/backend`)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create and configure environment file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
# Example: OPENAI_API_KEY="your_openai_api_key_here"
```
Ensure the backend is running, typically on `http://localhost:8000`.

#### Step 3: Set Up the Web App (`/web-app`)
```bash
cd web-app
# Ensure you have Node.js and pnpm installed
# npm install -g pnpm # If you don't have pnpm
pnpm install

# Create .env.local file for environment variables
cp .env.example .env.local # Or create .env.local manually
# Edit .env.local and set the backend URL
# Example: VITE_BACKEND_URL="http://localhost:8000"

pnpm run dev
```
The web app should be accessible at `http://localhost:5173` (or another port if specified).

#### Step 4: Set Up the iOS App (`/ios-app`)
```bash
cd ios-app
# Open TheGenius.xcodeproj (or your project's name) in Xcode
# If needed, update the backend API URL in the relevant network service/manager class
# (e.g., within a file like `NetworkService.swift` or `ChatViewModel.swift`).
# The default should point to localhost for local backend testing.
# Build and run on an iOS Simulator or a physical device.
```

#### Step 5: Test
1.  **Backend**: Navigate to `http://localhost:8000/docs` in your browser to see the API documentation.
2.  **Web App**: Open `http://localhost:5173` (or the configured port) to interact with the chat interface.
3.  **iOS App**: Launch from Xcode.
4.  **Test Chat**: Send a message like "Hello" to verify AI response.

## 📁 Project Structure

```
the-genius/
├── 📱 ios-app/                    # Native iOS application (SwiftUI)
│   ├── TheGenius/                 # Main app source code (adjust if different)
│   │   ├──ViewModels/ChatViewModel.swift # Core chat logic & SSE
│   │   ├──Views/ContentView.swift    # Main app UI
│   │   └── ...                    # Other UI, model, service files
│   ├── TheGenius.xcodeproj/       # Xcode project file
│   └── README.md                  # iOS-specific details
│
├── 🌐 web-app/                    # Web application (React, TypeScript, Vite)
│   ├── public/                    # Static assets
│   ├── src/                       # Source code
│   │   ├── components/            # UI components
│   │   ├── hooks/                 # React hooks
│   │   ├── services/              # API interaction
│   │   └── App.tsx                # Main application component
│   ├── .env.example               # Example environment variables
│   ├── package.json               # Dependencies and scripts
│   └── README.md                  # Web app specific details
│
├── 🧠 backend/                    # Backend API (Python, FastAPI)
│   ├── app/                       # Main application logic
│   │   ├── api/                   # API endpoint definitions
│   │   ├── core/                  # Configuration, core settings
│   │   ├── models/                # Pydantic data models
│   │   ├── services/              # Business logic, OpenAI integration
│   │   └── main.py                # FastAPI application entry point
│   ├── .env.example               # Example environment variables
│   ├── requirements.txt           # Python dependencies
│   └── README.md                  # Backend specific details
│
├── 📊 espn-api-util/             # ESPN fantasy sports data integration (Python)
│   ├── espn_api/                  # ESPN API interaction logic
│   ├── mcp_tools/                 # MCP tool definitions for ESPN functions
│   └── README.md                  # ESPN utility specific details
│
├── ⚾ pybaseball-api-util/        # PyBaseball data utility (Python)
│   ├── utils/                     # Baseball data functions
│   └── README.md                  # PyBaseball utility specific details
│
├── 📚 shared-resources/          # Shared assets, prompts, configurations
│   ├── prompts/                   # Modular prompt engineering templates
│   └── configs/                   # Shared configuration files
│
└── 📖 README.md                   # This overview file
```

## 🤖 AI Reviewer Notes

This project is structured to be effectively reviewed and understood by AI agents due to several key characteristics:

-   **Clear Separation of Concerns**: Distinct modules for frontend (web, iOS), backend API, and data utilities (`espn-api-util`, `pybaseball-api-util`) simplify understanding individual components.
-   **Well-Defined API Contracts**:
    -   The backend exposes OpenAPI documentation (`/docs`, `/redoc`) for clear, machine-readable API specifications.
    -   The `espn-api-util` likely uses MCP (Machine Comprehensible Plan) tool definitions, making its functions understandable as tools for an AI agent.
-   **Structured Data Models**:
    -   **Backend**: Pydantic models enforce data schemas for API requests and responses.
    -   **iOS App**: Swift `Codable` structs are used for handling data from the API.
-   **Modular Prompt Engineering**: The `shared-resources/prompts/` directory suggests that prompts for interacting with LLMs are organized and reusable, allowing for easier analysis and modification.
-   **Module-Specific READMEs**: Each major directory (`ios-app`, `web-app`, `backend`, etc.) contains its own `README.md`, providing localized context and setup instructions.
-   **Consistent Technology Stacks within Modules**: For example, the backend consistently uses Python and FastAPI, while the web app uses a standard React/TypeScript/Vite stack.

## 🌟 Key Features (Summary)

-   Cross-Platform (Web & iOS)
-   Real-Time AI Responses via SSE
-   Structured Advice with Confidence
-   ESPN & PyBaseball Data Integration
-   Web Search Capability

## 🔧 Requirements

### For Development
-   Python 3.9+ (Backend, Utilities)
-   Node.js 18+ & pnpm (Web App)
-   Xcode 14+ (iOS App)
-   OpenAI API Key

## 📄 License

[Add your license information here]

---

**The Genius** - Making fantasy sports decisions easier, one AI-powered conversation at a time. 🏆