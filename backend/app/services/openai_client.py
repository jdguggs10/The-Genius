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
    previous_response_id: str = None
) -> AsyncGenerator[str, None]:
    """
    Gets a streaming response from OpenAI's Responses API with structured JSON output.
    
    Args:
        prompt: User prompt (for backward compatibility)
        conversation_messages: List of conversation messages (role/content dicts)
        previous_response_id: OpenAI response ID for conversation continuity
        prompt_type: Type of prompt to use from config ("default", "detailed", "baseball", "football", "basketball")
    
    Yields:
        str: Event-formatted chunks containing both text and structured JSON deltas.
    """
    try:
        # Get appropriate system instructions
        if instructions is None:
            instructions = prompt_loader.get_system_prompt(prompt_type)
        
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
            api_input = conversation_messages
        else:
            # Fallback to building full prompt (backward compatibility)
            full_prompt = prompt_loader.build_full_prompt(
                user_prompt=prompt,
                system_prompt=instructions,
                schema=StructuredAdvice.model_json_schema(),
                enable_web_search=enable_web_search
            )
            api_input = full_prompt
        
        logger.info(f"Streaming request to OpenAI Responses API model: {model}")
        logger.info(f"Using previous_response_id: {previous_response_id is not None}")
        
        # Prepare tools if web search is enabled
        tools = [{"type": "web_search"}] if enable_web_search else None
        
        # Build the API call parameters
        api_params = {
            "model": model,
            "input": api_input,
            "stream": True,
            "max_output_tokens": max_tokens,
        }
        
        # Add tools if enabled
        if tools:
            api_params["tools"] = tools
            
        # Add previous response ID if provided
        if previous_response_id:
            api_params["previous_response_id"] = previous_response_id
        
        # Add instructions only for new conversations (not when using previous_response_id)
        if not previous_response_id and instructions:
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
                    if accumulated_content.strip().startswith('{'):
                        parsed_advice = StructuredAdvice.model_validate_json(accumulated_content)
                    else:
                        parsed_advice = StructuredAdvice(
                            main_advice=accumulated_content.strip(),
                            model_identifier=model
                        )
                    
                    # Include response_id in the final response
                    final_data = {
                        'status': 'complete', 
                        'final_json': parsed_advice.model_dump(),
                        'response_id': response_id_captured
                    }
                    yield f"event: response_complete\ndata: {json.dumps(final_data)}\n\n"
                except Exception as e:
                    logger.error(f"Failed to parse final response: {e}")
                    fallback_advice = StructuredAdvice(
                        main_advice=accumulated_content.strip() or "No response received",
                        reasoning="Failed to parse structured response",
                        model_identifier=model
                    )
                    final_data = {
                        'status': 'complete',
                        'final_json': fallback_advice.model_dump(),
                        'response_id': response_id_captured
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
        
        # Prepare tools if web search is enabled
        tools = [{"type": "web_search"}] if enable_web_search else None
        
        response = client.responses.create(
            model=model,
            input=full_prompt,
            stream=False,
            max_output_tokens=max_tokens,
            tools=tools
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

# Example usage for CLI testing (if __name__ == "__main__")
async def main_cli():
    print("Starting CLI for OpenAI Fantasy Sports Assistant...")
    print("Using model:", OPENAI_DEFAULT_MODEL_INTERNAL)
    print("Type 'exit' to quit, or 'searchon'/'searchoff' to toggle web search (currently illustrative).")
    
    enable_search_cli = False # Default search to off

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            if user_input.lower() == "searchon":
                enable_search_cli = True
                print("Web search (illustrative) is ON for next query.")
                continue
            if user_input.lower() == "searchoff":
                enable_search_cli = False
                print("Web search (illustrative) is OFF for next query.")
                continue
            
            # --- Streaming Response Example (Commented out by default) ---
            # print("\nAI Assistant (Streaming JSON Chunks):")
            # accumulated_json = []
            # async for chunk in get_streaming_response(user_input, enable_web_search=enable_search_cli):
            #     print(chunk, end="", flush=True)
            #     accumulated_json.append(chunk)
            # print("\n--- End of Stream ---")
            # try:
            #     full_json_str = "".join(accumulated_json)
            #     if full_json_str.strip(): # Ensure not empty
            #         parsed_streamed_advice = StructuredAdvice.model_validate_json(full_json_str)
            #         print("\nParsed Streamed Advice:")
            #         print(parsed_streamed_advice.model_dump_json(indent=2))
            #     else:
            #         print("\nStream produced no JSON content.")
            # except json.JSONDecodeError as e:
            #     print(f"\nError decoding streamed JSON: {e}")
            #     print(f"Received: {full_json_str}")
            # except Exception as e:
            #     print(f"\nError processing streamed response: {e}")
            # print("\n")
            
            # --- Non-Streaming Response Example (Default for CLI) ---
            print("\nAI Assistant (Structured JSON Response):")
            response_obj = get_response(user_input, enable_web_search=enable_search_cli)
            if response_obj: # Should always be a StructuredAdvice object due to error handling
                print(response_obj.model_dump_json(indent=2))
            else:
                # This case should ideally not be reached if get_response always returns a StructuredAdvice
                print("Error: No response object received.")
            print("\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"CLI Error: {e}")
            logger.exception("Exception in CLI loop")

if __name__ == "__main__":
    import asyncio
    # To run the async main_cli in a synchronous context if this file is run directly
    # For Python 3.7+
    try:
        asyncio.run(main_cli())
    except KeyboardInterrupt:
        print("Exiting via KeyboardInterrupt...")
    except Exception as e:
        print(f"Unhandled error in CLI: {e}")
        logger.error(f"Unhandled error in CLI execution: {e}", exc_info=True)