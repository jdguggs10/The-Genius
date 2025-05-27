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
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Get recent activity from the league
        activities = None
        fetch_size = min(limit + offset + 50, 100)  # ESPN API usually limits to 100
        
        try:
            # First, try fetching activities without the size parameter
            activities_no_size = league.recent_activity()
            
            # Check if a decent number of activities were returned
            if activities_no_size and len(activities_no_size) > 50: # Threshold of 50
                activities = activities_no_size
            else:
                # If few or no activities returned, try with fetch_size
                try:
                    activities_with_size = league.recent_activity(size=fetch_size)
                    activities = activities_with_size
                except Exception as e_size:
                    from utils import log_error
                    log_error(f"Error calling league.recent_activity(size={fetch_size}): {str(e_size)}")
                    # If the call with size fails, and the initial call returned some (but few) activities, use those.
                    # If initial call also returned None or empty, activities will remain None.
                    if activities_no_size is not None: # Check if activities_no_size had content
                        activities = activities_no_size
                    else: # Both calls essentially failed to return data
                        activities = [] # Ensure activities is an empty list not None
                        
        except Exception as e_no_size:
            from utils import log_error
            log_error(f"Error calling league.recent_activity() (no size): {str(e_no_size)}")
            # If the first call (no size) fails, try the call with fetch_size
            try:
                activities = league.recent_activity(size=fetch_size)
            except Exception as e_size_after_fail:
                log_error(f"Error calling league.recent_activity(size={fetch_size}) after initial fail: {str(e_size_after_fail)}")
                # If both calls fail, activities will be None or what was assigned before second try block
                # We want to ensure it's an empty list to avoid issues downstream before the main error handling
                activities = []

        # If after all attempts, activities is still None or empty, it will be handled by the main try-except
        # or by subsequent checks. For safety, ensure it's a list.
        if activities is None:
            activities = []

        # Process and filter activities
        processed_activities = []
        for activity in activities:
            try:
                # Convert activity to dictionary
                activity_dict = activity_to_dict(activity)
                
                # Filter by activity type if specified
                if activity_type and activity_dict.get("type") != activity_type:
                    continue
                
                processed_activities.append(activity_dict)
            except Exception as e:
                # If we can't process an individual activity, log and continue
                from utils import log_error
                log_error(f"Error processing activity: {str(e)}")
                continue
        
        # Apply offset and limit
        start_index = offset
        end_index = offset + limit
        return processed_activities[start_index:end_index]
    
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
        add_drop_types = ["ADD", "DROP"]
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