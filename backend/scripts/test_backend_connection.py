#!/usr/bin/env python
"""
Test script to check the backend connection to PyBaseball MCP server.
"""
import asyncio
import os
import sys

# Add the parent directory to sys.path to allow importing from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pybaseball_service import PyBaseballService

async def test_backend_connection():
    """Test backend connection to PyBaseball MCP server."""
    ps = PyBaseballService()
    print(f"Service URL: {ps.base_url}")
    
    print("\n1️⃣ Testing health check...")
    health = await ps._call_tool("health_check", {})
    print(f"Health response: {health}")
    
    print("\n2️⃣ Testing player search...")
    players = await ps.search_players("Judge")
    print(f"Players response: {players}")
    
    print("\n3️⃣ Testing protocol info...")
    try:
        info = await ps._call_tool("protocol-info", {})
        print(f"Protocol info: {info}")
    except Exception as e:
        print(f"Error accessing protocol info: {e}")
    
    print("\n4️⃣ Testing stat leaders...")
    leaders = await ps.get_stat_leaders("HR", 3)
    print(f"Stat leaders: {leaders}")
    
    print("\n5️⃣ Testing streaming response handling...")
    # This endpoint should be using chunked transfer encoding
    result = await ps._call_tool("player_stats", {"player_name": "Shohei Ohtani"})
    print(f"Streaming response properly handled: {'✅' if result else '❌'}")
    print(f"Response: {result[:200]}..." if len(str(result)) > 200 else result)

if __name__ == "__main__":
    asyncio.run(test_backend_connection())
