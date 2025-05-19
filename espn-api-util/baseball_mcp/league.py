"""
League-level data access for ESPN Fantasy Baseball MCP Server
Handles league info, settings, standings, and scoreboard
"""

from typing import Dict, Any, Optional, List
from utils import league_service, handle_error, team_to_dict, boxscore_to_dict
from auth import auth_service

def get_league_info(league_id: int, year: Optional[int] = None, 
                   session_id: str = "default_session") -> Dict[str, Any]:
    """
    Get basic information about a fantasy baseball league.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        Dictionary containing league name, year, current_week, team_count, teams, scoring_type
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Extract basic info
        info = {
            "league_id": league_id,
            "name": getattr(league.settings, "name", f"League {league_id}"),
            "year": league.year,
            "current_week": getattr(league, "current_week", getattr(league, "currentMatchupPeriod", 1)),
            "team_count": len(league.teams),
            "teams": [getattr(team, "team_name", f"Team {i+1}") for i, team in enumerate(league.teams)],
            "scoring_type": getattr(league.settings, "scoring_type", "UNKNOWN"),
            "is_public": getattr(league.settings, "is_public", False),
        }
        
        # Add additional league settings if available
        if hasattr(league.settings, "trade_deadline"):
            info["trade_deadline"] = league.settings.trade_deadline
        
        if hasattr(league.settings, "playoff_team_count"):
            info["playoff_team_count"] = league.settings.playoff_team_count
            
        if hasattr(league.settings, "reg_season_count"):
            info["regular_season_weeks"] = league.settings.reg_season_count
        
        return info
    
    except Exception as e:
        return handle_error(e, "get_league_info")

def get_league_settings(league_id: int, year: Optional[int] = None,
                       session_id: str = "default_session") -> Dict[str, Any]:
    """
    Get detailed league settings and configuration.
    
    Args:
        league_id: The ESPN fantasy baseball league ID  
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        Dictionary containing detailed league settings
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        settings = league.settings
        
        # Extract settings information
        settings_info = {
            "league_name": getattr(settings, "name", f"League {league_id}"),
            "scoring_type": getattr(settings, "scoring_type", "UNKNOWN"),
            "num_teams": len(league.teams),
            "is_public": getattr(settings, "is_public", False),
            "draft_type": getattr(settings, "draft_type", "UNKNOWN"),
        }
        
        # Add roster settings
        if hasattr(settings, "roster_slots"):
            settings_info["roster_slots"] = settings.roster_slots
            
        # Add stat categories for category leagues
        if hasattr(settings, "stat_categories"):
            settings_info["stat_categories"] = settings.stat_categories
            
        # Add scoring settings 
        if hasattr(settings, "scoring_settings"):
            settings_info["scoring_settings"] = settings.scoring_settings
            
        # Add playoff settings
        playoff_info = {}
        if hasattr(settings, "playoff_team_count"):
            playoff_info["playoff_team_count"] = settings.playoff_team_count
        if hasattr(settings, "playoff_start_week"):
            playoff_info["playoff_start_week"] = settings.playoff_start_week
        if hasattr(settings, "playoff_seed_tie_rule"):
            playoff_info["playoff_seed_tie_rule"] = settings.playoff_seed_tie_rule
        
        if playoff_info:
            settings_info["playoff_settings"] = playoff_info
            
        # Add waiver settings
        if hasattr(settings, "waiver_period"):
            settings_info["waiver_period"] = settings.waiver_period
        if hasattr(settings, "faab_budget"):
            settings_info["faab_budget"] = settings.faab_budget
            
        # Add trade settings
        if hasattr(settings, "trade_deadline"):
            settings_info["trade_deadline"] = settings.trade_deadline
        if hasattr(settings, "trade_veto_period"):
            settings_info["trade_veto_period"] = settings.trade_veto_period
            
        # Add schedule settings  
        if hasattr(settings, "reg_season_count"):
            settings_info["regular_season_length"] = settings.reg_season_count
        if hasattr(settings, "matchup_periods"):
            settings_info["matchup_periods"] = settings.matchup_periods
            
        return settings_info
    
    except Exception as e:
        return handle_error(e, "get_league_settings")

def get_league_standings(league_id: int, year: Optional[int] = None,
                        session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get current standings for a league, ordered by ranking.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of teams ordered by standing with their records and stats
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Check scoring type to determine sorting
        scoring_type = getattr(league.settings, "scoring_type", "").lower()
        is_roto = "roto" in scoring_type
        
        # Sort teams based on scoring type
        if is_roto:
            # For rotisserie leagues, sort by roto_points if available
            sorted_teams = sorted(league.teams, 
                                key=lambda x: getattr(x, "roto_points", getattr(x, "points_for", 0)),
                                reverse=True)
        else:
            # For head-to-head leagues, sort by wins then points
            sorted_teams = sorted(league.teams, 
                                key=lambda x: (getattr(x, "wins", 0), getattr(x, "points_for", 0)),
                                reverse=True)
        
        # Build standings list
        standings = []
        for i, team in enumerate(sorted_teams):
            team_standing = {
                "rank": i + 1,
                **team_to_dict(team)
            }
            
            # For rotisserie leagues, include roto_points if available
            if is_roto and hasattr(team, "roto_points"):
                team_standing["roto_points"] = team.roto_points
                
            standings.append(team_standing)
        
        return standings
    
    except Exception as e:
        return handle_error(e, "get_league_standings")

def get_league_scoreboard(league_id: int, matchup_period: Optional[int] = None,
                         session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get scoreboard/matchups overview for a given week.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        matchup_period: The week/period number (defaults to current week)
        session_id: Session identifier for authentication
    
    Returns:
        List of matchups with basic score information (not detailed box scores)
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year=None, espn_s2=espn_s2, swid=swid)
        
        # Use current week if not specified
        if matchup_period is None:
            matchup_period = getattr(league, "current_week", getattr(league, "currentMatchupPeriod", 1))
        
        # Get matchups for the specified period
        try:
            # Try to use scoreboard method if available
            if hasattr(league, "scoreboard"):
                matchups = league.scoreboard(matchup_period)
            else:
                # Fall back to box_scores method
                matchups = league.box_scores(matchup_period)
        except Exception:
            # If specific week fails, try box_scores method with current week
            matchups = league.box_scores()
        
        # Convert matchups to simplified format (not full box scores)
        scoreboard = []
        for matchup in matchups:
            matchup_info = {
                "matchup_period": matchup_period,
                "home_team": {
                    "team_id": getattr(matchup.home_team, "team_id", None),
                    "team_name": getattr(matchup.home_team, "team_name", "Unknown"),
                    "wins": getattr(matchup.home_team, "wins", 0),
                    "losses": getattr(matchup.home_team, "losses", 0),
                },
                "away_team": {
                    "team_id": getattr(matchup.away_team, "team_id", None),
                    "team_name": getattr(matchup.away_team, "team_name", "Unknown"),
                    "wins": getattr(matchup.away_team, "wins", 0),
                    "losses": getattr(matchup.away_team, "losses", 0),
                } if hasattr(matchup, "away_team") and matchup.away_team else None,
                "home_score": getattr(matchup, "home_score", 0),
                "away_score": getattr(matchup, "away_score", 0),
            }
            
            # Determine winner
            if matchup_info["away_team"] is None:
                matchup_info["winner"] = "BYE"
            elif matchup_info["home_score"] > matchup_info["away_score"]:
                matchup_info["winner"] = "HOME"
            elif matchup_info["away_score"] > matchup_info["home_score"]:
                matchup_info["winner"] = "AWAY"
            else:
                matchup_info["winner"] = "TIE"
            
            scoreboard.append(matchup_info)
        
        return scoreboard
    
    except Exception as e:
        return handle_error(e, "get_league_scoreboard")