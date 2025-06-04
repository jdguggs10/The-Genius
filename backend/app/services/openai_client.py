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
        
        # Prepare tools including PyBaseball integration
        tools = []

        # Add web search if enabled
        if enable_web_search:
            tools.append({
                "type": "web_search",
                "name": "web_search"
            })

        # Add PyBaseball tools
        tools.extend([
            {
                "type": "function",
                "function": {
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
                }
            },
            {
                "type": "function",
                "function": {
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
                }
            },
            {
                "type": "function",
                "function": {
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
            }
        ])
        
        # Build the API call parameters
        api_params = {
            "model": model,
            "input": api_input,
            "stream": True,
            "max_output_tokens": max_tokens,
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
        
        # Use the correct Responses API call
        response = await async_client.responses.create(**api_params)
        
        accumulated_content = ""
        response_id_captured = None
        
        async for event in response:
            logger.debug(f"Received event type: {getattr(event, 'type', 'unknown')}, Event: {event}") 
            evt_type = getattr(event, 'type', None)

            # Capture response ID from the first event
            if evt_type == "response.created" and hasattr(event, 'response') and hasattr(event.response, 'id'):
                response_id_captured = event.response.id
                yield f"event: status_update\ndata: {json.dumps({'status': 'created', 'message': 'Connecting...', 'response_id': response_id_captured})}\n\n"
                continue

            if evt_type == "response.web_search_call.searching":
                yield f"event: status_update\ndata: {json.dumps({'status': 'web_search_searching', 'message': 'Searching the web...'})}\n\n"
            elif evt_type == "response.output_text.delta":
                delta = event.delta
                accumulated_content += delta
                yield f"event: text_delta\ndata: {json.dumps({'delta': delta})}\n\n"
            elif evt_type == "response.output_text.done":
                continue
            elif evt_type == "response.created":
                yield f"event: status_update\ndata: {json.dumps({'status': 'created', 'message': 'Connecting...'})}\n\n"
            elif evt_type == "response.in_progress":
                logger.debug(f"OpenAI response stream in progress: {event}") # Potentially noisy for UI
                continue
            elif evt_type == "response.output_item.added":
                item_type = getattr(getattr(event, 'item', None), 'type', None)
                if item_type == 'web_search_call':
                    yield f"event: status_update\ndata: {json.dumps({'status': 'web_search_started', 'message': 'Starting web search...'})}\n\n"
                elif item_type == 'message':
                    yield f"event: status_update\ndata: {json.dumps({'status': 'message_start', 'message': 'Assistant is typing...'})}\n\n"
                else:
                    logger.debug(f"OpenAI response output item added (type: {item_type}): {event}")
                continue
            elif evt_type == "response.web_search_call.in_progress":
                logger.debug(f"OpenAI web search call in progress: {event}") # Covered by 'searching' for UI
                continue
            elif evt_type == "response.web_search_call.completed":
                yield f"event: status_update\ndata: {json.dumps({'status': 'web_search_completed', 'message': 'Web search completed.'})}\n\n"
            elif evt_type == "response.function_call":
                # Handle function calls to PyBaseball service
                if hasattr(event, 'function_call'):
                    func_call = event.function_call
                    func_name = func_call.name if hasattr(func_call, 'name') else ''
                    
                    yield f"event: status_update\ndata: {json.dumps({'status': 'function_call_started', 'message': f'Calling {func_name}...'})}\n\n"
            elif evt_type == "response.function_call.done":
                # Handle completed function calls to PyBaseball service
                if hasattr(event, 'function_call'):
                    func_call = event.function_call
                    func_name = func_call.name if hasattr(func_call, 'name') else ''
                    args = json.loads(func_call.arguments) if hasattr(func_call, 'arguments') else {}
                    
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
                            # Stream the tool result back
                            yield f"event: tool_result\ndata: {json.dumps({'tool': func_name, 'result': result})}\n\n"
                            yield f"event: status_update\ndata: {json.dumps({'status': 'function_call_completed', 'message': f'{func_name} completed.'})}\n\n"
                            
                    except Exception as e:
                        logger.error(f"Error executing tool {func_name}: {e}")
                        yield f"event: tool_error\ndata: {json.dumps({'tool': func_name, 'error': str(e)})}\n\n"
            elif evt_type == "response.output_item.done":
                item_type = getattr(getattr(event, 'item', None), 'type', None)
                if item_type == 'message':
                     # This event might be too quick before response_complete, but can be used.
                    yield f"event: status_update\ndata: {json.dumps({'status': 'message_generating_done', 'message': 'Finalizing response...'})}\n\n"
                else:
                    logger.debug(f"OpenAI response output item done (type: {item_type}): {event}")
                continue
            elif evt_type == "response.content_part.added":
                logger.debug(f"OpenAI response content part added: {event}")
                continue
            elif evt_type == "response.output_text.annotation.added":
                annotation_title = getattr(getattr(event, 'annotation', None), 'title', 'citation')
                yield f"event: status_update\ndata: {json.dumps({'status': 'annotation_found', 'message': f'Processing {annotation_title}...'})}\n\n"
            elif evt_type == "response.content_part.done":
                logger.debug(f"OpenAI response content part done: {event}")
                continue
            elif evt_type == "response.completed":
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
                        parsed_advice = StructuredAdvice.model_validate_json(accumulated_content)
                    else:
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
    except Exception as e:
        logger.error(f"An unexpected error occurred while streaming: {e}")
        yield f"event: error\ndata: {json.dumps({'error': 'UNEXPECTED_ERROR', 'message': str(e)})}\n\n"


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
                "type": "web_search",
                "name": "web_search"
            })

        # Add PyBaseball tools
        tools.extend([
            {
                "type": "function",
                "function": {
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
                }
            },
            {
                "type": "function",
                "function": {
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
                }
            },
            {
                "type": "function",
                "function": {
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
            }
        ])
        
        response = client.responses.create(
            model=model,
            input=full_prompt,
            stream=False,
            max_output_tokens=max_tokens,
            tools=tools if tools else None
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

