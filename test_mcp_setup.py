#!/usr/bin/env python3
"""
Test script to verify MCP server setup for Claude Desktop
"""
import json
import os
import subprocess
import sys

def test_config_file():
    """Test that the Claude Desktop config file exists and is valid"""
    config_path = "/Users/geraldgugger/Library/Application Support/Claude/claude_desktop_config.json"
    
    if not os.path.exists(config_path):
        print("❌ Claude Desktop config file not found!")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Claude Desktop config file found and valid JSON")
        
        if 'mcpServers' not in config:
            print("❌ No mcpServers section in config")
            return False
        
        servers = config['mcpServers']
        print(f"📋 Found {len(servers)} MCP servers configured:")
        
        for name, server_config in servers.items():
            print(f"  • {name}: {server_config.get('command', 'No command')}")
        
        # Check for our specific servers
        if 'espn-baseball' in servers and 'pybaseball-stats' in servers:
            print("✅ Both ESPN Baseball and PyBaseball MCP servers configured")
            return True
        else:
            print("❌ Missing one or both MCP servers")
            return False
            
    except json.JSONDecodeError:
        print("❌ Claude Desktop config file contains invalid JSON")
        return False

def test_startup_scripts():
    """Test that startup scripts exist and are executable"""
    scripts = [
        "/Users/geraldgugger/Code/the-genius/espn-api-util/start_baseball_mcp_simple.sh",
        "/Users/geraldgugger/Code/the-genius/pybaseball-api-util/start_pybaseball_mcp_claude.sh"
    ]
    
    all_good = True
    for script in scripts:
        if os.path.exists(script) and os.access(script, os.X_OK):
            print(f"✅ {os.path.basename(script)} exists and is executable")
        else:
            print(f"❌ {os.path.basename(script)} missing or not executable")
            all_good = False
    
    return all_good

def main():
    print("🔍 Testing Claude Desktop MCP Setup")
    print("=" * 40)
    
    config_ok = test_config_file()
    scripts_ok = test_startup_scripts()
    
    print("\n" + "=" * 40)
    if config_ok and scripts_ok:
        print("✅ MCP setup looks good!")
        print("\n📝 Next steps:")
        print("1. Restart Claude Desktop if it's running")
        print("2. The MCP servers should automatically start when Claude Desktop launches")
        print("3. You can use baseball statistics tools in your conversations")
        print("\n🛠️  Available tools:")
        print("  ESPN: Fantasy baseball data, team stats, player info")
        print("  PyBaseball: MLB statistics, player stats, standings, leaders")
    else:
        print("❌ MCP setup has issues that need to be fixed")
        sys.exit(1)

if __name__ == "__main__":
    main() 