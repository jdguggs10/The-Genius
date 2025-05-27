"""
Utility functions for PyBaseball MCP Server.
Includes caching, formatting, and helper functions.
"""
import json
from datetime import datetime, timedelta
from functools import lru_cache
import logging
import pybaseball as pyb
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Simple in-memory cache with TTL
_cache = {}
_cache_timestamps = {}
CACHE_TTL_SECONDS = 300  # 5 minutes

def setup_cache():
    """Configure PyBaseball cache for better performance."""
    # Enable caching
    pyb.cache.enable()
    
    # Set cache directory to a specific location
    cache_dir = Path.home() / ".pybaseball" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure cache settings if available
    try:
        # Set cache expiry to 1 day for better performance
        pyb.cache.config.cache_expiry = 86400  # 24 hours in seconds
        logger.info(f"PyBaseball cache configured at: {cache_dir}")
    except AttributeError:
        # Older versions might not have these settings
        logger.info("PyBaseball cache enabled with default settings")

def clear_cache():
    """Clear the PyBaseball cache."""
    try:
        pyb.cache.purge()
        logger.info("PyBaseball cache cleared")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise

def get_cache_info():
    """Get information about the cache status."""
    try:
        enabled = pyb.cache.is_enabled()
        return {
            "enabled": enabled,
            "cache_directory": str(pyb.cache.config.cache_directory) if hasattr(pyb.cache.config, 'cache_directory') else "Default",
        }
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        return {"enabled": False, "error": str(e)}

def get_cached_result(key: str):
    """Get cached result if still valid."""
    if key in _cache and key in _cache_timestamps:
        if datetime.now() - _cache_timestamps[key] < timedelta(seconds=CACHE_TTL_SECONDS):
            logger.debug(f"Cache hit for key: {key}")
            return _cache[key]
    return None

def set_cached_result(key: str, value: any):
    """Store result in cache."""
    _cache[key] = value
    _cache_timestamps[key] = datetime.now()
    logger.debug(f"Cached result for key: {key}")

def format_error(error_msg: str) -> str:
    """Format error messages consistently."""
    return json.dumps({
        "error": True,
        "message": error_msg,
        "timestamp": datetime.now().isoformat()
    }, indent=2)

def format_success(data: dict) -> str:
    """Format successful responses consistently."""
    return json.dumps({
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }, indent=2)

@lru_cache(maxsize=100)
def normalize_team_name(team: str) -> str:
    """Normalize team names to standard abbreviations."""
    team_map = {
        # Full names to abbreviations
        "arizona diamondbacks": "ARI", "diamondbacks": "ARI", "dbacks": "ARI",
        "atlanta braves": "ATL", "braves": "ATL",
        "baltimore orioles": "BAL", "orioles": "BAL", "o's": "BAL",
        "boston red sox": "BOS", "red sox": "BOS", "sox": "BOS",
        "chicago cubs": "CHC", "cubs": "CHC", "cubbies": "CHC",
        "chicago white sox": "CHW", "white sox": "CHW",
        "cincinnati reds": "CIN", "reds": "CIN",
        "cleveland guardians": "CLE", "guardians": "CLE",
        "colorado rockies": "COL", "rockies": "COL",
        "detroit tigers": "DET", "tigers": "DET",
        "houston astros": "HOU", "astros": "HOU", "stros": "HOU",
        "kansas city royals": "KC", "royals": "KC",
        "los angeles angels": "LAA", "angels": "LAA", "halos": "LAA",
        "los angeles dodgers": "LAD", "dodgers": "LAD",
        "miami marlins": "MIA", "marlins": "MIA", "fish": "MIA",
        "milwaukee brewers": "MIL", "brewers": "MIL", "brew crew": "MIL",
        "minnesota twins": "MIN", "twins": "MIN",
        "new york mets": "NYM", "mets": "NYM", "amazins": "NYM",
        "new york yankees": "NYY", "yankees": "NYY", "yanks": "NYY",
        "oakland athletics": "OAK", "athletics": "OAK", "a's": "OAK",
        "philadelphia phillies": "PHI", "phillies": "PHI", "phils": "PHI",
        "pittsburgh pirates": "PIT", "pirates": "PIT", "bucs": "PIT",
        "san diego padres": "SD", "padres": "SD", "pads": "SD",
        "san francisco giants": "SF", "giants": "SF",
        "seattle mariners": "SEA", "mariners": "SEA", "m's": "SEA",
        "st louis cardinals": "STL", "cardinals": "STL", "cards": "STL",
        "tampa bay rays": "TB", "rays": "TB",
        "texas rangers": "TEX", "rangers": "TEX",
        "toronto blue jays": "TOR", "blue jays": "TOR", "jays": "TOR",
        "washington nationals": "WSH", "nationals": "WSH", "nats": "WSH"
    }
    
    # Try to find team in map
    team_lower = team.lower().strip()
    return team_map.get(team_lower, team.upper()[:3])

def validate_year(year: int) -> bool:
    """Validate that year is reasonable for baseball data."""
    current_year = datetime.now().year
    return 1871 <= year <= current_year

def parse_date_range(date_str: str) -> tuple:
    """
    Parse various date range formats.
    
    Examples:
        "last 7 days"
        "past month"
        "2024-05-01 to 2024-05-31"
    """
    date_str = date_str.lower().strip()
    end_date = datetime.now()
    
    if "last" in date_str or "past" in date_str:
        # Extract number
        import re
        numbers = re.findall(r'\d+', date_str)
        days = int(numbers[0]) if numbers else 7
        
        if "month" in date_str:
            days = days * 30
        elif "week" in date_str:
            days = days * 7
            
        start_date = end_date - timedelta(days=days)
        
    else:
        # Try to parse explicit dates
        parts = date_str.split(" to ")
        if len(parts) == 2:
            start_date = datetime.strptime(parts[0].strip(), "%Y-%m-%d")
            end_date = datetime.strptime(parts[1].strip(), "%Y-%m-%d")
        else:
            # Default to last 30 days
            start_date = end_date - timedelta(days=30)
            
    return start_date, end_date

# Initialize cache on import
setup_cache()