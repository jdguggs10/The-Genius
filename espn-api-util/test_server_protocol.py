#!/usr/bin/env python3
"""
Test script to validate MCP Server Protocol Compliance
"""

import json
import sys
import subprocess
import os
import signal
import time

def test_mcp_server_initialization():
    """Test that the MCP server responds correctly to an initialize message"""
    
    print("Testing ESPN Fantasy Baseball MCP Server Initialization...")
    print("=" * 60) # Corrected print length
    
    # Change to the baseball_mcp directory
    baseball_mcp_dir = os.path.join(os.path.dirname(__file__), 'baseball_mcp')
    original_dir = os.getcwd()
    process = None # Initialize process to None

    if os.path.exists(baseball_mcp_dir) and os.path.isdir(baseball_mcp_dir):
        os.chdir(baseball_mcp_dir)
    else:
        print(f"❌ Could not change to directory: {baseball_mcp_dir}. Ensure it exists relative to the script.")
        if not os.path.exists('baseball_mcp_server.py'): # Check in original_dir if chdir failed
            # Check if script is already in baseball_mcp folder
            if os.path.basename(original_dir) == 'baseball_mcp' and os.path.exists('baseball_mcp_server.py'):
                 print(f"⚠️ Running from current directory: {original_dir} (seems to be baseball_mcp).")
            else:
                print("❌ baseball_mcp_server.py not found in current directory or expected relative path. Aborting.")
                return False
        else: # baseball_mcp_server.py found in original_dir
            print(f"⚠️ Running from current directory: {original_dir} as baseball_mcp_server.py found here. This might have unintended consequences if other relative paths are expected.")

    
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
            # env={**os.environ, 'PYTHONPATH': '.'} # PYTHONPATH '.' is implicit when cwd is baseball_mcp_dir
            # If not in baseball_mcp_dir, PYTHONPATH might need adjustment or direct path to modules
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
        if process and process.poll() is not None:
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
                # Check stderr if no response
                if process:
                    stderr_output = process.stderr.read()
                    if stderr_output:
                        print(f"Stderr from server: {stderr_output}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            print(f"Raw response: {response_line}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        import traceback
        traceback.print_exc() # Print stack trace for better debugging
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
        os.chdir(original_dir) # Change back to original directory

if __name__ == "__main__":
    print("ESPN Fantasy Baseball MCP Server Protocol Test")
    print("=" * 50)
    
    mcp_test_passed = test_mcp_server_initialization()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"MCP Server Protocol Initialization: {'✅ PASSED' if mcp_test_passed else '❌ FAILED'}")
    
    if mcp_test_passed:
        print("🎉 MCP server initialization test passed!")
        sys.exit(0)
    else:
        print("❌ MCP server initialization test failed. Check the issues above.")
        sys.exit(1) 