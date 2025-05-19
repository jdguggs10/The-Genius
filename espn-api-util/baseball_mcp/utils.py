"""
Utility functions and services for ESPN Fantasy Baseball MCP Server
Handles league caching, serialization, and error handling
"""

import sys
import hashlib
from typing import Dict, Any, Optional
from espn_api import baseball
import datetime
from metadata import POSITION_MAP, STATS_MAP, ACTIVITY_MAP

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
            year = current_date.year
        
        # Generate cache key
        auth_hash = self._generate_auth_hash(espn_s2, swid)
        cache_key = f"baseball_{league_id}_{year}_{auth_hash}"
        
        # Return cached league if available
        if cache_key in self.leagues:
            return self.leagues[cache_key]
        
        # Create new league instance
        log_error(f"Creating new baseball league instance for {league_id}, year {year}")
        try:
            league = baseball.League(
                league_id=league_id, 
                year=year, 
                espn_s2=espn_s2, 
                swid=swid
            )
            self.leagues[cache_key] = league
            return league
        except Exception as e:
            log_error(f"Error creating baseball league: {str(e)}")
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
    """Convert an Activity object to a dictionary"""
    try:
        # Convert activity type from ESPN code to friendly name
        activity_type = None
        for friendly_name, espn_codes in ACTIVITY_MAP.items():
            if hasattr(activity, "msg_type") and activity.msg_type in espn_codes:
                activity_type = friendly_name
                break
        
        if not activity_type:
            activity_type = f"UNKNOWN_{getattr(activity, 'msg_type', 'NO_TYPE')}"
        
        activity_dict = {
            "type": activity_type,
            "date": getattr(activity, "date", None),
            "team": team_to_dict(activity.team) if hasattr(activity, "team") else None,
        }
        
        # Handle different activity types
        if activity_type in ["ADD", "WAIVER_MOVED"]:
            if hasattr(activity, "player"):
                activity_dict["added_player"] = player_to_dict(activity.player)
            if hasattr(activity, "source"):
                activity_dict["source"] = activity.source
            if hasattr(activity, "bid_amount"):
                activity_dict["bid_amount"] = activity.bid_amount
        
        elif activity_type == "DROP":
            if hasattr(activity, "player"):
                activity_dict["dropped_player"] = player_to_dict(activity.player)
        
        elif activity_type in ["TRADE_ACCEPTED", "TRADE_PENDING"]:
            if hasattr(activity, "trade_partner"):
                activity_dict["trade_partner"] = team_to_dict(activity.trade_partner)
            if hasattr(activity, "players_in"):
                activity_dict["players_in"] = [player_to_dict(p) for p in activity.players_in]
            if hasattr(activity, "players_out"):
                activity_dict["players_out"] = [player_to_dict(p) for p in activity.players_out]
        
        return activity_dict
    except Exception as e:
        log_error(f"Error serializing activity: {str(e)}")
        return {"error": f"Error serializing activity: {str(e)}"}

def pick_to_dict(pick: Any) -> Dict[str, Any]:
    """Convert a Pick object to a dictionary"""
    try:
        pick_dict = {
            "round_num": getattr(pick, "round_num", None),
            "round_pick": getattr(pick, "round_pick", None),
            "overall_pick": getattr(pick, "pick_num", None),
            "team": team_to_dict(pick.team) if hasattr(pick, "team") else None,
            "player": player_to_dict(pick.player) if hasattr(pick, "player") else None,
        }
        
        # Add auction-specific fields
        if hasattr(pick, "auction_price"):
            pick_dict["auction_price"] = pick.auction_price
        
        # Add keeper flag if available
        if hasattr(pick, "keeper_status"):
            pick_dict["keeper"] = pick.keeper_status
        
        return pick_dict
    except Exception as e:
        log_error(f"Error serializing pick: {str(e)}")
        return {"error": f"Error serializing pick: {str(e)}"}