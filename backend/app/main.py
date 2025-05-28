from fastapi import FastAPI, Query, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import logging
import psutil
import platform

from app.models import AdviceRequest, AdviceResponse
from app.services.openai_client import get_response

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fantasy AI Backend",
    description="AI-powered fantasy sports advice using OpenAI's GPT-4.1",
    version="1.0.0"
)

# CORS middleware with very permissive settings for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Welcome page that shows your API is working"""
    return """
    <html>
        <head>
            <title>Fantasy AI Backend</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #4a4a4a; }
                .status { color: #28a745; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>🏆 Fantasy AI Backend</h1>
            <p class="status">✅ API is running successfully!</p>
            <p>This backend provides AI-powered fantasy sports advice using OpenAI's GPT-4.1.</p>
            
            <h2>Available Endpoints:</h2>
            <ul>
                <li><strong>POST /advice</strong> - Get AI fantasy sports advice</li>
                <li><strong>GET /health</strong> - Check if the API is healthy</li>
                <li><strong>GET /docs</strong> - View API documentation</li>
            </ul>
            
            <p>Frontend web app connects to this backend to provide the chat interface.</p>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with system information"""
    try:
        # Get system information
        system_info = {
            "status": "healthy",
            "message": "Backend is running",
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "memory_usage": f"{psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB",
                "cpu_percent": psutil.Process().cpu_percent(),
            },
            "cors_enabled": True
        }
        logger.info(f"Health check response: {system_info}")
        return system_info
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/healthz")
async def healthz_check():
    """Health check endpoint for Render compatibility"""
    return await health_check()

@app.post("/advice")
async def get_advice(body: AdviceRequest) -> AdviceResponse:
    """
    Get AI-powered fantasy sports advice
    
    This endpoint:
    1. Takes a user's question about fantasy sports
    2. Sends it to OpenAI's GPT-4.1
    3. Returns the AI's response
    """
    try:
        logger.info("=== ADVICE REQUEST RECEIVED ===")
        logger.info(f"Request body: {body}")
        logger.info(f"Web search enabled in request: {body.enable_web_search}")
        logger.info(f"Web search field type: {type(body.enable_web_search)}")
        
        # Get the user's question (last message in conversation)
        if not body.conversation:
            logger.error("No conversation provided")
            raise HTTPException(status_code=400, detail="No conversation provided")
        
        user_question = body.conversation[-1].content
        if not user_question.strip():
            logger.error("Empty question provided")
            raise HTTPException(status_code=400, detail="Empty question provided")
        
        # Use specified model or default to environment variable or fallback
        default_model = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4.1")
        model_name = body.model if body.model else default_model
        
        # Check if web search should be enabled
        enable_web_search = getattr(body, 'enable_web_search', False)
        
        logger.info(f"Processing request with model: {model_name}, web_search: {enable_web_search}")
        
        # Get response from OpenAI
        reply, model_used = get_response(
            prompt=user_question, 
            model=model_name,
            enable_web_search=enable_web_search
        )
        
        logger.info(f"Got response from OpenAI: {reply[:100]}...")  # Log first 100 chars
        logger.info(f"Model used: {model_used}")
        
        response = AdviceResponse(reply=reply, model=model_used)
        logger.info(f"Returning response: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing advice request: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)