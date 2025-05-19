"""
Team roster and info module for ESPN Fantasy Baseball MCP Server
Handles team rosters, team info, and team schedules
"""

from typing import Dict, Any, Optional, List
from utils import league_service, handle_error, team_to_dict, player_to_dict
from auth import auth_service

def get_team_roster(league_id: int, team_id: int, year: Optional[int] = None,
                   session_id: str = "default_session") -> Dict[str, Any]:
    """
    Get a team's current roster with detailed player information.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        team_id: The team ID in the league (usually 1-N where N is number of teams)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        Dictionary containing team info and detailed roster
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Validate team ID
        if team_id < 1 or team_id > len(league.teams):
            return {"error": f"Invalid team_id. Must be between 1 and {len(league.teams)}"}
        
        # Get the team (team_id is 1-based, but list is 0-based)
        team = league.teams[team_id - 1]
        
        # Build roster information
        roster_info = {
            **team_to_dict(team),
            "roster": []
        }
        
        # Process each player in the roster
        for player in team.roster:
            player_info = player_to_dict(player)
            
            # Add lineup slot information if available
            if hasattr(player, "lineupSlot"):
                from metadata import POSITION_MAP
                player_info["lineup_slot"] = POSITION_MAP.get(player.lineupSlot, f"Slot_{player.lineupSlot}")
            
            roster_info["roster"].append(player_info)
        
        return roster_info
    
    except Exception as e:
        return handle_error(e, "get_team_roster")

def get_team_info(league_id: int, team_id: int, year: Optional[int] = None,
                 session_id: str = "default_session") -> Dict[str, Any]:
    """
    Get a team's general information including metadata and performance stats.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        team_id: The team ID in the league (usually 1-N where N is number of teams)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        Dictionary containing comprehensive team information
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Validate team ID
        if team_id < 1 or team_id > len(league.teams):
            return {"error": f"Invalid team_id. Must be between 1 and {len(league.teams)}"}
        
        # Get the team (team_id is 1-based, but list is 0-based)
        team = league.teams[team_id - 1]
        
        # Convert team to dictionary with all available information
        team_info = team_to_dict(team)
        
        # Add roster size information
        team_info["roster_size"] = len(team.roster) if hasattr(team, "roster") else 0
        
        # Add division information if available
        if hasattr(team, "division_id") and team.division_id is not None:
            team_info["division_id"] = team.division_id
            if hasattr(team, "division_name"):
                team_info["division_name"] = team.division_name
        
        # Add owner information if available (sometimes it's a list)
        if hasattr(team, "owners"):
            if isinstance(team.owners, list):
                team_info["owners"] = team.owners
            else:
                team_info["owners"] = [team.owners] if team.owners else []
        
        # Add playoff information if available
        if hasattr(team, "playoff_seed"):
            team_info["playoff_seed"] = team.playoff_seed
        if hasattr(team, "playoff_pct"):
            team_info["playoff_pct"] = team.playoff_pct
            
        # Add streak information if available
        if hasattr(team, "streak_type"):
            team_info["streak_type"] = team.streak_type
        if hasattr(team, "streak_length"):
            team_info["streak_length"] = team.streak_length
            
        return team_info
    
    except Exception as e:
        return handle_error(e, "get_team_info")

def get_team_schedule(league_id: int, team_id: int, year: Optional[int] = None,
                     session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get a team's schedule showing opponents and results for each week.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        team_id: The team ID in the league (usually 1-N where N is number of teams)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of matchups/schedule entries for the team
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Validate team ID
        if team_id < 1 or team_id > len(league.teams):
            return [{"error": f"Invalid team_id. Must be between 1 and {len(league.teams)}"}]
        
        # Get the team (team_id is 1-based, but list is 0-based)
        team = league.teams[team_id - 1]
        
        # Check if team has schedule attribute
        if hasattr(team, "schedule") and team.schedule:
            # If team.schedule exists, use it directly
            schedule = []
            for i, matchup in enumerate(team.schedule):
                matchup_info = {
                    "week": i + 1,
                    "opponent": None,
                    "home_score": None,
                    "away_score": None,
                    "winner": None,
                    "is_home": None,
                }
                
                # Determine if this team is home or away
                if hasattr(matchup, "home_team") and hasattr(matchup, "away_team"):
                    if matchup.home_team.team_id == team.team_id:
                        matchup_info["is_home"] = True
                        matchup_info["opponent"] = getattr(matchup.away_team, "team_name", "Unknown")
                    else:
                        matchup_info["is_home"] = False
                        matchup_info["opponent"] = getattr(matchup.home_team, "team_name", "Unknown")
                    
                    # Add scores if available
                    if hasattr(matchup, "home_score"):
                        matchup_info["home_score"] = matchup.home_score
                    if hasattr(matchup, "away_score"):
                        matchup_info["away_score"] = matchup.away_score
                        
                    # Determine winner
                    if matchup_info["home_score"] is not None and matchup_info["away_score"] is not None:
                        if matchup_info["home_score"] > matchup_info["away_score"]:
                            matchup_info["winner"] = "HOME"
                        elif matchup_info["away_score"] > matchup_info["home_score"]:
                            matchup_info["winner"] = "AWAY"
                        else:
                            matchup_info["winner"] = "TIE"
                
                schedule.append(matchup_info)
                
            return schedule
        
        else:
            # If team.schedule doesn't exist, build schedule from league box scores
            schedule = []
            
            # Try to get current week to determine how many weeks to check
            current_week = getattr(league, "current_week", getattr(league, "currentMatchupPeriod", 10))
            max_weeks = min(current_week + 5, 25)  # Check up to 25 weeks max (baseball season length)
            
            for week in range(1, max_weeks + 1):
                try:
                    # Get box scores for this week
                    box_scores = league.box_scores(week)
                    
                    # Find the matchup involving this team
                    team_matchup = None
                    for box_score in box_scores:
                        if (hasattr(box_score, "home_team") and box_score.home_team.team_id == team.team_id) or \
                           (hasattr(box_score, "away_team") and box_score.away_team and box_score.away_team.team_id == team.team_id):
                            team_matchup = box_score
                            break
                    
                    if team_matchup:
                        matchup_info = {
                            "week": week,
                            "opponent": None,
                            "home_score": getattr(team_matchup, "home_score", None),
                            "away_score": getattr(team_matchup, "away_score", None),
                            "winner": None,
                            "is_home": None,
                        }
                        
                        # Determine if this team is home or away
                        if team_matchup.home_team.team_id == team.team_id:
                            matchup_info["is_home"] = True
                            if hasattr(team_matchup, "away_team") and team_matchup.away_team:
                                matchup_info["opponent"] = getattr(team_matchup.away_team, "team_name", "Unknown")
                            else:
                                matchup_info["opponent"] = "BYE"
                        else:
                            matchup_info["is_home"] = False
                            matchup_info["opponent"] = getattr(team_matchup.home_team, "team_name", "Unknown")
                        
                        # Determine winner
                        if matchup_info["home_score"] is not None and matchup_info["away_score"] is not None:
                            if matchup_info["opponent"] == "BYE":
                                matchup_info["winner"] = "BYE"
                            elif matchup_info["home_score"] > matchup_info["away_score"]:
                                matchup_info["winner"] = "HOME"
                            elif matchup_info["away_score"] > matchup_info["home_score"]:
                                matchup_info["winner"] = "AWAY"
                            else:
                                matchup_info["winner"] = "TIE"
                        
                        schedule.append(matchup_info)
                
                except Exception:
                    # If we can't get a specific week, continue to next
                    continue
            
            return schedule
    
    except Exception as e:
        return [handle_error(e, "get_team_schedule")]