import os
import logging
import httpx
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PyBaseballService:
    """Service for integrating with the PyBaseball API."""
    
    def __init__(self):
        self.base_url = os.getenv("PYBASEBALL_SERVICE_URL", "https://genius-pybaseball.onrender.com")
        self.timeout = 30  # seconds
        logger.info(f"PyBaseball service initialized with URL: {self.base_url}")
    
    async def _call_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Call a PyBaseball tool and return the result."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/tools/{tool_name}",
                    json=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                return result.get("result", "No data available")
        except Exception as e:
            logger.error(f"Error calling PyBaseball tool {tool_name}: {e}")
            return f"Error retrieving data: {str(e)}"
    
    # Tool wrapper functions
    async def get_player_stats(self, player_name: str, year: Optional[int] = None) -> str:
        """Get season statistics for an MLB player."""
        params = {"player_name": player_name}
        if year:
            params["year"] = year
        return await self._call_tool("player_stats", params)
    
    async def get_mlb_standings(self, year: Optional[int] = None) -> str:
        """Get current MLB standings."""
        params = {}
        if year:
            params["year"] = year
        return await self._call_tool("mlb_standings", params)
    
    async def get_stat_leaders(self, stat: str, year: Optional[int] = None, 
                               top_n: int = 10, player_type: str = "batting") -> str:
        """Get MLB statistical leaders."""
        params = {
            "stat": stat,
            "top_n": top_n,
            "player_type": player_type
        }
        if year:
            params["year"] = year
        return await self._call_tool("stat_leaders", params)
    
    async def search_players(self, search_term: str) -> str:
        """Search for MLB players by name."""
        return await self._call_tool("search_players", {"search_term": search_term})
    
    async def get_schedule_and_record(self, season: int, team: str) -> str:
        """Get team-by-team game results & upcoming schedule."""
        params = {
            "season": season,
            "team": team
        }
        return await self._call_tool("schedule_and_record", params)
    
    async def get_statcast(self, start_dt: str, end_dt: str) -> str:
        """Get all Statcast pitches in the date window."""
        params = {
            "start_dt": start_dt,
            "end_dt": end_dt
        }
        return await self._call_tool("statcast", params)
    
    async def get_statcast_pitcher(self, player_id: int, start_dt: str, end_dt: str) -> str:
        """Get pitch-level Statcast for one pitcher."""
        params = {
            "player_id": player_id,
            "start_dt": start_dt,
            "end_dt": end_dt
        }
        return await self._call_tool("statcast_pitcher", params)
    
    async def get_statcast_batter(self, player_id: int, start_dt: str, end_dt: str) -> str:
        """Get batter-level Statcast."""
        params = {
            "player_id": player_id,
            "start_dt": start_dt,
            "end_dt": end_dt
        }
        return await self._call_tool("statcast_batter", params)
    
    async def get_pitching_stats(self, start_season: int, end_season: Optional[int] = None) -> str:
        """Get season-level FanGraphs pitching metrics."""
        params = {
            "start_season": start_season
        }
        if end_season:
            params["end_season"] = end_season
        else:
            params["end_season"] = start_season
        return await self._call_tool("pitching_stats", params)
    
    async def get_batting_stats(self, start_season: int, end_season: Optional[int] = None) -> str:
        """Get season-level FanGraphs batting metrics."""
        params = {
            "start_season": start_season
        }
        if end_season:
            params["end_season"] = end_season
        else:
            params["end_season"] = start_season
        return await self._call_tool("batting_stats", params)
    
    async def get_playerid_lookup(self, last_name: str, first_name: Optional[str] = None) -> str:
        """Get MLBAM, FanGraphs, B-Ref IDs, etc."""
        params = {
            "last_name": last_name
        }
        if first_name:
            params["first_name"] = first_name
        return await self._call_tool("playerid_lookup", params)
    
    async def get_team_ids(self) -> str:
        """Get master lookup of MLB team IDs & abbreviations."""
        return await self._call_tool("team_ids", {})

# Global instance
pybaseball_service = PyBaseballService()