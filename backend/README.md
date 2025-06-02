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
│   │   ├── __init__.py            # Makes 'services' a Python package
│   │   ├── confidence_phrase_tuner.py # Tunes confidence phrases based on scores
│   │   ├── confidence_scoring.py  # Calculates confidence scores for advice
│   │   ├── openai_client.py       # Handles all communication with OpenAI API, including prompt construction, streaming, and structured JSON response enforcement.
│   │   ├── prompt_loader.py       # Loads and manages system prompts
│   │   ├── response_logger.py     # Logs AI responses
│   │   ├── schema_validator.py    # Validates JSON schemas
│   │   └── web_search_discipline.py # Manages web search integration (if enabled)
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

### 5. `POST /search-discipline`
- **Description**: Test endpoint for web search discipline logic. Useful for understanding how a given query will be treated by the search decision system.
- **Request Parameters (Query)**:
    - `query: str` (required): The user query to test.
    - `search_override: Optional[str]` (optional): An optional command to override default search behavior (e.g., "/nosrch" to force no search, "/search" to force search).
- **Response Body (`application/json`)**:
  ```json
  {
    "query": "Is player X injured?",
    "search_override": null,
    "decision": "MANDATORY", // Or "DISALLOWED", "USER_OVERRIDE_NO", "USER_OVERRIDE_YES", "DEFAULT_NO", "DEFAULT_YES"
    "reasoning": "Query contains time-sensitive keywords.",
    "should_search": true,
    "policy_payload": {
      "user_query": "Is player X injured?",
      "conversation_context": null,
      "user_override": null,
      "system_rules_decision": "MANDATORY",
      "system_rules_reasoning": "Query contains time-sensitive keywords.",
      "final_decision": "MANDATORY",
      "final_reasoning": "Query contains time-sensitive keywords."
    },
    "query_analysis": {
      "is_time_sensitive": true,
      "has_active_entities": false,
      "time_sensitive_keywords": ["injured"],
      "active_entity_reasons": [],
      "query_classification": "interrogative"
    }
  }
  ```

### 6. `GET /model`
- **Description**: Returns the default AI model name currently configured for the backend.
- **Response Body (`application/json`)**:
  ```json
  {
    "model": "o4-mini" 
  }
  ```
  *(Note: The actual model name is determined by the `OPENAI_DEFAULT_MODEL_INTERNAL` variable in the backend.)*

### 7. `POST /feedback`
- **Description**: Submit outcome feedback for a specific AI response. This is used to evaluate and improve the confidence calibration of the AI.
- **Request Body (`OutcomeFeedback`)**:
  ```json
  {
    "response_id": "resp_xxxxxxxxxxxx",
    "outcome": true, // true if advice was correct/helpful, false if incorrect/unhelpful
    "feedback_notes": "The advice was spot on, player X had a great game." // Optional
  }
  ```
- **Response Body (`application/json`)**:
    - **Success (200 OK)**:
      ```json
      {
        "status": "success",
        "message": "Feedback recorded successfully",
        "response_id": "resp_xxxxxxxxxxxx"
      }
      ```
    - **Error (404 Not Found)**: If `response_id` is not found.
    - **Error (500 Internal Server Error)**: For other processing errors.

### 8. `GET /confidence/stats`
- **Description**: Get aggregated confidence scoring statistics, including Brier score analysis, over a specified period.
- **Request Parameters (Query)**:
    - `days_back: int` (optional, default: 7): The number of days to look back for statistics.
- **Response Body (`application/json`)**:
  ```json
  {
    "total_responses": 150,
    "responses_with_feedback": 120,
    "positive_feedback_count": 90,
    "negative_feedback_count": 30,
    "avg_confidence_score": 0.75,
    "brier_score_overall": 0.18,
    "calibration_data": [
      {"confidence_band": "0.0-0.1", "count": 10, "observed_accuracy": 0.05, "brier_score_band": 0.01},
      // ... more bands ...
      {"confidence_band": "0.9-1.0", "count": 25, "observed_accuracy": 0.88, "brier_score_band": 0.02}
    ],
    "last_updated": "YYYY-MM-DDTHH:MM:SSZ"
  }
  ```
  *(Note: The actual structure of `calibration_data` and other fields might vary based on `response_logger.get_confidence_stats` implementation.)*

### 9. `GET /confidence/recent`
- **Description**: Retrieve recent confidence scoring logs for monitoring and debugging purposes.
- **Request Parameters (Query)**:
    - `limit: int` (optional, default: 20): The maximum number of recent logs to return.
- **Response Body (`application/json`)**:
  ```json
  {
    "logs": [
      {
        "id": 123,
        "response_text": "Advice given...",
        "confidence_score": 0.85,
        "user_query": "User question...",
        "model_used": "o4-mini",
        "web_search_used": false,
        "outcome": true,
        "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
        "feedback_timestamp": "YYYY-MM-DDTHH:MM:SSZ",
        "response_id": "resp_zzzzzzzzzz"
      }
      // ... more logs ...
    ],
    "total_count": 20, // or the actual number of logs returned
    "timestamp": "YYYY-MM-DDTHH:MM:SSZ" // Timestamp of the most recent log in the list
  }
  ```

### 10. `GET /confidence/brier-score`
- **Description**: Calculate the Brier score, a measure of confidence calibration, over a specified period.
- **Request Parameters (Query)**:
    - `days_back: int` (optional, default: 7): The number of days to include in the Brier score calculation.
- **Response Body (`application/json`)**:
  ```json
  {
    "brier_score": 0.18,
    "total_predictions": 120,
    "calibration_curve_data": [
      {"predicted_probability": 0.1, "observed_frequency": 0.08},
      // ... more points ...
      {"predicted_probability": 0.9, "observed_frequency": 0.85}
    ],
    "reliability_diagram_data": { /* ... data for plotting ... */ }
  }
  ```
  *(Note: The actual structure is defined by `confidence_scoring_service.calculate_brier_score`.)*

### 11. `GET /confidence/calibration`
- **Description**: Get a detailed analysis of confidence calibration, typically by confidence bands or bins.
- **Request Parameters (Query)**:
    - `days_back: int` (optional, default: 30): The number of days to include in the calibration analysis.
- **Response Body (`application/json`)**:
  ```json
  {
    "overall_calibration": {
      "average_confidence": 0.75,
      "observed_accuracy": 0.72,
      "expected_calibration_error (ECE)": 0.05
    },
    "calibration_bands": [
      {"band": "[0.0, 0.1]", "count": 10, "avg_confidence": 0.05, "observed_accuracy": 0.08, "is_calibrated": true},
      // ... more bands ...
      {"band": "[0.9, 1.0]", "count": 25, "avg_confidence": 0.95, "observed_accuracy": 0.88, "is_calibrated": false}
    ],
    "drift_analysis": { /* ... details on calibration changes over time ... */ }
  }
  ```
  *(Note: The actual structure is defined by `confidence_phrase_tuner.analyze_calibration_drift`.)*

### 12. `POST /confidence/auto-tune`
- **Description**: Run an automatic process to tune confidence phrases based on recent calibration performance.
- **Request Parameters (Query)**:
    - `days_back: int` (optional, default: 7): The number of days of data to analyze for auto-tuning.
    - `dry_run: bool` (optional, default: True): If `true`, the endpoint will report what changes it would make without actually applying them. If `false`, changes are applied.
- **Response Body (`application/json`)**:
  ```json
  {
    "status": "dry_run_complete", // or "tuning_applied"
    "analyzed_period_days": 7,
    "previous_calibration": { /* ... calibration data before tuning ... */ },
    "suggested_adjustments": [
      {"phrase_key": "high_confidence", "old_threshold": 0.8, "new_threshold": 0.85, "reason": "Overconfident in 0.8 band"}
      // ... more adjustments ...
    ],
    "new_phrase_configuration": { /* ... updated phrase settings if not a dry run ... */ },
    "summary": "Suggested 2 adjustments based on calibration analysis."
  }
  ```
  *(Note: The actual structure is defined by `confidence_phrase_tuner.auto_tune_phrases`.)*

### 13. `GET /confidence/phrase-status`
- **Description**: Get the current status of the confidence phrase tuning system, including current phrase mappings and calibration metrics.
- **Response Body (`application/json`)**:
  ```json
  {
    "current_phrase_map": {
      "high_confidence": {"min_score": 0.85, "max_score": 1.0, "phrase": "Highly confident"},
      "medium_confidence": {"min_score": 0.6, "max_score": 0.84, "phrase": "Fairly confident"},
      // ... other phrases ...
    },
    "last_tuned_timestamp": "YYYY-MM-DDTHH:MM:SSZ",
    "recent_calibration_score": 0.04, // e.g., ECE
    "tuning_mode": "automatic" // or "manual"
  }
  ```
  *(Note: The actual structure is defined by `confidence_phrase_tuner.get_calibration_status`.)*

## 🤖 AI Reviewer Notes

For AI agents reviewing this backend module, the following points are crucial:

-   **`app/main.py`**: This file is the entry point for the FastAPI application. It defines all API routes (`@app.post("/advice")`, etc.) and handles incoming requests. Understanding the routing and request validation here is key.
-   **`app/services/openai_client.py`**: This module encapsulates all interactions with the OpenAI API.
    -   It constructs the prompts sent to OpenAI, leveraging `app/services/prompt_loader.py` for dynamic prompt generation based on `prompt_type` and `use_step2_architecture` flags. This includes system messages, user conversation history, and schema instructions.
    -   It dynamically includes the JSON schema (derived from `app.models.StructuredAdvice`) in the request to OpenAI to enforce structured JSON output. This is typically handled by `prompt_loader.build_conversation_messages`.
    -   It implements the logic for both streaming (using `AsyncOpenAI`) and non-streaming (using `OpenAI`) responses.
    -   The default model is `gpt-4.1` (defined by `OPENAI_DEFAULT_MODEL_INTERNAL` in `openai_client.py`), which can be overridden by the `OPENAI_DEFAULT_MODEL` environment variable or a model specified in an API request.
-   **`app/models.py`**: Contains Pydantic models that define the structure of API requests (e.g., `AdviceRequest`, `OutcomeFeedback`) and responses (e.g., `StructuredAdvice`).
    -   The `StructuredAdvice` model is particularly important as its schema (`StructuredAdvice.model_json_schema()`) is used to instruct OpenAI on the desired JSON output format.
-   **`app/services/prompt_loader.py`**: Manages the loading and construction of prompts sent to the AI, including system prompts and the integration of JSON schemas.
-   **`app/services/response_logger.py`**: Handles logging of AI responses and user feedback (`OutcomeFeedback`) to a database, crucial for confidence scoring and calibration.
-   **`app/services/confidence_scoring.py` & `app/services/confidence_phrase_tuner.py`**: These modules manage the calculation of confidence scores, Brier scores, calibration analysis, and automatic tuning of confidence phrases.
-   **`app/services/web_search_discipline.py`**: Implements the logic to decide whether a web search should be performed for a given query based on various factors.
-   **`app/services/schema_validator.py`**: Ensures that AI responses, especially streaming ones, conform to the expected `StructuredAdvice` schema, with fallback mechanisms.
-   **Environment Variable Configuration**: Key configurations, such as the `OPENAI_API_KEY`, `SYSTEM_PROMPT` (via `prompt_loader`), and `OPENAI_DEFAULT_MODEL`, are managed via environment variables (loaded from `.env` file in development). This allows for flexibility without hardcoding sensitive data or settings.
-   **Default AI Model**: The backend's internal default AI model is `gpt-4.1` (see `OPENAI_DEFAULT_MODEL_INTERNAL` in `app/services/openai_client.py`). This can be overridden by the `OPENAI_DEFAULT_MODEL` environment variable. **Tasks should refer to this default unless specified. The `o4-mini` model might be mentioned in client requests or older documentation, but `gpt-4.1` is the current internal default.**
-   **Structured Responses**: The core design revolves around getting structured JSON responses from the LLM, enforced by Pydantic models and OpenAI's API features. Validation is performed by `schema_validator.py`.
-   **Date Anchoring**: User messages are automatically prepended with the current date (see `add_date_anchoring_to_conversation` in `app/main.py`) to provide temporal context to the AI.

## 🔧 Configuration Deep Dive

### Environment Variables

| Variable               | Required | Default                                   | Description                                                                                                                               |
| ---------------------- | -------- | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `OPENAI_API_KEY`       | ✅ Yes    | N/A                                       | Your OpenAI API key.                                                                                                                      |
| `SYSTEM_PROMPT`        | ❌ No     | (Managed by `prompt_loader.py`)           | Base system instructions for the AI. Loaded via `prompt_loader.py`, which has its own default if this env var is not set. Overrides the default prompt in `prompt_config.yaml`. |
| `OPENAI_DEFAULT_MODEL` | ❌ No     | `gpt-4.1`                                 | Overrides the internal default AI model (`gpt-4.1`) used for responses. See `OPENAI_DEFAULT_MODEL_INTERNAL` in `openai_client.py`.         |
| `PORT`                 | ❌ No     | `8000`                                    | Port for Uvicorn to run the server on.                                                                                                    |
| `LOG_LEVEL`            | ❌ No     | `INFO`                                    | Logging level for the application (e.g., `DEBUG`, `INFO`, `WARNING`).                                                                     |

### OpenAI Client Settings (`app/services/openai_client.py`)
-   **System Prompt Construction**: The effective system prompt sent to OpenAI is constructed by `app/services/prompt_loader.py`. It can be influenced by the `SYSTEM_PROMPT` environment variable (which overrides defaults in `prompt_config.yaml`), the `prompt_type` request parameter, and whether `use_step2_architecture` is active (which may use a "slim" version of the prompt). Specific instructions to generate JSON according to the `StructuredAdvice` schema are also integrated by the prompt loader.
-   **JSON Schema Enforcement**: The JSON schema from `StructuredAdvice.model_json_schema()` is incorporated into the messages sent to the OpenAI API (usually within an assistant message as part of the `use_step2_architecture` approach) to guide the LLM towards producing valid structured JSON.
-   **Streaming vs. Non-Streaming**: The client offers methods for both, impacting how data is received from OpenAI and relayed to the API caller. Streaming uses `AsyncOpenAI` and non-streaming uses `OpenAI`.
-   **Schema Validation**: For streaming responses, `app/services/schema_validator.py` attempts to validate the incoming chunks and the final accumulated response, providing a fallback if validation fails.

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