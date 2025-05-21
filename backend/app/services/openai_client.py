import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Tuple, Dict, List, Optional, Any
 
import logging

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("OPENAI_API_KEY environment variable is not set")
    raise EnvironmentError("Missing OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def get_response(
    prompt: str,
    model: str = "gpt-4.1",
    instructions: str = "You are a helpful assistant.",
    max_tokens: int = 150,
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
        params = {
            "model": model,
            "instructions": instructions,
            "input": prompt,
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        
        # Add web search tool if enabled
        if enable_web_search:
            logging.info("Enabling web search tool for this request")
            # Define the web search tool
            web_search_tool = {
                "type": "web_search"
            }
            params["tools"] = [web_search_tool]
        
        # Call the OpenAI Responses API
        resp = client.responses.create(**params)
        
        status = getattr(resp, "http_response", None)
        if status:
            logging.info(f"OpenAI API response status code: {status.status_code}")
        else:
            logging.info("OpenAI API response received")
            
        # Log model information
        actual_model = getattr(resp, "model", model)
        logging.info(f"Response generated using model: {actual_model}")
        
    except Exception as e:
        logging.error(f"Error calling OpenAI API with {model}: {e}")
        raise
    
    # Extract the text response from the Responses API
    return resp.output_text, actual_model

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
        
        response_text, used_model = get_response(
            prompt=user_input,
            instructions=system_prompt,
            enable_web_search=enable_search
        )
        print(f"Bot ({used_model}): {response_text}")