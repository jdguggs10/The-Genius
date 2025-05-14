import os
from openai import OpenAI
from typing import Tuple
 
import logging

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
    temperature: float = 0.7
) -> Tuple[str, str]:
    """
    Sends a prompt to the OpenAI Responses API using GPT-4.1 and returns the assistant's reply.
    
    Args:
        prompt: The user's input text
        model: The OpenAI model to use (default is gpt-4.1)
        max_tokens: Maximum number of tokens to generate
        temperature: Controls randomness (0-1)
        
    Returns:
        Tuple containing:
        - The text response from the AI
        - The model name used
    """
    try:
        # Using the Responses API with GPT-4.1
        resp = client.responses.create(
            model=model,
            instructions=instructions,
            input=prompt,
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
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
