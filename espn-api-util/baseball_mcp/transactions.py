"""
Transaction and activity module for ESPN Fantasy Baseball MCP Server
Handles league transactions, adds, drops, trades, and waivers
"""

from typing import Dict, Any, Optional, List
from utils import league_service, handle_error, activity_to_dict
from auth import auth_service

def get_recent_activity(league_id: int, limit: int = 25, activity_type: Optional[str] = None, 
                       offset: int = 0, year: Optional[int] = None,
                       session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get recent activity and transactions for the league.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        limit: Maximum number of activities to return (default 25)
        activity_type: Filter by activity type (e.g., "ADD", "DROP", "TRADE_ACCEPTED")
        offset: Number of activities to skip (for pagination)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of activity/transaction dictionaries
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        from utils import log_error
        log_error(f"Retrieved credentials for session {session_id}: {credentials}")
        log_error(f"ESP_S2 length: {len(espn_s2) if espn_s2 else 0}, SWID length: {len(swid) if swid else 0}")
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Get recent activity from the league with enhanced debugging
        activities = None
        fetch_size = min(limit + offset + 50, 100)  # ESPN API usually limits to 100
        
        from utils import log_error
        log_error(f"Attempting to fetch recent activity for league {league_id}, year {year}")
        
        try:
            # First, try fetching activities without the size parameter
            activities_no_size = league.recent_activity()
            log_error(f"Initial activity fetch returned {len(activities_no_size) if activities_no_size else 0} items")
            
            # Check if activities were returned
            if activities_no_size:
                # Log sample activity for debugging
                if len(activities_no_size) > 0:
                    sample_activity = activities_no_size[0]
                    log_error(f"Sample activity type: {getattr(sample_activity, 'msg_type', 'NO_TYPE')}, has team: {hasattr(sample_activity, 'team')}, team is not None: {hasattr(sample_activity, 'team') and sample_activity.team is not None}")
                
                if len(activities_no_size) > 50:  # Threshold of 50
                    activities = activities_no_size
                else:
                    # Try with fetch_size for more activities
                    try:
                        activities_with_size = league.recent_activity(size=fetch_size)
                        log_error(f"Activity fetch with size {fetch_size} returned {len(activities_with_size) if activities_with_size else 0} items")
                        activities = activities_with_size if activities_with_size else activities_no_size
                    except Exception as e_size:
                        log_error(f"Error calling league.recent_activity(size={fetch_size}): {str(e_size)}")
                        activities = activities_no_size
            else:
                log_error("No activities returned from initial fetch, trying with size parameter")
                try:
                    activities = league.recent_activity(size=fetch_size)
                    log_error(f"Activity fetch with size returned {len(activities) if activities else 0} items")
                except Exception as e_size:
                    log_error(f"Error calling league.recent_activity(size={fetch_size}): {str(e_size)}")
                    activities = []
                        
        except Exception as e_no_size:
            log_error(f"Error calling league.recent_activity() (no size): {str(e_no_size)}")
            # If the first call fails, try the call with fetch_size
            try:
                activities = league.recent_activity(size=fetch_size)
                log_error(f"Fallback activity fetch returned {len(activities) if activities else 0} items")
            except Exception as e_size_after_fail:
                log_error(f"Error calling league.recent_activity(size={fetch_size}) after initial fail: {str(e_size_after_fail)}")
                activities = []

        # Ensure activities is a list for safety
        if activities is None:
            activities = []
            log_error("Final activities is None, converting to empty list")

        # Process and filter activities with enhanced debugging
        processed_activities = []
        log_error(f"Processing {len(activities)} activities")
        
        for i, activity in enumerate(activities):
            try:
                # Convert activity to dictionary
                activity_dict = activity_to_dict(activity)
                
                # Log first few activities for debugging
                if i < 3:
                    log_error(f"Activity {i}: type={activity_dict.get('type')}, date={activity_dict.get('date')}, has_team={activity_dict.get('team') is not None}")
                
                # Filter by activity type if specified
                if activity_type and activity_dict.get("type") != activity_type:
                    continue
                
                processed_activities.append(activity_dict)
            except Exception as e:
                # If we can't process an individual activity, log and continue
                log_error(f"Error processing activity {i}: {str(e)}")
                # Add a placeholder error activity for debugging
                processed_activities.append({
                    "error": f"Failed to process activity: {str(e)}",
                    "type": "PROCESSING_ERROR",
                    "date": "UNKNOWN",
                    "raw_activity_type": getattr(activity, 'msg_type', 'UNKNOWN') if activity else 'NULL_ACTIVITY'
                })
                continue
        
        # Apply offset and limit
        start_index = offset
        end_index = offset + limit
        result = processed_activities[start_index:end_index]
        
        log_error(f"Returning {len(result)} activities after offset {offset} and limit {limit}")
        if result and len(result) > 0:
            log_error(f"First result type: {result[0].get('type')}, has error: {'error' in result[0]}")
        
        return result
    
    except Exception as e:
        return [handle_error(e, "get_recent_activity")]

def get_waiver_activity(league_id: int, limit: int = 25, year: Optional[int] = None,
                       session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get recent waiver wire activity specifically.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        limit: Maximum number of activities to return (default 25)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of waiver-related activity dictionaries
    """
    try:
        # Get all recent activities
        all_activities = get_recent_activity(league_id, limit=limit*2, year=year, session_id=session_id)
        
        # Filter for waiver-related activities
        waiver_types = ["ADD", "WAIVER_MOVED", "WAIVER_BUDGET_USED"]
        waiver_activities = []
        
        for activity in all_activities:
            if isinstance(activity, dict) and activity.get("type") in waiver_types:
                # Additionally check if the source indicates waivers
                if activity.get("source") in ["WAIVERS", "FA"] or "waiver" in activity.get("type", "").lower():
                    waiver_activities.append(activity)
        
        return waiver_activities[:limit]
    
    except Exception as e:
        return [handle_error(e, "get_waiver_activity")]

def get_trade_activity(league_id: int, limit: int = 25, year: Optional[int] = None,
                      session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get recent trade activity specifically.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        limit: Maximum number of activities to return (default 25)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of trade-related activity dictionaries
    """
    try:
        # Get all recent activities
        all_activities = get_recent_activity(league_id, limit=limit*2, year=year, session_id=session_id)
        
        # Filter for trade-related activities
        trade_types = ["TRADE_ACCEPTED", "TRADE_PENDING", "TRADE_DECLINED"]
        trade_activities = []
        
        for activity in all_activities:
            if isinstance(activity, dict) and activity.get("type") in trade_types:
                trade_activities.append(activity)
        
        return trade_activities[:limit]
    
    except Exception as e:
        return [handle_error(e, "get_trade_activity")]

def get_add_drop_activity(league_id: int, limit: int = 25, year: Optional[int] = None,
                         session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get recent add/drop activity specifically.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        limit: Maximum number of activities to return (default 25)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of add/drop activity dictionaries
    """
    try:
        # Get all recent activities
        all_activities = get_recent_activity(league_id, limit=limit*2, year=year, session_id=session_id)
        
        # Filter for add/drop activities
        add_drop_types = ["ADD", "DROP", "ROSTER_MOVE"]
        add_drop_activities = []
        
        for activity in all_activities:
            if isinstance(activity, dict) and activity.get("type") in add_drop_types:
                add_drop_activities.append(activity)
        
        return add_drop_activities[:limit]
    
    except Exception as e:
        return [handle_error(e, "get_add_drop_activity")]

def get_team_transactions(league_id: int, team_id: int, limit: int = 25, year: Optional[int] = None,
                         session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get recent transactions for a specific team.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        team_id: The team ID to filter transactions for
        limit: Maximum number of activities to return (default 25)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of activity dictionaries for the specified team
    """
    try:
        # Get all recent activities (fetch more to allow for filtering)
        all_activities = get_recent_activity(league_id, limit=limit*3, year=year, session_id=session_id)
        
        # Filter for activities involving the specified team
        team_activities = []
        
        for activity in all_activities:
            if isinstance(activity, dict) and "team" in activity:
                # Check if this activity involves the specified team
                if (activity["team"] and 
                    activity["team"].get("team_id") == team_id):
                    team_activities.append(activity)
                
                # For trades, also check the trade partner
                elif (activity.get("type") in ["TRADE_ACCEPTED", "TRADE_PENDING", "TRADE_DECLINED"] and
                      "trade_partner" in activity and
                      activity["trade_partner"] and
                      activity["trade_partner"].get("team_id") == team_id):
                    team_activities.append(activity)
        
        return team_activities[:limit]
    
    except Exception as e:
        return [handle_error(e, "get_team_transactions")]

def get_player_transaction_history(league_id: int, player_name: str, year: Optional[int] = None,
                                  session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get transaction history for a specific player.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        player_name: Name of the player to search for
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of activity dictionaries involving the specified player
    """
    try:
        # Get all recent activities (fetch more for comprehensive search)
        all_activities = get_recent_activity(league_id, limit=100, year=year, session_id=session_id)
        
        # Filter for activities involving the specified player
        player_activities = []
        
        for activity in all_activities:
            if isinstance(activity, dict):
                # Check if player is involved in the activity
                player_involved = False
                
                # Check added player
                if ("added_player" in activity and 
                    activity["added_player"] and
                    player_name.lower() in activity["added_player"].get("name", "").lower()):
                    player_involved = True
                
                # Check dropped player
                elif ("dropped_player" in activity and 
                      activity["dropped_player"] and
                      player_name.lower() in activity["dropped_player"].get("name", "").lower()):
                    player_involved = True
                
                # Check trade players
                elif activity.get("type") in ["TRADE_ACCEPTED", "TRADE_PENDING"]:
                    # Check players going to the team
                    if "players_in" in activity and activity["players_in"]:
                        for player in activity["players_in"]:
                            if player_name.lower() in player.get("name", "").lower():
                                player_involved = True
                                break
                    
                    # Check players leaving the team
                    if "players_out" in activity and activity["players_out"]:
                        for player in activity["players_out"]:
                            if player_name.lower() in player.get("name", "").lower():
                                player_involved = True
                                break
                
                if player_involved:
                    player_activities.append(activity)
        
        return player_activities
    
    except Exception as e:
        return [handle_error(e, "get_player_transaction_history")]

def get_lineup_activity(league_id: int, limit: int = 25, year: Optional[int] = None,
                       session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get recent lineup change activity specifically.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        limit: Maximum number of activities to return (default 25)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of lineup-related activity dictionaries
    """
    try:
        # Get all recent activities
        all_activities = get_recent_activity(league_id, limit=limit*2, year=year, session_id=session_id)
        
        # Filter for lineup-related activities
        lineup_types = ["LINEUP_SET", "ROSTER_MOVE"]
        lineup_activities = []
        
        for activity in all_activities:
            if isinstance(activity, dict) and activity.get("type") in lineup_types:
                lineup_activities.append(activity)
        
        return lineup_activities[:limit]
    
    except Exception as e:
        return [handle_error(e, "get_lineup_activity")]

def get_settings_activity(league_id: int, limit: int = 25, year: Optional[int] = None,
                         session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get recent league/team settings change activity.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        limit: Maximum number of activities to return (default 25)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of settings-related activity dictionaries
    """
    try:
        # Get all recent activities
        all_activities = get_recent_activity(league_id, limit=limit*2, year=year, session_id=session_id)
        
        # Filter for settings-related activities
        settings_types = ["LEAGUE_EDIT", "TEAM_EDIT"]
        settings_activities = []
        
        for activity in all_activities:
            if isinstance(activity, dict) and activity.get("type") in settings_types:
                settings_activities.append(activity)
        
        return settings_activities[:limit]
    
    except Exception as e:
        return [handle_error(e, "get_settings_activity")]

def get_keeper_activity(league_id: int, limit: int = 25, year: Optional[int] = None,
                       session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get recent keeper/dynasty league activity.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        limit: Maximum number of activities to return (default 25)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of keeper-related activity dictionaries
    """
    try:
        # Get all recent activities
        all_activities = get_recent_activity(league_id, limit=limit*2, year=year, session_id=session_id)
        
        # Filter for keeper-related activities
        keeper_types = ["KEEPER_SELECT"]
        keeper_activities = []
        
        for activity in all_activities:
            if isinstance(activity, dict) and activity.get("type") in keeper_types:
                keeper_activities.append(activity)
        
        return keeper_activities[:limit]
    
    except Exception as e:
        return [handle_error(e, "get_keeper_activity")]