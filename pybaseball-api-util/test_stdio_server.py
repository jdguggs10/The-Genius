#!/usr/bin/env python3
"""
Test script to debug the MCP stdio server issues.
"""
import subprocess
import json
import sys
import os
import time
import signal

def test_stdio_server():
    """Test the MCP stdio server with proper protocol handling."""
    print("Testing MCP stdio server...", file=sys.stderr)
    
    # Set environment
    env = os.environ.copy()
    env["MCP_STDIO_MODE"] = "1"
    
    # Start the server
    process = subprocess.Popen(
        ["bash", "./start_pybaseball_mcp_claude.sh"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    try:
        # Wait a moment for server to start
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ Server exited with code: {process.returncode}", file=sys.stderr)
            print(f"Stderr: {stderr}", file=sys.stderr)
            return False
        
        print("✅ Server started and is running", file=sys.stderr)
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"}
            }
        }
        
        print("Sending initialization request...", file=sys.stderr)
        request_json = json.dumps(init_request)
        print(f"Request: {request_json}", file=sys.stderr)
        
        process.stdin.write(request_json + "\n")
        process.stdin.flush()
        
        # Set a timeout for reading response
        def timeout_handler(signum, frame):
            raise TimeoutError("Response timeout")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout
        
        try:
            print("Waiting for response...", file=sys.stderr)
            response_line = process.stdout.readline()
            signal.alarm(0)  # Cancel timeout
            
            if response_line:
                print(f"Raw response: {response_line.strip()}", file=sys.stderr)
                try:
                    response = json.loads(response_line.strip())
                    if "result" in response:
                        server_info = response["result"].get("serverInfo", {})
                        print(f"✅ Server initialized: {server_info.get('name', 'Unknown')}", file=sys.stderr)
                        
                        # Send initialized notification
                        initialized_notification = {
                            "jsonrpc": "2.0",
                            "method": "notifications/initialized"
                        }
                        
                        print("Sending initialized notification...", file=sys.stderr)
                        process.stdin.write(json.dumps(initialized_notification) + "\n")
                        process.stdin.flush()
                        
                        # Request tools list
                        tools_request = {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/list",
                            "params": {}
                        }
                        
                        print("Requesting tools list...", file=sys.stderr)
                        process.stdin.write(json.dumps(tools_request) + "\n")
                        process.stdin.flush()
                        
                        # Read tools response
                        signal.alarm(10)  # Reset timeout
                        tools_response_line = process.stdout.readline()
                        signal.alarm(0)
                        
                        if tools_response_line:
                            tools_response = json.loads(tools_response_line.strip())
                            tools = tools_response.get("result", {}).get("tools", [])
                            print(f"✅ Got {len(tools)} tools", file=sys.stderr)
                            for tool in tools[:3]:
                                print(f"  - {tool['name']}", file=sys.stderr)
                            return True
                        else:
                            print("❌ No tools response", file=sys.stderr)
                            return False
                    else:
                        print(f"❌ Invalid response format: {response}", file=sys.stderr)
                        return False
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}", file=sys.stderr)
                    print(f"Response was: {response_line}", file=sys.stderr)
                    return False
            else:
                print("❌ No response received", file=sys.stderr)
                return False
                
        except TimeoutError:
            print("❌ Response timeout", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}", file=sys.stderr)
        return False
    finally:
        # Clean up
        signal.alarm(0)  # Cancel any pending alarms
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    print("MCP Stdio Server Debug Test", file=sys.stderr)
    print("=" * 40, file=sys.stderr)
    
    success = test_stdio_server()
    if success:
        print("🎉 Server test passed!", file=sys.stderr)
    else:
        print("❌ Server test failed!", file=sys.stderr)
        sys.exit(1) 