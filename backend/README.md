# Fantasy AI Backend

> **The Brain Behind The Genius** - FastAPI server that powers your fantasy sports AI assistant with structured, streaming JSON responses.

This is the backend API server that handles all the smart stuff - connecting to OpenAI, processing fantasy sports questions, and sending back intelligent, structured advice via a streaming API.

## 🧠 What This Does

This backend server:
- **Receives Questions**: Gets fantasy sports questions from your web app or mobile app via a JSON payload.
- **Talks to AI**: Sends questions to OpenAI's API (defaulting to `gpt-4o-mini`), requesting structured JSON output.
- **Streams Structured Answers**: Streams back fantasy sports advice formatted as a single JSON object (`StructuredAdvice` model) chunk by chunk. This allows clients to display information progressively.
- **Offers Non-Streaming Option**: Provides an alternative endpoint for receiving the full structured JSON response in one go.
- **Manages CORS**: Ensures your client applications can communicate with this server.

## 🔧 Technology Stack (What's Under the Hood)

- **FastAPI**: Modern Python web framework.
- **OpenAI GPT-4o-mini**: Default AI model via the Responses API, configured for structured JSON output. **IMPORTANT NOTE:** `gpt-4o-mini` is the specified default model. Do not change this without explicit instruction.
- **Pydantic**: Ensures data is properly formatted, validated, and used for defining the JSON schema for OpenAI.
- **Uvicorn**: Production-ready ASGI web server.
- **Docker**: Containerization for easy deployment.
- **Render.com**: Cloud hosting platform.

## 📁 Project Structure

```
backend/
├── app/                           # Main application code
│   ├── services/                  # External service connections
│   │   └── openai_client.py      # Connects to OpenAI, handles streaming and JSON formatting
│   ├── models.py                  # Pydantic models for request/response and JSON schemas
│   └── main.py                    # Main FastAPI server file with all endpoints
├── tests/                         # Automated tests (ensure these are updated for new response types)
│   ├── test_main.py              # Tests for API endpoints
│   ├── test_openai_client.py     # Tests for OpenAI integration
│   └── test_responses_api.py     # Tests for Responses API
├── requirements.txt               # Python packages needed
├── requirements-test.txt          # Testing packages
├── pyproject.toml                # Poetry configuration (if used)
├── Dockerfile                    # Instructions for Docker deployment
├── render.yaml                   # Render.com deployment settings
└── README.md                     # This file
```

## 🚀 Quick Start Guide

### Step 1: Get Your Environment Ready

**Install Python** (if you don't have it):
1. Go to [python.org](https://python.org)
2. Download Python 3.11 or newer
3. Install it (check "Add to PATH" on Windows)

**Get an OpenAI API Key**:
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an account or sign in.
3. Navigate to API Keys and create a new secret key.
4. **Important**: Ensure your OpenAI account has credits.

### Step 2: Download and Set Up the Code

```bash
# 1. Navigate to the backend folder
cd backend

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install all required packages
pip install -r requirements.txt
```

### Step 3: Configure Your Environment

Create a `.env` file in the `backend` directory:
```env
# Required: Your OpenAI API Key
OPENAI_API_KEY=sk-your_actual_openai_key_here

# Optional: System prompt (how the AI should behave)
# This is combined with JSON schema instructions in openai_client.py
SYSTEM_PROMPT="You are a helpful fantasy sports assistant with deep knowledge of player performance, matchups, and strategy. You MUST respond in JSON format adhering to the provided schema."

# Optional: Override default model (default is gpt-4o-mini)
# OPENAI_DEFAULT_MODEL="gpt-4o"
```

### Step 4: Test the Server

**Start the development server**:
```bash
# From the 'the-genius/backend' directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Test it's working**:
1. Open your web browser to `http://localhost:8000`. You should see the API welcome page.
2. Go to `http://localhost:8000/docs` for interactive API documentation.

**Test the `/advice` streaming endpoint**:
Use `curl` or a tool like Postman that can handle streaming responses.
```bash
curl -N -X POST "http://localhost:8000/advice" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {"role": "user", "content": "Should I start Patrick Mahomes or Josh Allen this week?"}
    ]
  }'
```
You should see JSON chunks streaming in, which together will form a complete `StructuredAdvice` object.

**Test the `/advice-non-streaming` endpoint**:
```bash
curl -X POST "http://localhost:8000/advice-non-streaming" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {"role": "user", "content": "Who are the top 3 waiver wire pickups for WR this week?"}
    ]
  }'
```
This will return the complete `StructuredAdvice` JSON object at once.

## API Endpoints

### 1. `GET /` - Welcome Page
- **Description**: Basic HTML page indicating the API is running and showing some system stats.
- **Usage**: Browser access to `http://localhost:8000`.

### 2. `GET /health` - Health Check
- **Description**: Returns the health status and version of the API.
- **Response**: `{"status": "healthy", "version": "1.1.0"}`

### 3. `POST /advice` - Get Streaming Structured AI Fantasy Advice
- **Description**: Main endpoint for getting AI fantasy sports advice. The response is streamed as JSON chunks that form a single `StructuredAdvice` object. The client is expected to accumulate these chunks and parse the complete JSON.
- **Media Type**: `application/x-ndjson` (Newline Delimited JSON, though in this case it's chunks of a single JSON object)
- **Request Body (`AdviceRequest`)**:
  ```json
  {
    "conversation": [
      {
        "role": "user", // or "assistant", "system"
        "content": "Your fantasy question here"
      }
      // More messages can be part of the conversation history
    ],
    "model": "gpt-4o-mini", // Optional: specify a model
    "enable_web_search": false // Optional: Currently not used with JSON mode
  }
  ```
- **Response Stream (Chunks forming `StructuredAdvice`)**:
  The server streams text chunks. When concatenated, they form a JSON object like this:
  ```json
  {
    "main_advice": "Consider starting Josh Allen over Patrick Mahomes this week.",
    "reasoning": "Josh Allen has a more favorable matchup against a weaker pass defense, and has been consistently outperforming Mahomes in recent weeks based on fantasy points per game. Mahomes is facing a tougher secondary.",
    "confidence_score": 0.75,
    "alternatives": [
      {
        "player": "Patrick Mahomes",
        "reason": "Still an elite QB, could always have a massive game. A good start if you prefer his floor."
      },
      {
        "player": "QB Streaming Option X",
        "reason": "If both Allen and Mahomes have very tough matchups and a high-upside streamer is available."
      }
    ],
    "model_identifier": "gpt-4o-mini"
  }
  ```
  *Note: Field names are snake_case as per default Pydantic model serialization for JSON.*

### 4. `POST /advice-non-streaming` - Get Non-Streaming Structured AI Fantasy Advice
- **Description**: Same as `/advice` but returns the complete `StructuredAdvice` JSON object in a single response without streaming. Useful for testing or clients that don't require streaming.
- **Request Body**: Same as `/advice`.
- **Response Body (`StructuredAdvice`)**:
  A single JSON object identical in structure to the one described for the `/advice` endpoint's complete stream.

## 🔧 Configuration Options

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key | `sk-abc123...` |
| `SYSTEM_PROMPT` | ❌ No | Base system instructions for the AI. JSON formatting instructions are added programmatically. | `You are a fantasy expert...` |
| `PORT` | ❌ No | Port to run server on (default `8000`) | `8000` |
| `OPENAI_DEFAULT_MODEL` | ❌ No | Overrides the default AI model. If not set, defaults to `gpt-4o-mini`. | `gpt-4o` |

### OpenAI Settings (in `app/services/openai_client.py`)

- **Default Model**: The primary default AI model is `gpt-4o-mini`, explicitly set in `app/services/openai_client.py`. This can be overridden by the `OPENAI_DEFAULT_MODEL` environment variable.
- **System Instructions**: The `SYSTEM_DEFAULT_INSTRUCTIONS` (from env or hardcoded) is combined with specific instructions to output JSON according to the `StructuredAdvice` Pydantic model's schema.
- **JSON Schema**: The `StructuredAdvice.model_json_schema()` is passed to the OpenAI API's `response_format` parameter to enforce JSON output.

---

This README provides a comprehensive overview of the Fantasy AI Backend, its setup, and API usage. Remember to keep your tests updated as the API evolves!