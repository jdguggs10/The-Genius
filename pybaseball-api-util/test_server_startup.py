#!/usr/bin/env python3
"""
Simple test to check if the PyBaseball MCP server can start up without errors.
"""
import sys
import os
import subprocess

def test_server_startup():
    """Test if the server can start up without import or initialization errors."""
    print("Testing PyBaseball MCP Server startup...", file=sys.stderr)
    
    # Test 1: Import test
    print("1. Testing imports...", file=sys.stderr)
    try:
        import pybaseball_mcp_server_v2
        print("   ✅ Server module imports successfully", file=sys.stderr)
    except Exception as e:
        print(f"   ❌ Import error: {e}", file=sys.stderr)
        return False
    
    # Test 2: Function imports
    print("2. Testing function imports...", file=sys.stderr)
    try:
        from pybaseball_mcp.players import get_player_stats, get_player_recent_stats, search_player
        from pybaseball_mcp.teams import get_standings, get_league_leaders, get_team_stats
        from pybaseball_mcp.utils import clear_cache, get_cache_info
        print("   ✅ All function modules import successfully", file=sys.stderr)
    except Exception as e:
        print(f"   ❌ Function import error: {e}", file=sys.stderr)
        return False
    
    # Test 3: MCP library availability
    print("3. Testing MCP library...", file=sys.stderr)
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool as MCPTool, TextContent
        import mcp.types as types
        print("   ✅ MCP library imports successfully", file=sys.stderr)
    except Exception as e:
        print(f"   ❌ MCP import error: {e}", file=sys.stderr)
        return False
    
    # Test 4: PyBaseball library
    print("4. Testing PyBaseball library...", file=sys.stderr)
    try:
        import pybaseball as pyb
        pyb.cache.enable()
        print("   ✅ PyBaseball library imports and cache enabled", file=sys.stderr)
    except Exception as e:
        print(f"   ❌ PyBaseball error: {e}", file=sys.stderr)
        return False
    
    # Test 5: Quick server startup test
    print("5. Testing server startup (should exit immediately)...", file=sys.stderr)
    env = os.environ.copy()
    env["MCP_STDIO_MODE"] = "1"
    
    # Create a process that will get immediate EOF
    process = subprocess.Popen(
        [sys.executable, "pybaseball_mcp_server_v2.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    # Close stdin immediately to simulate what happens when Claude starts the server
    process.stdin.close()
    
    # Wait for process to exit
    try:
        stdout, stderr = process.communicate(timeout=10)
        if process.returncode == 0:
            print("   ✅ Server starts and exits cleanly", file=sys.stderr)
        else:
            print(f"   ❌ Server exited with code {process.returncode}", file=sys.stderr)
            if stderr:
                print(f"   Error output: {stderr}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        process.kill()
        print("   ❌ Server didn't exit cleanly within 10 seconds", file=sys.stderr)
        return False
    
    return True

if __name__ == "__main__":
    print("PyBaseball MCP Server Startup Test", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    if test_server_startup():
        print("🎉 All startup tests passed!", file=sys.stderr)
        print("The server should work with Claude Desktop.", file=sys.stderr)
    else:
        print("❌ Some startup tests failed!", file=sys.stderr)
        print("There are issues that need to be fixed before using with Claude Desktop.", file=sys.stderr)
        sys.exit(1) 