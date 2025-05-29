from fastapi import FastAPI, Query, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
import os
import logging
import psutil
import platform
import json # For constructing the final JSON object if needed, or for error responses

from app.models import AdviceRequest, StructuredAdvice # Import StructuredAdvice
from app.services.openai_client import get_streaming_response, OPENAI_DEFAULT_MODEL_INTERNAL, SYSTEM_DEFAULT_INSTRUCTIONS, get_response as get_openai_non_streaming_response

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fantasy AI Backend",
    description="AI-powered fantasy sports advice, delivered via OpenAI's Responses API with streaming JSON.",
    version="1.1.0"
)

# CORS configuration
origins = [
    "http://localhost:3000",  # React app
    "http://localhost:5173",  # Vite React app
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    # Add any other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint providing basic info about the API.
    """
    return """
    <html>
        <head>
            <title>Fantasy AI Backend</title>
        </head>
        <body>
            <h1>Fantasy AI Backend</h1>
            <p>Welcome to the AI-powered fantasy sports advice API.</p>
            <p>Use the /advice endpoint to get streaming JSON advice.</p>
            <p>Current System Stats:</p>
            <ul>
                <li>CPU Usage: {psutil.cpu_percent()}%</li>
                <li>Memory Usage: {psutil.virtual_memory().percent}%</li>
                <li>Python Version: {platform.python_version()}</li>
                <li>OS: {platform.system()} {platform.release()}</li>
            </ul>
        </body>
    </html>
    """

@app.post("/advice")
async def get_advice_streaming(body: AdviceRequest) -> StreamingResponse:
    """
    Get AI-powered fantasy sports advice, streamed as Server-Sent Events.
    
    This endpoint:
    1. Takes a user's question about fantasy sports.
    2. Sends it to OpenAI's Responses API with structured JSON output.
    3. Streams the response as SSE events with both text deltas and structured JSON.
    """
    try:
        logger.info(f"Received advice request: {body.conversation[-1].content if body.conversation else 'No prompt'}")
        
        user_prompt = ""
        if body.conversation:
            # Simple concatenation for now; more sophisticated context handling could be added
            user_prompt = "\n".join([msg.content for msg in body.conversation if msg.role == 'user'])
        
        if not user_prompt:
             raise HTTPException(status_code=400, detail="No user prompt provided in conversation.")

        model_to_use = body.model if body.model else OPENAI_DEFAULT_MODEL_INTERNAL

        logger.info(f"Relaying to OpenAI Responses API with prompt: {user_prompt[:100]}... using model: {model_to_use}")

        # Stream Server-Sent Events for both web and mobile compatibility
        return StreamingResponse(
            get_streaming_response(
                prompt=user_prompt, 
                model=model_to_use,
                enable_web_search=body.enable_web_search or False
            ), 
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )

    except HTTPException as he:
        logger.error(f"HTTPException in /advice: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Error in /advice endpoint: {e}", exc_info=True)
        # Return SSE-formatted error
        async def error_stream():
            yield f"event: error\ndata: {json.dumps({'error': 'INTERNAL_SERVER_ERROR', 'message': str(e)})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

# Example non-streaming endpoint (optional, for testing or specific use cases)
@app.post("/advice-non-streaming", response_model=StructuredAdvice)
async def get_advice_non_streaming(body: AdviceRequest) -> StructuredAdvice:
    """
    Get AI-powered fantasy sports advice as a single JSON object (non-streaming).
    This endpoint is primarily for testing or use cases where streaming is not preferred.
    It directly returns a `StructuredAdvice` Pydantic model.
    """
    try:
        logger.info(f"Received non-streaming advice request: {body.conversation[-1].content if body.conversation else 'No prompt'}")
        
        user_prompt = ""
        if body.conversation:
            user_prompt = "\n".join([msg.content for msg in body.conversation if msg.role == 'user'])
        
        if not user_prompt:
            raise HTTPException(status_code=400, detail="No user prompt provided in conversation.")

        model_to_use = body.model if body.model else OPENAI_DEFAULT_MODEL_INTERNAL

        logger.info(f"Relaying to OpenAI service (non-streaming) with prompt: {user_prompt[:100]}... using model: {model_to_use}")

        # Call the synchronous, non-streaming function that returns a parsed StructuredAdvice object
        advice_object = get_openai_non_streaming_response(
            prompt=user_prompt, 
            model=model_to_use
            # instructions and other params will use defaults in get_openai_non_streaming_response
        )
        return advice_object

    except HTTPException as he:
        logger.error(f"HTTPException in /advice-non-streaming: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Error in /advice-non-streaming endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "version": app.version}

# Add more endpoints as needed...

# To run this app (for development):
# uvicorn app.main:app --reload

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)