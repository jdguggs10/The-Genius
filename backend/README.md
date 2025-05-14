# Fantasy AI Backend

A FastAPI application that provides AI-powered fantasy sports advice using OpenAI's Responses API with GPT-4.1.

## Features

- Uses OpenAI's Responses API (not Chat Completions API)
- Default model is GPT-4.1
- Allows specifying different models when needed
- Returns model information with each response
- Containerized with Docker

## API Endpoints

- `/advice`: Get AI advice using the default GPT-4.1 model
- `/custom-advice`: Get AI advice with a specified model

## Setup Instructions

### Prerequisites

- Python 3.11+
- Poetry for dependency management
- OpenAI API key with access to GPT-4.1

### Local Development

1. Clone the repository
2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env to add your OPENAI_API_KEY
   ```
3. Install dependencies:
   ```bash
   poetry install
   ```
4. Run the server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t fantasy-backend .
   ```
2. Run the container:
   ```bash
   docker run -p 8080:8080 --env-file .env fantasy-backend
   ```

## Testing

Run the tests with:
```bash
poetry run pytest
```

See the [Testing Guide](TESTING.md) for more detailed testing instructions.

## API Usage Example

```bash
# Get advice using GPT-4.1
curl -X POST "http://localhost:8000/advice" \
  -H "Content-Type: application/json" \
  -d '{"conversation":[{"role":"user","content":"Which quarterback should I start this week?"}]}'

# Get advice using a different model
curl -X POST "http://localhost:8000/custom-advice?model=gpt-4o" \
  -H "Content-Type: application/json" \
  -d '{"conversation":[{"role":"user","content":"Should I trade for Christian McCaffrey?"}]}'
```

## Technical Details

- FastAPI web framework
- Pydantic for data validation
- OpenAI's official Python client
- Responses API (beta) for AI completions
- GPT-4.1 as the default model