"""
Player statistics module for PyBaseball MCP Server.
Handles fetching individual player stats from MLB data.
"""
import pybaseball as pyb
from pybaseball import playerid_lookup, batting_stats, pitching_stats, statcast_batter, statcast_pitcher
import pandas as pd
from datetime import datetime, timedelta
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Cache configuration
pyb.cache.enable()

def get_player_stats(player_name: str, year: int = None) -> str:
    """
    Get season statistics for a specific player.
    
    Args:
        player_name: Full name of the player (e.g., "Shohei Ohtani")
        year: Season year (defaults to current year)
    
    Returns:
        JSON string with player stats or error message
    """
    try:
        # Default to current year if not specified
        if year is None:
            year = datetime.now().year
            
        # Split name into first and last
        name_parts = player_name.strip().split()
        if len(name_parts) < 2:
            return f"Error: Please provide both first and last name for '{player_name}'"
            
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])  # Handle names like "De La Cruz"
        
        # Look up player ID
        logger.info(f"Looking up player: {first_name} {last_name}")
        player_lookup = playerid_lookup(last_name, first_name)
        
        if player_lookup.empty:
            return f"Player '{player_name}' not found in database"
            
        # Get the most recent player entry (in case of multiple matches)
        player_info = player_lookup.iloc[0]
        player_id = int(player_info['key_mlbam'])
        
        # Try batting stats first
        try:
            batting_df = batting_stats(year, qual=1)
            player_batting = batting_df[batting_df['IDfg'] == player_info['key_fangraphs']]
            
            if not player_batting.empty:
                stats = player_batting.iloc[0]
                return json.dumps({
                    "player": player_name,
                    "year": year,
                    "type": "batting",
                    "games": int(stats.get('G', 0)),
                    "avg": round(float(stats.get('AVG', 0)), 3),
                    "obp": round(float(stats.get('OBP', 0)), 3),
                    "slg": round(float(stats.get('SLG', 0)), 3),
                    "ops": round(float(stats.get('OPS', 0)), 3),
                    "hr": int(stats.get('HR', 0)),
                    "rbi": int(stats.get('RBI', 0)),
                    "runs": int(stats.get('R', 0)),
                    "sb": int(stats.get('SB', 0)),
                    "war": round(float(stats.get('WAR', 0)), 1)
                }, indent=2)
        except Exception as e:
            logger.debug(f"No batting stats found: {e}")
            
        # Try pitching stats if no batting stats found
        try:
            pitching_df = pitching_stats(year, qual=1)
            player_pitching = pitching_df[pitching_df['IDfg'] == player_info['key_fangraphs']]
            
            if not player_pitching.empty:
                stats = player_pitching.iloc[0]
                return json.dumps({
                    "player": player_name,
                    "year": year,
                    "type": "pitching",
                    "games": int(stats.get('G', 0)),
                    "games_started": int(stats.get('GS', 0)),
                    "wins": int(stats.get('W', 0)),
                    "losses": int(stats.get('L', 0)),
                    "saves": int(stats.get('SV', 0)),
                    "era": round(float(stats.get('ERA', 0)), 2),
                    "whip": round(float(stats.get('WHIP', 0)), 3),
                    "ip": round(float(stats.get('IP', 0)), 1),
                    "so": int(stats.get('SO', 0)),
                    "k9": round(float(stats.get('K/9', 0)), 1),
                    "war": round(float(stats.get('WAR', 0)), 1)
                }, indent=2)
        except Exception as e:
            logger.debug(f"No pitching stats found: {e}")
            
        return f"No stats found for {player_name} in {year}"
        
    except Exception as e:
        logger.error(f"Error fetching stats for {player_name}: {str(e)}")
        return f"Error retrieving stats: {str(e)}"


def get_player_recent_stats(player_name: str, days: int = 30) -> str:
    """
    Get recent game statistics for a player.
    
    Args:
        player_name: Full name of the player
        days: Number of days to look back (default 30)
    
    Returns:
        JSON string with recent stats summary
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Split name
        name_parts = player_name.strip().split()
        if len(name_parts) < 2:
            return f"Error: Please provide both first and last name"
            
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])
        
        # Look up player
        player_lookup = playerid_lookup(last_name, first_name)
        if player_lookup.empty:
            return f"Player '{player_name}' not found"
            
        player_info = player_lookup.iloc[0]
        player_id = int(player_info['key_mlbam'])
        
        # Get statcast data for recent games
        try:
            # Try as a batter first
            recent_data = statcast_batter(
                start_dt=start_date.strftime('%Y-%m-%d'),
                end_dt=end_date.strftime('%Y-%m-%d'),
                player_id=player_id
            )
            
            if not recent_data.empty:
                # Calculate batting stats
                hits = len(recent_data[recent_data['events'].isin(['single', 'double', 'triple', 'home_run'])])
                at_bats = len(recent_data[recent_data['events'].notna()])
                avg = round(hits / at_bats, 3) if at_bats > 0 else 0
                
                home_runs = len(recent_data[recent_data['events'] == 'home_run'])
                
                return json.dumps({
                    "player": player_name,
                    "period": f"Last {days} days",
                    "type": "batting",
                    "at_bats": at_bats,
                    "hits": hits,
                    "avg": avg,
                    "home_runs": home_runs,
                    "max_exit_velocity": round(recent_data['launch_speed'].max(), 1) if 'launch_speed' in recent_data else None,
                    "avg_exit_velocity": round(recent_data['launch_speed'].mean(), 1) if 'launch_speed' in recent_data else None
                }, indent=2)
                
        except:
            # Try as pitcher
            recent_data = statcast_pitcher(
                start_dt=start_date.strftime('%Y-%m-%d'),
                end_dt=end_date.strftime('%Y-%m-%d'),
                player_id=player_id
            )
            
            if not recent_data.empty:
                # Calculate pitching stats
                return json.dumps({
                    "player": player_name,
                    "period": f"Last {days} days",
                    "type": "pitching",
                    "pitches_thrown": len(recent_data),
                    "avg_velocity": round(recent_data['release_speed'].mean(), 1) if 'release_speed' in recent_data else None,
                    "max_velocity": round(recent_data['release_speed'].max(), 1) if 'release_speed' in recent_data else None,
                    "strike_percentage": round(len(recent_data[recent_data['type'] == 'S']) / len(recent_data) * 100, 1) if len(recent_data) > 0 else 0
                }, indent=2)
                
        return f"No recent data found for {player_name}"
        
    except Exception as e:
        logger.error(f"Error fetching recent stats: {str(e)}")
        return f"Error retrieving recent stats: {str(e)}"


def search_player(search_term: str) -> str:
    """
    Search for players by partial name match.
    
    Args:
        search_term: Partial name to search for
        
    Returns:
        JSON string with list of matching players
    """
    try:
        # Try to find players with the search term
        # PyBaseball doesn't have a direct search, so we'll be creative
        results = []
        
        # Search in recent batting stats
        current_year = datetime.now().year
        batting_df = batting_stats(current_year, qual=1)
        
        # Search for matches in player names
        matches = batting_df[batting_df['Name'].str.contains(search_term, case=False, na=False)]
        
        for _, player in matches.head(10).iterrows():
            results.append({
                "name": player['Name'],
                "team": player.get('Team', 'Unknown'),
                "position": "Batter",
                "stats_available": True
            })
            
        return json.dumps({
            "search_term": search_term,
            "results": results,
            "count": len(results)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error searching for players: {str(e)}")
        return f"Error searching: {str(e)}"