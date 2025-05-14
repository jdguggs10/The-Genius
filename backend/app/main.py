from fastapi import FastAPI, Query

from app.models import AdviceRequest, AdviceResponse
from app.services.openai_client import get_response  # Only import the new function

app = FastAPI()


@app.post("/advice", response_model=AdviceResponse)
async def get_advice(body: AdviceRequest) -> AdviceResponse:
    """
    Echoes advice back from the OpenAI Responses API using GPT-4.1.

    • Expects `AdviceRequest` with a `conversation` list.
    • Uses the last user message as the prompt.
    • Returns an `AdviceResponse` with the model's reply.
    """
    # Get the model name if specified in the request, otherwise use default (gpt-4.1)
    model_name = body.model if body.model else "gpt-4.1"
    
    # Call the helper function with the specified model
    reply, model_used = get_response(body.conversation[-1].content, model=model_name)
    return AdviceResponse(reply=reply, model=model_used)


@app.post("/custom-advice", response_model=AdviceResponse)
async def get_custom_advice(
    body: AdviceRequest, 
    model: str = Query("gpt-4.1", description="OpenAI model to use (e.g., gpt-4.1)")
) -> AdviceResponse:
    """
    Similar to /advice but allows specifying which OpenAI model to use.
    
    • Expects `AdviceRequest` with a `conversation` list.
    • Uses the last user message as the prompt.
    • Allows specifying the model via query parameter.
    • Returns an `AdviceResponse` with the model's reply.
    """
    reply, model_used = get_response(body.conversation[-1].content, model=model)
    return AdviceResponse(reply=reply, model=model_used)