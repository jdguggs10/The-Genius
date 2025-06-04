import os
from dotenv import load_dotenv
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError, NotFoundError, BadRequestError, AsyncOpenAI
# Removed problematic imports that don't exist in this version
# from openai.types.responses import ResponseOutputTextDeltaEvent, ResponseDoneEvent, ResponseErrorEvent
from typing import Tuple, Dict, List, Optional, Any, AsyncGenerator, Awaitable

import logging
import json # For parsing in the non-streaming version and CLI

# Import the Pydantic model for structured responses
from app.models import StructuredAdvice

# Import the new modular prompt loader
from app.services.prompt_loader import prompt_loader

# Import the schema validator
from app.services.schema_validator import schema_validator

# Import the PyBaseball service
from app.services.pybaseball_service import PyBaseballService

# Instantiate the PyBaseball service
pybaseball_service = PyBaseballService()

# Load environment variables from .env file
load_dotenv()

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY environment variable is not set")
    raise EnvironmentError("Missing OPENAI_API_KEY")

# Use AsyncOpenAI for the streaming function
async_client = AsyncOpenAI(api_key=api_key)
# Keep synchronous client for the existing non-streaming function
client = OpenAI(api_key=api_key)

# Define the default model by checking environment variable first, then fallback
OPENAI_DEFAULT_MODEL_INTERNAL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4.1") # Default model updated to GPT-4.1

# Use the modular prompt system for default instructions
SYSTEM_DEFAULT_INSTRUCTIONS = prompt_loader.get_system_prompt("default")

# Add this helper function near the top of the file after the imports
def check_model_compatibility(model: str) -> dict:
    """
    Checks if a model is compatible with various OpenAI API features.
    
    Args:
        model: The model name to check
        
    Returns:
        dict: Compatibility information for various features
    """
    # Define known compatibility information
    # Based on documentation and testing as of 2025
    compatibility = {
        "gpt-4.1": {
            "web_search": True,
            "function_calling": True,
            "step2_architecture": True,
            "complex_prompts": True,
            "recommended": True
        },
        "gpt-4.1-mini": {
            "web_search": True,  # Supports web search but with limitations
            "function_calling": True,  # Supports function calling but with limitations
            "step2_architecture": False,  # May struggle with complex system prompts
            "complex_prompts": False,  # Often has difficulty with complex schemas
            "recommended": False
        },
        "gpt-4-turbo": {
            "web_search": False,  # Not explicitly designed for web search
            "function_calling": True,
            "step2_architecture": True,
            "complex_prompts": True,
            "recommended": False  # Deprecated in favor of gpt-4.1
        }
    }
    
    # Get compatibility for the requested model
    model_compat = compatibility.get(model, {
        "web_search": False,
        "function_calling": False,
        "step2_architecture": False,
        "complex_prompts": False,
        "recommended": False,
        "unknown_model": True
    })
    
    if model_compat.get("unknown_model", False):
        logger.warning(f"Unknown model: {model}. Compatibility information may not be accurate.")
    
    return model_compat

async def get_streaming_response(
    prompt: str = None,
    model: str = OPENAI_DEFAULT_MODEL_INTERNAL,
    instructions: str = None,
    max_tokens: int = 2000,
    enable_web_search: bool = True,
    prompt_type: str = "default",
    conversation_messages: List = None,
    previous_response_id: str = None,
    use_step2_architecture: bool = True
) -> AsyncGenerator[str, None]:
    """
    Gets a streaming response from OpenAI's Responses API with structured JSON output.
    
    Args:
        prompt: User prompt (for backward compatibility)
        conversation_messages: List of conversation messages (role/content dicts)
        previous_response_id: OpenAI response ID for conversation continuity
        prompt_type: Type of prompt to use from config ("default", "detailed", "baseball", "football", "basketball")
        use_step2_architecture: Whether to use Step 2 slim prompt + assistant messages (default: True)
    
    Yields:
        str: Event-formatted chunks containing both text and structured JSON deltas.
    """
    try:
        # Check model compatibility
        model_compat = check_model_compatibility(model)
        logger.info(f"Model compatibility check for {model}: {model_compat}")
        
        # Warn about potential compatibility issues
        if not model_compat.get("recommended", False):
            logger.warning(f"Model {model} is not recommended for production use")
            
        if enable_web_search and not model_compat.get("web_search", False):
            logger.warning(f"Web search may not be fully supported by model {model}")
            
        if use_step2_architecture and not model_compat.get("step2_architecture", False):
            logger.warning(f"Step 2 architecture may not be fully supported by model {model}")
            logger.info(f"Automatically adjusting to use simpler prompt architecture for {model}")
            use_step2_architecture = False  # Fall back to simpler architecture
        
        # Get appropriate system instructions
        if instructions is None:
            instructions = prompt_loader.get_system_prompt(prompt_type, use_slim_prompt=use_step2_architecture)
        
        # Prepare the input for OpenAI Responses API
        api_input = None
        response_id = None
        
        if previous_response_id:
            # Use previous response ID for conversation continuity
            # When using previous_response_id, we only need the new user message
            if conversation_messages and len(conversation_messages) > 0:
                # Get the latest user message
                latest_message = conversation_messages[-1]
                api_input = latest_message.get('content', prompt or '')
            else:
                api_input = prompt or ''
        elif conversation_messages and len(conversation_messages) > 0:
            # Use full conversation history when no previous_response_id
            if use_step2_architecture:
                # Step 2: Build conversation messages with slim system prompt + assistant workflow
                # Don't use the conversation_messages directly - rebuild with our structure
                user_prompt = conversation_messages[-1].get('content', prompt or '') if conversation_messages else prompt
                api_input = prompt_loader.build_conversation_messages(
                    user_prompt=user_prompt,
                    system_prompt=instructions,
                    schema=StructuredAdvice.model_json_schema(),
                    enable_web_search=enable_web_search,
                    use_slim_prompt=True
                )
            else:
                # Legacy: Use conversation messages as-is
                api_input = conversation_messages
        else:
            # Fallback to building prompt
            if use_step2_architecture:
                # Step 2: Use conversation message format
                api_input = prompt_loader.build_conversation_messages(
                    user_prompt=prompt,
                    system_prompt=instructions,
                    schema=StructuredAdvice.model_json_schema(),
                    enable_web_search=enable_web_search,
                    use_slim_prompt=True
                )
            else:
                # Legacy: Single prompt string
                full_prompt = prompt_loader.build_full_prompt(
                    user_prompt=prompt,
                    system_prompt=instructions,
                    schema=StructuredAdvice.model_json_schema(),
                    enable_web_search=enable_web_search
                )
                api_input = full_prompt
        
        logger.info(f"Streaming request to OpenAI Responses API model: {model}")
        logger.info(f"Using previous_response_id: {previous_response_id is not None}")
        logger.info(f"Using Step 2 architecture: {use_step2_architecture}")
        
        # Log the API input structure for debugging
        if isinstance(api_input, list):
            logger.info(f"API input is a list with {len(api_input)} items")
            for i, item in enumerate(api_input):
                logger.info(f"API input item {i}: {str(item)[:100]}...")
        else:
            logger.info(f"API input is a string: {str(api_input)[:100]}...")
        
        # Prepare tools including PyBaseball integration
        tools = []

        # Add web search if enabled
        if enable_web_search:
            tools.append({
                "type": "web_search"
            })

        # Add PyBaseball tools
        tools.extend([
            {
                "type": "function",
                "name": "get_mlb_player_stats",
                "description": "Get season statistics for a specific MLB player",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "player_name": {
                            "type": "string",
                            "description": "Full name of the player (e.g., 'Shohei Ohtani')"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Season year (optional, defaults to current year)"
                        }
                    },
                    "required": ["player_name"]
                }
            },
            {
                "type": "function",
                "name": "get_mlb_standings",
                "description": "Get current MLB standings by division",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "Season year (optional)"
                        }
                    }
                }
            },
            {
                "type": "function",
                "name": "search_mlb_players",
                "description": "Search for MLB players by partial name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_term": {
                            "type": "string",
                            "description": "Partial name to search for"
                        }
                    },
                    "required": ["search_term"]
                }
            }
        ])
        
        # Build the API call parameters
        api_params = {
            "model": model,
            "input": api_input,
            "stream": True,
            "max_output_tokens": max_tokens,
            "temperature": 0,  # Set temperature to 0 for deterministic responses
        }
        
        # Add tools if there are any
        if tools:
            api_params["tools"] = tools
        
        # Add previous response ID if provided
        if previous_response_id:
            api_params["previous_response_id"] = previous_response_id
        
        # Add instructions only for new conversations and legacy mode
        if not previous_response_id and instructions and not use_step2_architecture:
            api_params["instructions"] = instructions
        
        # Log the final API parameters for debugging
        logger.info(f"API parameters: model={model}, max_tokens={max_tokens}, tools={len(tools)}")
        
        # Use the correct Responses API call
        response = await async_client.responses.create(**api_params)
        
        accumulated_content = ""
        response_id_captured = None
        event_count = 0
        
        # ------------------------------------------------------------------
        # State for new-style function-call events (March 2025 API update)
        # ------------------------------------------------------------------
        func_call_name: Optional[str] = None          # Captures the tool name
        func_call_args_buffer: str = ""               # Accumulates argument chunks

        async for event in response:
            event_count += 1
            # Log every event for better debugging
            logger.info(f"Event #{event_count} type: {getattr(event, 'type', 'unknown')}, Event data: {event}")
            
            evt_type = getattr(event, 'type', None)

            # Capture response ID from the first event
            if evt_type == "response.created" and hasattr(event, 'response') and hasattr(event.response, 'id'):
                response_id_captured = event.response.id
                logger.info(f"Response ID captured: {response_id_captured}")
                yield f"event: status_update\ndata: {json.dumps({'status': 'created', 'message': 'Connecting...', 'response_id': response_id_captured})}\n\n"
                continue

            if evt_type == "response.web_search_call.searching":
                logger.info("Web search in progress")
                yield f"event: status_update\ndata: {json.dumps({'status': 'web_search_searching', 'message': 'Searching the web...'})}\n\n"
            elif evt_type == "response.output_text.delta":
                delta = event.delta
                accumulated_content += delta
                # Only log the first few deltas to avoid overwhelming logs
                if len(accumulated_content) < 200:
                    logger.info(f"Text delta received: '{delta}'")
                elif event_count % 10 == 0:
                    logger.info(f"Text delta milestone: {len(accumulated_content)} chars accumulated")
                yield f"event: text_delta\ndata: {json.dumps({'delta': delta})}\n\n"
            elif evt_type == "response.output_text.done":
                logger.info("Output text completed")
                continue
            elif evt_type == "response.created":
                logger.info("Response created event received")
                yield f"event: status_update\ndata: {json.dumps({'status': 'created', 'message': 'Connecting...'})}\n\n"
            elif evt_type == "response.in_progress":
                logger.info("Response in progress event")
                continue
            elif evt_type == "response.output_item.added":
                item_type = getattr(getattr(event, 'item', None), 'type', None)
                logger.info(f"Output item added: {item_type}")
                if item_type == 'web_search_call':
                    yield f"event: status_update\ndata: {json.dumps({'status': 'web_search_started', 'message': 'Starting web search...'})}\n\n"
                elif item_type == 'message':
                    yield f"event: status_update\ndata: {json.dumps({'status': 'message_start', 'message': 'Assistant is typing...'})}\n\n"
                else:
                    logger.info(f"Unknown output item type: {item_type}")
                continue
            elif evt_type == "response.web_search_call.in_progress":
                logger.info("Web search call in progress")
                continue
            elif evt_type == "response.web_search_call.completed":
                logger.info("Web search completed")
                yield f"event: status_update\ndata: {json.dumps({'status': 'web_search_completed', 'message': 'Web search completed.'})}\n\n"

            # --------------------------------------------------------------
            # NEW‑STYLE FUNCTION CALL EVENTS  (Responses API ≥ 2025‑03)
            # --------------------------------------------------------------
            elif evt_type in ("response.function_call.name", "response.function_call_name"):
                # Capture the name of the function/tool being invoked
                func_call_name = getattr(event, "name", None) or getattr(
                    getattr(event, "function_call", None), "name", None
                )
                logger.info(f"Function call name: {func_call_name}")
                if func_call_name:
                    yield (
                        "event: status_update\n"
                        f"data: {json.dumps({'status': 'function_call_started', 'message': f'Calling {func_call_name}...'})}\n\n"
                    )
                continue

            elif evt_type == "response.function_call_arguments.delta":
                # Arguments come in piecemeal; accumulate them
                delta_args = getattr(event, "delta", "")
                func_call_args_buffer += delta_args
                logger.info(f"Function call arguments delta: {delta_args}")
                continue

            elif evt_type == "response.function_call_arguments.done":
                # All arguments received – parse and execute the tool
                logger.info(f"Function call arguments complete: {func_call_args_buffer}")
                try:
                    args = json.loads(func_call_args_buffer or "{}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse function‑call arguments: {e}")
                    args = {}

                # Route to appropriate PyBaseball method
                result = None
                try:
                    if func_call_name == "get_mlb_player_stats":
                        result = await pybaseball_service.get_player_stats(
                            args.get("player_name"), args.get("year")
                        )
                    elif func_call_name == "get_mlb_standings":
                        result = await pybaseball_service.get_mlb_standings(
                            args.get("year")
                        )
                    elif func_call_name == "search_mlb_players":
                        result = await pybaseball_service.search_players(
                            args.get("search_term")
                        )

                    if result is not None:
                        logger.info(f"Tool result for {func_call_name}: {str(result)[:100]}...")
                        # Stream the tool result back to the client
                        yield (
                            "event: tool_result\n"
                            f"data: {json.dumps({'tool': func_call_name, 'result': result})}\n\n"
                        )
                        yield (
                            "event: status_update\n"
                            f"data: {json.dumps({'status': 'function_call_completed', 'message': f'{func_call_name} completed.'})}\n\n"
                        )
                except Exception as e:
                    logger.error(f"Error executing tool {func_call_name}: {e}")
                    yield (
                        "event: tool_error\n"
                        f"data: {json.dumps({'tool': func_call_name, 'error': str(e)})}\n\n"
                    )

                # Reset buffers for potential subsequent calls
                func_call_name = None
                func_call_args_buffer = ""
                continue

            # Legacy/old-style function-call event handlers:
            elif evt_type == "response.function_call":
                # Handle function calls to PyBaseball service
                if hasattr(event, 'function_call'):
                    func_call = event.function_call
                    func_name = func_call.name if hasattr(func_call, 'name') else ''
                    logger.info(f"Legacy function call: {func_name}")
                    
                    yield f"event: status_update\ndata: {json.dumps({'status': 'function_call_started', 'message': f'Calling {func_name}...'})}\n\n"
            elif evt_type == "response.function_call.done":
                # Handle completed function calls to PyBaseball service
                if hasattr(event, 'function_call'):
                    func_call = event.function_call
                    func_name = func_call.name if hasattr(func_call, 'name') else ''
                    args = json.loads(func_call.arguments) if hasattr(func_call, 'arguments') else {}
                    logger.info(f"Legacy function call completed: {func_name} with args: {args}")
                    
                    try:
                        result = None
                        
                        # Route to appropriate PyBaseball function
                        if func_name == "get_mlb_player_stats":
                            result = await pybaseball_service.get_player_stats(
                                args.get('player_name'),
                                args.get('year')
                            )
                        elif func_name == "get_mlb_standings":
                            result = await pybaseball_service.get_mlb_standings(
                                args.get('year')
                            )
                        elif func_name == "search_mlb_players":
                            result = await pybaseball_service.search_players(
                                args.get('search_term')
                            )
                        
                        if result:
                            logger.info(f"Legacy tool result for {func_name}: {str(result)[:100]}...")
                            # Stream the tool result back
                            yield f"event: tool_result\ndata: {json.dumps({'tool': func_name, 'result': result})}\n\n"
                            yield f"event: status_update\ndata: {json.dumps({'status': 'function_call_completed', 'message': f'{func_name} completed.'})}\n\n"
                            
                    except Exception as e:
                        logger.error(f"Error executing legacy tool {func_name}: {e}")
                        yield f"event: tool_error\ndata: {json.dumps({'tool': func_name, 'error': str(e)})}\n\n"
            elif evt_type == "response.output_item.done":
                item_type = getattr(getattr(event, 'item', None), 'type', None)
                logger.info(f"Output item done: {item_type}")
                if item_type == 'message':
                     # This event might be too quick before response_complete, but can be used.
                    yield f"event: status_update\ndata: {json.dumps({'status': 'message_generating_done', 'message': 'Finalizing response...'})}\n\n"
                else:
                    logger.debug(f"OpenAI response output item done (type: {item_type}): {event}")
                continue
            elif evt_type == "response.content_part.added":
                logger.info(f"Content part added: {event}")
                continue
            elif evt_type == "response.output_text.annotation.added":
                annotation_title = getattr(getattr(event, 'annotation', None), 'title', 'citation')
                logger.info(f"Annotation added: {annotation_title}")
                yield f"event: status_update\ndata: {json.dumps({'status': 'annotation_found', 'message': f'Processing {annotation_title}...'})}\n\n"
            elif evt_type == "response.content_part.done":
                logger.info(f"Content part done: {event}")
                continue
            elif evt_type == "response.completed":
                logger.info("Response completed, validating final content")
                try:
                    # Step 6: Schema validation before finalizing response
                    is_valid, error_msg = schema_validator.validate_streaming_chunk(
                        accumulated_content, is_complete=True
                    )
                    
                    if not is_valid:
                        logger.warning(f"Schema validation failed: {error_msg}")
                        # Create fallback response using schema validator
                        fallback_data = schema_validator.create_fallback_response(
                            accumulated_content, error_msg
                        )
                        final_data = {
                            'status': 'complete',
                            'final_json': fallback_data,
                            'response_id': response_id_captured,
                            'validation_error': error_msg
                        }
                        yield f"event: response_complete\ndata: {json.dumps(final_data)}\n\n"
                        break
                    
                    # Parse the validated content
                    if accumulated_content.strip().startswith('{'):
                        logger.info("Parsing accumulated content as JSON")
                        parsed_advice = StructuredAdvice.model_validate_json(accumulated_content)
                    else:
                        logger.info("Parsing accumulated content as plain text")
                        parsed_advice = StructuredAdvice(
                            main_advice=accumulated_content.strip(),
                            model_identifier=model
                        )
                    
                    # Final schema validation on the parsed object
                    advice_dict = parsed_advice.model_dump()
                    is_valid, error_msg = schema_validator.validate_json(advice_dict)
                    
                    if not is_valid:
                        logger.warning(f"Final schema validation failed: {error_msg}")
                        # Create fallback response
                        fallback_data = schema_validator.create_fallback_response(
                            accumulated_content, error_msg
                        )
                        final_data = {
                            'status': 'complete',
                            'final_json': fallback_data,
                            'response_id': response_id_captured,
                            'validation_error': error_msg
                        }
                    else:
                        logger.info("Schema validation passed, sending final response")
                        # Include response_id in the successful final response
                        final_data = {
                            'status': 'complete', 
                            'final_json': advice_dict,
                            'response_id': response_id_captured
                        }
                    
                    yield f"event: response_complete\ndata: {json.dumps(final_data)}\n\n"
                    
                except Exception as e:
                    logger.error(f"Failed to parse final response: {e}")
                    fallback_advice = schema_validator.create_fallback_response(
                        accumulated_content.strip() or "No response received",
                        f"Parse error: {e}"
                    )
                    final_data = {
                        'status': 'complete',
                        'final_json': fallback_advice,
                        'response_id': response_id_captured,
                        'parse_error': str(e)
                    }
                    yield f"event: response_complete\ndata: {json.dumps(final_data)}\n\n"
                break
            # Error or failure events
            elif evt_type in ("response.error", "response.failed") or hasattr(event, 'error'):
                err_msg = getattr(event, 'error', None)
                if err_msg is None and hasattr(event, 'message'): # Check for message attribute if error is not present
                    err_msg = event.message
                err_text = str(err_msg) if err_msg else "Unknown error" # Ensure err_text is always a string
                logger.error(f"OpenAI API error: {err_text}")
                yield f"event: error\ndata: {json.dumps({'error': 'API_ERROR', 'message': err_text})}\n\n"
                break
            else:
                logger.warning(f"Unhandled event type: {evt_type}, Event: {event}")
                # Try to handle the unknown event generically
                yield f"event: status_update\ndata: {json.dumps({'status': 'unknown_event', 'message': f'Received event: {evt_type}'})}\n\n"

        logger.info(f"Stream completed with {event_count} total events")
        # If we exited the loop without any events, that's a problem
        if event_count == 0:
            logger.error("No events received from OpenAI API")
            yield f"event: error\ndata: {json.dumps({'error': 'NO_EVENTS', 'message': 'No events received from the API'})}\n\n"

    except APIConnectionError as e:
        logger.error(f"OpenAI API request failed to connect: {e}")
        yield f"event: error\ndata: {json.dumps({'error': 'CONNECTION_ERROR', 'message': str(e)})}\n\n"
    except RateLimitError as e:
        logger.error(f"OpenAI API request exceeded rate limit: {e}")
        yield f"event: error\ndata: {json.dumps({'error': 'RATE_LIMIT_ERROR', 'message': str(e)})}\n\n"
    except AuthenticationError as e:
        logger.error(f"OpenAI API authentication failed: {e}")
        yield f"event: error\ndata: {json.dumps({'error': 'AUTH_ERROR', 'message': str(e)})}\n\n"
    except APIError as e:
        logger.error(f"OpenAI API returned an API Error: {e}")
        yield f"event: error\ndata: {json.dumps({'error': 'API_ERROR', 'message': str(e)})}\n\n"
    except BadRequestError as e:
        logger.error(f"OpenAI API bad request error: {e}")
        yield f"event: error\ndata: {json.dumps({'error': 'BAD_REQUEST', 'message': str(e)})}\n\n"
    except NotFoundError as e:
        logger.error(f"OpenAI API resource not found: {e}")
        yield f"event: error\ndata: {json.dumps({'error': 'NOT_FOUND', 'message': str(e)})}\n\n"
    except Exception as e:
        logger.error(f"An unexpected error occurred while streaming: {type(e).__name__}: {e}")
        yield f"event: error\ndata: {json.dumps({'error': 'UNEXPECTED_ERROR', 'message': f"{type(e).__name__}: {str(e)}"})}\n\n"


# Existing get_response function (non-streaming, uses synchronous client.responses.create)
def get_response(
    prompt: str,
    model: str = OPENAI_DEFAULT_MODEL_INTERNAL,
    instructions: str = None, 
    max_tokens: int = 2000,
    enable_web_search: bool = True,
    prompt_type: str = "default"
) -> StructuredAdvice:
    """
    Gets a non-streaming response from OpenAI's Responses API.
    
    Args:
        prompt_type: Type of prompt to use from config ("default", "detailed", "baseball", "football", "basketball")
    """
    try:
        # Get appropriate system instructions
        if instructions is None:
            instructions = prompt_loader.get_system_prompt(prompt_type)
        
        # Build the complete prompt using the new modular system
        full_prompt = prompt_loader.build_full_prompt(
            user_prompt=prompt,
            system_prompt=instructions,
            schema=StructuredAdvice.model_json_schema(),
            enable_web_search=enable_web_search
        )
        
        logger.info(f"Request to OpenAI Responses API model: {model}")
        
        # Prepare tools including PyBaseball integration
        tools = []

        # Add web search if enabled
        if enable_web_search:
            tools.append({
                "type": "web_search"
            })

        # Add PyBaseball tools
        tools.extend([
            {
                "type": "function",
                "name": "get_mlb_player_stats",
                "description": "Get season statistics for a specific MLB player",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "player_name": {
                            "type": "string",
                            "description": "Full name of the player (e.g., 'Shohei Ohtani')"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Season year (optional, defaults to current year)"
                        }
                    },
                    "required": ["player_name"]
                }
            },
            {
                "type": "function",
                "name": "get_mlb_standings",
                "description": "Get current MLB standings by division",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "Season year (optional)"
                        }
                    }
                }
            },
            {
                "type": "function",
                "name": "search_mlb_players",
                "description": "Search for MLB players by partial name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_term": {
                            "type": "string",
                            "description": "Partial name to search for"
                        }
                    },
                    "required": ["search_term"]
                }
            }
        ])
        
        response = client.responses.create(
            model=model,
            input=full_prompt,
            stream=False,
            max_output_tokens=max_tokens,
            tools=tools if tools else None,
            temperature=0  # Set temperature to 0 for deterministic responses
        )
        
        # Extract content from response
        if response.output and len(response.output) > 0:
            for output_item in response.output:
                if hasattr(output_item, 'content') and output_item.content:
                    for content_item in output_item.content:
                        if hasattr(content_item, 'text'):
                            response_text = content_item.text
                            
                            # Try to parse as JSON first
                            try:
                                if response_text.strip().startswith('{'):
                                    parsed_advice = StructuredAdvice.model_validate_json(response_text)
                                    if parsed_advice.model_identifier is None:
                                        parsed_advice.model_identifier = model
                                    return parsed_advice
                            except:
                                pass
                            
                            # Fallback: create structured advice from text
                            return StructuredAdvice(
                                main_advice=response_text.strip(),
                                model_identifier=model
                            )
        
        # Fallback error case
        return StructuredAdvice(
            main_advice="Error: No valid response received from OpenAI",
            reasoning="The API response was empty or malformed"
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from OpenAI response: {e}")
        return StructuredAdvice(main_advice=f"Error: Failed to decode JSON response. {e}")
    except APIConnectionError as e:
        logger.error(f"OpenAI API request failed to connect: {e}")
        return StructuredAdvice(main_advice=f"Error: API Connection Error. {e}")
    except RateLimitError as e:
        logger.error(f"OpenAI API request exceeded rate limit: {e}")
        return StructuredAdvice(main_advice=f"Error: Rate Limit Exceeded. {e}")
    except AuthenticationError as e:
        logger.error(f"OpenAI API authentication failed: {e}")
        return StructuredAdvice(main_advice=f"Error: Authentication Failed. {e}")
    except APIError as e:
        logger.error(f"OpenAI API returned an API Error: {e}")
        return StructuredAdvice(main_advice=f"Error: OpenAI API Error. {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return StructuredAdvice(main_advice=f"Error: An unexpected error occurred. {e}")


# Add a test function at the end of the file
async def test_openai_connectivity(model: str = OPENAI_DEFAULT_MODEL_INTERNAL) -> dict:
    """
    Tests the connectivity to OpenAI API with a simple request.
    
    Args:
        model: The model to test with (defaults to the configured default model)
        
    Returns:
        dict: Response information including success status and any error details
    """
    try:
        logger.info(f"Testing OpenAI connectivity with model: {model}")
        response = await async_client.responses.create(
            model=model,
            input="Hello, this is a test message. Please respond with 'API connection successful'.",
            stream=False,
            max_output_tokens=50,
            temperature=0
        )
        
        # Extract basic response info
        response_text = None
        if response.output and len(response.output) > 0:
            for output_item in response.output:
                if hasattr(output_item, 'content') and output_item.content:
                    for content_item in output_item.content:
                        if hasattr(content_item, 'text'):
                            response_text = content_item.text
                            break
                    if response_text:
                        break
        
        # Compile results
        result = {
            "success": True,
            "model": model,
            "response_id": response.id if hasattr(response, 'id') else None,
            "response_text": response_text,
            "usage": {
                "input_tokens": response.usage.input_tokens if hasattr(response, 'usage') else None,
                "output_tokens": response.usage.output_tokens if hasattr(response, 'usage') else None,
                "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None
            }
        }
        logger.info(f"OpenAI connectivity test successful: {result}")
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "model": model,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }
        logger.error(f"OpenAI connectivity test failed: {error_result}")
        return error_result

