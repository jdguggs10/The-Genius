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
SYSTEM_DEFAULT_INSTRUCTIONS = os.getenv("SYSTEM_PROMPT", "You are a helpful fantasy sports assistant with deep knowledge of player performance, matchups, and strategy.")

async def get_streaming_response(
    prompt: str,
    model: str = OPENAI_DEFAULT_MODEL_INTERNAL,
    instructions: str = SYSTEM_DEFAULT_INSTRUCTIONS,
    max_tokens: int = 2000,
    enable_web_search: bool = False
) -> AsyncGenerator[str, None]:
    """
    Gets a streaming response from OpenAI's Responses API with structured JSON output.
    
    Yields:
        str: Event-formatted chunks containing both text and structured JSON deltas.
    """
    try:
        # Build the input prompt with instructions
        full_prompt = f"{instructions}\n\nUser: {prompt}\n\nPlease respond with structured JSON that matches this schema: {StructuredAdvice.model_json_schema()}"
        
        logger.info(f"Streaming request to OpenAI Responses API model: {model}")
        
        # Prepare tools if web search is enabled
        tools = [{"type": "web_search"}] if enable_web_search else None
        
        # Use the correct Responses API call
        response = await async_client.responses.create( # Reverted name from response_stream
            model=model,
            input=full_prompt,
            stream=True,
            max_output_tokens=max_tokens,
            tools=tools
        )
        
        accumulated_content = ""
        
        async for event in response:
            # Restored original debug logging and event type handling
            logger.debug(f"Received event type: {getattr(event, 'type', 'unknown')}, Event: {event}") 
            evt_type = getattr(event, 'type', None)

            # Web search in-progress event
            if evt_type == "response.web_search_call.searching":
                yield f"event: web_search\ndata: {json.dumps({'status': 'searching', 'message': 'Searching the web for current information...'})}\n\n"
            # Text delta events
            elif evt_type == "response.output_text.delta":
                delta = event.delta # Assumes event.delta exists
                accumulated_content += delta
                yield f"event: text_delta\ndata: {json.dumps({'delta': delta})}\n\n"
            # Text done events (skip)
            elif evt_type == "response.output_text.done":
                continue
            # Final completion event
            elif evt_type == "response.completed":
                try:
                    if accumulated_content.strip().startswith('{'):
                        parsed_advice = StructuredAdvice.model_validate_json(accumulated_content)
                    else:
                        parsed_advice = StructuredAdvice(
                            main_advice=accumulated_content.strip(),
                            model_identifier=model
                        )
                    yield f"event: response_complete\ndata: {json.dumps({'status': 'complete', 'final_json': parsed_advice.model_dump()})}\n\n"
                except Exception as e:
                    logger.error(f"Failed to parse final response: {e}")
                    fallback_advice = StructuredAdvice(
                        main_advice=accumulated_content.strip() or "No response received",
                        reasoning="Failed to parse structured response",
                        model_identifier=model
                    )
                    yield f"event: response_complete\ndata: {json.dumps({'status': 'complete', 'final_json': fallback_advice.model_dump()})}\n\n"
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
    instructions: str = SYSTEM_DEFAULT_INSTRUCTIONS, 
    max_tokens: int = 2000,
    enable_web_search: bool = False
) -> StructuredAdvice:
    """
    Gets a non-streaming response from OpenAI's Responses API.
    """
    try:
        # Build the input prompt with instructions
        full_prompt = f"{instructions}\n\nUser: {prompt}\n\nPlease respond with structured JSON that matches this schema: {StructuredAdvice.model_json_schema()}"
        
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