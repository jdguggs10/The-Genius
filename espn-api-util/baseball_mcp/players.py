"""
Player data and statistics module for ESPN Fantasy Baseball MCP Server
Handles player stats, free agents, and player queries
"""

from typing import Dict, Any, Optional, List
from utils import league_service, handle_error, player_to_dict
from auth import auth_service

def get_player_stats(league_id: int, player_name: str, year: Optional[int] = None,
                    session_id: str = "default_session") -> Dict[str, Any]:
    """
    Get detailed statistics for a specific player.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        player_name: Name of the player to search for
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        Dictionary containing player information and statistics
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Search for player in team rosters first
        player = None
        team_found = None
        
        for team in league.teams:
            for roster_player in team.roster:
                if player_name.lower() in roster_player.name.lower():
                    player = roster_player
                    team_found = team
                    break
            if player:
                break
        
        # If not found in rosters, search free agents
        if not player:
            try:
                free_agents = league.free_agents(size=200)  # Get a larger pool to search
                for fa_player in free_agents:
                    if player_name.lower() in fa_player.name.lower():
                        player = fa_player
                        break
            except Exception:
                pass  # If free agents search fails, continue with what we have
        
        if not player:
            return {"error": f"Player '{player_name}' not found in league {league_id}"}
        
        # Convert player to dictionary
        player_stats = player_to_dict(player)
        
        # Add team information if player is on a roster
        if team_found:
            player_stats["fantasy_team"] = {
                "team_id": getattr(team_found, "team_id", None),
                "team_name": getattr(team_found, "team_name", "Unknown"),
                "owner": getattr(team_found, "owner", "Unknown")
            }
        else:
            player_stats["fantasy_team"] = None
            player_stats["status"] = "FREE_AGENT"
        
        # Add weekly stats if available
        if hasattr(player, "stats") and player.stats:
            from metadata import STATS_MAP
            
            # Convert weekly/recent stats if available
            weekly_stats = {}
            season_stats = {}
            
            # ESPN API sometimes provides stats with different time periods
            for period, period_stats in player.stats.items():
                converted_stats = {}
                for stat_id, value in period_stats.items():
                    stat_name = STATS_MAP.get(stat_id, f"stat_{stat_id}")
                    converted_stats[stat_name] = value
                
                if "week" in str(period) or "recent" in str(period):
                    weekly_stats[str(period)] = converted_stats
                else:
                    season_stats[str(period)] = converted_stats
            
            if weekly_stats:
                player_stats["weekly_stats"] = weekly_stats
            if season_stats:
                player_stats["season_stats"] = season_stats
        
        # Add ownership information for free agents
        if hasattr(player, "percent_owned"):
            player_stats["ownership"] = {
                "percent_owned": player.percent_owned,
                "percent_started": getattr(player, "percent_started", None)
            }
        
        return player_stats
    
    except Exception as e:
        return handle_error(e, "get_player_stats")

def get_free_agents(league_id: int, week: Optional[int] = None, position: Optional[str] = None,
                   position_id: Optional[int] = None, limit: int = 50, year: Optional[int] = None,
                   session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get list of available free agents with filtering options.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        week: Week for which to get stats (defaults to current week)
        position: Position filter (e.g., "C", "1B", "OF", "SP", "RP")
        position_id: ESPN position ID filter (alternative to position name)
        limit: Maximum number of players to return (default 50)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of free agent player dictionaries
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Build free agents query parameters
        fa_params = {"size": min(limit, 100)}  # ESPN typically limits to 100
        
        if week is not None:
            fa_params["week"] = week
        
        # Handle position filtering
        if position_id is not None:
            fa_params["position_id"] = position_id
        elif position is not None:
            # Convert position name to position ID if needed
            from metadata import POSITION_MAP
            # Create reverse mapping
            position_name_to_id = {v: k for k, v in POSITION_MAP.items() if v == position}
            if position_name_to_id:
                fa_params["position_id"] = list(position_name_to_id.keys())[0]
            else:
                # If exact match not found, try to find by string matching
                fa_params["position"] = position
        
        # Get free agents from league
        try:
            free_agents = league.free_agents(**fa_params)
        except Exception:
            # If parameterized call fails, try with just size
            free_agents = league.free_agents(size=limit)
        
        # Process free agents
        processed_agents = []
        for player in free_agents:
            try:
                player_dict = player_to_dict(player)
                
                # Add additional free agent specific information
                player_dict["status"] = "FREE_AGENT"
                
                # Add fantasy relevance metrics if available
                if hasattr(player, "percent_owned"):
                    player_dict["ownership_info"] = {
                        "percent_owned": player.percent_owned,
                        "percent_started": getattr(player, "percent_started", None),
                        "percent_change": getattr(player, "percent_change", None)
                    }
                
                # Filter by position if specified and not filtered by API
                if position and not position_id:
                    eligible_positions = player_dict.get("eligible_positions", [])
                    if position not in eligible_positions:
                        continue
                
                processed_agents.append(player_dict)
                
                # Stop if we've reached the limit
                if len(processed_agents) >= limit:
                    break
                    
            except Exception as e:
                # If we can't process an individual player, log and continue
                from utils import log_error
                log_error(f"Error processing free agent: {str(e)}")
                continue
        
        return processed_agents
    
    except Exception as e:
        return [handle_error(e, "get_free_agents")]

def get_top_performers(league_id: int, position: Optional[str] = None, limit: int = 20,
                      metric: str = "points", year: Optional[int] = None,
                      session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get top performing players across all teams in the league.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        position: Position filter (e.g., "C", "1B", "OF", "SP", "RP")
        limit: Maximum number of players to return (default 20)
        metric: Metric to sort by ("points", "batting_average", "home_runs", "era", etc.)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of top performing player dictionaries
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Collect all players from all teams
        all_players = []
        for team in league.teams:
            for player in team.roster:
                player_dict = player_to_dict(player)
                player_dict["fantasy_team"] = {
                    "team_id": getattr(team, "team_id", None),
                    "team_name": getattr(team, "team_name", "Unknown"),
                    "owner": getattr(team, "owner", "Unknown")
                }
                all_players.append(player_dict)
        
        # Filter by position if specified
        if position:
            filtered_players = []
            for player in all_players:
                eligible_positions = player.get("eligible_positions", [])
                if position in eligible_positions or player.get("position") == position:
                    filtered_players.append(player)
            all_players = filtered_players
        
        # Sort by the specified metric
        def get_sort_value(player):
            if metric == "points":
                return player.get("total_points", 0)
            elif metric in player.get("stats", {}):
                return player["stats"].get(metric, 0)
            else:
                # Try common stat mappings
                stat_mappings = {
                    "batting_average": "AVG",
                    "home_runs": "HR",
                    "rbi": "RBI",
                    "stolen_bases": "SB",
                    "era": "ERA",
                    "whip": "WHIP",
                    "strikeouts": "K",
                    "wins": "W",
                    "saves": "SV"
                }
                mapped_stat = stat_mappings.get(metric.lower())
                if mapped_stat and mapped_stat in player.get("stats", {}):
                    # For ERA and WHIP, lower is better
                    value = player["stats"][mapped_stat]
                    if mapped_stat in ["ERA", "WHIP"]:
                        return -value if value > 0 else 0  # Negative for reverse sort
                    return value
                return 0
        
        # Sort players by the metric (descending for most stats)
        sorted_players = sorted(all_players, key=get_sort_value, reverse=True)
        
        # Return top performers
        return sorted_players[:limit]
    
    except Exception as e:
        return [handle_error(e, "get_top_performers")]

def search_players(league_id: int, search_term: str, include_rostered: bool = True,
                  include_free_agents: bool = True, year: Optional[int] = None,
                  session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Search for players by name across rosters and free agents.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        search_term: Partial or full player name to search for
        include_rostered: Whether to include players on team rosters
        include_free_agents: Whether to include free agents
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of matching player dictionaries
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        matching_players = []
        search_lower = search_term.lower()
        
        # Search rostered players
        if include_rostered:
            for team in league.teams:
                for player in team.roster:
                    if search_lower in player.name.lower():
                        player_dict = player_to_dict(player)
                        player_dict["status"] = "ROSTERED"
                        player_dict["fantasy_team"] = {
                            "team_id": getattr(team, "team_id", None),
                            "team_name": getattr(team, "team_name", "Unknown"),
                            "owner": getattr(team, "owner", "Unknown")
                        }
                        matching_players.append(player_dict)
        
        # Search free agents
        if include_free_agents:
            try:
                free_agents = league.free_agents(size=100)  # Get more for better search
                for player in free_agents:
                    if search_lower in player.name.lower():
                        player_dict = player_to_dict(player)
                        player_dict["status"] = "FREE_AGENT"
                        player_dict["fantasy_team"] = None
                        matching_players.append(player_dict)
            except Exception:
                pass  # If free agents search fails, continue with rostered players
        
        # Remove duplicates based on player name (in case player appears in both searches)
        seen_names = set()
        unique_players = []
        for player in matching_players:
            name = player.get("name", "")
            if name not in seen_names:
                seen_names.add(name)
                unique_players.append(player)
        
        # Sort by name for consistent ordering
        unique_players.sort(key=lambda p: p.get("name", ""))
        
        return unique_players
    
    except Exception as e:
        return [handle_error(e, "search_players")]

def get_waiver_claims(league_id: int, limit: int = 25, year: Optional[int] = None,
                     session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get recent waiver claims and FAAB bids information.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        limit: Maximum number of claims to return
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of waiver claim dictionaries
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Try to get waiver claims through different ESPN API methods
        waiver_claims = []
        
        # Method 1: Check if league has a waiver method
        if hasattr(league, 'waiver_claims'):
            try:
                claims = league.waiver_claims(limit=limit)
                for claim in claims:
                    try:
                        claim_dict = {
                            "type": "WAIVER_CLAIM",
                            "player": player_to_dict(claim.player) if hasattr(claim, 'player') else None,
                            "team": claim.team.team_name if hasattr(claim, 'team') else None,
                            "bid_amount": getattr(claim, 'bid_amount', None),
                            "priority": getattr(claim, 'priority', None),
                            "status": getattr(claim, 'status', 'UNKNOWN'),
                            "date": getattr(claim, 'date', None)
                        }
                        waiver_claims.append(claim_dict)
                    except Exception as e:
                        from utils import log_error
                        log_error(f"Error processing waiver claim: {str(e)}")
                        continue
            except Exception as e:
                from utils import log_error
                log_error(f"Error fetching waiver claims: {str(e)}")
        
        # Method 2: Fallback to activity filtering
        if not waiver_claims:
            from transactions import get_waiver_activity
            waiver_activities = get_waiver_activity(league_id, limit, year, session_id)
            
            for activity in waiver_activities:
                if activity.get("source") == "WAIVERS":
                    waiver_claims.append({
                        "type": "WAIVER_ACTIVITY",
                        "activity_type": activity.get("type"),
                        "player": activity.get("added_player"),
                        "team": activity.get("team", {}).get("team_name"),
                        "date": activity.get("date"),
                        "source": "ACTIVITY_LOG"
                    })
        
        return waiver_claims
    
    except Exception as e:
        return [handle_error(e, "get_waiver_claims")]