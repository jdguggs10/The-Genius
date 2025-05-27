"""
ESPN Fantasy Baseball MCP Server
A baseball-only Model Context Protocol server providing comprehensive access to ESPN Fantasy Baseball data.

This modular server replaces the multi-sport version and focuses exclusively on baseball fantasy data.
"""

import sys
import os
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
    print(message, file=sys.stderr)

try:
    # Initialize FastMCP server
    log_error("Initializing ESPN Fantasy Baseball MCP server...")
    mcp = FastMCP("espn-baseball", dependencies=['espn-api'])

    # Constants for current year calculation
    current_date = datetime.datetime.now()
    # Baseball season runs spring to fall within the same calendar year
    BASEBALL_YEAR = current_date.year

    log_error(f"Using default year for baseball: {BASEBALL_YEAR}")

    # Session ID for this server instance
    SESSION_ID = "default_session"

    # =============================================================================
    # AUTHENTICATION TOOLS
    # =============================================================================

    @mcp.tool()
    async def auth_store_credentials(espn_s2: str, swid: str) -> str:
        """Store ESPN authentication credentials for this session.
        
        Args:
            espn_s2: The ESPN_S2 cookie value from your ESPN account
            swid: The SWID cookie value from your ESPN account
        """
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

    # =============================================================================
    # LEAGUE-LEVEL TOOLS
    # =============================================================================

    @mcp.tool()
    async def league_get_info(league_id: int, year: int = None) -> str:
        """Get basic information about a fantasy baseball league.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_league_info(league_id, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting league info: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting league info: {str(e)}"

    @mcp.tool()
    async def league_get_settings(league_id: int, year: int = None) -> str:
        """Get detailed league settings and configuration.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_league_settings(league_id, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting league settings: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting league settings: {str(e)}"

    @mcp.tool()
    async def league_get_standings(league_id: int, year: int = None) -> str:
        """Get current standings for a league.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_league_standings(league_id, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting league standings: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting league standings: {str(e)}"

    @mcp.tool()
    async def league_get_scoreboard(league_id: int, matchup_period: int = None) -> str:
        """Get scoreboard/matchups overview for a given week.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            matchup_period: The week/period number (defaults to current week)
        """
        try:
            result = get_league_scoreboard(league_id, matchup_period, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting league scoreboard: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting league scoreboard: {str(e)}"

    # =============================================================================
    # TEAM/ROSTER TOOLS
    # =============================================================================

    @mcp.tool()
    async def team_get_roster(league_id: int, team_id: int, year: int = None) -> str:
        """Get a team's current roster with detailed player information.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            team_id: The team ID in the league (usually 1-N where N is number of teams)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_team_roster(league_id, team_id, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting team roster: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting team roster: {str(e)}"

    @mcp.tool()
    async def team_get_info(league_id: int, team_id: int, year: int = None) -> str:
        """Get a team's general information including metadata and performance stats.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            team_id: The team ID in the league (usually 1-N where N is number of teams)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_team_info(league_id, team_id, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting team info: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting team info: {str(e)}"

    @mcp.tool()
    async def team_get_schedule(league_id: int, team_id: int, year: int = None) -> str:
        """Get a team's schedule showing opponents and results for each week.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            team_id: The team ID in the league (usually 1-N where N is number of teams)  
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_team_schedule(league_id, team_id, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting team schedule: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting team schedule: {str(e)}"

    # =============================================================================
    # MATCHUP/SCORING TOOLS
    # =============================================================================

    @mcp.tool()
    async def matchup_get_week_results(league_id: int, week: int = None, year: int = None) -> str:
        """Get high-level matchup results for a specific week.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            week: The week number (defaults to current week)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_week_matchups(league_id, week, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting week matchups: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting week matchups: {str(e)}"

    @mcp.tool()
    async def matchup_get_boxscore(league_id: int, week: int, home_team_id: int, year: int = None) -> str:
        """Get detailed box score breakdown for a specific matchup.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            week: The week number
            home_team_id: The ID of the home team (to identify the specific matchup)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_matchup_boxscore(league_id, week, home_team_id, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting matchup boxscore: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting matchup boxscore: {str(e)}"

    # =============================================================================
    # TRANSACTION TOOLS
    # =============================================================================

    @mcp.tool()
    async def transaction_get_recent_activity(league_id: int, limit: int = 25, activity_type: str = None, 
                                            offset: int = 0, year: int = None) -> str:
        """Get recent activity and transactions for the league.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            limit: Maximum number of activities to return (default 25)
            activity_type: Filter by activity type (e.g., "ADD", "DROP", "TRADE_ACCEPTED")
            offset: Number of activities to skip (for pagination)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_recent_activity(league_id, limit, activity_type, offset, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting recent activity: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting recent activity: {str(e)}"

    @mcp.tool()
    async def transaction_get_waiver_activity(league_id: int, limit: int = 25, year: int = None) -> str:
        """Get recent waiver wire activity specifically.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            limit: Maximum number of activities to return (default 25)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_waiver_activity(league_id, limit, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting waiver activity: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting waiver activity: {str(e)}"

    @mcp.tool()
    async def transaction_get_trade_activity(league_id: int, limit: int = 25, year: int = None) -> str:
        """Get recent trade activity specifically.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            limit: Maximum number of activities to return (default 25)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_trade_activity(league_id, limit, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting trade activity: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting trade activity: {str(e)}"

    @mcp.tool()
    async def transaction_get_add_drop_activity(league_id: int, limit: int = 25, year: int = None) -> str:
        """Get recent add/drop activity specifically.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            limit: Maximum number of activities to return (default 25)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_add_drop_activity(league_id, limit, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting add/drop activity: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting add/drop activity: {str(e)}"

    @mcp.tool()
    async def transaction_get_team_transactions(league_id: int, team_id: int, limit: int = 25, year: int = None) -> str:
        """Get recent transactions for a specific team.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            team_id: The team ID to filter transactions for
            limit: Maximum number of activities to return (default 25)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_team_transactions(league_id, team_id, limit, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting team transactions: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting team transactions: {str(e)}"

    @mcp.tool()
    async def transaction_get_player_history(league_id: int, player_name: str, year: int = None) -> str:
        """Get transaction history for a specific player.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            player_name: Name of the player to search for
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_player_transaction_history(league_id, player_name, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting player transaction history: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting player transaction history: {str(e)}"

    @mcp.tool()
    async def transaction_get_lineup_activity(league_id: int, limit: int = 25, year: int = None) -> str:
        """Get recent lineup change activity.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            limit: Maximum number of activities to return (default 25)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_lineup_activity(league_id, limit, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting lineup activity: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting lineup activity: {str(e)}"

    @mcp.tool()
    async def transaction_get_settings_activity(league_id: int, limit: int = 25, year: int = None) -> str:
        """Get recent league/team settings change activity.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            limit: Maximum number of activities to return (default 25)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_settings_activity(league_id, limit, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting settings activity: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting settings activity: {str(e)}"

    @mcp.tool()
    async def transaction_get_keeper_activity(league_id: int, limit: int = 25, year: int = None) -> str:
        """Get recent keeper/dynasty league activity.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            limit: Maximum number of activities to return (default 25)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_keeper_activity(league_id, limit, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting keeper activity: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting keeper activity: {str(e)}"

    # =============================================================================
    # PLAYER TOOLS
    # =============================================================================

    @mcp.tool()
    async def player_get_stats(league_id: int, player_name: str, year: int = None) -> str:
        """Get detailed statistics for a specific player.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            player_name: Name of the player to search for
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_player_stats(league_id, player_name, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting player stats: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting player stats: {str(e)}"

    @mcp.tool()
    async def player_get_free_agents(league_id: int, week: int = None, position: str = None,
                                   position_id: int = None, limit: int = 50, year: int = None) -> str:
        """Get list of available free agents with filtering options.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            week: Week for which to get stats (defaults to current week)
            position: Position filter (e.g., "C", "1B", "OF", "SP", "RP")
            position_id: ESPN position ID filter (alternative to position name)
            limit: Maximum number of players to return (default 50)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_free_agents(league_id, week, position, position_id, limit, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting free agents: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting free agents: {str(e)}"

    @mcp.tool()
    async def player_get_top_performers(league_id: int, position: str = None, limit: int = 20,
                                       metric: str = "points", year: int = None) -> str:
        """Get top performing players across all teams in the league.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            position: Position filter (e.g., "C", "1B", "OF", "SP", "RP")
            limit: Maximum number of players to return (default 20)
            metric: Metric to sort by ("points", "batting_average", "home_runs", "era", etc.)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_top_performers(league_id, position, limit, metric, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting top performers: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting top performers: {str(e)}"

    @mcp.tool()
    async def player_search(league_id: int, search_term: str, include_rostered: bool = True,
                           include_free_agents: bool = True, year: int = None) -> str:
        """Search for players by name across rosters and free agents.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            search_term: Partial or full player name to search for
            include_rostered: Whether to include players on team rosters
            include_free_agents: Whether to include free agents
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = search_players(league_id, search_term, include_rostered, include_free_agents, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error searching players: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error searching players: {str(e)}"

    @mcp.tool()
    async def player_get_waiver_claims(league_id: int, limit: int = 25, year: int = None) -> str:
        """Get recent waiver claims and FAAB bids information.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            limit: Maximum number of claims to return (default 25)
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_waiver_claims(league_id, limit, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting waiver claims: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting waiver claims: {str(e)}"

    # =============================================================================
    # DRAFT TOOLS
    # =============================================================================

    @mcp.tool()
    async def draft_get_results(league_id: int, year: int = None) -> str:
        """Get complete draft results for the league.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_draft_results(league_id, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting draft results: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting draft results: {str(e)}"

    @mcp.tool()
    async def draft_get_round(league_id: int, round_num: int, year: int = None) -> str:
        """Get draft picks for a specific round.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            round_num: The round number to retrieve
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_draft_by_round(league_id, round_num, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting draft round: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting draft round: {str(e)}"

    @mcp.tool()
    async def draft_get_team_picks(league_id: int, team_id: int, year: int = None) -> str:
        """Get all draft picks for a specific team.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            team_id: The team ID to get draft picks for
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_team_draft_picks(league_id, team_id, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting team draft picks: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting team draft picks: {str(e)}"

    @mcp.tool()
    async def draft_get_analysis(league_id: int, year: int = None) -> str:
        """Get analysis of the draft including statistics and insights.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_draft_analysis(league_id, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting draft analysis: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting draft analysis: {str(e)}"

    @mcp.tool()
    async def draft_get_scarcity_analysis(league_id: int, year: int = None) -> str:
        """Analyze position scarcity based on draft patterns.
        
        Args:
            league_id: The ESPN fantasy baseball league ID
            year: Optional year for historical data (defaults to current season)
        """
        try:
            result = get_position_scarcity_analysis(league_id, year, SESSION_ID)
            return str(result)
        except Exception as e:
            log_error(f"Error getting position scarcity analysis: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting position scarcity analysis: {str(e)}"

    # =============================================================================
    # METADATA TOOLS
    # =============================================================================

    @mcp.tool()
    async def metadata_get_positions() -> str:
        """Get mapping of ESPN position slot IDs to position names."""
        try:
            result = get_positions()
            return str(result)
        except Exception as e:
            log_error(f"Error getting positions metadata: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting positions metadata: {str(e)}"

    @mcp.tool()
    async def metadata_get_stats() -> str:
        """Get mapping of ESPN stat IDs to stat abbreviations."""
        try:
            result = get_stat_map()
            return str(result)
        except Exception as e:
            log_error(f"Error getting stats metadata: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting stats metadata: {str(e)}"

    @mcp.tool()
    async def metadata_get_activity_types() -> str:
        """Get mapping of friendly activity names to ESPN message type codes."""
        try:
            result = get_activity_types()
            return str(result)
        except Exception as e:
            log_error(f"Error getting activity types metadata: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error getting activity types metadata: {str(e)}"

    # =============================================================================
    # SERVER STARTUP
    # =============================================================================

    if __name__ == "__main__":
        log_error("Starting ESPN Fantasy Baseball MCP server...")
        mcp.run()

except Exception as e:
    # Log any exception that might occur during server initialization
    log_error(f"ERROR DURING SERVER INITIALIZATION: {str(e)}")
    traceback.print_exc(file=sys.stderr)
    # Keep the process running to see logs
    log_error("Server failed to start, but kept running for logging. Press Ctrl+C to exit.")
    # Wait indefinitely to keep the process alive for logs
    import time
    while True:
        time.sleep(10)