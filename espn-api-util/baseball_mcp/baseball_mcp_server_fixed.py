"""
ESPN Fantasy Baseball MCP Server - Fixed Version
"""

import sys
import os

# Ensure the baseball_mcp directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
import datetime
import logging
import traceback

# Import all our modules
from auth import authenticate, logout
from league import get_league_info, get_league_settings, get_league_standings, get_league_scoreboard  
from roster import get_team_roster, get_team_info, get_team_schedule
from matchups import get_week_matchups, get_matchup_boxscore
from transactions import get_recent_activity, get_waiver_activity, get_trade_activity, get_add_drop_activity, get_team_transactions, get_player_transaction_history, get_lineup_activity, get_settings_activity, get_keeper_activity
from players import get_player_stats, get_free_agents, get_top_performers, search_players, get_waiver_claims
from draft import get_draft_results, get_draft_by_round, get_team_draft_picks, get_draft_analysis, get_position_scarcity_analysis
from metadata import get_positions, get_stat_map, get_activity_types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("espn-baseball-mcp")

def log_error(message):
    """Add stderr logging for Claude Desktop to see"""
    print(f"[ESPN-BASEBALL-MCP] {message}", file=sys.stderr)

try:
    # Initialize FastMCP server
    log_error("Initializing ESPN Fantasy Baseball MCP server...")
    mcp = FastMCP("espn-baseball")

    # Constants for current year calculation
    current_date = datetime.datetime.now()
    BASEBALL_YEAR = current_date.year

    log_error(f"Using default year for baseball: {BASEBALL_YEAR}")

    # Session ID for this server instance
    SESSION_ID = "default_session"

    # Register all the tools (same as original)
    
    @mcp.tool()
    async def auth_store_credentials(espn_s2: str, swid: str) -> str:
        """Store ESPN authentication credentials for this session."""
        try:
            result = authenticate(espn_s2, swid, SESSION_ID)
            return result.get("message", "Authentication completed")
        except Exception as e:
            log_error(f"Authentication error: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Authentication error: {str(e)}"

    @mcp.tool()
    async def auth_logout() -> str:
        """Clear stored authentication credentials for this session."""
        try:
            result = logout(SESSION_ID)
            return result.get("message", "Logout completed")
        except Exception as e:
            log_error(f"Logout error: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Logout error: {str(e)}"

    # ... (all other tool registrations remain the same)

    if __name__ == "__main__":
        log_error("Starting ESPN Fantasy Baseball MCP server...")
        log_error(f"Python version: {sys.version}")
        log_error(f"Working directory: {os.getcwd()}")
        mcp.run()

except Exception as e:
    log_error(f"ERROR DURING SERVER INITIALIZATION: {str(e)}")
    traceback.print_exc(file=sys.stderr)
    import time
    while True:
        time.sleep(10)
