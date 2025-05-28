"""
Utility functions and services for ESPN Fantasy Baseball MCP Server
Handles league caching, serialization, and error handling
"""

import sys
import hashlib
from typing import Dict, Any, Optional
from espn_api import baseball
import datetime
from metadata import POSITION_MAP, STATS_MAP, ACTIVITY_MAP, get_activity_name, ESPN_ACTION_TYPE_MAP

# Apply ESPN API authentication patch to fix None cookies bug
try:
    from espn_api_patch import apply_espn_api_patch
    apply_espn_api_patch()
except Exception as e:
    print(f"⚠ ESPN API patch not applied: {str(e)}", file=sys.stderr)

def log_error(message: str):
    """Add stderr logging for Claude Desktop to see"""
    print(message, file=sys.stderr)

def handle_error(error: Exception, context: str) -> Dict[str, str]:
    """Global error handler that returns consistent error responses"""
    error_msg = str(error)
    log_error(f"Error in {context}: {error_msg}")
    
    if "401" in error_msg or "Private" in error_msg:
        return {
            "error": "This appears to be a private league. Please use the authenticate tool first with your ESPN_S2 and SWID cookies to access private leagues."
        }
    
    return {"error": f"Error in {context}: {error_msg}"}

def convert_timestamp(timestamp: Optional[int]) -> Optional[str]:
    """
    Convert ESPN timestamp to readable date string with validation.
    
    Args:
        timestamp: ESPN timestamp (usually in milliseconds)
        
    Returns:
        Formatted date string or None if invalid
    """
    if timestamp is None:
        return None
    
    try:
        # ESPN timestamps are usually in milliseconds
        if timestamp > 9999999999:  # More than 10 digits, likely milliseconds
            timestamp = timestamp / 1000
        
        # Validate timestamp is reasonable (not in far future)
        current_time = datetime.datetime.now().timestamp()
        future_limit = current_time + (2 * 365 * 24 * 60 * 60)  # 2 years in future
        
        if timestamp > future_limit:
            log_error(f"Invalid future timestamp detected: {timestamp}")
            return f"INVALID_FUTURE_DATE_{int(timestamp)}"
        
        # Convert to datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    except (ValueError, OSError) as e:
        log_error(f"Error converting timestamp {timestamp}: {str(e)}")
        return f"INVALID_TIMESTAMP_{timestamp}"

class BaseballLeagueService:
    """Service for caching and managing ESPN Baseball League objects"""
    
    def __init__(self):
        self.leagues: Dict[str, Any] = {}
    
    def _generate_auth_hash(self, espn_s2: Optional[str], swid: Optional[str]) -> str:
        """Generate a hash for authentication credentials"""
        if not espn_s2 or not swid:
            return "no_auth"
        
        combined = f"{espn_s2}_{swid}"
        return hashlib.md5(combined.encode()).hexdigest()[:8]
    
    def get_league(self, league_id: int, year: Optional[int] = None, 
                   espn_s2: Optional[str] = None, swid: Optional[str] = None) -> Any:
        """Get a cached league instance or create a new one"""
        
        # Determine year if not provided
        if year is None:
            current_date = datetime.datetime.now()
            # Baseball season runs spring to fall within the same calendar year
            # But if it's early in the year (before March), might be referring to previous year
            if current_date.month < 3:
                year = current_date.year - 1
            else:
                year = current_date.year
            
            log_error(f"Auto-detected year {year} for league {league_id}")
        
        # Generate cache key
        auth_hash = self._generate_auth_hash(espn_s2, swid)
        cache_key = f"baseball_{league_id}_{year}_{auth_hash}"
        
        # Return cached league if available
        if cache_key in self.leagues:
            return self.leagues[cache_key]
        
        # Create new league instance
        log_error(f"Creating new baseball league instance for {league_id}, year {year}")
        log_error(f"Auth provided: ESPN_S2={'Yes' if espn_s2 else 'No'}, SWID={'Yes' if swid else 'No'}")
        try:
            league = baseball.League(
                league_id=league_id, 
                year=year, 
                espn_s2=espn_s2, 
                swid=swid
            )
            log_error(f"League created successfully. League name: {getattr(league, 'name', 'Unknown')}")
            self.leagues[cache_key] = league
            return league
        except Exception as e:
            import traceback
            log_error(f"Error creating baseball league: {str(e)}")
            log_error(f"Full traceback: {traceback.format_exc()}")
            raise

# Global league service instance
league_service = BaseballLeagueService()

def team_to_dict(team: Any) -> Dict[str, Any]:
    """Convert a Team object to a dictionary"""
    try:
        team_dict = {
            "team_id": getattr(team, "team_id", None),
            "team_name": getattr(team, "team_name", "Unknown"),
            "team_abbrev": getattr(team, "team_abbrev", ""),
            "owner": getattr(team, "owner", "Unknown"),
            "wins": getattr(team, "wins", 0),
            "losses": getattr(team, "losses", 0),
            "ties": getattr(team, "ties", 0),
            "points_for": getattr(team, "points_for", 0),
            "points_against": getattr(team, "points_against", 0),
            "division_id": getattr(team, "division_id", None),
            "division_name": getattr(team, "division_name", ""),
            "logo_url": getattr(team, "logo_url", ""),
            "standing": getattr(team, "standing", None),
        }
        
        # Add optional attributes if they exist
        optional_attrs = ["acquisitions", "drops", "trades", "moves", "playoff_pct"]
        for attr in optional_attrs:
            if hasattr(team, attr):
                team_dict[attr] = getattr(team, attr)
        
        return team_dict
    except Exception as e:
        log_error(f"Error serializing team: {str(e)}")
        return {"error": f"Error serializing team: {str(e)}"}

def player_to_dict(player: Any) -> Dict[str, Any]:
    """Convert a Player object to a dictionary"""
    try:
        player_dict = {
            "player_id": getattr(player, "playerId", getattr(player, "player_id", None)),
            "name": getattr(player, "name", "Unknown"),
            "position": getattr(player, "position", "Unknown"),
            "pro_team": getattr(player, "proTeam", getattr(player, "pro_team", "Unknown")),
            "pro_team_id": getattr(player, "proTeamId", getattr(player, "pro_team_id", None)),
        }
        
        # Convert eligible positions if they exist
        if hasattr(player, "eligibleSlots"):
            eligible_positions = []
            for slot_id in player.eligibleSlots:
                position_name = POSITION_MAP.get(slot_id, f"Position_{slot_id}")
                if position_name not in eligible_positions:
                    eligible_positions.append(position_name)
            player_dict["eligible_positions"] = eligible_positions
        
        # Add stats if available
        if hasattr(player, "stats"):
            converted_stats = {}
            for stat_id, value in player.stats.items():
                stat_name = STATS_MAP.get(stat_id, f"stat_{stat_id}")
                converted_stats[stat_name] = value
            player_dict["stats"] = converted_stats
        
        # Add optional attributes
        optional_attrs = [
            "total_points", "projected_total_points", "avg_points", 
            "last_week_points", "percent_owned", "percent_started"
        ]
        for attr in optional_attrs:
            if hasattr(player, attr):
                player_dict[attr] = getattr(player, attr)
        
        # Handle injury status
        if hasattr(player, "injuryStatus"):
            player_dict["injury_status"] = getattr(player, "injuryStatus", "ACTIVE")
        
        return player_dict
    except Exception as e:
        log_error(f"Error serializing player: {str(e)}")
        return {"error": f"Error serializing player: {str(e)}"}

def boxscore_to_dict(boxscore: Any) -> Dict[str, Any]:
    """Convert a BoxScore object to a dictionary"""
    try:
        boxscore_dict = {
            "matchup_period": getattr(boxscore, "matchup_period", None),
            "home_team": team_to_dict(boxscore.home_team) if hasattr(boxscore, "home_team") else None,
            "away_team": team_to_dict(boxscore.away_team) if hasattr(boxscore, "away_team") else None,
            "home_score": getattr(boxscore, "home_score", 0),
            "away_score": getattr(boxscore, "away_score", 0),
        }
        
        # Determine winner
        if boxscore_dict["home_score"] > boxscore_dict["away_score"]:
            boxscore_dict["winner"] = "HOME"
        elif boxscore_dict["away_score"] > boxscore_dict["home_score"]:
            boxscore_dict["winner"] = "AWAY" 
        else:
            boxscore_dict["winner"] = "TIE"
        
        # Add team stats for category leagues
        if hasattr(boxscore, "home_stats"):
            home_stats = {}
            for stat_id, value in boxscore.home_stats.items():
                stat_name = STATS_MAP.get(stat_id, f"stat_{stat_id}")
                home_stats[stat_name] = value
            boxscore_dict["home_stats"] = home_stats
        
        if hasattr(boxscore, "away_stats"):
            away_stats = {}
            for stat_id, value in boxscore.away_stats.items():
                stat_name = STATS_MAP.get(stat_id, f"stat_{stat_id}")
                away_stats[stat_name] = value
            boxscore_dict["away_stats"] = away_stats
        
        # Add lineup information if available
        if hasattr(boxscore, "home_lineup"):
            boxscore_dict["home_lineup"] = [boxplayer_to_dict(bp) for bp in boxscore.home_lineup]
        
        if hasattr(boxscore, "away_lineup"):
            boxscore_dict["away_lineup"] = [boxplayer_to_dict(bp) for bp in boxscore.away_lineup]
        
        return boxscore_dict
    except Exception as e:
        log_error(f"Error serializing boxscore: {str(e)}")
        return {"error": f"Error serializing boxscore: {str(e)}"}

def boxplayer_to_dict(boxplayer: Any) -> Dict[str, Any]:
    """Convert a BoxPlayer object to a dictionary"""
    try:
        boxplayer_dict = {
            "player": player_to_dict(boxplayer.player) if hasattr(boxplayer, "player") else None,
            "position": POSITION_MAP.get(getattr(boxplayer, "position", None), getattr(boxplayer, "position", "Unknown")),
            "points": getattr(boxplayer, "points", 0),
            "projected_points": getattr(boxplayer, "projected_points", 0),
        }
        
        # Add stats if available
        if hasattr(boxplayer, "stats"):
            converted_stats = {}
            for stat_id, value in boxplayer.stats.items():
                stat_name = STATS_MAP.get(stat_id, f"stat_{stat_id}")
                converted_stats[stat_name] = value
            boxplayer_dict["stats"] = converted_stats
        
        return boxplayer_dict
    except Exception as e:
        log_error(f"Error serializing boxplayer: {str(e)}")
        return {"error": f"Error serializing boxplayer: {str(e)}"}

def activity_to_dict(activity: Any) -> Dict[str, Any]:
    """
    Convert an ESPN Baseball Activity object to a dictionary.
    ESPN Baseball activities use action tuples instead of msg_type codes.
    """
    try:
        # Initialize basic dict with timestamp conversion
        raw_date = getattr(activity, "date", None)
        activity_dict = {
            "type": "UNKNOWN_ACTIVITY",  # Will be determined from actions
            "date": convert_timestamp(raw_date),
            "raw_timestamp": raw_date,
            "team": None,
            "added_player": None,
            "dropped_player": None,
            "players_in": [],
            "players_out": [],
        }

        # ESPN Baseball activities have actions as tuples: (Team, action_type, player_name)
        if hasattr(activity, 'actions') and activity.actions:
            log_error(f"Processing activity with {len(activity.actions)} actions")
            
            for i, action_tuple in enumerate(activity.actions):
                try:
                    if isinstance(action_tuple, tuple) and len(action_tuple) == 3:
                        team_obj, action_type, player_name = action_tuple
                        
                        log_error(f"Action {i}: Team={team_obj}, Type='{action_type}', Player='{player_name}'")
                        
                        # Extract team information (use first team found)
                        if activity_dict["team"] is None and team_obj:
                            activity_dict["team"] = team_to_dict(team_obj)
                        
                        # Map ESPN action type to our standard types
                        mapped_type = ESPN_ACTION_TYPE_MAP.get(action_type)
                        if mapped_type:
                            # For activities with multiple actions, use the first recognizable type
                            if activity_dict["type"] == "UNKNOWN_ACTIVITY":
                                activity_dict["type"] = mapped_type
                            
                            # Extract player information based on action type
                            player_dict = {"name": player_name}
                            
                            if mapped_type == "ADD":
                                if not activity_dict["added_player"]:
                                    activity_dict["added_player"] = player_dict
                                    # Determine source from action type
                                    if "FA" in action_type:
                                        activity_dict["source"] = "FREE_AGENT"
                                    elif "WAIVER" in action_type:
                                        activity_dict["source"] = "WAIVERS"
                                        
                            elif mapped_type == "DROP":
                                if not activity_dict["dropped_player"]:
                                    activity_dict["dropped_player"] = player_dict
                                    
                            elif mapped_type == "TRADE_ACCEPTED":
                                # For trades, we need to determine direction based on team perspective
                                # Since we don't have clear trade direction info, add to players_in for now
                                activity_dict["players_in"].append(player_dict)
                        
                        else:
                            log_error(f"Unknown action type: '{action_type}'")
                    
                    else:
                        log_error(f"Unexpected action format: {action_tuple}")
                
                except Exception as e:
                    log_error(f"Error processing action {i}: {str(e)}")
                    continue
        
        # If we have both ADD and DROP in the same activity, it's likely a roster move
        if (activity_dict.get("added_player") and activity_dict.get("dropped_player") and 
            activity_dict["type"] in ["ADD", "DROP"]):
            activity_dict["type"] = "ROSTER_MOVE"
        
        log_error(f"Final activity type: {activity_dict['type']}")
        return activity_dict
        
    except Exception as e:
        log_error(f"Error serializing activity: {str(e)}")
        return {
            "error": f"Error serializing activity: {str(e)}",
            "type": "ERROR_PROCESSING",
            "date": convert_timestamp(getattr(activity, "date", None)),
            "raw_timestamp": getattr(activity, "date", None)
        }

def pick_to_dict(pick: Any) -> Dict[str, Any]:
    """Convert a Pick object to a dictionary with null safety"""
    try:
        # Safely get attributes with null handling
        round_num = getattr(pick, "round_num", None)
        round_pick = getattr(pick, "round_pick", None)
        overall_pick = getattr(pick, "pick_num", None)
        
        pick_dict = {
            "round_num": round_num if round_num is not None else 0,
            "round_pick": round_pick if round_pick is not None else 0,
            "overall_pick": overall_pick if overall_pick is not None else 0,
            "team": team_to_dict(pick.team) if hasattr(pick, "team") and pick.team else None,
            "player": player_to_dict(pick.player) if hasattr(pick, "player") and pick.player else None,
        }
        
        # Add auction-specific fields with null safety
        if hasattr(pick, "auction_price"):
            auction_price = pick.auction_price
            pick_dict["auction_price"] = auction_price if auction_price is not None else 0
        
        # Add keeper flag if available
        if hasattr(pick, "keeper_status"):
            pick_dict["keeper"] = bool(pick.keeper_status)
        
        return pick_dict
    except Exception as e:
        log_error(f"Error serializing pick: {str(e)}")
        return {
            "error": f"Error serializing pick: {str(e)}",
            "round_num": 0,
            "round_pick": 0,
            "overall_pick": 0,
            "team": None,
            "player": None
        }