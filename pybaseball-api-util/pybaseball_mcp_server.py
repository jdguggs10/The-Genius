#!/usr/bin/env python3
"""
PyBaseball MCP Server - Provides MLB statistics via Model Context Protocol.
This server exposes baseball statistics from PyBaseball as tools for AI assistants.
"""
import os
import sys
import logging
import asyncio
from typing import Optional
from datetime import datetime

# Try importing MCP Server - we'll provide a fallback if not available
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool as MCPTool
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
from pybaseball_mcp.utils import clear_cache

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

# Initialize MCP server
if MCP_AVAILABLE:
    server = Server("pybaseball-stats")
else:
    # Fallback FastAPI implementation
    mcp = FastMCP("pybaseball-stats", dependencies=["pybaseball", "pandas"])

# Register tool functions
@mcp.tool()
async def player_stats(player_name: str, year: Optional[int] = None) -> str:
    """
    Get season statistics for a specific MLB player.
    
    Args:
        player_name: Full name of the player (e.g., "Shohei Ohtani")
        year: Season year (defaults to current year)
    
    Returns:
        JSON string with batting or pitching statistics
    """
    return get_player_stats(player_name, year)

@mcp.tool()
async def player_recent_performance(player_name: str, days: int = 30) -> str:
    """
    Get recent game performance for an MLB player.
    
    Args:
        player_name: Full name of the player
        days: Number of days to look back (default 30)
    
    Returns:
        JSON string with recent performance metrics
    """
    return get_player_recent_stats(player_name, days)

@mcp.tool()
async def search_players(search_term: str) -> str:
    """
    Search for MLB players by name.
    
    Args:
        search_term: Partial name to search for
    
    Returns:
        JSON string with list of matching players
    """
    return search_player(search_term)

@mcp.tool()
async def mlb_standings(year: Optional[int] = None) -> str:
    """
    Get current MLB standings by division.
    
    Args:
        year: Season year (defaults to current year)
    
    Returns:
        JSON string with standings for all divisions
    """
    return get_standings(year)

@mcp.tool()
async def stat_leaders(
    stat: str,
    year: Optional[int] = None,
    top_n: int = 10,
    player_type: str = "batting"
) -> str:
    """
    Get MLB leaders for a specific statistic.
    
    Args:
        stat: Statistic to rank by (e.g., "HR", "AVG", "ERA", "SO")
        year: Season year (defaults to current year)
        top_n: Number of top players to return (default 10)
        player_type: "batting" or "pitching"
    
    Returns:
        JSON string with league leaders
    """
    return get_league_leaders(stat, year, top_n, player_type)

@mcp.tool()
async def team_statistics(team_name: str, year: Optional[int] = None) -> str:
    """
    Get aggregate statistics for an MLB team.
    
    Args:
        team_name: Team name or abbreviation (e.g., "Yankees", "NYY")
        year: Season year (defaults to current year)
    
    Returns:
        JSON string with team batting and pitching statistics
    """
    return get_team_stats(team_name, year)

@mcp.tool()
async def clear_stats_cache() -> str:
    """
    Clear the statistics cache to force fresh data retrieval.
    
    Returns:
        Confirmation message
    """
    clear_cache()
    return "Statistics cache cleared successfully"

# Health check endpoint
@mcp.tool()
async def health_check() -> str:
    """
    Check if the PyBaseball MCP server is running properly.
    
    Returns:
        Server status information
    """
    import pybaseball
    return f"PyBaseball MCP Server is running. PyBaseball version: {pybaseball.__version__}"

if __name__ == "__main__":
    # Check if running in MCP stdio mode for Claude Desktop
    if os.environ.get("MCP_STDIO_MODE") == "1":
        if MCP_AVAILABLE:
            logger.info("Starting PyBaseball MCP Server in stdio mode...")
            # For real MCP integration, run in stdio mode
            try:
                mcp.run()
            except KeyboardInterrupt:
                logger.info("Server stopped by user")
            except Exception as e:
                logger.error(f"Server error: {e}")
                sys.exit(1)
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
            mcp.run(port=port)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1)