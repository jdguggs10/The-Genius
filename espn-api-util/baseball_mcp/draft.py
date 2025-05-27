"""
Draft results module for ESPN Fantasy Baseball MCP Server
Handles draft picks, draft order, and draft analysis
"""

from typing import Dict, Any, Optional, List
from utils import league_service, handle_error, pick_to_dict, team_to_dict, player_to_dict
from auth import auth_service

def get_draft_results(league_id: int, year: Optional[int] = None,
                     session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get complete draft results for the league.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of draft picks in order with team, player, and pick information
    """
    try:
        # Get credentials for this session
        credentials = auth_service.get_credentials(session_id)
        espn_s2 = credentials.get('espn_s2') if credentials else None
        swid = credentials.get('swid') if credentials else None
        
        # Get league instance
        league = league_service.get_league(league_id, year, espn_s2, swid)
        
        # Check if draft data is available
        if not hasattr(league, "draft") or not league.draft:
            return [{"error": "Draft data not available for this league/year"}]
        
        # Process each draft pick
        draft_picks = []
        for pick in league.draft:
            try:
                pick_dict = pick_to_dict(pick)
                draft_picks.append(pick_dict)
            except Exception as e:
                # If we can't process an individual pick, log and continue
                from utils import log_error
                log_error(f"Error processing draft pick: {str(e)}")
                continue
        
        # Sort by overall pick number to ensure correct order with null safety
        draft_picks.sort(key=lambda p: p.get("overall_pick", 0) or 0)
        
        return draft_picks
    
    except Exception as e:
        return [handle_error(e, "get_draft_results")]

def get_draft_by_round(league_id: int, round_num: int, year: Optional[int] = None,
                      session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get draft picks for a specific round.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        round_num: The round number to retrieve
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of draft picks for the specified round
    """
    try:
        # Get all draft results
        all_picks = get_draft_results(league_id, year, session_id)
        
        # Filter for the specified round
        round_picks = []
        for pick in all_picks:
            if isinstance(pick, dict) and pick.get("round_num") == round_num:
                round_picks.append(pick)
        
        # Sort by pick number within the round with null safety
        round_picks.sort(key=lambda p: p.get("round_pick", 0) or 0)
        
        return round_picks
    
    except Exception as e:
        return [handle_error(e, "get_draft_by_round")]

def get_team_draft_picks(league_id: int, team_id: int, year: Optional[int] = None,
                        session_id: str = "default_session") -> List[Dict[str, Any]]:
    """
    Get all draft picks for a specific team.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        team_id: The team ID to get draft picks for
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        List of draft picks made by the specified team
    """
    try:
        # Get all draft results
        all_picks = get_draft_results(league_id, year, session_id)
        
        # Filter for the specified team
        team_picks = []
        for pick in all_picks:
            if (isinstance(pick, dict) and 
                "team" in pick and 
                pick["team"] and 
                pick["team"].get("team_id") == team_id):
                team_picks.append(pick)
        
        # Sort by overall pick number with null safety
        team_picks.sort(key=lambda p: p.get("overall_pick", 0) or 0)
        
        return team_picks
    
    except Exception as e:
        return [handle_error(e, "get_team_draft_picks")]

def get_draft_analysis(league_id: int, year: Optional[int] = None,
                      session_id: str = "default_session") -> Dict[str, Any]:
    """
    Get analysis of the draft including statistics and insights.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        Dictionary containing draft analysis and statistics
    """
    try:
        # Get all draft results
        all_picks = get_draft_results(league_id, year, session_id)
        
        if not all_picks or (len(all_picks) == 1 and "error" in all_picks[0]):
            return {"error": "Cannot analyze draft - no draft data available"}
        
        # Initialize analysis structure
        analysis = {
            "total_picks": len(all_picks),
            "total_rounds": 0,
            "draft_type": "UNKNOWN",
            "position_breakdown": {},
            "team_analysis": {},
            "auction_analysis": None,
            "keeper_analysis": None
        }
        
        # Analyze draft structure
        rounds = set()
        total_auction_spent = 0
        auction_picks = 0
        keeper_count = 0
        
        # Position tracking
        position_counts = {}
        
        # Team analysis tracking
        team_stats = {}
        
        for pick in all_picks:
            if not isinstance(pick, dict):
                continue
                
            # Track rounds
            if "round_num" in pick and pick["round_num"]:
                rounds.add(pick["round_num"])
            
            # Track auction prices
            if "auction_price" in pick and pick["auction_price"] is not None:
                total_auction_spent += pick["auction_price"]
                auction_picks += 1
            
            # Track keepers
            if pick.get("keeper", False):
                keeper_count += 1
            
            # Analyze by position
            if "player" in pick and pick["player"]:
                player_position = pick["player"].get("position", "UNKNOWN")
                position_counts[player_position] = position_counts.get(player_position, 0) + 1
            
            # Analyze by team
            if "team" in pick and pick["team"]:
                team_id = pick["team"].get("team_id")
                team_name = pick["team"].get("team_name", f"Team {team_id}")
                
                if team_id not in team_stats:
                    team_stats[team_id] = {
                        "team_name": team_name,
                        "total_picks": 0,
                        "auction_spent": 0,
                        "keepers": 0,
                        "positions_drafted": {}
                    }
                
                team_stats[team_id]["total_picks"] += 1
                if "auction_price" in pick and pick["auction_price"] is not None:
                    team_stats[team_id]["auction_spent"] += pick["auction_price"]
                if pick.get("keeper", False):
                    team_stats[team_id]["keepers"] += 1
                
                # Track positions by team
                if "player" in pick and pick["player"]:
                    player_position = pick["player"].get("position", "UNKNOWN")
                    team_positions = team_stats[team_id]["positions_drafted"]
                    team_positions[player_position] = team_positions.get(player_position, 0) + 1
        
        # Set analysis results
        analysis["total_rounds"] = len(rounds) if rounds else 0
        analysis["position_breakdown"] = position_counts
        analysis["team_analysis"] = team_stats
        
        # Determine draft type
        if auction_picks > 0:
            analysis["draft_type"] = "AUCTION" if auction_picks == len(all_picks) else "HYBRID"
            analysis["auction_analysis"] = {
                "total_spent": total_auction_spent,
                "average_price": total_auction_spent / auction_picks if auction_picks > 0 else 0,
                "auction_picks": auction_picks
            }
        else:
            analysis["draft_type"] = "SNAKE"
        
        # Keeper analysis
        if keeper_count > 0:
            analysis["keeper_analysis"] = {
                "total_keepers": keeper_count,
                "keeper_percentage": (keeper_count / len(all_picks)) * 100 if all_picks else 0
            }
        
        return analysis
    
    except Exception as e:
        return handle_error(e, "get_draft_analysis")

def get_position_scarcity_analysis(league_id: int, year: Optional[int] = None,
                                  session_id: str = "default_session") -> Dict[str, Any]:
    """
    Analyze position scarcity based on draft patterns.
    
    Args:
        league_id: The ESPN fantasy baseball league ID
        year: Optional year for historical data (defaults to current season)
        session_id: Session identifier for authentication
    
    Returns:
        Dictionary containing position scarcity analysis
    """
    try:
        # Get all draft results
        all_picks = get_draft_results(league_id, year, session_id)
        
        if not all_picks or (len(all_picks) == 1 and "error" in all_picks[0]):
            return {"error": "Cannot analyze position scarcity - no draft data available"}
        
        # Group picks by position and analyze when they were drafted
        position_picks = {}
        
        for pick in all_picks:
            if not isinstance(pick, dict) or "player" not in pick or not pick["player"]:
                continue
            
            player_position = pick["player"].get("position", "UNKNOWN")
            overall_pick = pick.get("overall_pick", 0)
            round_num = pick.get("round_num", 0)
            
            if player_position not in position_picks:
                position_picks[player_position] = []
            
            position_picks[player_position].append({
                "overall_pick": overall_pick,
                "round_num": round_num,
                "player_name": pick["player"].get("name", "Unknown")
            })
        
        # Analyze scarcity for each position
        scarcity_analysis = {}
        
        for position, picks in position_picks.items():
            if not picks:
                continue
            
            # Sort by overall pick with null safety
            picks.sort(key=lambda p: p.get("overall_pick", 0) or 0)
            
            # Calculate scarcity metrics
            total_drafted = len(picks)
            first_pick = picks[0]["overall_pick"] if picks else 0
            last_pick = picks[-1]["overall_pick"] if picks else 0
            
            # Calculate average draft position
            avg_draft_position = sum(p["overall_pick"] for p in picks) / total_drafted if total_drafted > 0 else 0
            
            # Determine scarcity level
            scarcity_level = "LOW"
            if first_pick <= 50:  # First player taken in early rounds
                if total_drafted <= 20:
                    scarcity_level = "HIGH"
                elif total_drafted <= 40:
                    scarcity_level = "MEDIUM"
            elif first_pick <= 100:
                if total_drafted <= 15:
                    scarcity_level = "MEDIUM"
            
            scarcity_analysis[position] = {
                "total_drafted": total_drafted,
                "first_picked": first_pick,
                "last_picked": last_pick,
                "avg_draft_position": round(avg_draft_position, 1),
                "scarcity_level": scarcity_level,
                "early_picks": [p for p in picks if p["overall_pick"] <= 50],
                "late_picks": [p for p in picks if p["overall_pick"] > 150]
            }
        
        # Sort positions by scarcity (first pick and total drafted)
        sorted_positions = sorted(
            scarcity_analysis.items(),
            key=lambda x: (x[1]["first_picked"], -x[1]["total_drafted"])
        )
        
        return {
            "position_scarcity": dict(sorted_positions),
            "scarcest_positions": [pos for pos, data in sorted_positions[:3]],
            "most_available_positions": [pos for pos, data in sorted_positions[-3:] if data["total_drafted"] > 5]
        }
    
    except Exception as e:
        return handle_error(e, "get_position_scarcity_analysis")