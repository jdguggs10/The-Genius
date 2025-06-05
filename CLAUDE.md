# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**The Genius** is an AI-powered fantasy sports assistant that provides intelligent advice through web, iOS, and API interfaces. It combines OpenAI's GPT-4.1 models with real sports data via ESPN and PyBaseball integrations.

## Architecture

### Core Components
- **Backend API** (`/backend/`): Python FastAPI server with OpenAI integration, structured JSON responses, SSE streaming
- **Web App** (`/web-app/`): React 19 + TypeScript + Vite + Tailwind CSS v4 PWA
- **iOS App** (`/ios-app/`): SwiftUI native app with ESPN login integration
- **ESPN Integration** (`/espn-api-util/`): MCP server for fantasy baseball data
- **PyBaseball Integration** (`/pybaseball-api-util/`): MCP server for MLB statistics
- **Shared Resources** (`/shared-resources/`): Modular prompt system and static data

### Key Technologies
- **AI**: OpenAI GPT-4.1-mini with structured JSON output using Pydantic schemas
- **Backend**: FastAPI, SQLAlchemy, Server-Sent Events for real-time streaming
- **Frontend**: React 19, Tailwind CSS v4 (Oxide engine), DaisyUI components
- **Mobile**: SwiftUI, iOS 16.0+, PhotosPicker for image attachments
- **Data**: ESPN API, PyBaseball library, MCP (Model Context Protocol)

## Common Development Commands

### Backend Development
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python -m pytest tests/ -v
```

### Web App Development
```bash
cd web-app
pnpm install

# Development (auto-connects to localhost:8000)
pnpm run dev

# Development with production backend
pnpm run dev:prod-backend

# Build and preview
pnpm run build
pnpm run preview

# Linting
pnpm run lint
pnpm run lint:fix
```

### iOS Development
```bash
# Open in Xcode
open ios-app/ios-app.xcodeproj

# For local development, edit ApiConfiguration.swift:
# Uncomment: return localBackendURL
# Comment: return productionBackendURL
```

### ESPN/PyBaseball MCP Servers
```bash
# ESPN integration
cd espn-api-util
./setup.sh
./start_baseball_mcp.sh

# PyBaseball integration  
cd pybaseball-api-util
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./start_pybaseball_mcp_claude.sh
```

## Environment Configuration

The project features **automatic environment detection**:
- **Development**: Automatically uses `localhost:8000`
- **Production**: Automatically uses `https://genius-backend-nhl3.onrender.com`
- **No manual URL switching required**

## Key Architectural Patterns

1. **Structured AI Responses**: All OpenAI responses use Pydantic models with JSON schema validation
2. **Real-time Streaming**: SSE implementation for progressive response delivery across all clients
3. **Modular Prompt System**: Markdown-based prompts in `/shared-resources/prompts/` organized by sport and function
4. **MCP Integration**: Standardized AI tool protocol for external data access
5. **Response Tracking**: iOS app uses `previous_response_id` for multi-turn conversation context
6. **Cross-platform State Management**: Consistent data models between web, iOS, and API

## Testing Commands

```bash
# Backend tests
cd backend && python -m pytest tests/ -v

# Web app linting (no Jest tests currently)
cd web-app && pnpm run lint

# iOS tests
cd ios-app && xcodebuild test -scheme ios-app -destination 'platform=iOS Simulator,name=iPhone 15'
```

## Deployment

- **Backend**: Auto-deploys to Render.com via GitHub integration
- **Web App**: Auto-connects to production backend, deploys to Render
- **iOS App**: Archive for App Store distribution via Xcode