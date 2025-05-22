from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
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

# CORS middleware - allows your web app to talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you'd want to be more specific
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """Initialize Redis connection for rate limiting when the app starts"""
    try:
        # Try to connect to Redis (for rate limiting)
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        logger.info(f"Attempting to connect to Redis at: {redis_url}")
        r = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(r, prefix="rl")
        logger.info("Redis connected successfully for rate limiting")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e} - rate limiting disabled")
        logger.warning(f"REDIS_URL environment variable: {os.environ.get('REDIS_URL', 'not set')}")
        # Set a flag to indicate rate limiting is disabled
        app.state.rate_limiting_enabled = False
    else:
        app.state.rate_limiting_enabled = True

# Rate limiter: 5 requests per day per IP
daily_limit = RateLimiter(times=5, seconds=86_400)  # 86,400 seconds = 24 hours

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
            "redis": {
                "connected": app.state.rate_limiting_enabled if hasattr(app.state, 'rate_limiting_enabled') else False
            }
        }
        logger.info(f"Health check response: {system_info}")
        return system_info
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

@app.post("/advice")
async def get_advice(
    body: AdviceRequest, 
    rate_limit: None = Depends(daily_limit)
) -> AdviceResponse:
    """
    Get AI-powered fantasy sports advice
    
    This endpoint:
    1. Takes a user's question about fantasy sports
    2. Sends it to OpenAI's GPT-4.1
    3. Returns the AI's response
    4. Limits users to 5 requests per day
    """
    try:
        # Get the user's question (last message in conversation)
        if not body.conversation:
            raise HTTPException(status_code=400, detail="No conversation provided")
        
        user_question = body.conversation[-1].content
        if not user_question.strip():
            raise HTTPException(status_code=400, detail="Empty question provided")
        
        # Use specified model or default to GPT-4.1
        model_name = body.model if body.model else "gpt-4.1"
        
        # Check if web search should be enabled
        enable_web_search = getattr(body, 'enable_web_search', False)
        
        logger.info(f"Processing request with model: {model_name}, web_search: {enable_web_search}")
        
        # Get response from OpenAI
        reply, model_used = get_response(
            prompt=user_question, 
            model=model_name,
            enable_web_search=enable_web_search
        )
        
        return AdviceResponse(reply=reply, model=model_used)
        
    except Exception as e:
        logger.error(f"Error processing advice request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/custom-advice")
async def get_custom_advice(
    body: AdviceRequest, 
    model: str = Query("gpt-4.1", description="OpenAI model to use"),
    enable_web_search: bool = Query(False, description="Enable web search capability"),
    rate_limit: None = Depends(daily_limit)
) -> AdviceResponse:
    """
    Get AI advice with custom model and settings
    """
    try:
        if not body.conversation:
            raise HTTPException(status_code=400, detail="No conversation provided")
        
        user_question = body.conversation[-1].content
        if not user_question.strip():
            raise HTTPException(status_code=400, detail="Empty question provided")
        
        logger.info(f"Custom advice request with model: {model}, web_search: {enable_web_search}")
        
        reply, model_used = get_response(
            prompt=user_question, 
            model=model,
            enable_web_search=enable_web_search
        )
        
        return AdviceResponse(reply=reply, model=model_used)
        
    except Exception as e:
        logger.error(f"Error processing custom advice request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Handle rate limit exceeded
@app.exception_handler(429)
async def rate_limit_handler(request, exc):
    return {"error": "Daily limit of 5 messages exceeded. Please try again tomorrow or download our iOS app for unlimited access."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)