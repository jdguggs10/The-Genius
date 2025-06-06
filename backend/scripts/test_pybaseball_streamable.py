#!/usr/bin/env python
"""
Comprehensive test script for PyBaseball MCP server with Streamable HTTP protocol.

This script tests both the backend service connection and the direct HTTP connection
to verify that the March 2025 specification for Streamable HTTP is correctly implemented
and working with chunked transfer encoding.

Usage:
  python test_pybaseball_streamable.py [server_url]

If server_url is not specified, it uses the PYBASEBALL_SERVICE_URL environment variable
or falls back to the default URL (http://localhost:8000).
"""
import asyncio
import os
import sys
import json
import httpx
from typing import Dict, Any, List, Optional, Tuple

# Add the parent directory to sys.path to allow importing from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pybaseball_service import PyBaseballService


# --- Configuration ---
SERVER_URL = os.environ.get("PYBASEBALL_SERVICE_URL", "http://localhost:8000")


async def test_direct_protocol_info() -> Tuple[bool, Dict[str, Any]]:
    """
    Test the protocol-info endpoint directly to verify server capabilities.
    
    Returns:
        Tuple of (success, protocol_info)
    """
    print("\n🔍 Testing protocol-info endpoint directly...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_URL}/protocol-info")
            if response.status_code == 200:
                info = response.json()
                print(f"✅ Protocol info: {json.dumps(info, indent=2)}")
                
                # Verify required fields
                if "protocol" in info and "version" in info:
                    if info["protocol"] == "MCP Streamable HTTP":
                        print("✅ Server identifies as MCP Streamable HTTP")
                        return True, info
                    else:
                        print(f"⚠️ Server identifies as {info['protocol']}, expected MCP Streamable HTTP")
                        return False, info
                else:
                    print("❌ Protocol info missing required fields")
                    return False, info
            else:
                print(f"❌ Protocol info request failed: {response.status_code}")
                return False, {}
        except Exception as e:
            print(f"❌ Error testing protocol info: {e}")
            return False, {}


async def test_direct_chunked_encoding(tool_name: str = "player_stats", params: Dict[str, Any] = None) -> bool:
    """
    Test chunked encoding by directly analyzing the response from the server.
    
    Args:
        tool_name: Name of the tool to test
        params: Parameters to pass to the tool
    
    Returns:
        True if chunked encoding is working properly
    """
    if params is None:
        params = {"player_name": "Shohei Ohtani"}
        
    print(f"\n🔄 Testing chunked encoding directly with {tool_name}...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Make a request
            response = await client.post(
                f"{SERVER_URL}/tools/{tool_name}",
                json=params,
                headers={"Accept": "application/json"},
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"❌ Request failed: {response.status_code}")
                return False
            
            # Check transfer encoding header
            if "transfer-encoding" in response.headers:
                encoding = response.headers["transfer-encoding"]
                if "chunked" in encoding.lower():
                    print(f"✅ Server is using Transfer-Encoding: chunked")
                else:
                    print(f"⚠️ Server is using Transfer-Encoding but not chunked: {encoding}")
                    return False
            else:
                print("⚠️ No Transfer-Encoding header found")
                # Continue anyway since the header might be handled by proxies
            
            # Try to read response chunks
            chunk_count = 0
            async for chunk in response.aiter_bytes():
                chunk_count += 1
                # Just count chunks, no need to display them all
                if chunk_count <= 2:  # Only show first few chunks
                    print(f"📦 Received chunk {chunk_count}: {chunk[:50]}...")
            
            print(f"✅ Received {chunk_count} chunks from server")
            
            # If we got multiple chunks, that's a good sign
            return chunk_count > 1
            
        except Exception as e:
            print(f"❌ Error testing chunked encoding: {e}")
            return False


async def test_backend_service():
    """Test backend connection to PyBaseball MCP server via PyBaseballService."""
    print("\n🔄 Testing backend connection via PyBaseballService...")
    
    ps = PyBaseballService(url=SERVER_URL)  # Use the same URL as direct tests
    print(f"Service URL: {ps.base_url}")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    tests_total += 1
    print("\n1️⃣ Testing health check...")
    try:
        health = await ps._call_tool("health_check", {})
        print(f"Health response: {health}")
        if health:
            tests_passed += 1
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: Player Search
    tests_total += 1
    print("\n2️⃣ Testing player search...")
    try:
        players = await ps.search_players("Judge")
        print(f"Players response: {players}")
        if players:
            tests_passed += 1
    except Exception as e:
        print(f"❌ Player search failed: {e}")
    
    # Test 3: Protocol Info
    tests_total += 1
    print("\n3️⃣ Testing protocol info...")
    try:
        info = await ps._call_tool("protocol-info", {})
        print(f"Protocol info: {info}")
        if "protocol" in info and info["protocol"] == "MCP Streamable HTTP":
            tests_passed += 1
    except Exception as e:
        print(f"❌ Protocol info failed: {e}")
    
    # Test 4: Stat Leaders
    tests_total += 1
    print("\n4️⃣ Testing stat leaders...")
    try:
        leaders = await ps.get_stat_leaders("HR", 3)
        print(f"Stat leaders: {leaders}")
        if leaders:
            tests_passed += 1
    except Exception as e:
        print(f"❌ Stat leaders failed: {e}")
    
    # Test 5: Player Stats (slower, good for testing chunked encoding)
    tests_total += 1
    print("\n5️⃣ Testing player stats (streaming response)...")
    try:
        result = await ps._call_tool("player_stats", {"player_name": "Shohei Ohtani"})
        print(f"Streaming response received: {'✅' if result else '❌'}")
        print(f"Response: {result[:200]}..." if len(str(result)) > 200 else result)
        if result:
            tests_passed += 1
    except Exception as e:
        print(f"❌ Player stats failed: {e}")
    
    # Test 6: MLB Standings (reported bug)
    tests_total += 1
    print("\n6️⃣ Testing MLB standings (reported bug)...")
    try:
        standings = await ps.get_mlb_standings()
        print(f"Standings response: {standings}")
        if standings and "standings" in standings:
            tests_passed += 1
            print("✅ MLB standings endpoint is working properly")
        else:
            print("⚠️ MLB standings response format may have issues")
    except Exception as e:
        print(f"❌ MLB standings failed: {e}")
        print(f"This confirms the reported bug in mlb_standings")
    
    print(f"\nTests passed: {tests_passed}/{tests_total} ({int(tests_passed/tests_total*100)}%)")
    
    return tests_passed == tests_total


async def main():
    """Run all tests."""
    print("🧪 Comprehensive PyBaseball MCP Server Streamable HTTP Test")
    print("==========================================================")
    print(f"Server URL: {SERVER_URL}")
    
    success = True
    
    # Test 1: Protocol Info
    protocol_success, _ = await test_direct_protocol_info()
    success = success and protocol_success
    
    # Test 2: Chunked Encoding
    chunked_success = await test_direct_chunked_encoding()
    success = success and chunked_success
    
    # Test 3: Backend Service
    backend_success = await test_backend_service()
    success = success and backend_success
    
    # Print summary
    print("\n==========================================================")
    print("Test Summary:")
    print(f"Protocol Info: {'✅ PASSED' if protocol_success else '❌ FAILED'}")
    print(f"Chunked Encoding: {'✅ PASSED' if chunked_success else '❌ FAILED'}")
    print(f"Backend Service: {'✅ PASSED' if backend_success else '❌ FAILED'}")
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if success else '❌ SOME TESTS FAILED'}")
    print(f"Server URL: {SERVER_URL}")
    
    return 0 if success else 1


if __name__ == "__main__":
    # Check if server URL was provided as argument
    if len(sys.argv) > 1:
        SERVER_URL = sys.argv[1]
        
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
