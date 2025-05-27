#!/usr/bin/env python3
"""
Debug script to simulate Claude Desktop's interaction with the MCP server.
"""
import subprocess
import json
import sys
import os
import time

def simulate_claude_startup():
    """Simulate what Claude Desktop does when starting the MCP server."""
    print("Simulating Claude Desktop startup sequence...", file=sys.stderr)
    
    # Start the server using the same command Claude Desktop would use
    env = os.environ.copy()
    env["MCP_STDIO_MODE"] = "1"
    
    print("Starting server process...", file=sys.stderr)
    process = subprocess.Popen(
        ["bash", "./start_pybaseball_mcp_claude.sh"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        bufsize=0  # Unbuffered
    )
    
    try:
        # Give it a moment to start
        time.sleep(1)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ Server exited immediately with code: {process.returncode}", file=sys.stderr)
            print(f"Stdout: {stdout}", file=sys.stderr)
            print(f"Stderr: {stderr}", file=sys.stderr)
            return False
        
        print("✅ Server started successfully", file=sys.stderr)
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "claude-desktop", "version": "1.0"}
            }
        }
        
        print("Sending initialization request...", file=sys.stderr)
        try:
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
        except BrokenPipeError:
            print("❌ Broken pipe when sending initialization", file=sys.stderr)
            return False
        
        # Try to read response
        print("Waiting for response...", file=sys.stderr)
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"✅ Got initialization response: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}", file=sys.stderr)
                return True
            else:
                print("❌ No response received", file=sys.stderr)
                return False
        except Exception as e:
            print(f"❌ Error reading response: {e}", file=sys.stderr)
            return False
            
    finally:
        # Clean up
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    print("Claude Desktop MCP Server Startup Simulation", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    success = simulate_claude_startup()
    if success:
        print("🎉 Server startup simulation successful!", file=sys.stderr)
        print("The server should work with Claude Desktop.", file=sys.stderr)
    else:
        print("❌ Server startup simulation failed!", file=sys.stderr)
        print("Claude Desktop will not be able to connect to this server.", file=sys.stderr) 