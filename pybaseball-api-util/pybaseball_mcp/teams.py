"""
Team and league statistics module for PyBaseball MCP Server.
Handles league-wide stats, standings, and leaderboards.
"""
import pybaseball as pyb
from pybaseball import standings, batting_stats, pitching_stats
import pandas as pd
from datetime import datetime
import json
import logging

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
        
        # Process each division
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
            
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error fetching standings: {str(e)}")
        return f"Error retrieving standings: {str(e)}"


def get_league_leaders(stat: str, year: int = None, top_n: int = 10, player_type: str = "batting") -> str:
    """
    Get league leaders for a specific statistic.
    
    Args:
        stat: Statistic to rank by (e.g., "HR", "AVG", "ERA")
        year: Season year
        top_n: Number of top players to return
        player_type: "batting" or "pitching"
        
    Returns:
        JSON string with league leaders
    """
    try:
        if year is None:
            year = datetime.now().year
            
        # Map common stat names to actual column names
        stat_mapping = {
            # Batting stats
            "avg": "AVG", "average": "AVG", "batting_average": "AVG",
            "hr": "HR", "home_runs": "HR", "homers": "HR",
            "rbi": "RBI", "ribbies": "RBI",
            "runs": "R", "r": "R",
            "hits": "H", "h": "H",
            "sb": "SB", "stolen_bases": "SB", "steals": "SB",
            "obp": "OBP", "on_base": "OBP",
            "slg": "SLG", "slugging": "SLG",
            "ops": "OPS",
            "war": "WAR",
            # Pitching stats
            "era": "ERA", "earned_run_average": "ERA",
            "wins": "W", "w": "W",
            "strikeouts": "SO", "so": "SO", "ks": "SO",
            "whip": "WHIP",
            "saves": "SV", "sv": "SV",
            "k9": "K/9", "k_per_9": "K/9"
        }
        
        # Normalize stat name
        stat_column = stat_mapping.get(stat.lower(), stat.upper())
        
        # Determine if batting or pitching stat
        pitching_stats_list = ["ERA", "W", "L", "SV", "SO", "WHIP", "K/9", "BB/9", "IP"]
        is_pitching = stat_column in pitching_stats_list or player_type.lower() == "pitching"
        
        # Get appropriate stats
        if is_pitching:
            df = pitching_stats(year, qual=1)
            sort_ascending = stat_column in ["ERA", "WHIP", "BB/9"]  # Lower is better
        else:
            df = batting_stats(year, qual=1)
            sort_ascending = False  # Higher is better for batting stats
            
        # Check if stat exists
        if stat_column not in df.columns:
            available_stats = [col for col in df.columns if not col.startswith('ID')]
            return f"Stat '{stat}' not found. Available stats: {', '.join(available_stats[:20])}"
            
        # Sort and get top players
        df_sorted = df.sort_values(stat_column, ascending=sort_ascending).head(top_n)
        
        leaders = []
        for idx, (_, player) in enumerate(df_sorted.iterrows(), 1):
            leaders.append({
                "rank": idx,
                "name": player['Name'],
                "team": player.get('Team', 'Unknown'),
                stat_column: float(player[stat_column]) if pd.notna(player[stat_column]) else 0
            })
            
        return json.dumps({
            "stat": stat_column,
            "year": year,
            "type": "pitching" if is_pitching else "batting",
            "leaders": leaders
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error fetching league leaders: {str(e)}")
        return f"Error retrieving league leaders: {str(e)}"


def get_team_stats(team_name: str, year: int = None) -> str:
    """
    Get team aggregate statistics.
    
    Args:
        team_name: Team name or abbreviation
        year: Season year
        
    Returns:
        JSON string with team stats
    """
    try:
        if year is None:
            year = datetime.now().year
            
        # Get batting and pitching stats
        batting_df = batting_stats(year, qual=1)
        pitching_df = pitching_stats(year, qual=1)
        
        # Filter by team
        team_batting = batting_df[batting_df['Team'].str.contains(team_name, case=False, na=False)]
        team_pitching = pitching_df[pitching_df['Team'].str.contains(team_name, case=False, na=False)]
        
        if team_batting.empty and team_pitching.empty:
            return f"No stats found for team '{team_name}'"
            
        # Aggregate team stats
        result = {
            "team": team_name,
            "year": year,
            "batting": {
                "players": len(team_batting),
                "avg_avg": round(team_batting['AVG'].mean(), 3),
                "total_hr": int(team_batting['HR'].sum()),
                "total_rbi": int(team_batting['RBI'].sum()),
                "total_runs": int(team_batting['R'].sum()),
                "team_ops": round(team_batting['OPS'].mean(), 3)
            },
            "pitching": {
                "pitchers": len(team_pitching),
                "avg_era": round(team_pitching['ERA'].mean(), 2),
                "total_wins": int(team_pitching['W'].sum()),
                "total_saves": int(team_pitching['SV'].sum()),
                "total_strikeouts": int(team_pitching['SO'].sum())
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error fetching team stats: {str(e)}")
        return f"Error retrieving team stats: {str(e)}"