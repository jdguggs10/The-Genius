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

# Define a speculative map for common action types found in espn-api
# This map might need adjustment based on actual data from activity.actions
# Key: action.type (or similar attribute from an action object/dict)
# Value: The standardized activity_type we want to use
SPECULATIVE_ACTION_TYPE_MAP = {
    # Common action types from espn_api (these are guesses)
    "PLAYERMOVED": "TRADE_ACCEPTED", # Often used for trades
    "PLAYERADDED": "ADD",
    "PLAYERDROPPED": "DROP",
    "FAAB_BID_PROCESSED": "WAIVER_MOVED", # Or just ADD if player is added
    "ROSTER_ORDER_CHANGED": "SETTINGS_CHANGED", # Or a more specific type
    # Potential dict keys if action is a dict and 'type' is a string
    "ADD": "ADD",
    "DROP": "DROP",
    "TRADED": "TRADE_ACCEPTED",
    "WAIVER": "WAIVER_MOVED", # Could also be ADD if player is involved
}

def activity_to_dict(activity: Any) -> Dict[str, Any]:
    """Convert an Activity object to a dictionary, with fallback to activity.actions"""
    try:
        original_msg_type = getattr(activity, 'msg_type', 'NO_TYPE')
        derived_activity_type = None

        # 1. Primary type determination (from activity.msg_type)
        if hasattr(activity, "msg_type"):
            for friendly_name, espn_codes in ACTIVITY_MAP.items():
                if activity.msg_type in espn_codes:
                    derived_activity_type = friendly_name
                    break
        
        # Initialize basic dict
        activity_dict = {
            "type": derived_activity_type, # Will be updated if None or UNKNOWN after this
            "date": getattr(activity, "date", None),
            # Use activity.team if it exists and is not None
            "team": team_to_dict(activity.team) if hasattr(activity, "team") and activity.team else None
        }

        # Store data derived from actions separately for clarity before merging
        action_derived_data = {
            "type": None,
            "team": None,
            "added_player": None,
            "dropped_player": None,
            "players_in": [],
            "players_out": [],
            "source": None, # e.g. for waiver source from action
            "bid_amount": None, # e.g. for waiver bid from action
        }
        actions_parsed_type = None
        parsed_actions = False


        # 2. Secondary Type and Data Extraction from activity.actions
        if (not derived_activity_type or derived_activity_type.startswith("UNKNOWN_")) and \
           hasattr(activity, 'actions') and activity.actions and isinstance(activity.actions, list):
            
            parsed_actions = True # Flag that we've entered action parsing logic

            for action_item in activity.actions:
                if not action_item: continue

                current_action_type_str = None
                # Try to get type from action_item (could be obj.type or dict['type'])
                if hasattr(action_item, 'type'):
                    current_action_type_str = str(getattr(action_item, 'type')).upper()
                elif isinstance(action_item, dict) and 'type' in action_item:
                    current_action_type_str = str(action_item.get('type')).upper()

                # A. Infer activity type from action_item.type
                if actions_parsed_type is None and current_action_type_str:
                    actions_parsed_type = SPECULATIVE_ACTION_TYPE_MAP.get(current_action_type_str)

                # B. Infer activity type from action_item attributes if type still unknown
                if actions_parsed_type is None:
                    if hasattr(action_item, 'playerAdded') and getattr(action_item, 'playerAdded'):
                        actions_parsed_type = 'ADD'
                    elif hasattr(action_item, 'playerDropped') and getattr(action_item, 'playerDropped'):
                        actions_parsed_type = 'DROP'
                    # Add more specific inferences if needed, e.g. for trades by checking for fromTeamId/toTeamId

                # C. Extract team from action (if main team is missing)
                if action_derived_data["team"] is None: # Only take first one found
                    action_team_id = None
                    if hasattr(action_item, 'teamId'): action_team_id = getattr(action_item, 'teamId')
                    elif isinstance(action_item, dict) and 'teamId' in action_item: action_team_id = action_item.get('teamId')
                    
                    if action_team_id is not None: # Check for not None, as teamId could be 0
                        action_derived_data["team"] = {"team_id": action_team_id, "team_name": f"Team {action_team_id} (from action)"}

                # D. Extract player details based on action_item (for ADD/DROP/TRADE)
                # This part is tricky because one activity can have multiple actions (e.g. a trade)
                # We'll focus on populating based on what the action_item directly provides.
                # This logic will be further refined in step 6 for fallbacks.

                action_player_obj = getattr(action_item, 'player', None)
                action_player_id = getattr(action_item, 'playerId', None)
                if isinstance(action_item, dict): # If action_item is a dict
                    action_player_obj = action_item.get('player', action_player_obj)
                    action_player_id = action_item.get('playerId', action_player_id)

                # Simplistic player extraction for now, will be refined
                # If the action type (or inferred type) is ADD:
                if (actions_parsed_type == 'ADD' or current_action_type_str == 'PLAYERADDED') and not action_derived_data["added_player"]:
                    if action_player_obj:
                        action_derived_data["added_player"] = player_to_dict(action_player_obj)
                    elif action_player_id:
                        action_derived_data["added_player"] = {"player_id": action_player_id, "name": "Player (from action)"}
                
                # If the action type (or inferred type) is DROP:
                elif (actions_parsed_type == 'DROP' or current_action_type_str == 'PLAYERDROPPED') and not action_derived_data["dropped_player"]:
                    if action_player_obj:
                        action_derived_data["dropped_player"] = player_to_dict(action_player_obj)
                    elif action_player_id:
                        action_derived_data["dropped_player"] = {"player_id": action_player_id, "name": "Player (from action)"}

                # For trades, collect all involved players from actions
                # This assumes an action in a trade might have 'playerId', 'fromTeamId', 'toTeamId'
                # The main activity.team (or action_derived_data["team"]) is the perspective.
                if (actions_parsed_type == 'TRADE_ACCEPTED' or current_action_type_str == 'PLAYERMOVED'):
                    player_for_trade = None
                    if action_player_obj: player_for_trade = player_to_dict(action_player_obj)
                    elif action_player_id: player_for_trade = {"player_id": action_player_id, "name": "Player (from action)"}

                    if player_for_trade:
                        # Determine if player is 'in' or 'out' based on team IDs in action
                        # This requires knowing the perspective team (activity_dict["team"] or action_derived_data["team"])
                        perspective_team_id = (activity_dict["team"] or action_derived_data["team"] or {}).get("team_id")
                        
                        from_team_id = getattr(action_item, 'fromTeamId', None)
                        to_team_id = getattr(action_item, 'toTeamId', None)
                        if isinstance(action_item, dict):
                            from_team_id = action_item.get('fromTeamId', from_team_id)
                            to_team_id = action_item.get('toTeamId', to_team_id)

                        if perspective_team_id is not None:
                            if to_team_id == perspective_team_id:
                                action_derived_data["players_in"].append(player_for_trade)
                            elif from_team_id == perspective_team_id:
                                action_derived_data["players_out"].append(player_for_trade)
                        # If perspective_team_id is None, we might not be able to categorize, or might add to a generic "involved_players"

                # Extract source and bid_amount if available from actions (e.g., for waivers)
                if hasattr(action_item, 'source') and not action_derived_data["source"]:
                    action_derived_data["source"] = getattr(action_item, 'source')
                if hasattr(action_item, 'bidAmount') and not action_derived_data["bid_amount"]: # espn-api often uses bidAmount
                    action_derived_data["bid_amount"] = getattr(action_item, 'bidAmount')


            # Update derived_activity_type if actions provided one
            if actions_parsed_type:
                derived_activity_type = actions_parsed_type
        
        # 3. Final type assignment in activity_dict
        if not derived_activity_type: # If still no type after msg_type and actions
            activity_dict["type"] = f"UNKNOWN_{original_msg_type}"
        else:
            activity_dict["type"] = derived_activity_type

        # Update team from actions if primary team was None
        if activity_dict["team"] is None and action_derived_data["team"]:
            activity_dict["team"] = action_derived_data["team"]


        # 4. Populate standard fields based on primary attributes (activity.player, etc.)
        # This uses the now finalized activity_dict["type"]
        current_type = activity_dict["type"]
        if not current_type.startswith("UNKNOWN_"):
            if current_type in ["ADD", "WAIVER_MOVED"]:
                if hasattr(activity, "player"): # Primary source
                    activity_dict["added_player"] = player_to_dict(activity.player)
                if hasattr(activity, "source"): activity_dict["source"] = activity.source
                if hasattr(activity, "bid_amount"): activity_dict["bid_amount"] = activity.bid_amount
            
            elif current_type == "DROP":
                if hasattr(activity, "player"): # Primary source
                    activity_dict["dropped_player"] = player_to_dict(activity.player)
            
            elif current_type in ["TRADE_ACCEPTED", "TRADE_PENDING"]: # TRADE_PENDING might not have all details
                if hasattr(activity, "trade_partner"):
                    activity_dict["trade_partner"] = team_to_dict(activity.trade_partner)
                if hasattr(activity, "players_in"): # Primary source
                    activity_dict["players_in"] = [player_to_dict(p) for p in activity.players_in if p]
                if hasattr(activity, "players_out"): # Primary source
                    activity_dict["players_out"] = [player_to_dict(p) for p in activity.players_out if p]

        # 5. Fallback Player/Trade Data Population (using action_derived_data)
        # If primary attributes didn't populate these fields, try with data from actions.
        if parsed_actions: # Only if we actually parsed actions
            if current_type in ["ADD", "WAIVER_MOVED"] and not activity_dict.get("added_player"):
                if action_derived_data["added_player"]: activity_dict["added_player"] = action_derived_data["added_player"]
                # Fallback for source/bid if not set by primary attributes
                if not activity_dict.get("source") and action_derived_data["source"]:
                     activity_dict["source"] = action_derived_data["source"]
                if not activity_dict.get("bid_amount") and action_derived_data["bid_amount"]:
                     activity_dict["bid_amount"] = action_derived_data["bid_amount"]

            elif current_type == "DROP" and not activity_dict.get("dropped_player"):
                if action_derived_data["dropped_player"]: activity_dict["dropped_player"] = action_derived_data["dropped_player"]

            elif current_type == "TRADE_ACCEPTED":
                # For trades, action data for players_in/out might be more reliable or the only source
                # The API might represent all trade legs in actions.
                # If primary attributes (activity.players_in/out) were empty, use action_derived ones.
                if not activity_dict.get("players_in") and action_derived_data["players_in"]:
                    activity_dict["players_in"] = action_derived_data["players_in"]
                if not activity_dict.get("players_out") and action_derived_data["players_out"]:
                    activity_dict["players_out"] = action_derived_data["players_out"]
                
                # Trade partner might also be inferred from actions if not directly available
                # (This is complex: requires identifying other team in actions. Skipped for now.)

        return activity_dict
        
    except Exception as e:
        log_error(f"Error serializing activity: {str(e)}")
        # In case of error, still try to return basic info if possible
        return {
            "error": f"Error serializing activity: {str(e)}",
            "type": f"ERROR_PROCESSING_{getattr(activity, 'msg_type', 'NO_TYPE')}", # Keep original_msg_type if available
            "date": getattr(activity, "date", None) # Attempt to get date even in error
        }

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