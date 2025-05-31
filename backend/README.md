# Fantasy AI Backend

> **The Brain Behind The Genius** - FastAPI server that powers your fantasy sports AI assistant with structured, streaming JSON responses.

This is the backend API server that handles the core logic for "The Genius" application. It receives requests from client applications (web and iOS), interacts with the OpenAI API (defaulting to `o4-mini`) to generate fantasy sports advice, and returns this advice in a structured JSON format, with options for both streaming and non-streaming responses.

## 🧠 What This Does

This backend server:
- **Receives Questions**: Gets fantasy sports questions from your web app or mobile app via a JSON payload.
- **Talks to AI**: Sends questions to OpenAI's API (defaulting to `o4-mini`), requesting structured JSON output.
- **Streams Structured Answers**: Provides an endpoint (`/advice`) that streams fantasy sports advice. The advice is formatted as a single JSON object (`StructuredAdvice` model) delivered in chunks, enabling progressive display on the client-side.
- **Offers Non-Streaming Option**: Includes an endpoint (`/advice-non-streaming`) for clients that prefer to receive the complete structured JSON response in a single payload.
- **Manages Configuration**: Utilizes environment variables for sensitive information like API keys and configurable parameters like system prompts.
- **Handles Cross-Origin Resource Sharing (CORS)**: Configured to allow requests from specified client application origins.

## 🔧 Technology Stack (What's Under the Hood)

- **FastAPI**: A modern, high-performance Python web framework used for building the API.
- **OpenAI API (GPT models)**: Primarily utilizes `o4-mini` by default for generating intelligent advice. Configured to leverage OpenAI's structured JSON response capabilities.
    - **IMPORTANT NOTE**: The default AI model is `o4-mini`. This model is specified for cost and performance reasons. Do not change this to a different model (e.g., GPT-4 Turbo) without explicit instruction and consideration of implications.
- **Pydantic**: Used for data validation, settings management, and defining the JSON schemas that are passed to OpenAI to ensure structured responses.
- **Uvicorn**: An ASGI (Asynchronous Server Gateway Interface) web server, used for running the FastAPI application in production.
- **Docker**: Enables containerization of the application for consistent deployment environments.
- **Render.com**: The primary platform for cloud hosting and deployment of this backend service.
- **Python 3.11+**: The programming language used.

## 📁 Project Structure

```
backend/
├── app/                           # Main application source code
│   ├── services/                  # Modules for interacting with external services
│   │   └── openai_client.py       # Handles all communication with OpenAI API, including prompt construction, streaming, and structured JSON response enforcement.
│   ├── models.py                  # Defines Pydantic models for API request/response bodies and the schema for OpenAI's structured JSON output.
│   └── main.py                    # FastAPI application entry point, defining API routes, request handlers, and global configurations (e.g., CORS).
├── tests/                         # Automated tests
│   ├── test_main.py               # Endpoint tests
│   ├── test_openai_client.py      # Tests for OpenAI integration logic
│   └── ...                        # Other test files
├── .env.example                   # Example environment variables file
├── requirements.txt               # Core Python dependencies for the application
├── requirements-dev.txt           # Additional dependencies for development and testing
├── Dockerfile                     # Defines the Docker image for containerized deployment
├── render.yaml                    # Configuration file for deployment on Render.com
└── README.md                      # This documentation file
```

## 🚀 Quick Start Guide

### Step 1: Prerequisites
- **Python 3.11 or newer**: Download from [python.org](https://python.org).
- **OpenAI API Key**:
    1.  Go to [platform.openai.com](https://platform.openai.com).
    2.  Sign up or log in.
    3.  Navigate to "API Keys" and create a new secret key.
    4.  Ensure your OpenAI account has sufficient credits/quota.

### Step 2: Setup

```bash
# Navigate to the backend directory (if not already there)
# cd path/to/the-genius/backend

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# For development, also install testing dependencies:
pip install -r requirements-dev.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the `backend` directory. You can copy the example file first:
```bash
cp .env.example .env
```
Then, edit the `.env` file with your actual credentials and any desired optional settings:
```env
# Required: Your OpenAI API Key
OPENAI_API_KEY=sk-your_actual_openai_key_here

# Optional: System prompt (how the AI should behave)
# This is combined with JSON schema instructions in openai_client.py
SYSTEM_PROMPT="You are a helpful fantasy sports assistant with deep knowledge of player performance, matchups, and strategy. You MUST respond in JSON format adhering to the provided schema."

# Optional: Override the default OpenAI model (defaults to o4-mini if not set)
# OPENAI_DEFAULT_MODEL="o4-mini"
```

### Step 4: Run the Development Server
```bash
# From the 'the-genius/backend' directory, with venv activated:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Test
1.  **API Welcome Page**: Open `http://localhost:8000` in your browser.
2.  **Interactive API Docs (Swagger UI)**: Open `http://localhost:8000/docs`.
3.  **Streaming Advice Endpoint**:
    ```bash
    curl -N -X POST "http://localhost:8000/advice" \
      -H "Content-Type: application/json" \
      -d '{
        "conversation": [
          {"role": "user", "content": "Should I start Patrick Mahomes or Josh Allen this week?"}
        ],
        "model": "o4-mini"
      }'
    ```
4.  **Non-Streaming Advice Endpoint**:
    ```bash
    curl -X POST "http://localhost:8000/advice-non-streaming" \
      -H "Content-Type: application/json" \
      -d '{
        "conversation": [
          {"role": "user", "content": "Who are the top 3 waiver wire pickups for WR this week?"}
        ],
        "model": "o4-mini"
      }'
    ```

## API Endpoints

### 1. `GET /`
- **Description**: A simple HTML welcome page indicating the API is operational.
- **Response**: HTML content.

### 2. `GET /health`
- **Description**: Provides a health check for the API.
- **Response (`application/json`)**: `{"status": "healthy", "version": "x.y.z"}` (version from app settings)

### 3. `POST /advice`
- **Description**: The primary endpoint for obtaining AI-generated fantasy sports advice. The response is streamed as newline-delimited JSON chunks, which together form a single `StructuredAdvice` JSON object. Clients should accumulate these chunks.
- **Request Body (`AdviceRequest`)**:
  ```json
  {
    "conversation": [
      {"role": "user", "content": "Your question here"},
      {"role": "assistant", "content": "Previous AI response (if any)"},
      {"role": "user", "content": "Follow-up question"}
    ],
    "model": "o4-mini", // Optional: Defaults to OPENAI_DEFAULT_MODEL or o4-mini
    "enable_web_search": false // Optional: Feature flag, currently not fully utilized with structured JSON mode
  }
  ```
- **Response Stream (`application/x-ndjson` leading to `StructuredAdvice`)**:
  Chunks of a JSON object. Concatenated example:
  ```json
  {
    "main_advice": "Start Josh Allen.",
    "reasoning": "Allen has a better matchup and higher recent performance.",
    "confidence_score": 0.8,
    "alternatives": [{"player": "Patrick Mahomes", "reason": "Solid floor but tougher matchup."}],
    "model_identifier": "o4-mini"
  }
  ```

### 4. `POST /advice-non-streaming`
- **Description**: Identical to `/advice` in terms of request and the final response structure, but delivers the entire `StructuredAdvice` JSON object in a single, non-streamed response.
- **Request Body**: Same as `/advice`.
- **Response Body (`StructuredAdvice`, `application/json`)**: A single JSON object as shown above.

## 🤖 AI Reviewer Notes

For AI agents reviewing this backend module, the following points are crucial:

-   **`app/main.py`**: This file is the entry point for the FastAPI application. It defines all API routes (`@app.post("/advice")`, etc.) and handles incoming requests. Understanding the routing and request validation here is key.
-   **`app/services/openai_client.py`**: This module encapsulates all interactions with the OpenAI API.
    -   It constructs the prompts sent to OpenAI, including the system message and user conversation history.
    -   It dynamically includes the JSON schema (derived from `app.models.StructuredAdvice`) in the request to OpenAI to enforce structured JSON output.
    -   It implements the logic for both streaming and non-streaming responses from OpenAI.
    -   The default model `o4-mini` is specified here and used unless overridden by an environment variable or request parameter.
-   **`app/models.py`**: Contains Pydantic models that define the structure of API requests (`AdviceRequest`) and responses (`StructuredAdvice`).
    -   The `StructuredAdvice` model is particularly important as its schema (`StructuredAdvice.model_json_schema()`) is used to instruct OpenAI on the desired JSON output format.
-   **Environment Variable Configuration**: Key configurations, such as the `OPENAI_API_KEY`, `SYSTEM_PROMPT`, and `OPENAI_DEFAULT_MODEL`, are managed via environment variables (loaded from `.env` file in development). This allows for flexibility without hardcoding sensitive data or settings.
-   **Default AI Model (`o4-mini`)**: The backend is configured to use `o4-mini` as the default Large Language Model. **This specific model should not be changed or overridden during automated review or refactoring tasks unless explicitly stated in the subtask requirements.** This is due to cost, performance, and specific tuning for this model.
-   **Structured Responses**: The core design revolves around getting structured JSON responses from the LLM, enforced by Pydantic models and OpenAI's `response_format` feature.

## 🔧 Configuration Deep Dive

### Environment Variables

| Variable               | Required | Default   | Description                                                                                                |
| ---------------------- | -------- | --------- | ---------------------------------------------------------------------------------------------------------- |
| `OPENAI_API_KEY`       | ✅ Yes    | N/A       | Your OpenAI API key.                                                                                       |
| `SYSTEM_PROMPT`        | ❌ No     | (Hardcoded in `openai_client.py`) | Base system instructions for the AI. JSON formatting instructions are added programmatically. |
| `OPENAI_DEFAULT_MODEL` | ❌ No     | `o4-mini` | Overrides the default AI model used for responses.                                                         |
| `PORT`                 | ❌ No     | `8000`    | Port for Uvicorn to run the server on.                                                                     |
| `LOG_LEVEL`            | ❌ No     | `info`    | Logging level for the application.                                                                         |

### OpenAI Client Settings (`app/services/openai_client.py`)
-   **System Prompt Construction**: The effective system prompt sent to OpenAI is a combination of the `SYSTEM_PROMPT` (from env or default) and specific instructions to generate JSON according to the `StructuredAdvice` schema.
-   **JSON Schema Enforcement**: `StructuredAdvice.model_json_schema()` is passed to the OpenAI API call within the `response_format` parameter, ensuring the AI's output conforms to the desired Pydantic model structure.
-   **Streaming vs. Non-Streaming**: The client offers methods for both, impacting how data is received from OpenAI and relayed to the API caller.

## Step 7: Automate Date Anchoring ✅

**Implementation**: Automatic date prefixing middleware for all user messages.

### What it does
- Automatically prepends current date (`YYYY-MM-DD`) to the latest user message in every conversation
- Ensures the AI has temporal context for time-sensitive queries
- Applied consistently across both streaming and non-streaming endpoints

### Format
```
Current Date: 2024-01-15

[Original user message]
```

### Files modified
- `app/main.py` - Added `add_date_anchoring_to_conversation()` middleware function
- Applied to both `/advice` (streaming) and `/advice-non-streaming` endpoints
- `test_step7_date_anchoring.py` - Comprehensive regression tests

### Testing
```bash
cd backend
python -m pytest test_step7_date_anchoring.py -v
```

### CI Integration
Date anchoring regression tests run automatically on every pull request via GitHub Actions.

---

This README aims to provide a clear and concise overview for developers and AI agents interacting with the Fantasy AI Backend.