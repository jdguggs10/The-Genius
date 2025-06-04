#!/usr/bin/env python3
"""
PyBaseball MCP Server - Provides MLB statistics via Model Context Protocol.
This server exposes baseball statistics from PyBaseball as tools for AI assistants.
"""
import os
import sys
import logging
import asyncio
from typing import Optional, Any, Sequence
from datetime import datetime
import contextlib
import io

# Import MCP Server
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool as MCPTool, TextContent
import mcp.types as types

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

# Set up logging - ensure it goes to stderr in MCP mode
if os.environ.get("MCP_STDIO_MODE") == "1":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # Force logging to stderr in MCP mode
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("pybaseball-stats")

@server.list_tools()
async def handle_list_tools() -> list[MCPTool]:
    """List available tools."""
    return [
        MCPTool(
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
        MCPTool(
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
        MCPTool(
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
        MCPTool(
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
        MCPTool(
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
        MCPTool(
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
        MCPTool(
            name="clear_stats_cache",
            description="Clear the statistics cache to force fresh data retrieval",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        MCPTool(
            name="health_check",
            description="Check if the PyBaseball MCP server is running properly",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> Sequence[types.TextContent]:
    """Handle tool calls."""
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
            result = f"Unknown tool: {name}"
        
        return [TextContent(type="text", text=str(result))]
    
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point for the MCP server."""
    if os.environ.get("MCP_STDIO_MODE") == "1":
        logger.info("Starting PyBaseball MCP Server in stdio mode...")
        try:
            async with stdio_server() as (read_stream, write_stream):
                await server.run(
                    read_stream,
                    write_stream,
                    server.create_initialization_options()
                )
        except Exception as e:
            # Handle cancellation and other errors gracefully
            if "notifications/cancelled" in str(e) or "ValidationError" in str(e):
                logger.warning("Client sent unsupported notification (likely cancellation). This is expected behavior.")
                # Exit gracefully instead of crashing
                return
            else:
                logger.error(f"Unexpected server error: {e}")
                raise
    else:
        logger.error("This server only supports MCP STDIO mode")
        logger.error("Use MCP_STDIO_MODE=1 environment variable to run in stdio mode")
        sys.exit(1)

if __name__ == "__main__":
    if os.environ.get("MCP_STDIO_MODE") == "1":
        asyncio.run(main())
    else:
        logger.error("This server only supports MCP STDIO mode")
        logger.error("Use MCP_STDIO_MODE=1 environment variable to run in stdio mode")
        sys.exit(1) 