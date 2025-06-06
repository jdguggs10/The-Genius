"""
Fix for the MLB standings endpoint to handle both dictionary and list return types.
This patch addresses the error: 'list' object has no attribute 'items'
"""
import logging
import json
from datetime import datetime
from pybaseball import standings

logger = logging.getLogger(__name__)

def get_standings(year: int = None, league: str = "all") -> str:
    """
    Get current MLB standings.
    
    Args:
        year: Season year (defaults to current)
        league: "AL", "NL", or "all"
        
    Returns:
        JSON string with standings
    """
    try:
        if year is None:
            year = datetime.now().year
            
        # Get standings
        standings_data = standings(year)
        result = {"year": year, "standings": {}}
        
        # Handle different return types from the pybaseball standings function
        if isinstance(standings_data, dict):
            # Process each division in dictionary format
            for division, df in standings_data.items():
                division_name = division.replace('_', ' ').title()
                
                teams = []
                for _, team in df.iterrows():
                    teams.append({
                        "team": team['Tm'],
                        "wins": int(team['W']),
                        "losses": int(team['L']),
                        "win_pct": round(float(team['W-L%']), 3),
                        "games_back": team.get('GB', '0')
                    })
                    
                result["standings"][division_name] = teams
        elif isinstance(standings_data, list):
            # Handle list format (this is likely what's causing the bug)
            # In this case, each item in the list is a dataframe for a division
            for i, df in enumerate(standings_data):
                # Try to determine division name from the dataframe
                # If division name can't be determined, use a generic name based on index
                division_name = f"Division {i+1}"
                
                teams = []
                for _, team in df.iterrows():
                    teams.append({
                        "team": team['Tm'],
                        "wins": int(team['W']),
                        "losses": int(team['L']),
                        "win_pct": round(float(team['W-L%']), 3),
                        "games_back": team.get('GB', '0')
                    })
                
                result["standings"][division_name] = teams
        else:
            # Handle unexpected return type
            return json.dumps({
                "error": f"Unexpected standings data type: {type(standings_data)}",
                "year": year
            })
            
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error fetching standings: {str(e)}")
        return json.dumps({
            "error": f"Error retrieving standings: {str(e)}",
            "year": year if year else datetime.now().year
        })
