#!/usr/bin/env python3

import os
import sys
import logging
import asyncio
from typing import Any, Sequence

# Import MCP Server components - using native patterns
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ErrorData
import mcp.types as types
from enum import Enum

# Define error codes similar to the spec
class ErrorCode(Enum):
    TOOL_NOT_FOUND = "tool_not_found"
    INTERNAL_ERROR = "internal_error"

# FastAPI for HTTP transport
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Import our modules
from pybaseball_mcp.players import (
    get_player_stats,
    get_player_recent_stats,
    search_player
)
from pybaseball_mcp.teams import (
    get_standings,
    get_league_leaders,
    get_team_stats
)
from pybaseball_mcp.utils import clear_cache, get_cache_info

# For HTTP server deployment
import uvicorn

# --- Configuration ---
MCP_STDIO_MODE = os.environ.get("MCP_STDIO_MODE", "0") == "1"
PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"

# --- Logging Setup ---
log_stream = sys.stderr if MCP_STDIO_MODE else sys.stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=log_stream
)
logger = logging.getLogger(__name__)

# --- Native MCP Server Implementation ---
server = Server("pybaseball-stats")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="player_stats",
            description="Get season statistics for a specific MLB player",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_name": {
                        "type": "string",
                        "description": "Full name of the player (e.g., 'Shohei Ohtani')"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Season year (defaults to current year)",
                        "minimum": 1871
                    }
                },
                "required": ["player_name"]
            }
        ),
        Tool(
            name="player_recent_performance",
            description="Get recent game performance for an MLB player",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_name": {
                        "type": "string",
                        "description": "Full name of the player"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back (default 30)",
                        "minimum": 1,
                        "maximum": 365,
                        "default": 30
                    }
                },
                "required": ["player_name"]
            }
        ),
        Tool(
            name="search_players",
            description="Search for MLB players by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Partial name to search for"
                    }
                },
                "required": ["search_term"]
            }
        ),
        Tool(
            name="mlb_standings",
            description="Get current MLB standings by division",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "Season year (defaults to current year)",
                        "minimum": 1871
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="stat_leaders",
            description="Get MLB leaders for a specific statistic",
            inputSchema={
                "type": "object",
                "properties": {
                    "stat": {
                        "type": "string",
                        "description": "Statistic to rank by (e.g., 'HR', 'AVG', 'ERA', 'SO')"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Season year (defaults to current year)",
                        "minimum": 1871
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of top players to return (default 10)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    },
                    "player_type": {
                        "type": "string",
                        "description": "Type of player statistics",
                        "enum": ["batting", "pitching"],
                        "default": "batting"
                    }
                },
                "required": ["stat"]
            }
        ),
        Tool(
            name="team_statistics",
            description="Get aggregate statistics for an MLB team",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_name": {
                        "type": "string",
                        "description": "Team name or abbreviation (e.g., 'Yankees', 'NYY')"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Season year (defaults to current year)",
                        "minimum": 1871
                    }
                },
                "required": ["team_name"]
            }
        ),
        Tool(
            name="clear_stats_cache",
            description="Clear the statistics cache to force fresh data retrieval",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="health_check",
            description="Check if the PyBaseball MCP server is running properly",
            inputSchema={"type": "object", "properties": {}, "required": []}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent | ErrorData]:
    """Handle tool calls."""
    logger.info(f"Tool call: {name} with args: {arguments}")
    try:
        if name == "player_stats":
            result = get_player_stats(
                arguments.get("player_name"),
                arguments.get("year")
            )
        elif name == "player_recent_performance":
            result = get_player_recent_stats(
                arguments.get("player_name"),
                arguments.get("days", 30)
            )
        elif name == "search_players":
            result = search_player(arguments.get("search_term"))
        elif name == "mlb_standings":
            result = get_standings(arguments.get("year"))
        elif name == "stat_leaders":
            result = get_league_leaders(
                arguments.get("stat"),
                arguments.get("year"),
                arguments.get("top_n", 10),
                arguments.get("player_type", "batting")
            )
        elif name == "team_statistics":
            result = get_team_stats(
                arguments.get("team_name"),
                arguments.get("year")
            )
        elif name == "clear_stats_cache":
            clear_cache()
            result = "Statistics cache cleared successfully"
        elif name == "health_check":
            import pybaseball
            result = f"PyBaseball MCP Server is running. PyBaseball version: {pybaseball.__version__}"
        else:
            logger.warning(f"Unknown tool called: {name}")
            return [ErrorData(
                type="error", 
                error={"code": ErrorCode.TOOL_NOT_FOUND.value, 
                       "message": f"Unknown tool: {name}"}
            )]
        
        logger.info(f"Tool {name} result: {str(result)[:200]}...")
        return [TextContent(type="text", text=str(result))]
    
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}", exc_info=True)
        return [ErrorData(
            type="error",
            error={"code": ErrorCode.INTERNAL_ERROR.value,
                  "message": f"Error executing tool {name}: {str(e)}"}
        )]

# --- Transport Layer: STDIO ---
async def run_stdio_server():
    """Runs the MCP server over STDIO using native patterns."""
    logger.info("Starting PyBaseball MCP Server in STDIO mode...")
    
    async with stdio_server() as (read_stream, write_stream):
        # Create initialization options with updated protocol version
        init_options = server.create_initialization_options()
        init_options.protocolVersion = "2025-03-26"  # March 2025 spec
        
        await server.run(
            read_stream,
            write_stream,
            init_options
        )

# --- Transport Layer: Streamable HTTP ---
# Create FastAPI app for HTTP transport
http_app = FastAPI(
    title="PyBaseball MCP Server",
    description="MLB statistics via Model Context Protocol over Streamable HTTP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Import streamable HTTP implementation
from streamable_http import register_streamable_http_routes

# Register streamable HTTP routes that comply with March 2025 specification
register_streamable_http_routes(http_app, handle_call_tool, handle_list_tools)

@http_app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint."""
    return JSONResponse(
        content={"message": "PyBaseball MCP Server", "transport": "Streamable HTTP"},
        headers={"Content-Type": "application/json"}
    )

@http_app.get("/health", response_class=JSONResponse)
async def health_check():
    """Health check endpoint."""
    import pybaseball
    return JSONResponse(
        content={
            "status": "healthy", 
            "server": "pybaseball-mcp", 
            "version": pybaseball.__version__,
            "protocol": "Streamable HTTP",
            "protocol_version": "2025-03-26"
        },
        headers={"Content-Type": "application/json"}
    )

# --- Main Execution ---
if __name__ == "__main__":
    if MCP_STDIO_MODE:
        # Run in STDIO mode
        try:
            asyncio.run(run_stdio_server())
        except KeyboardInterrupt:
            logger.info("STDIO server shutdown requested.")
        finally:
            logger.info("STDIO server exiting.")
    else:
        # Run in Streamable HTTP mode using native MCP ASGI app
        logger.info(f"Starting PyBaseball MCP Server in Streamable HTTP mode on {HOST}:{PORT}...")
        logger.info("Using native MCP Streamable HTTP transport (March 2025 spec).")
        logger.info("Cloudflare deployment ready with chunked transfer encoding support.")
        
        # Use Uvicorn with proper settings for Streamable HTTP
        uvicorn.run(
            http_app,
            host=HOST,
            port=PORT,
            log_level="info",
            timeout_keep_alive=120,  # Longer keep-alive for streaming connections
            h11_max_incomplete_event_size=0  # No limit on event size for streaming
        )
        logger.info("Streamable HTTP server exiting.")
