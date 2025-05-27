#!/usr/bin/env python3
"""
Diagnostic script for ESPN Fantasy Baseball MCP Server
"""

import os
import sys
import subprocess
import json

print("ESPN Fantasy Baseball MCP Server Diagnostics")
print("=" * 50)

# 1. Check Python version
print("\n1. Python Version:")
print(f"   {sys.version}")
if sys.version_info < (3, 12):
    print("   ❌ Python 3.12+ required")
else:
    print("   ✅ Python version OK")

# 2. Check current directory
print("\n2. Current Directory:")
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"   {script_dir}")

# 3. Check virtual environment
print("\n3. Virtual Environment:")
venv_path = os.path.join(script_dir, ".venv")
if os.path.exists(venv_path):
    print(f"   ✅ Found at: {venv_path}")
else:
    print(f"   ❌ Not found at: {venv_path}")

# 4. Check baseball_mcp directory
print("\n4. Baseball MCP Directory:")
baseball_mcp_dir = os.path.join(script_dir, "baseball_mcp")
if os.path.exists(baseball_mcp_dir):
    print(f"   ✅ Found at: {baseball_mcp_dir}")
    
    # List files
    print("   Files:")
    required_files = [
        "baseball_mcp_server.py",
        "auth.py",
        "utils.py",
        "metadata.py",
        "league.py",
        "roster.py",
        "matchups.py",
        "transactions.py",
        "players.py",
        "draft.py",
        "__init__.py"
    ]
    
    for file in required_files:
        file_path = os.path.join(baseball_mcp_dir, file)
        if os.path.exists(file_path):
            print(f"     ✅ {file}")
        else:
            print(f"     ❌ {file} - MISSING!")
else:
    print(f"   ❌ Not found at: {baseball_mcp_dir}")

# 5. Check installed packages
print("\n5. Required Packages:")
try:
    # Activate venv and check packages
    if os.path.exists(venv_path):
        pip_cmd = os.path.join(venv_path, "bin", "pip")
        result = subprocess.run([pip_cmd, "list"], capture_output=True, text=True)
        
        required_packages = ["espn-api", "mcp", "pydantic", "httpx"]
        installed = result.stdout
        
        for pkg in required_packages:
            if pkg in installed:
                print(f"   ✅ {pkg}")
            else:
                print(f"   ❌ {pkg} - NOT INSTALLED!")
except Exception as e:
    print(f"   ❌ Error checking packages: {e}")

# 6. Check Claude Desktop config
print("\n6. Claude Desktop Configuration:")
if sys.platform == "darwin":
    config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
else:
    config_path = os.path.expanduser("~/.config/claude-desktop/claude_desktop_config.json")

if os.path.exists(config_path):
    print(f"   ✅ Found at: {config_path}")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "mcpServers" in config and "espn-baseball" in config["mcpServers"]:
            print("   ✅ espn-baseball server configured")
            server_config = config["mcpServers"]["espn-baseball"]
            print(f"   Command: {server_config.get('command', 'NOT SET')}")
        else:
            print("   ❌ espn-baseball server not configured")
    except Exception as e:
        print(f"   ❌ Error reading config: {e}")
else:
    print(f"   ❌ Not found at: {config_path}")

# 7. Test import
print("\n7. Testing Module Imports:")
sys.path.insert(0, baseball_mcp_dir)
try:
    import auth
    print("   ✅ auth module")
except ImportError as e:
    print(f"   ❌ auth module: {e}")

try:
    from mcp.server.fastmcp import FastMCP
    print("   ✅ FastMCP")
except ImportError as e:
    print(f"   ❌ FastMCP: {e}")

# 8. Test server startup
print("\n8. Testing Server Startup:")
server_script = os.path.join(baseball_mcp_dir, "baseball_mcp_server.py")
if os.path.exists(server_script):
    print("   Starting server for 3 seconds...")
    try:
        # Use the venv Python
        python_cmd = os.path.join(venv_path, "bin", "python") if os.path.exists(venv_path) else sys.executable
        
        # Start the server
        env = os.environ.copy()
        env["PYTHONPATH"] = baseball_mcp_dir
        
        proc = subprocess.Popen(
            [python_cmd, server_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=baseball_mcp_dir
        )
        
        # Wait a bit
        import time
        time.sleep(3)
        
        # Check if still running
        if proc.poll() is None:
            print("   ✅ Server started successfully!")
            proc.terminate()
            proc.wait()
        else:
            stdout, stderr = proc.communicate()
            print("   ❌ Server crashed!")
            print("   STDERR:")
            print(stderr)
            print("   STDOUT:")
            print(stdout)
    except Exception as e:
        print(f"   ❌ Error starting server: {e}")
else:
    print("   ❌ Server script not found")

print("\n" + "=" * 50)
print("Diagnostics complete!")