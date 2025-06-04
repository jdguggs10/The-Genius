#!/usr/bin/env python
"""
Test script for verifying the PyBaseball service integration.
This script will test the PyBaseball service functions directly.

Usage:
    python test_pybaseball_integration.py

Requirements:
    - httpx
    - python-dotenv
"""

import os
import asyncio
import json
from dotenv import load_dotenv
import sys

# Add the parent directory to sys.path to allow importing from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pybaseball_service import PyBaseballService

# Load environment variables
load_dotenv()

# Create a PyBaseball service instance
pybaseball = PyBaseballService()

async def test_player_stats():
    """Test getting player statistics."""
    player_name = "Shohei Ohtani"
    print(f"\n📊 Testing get_player_stats for {player_name}...")
    result = await pybaseball.get_player_stats(player_name)
    print(f"\nResult: {result}\n")
    return result

async def test_mlb_standings():
    """Test getting MLB standings."""
    print("\n🏆 Testing get_mlb_standings...")
    result = await pybaseball.get_mlb_standings()
    print(f"\nResult: {result}\n")
    return result

async def test_search_players():
    """Test searching for players."""
    search_term = "Rodriguez"
    print(f"\n🔍 Testing search_players for '{search_term}'...")
    result = await pybaseball.search_players(search_term)
    print(f"\nResult: {result}\n")
    return result

async def test_stat_leaders():
    """Test getting statistical leaders."""
    stat = "HR"
    print(f"\n👑 Testing get_stat_leaders for {stat}...")
    result = await pybaseball.get_stat_leaders(stat, top_n=5)
    print(f"\nResult: {result}\n")
    return result

async def main():
    """Run all tests."""
    print("🧪 Testing PyBaseball Service Integration")
    print("========================================")
    print(f"Using PyBaseball service URL: {pybaseball.base_url}")
    
    try:
        # Test all functions
        await test_player_stats()
        await test_mlb_standings()
        await test_search_players()
        await test_stat_leaders()
        
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("\nPlease check:")
        print("  1. PYBASEBALL_SERVICE_URL environment variable is set correctly")
        print("  2. The PyBaseball service is running at https://genius-pybaseball.onrender.com")
        print("  3. Network connectivity to the service URL")

if __name__ == "__main__":
    asyncio.run(main()) 