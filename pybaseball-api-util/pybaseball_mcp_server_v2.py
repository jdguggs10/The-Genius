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

# Try importing MCP Server
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool as MCPTool, TextContent
    import mcp.types as types
    MCP_AVAILABLE = True
except ImportError:
    # If MCP isn't available, we'll use a simple FastAPI server
    from fastapi import FastAPI
    from pydantic import BaseModel
    import uvicorn
    MCP_AVAILABLE = False
    
    class FastMCP:
        """Fallback MCP implementation using FastAPI."""
        def __init__(self, name: str, dependencies=None):
            self.name = name
            self.app = FastAPI(title=f"{name} MCP Server")
            self.tools = {}
            
        def tool(self, func=None, *, name: str = None):
            """Decorator to register a tool."""
            def decorator(f):
                tool_name = name or f.__name__
                self.tools[tool_name] = f
                
                # Create a POST endpoint for this tool
                @self.app.post(f"/tools/{tool_name}")
                async def tool_endpoint(**kwargs):
                    try:
                        if asyncio.iscoroutinefunction(f):
                            result = await f(**kwargs)
                        else:
                            result = f(**kwargs)
                        return {"result": result}
                    except Exception as e:
                        return {"error": str(e)}
                
                return f
            
            if func is None:
                return decorator
            return decorator(func)
            
        def run(self, port: int = None):
            """Run the server."""
            port = port or int(os.environ.get("PORT", "8002"))
            
            # Add a root endpoint
            @self.app.get("/")
            async def root():
                return {
                    "name": self.name,
                    "type": "mcp_server",
                    "tools": list(self.tools.keys())
                }
            
            # Add tools listing endpoint
            @self.app.get("/tools")
            async def list_tools():
                tool_list = []
                for name, func in self.tools.items():
                    tool_list.append({
                        "name": name,
                        "description": func.__doc__ or "No description",
                        "parameters": str(func.__annotations__)
                    })
                return {"tools": tool_list}
            
            # Add health endpoint
            @self.app.get("/health")
            async def health():
                return {"status": "healthy", "server": self.name}
            
            print(f"Starting {self.name} on port {port}", file=sys.stderr)
            print(f"Available tools: {list(self.tools.keys())}", file=sys.stderr)
            uvicorn.run(self.app, host="0.0.0.0", port=port)

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

# Initialize the appropriate server
if MCP_AVAILABLE:
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

else:
    # Fallback FastAPI implementation
    mcp = FastMCP("pybaseball-stats", dependencies=["pybaseball", "pandas"])

    # Register tool functions using the fallback implementation
    @mcp.tool()
    async def player_stats(player_name: str, year: Optional[int] = None) -> str:
        """Get season statistics for a specific MLB player."""
        return get_player_stats(player_name, year)

    @mcp.tool()
    async def player_recent_performance(player_name: str, days: int = 30) -> str:
        """Get recent game performance for an MLB player."""
        return get_player_recent_stats(player_name, days)

    @mcp.tool()
    async def search_players(search_term: str) -> str:
        """Search for MLB players by name."""
        return search_player(search_term)

    @mcp.tool()
    async def mlb_standings(year: Optional[int] = None) -> str:
        """Get current MLB standings by division."""
        return get_standings(year)

    @mcp.tool()
    async def stat_leaders(
        stat: str,
        year: Optional[int] = None,
        top_n: int = 10,
        player_type: str = "batting"
    ) -> str:
        """Get MLB leaders for a specific statistic."""
        return get_league_leaders(stat, year, top_n, player_type)

    @mcp.tool()
    async def team_statistics(team_name: str, year: Optional[int] = None) -> str:
        """Get aggregate statistics for an MLB team."""
        return get_team_stats(team_name, year)

    @mcp.tool()
    async def clear_stats_cache() -> str:
        """Clear the statistics cache to force fresh data retrieval."""
        clear_cache()
        return "Statistics cache cleared successfully"

    @mcp.tool()
    async def health_check() -> str:
        """Check if the PyBaseball MCP server is running properly."""
        import pybaseball
        return f"PyBaseball MCP Server is running. PyBaseball version: {pybaseball.__version__}"


async def main():
    """Main entry point for the MCP server."""
    if MCP_AVAILABLE and os.environ.get("MCP_STDIO_MODE") == "1":
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
        logger.info("Starting PyBaseball MCP Server in HTTP mode...")
        port = int(os.environ.get("PORT", "8002"))
        mcp.run(port=port)


if __name__ == "__main__":
    if os.environ.get("MCP_STDIO_MODE") == "1":
        if MCP_AVAILABLE:
            asyncio.run(main())
        else:
            logger.error("MCP_STDIO_MODE requested but MCP library not available")
            logger.error("Please install the full MCP library: pip install mcp")
            sys.exit(1)
    else:
        # Run the HTTP server mode (fallback or when not in Claude Desktop)
        logger.info("Starting PyBaseball MCP Server in HTTP mode...")
        
        # Load port from environment or use default
        port = int(os.environ.get("PORT", "8002"))
        
        try:
            if MCP_AVAILABLE:
                # Use fallback mode even with MCP available for HTTP
                mcp = FastMCP("pybaseball-stats", dependencies=["pybaseball", "pandas"])
                # Register tools... (would need to duplicate the registration here)
            mcp.run(port=port)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1) 