from fastapi import FastAPI, Query, HTTPException, Response, Request, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
import os
import logging
import psutil
import platform
import json # For constructing the final JSON object if needed, or for error responses
from typing import Optional
from datetime import datetime

from app.models import AdviceRequest, StructuredAdvice, OutcomeFeedback, ModelResponse # Import StructuredAdvice and new Step 5 models
from app.services.openai_client import get_streaming_response, OPENAI_DEFAULT_MODEL_INTERNAL, SYSTEM_DEFAULT_INSTRUCTIONS, get_response as get_openai_non_streaming_response, test_openai_connectivity
from app.services.web_search_discipline import web_search_discipline, SearchDecision
from app.services.response_logger import response_logger # Step 5: Import response logger
from app.services.confidence_scoring import confidence_scoring_service # Step 5: Import confidence service
from app.services.confidence_phrase_tuner import confidence_phrase_tuner # Step 5: Import phrase tuner
from app.services.pybaseball_service import PyBaseballService # Import the PyBaseball service

# Dependency for PyBaseballService
async def get_pybaseball_service():
    # In a real application, you might have more complex setup here,
    # like connection pooling or configuration.
    # For now, we just instantiate it.
    # Ensure PYBASEBALL_MCP_URL is set in your environment.
    return PyBaseballService()

# from app.services.chat_service import (
#     handle_advice_request,
#     handle_web_search_request,
#     get_current_openai_model_from_env  # Assuming this might be useful or refactored
# )
#from app.services.espn_api_service import get_espn_api_data_sync
# from app.utils.logging_config import get_logger
# from app.utils.rate_limiter import get_limiter_key 

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Fantasy AI Backend",
    description="AI-powered fantasy sports advice, delivered via OpenAI's Responses API with streaming JSON.",
    version="1.1.0"
)

# --- health probe ----------------------------------------------------------
@app.get("/healthz", tags=["infra"])
async def healthz():
    """Lightweight liveness probe for orchestrators and test scripts."""
    return {"status": "ok"}
# --------------------------------------------------------------------------

# CORS configuration
origins = [
    "http://localhost:3000",  # React app
    "http://localhost:5173",  # Vite React app
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://genius-frontend.onrender.com",  # Production frontend
    "https://genius-frontend-*.onrender.com",  # Any other Render frontend deployments
    "*"  # Allow all origins temporarily for debugging
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variable for the default model
OPENAI_DEFAULT_MODEL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4.1-mini") 

# --- Router Definitions ---
api_router = APIRouter()
settings_router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint providing basic info about the API.
    """
    return f"""
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

def add_date_anchoring_to_conversation(conversation_messages: list) -> list:
    """
    Step 7: Automate Date Anchoring - Prepend current date to the latest user message
    
    Args:
        conversation_messages: List of conversation messages
        
    Returns:
        List of conversation messages with date anchoring applied to the latest user message
    """
    if not conversation_messages:
        return conversation_messages
    
    # Create a copy to avoid modifying the original
    dated_messages = conversation_messages.copy()
    
    # Find the last user message and prepend current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for i in range(len(dated_messages) - 1, -1, -1):
        if dated_messages[i].get("role") == "user":
            original_content = dated_messages[i]["content"]
            dated_content = f"Current Date: {current_date}\n\n{original_content}"
            dated_messages[i]["content"] = dated_content
            break
    
    return dated_messages

@app.post("/advice")
async def get_advice_streaming(body: AdviceRequest) -> StreamingResponse:
    """
    Get AI-powered fantasy sports advice, streamed as Server-Sent Events.
    
    This endpoint:
    1. Takes a user's question about fantasy sports with optional conversation history.
    2. Applies systematic web search discipline rules (Step 4 implementation).
    3. Sends it to OpenAI's Responses API with structured JSON output.
    4. Uses previous_response_id for conversation continuity when available.
    5. Streams the response as SSE events with both text deltas and structured JSON.
    6. Logs confidence scoring data for calibration (Step 5 implementation).
    """
    try:
        logger.info(f"Received advice request with {len(body.conversation) if body.conversation else 0} messages")
        logger.info(f"Previous response ID provided: {body.previous_response_id is not None}")
        
        # Validate input
        if not body.conversation or len(body.conversation) == 0:
            raise HTTPException(status_code=400, detail="No conversation provided.")
        
        # Get the latest message content for logging and search discipline
        latest_message = body.conversation[-1].content if body.conversation else "No content"
        logger.info(f"Latest message: {latest_message[:100]}...")

        # Apply web search discipline (Step 4 implementation)
        if body.enable_web_search is None:
            # Use systematic search discipline rules
            search_decision, search_reasoning = web_search_discipline.should_search(
                user_query=latest_message,
                conversation_context=[{"role": msg.role, "content": msg.content} for msg in body.conversation],
                user_override=body.search_override
            )
            
            enable_web_search_final = search_decision == SearchDecision.MANDATORY
            logger.info(f"Search discipline decision: {search_decision.value} - {search_reasoning}")
            
            # Add search decision metadata to logs for monitoring
            search_metadata = web_search_discipline.get_search_policy_payload(
                latest_message, 
                [{"role": msg.role, "content": msg.content} for msg in body.conversation],
                body.search_override
            )
            logger.info(f"Search metadata: {search_metadata}")
            
        else:
            # User explicitly forced search on/off
            enable_web_search_final = body.enable_web_search
            logger.info(f"Web search manually {('enabled' if enable_web_search_final else 'disabled')} by user")

        model_to_use = body.model if body.model else OPENAI_DEFAULT_MODEL_INTERNAL

        # Convert conversation messages to the format expected by the OpenAI client
        conversation_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in body.conversation
        ] if body.conversation else []

        # Step 7: Apply date anchoring middleware to conversation messages
        conversation_messages = add_date_anchoring_to_conversation(conversation_messages)
        
        # Update latest_message after date anchoring for accurate logging
        if conversation_messages:
            for msg in reversed(conversation_messages):
                if msg.get("role") == "user":
                    latest_message = msg["content"]
                    break

        logger.info(f"Relaying to OpenAI Responses API using model: {model_to_use}")
        logger.info(f"Final web search decision: {enable_web_search_final}")
        logger.info(f"Date anchoring applied to conversation messages")

        # Step 5: Create wrapper function to log confidence scores
        async def streaming_response_with_logging():
            final_advice = None
            openai_response_id = None
            
            async for chunk in get_streaming_response(
                conversation_messages=conversation_messages,
                previous_response_id=body.previous_response_id,
                model=model_to_use,
                enable_web_search=enable_web_search_final,
                prompt_type=body.prompt_type or "default",
                use_step2_architecture=body.use_step2_architecture if body.use_step2_architecture is not None else True
            ):
                # Pass through all chunks
                yield chunk
                
                # Capture final response for logging
                if chunk.startswith("event: response_complete"):
                    try:
                        # Extract the final JSON from the chunk
                        data_start = chunk.find("data: ") + 6
                        data_json = json.loads(chunk[data_start:].split("\n")[0])
                        
                        if "final_json" in data_json:
                            final_advice = StructuredAdvice.model_validate(data_json["final_json"])
                            openai_response_id = data_json.get("response_id")
                            
                            # Log the response with confidence scoring (Step 5)
                            response_logger.log_response(
                                advice=final_advice,
                                user_query=latest_message,
                                conversation_context=conversation_messages,
                                model_used=model_to_use,
                                web_search_used=enable_web_search_final,
                                response_id=openai_response_id
                            )
                    except Exception as e:
                        logger.error(f"Failed to log confidence data: {e}")

        # Stream Server-Sent Events for both web and mobile compatibility
        return StreamingResponse(
            streaming_response_with_logging(), 
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
        
        # Convert conversation messages to the format expected by the OpenAI client
        conversation_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in body.conversation
        ] if body.conversation else []

        # Step 7: Apply date anchoring middleware to conversation messages
        conversation_messages = add_date_anchoring_to_conversation(conversation_messages)
        
        user_prompt = ""
        if conversation_messages:
            user_prompt = "\n".join([msg["content"] for msg in conversation_messages if msg["role"] == 'user'])
        
        if not user_prompt:
            raise HTTPException(status_code=400, detail="No user prompt provided in conversation.")

        # Apply web search discipline (Step 4 implementation)
        if body.enable_web_search is None:
            # Use systematic search discipline rules
            search_decision, search_reasoning = web_search_discipline.should_search(
                user_query=user_prompt,
                conversation_context=conversation_messages,
                user_override=body.search_override
            )
            
            enable_web_search_final = search_decision == SearchDecision.MANDATORY
            logger.info(f"Search discipline decision: {search_decision.value} - {search_reasoning}")
        else:
            # User explicitly forced search on/off
            enable_web_search_final = body.enable_web_search
            logger.info(f"Web search manually {('enabled' if enable_web_search_final else 'disabled')} by user")

        model_to_use = body.model if body.model else OPENAI_DEFAULT_MODEL_INTERNAL

        logger.info(f"Relaying to OpenAI service (non-streaming) with prompt: {user_prompt[:100]}... using model: {model_to_use}")
        logger.info(f"Date anchoring applied to conversation messages")

        # Call the synchronous, non-streaming function that returns a parsed StructuredAdvice object
        advice_object = get_openai_non_streaming_response(
            prompt=user_prompt, 
            model=model_to_use,
            enable_web_search=enable_web_search_final,
            prompt_type=body.prompt_type or "default"
        )

        # Step 5: Log confidence scoring data
        response_logger.log_response(
            advice=advice_object,
            user_query=user_prompt,
            conversation_context=conversation_messages,
            model_used=model_to_use,
            web_search_used=enable_web_search_final,
            response_id=None  # Non-streaming doesn't have OpenAI response ID
        )

        return advice_object

    except HTTPException as he:
        logger.error(f"HTTPException in /advice-non-streaming: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Error in /advice-non-streaming endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "version": app.version}

@app.post("/search-discipline")
async def test_search_discipline(query: str, search_override: Optional[str] = None):
    """
    Test endpoint for web search discipline logic (Step 4 implementation).
    
    Args:
        query: The user query to test
        search_override: Optional override command (e.g., "/nosrch")
        
    Returns:
        Search decision analysis and reasoning
    """
    try:
        # Get search decision
        decision, reasoning = web_search_discipline.should_search(
            user_query=query,
            conversation_context=None,
            user_override=search_override
        )
        
        # Get full policy payload
        policy_payload = web_search_discipline.get_search_policy_payload(
            user_query=query,
            conversation_context=None,
            user_override=search_override
        )
        
        return {
            "query": query,
            "search_override": search_override,
            "decision": decision.value,
            "reasoning": reasoning,
            "should_search": decision == SearchDecision.MANDATORY,
            "policy_payload": policy_payload,
            "query_analysis": {
                "is_time_sensitive": web_search_discipline._is_time_sensitive_query(query),
                "has_active_entities": web_search_discipline._has_recently_active_entities(query),
                "time_sensitive_keywords": web_search_discipline._get_time_sensitive_reasons(query),
                "active_entity_reasons": web_search_discipline._get_active_entity_reasons(query),
                "query_classification": web_search_discipline._classify_query(query)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in search discipline test: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error testing search discipline: {str(e)}")

@app.get("/model")
async def get_default_model():
    """
    Returns the default AI model name.
    """
    return {"model": OPENAI_DEFAULT_MODEL_INTERNAL}

# Step 5: Confidence Scoring Endpoints
@app.post("/feedback")
async def submit_feedback(feedback: OutcomeFeedback):
    """
    Submit outcome feedback for a response to improve confidence calibration.
    
    Args:
        feedback: Feedback data with response_id and outcome
        
    Returns:
        Status of feedback submission
    """
    try:
        success = response_logger.update_response_outcome(
            response_id=feedback.response_id,
            outcome=feedback.outcome,
            feedback_notes=feedback.feedback_notes
        )
        
        if success:
            return {
                "status": "success",
                "message": "Feedback recorded successfully",
                "response_id": feedback.response_id
            }
        else:
            raise HTTPException(status_code=404, detail="Response ID not found")
            
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@app.get("/confidence/stats")
async def get_confidence_stats(days_back: int = Query(7, description="Days to look back for statistics")):
    """
    Get confidence scoring statistics and Brier score analysis.
    
    Args:
        days_back: Number of days to include in analysis
        
    Returns:
        Confidence statistics and calibration metrics
    """
    try:
        stats = response_logger.get_confidence_stats(days_back)
        return stats
    except Exception as e:
        logger.error(f"Error getting confidence stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting confidence stats: {str(e)}")

@app.get("/confidence/recent")
async def get_recent_confidence_logs(limit: int = Query(20, description="Number of recent logs to return")):
    """
    Get recent confidence scoring logs for monitoring.
    
    Args:
        limit: Maximum number of logs to return
        
    Returns:
        Recent confidence logs
    """
    try:
        logs = response_logger.get_recent_logs(limit)
        return {
            "logs": logs,
            "total_count": len(logs),
            "timestamp": logs[0]["timestamp"] if logs else None
        }
    except Exception as e:
        logger.error(f"Error getting recent logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting recent logs: {str(e)}")

@app.get("/confidence/brier-score")
async def calculate_brier_score(days_back: int = Query(7, description="Days to include in Brier score calculation")):
    """
    Calculate Brier score for confidence calibration analysis.
    
    Args:
        days_back: Number of days to include in calculation
        
    Returns:
        Brier score and related calibration metrics
    """
    try:
        brier_data = confidence_scoring_service.calculate_brier_score(days_back)
        return brier_data
    except Exception as e:
        logger.error(f"Error calculating Brier score: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating Brier score: {str(e)}")

@app.get("/confidence/calibration")
async def get_calibration_analysis(days_back: int = Query(30, description="Days to include in calibration analysis")):
    """
    Get confidence calibration analysis by confidence bands.
    
    Args:
        days_back: Number of days to include in analysis
        
    Returns:
        Calibration analysis by confidence bands
    """
    try:
        analysis = confidence_phrase_tuner.analyze_calibration_drift(days_back)
        return analysis
    except Exception as e:
        logger.error(f"Error getting calibration analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting calibration analysis: {str(e)}")

@app.post("/confidence/auto-tune")
async def run_auto_tune(days_back: int = Query(7, description="Days to analyze for auto-tuning"), dry_run: bool = Query(True, description="Whether to run in dry-run mode")):
    """
    Run automatic phrase tuning based on confidence calibration.
    
    Args:
        days_back: Number of days to analyze
        dry_run: Whether to run in dry-run mode (default: True)
        
    Returns:
        Auto-tuning results and actions taken
    """
    try:
        results = confidence_phrase_tuner.auto_tune_phrases(days_back, dry_run)
        return results
    except Exception as e:
        logger.error(f"Error running auto-tune: {e}")
        raise HTTPException(status_code=500, detail=f"Error running auto-tune: {str(e)}")

@app.get("/confidence/phrase-status")
async def get_phrase_tuning_status():
    """
    Get current status of confidence phrase tuning system.
    
    Returns:
        Current calibration status and configuration
    """
    try:
        status = confidence_phrase_tuner.get_calibration_status()
        return status
    except Exception as e:
        logger.error(f"Error getting phrase status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting phrase status: {str(e)}")

# --- New Settings Endpoint ---
@settings_router.get("/default-model", response_model=ModelResponse)
async def get_default_openai_model_endpoint(): # Renamed to avoid conflict if get_default_openai_model exists elsewhere
    """
    Retrieves the default OpenAI model name from environment variables.
    """
    model_name = os.getenv("OPENAI_DEFAULT_MODEL")
    if not model_name:
        logger.warning("OPENAI_DEFAULT_MODEL environment variable is not set.")
        # Consider raising HTTPException or returning a default based on ModelResponse specifics
        # For now, returning a placeholder if ModelResponse allows it, or adjust as needed.
        # If ModelResponse.model is not Optional, this will cause an error if model_name is None.
        # Assuming ModelResponse can handle a potentially None or specific default string.
        return ModelResponse(model= os.getenv("OPENAI_DEFAULT_MODEL", "fallback_model_not_set"))
    return ModelResponse(model=model_name)

# --- Include Routers ---
# Make sure to include your main api_router if it contains other endpoints like /advice
# Example: app.include_router(api_router, prefix="/api/v1") 
app.include_router(settings_router)

# Add a new endpoint to test PyBaseball service connection
@app.get("/pybaseball/health")
async def pybaseball_health_check():
    """Check if the PyBaseball service is accessible."""
    try:
        # Test the connection by searching for a player
        result = await pybaseball_service.search_players("Trout")
        return {"status": "ok", "message": "Successfully connected to PyBaseball service", "sample_data": result[:100] + "..." if len(result) > 100 else result}
    except Exception as e:
        logger.error(f"Error connecting to PyBaseball service: {e}")
        return {"status": "error", "message": f"Error connecting to PyBaseball service: {str(e)}"}

# Add baseball data endpoints
@app.get("/pybaseball/player/{player_name}")
async def get_player_stats(player_name: str, year: Optional[int] = None):
    """Get statistics for a specific player."""
    try:
        result = await pybaseball_service.get_player_stats(player_name, year)
        return {"status": "ok", "data": result}
    except Exception as e:
        logger.error(f"Error getting player stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving player data: {str(e)}")

@app.get("/pybaseball/player/{player_name}/stats")
async def get_player_stats(
    player_name: str,
    year: Optional[int] = Query(None, description="Season year (defaults to current year)"),
    pybaseball_service: PyBaseballService = Depends(get_pybaseball_service) # Corrected
):
    """
    Get season statistics for a specific MLB player.
    - **player_name**: Full name of the player (e.g., 'Shohei Ohtani').
    - **year**: Optional season year.
    """
    try:
        # Example of how the service would be called:
        # result = await pybaseball_service.get_player_stats(player_name, year)
        # return result
        return await pybaseball_service.get_player_stats(player_name, year)
    except Exception as e:
        logger.error(f"Error in get_player_stats endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pybaseball/player/search/{search_term}")
async def search_players(
    search_term: str,
    pybaseball_service: PyBaseballService = Depends(get_pybaseball_service) # Corrected
):
    """
    Search for MLB players by name.
    - **search_term**: Partial name to search for.
    """
    try:
        # Example of how the service would be called:
        # result = await pybaseball_service.search_players(search_term)
        # return result
        return await pybaseball_service.search_players(search_term)
    except Exception as e:
        logger.error(f"Error in search_players endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pybaseball/standings")
async def get_mlb_standings(
    year: Optional[int] = Query(None, description="Season year (defaults to current year)"),
    pybaseball_service: PyBaseballService = Depends(get_pybaseball_service) # Corrected
):
    """
    Get current MLB standings by division.
    - **year**: Optional season year.
    """
    try:
        return await pybaseball_service.get_mlb_standings(year)
    except Exception as e:
        logger.error(f"Error in get_mlb_standings endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pybaseball/stat_leaders/{stat}")
async def get_stat_leaders(
    stat: str,
    year: Optional[int] = Query(None, description="Season year (defaults to current year)"),
    top_n: Optional[int] = Query(10, description="Number of top players to return (default 10)"),
    player_type: Optional[str] = Query("batting", description="Type of player statistics (batting or pitching)"),
    pybaseball_service: PyBaseballService = Depends(get_pybaseball_service) # Corrected
):
    """
    Get MLB leaders for a specific statistic.
    - **stat**: Statistic to rank by (e.g., 'HR', 'AVG', 'ERA', 'SO').
    - **year**: Optional season year.
    - **top_n**: Optional number of top players.
    - **player_type**: Optional player type ('batting' or 'pitching').
    """
    if player_type not in ["batting", "pitching"]:
        raise HTTPException(status_code=400, detail="Invalid player_type. Must be 'batting' or 'pitching'.")
    try:
        return await pybaseball_service.get_stat_leaders(stat, year, top_n, player_type)
    except Exception as e:
        logger.error(f"Error in get_stat_leaders endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pybaseball/player/{player_name}/recent_performance")
async def get_player_recent_performance(
    player_name: str,
    days: int = Query(30, description="Number of days to look back (default 30)"),
    pybaseball_service: PyBaseballService = Depends(get_pybaseball_service) # Corrected
):
    """
    Get recent game performance for an MLB player.
    - **player_name**: Full name of the player.
    - **days**: Number of days to look back (default 30).
    """
    try:
        # Example of how the service would be called:
        # result = await pybaseball_service.get_player_recent_performance(player_name, days)
        # return result
        return await pybaseball_service.get_player_recent_performance(player_name, days)
    except Exception as e:
        logger.error(f"Error in get_player_recent_performance endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pybaseball/team/{team_name}/statistics")
async def get_team_statistics(
    team_name: str,
    year: Optional[int] = Query(None, description="Season year (defaults to current year)"),
    pybaseball_service: PyBaseballService = Depends(get_pybaseball_service) # Corrected
):
    """
    Get aggregate statistics for an MLB team.
    - **team_name**: Team name or abbreviation (e.g., 'Yankees', 'NYY').
    - **year**: Optional season year.
    """
    try:
        # Example of how the service would be called:
        # result = await pybaseball_service.get_team_statistics(team_name, year)
        # return result
        return await pybaseball_service.get_team_statistics(team_name, year)
    except Exception as e:
        logger.error(f"Error in get_team_statistics endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pybaseball/cache/clear")
async def clear_pybaseball_cache(
    pybaseball_service: PyBaseballService = Depends(get_pybaseball_service) # Corrected
):
    """
    Clear the PyBaseball statistics cache.
    """
    try:
        # Example of how the service would be called:
        # result = await pybaseball_service.clear_pybaseball_cache()
        # return result
        return await pybaseball_service.clear_pybaseball_cache()
    except Exception as e:
        logger.error(f"Error in clear_pybaseball_cache endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pybaseball/service_health")
async def check_pybaseball_service_health(
    pybaseball_service: PyBaseballService = Depends(get_pybaseball_service) # Corrected
):
    """
    Check the health of the PyBaseball MCP service.
    """
    try:
        # Example of how the service would be called:
        # result = await pybaseball_service.check_pybaseball_service_health()
        # return result
        return await pybaseball_service.check_pybaseball_service_health()
    except Exception as e:
        logger.error(f"Error in check_pybaseball_service_health endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Add this endpoint near the health endpoint
@app.get("/api/test-openai", response_model=dict)
async def test_openai_api(model: str = None):
    """
    Tests the OpenAI API connectivity with a simple request
    """
    test_model = model or OPENAI_DEFAULT_MODEL_INTERNAL
    result = await test_openai_connectivity(model=test_model)
    return result

# To run this app (for development):
# uvicorn app.main:app --reload

if __name__ == "__main__":
    import uvicorn  # Import uvicorn here
    
    # Remove or comment out any direct service calls that might have been here for testing.
    # For example, ensure lines like these are NOT present or are commented out:
    # # temp_service = PyBaseballService()
    # # loop = asyncio.get_event_loop()
    # # result = loop.run_until_complete(temp_service.search_players("Trout"))
    # # print(result)

    logger.info("Starting FastAPI server with Uvicorn...")
    uvicorn.run(
        "main:app",  # Or app if main.py is in the root and run as python main.py
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=True # Added reload for development convenience, can be removed for production
    )