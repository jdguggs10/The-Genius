from mcp.server.fastmcp import FastMCP
from espn_api import football, baseball
import os
import sys
import datetime
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("espn-fantasy")

# Add stderr logging for Claude Desktop to see
def log_error(message):
    print(message, file=sys.stderr)

try:
    # Initialize FastMCP server
    log_error("Initializing FastMCP server...")
    mcp = FastMCP("espn-fantasy", dependancies=['espn-api'])

    # Constants
    current_date = datetime.datetime.now()
    # Football season typically ends in February, new season starts in September
    # So use previous year before July
    FOOTBALL_YEAR = current_date.year if current_date.month >= 7 else current_date.year - 1
    # Baseball season runs spring to fall within the same calendar year
    # Almost always use current year except maybe in January/February
    BASEBALL_YEAR = current_date.year
    # Default to football for backward compatibility
    CURRENT_YEAR = FOOTBALL_YEAR  # Keep for backwards compatibility

    log_error(f"Using default years: Football={FOOTBALL_YEAR}, Baseball={BASEBALL_YEAR}")

    class ESPNFantasyAPI:
        def __init__(self):
            self.leagues = {}  # Cache for league objects
            # Store credentials separately per-session rather than globally
            self.credentials = {}
        
        def get_league(self, session_id, league_id, year=None, sport="football"):
            """Get a league instance with caching, using stored credentials if available"""
            # Determine which year to use if none specified
            if year is None:
                if sport == "football":
                    year = FOOTBALL_YEAR
                elif sport == "baseball":
                    year = BASEBALL_YEAR
                else:
                    year = CURRENT_YEAR  # Fallback
                    
            key = f"{sport}_{league_id}_{year}"
            
            # Check if we have credentials for this session
            espn_s2 = None
            swid = None
            if session_id in self.credentials:
                espn_s2 = self.credentials[session_id].get('espn_s2')
                swid = self.credentials[session_id].get('swid')
            
            # Create league cache key including auth info
            cache_key = f"{key}_{espn_s2}_{swid}"
            
            if cache_key not in self.leagues:
                log_error(f"Creating new {sport} league instance for {league_id}, year {year}")
                try:
                    if sport == "football":
                        self.leagues[cache_key] = football.League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
                    elif sport == "baseball":
                        self.leagues[cache_key] = baseball.League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
                    else:
                        raise ValueError(f"Unsupported sport: {sport}")
                except Exception as e:
                    log_error(f"Error creating {sport} league: {str(e)}")
                    raise
            
            return self.leagues[cache_key]
        
        def store_credentials(self, session_id, espn_s2, swid):
            """Store credentials for a session"""
            self.credentials[session_id] = {
                'espn_s2': espn_s2,
                'swid': swid
            }
            log_error(f"Stored credentials for session {session_id}")
        
        def clear_credentials(self, session_id):
            """Clear credentials for a session"""
            if session_id in self.credentials:
                del self.credentials[session_id]
                log_error(f"Cleared credentials for session {session_id}")

    # Create our API instance
    api = ESPNFantasyAPI()

    # Store a session map
    SESSION_ID = "default_session"

    @mcp.tool()
    async def authenticate(espn_s2: str, swid: str) -> str:
        """Store ESPN authentication credentials for this session.
        
        Args:
            espn_s2: The ESPN_S2 cookie value from your ESPN account
            swid: The SWID cookie value from your ESPN account
        """
        try:
            log_error("Authenticating...")
            # Store credentials for this session
            api.store_credentials(SESSION_ID, espn_s2, swid)
            
            return "Authentication successful. Your credentials are stored for this session only."
        except Exception as e:
            log_error(f"Authentication error: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Authentication error: {str(e)}"

    @mcp.tool()
    async def get_league_info(league_id: int, year: int = None, sport: str = "football") -> str:
        """Get basic information about a fantasy sports league.
        
        Args:
            league_id: The ESPN fantasy league ID
            year: Optional year for historical data (defaults to current season based on sport)
            sport: Sport type (football or baseball, defaults to football)
        """
        try:
            log_error(f"Getting {sport} league info for league {league_id}, year {year if year else 'current'}")
            # Get league using stored credentials
            league = api.get_league(SESSION_ID, league_id, year, sport)
            
            info = {
                "name": league.settings.name,
                "year": league.year,
                "current_week": league.current_week,
                "team_count": len(league.teams),
                "teams": [team.team_name for team in league.teams],
                "scoring_type": league.settings.scoring_type,
            }
            
            # Add football-specific field if sport is football
            if sport == "football":
                info["nfl_week"] = league.nfl_week
            
            return str(info)
        except Exception as e:
            log_error(f"Error retrieving {sport} league info: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            if "401" in str(e) or "Private" in str(e):
                return ("This appears to be a private league. Please use the authenticate tool first with your "
                      "ESPN_S2 and SWID cookies to access private leagues.")
            return f"Error retrieving {sport} league: {str(e)}"

    @mcp.tool()
    async def get_team_roster(league_id: int, team_id: int, year: int = None, sport: str = "football") -> str:
        """Get a team's current roster.
        
        Args:
            league_id: The ESPN fantasy league ID
            team_id: The team ID in the league (usually 1-12)
            year: Optional year for historical data (defaults to current season based on sport)
            sport: Sport type (football or baseball, defaults to football)
        """
        try:
            log_error(f"Getting {sport} team roster for league {league_id}, team {team_id}, year {year if year else 'current'}")
            # Get league using stored credentials
            league = api.get_league(SESSION_ID, league_id, year, sport)
            
            # Team IDs in ESPN API are 1-based
            if team_id < 1 or team_id > len(league.teams):
                return f"Invalid team_id. Must be between 1 and {len(league.teams)}"
            
            team = league.teams[team_id - 1]
            
            roster_info = {
                "team_name": getattr(team, "team_name", "Unknown"),
                "owner": getattr(team, "owners", ["Unknown"]),
                "wins": getattr(team, "wins", 0),
                "losses": getattr(team, "losses", 0), 
                "roster": []
            }
            
            for player in team.roster:
                player_info = {
                    "name": getattr(player, "name", "Unknown"),
                    "position": getattr(player, "position", "Unknown"),
                    "proTeam": getattr(player, "proTeam", "Unknown"),
                    "stats": getattr(player, "stats", {})
                }
                
                # Add optional fields that might not be available in all sports
                if hasattr(player, "total_points"):
                    player_info["points"] = player.total_points
                
                if hasattr(player, "projected_total_points"):
                    player_info["projected_points"] = player.projected_total_points
                
                roster_info["roster"].append(player_info)
            
            return str(roster_info)
        except Exception as e:
            log_error(f"Error retrieving {sport} team roster: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            if "401" in str(e) or "Private" in str(e):
                return ("This appears to be a private league. Please use the authenticate tool first with your "
                      "ESPN_S2 and SWID cookies to access private leagues.")
            return f"Error retrieving {sport} team roster: {str(e)}"
        
    @mcp.tool()
    async def get_team_info(league_id: int, team_id: int, year: int = None, sport: str = "football") -> str:
        """Get a team's general information. Including points scored, transactions, etc.
        
        Args:
            league_id: The ESPN fantasy league ID
            team_id: The team ID in the league (usually 1-12)
            year: Optional year for historical data (defaults to current season based on sport)
            sport: Sport type (football or baseball, defaults to football)
        """
        try:
            log_error(f"Getting {sport} team info for league {league_id}, team {team_id}, year {year if year else 'current'}")
            # Get league using stored credentials
            league = api.get_league(SESSION_ID, league_id, year, sport)

            # Team IDs in ESPN API are 1-based
            if team_id < 1 or team_id > len(league.teams):
                return f"Invalid team_id. Must be between 1 and {len(league.teams)}"
            
            team = league.teams[team_id - 1]

            # Use getattr to safely access attributes that might not be present in all sports
            team_info = {
                "team_name": getattr(team, "team_name", "Unknown"),
                "owner": getattr(team, "owners", ["Unknown"]),
                "wins": getattr(team, "wins", 0),
                "losses": getattr(team, "losses", 0),
                "ties": getattr(team, "ties", 0),
                "points_for": getattr(team, "points_for", 0),
                "points_against": getattr(team, "points_against", 0),
            }
            
            # Add optional attributes if they exist
            optional_attrs = [
                "acquisitions", "drops", "trades", "playoff_pct", 
                "final_standing", "outcomes"
            ]
            
            for attr in optional_attrs:
                if hasattr(team, attr):
                    team_info[attr] = getattr(team, attr)
            
            return str(team_info)

        except Exception as e:
            log_error(f"Error retrieving {sport} team info: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            if "401" in str(e) or "Private" in str(e):
                return ("This appears to be a private league. Please use the authenticate tool first with your "
                      "ESPN_S2 and SWID cookies to access private leagues.")
            return f"Error retrieving {sport} team info: {str(e)}"

    @mcp.tool()
    async def get_player_stats(league_id: int, player_name: str, year: int = None, sport: str = "football") -> str:
        """Get stats for a specific player.
        
        Args:
            league_id: The ESPN fantasy league ID
            player_name: Name of the player to search for
            year: Optional year for historical data (defaults to current season based on sport)
            sport: Sport type (football or baseball, defaults to football)
        """
        try:
            log_error(f"Getting {sport} player stats for {player_name} in league {league_id}, year {year if year else 'current'}")
            # Get league using stored credentials
            league = api.get_league(SESSION_ID, league_id, year, sport)
            
            # Search for player by name
            player = None
            for team in league.teams:
                for roster_player in team.roster:
                    if player_name.lower() in roster_player.name.lower():
                        player = roster_player
                        break
                if player:
                    break
            
            if not player:
                return f"Player '{player_name}' not found in {sport} league {league_id}"
            
            # Get player stats using safe attribute access
            stats = {
                "name": getattr(player, "name", "Unknown"),
                "position": getattr(player, "position", "Unknown"),
                "team": getattr(player, "proTeam", "Unknown"),
                "stats": getattr(player, "stats", {})
            }
            
            # Add optional fields that might not be available in all sports
            optional_attrs = [
                "total_points", "projected_total_points", "injured"
            ]
            
            for attr in optional_attrs:
                if hasattr(player, attr):
                    # Map to appropriate key names
                    key = "points" if attr == "total_points" else "projected_points" if attr == "projected_total_points" else attr
                    stats[key] = getattr(player, attr)
            
            return str(stats)
        except Exception as e:
            log_error(f"Error retrieving {sport} player stats: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            if "401" in str(e) or "Private" in str(e):
                return ("This appears to be a private league. Please use the authenticate tool first with your "
                      "ESPN_S2 and SWID cookies to access private leagues.")
            return f"Error retrieving {sport} player stats: {str(e)}"

    @mcp.tool()
    async def get_league_standings(league_id: int, year: int = None, sport: str = "football") -> str:
        """Get current standings for a league.
        
        Args:
            league_id: The ESPN fantasy league ID
            year: Optional year for historical data (defaults to current season based on sport)
            sport: Sport type (football or baseball, defaults to football)
        """
        try:
            log_error(f"Getting {sport} league standings for league {league_id}, year {year if year else 'current'}")
            # Get league using stored credentials
            league = api.get_league(SESSION_ID, league_id, year, sport)
            
            # Check scoring type to determine sorting
            scoring_type = getattr(league.settings, "scoring_type", "").lower()
            is_roto = "roto" in scoring_type
            
            # Sort teams based on sport and scoring type
            if is_roto and sport == "baseball":
                # For rotisserie baseball, sort by roto_points if available, otherwise fall back to points_for
                sorted_teams = sorted(league.teams, 
                                    key=lambda x: getattr(x, "roto_points", getattr(x, "points_for", 0)),
                                    reverse=True)
            else:
                # For head-to-head leagues (football or baseball), sort by wins then points
                sorted_teams = sorted(league.teams, 
                                    key=lambda x: (getattr(x, "wins", 0), getattr(x, "points_for", 0)),
                                    reverse=True)
            
            standings = []
            for i, team in enumerate(sorted_teams):
                team_standing = {
                    "rank": i + 1,
                    "team_name": getattr(team, "team_name", "Unknown"),
                    "owner": getattr(team, "owners", ["Unknown"]),
                }
                
                # Add attributes if they exist
                for attr in ["wins", "losses", "points_for", "points_against"]:
                    if hasattr(team, attr):
                        team_standing[attr] = getattr(team, attr)
                
                # For rotisserie baseball, include roto_points if available
                if is_roto and sport == "baseball" and hasattr(team, "roto_points"):
                    team_standing["roto_points"] = team.roto_points
                
                standings.append(team_standing)
            
            return str(standings)
        except Exception as e:
            log_error(f"Error retrieving {sport} league standings: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            if "401" in str(e) or "Private" in str(e):
                return ("This appears to be a private league. Please use the authenticate tool first with your "
                      "ESPN_S2 and SWID cookies to access private leagues.")
            return f"Error retrieving {sport} league standings: {str(e)}"

    @mcp.tool()
    async def get_matchup_info(league_id: int, week: int = None, year: int = None, sport: str = "football") -> str:
        """Get matchup information for a specific week.
        
        Args:
            league_id: The ESPN fantasy league ID
            week: The week number (if None, uses current week)
            year: Optional year for historical data (defaults to current season based on sport)
            sport: Sport type (football or baseball, defaults to football)
        """
        try:
            log_error(f"Getting {sport} matchup info for league {league_id}, week {week}, year {year if year else 'current'}")
            # Get league using stored credentials
            league = api.get_league(SESSION_ID, league_id, year, sport)
            
            if week is None:
                week = getattr(league, "current_week", 1)
            
            # Try to get max weeks from league settings if available
            max_week = None
            if hasattr(league, "settings") and hasattr(league.settings, "reg_season_count"):
                max_week = league.settings.reg_season_count
            else:
                # Fall back to sport-specific defaults
                max_week = 17 if sport == "football" else 25  # Football has ~17 weeks, baseball ~25
                
            if week < 1 or (max_week and week > max_week):
                return f"Invalid week number for {sport}. Must be between 1 and {max_week}"
            
            matchups = league.box_scores(week)
            
            matchup_info = []
            for matchup in matchups:
                matchup_data = {}
                
                # Handle home team
                if hasattr(matchup, "home_team") and matchup.home_team:
                    matchup_data["home_team"] = getattr(matchup.home_team, "team_name", "Unknown")
                    matchup_data["home_score"] = getattr(matchup, "home_score", 0)
                else:
                    matchup_data["home_team"] = "Unknown"
                    matchup_data["home_score"] = 0
                
                # Handle away team
                if hasattr(matchup, "away_team") and matchup.away_team:
                    matchup_data["away_team"] = getattr(matchup.away_team, "team_name", "Unknown")
                    matchup_data["away_score"] = getattr(matchup, "away_score", 0)
                else:
                    matchup_data["away_team"] = "BYE"
                    matchup_data["away_score"] = 0
                
                # Determine winner
                home_score = matchup_data["home_score"]
                away_score = matchup_data["away_score"]
                
                if matchup_data["away_team"] == "BYE":
                    matchup_data["winner"] = "HOME"
                elif home_score > away_score:
                    matchup_data["winner"] = "HOME"
                elif away_score > home_score:
                    matchup_data["winner"] = "AWAY"
                else:
                    matchup_data["winner"] = "TIE"
                
                matchup_info.append(matchup_data)
            
            return str(matchup_info)
        except Exception as e:
            log_error(f"Error retrieving {sport} matchup information: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            if "401" in str(e) or "Private" in str(e):
                return ("This appears to be a private league. Please use the authenticate tool first with your "
                      "ESPN_S2 and SWID cookies to access private leagues.")
            return f"Error retrieving {sport} matchup information: {str(e)}"

    @mcp.tool()
    async def logout() -> str:
        """Clear stored authentication credentials for this session."""
        try:
            log_error("Logging out...")
            # Clear credentials for this session
            api.clear_credentials(SESSION_ID)
            
            return "Authentication credentials have been cleared."
        except Exception as e:
            log_error(f"Error logging out: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Error logging out: {str(e)}"

    if __name__ == "__main__":
        # Run the server
        log_error("Starting MCP server...")
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