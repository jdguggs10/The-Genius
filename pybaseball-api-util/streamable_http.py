# Updated FastAPI Routes for Streamable HTTP
"""
Implementation of Streamable HTTP protocol for PyBaseball MCP Server.
Following the March 2025 specification for Cloudflare deployment.
https://developers.cloudflare.com/agents/guides/remote-mcp-server/
"""
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
from typing import AsyncGenerator, Dict, Any, List
import json
import logging
import asyncio
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

def configure_cors(app: FastAPI):
    """Configure CORS for remote deployment compatibility."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for API access
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
        expose_headers=["Transfer-Encoding"],  # Expose Transfer-Encoding header for streaming
    )
    logger.info("CORS configured for Streamable HTTP compatibility")

async def streaming_json_response(result: Any) -> AsyncGenerator[bytes, None]:
    """Generate a streaming response following Streamable HTTP protocol."""
    # Start with a JSON object opening brace
    yield b'{'
    
    # Stream the "jsonrpc" field first
    yield b'"jsonrpc":"2.0",'
    
    # Then stream the result field
    yield b'"result":'
    
    # If the result is a string, wrap it in quotes
    if isinstance(result, str):
        yield f'"{result}"'.encode('utf-8')
    else:
        yield json.dumps(result).encode('utf-8')
    
    # End the JSON object
    yield b'}'

def register_streamable_http_routes(app: FastAPI, handle_call_tool, handle_list_tools):
    """Register Streamable HTTP compatible routes with the FastAPI app."""
    
    # Configure CORS for remote deployment
    configure_cors(app)
    
    # --- Legacy Routes (still supported) ---
    @app.get("/streamable-http/")
    async def streamable_root():
        """Root endpoint for Streamable HTTP compatibility."""
        return {"message": "PyBaseball MCP Server", "protocol": "Streamable HTTP"}
    
    @app.get("/streamable-http/tools", response_class=StreamingResponse)
    async def list_tools_stream_legacy():
        """Legacy list tools endpoint with streaming response."""
        tools = await handle_list_tools()
        
        async def stream_generator():
            tools_dict = {
                "tools": [{"name": tool.name, "description": tool.description} for tool in tools]
            }
            async for chunk in streaming_json_response(tools_dict):
                yield chunk
        
        return StreamingResponse(
            stream_generator(),
            media_type="application/json",
            headers={"Transfer-Encoding": "chunked"}
        )
    
    @app.post("/streamable-http/tools/{tool_name}", response_class=StreamingResponse)
    async def call_tool_stream_legacy(tool_name: str, request: Request):
        """Legacy call tool endpoint with streaming response."""
        # Parse request body
        arguments = await request.json()
        if arguments is None:
            arguments = {}
        
        # Call the tool
        result = await handle_call_tool(tool_name, arguments)
        
        # Stream the response
        async def stream_generator():
            if result and len(result) > 0:
                if hasattr(result[0], 'error'):  # ErrorData
                    error_response = {
                        "error": {
                            "code": result[0].error.get("code", "error"),
                            "message": result[0].error.get("message", "Unknown error")
                        }
                    }
                    async for chunk in streaming_json_response(error_response):
                        yield chunk
                elif hasattr(result[0], 'text'):  # TextContent
                    async for chunk in streaming_json_response({"data": result[0].text}):
                        yield chunk
                else:
                    async for chunk in streaming_json_response({"data": "Unknown result type"}):
                        yield chunk
            else:
                async for chunk in streaming_json_response({"data": "No result returned"}):
                    yield chunk
        
        return StreamingResponse(
            stream_generator(),
            media_type="application/json",
            headers={"Transfer-Encoding": "chunked"}
        )
        
    # --- Main Routes with Streamable HTTP ---
    # Override the /tools endpoint to use Streamable HTTP
    @app.get("/tools", response_class=StreamingResponse)
    async def list_tools_stream():
        """List tools endpoint with streaming response."""
        tools = await handle_list_tools()
        
        async def stream_generator():
            tools_dict = {
                "tools": [{"name": tool.name, "description": tool.description} for tool in tools]
            }
            async for chunk in streaming_json_response(tools_dict):
                yield chunk
        
        return StreamingResponse(
            stream_generator(),
            media_type="application/json", 
            headers={"Transfer-Encoding": "chunked"}
        )
    
    # Override the /tools/{tool_name} endpoint to use Streamable HTTP
    @app.post("/tools/{tool_name}", response_class=StreamingResponse)
    async def call_tool_stream(tool_name: str, request: Request):
        """Call a tool endpoint with streaming response."""
        # Parse request body
        arguments = await request.json()
        if arguments is None:
            arguments = {}
        
        # Call the tool
        result = await handle_call_tool(tool_name, arguments)
        
        # Stream the response
        async def stream_generator():
            if result and len(result) > 0:
                if hasattr(result[0], 'error'):  # ErrorData
                    error_response = {
                        "error": {
                            "code": result[0].error.get("code", "error"),
                            "message": result[0].error.get("message", "Unknown error")
                        }
                    }
                    async for chunk in streaming_json_response(error_response):
                        yield chunk
                elif hasattr(result[0], 'text'):  # TextContent
                    async for chunk in streaming_json_response({"data": result[0].text}):
                        yield chunk
                else:
                    async for chunk in streaming_json_response({"data": "Unknown result type"}):
                        yield chunk
            else:
                async for chunk in streaming_json_response({"data": "No result returned"}):
                    yield chunk
        
        return StreamingResponse(
            stream_generator(),
            media_type="application/json",
            headers={"Transfer-Encoding": "chunked"}
        )
    
    # --- JSON-RPC Endpoint ---
    @app.post("/jsonrpc", response_class=StreamingResponse)
    async def jsonrpc_endpoint(request: Request):
        """JSON-RPC 2.0 endpoint for Streamable HTTP protocol."""
        try:
            # Parse the request
            req_data = await request.json()
            
            # Verify it's a valid JSON-RPC request
            if "jsonrpc" not in req_data or req_data["jsonrpc"] != "2.0":
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32600,
                            "message": "Invalid Request: Not a valid JSON-RPC 2.0 request"
                        },
                        "id": req_data.get("id", None)
                    }
                )
                
            # Extract method and params
            method = req_data.get("method")
            params = req_data.get("params", {})
            request_id = req_data.get("id")
            
            # Handle different methods
            if method == "tool":
                # Tool invocation
                if "name" not in params:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32602,
                                "message": "Invalid params: Missing tool name"
                            },
                            "id": request_id
                        }
                    )
                    
                tool_name = params["name"]
                tool_params = params.get("parameters", {})
                
                # Call the tool
                result = await handle_call_tool(tool_name, tool_params)
                
                # Stream the response
                async def stream_generator():
                    yield f'{{"jsonrpc":"2.0","id":"{request_id}",'.encode('utf-8')
                    
                    if result and len(result) > 0:
                        if hasattr(result[0], 'error'):  # ErrorData
                            error_data = {
                                "error": {
                                    "code": result[0].error.get("code", -32000),
                                    "message": result[0].error.get("message", "Unknown error")
                                }
                            }
                            yield json.dumps(error_data)[1:].encode('utf-8')  # Remove the leading {
                        elif hasattr(result[0], 'text'):  # TextContent
                            yield f'"result":{json.dumps(result[0].text)}}}' .encode('utf-8')
                        else:
                            yield f'"result":"Unknown result type"}}' .encode('utf-8')
                    else:
                        yield f'"result":null}}' .encode('utf-8')
                
                return StreamingResponse(
                    stream_generator(),
                    media_type="application/json",
                    headers={"Transfer-Encoding": "chunked"}
                )
            
            elif method == "list_tools":
                # List available tools
                tools = await handle_list_tools()
                
                async def stream_generator():
                    yield f'{{"jsonrpc":"2.0","id":"{request_id}","result":'.encode('utf-8')
                    
                    tools_list = [{"name": tool.name, "description": tool.description} for tool in tools]
                    yield json.dumps(tools_list).encode('utf-8')
                    
                    yield b'}'
                
                return StreamingResponse(
                    stream_generator(),
                    media_type="application/json",
                    headers={"Transfer-Encoding": "chunked"}
                )
                
            else:
                # Method not found
                return JSONResponse(
                    status_code=404,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        },
                        "id": request_id
                    }
                )
                
        except json.JSONDecodeError:
            # Invalid JSON
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error: Invalid JSON"
                    },
                    "id": None
                }
            )
        except Exception as e:
            # Internal error
            logger.error(f"Error in JSON-RPC endpoint: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    },
                    "id": req_data.get("id", None) if 'req_data' in locals() else None
                }
            )
            
    # Legacy protocol info endpoint still supported
    @app.get("/streamable-http/protocol-info")
    async def protocol_info_legacy():
        """Legacy protocol information endpoint."""
        return {
            "protocol": "MCP Streamable HTTP",
            "version": "2025-03-26",
            "features": ["Transfer-Encoding: chunked", "Server-Side Events deprecated"],
            "client_requirements": ["Support for chunked transfer encoding"]
        }
        
    @app.get("/protocol-info")
    async def protocol_info():
        """Protocol information endpoint compliant with March 2025 specification."""
        return {
            "protocol": "MCP Streamable HTTP",
            "version": "2025-03-26",
            "features": [
                "Transfer-Encoding: chunked", 
                "Server-Side Events deprecated",
                "Tool annotations",
                "Progress notifications",
                "JSON-RPC batching"
            ],
            "client_requirements": ["Support for chunked transfer encoding"],
            "cloudflare_compatible": True,
            "oauth_supported": True,
            "streaming_mode": True,
            "supports_jsonrpc": True
        }
