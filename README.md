# FantasyAI - AI-Powered Fantasy Sports Assistant

FantasyAI is a fantasy sports advice platform that leverages OpenAI's GPT models to provide personalized fantasy sports recommendations and insights.

## Project Overview

This platform consists of several integrated components that work together to deliver AI-driven fantasy sports advice:

- **AI-powered advice engine** - Uses OpenAI's GPT-4.1 to analyze player stats and provide fantasy sports guidance
- **ESPN Fantasy data integration** - Connects to ESPN fantasy leagues to retrieve team rosters, player stats, and league information
- **iOS application** - Mobile interface for interacting with the AI assistant
- **RESTful backend API** - Handles requests between the frontend applications and AI/data services

## Project Structure

```
fantasy-ai/
├── backend/               # FastAPI backend server for AI interactions
├── espn-api-util/         # ESPN Fantasy API integration tools
├── ios-app/               # iOS mobile application (Swift/SwiftUI)
├── shared-resources/      # Shared assets and configurations
└── web-app/               # Web application frontend (planned)
```

## Components

### Backend

The backend is a FastAPI application that serves as the bridge between the frontend and OpenAI's services:

- Uses OpenAI's Responses API with GPT-4.1 by default
- Provides endpoints for getting AI-powered fantasy sports advice
- Containerized with Docker for easy deployment
- Connects to sports statistics data sources

### ESPN API Utility

The ESPN API utility is a Model Context Protocol (MCP) server that provides a standardized interface for accessing fantasy football data:

- Authentication and secure credential management for private leagues
- League information retrieval
- Team roster and player statistics
- Matchup data and league standings
- Designed to work with Claude Desktop through the MCP protocol

### iOS Application

The iOS app provides the primary user interface for the service:

- Built with Swift/SwiftUI for iOS devices
- Interactive chat interface for getting fantasy advice
- Will support ESPN fantasy team imports (premium feature)

### Web Application

A web interface is planned for future development to allow access from any browser.

## Getting Started

### Prerequisites

- Python 3.11+ (for backend and ESPN API)
- Docker (for containerized deployment)
- Xcode 14+ (for iOS development)
- OpenAI API key with access to GPT-4.1
- Apple Developer account (for iOS app deployment)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

4. Run the development server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

5. Alternatively, build and run with Docker:
   ```bash
   docker build -t fantasy-backend .
   docker run -p 8080:8080 --env-file .env fantasy-backend
   ```

### ESPN API Utility Setup

1. Navigate to the ESPN API utility directory:
   ```bash
   cd espn-api-util
   ```

2. Install dependencies:
   ```bash
   uv pip install -e .
   ```

3. Run the MCP server:
   ```bash
   uv run espn_fantasy_server.py
   ```

## API Usage

### Getting Fantasy Advice

```bash
# Get advice using the default GPT-4.1 model
curl -X POST "http://localhost:8080/advice" \
  -H "Content-Type: application/json" \
  -d '{"conversation":[{"role":"user","content":"Should I start Patrick Mahomes or Josh Allen this week?"}]}'

# Get advice using a specific model
curl -X POST "http://localhost:8080/custom-advice?model=gpt-4o" \
  -H "Content-Type: application/json" \
  -d '{"conversation":[{"role":"user","content":"Should I trade for Christian McCaffrey?"}]}'
```

## Development Roadmap

Based on the project structure and roadmap document:

1. ✅ Backend API development
2. ✅ ESPN API integration
3. 🔄 iOS app development (in progress)
4. 📅 In-app purchase implementation for premium features
5. 📅 Web application development
6. 📅 Performance optimizations and scaling

## Technology Stack

- **Backend**: FastAPI, Python, OpenAI API, Docker
- **ESPN Integration**: Python, MCP protocol, espn-api package
- **iOS App**: Swift, SwiftUI, StoreKit for in-app purchases
- **Data Sources**: ESPN Fantasy API, pybaseball

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please contact the project maintainer at gerald.gugger@gmail.com.
