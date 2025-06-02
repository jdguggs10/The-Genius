# The Genius - Fantasy Sports AI Web App

> **The Face of Your AI Assistant** - A modern, clean chat interface where users get expert fantasy sports advice

This frontend web application is the primary interaction point for users with The Genius AI. It provides a beautiful, mobile-friendly chat interface for asking fantasy sports questions and receiving intelligent, AI-powered responses.

## 🌟 Core Features

- **Intuitive Chat Interface**: Simple, WhatsApp-style messaging.
- **AI-Powered Advice**: Connects to the backend API for intelligent responses.
- **Real-time Streaming**: Messages stream via WebSockets/SSE for a fluid experience.
- **Enhanced UX & Performance**:
    - **Virtualized Message List**: `react-window` ensures smooth scrolling with long conversations.
    - **Skeleton Loaders**: Placeholders improve perceived performance during AI response generation.
    - **Scroll Management**: "New messages" chip for easy navigation.
    - **Message Actions**: One-click copy for message content.
    - **User & AI Avatars**: Clear visual distinction in chat.
- **Theming**: User-selectable light, dark, and system-preference themes.
- **Accessibility (A11y)**:
    - Semantic HTML (`role="log"`) and dynamic ARIA labels for screen readers.
    - Auto-focus on input field.
    - Respects reduced motion preferences.
- **PWA Capabilities**: Installable as a Progressive Web App with offline asset caching.
- **Robust Error Handling**: React Error Boundary for UI issues; toast notifications for operational errors.
- **Web Search Detection**: Automatically enables web search for queries requiring current stats.
- **Mobile-First Design**: Responsive across all device sizes.
- **Daily Usage Limits**: Tracks free user message quotas.

## 🎯 Target Audience

- **Fantasy Sports Players**: Seeking quick advice on lineups, trades, and pickups.
- **Casual Fans**: Needing help with complex fantasy decisions.
- **Mobile Users**: Preferring a simple chat interface.
- **Website Visitors**: The primary way users interact with the AI assistant.

## 🔧 Technology Stack

- **Core**: React 19, TypeScript, Vite, pnpm
- **Styling & UI**: DaisyUI, Tailwind CSS, Heroicons, Framer Motion (for animations)
- **Key Libraries**:
    - `react-window` (Virtualized lists)
    - `react-hot-toast` (Notifications)
    - `@vite-pwa/plugin` (PWA support)
    - `react-markdown` (Markdown rendering for AI responses)
- **Custom Hooks**: For WebSocket/SSE (`useChatSocket`, `useSSEClient`), daily quota (`useDailyQuota`), scroll behavior (`useScrollAnchor`), theme (`useTheme`), and conversation management (`useConversationManager`).

## 📁 Project Structure

```
web-app/
├── public/                      # Static files (icons, PWA manifest assets)
│   └── icons/                   # PWA related icons
├── src/                         # Source code
│   ├── assets/                  # Static assets like images, svgs (if any, not explicitly listed before but common)
│   ├── components/              # Reusable UI components
│   │   ├── chat.tsx             # Main chat interface logic and layout
│   │   ├── MessageDaisyUI.tsx   # Individual chat message rendering using DaisyUI
│   │   ├── SkeletonMessage.tsx  # Loading placeholder for messages
│   │   └── ChatErrorBoundary.tsx# Catches React rendering errors in the chat
│   ├── hooks/                   # Custom React Hooks for reusable logic
│   │   ├── useChatSocket.ts     # Manages WebSocket connection and streaming
│   │   ├── useSSEClient.ts      # Manages Server-Sent Events connection
│   │   ├── useDailyQuota.ts     # Manages 5-message daily limit (example)
│   │   ├── useScrollAnchor.ts   # Advanced scroll management for chat
│   │   ├── useTheme.ts          # Handles theme (light/dark/system)
│   │   └── useConversationManager.ts # Manages conversation state (messages, etc.)
│   ├── App.tsx                  # Main application component, sets up routing (if any) and global providers
│   ├── main.tsx                 # App entry point (initializes React, Toaster, Error Boundary)
│   ├── types/index.ts           # TypeScript type definitions
│   ├── index.css                # Global styles, Tailwind imports, dark mode base
│   └── vite-env.d.ts            # TypeScript definitions for Vite environment variables
├── .env.example                 # Example environment variables file
├── .gitignore                   # Specifies intentionally untracked files
├── package.json                 # Project metadata, dependencies, and scripts
├── pnpm-lock.yaml               # Exact versions of dependencies
├── vite.config.ts               # Vite configuration (build, server, plugins like VitePWA)
├── tailwind.config.js           # Tailwind CSS configuration
├── postcss.config.js            # PostCSS configuration (often for Tailwind/Autoprefixer)
├── tsconfig.json                # Base TypeScript configuration for the project
├── tsconfig.app.json            # TypeScript configuration for the application build
├── tsconfig.node.json           # TypeScript configuration for Node.js scripts (e.g., vite.config.ts)
├── eslint.config.js             # ESLint configuration for code linting
├── .stylelintrc.json            # Stylelint configuration for CSS linting
├── render.yaml                  # Deployment configuration for Render.com
└── README.md                    # This guide
```

## 🚀 Quick Start Guide

### Step 1: Environment Setup

1.  **Install Node.js**:
    - Go to [nodejs.org](https://nodejs.org), download and install the LTS version.
    - Verify: `node --version` (v18+ recommended), `npm --version`.
2.  **Enable Corepack & Install pnpm**:
    (Corepack is included with Node.js v16.9+)
    ```bash
    corepack enable
    corepack prepare pnpm@latest --activate
    pnpm --version # Verify pnpm installation
    ```
    If you prefer global install (and don't have Corepack or older Node): `npm install -g pnpm`.

### Step 2: Get Code & Install Dependencies

```bash
# 1. Navigate to the web-app folder
cd web-app

# 2. Install dependencies
pnpm install
```

### Step 3: Configure Environment Variables

1.  In the `web-app` directory, create a `.env` file. You can copy `web-app/.env.example` if it exists.
    ```bash
    cp .env.example .env  # If .env.example exists
    ```
2.  Edit `.env` with your backend URLs. See the "Environment Variables" section below for details.

Example `web-app/.env`:
```env
VITE_BACKEND_URL=http://localhost:8000
VITE_BACKEND_WS_URL=ws://localhost:8000/chat
# VITE_DEFAULT_MODEL_ID= (Optional) Specify a default model ID
```

### Step 4: Start the Development Server

```bash
# Start dev server (connects to backend specified by VITE_BACKEND_URL, default http://localhost:8000)
pnpm run dev

# Or, to connect to the production backend for development:
# pnpm run dev:prod-backend

# Output should show:
# VITE vX.X.X ready in XXX ms
# ➜ Local:   http://localhost:5173/ (or similar port)
```

### Step 5: Test

1.  Open your browser to the local URL (e.g., `http://localhost:5173`).
2.  Verify the chat interface loads.
3.  Test sending a message.
4.  Confirm daily message counter updates (if applicable).

## 🌱 Environment Variables

The application uses Vite to manage environment variables. Variables prefixed with `VITE_` are exposed to the client-side code. Create a `.env` file in the `web-app` root:

-   `VITE_BACKEND_URL`: (Required) The base HTTP URL for your backend API.
    -   Example: `http://localhost:8000` or `https://your-backend-api.com`
    -   Used for initial calls like fetching default model, etc.
-   `VITE_BACKEND_WS_URL`: (Required) The WebSocket URL for real-time chat.
    -   Example: `ws://localhost:8000/chat` or `wss://your-backend-api.com/chat`
    -   Used by `useChatSocket.ts` or `useSSEClient.ts`.
-   `VITE_DEFAULT_MODEL_ID`: (Optional) The ID of the default model to be used if not otherwise specified.
    -   Example: `claude-3-opus-20240229`
-   `NODE_ENV`: Set automatically by Vite scripts (`development` or `production`).

## ✨ Features Deep Dive & Core Components

This section highlights key components and hooks that form the core of the application.

### Core Components (`src/components/`)
-   `chat.tsx`: The heart of the user interface. Manages message state, user input, and orchestrates interactions with hooks for sending/receiving messages, handling scroll, and themes.
-   `MessageDaisyUI.tsx`: Renders individual chat messages with appropriate styling for user vs. AI, avatars, and message actions (like copy). Leverages DaisyUI for chat bubble styling.
-   `SkeletonMessage.tsx`: Provides a loading state UI for messages while the AI is generating a response, enhancing perceived performance.
-   `ChatErrorBoundary.tsx`: A React error boundary specifically for the chat interface to catch and handle rendering errors gracefully, preventing the entire app from crashing.

### Custom Hooks (`src/hooks/`)
-   `useChatSocket.ts` / `useSSEClient.ts`: Manage the real-time connection (WebSocket or SSE respectively) to the backend for sending user messages and receiving streamed AI responses. Handles connection state, message parsing, and error handling.
-   `useConversationManager.ts`: Likely responsible for managing the state of the conversation, including the list of messages, adding new messages, and potentially other conversation-related metadata.
-   `useDailyQuota.ts`: Implements the client-side logic for tracking the user's daily message quota, typically using `localStorage`.
-   `useScrollAnchor.ts`: Provides advanced scroll management for the chat list. Ensures that the view stays anchored correctly as new messages are added or when the user scrolls up. Includes features like a "new messages" indicator.
-   `useTheme.ts`: Manages the application's theme (light, dark, system preference). Persists the selected theme, often using `localStorage`, and applies the necessary changes to the UI.

### State Management
The application primarily uses React's built-in state management (e.g., `useState`, `useReducer`) within components and custom hooks. For shared state like messages or theme, it relies on these custom hooks to encapsulate and provide logic, which can be consumed by multiple components. This approach keeps complexity low for the current scale.

## 🛠 Development Guide

### Available `pnpm` Scripts

-   `pnpm run dev`: Starts the development server with hot reloading. Connects to backend defined by `VITE_BACKEND_URL` (defaults to `http://localhost:8000`).
-   `pnpm run dev:prod-backend`: Starts dev server, but connects to the production backend URL.
-   `pnpm run build`: Compiles TypeScript and builds the application for production (outputs to `dist/`).
-   `pnpm run build:local`: Builds for production using `http://localhost:8000` as the backend URL.
-   `pnpm run preview`: Serves the production build locally for testing.
-   `pnpm run preview:local-backend`: Builds with local backend URL and serves it.
-   `pnpm run lint`: Runs ESLint to check for code quality and style issues.
-   `pnpm run test`: Runs unit and component tests using Vitest in watch mode.
-   `pnpm run test:run`: Runs tests once without watching.

Refer to `package.json` for the exact commands and environment variables used.

### Making Changes
-   **UI/Component Logic**: Edit files in `src/components/` or `src/hooks/`.
-   **Styling**: Modify Tailwind classes in components or global styles in `src/index.css`.
-   **Daily Limits**: Adjust logic in `src/hooks/useDailyQuota.ts`.

### Example: Adding a "Clear Chat" Button
(This example remains relevant; ensure paths are current if attempting)
1.  Modify `src/components/chat.tsx`:
    ```typescript
    // Inside the Chat component:
    // Presuming messages are managed by a hook like useConversationManager:
    // import { useConversationManager } from '../hooks/useConversationManager';
    // const { clearMessages } = useConversationManager(); // Or however it's exposed

    const handleClearChat = () => {
      // setMessages([]); // If using local state
      // clearMessages(); // If using a manager hook
    };

    // In JSX:
    <button
      onClick={handleClearChat}
      className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm"
    >
      Clear Chat
    </button>
    ```
2.  Test and style as needed.

## ✅ Testing

The project uses [Vitest](https://vitest.dev/) for unit and component testing. Test files are co-located with the source files (e.g., `chat.test.tsx` alongside `chat.tsx`).

-   **Run tests (watch mode)**: `pnpm run test`
-   **Run tests (single run)**: `pnpm run test:run`

Testing libraries include:
-   `@testing-library/react` for rendering components and interacting with them.
-   `@testing-library/jest-dom` for custom DOM assertions.
-   `jsdom` to simulate a browser environment for tests.

Write tests for new components and hooks to ensure reliability.

## 💅 Linting and Formatting

-   **ESLint**: For JavaScript/TypeScript linting. Configuration in `eslint.config.js`.
    -   Run: `pnpm run lint`
-   **Stylelint**: For CSS and Tailwind CSS linting. Configuration in `.stylelintrc.json`. (Run via editor integration or `npx stylelint "**/*.css"`)
-   **TypeScript**: The `build` script (`tsc --project tsconfig.app.json`) also performs type checking.

It's recommended to integrate these linters with your code editor for real-time feedback and auto-formatting on save if possible.

## 🚀 Deployment

The application is configured for deployment on [Render.com](https://render.com/) via the `render.yaml` file.

**General Build Process**:
1.  Ensure your `.env` file (or environment variables in your deployment service) has the correct production `VITE_BACKEND_URL` and `VITE_BACKEND_WS_URL`.
2.  The `pnpm run build` script will:
    -   Run TypeScript checks (`tsc`).
    -   Build the application using Vite, outputting static assets to the `web-app/dist` directory.
3.  Deploy the contents of the `web-app/dist` directory as a static site.

Refer to `render.yaml` for specific build and start commands used by Render.

## 📜 PWA (Progressive Web App)

This app is a PWA, enabled by `vite-plugin-pwa`. This allows users to "install" the web app to their home screen on mobile devices or as a desktop app for an app-like experience. It also enables caching of assets for faster load times and some offline capabilities.

**Installation**:
-   **Desktop (Chrome/Edge)**: Look for an install icon (often a computer with a down arrow) in the address bar.
-   **Mobile (iOS/Android)**: Use the "Add to Home Screen" option in the browser's share menu.

The plugin is configured in `vite.config.ts`.

## 🤝 Contributing

(Placeholder: Add guidelines if this becomes a collaborative project)
-   Follow existing coding style.
-   Write tests for new features.
-   Update documentation as needed.

## 📄 License

(Placeholder: Specify a license, e.g., MIT, if applicable)

---

*This README was last updated on [Current Date]. It aims to provide a comprehensive overview for developers working on The Genius web application.*