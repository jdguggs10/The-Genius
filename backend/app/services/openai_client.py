import os
from dotenv import load_dotenv
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError, NotFoundError, BadRequestError
from typing import Tuple, Dict, List, Optional, Any
 
import logging

# Load environment variables from .env file
load_dotenv()

logging.getLogger(__name__).addHandler(logging.NullHandler()) # Add NullHandler if this is a library module to avoid "No handler found" warnings if not configured by app.
# However, since this service is part of an app that does configure logging, 
# just getting the logger is fine.
logger = logging.getLogger(__name__)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY environment variable is not set")
    raise EnvironmentError("Missing OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# Define the default model by checking environment variable first, then fallback
OPENAI_DEFAULT_MODEL_INTERNAL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4.1")

def get_response(
    prompt: str,
    model: str = OPENAI_DEFAULT_MODEL_INTERNAL, # Use the resolved default
    instructions: str = "You are a helpful assistant.",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    enable_web_search: bool = False
) -> Tuple[str, str]:
    """
    Sends a prompt to the OpenAI Responses API using GPT-4.1 and returns the assistant's reply.
    
    Args:
        prompt: The user's input text
        model: The OpenAI model to use (default is gpt-4.1)
        instructions: System instructions for the model
        max_tokens: Maximum number of tokens to generate
        temperature: Controls randomness (0-1)
        enable_web_search: Whether to enable the web search tool
        
    Returns:
        Tuple containing:
        - The text response from the AI
        - The model name used
    """
    try:
        # Define parameters for the API call
        # Use higher token limit for web search responses as they tend to be longer
        actual_max_tokens = max_tokens if not enable_web_search else max(max_tokens, 1500)
        
        params = {
            "model": model,
            "instructions": instructions,
            "input": prompt,
            "max_output_tokens": actual_max_tokens,
            "temperature": temperature,
        }
        
        # Add web search tool if enabled
        if enable_web_search:
            logger.info("Enabling web search tool for this request")
            # Define the web search tool (updated for GPT 4.1 compatibility)
            web_search_tool = {
                "type": "web_search_preview"
            }
            params["tools"] = [web_search_tool]
            logger.info(f"Web search tool added to params: {params['tools']}")
        else:
            logger.info("Web search not enabled for this request")
        
        # Call the OpenAI Responses API
        logger.info(f"Making OpenAI API call with params: {params}")
        resp = client.responses.create(**params)
        
        status = getattr(resp, "http_response", None)
        if status:
            logger.info(f"OpenAI API response status code: {status.status_code}")
        else:
            logger.info("OpenAI API response received")
            
        # Log model information
        actual_model = getattr(resp, "model", model)
        logger.info(f"Response generated using model: {actual_model}")
        
    except APIConnectionError as e:
        logger.error(f"OpenAI API Connection Error with model {model}: {e}")
        # Potentially retry or handle specific connection issues here
        raise
    except RateLimitError as e:
        logger.error(f"OpenAI API Rate Limit Exceeded with model {model}: {e}")
        # Potentially implement backoff strategy here or inform user
        raise
    except AuthenticationError as e:
        logger.error(f"OpenAI API Authentication Error with model {model}: {e}. Check your API key.")
        # This is a critical configuration error
        raise
    except NotFoundError as e:
        logger.error(f"OpenAI API Not Found Error (e.g., model not found) with model {model}: {e}")
        raise
    except BadRequestError as e: # Covers invalid requests, malformed inputs etc.
        logger.error(f"OpenAI API Invalid Request Error with model {model}: {e}. Input: {prompt[:100]}...", exc_info=True)
        # It might be useful to log details of the request that caused this
        raise
    except APIError as e: # Catch other generic OpenAI API errors
        logger.error(f"Generic OpenAI API Error with model {model}: {e}", exc_info=True)
        raise
    except Exception as e: # Catch any other unexpected errors
        logger.error(f"Unexpected error calling OpenAI API with model {model}: {e}", exc_info=True)
        raise
    
    # Extract the text response from the Responses API
    # Try multiple ways to get the response text
    response_text = "No response generated"
    
    # Method 1: Try output_text field (some responses have this)
    if hasattr(resp, 'output_text') and resp.output_text:
        response_text = resp.output_text
        logger.info("Used output_text field for response")
    
    # Method 2: Try output[0].content[0].text structure
    elif hasattr(resp, 'output') and resp.output and len(resp.output) > 0:
        output_item = resp.output[0]
        if hasattr(output_item, 'content') and output_item.content and len(output_item.content) > 0:
            content_item = output_item.content[0]
            if hasattr(content_item, 'text'):
                response_text = content_item.text
                logger.info("Used output[0].content[0].text structure for response")
        
        # Method 3: Try to get text from message type output
        elif hasattr(output_item, 'type') and output_item.type == 'message':
            if hasattr(output_item, 'content') and output_item.content:
                for content in output_item.content:
                    if hasattr(content, 'text'):
                        response_text = content.text
                        logger.info("Used message content text for response")
                        break
    
    # Method 4: Last resort - convert to string
    if response_text == "No response generated" and hasattr(resp, 'output'):
        response_text = str(resp.output)
        logger.info("Used string conversion as fallback for response")
    
    logger.info(f"Final response text length: {len(response_text)}")
    return response_text, actual_model

if __name__ == "__main__":
    system_prompt = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")
    print("Starting chat. Type 'exit' to quit.")
    print("Type 'search:' before your question to enable web search")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
            
        # Check if user wants to enable web search
        enable_search = False
        if user_input.lower().startswith("search:"):
            enable_search = True
            user_input = user_input[7:].strip()  # Remove "search:" prefix
            print("Web search enabled for this question.")
        
        # The model parameter will use OPENAI_DEFAULT_MODEL_INTERNAL if not overridden
        response_text, used_model = get_response(
            prompt=user_input,
            instructions=system_prompt,
            enable_web_search=enable_search
        )
        print(f"Bot ({used_model}): {response_text}")