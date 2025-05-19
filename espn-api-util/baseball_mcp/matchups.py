"""
Matchup and box score module for ESPN Fantasy Baseball MCP Server
Handles weekly matchups and detailed box score information
"""

from typing import Dict, Any, Optional, List
from utils import league_service, handle_error, boxscore_to_dict
from auth import auth_service

def get_week_matchups(league_id: int, week: Optional[int] = None, year: Optional[int] = None,
                     session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get high-level matchup results for a specific week.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        week: The week number (defaults to current week)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of matchups with basic score information
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Use current week if not specified
        if week is None:
            week = getattr(league, "current_week", getattr(league, "currentMatchupPeriod", 1))
        
        # Validate week number
        max_week = 25  # Baseball season typically spans about 25 weeks
        if hasattr(league.settings, "reg_season_count"):
            max_week = league.settings.reg_season_count
        
        if week < 1 or week > max_week:
            return [{"error": f"Invalid week number. Must be between 1 and {max_week}"}]
        
        # Get box scores for the week
        box_scores = league.box_scores(week)
        
        # Convert to simplified matchup format
        matchups = []
        for box_score in box_scores:
            matchup_info = {
                "week": week,
                "home_team": {
                    "team_id": getattr(box_score.home_team, "team_id", None),
                    "team_name": getattr(box_score.home_team, "team_name", "Unknown"),
                    "owner": getattr(box_score.home_team, "owner", "Unknown"),
                },
                "away_team": {
                    "team_id": getattr(box_score.away_team, "team_id", None),
                    "team_name": getattr(box_score.away_team, "team_name", "Unknown"),
                    "owner": getattr(box_score.away_team, "owner", "Unknown"),
                } if hasattr(box_score, "away_team") and box_score.away_team else None,
                "home_score": getattr(box_score, "home_score", 0),
                "away_score": getattr(box_score, "away_score", 0),
                "scoring_type": getattr(league.settings, "scoring_type", "UNKNOWN"),
            }
            
            # Determine winner
            if matchup_info["away_team"] is None:
                matchup_info["winner"] = "BYE"
                matchup_info["away_team"] = {"team_name": "BYE", "team_id": None, "owner": None}
            elif matchup_info["home_score"] > matchup_info["away_score"]:
                matchup_info["winner"] = "HOME"
            elif matchup_info["away_score"] > matchup_info["home_score"]:
                matchup_info["winner"] = "AWAY"
            else:
                matchup_info["winner"] = "TIE"
            
            # Add category breakdown for category leagues
            scoring_type = getattr(league.settings, "scoring_type", "").lower()
            if "category" in scoring_type:
                if hasattr(box_score, "home_stats") and hasattr(box_score, "away_stats"):
                    matchup_info["category_summary"] = _get_category_summary(box_score)
            
            matchups.append(matchup_info)
        
        return matchups
    
    except Exception as e:
        return [handle_error(e, "get_week_matchups")]

def get_matchup_boxscore(league_id: int, week: int, home_team_id: int, year: Optional[int] = None,
                        session_id: str = "default_session") -> Dict[str, Any]:
    """
    Get detailed box score breakdown for a specific matchup.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        week: The week number
        home_team_id: The ID of the home team (to identify the specific matchup)
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        Detailed box score with player-by-player breakdown
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Validate week number
        max_week = 25  # Baseball season typically spans about 25 weeks
        if hasattr(league.settings, "reg_season_count"):
            max_week = league.settings.reg_season_count
        
        if week < 1 or week > max_week:
            return {"error": f"Invalid week number. Must be between 1 and {max_week}"}
        
        # Get box scores for the week
        box_scores = league.box_scores(week)
        
        # Find the specific matchup by home team ID
        target_box_score = None
        for box_score in box_scores:
            if hasattr(box_score, "home_team") and box_score.home_team.team_id == home_team_id:
                target_box_score = box_score
                break
        
        if not target_box_score:
            return {"error": f"No matchup found for home team ID {home_team_id} in week {week}"}
        
        # Convert to detailed dictionary using the boxscore serializer
        detailed_boxscore = boxscore_to_dict(target_box_score)
        
        # Add additional analysis for category leagues
        scoring_type = getattr(league.settings, "scoring_type", "").lower()
        if "category" in scoring_type and hasattr(target_box_score, "home_stats"):
            detailed_boxscore["category_breakdown"] = _get_detailed_category_breakdown(target_box_score)
        
        # Add player performance analysis
        if "home_lineup" in detailed_boxscore and "away_lineup" in detailed_boxscore:
            detailed_boxscore["performance_analysis"] = _get_performance_analysis(
                detailed_boxscore["home_lineup"], 
                detailed_boxscore["away_lineup"],
                scoring_type
            )
        
        return detailed_boxscore
    
    except Exception as e:
        return handle_error(e, "get_matchup_boxscore")

def _get_category_summary(box_score: Any) -> Dict[str, Any]:
    """Helper function to summarize category performance"""
    from metadata import STATS_MAP
    
    category_summary = {
        "categories_won": {
            "home": 0,
            "away": 0,
            "tied": 0
        },
        "category_details": {}
    }
    
    if hasattr(box_score, "home_stats") and hasattr(box_score, "away_stats"):
        for stat_id, home_value in box_score.home_stats.items():
            stat_name = STATS_MAP.get(stat_id, f"stat_{stat_id}")
            away_value = box_score.away_stats.get(stat_id, 0)
            
            # Determine category winner (note: some stats like ERA and WHIP are better when lower)
            lower_is_better = stat_name.upper() in ["ERA", "WHIP"]
            
            if lower_is_better:
                if home_value < away_value:
                    winner = "home"
                elif away_value < home_value:
                    winner = "away"
                else:
                    winner = "tied"
            else:
                if home_value > away_value:
                    winner = "home"
                elif away_value > home_value:
                    winner = "away"
                else:
                    winner = "tied"
            
            category_summary["categories_won"][winner] += 1
            category_summary["category_details"][stat_name] = {
                "home_value": home_value,
                "away_value": away_value,
                "winner": winner
            }
    
    return category_summary

def _get_detailed_category_breakdown(box_score: Any) -> Dict[str, Any]:
    """Helper function to provide detailed category analysis"""
    from metadata import STATS_MAP
    
    breakdown = {
        "total_categories": 0,
        "home_wins": 0,
        "away_wins": 0,
        "ties": 0,
        "categories": {}
    }
    
    if hasattr(box_score, "home_stats") and hasattr(box_score, "away_stats"):
        for stat_id, home_value in box_score.home_stats.items():
            stat_name = STATS_MAP.get(stat_id, f"stat_{stat_id}")
            away_value = box_score.away_stats.get(stat_id, 0)
            
            # Determine category winner
            lower_is_better = stat_name.upper() in ["ERA", "WHIP"]
            
            if lower_is_better:
                if home_value < away_value:
                    winner = "home"
                    breakdown["home_wins"] += 1
                elif away_value < home_value:
                    winner = "away"
                    breakdown["away_wins"] += 1
                else:
                    winner = "tie"
                    breakdown["ties"] += 1
            else:
                if home_value > away_value:
                    winner = "home"
                    breakdown["home_wins"] += 1
                elif away_value > home_value:
                    winner = "away"
                    breakdown["away_wins"] += 1
                else:
                    winner = "tie"
                    breakdown["ties"] += 1
            
            breakdown["categories"][stat_name] = {
                "home_value": home_value,
                "away_value": away_value,
                "winner": winner,
                "lower_is_better": lower_is_better
            }
            
            breakdown["total_categories"] += 1
    
    return breakdown

def _get_performance_analysis(home_lineup: List[Dict[str, Any]], away_lineup: List[Dict[str, Any]], 
                            scoring_type: str) -> Dict[str, Any]:
    """Helper function to analyze player performance in the matchup"""
    
    analysis = {
        "top_performers": {
            "home": None,
            "away": None
        },
        "bench_analysis": {
            "home": {"active_points": 0, "bench_points": 0, "optimal_lineup": False},
            "away": {"active_points": 0, "bench_points": 0, "optimal_lineup": False}
        }
    }
    
    # Find top performers based on scoring type
    if "points" in scoring_type:
        # For points leagues, find highest scoring players
        home_top = max(home_lineup, key=lambda p: p.get("points", 0), default=None)
        away_top = max(away_lineup, key=lambda p: p.get("points", 0), default=None)
        
        if home_top:
            analysis["top_performers"]["home"] = {
                "player": home_top.get("player", {}).get("name", "Unknown"),
                "points": home_top.get("points", 0),
                "position": home_top.get("position", "Unknown")
            }
        
        if away_top:
            analysis["top_performers"]["away"] = {
                "player": away_top.get("player", {}).get("name", "Unknown"),
                "points": away_top.get("points", 0),
                "position": away_top.get("position", "Unknown")
            }
        
        # Analyze bench vs. active for points leagues
        for side, lineup in [("home", home_lineup), ("away", away_lineup)]:
            active_total = sum(p.get("points", 0) for p in lineup if p.get("position") not in ["BN", "IL", "BE"])
            bench_total = sum(p.get("points", 0) for p in lineup if p.get("position") in ["BN", "IL", "BE"])
            
            analysis["bench_analysis"][side]["active_points"] = active_total
            analysis["bench_analysis"][side]["bench_points"] = bench_total
            
            # Simple check: if any bench player scored more than lowest active player
            bench_players = [p for p in lineup if p.get("position") in ["BN", "IL", "BE"]]
            active_players = [p for p in lineup if p.get("position") not in ["BN", "IL", "BE"]]
            
            if bench_players and active_players:
                max_bench = max(p.get("points", 0) for p in bench_players)
                min_active = min(p.get("points", 0) for p in active_players)
                analysis["bench_analysis"][side]["optimal_lineup"] = max_bench <= min_active
            else:
                analysis["bench_analysis"][side]["optimal_lineup"] = True
    
    return analysis