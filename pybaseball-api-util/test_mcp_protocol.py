#!/usr/bin/env python3
"""
Test script to verify PyBaseball MCP server follows the proper MCP protocol.
"""
import asyncio
import json
import subprocess
import sys
import os

async def test_mcp_protocol():
    """Test the MCP protocol compliance of the PyBaseball server."""
    print("Testing PyBaseball MCP Server Protocol...", file=sys.stderr)
    
    # Set environment variable
    env = os.environ.copy()
    env["MCP_STDIO_MODE"] = "1"
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, "pybaseball_mcp_server_v2.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    try:
        # Step 1: Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        print("Sending initialization request...", file=sys.stderr)
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read the initialization response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialization response: {response['result']['serverInfo']['name']}", file=sys.stderr)
        else:
            print("❌ No initialization response", file=sys.stderr)
            return False
            
        # Step 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        print("Sending initialized notification...", file=sys.stderr)
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Step 3: Request tools list
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("Requesting tools list...", file=sys.stderr)
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # Read the tools response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            tools = response.get('result', {}).get('tools', [])
            print(f"✅ Found {len(tools)} tools:", file=sys.stderr)
            for tool in tools[:3]:  # Show first 3 tools
                print(f"  - {tool['name']}: {tool['description']}", file=sys.stderr)
            return True
        else:
            print("❌ No tools response", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}", file=sys.stderr)
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    try:
        success = asyncio.run(test_mcp_protocol())
        if success:
            print("🎉 MCP Protocol test passed!", file=sys.stderr)
        else:
            print("❌ MCP Protocol test failed!", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}", file=sys.stderr)
        sys.exit(1) 