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

# Global instance
pybaseball_service = PyBaseballService()