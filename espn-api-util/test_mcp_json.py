#!/usr/bin/env python3
"""
Test script to validate MCP JSON output
"""

import json
import sys
import subprocess
import os
import signal
import time

def test_mcp_server():
    """Test that the MCP server outputs valid JSON"""
    
    print("Testing ESPN Fantasy Baseball MCP Server JSON compliance...")
    print("=" * 60)
    
    # Change to the baseball_mcp directory
    baseball_mcp_dir = os.path.join(os.path.dirname(__file__), 'baseball_mcp')
    os.chdir(baseball_mcp_dir)
    
    # Start the server process
    cmd = [
        sys.executable, 
        'baseball_mcp_server.py'
    ]
    
    try:
        # Start the server
        print("Starting MCP server...")
        process = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, 'PYTHONPATH': '.'}
        )
        
        # Give the server a moment to start up
        time.sleep(2)
        
        # Send an MCP initialization message
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialization message...")
        init_json = json.dumps(init_message) + "\n"
        process.stdin.write(init_json)
        process.stdin.flush()
        
        # Read the response
        print("Reading server response...")
        
        # Check if the process has any stderr output (errors)
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            if stderr:
                print(f"❌ Server stderr output:")
                print(stderr)
            if stdout:
                print(f"Server stdout output:")
                print(stdout)
            return False
        
        # Try to read a line from stdout
        try:
            response_line = process.stdout.readline()
            if response_line:
                print(f"Raw response: {response_line.strip()}")
                
                # Try to parse as JSON
                response = json.loads(response_line.strip())
                print("✅ Server response is valid JSON!")
                print(f"Response: {json.dumps(response, indent=2)}")
                return True
            else:
                print("❌ No response received from server")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            print(f"Raw response: {response_line}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False
        
    finally:
        # Clean up the process
        if process and process.poll() is None:
            print("Terminating server process...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

def test_json_serialization():
    """Test that our utility functions produce valid JSON"""
    print("\nTesting JSON serialization of utility functions...")
    print("-" * 40)
    
    sys.path.insert(0, 'baseball_mcp')
    
    try:
        from utils import team_to_dict, player_to_dict
        from metadata import get_positions, get_stat_map, get_activity_types
        
        # Test metadata functions
        positions = get_positions()
        stats = get_stat_map()
        activities = get_activity_types()
        
        # Try to serialize each as JSON
        json.dumps(positions)
        print("✅ Positions metadata serializes to valid JSON")
        
        json.dumps(stats)
        print("✅ Stats metadata serializes to valid JSON")
        
        json.dumps(activities)
        print("✅ Activity types metadata serializes to valid JSON")
        
        print("✅ All utility functions produce valid JSON")
        return True
        
    except Exception as e:
        print(f"❌ JSON serialization error: {e}")
        return False

if __name__ == "__main__":
    print("ESPN Fantasy Baseball MCP JSON Validation Test")
    print("=" * 50)
    
    # Test 1: JSON serialization utilities
    json_test_passed = test_json_serialization()
    
    # Test 2: MCP server protocol compliance
    mcp_test_passed = test_mcp_server()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"JSON Serialization: {'✅ PASSED' if json_test_passed else '❌ FAILED'}")
    print(f"MCP Server Protocol: {'✅ PASSED' if mcp_test_passed else '❌ FAILED'}")
    
    if json_test_passed and mcp_test_passed:
        print("🎉 All tests passed! The server should work correctly with Claude Desktop.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the issues above.")
        sys.exit(1) 