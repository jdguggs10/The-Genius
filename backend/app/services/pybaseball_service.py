import os
import logging
import httpx
import json
from typing import Any, Dict, Optional, List

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
    async def get_player_stats(self, player_name: str, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieves season statistics for a specific MLB player.
        """
        payload = {"player_name": player_name}
        if year is not None:
            payload["year"] = year
        return await self._call_tool("player_stats", payload)

    async def search_players(self, search_term: str) -> Dict[str, Any]:
        """
        Searches for MLB players by name.
        """
        payload = {"search_term": search_term}
        return await self._call_tool("search_players", payload)

    async def get_mlb_standings(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieves current MLB standings by division.
        """
        payload = {}
        if year is not None:
            payload["year"] = year
        return await self._call_tool("mlb_standings", payload)

    async def get_stat_leaders(
        self, stat: str, year: Optional[int] = None, top_n: Optional[int] = 10, player_type: Optional[str] = "batting"
    ) -> Dict[str, Any]:
        """
        Retrieves MLB leaders for a specific statistic.
        """
        payload = {"stat": stat}
        if year is not None:
            payload["year"] = year
        if top_n is not None:
            payload["top_n"] = top_n
        if player_type is not None:
            payload["player_type"] = player_type
        return await self._call_tool("stat_leaders", payload)
    
    async def get_player_recent_performance(self, player_name: str, days: int = 30) -> str:
        """Get recent game performance for an MLB player."""
        params = {"player_name": player_name, "days": days}
        return await self._call_tool("player_recent_performance", params)

    async def get_team_statistics(self, team_name: str, year: Optional[int] = None) -> str:
        """Get aggregate statistics for an MLB team."""
        params = {"team_name": team_name}
        if year:
            params["year"] = year
        return await self._call_tool("team_statistics", params)

    async def clear_pybaseball_cache(self) -> str:
        """Clear the statistics cache on the PyBaseball service."""
        return await self._call_tool("clear_stats_cache", {})

    async def check_pybaseball_service_health(self) -> str:
        """Check the health of the PyBaseball MCP service itself."""
        return await self._call_tool("health_check", {})
    
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