from fastapi import FastAPI, Query

from app.models import AdviceRequest, AdviceResponse
from app.services.openai_client import get_response  # Only import the new function

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def root():
    """Provides a welcome page with information about how to use the API."""
    return """
    <html>
        <head>
            <title>Fantasy AI Backend</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #4a4a4a; }
                code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
                pre { background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
                .endpoint { margin-bottom: 30px; border-left: 4px solid #0366d6; padding-left: 15px; }
            </style>
        </head>
        <body>
            <h1>Fantasy AI Backend</h1>
            <p>Welcome to the Fantasy AI Backend API. This API provides AI-powered fantasy sports advice using OpenAI's GPT-4.1.</p>
            
            <h2>API Endpoints:</h2>
            
            <div class="endpoint">
                <h3>POST /advice</h3>
                <p>Get AI advice using the default GPT-4.1 model.</p>
                <h4>Example Request:</h4>
                <pre>
curl -X POST "http://localhost:8000/advice" \\
  -H "Content-Type: application/json" \\
  -d '{"conversation":[{"role":"user","content":"Which quarterback should I start this week?"}]}'
                </pre>
            </div>
            
            <div class="endpoint">
                <h3>POST /custom-advice</h3>
                <p>Get AI advice with a specified model.</p>
                <h4>Example Request:</h4>
                <pre>
curl -X POST "http://localhost:8000/custom-advice?model=gpt-4o" \\
  -H "Content-Type: application/json" \\
  -d '{"conversation":[{"role":"user","content":"Should I trade for Christian McCaffrey?"}]}'
                </pre>
            </div>
            
            <p>For more information, check the <a href="/docs">API documentation</a>.</p>
        </body>
    </html>
    """

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
    
    # Check if web search is enabled for this request
    enable_web_search = body.enable_web_search if hasattr(body, 'enable_web_search') else False
    
    # Call the helper function with the specified model
    reply, model_used = get_response(
        prompt=body.conversation[-1].content, 
        model=model_name,
        enable_web_search=enable_web_search
    )
    return AdviceResponse(reply=reply, model=model_used)


@app.post("/custom-advice", response_model=AdviceResponse)
async def get_custom_advice(
    body: AdviceRequest, 
    model: str = Query("gpt-4.1", description="OpenAI model to use (e.g., gpt-4.1)"),
    enable_web_search: bool = Query(False, description="Enable web search capability")
) -> AdviceResponse:
    """
    Similar to /advice but allows specifying which OpenAI model to use.
    
    • Expects `AdviceRequest` with a `conversation` list.
    • Uses the last user message as the prompt.
    • Allows specifying the model via query parameter.
    • Allows enabling web search via query parameter.
    • Returns an `AdviceResponse` with the model's reply.
    """
    reply, model_used = get_response(
        prompt=body.conversation[-1].content, 
        model=model,
        enable_web_search=enable_web_search
    )
    return AdviceResponse(reply=reply, model=model_used)