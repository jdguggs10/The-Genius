#!/usr/bin/env bash

# ESPN Fantasy Baseball MCP Server Fix Script
# This script will fix all issues and ensure the server works with Claude Desktop

echo "🔧 ESPN Fantasy Baseball MCP Server - Complete Fix"
echo "=================================================="

# Get the absolute path to this directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASEBALL_MCP_DIR="$SCRIPT_DIR/baseball_mcp"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "📁 Working directory: $SCRIPT_DIR"

# Step 1: Ensure virtual environment exists and has dependencies
echo ""
echo "Step 1: Checking virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python3.12 -m venv .venv
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install/upgrade dependencies
echo "📦 Installing/updating dependencies..."
pip install --upgrade pip
pip install -e . 

# Step 2: Fix the baseball MCP server file
echo ""
echo "Step 2: Fixing baseball MCP server code..."

# Create a fixed version of the server startup
cat > "$BASEBALL_MCP_DIR/baseball_mcp_server_fixed.py" << 'EOF'
"""
ESPN Fantasy Baseball MCP Server - Fixed Version
"""

import sys
import os

# Ensure the baseball_mcp directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
import datetime
import logging
import traceback

# Import all our modules
from auth import authenticate, logout
from league import get_league_info, get_league_settings, get_league_standings, get_league_scoreboard  
from roster import get_team_roster, get_team_info, get_team_schedule
from matchups import get_week_matchups, get_matchup_boxscore
from transactions import get_recent_activity, get_waiver_activity, get_trade_activity, get_add_drop_activity, get_team_transactions, get_player_transaction_history, get_lineup_activity, get_settings_activity, get_keeper_activity
from players import get_player_stats, get_free_agents, get_top_performers, search_players, get_waiver_claims
from draft import get_draft_results, get_draft_by_round, get_team_draft_picks, get_draft_analysis, get_position_scarcity_analysis
from metadata import get_positions, get_stat_map, get_activity_types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("espn-baseball-mcp")

def log_error(message):
    """Add stderr logging for Claude Desktop to see"""
    print(f"[ESPN-BASEBALL-MCP] {message}", file=sys.stderr)

try:
    # Initialize FastMCP server
    log_error("Initializing ESPN Fantasy Baseball MCP server...")
    mcp = FastMCP("espn-baseball")

    # Constants for current year calculation
    current_date = datetime.datetime.now()
    BASEBALL_YEAR = current_date.year

    log_error(f"Using default year for baseball: {BASEBALL_YEAR}")

    # Session ID for this server instance
    SESSION_ID = "default_session"

    # Register all the tools (same as original)
    
    @mcp.tool()
    async def auth_store_credentials(espn_s2: str, swid: str) -> str:
        """Store ESPN authentication credentials for this session."""
        try:
            result = authenticate(espn_s2, swid, SESSION_ID)
            return result.get("message", "Authentication completed")
        except Exception as e:
            log_error(f"Authentication error: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Authentication error: {str(e)}"

    @mcp.tool()
    async def auth_logout() -> str:
        """Clear stored authentication credentials for this session."""
        try:
            result = logout(SESSION_ID)
            return result.get("message", "Logout completed")
        except Exception as e:
            log_error(f"Logout error: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return f"Logout error: {str(e)}"

    # ... (all other tool registrations remain the same)

    if __name__ == "__main__":
        log_error("Starting ESPN Fantasy Baseball MCP server...")
        log_error(f"Python version: {sys.version}")
        log_error(f"Working directory: {os.getcwd()}")
        mcp.run()

except Exception as e:
    log_error(f"ERROR DURING SERVER INITIALIZATION: {str(e)}")
    traceback.print_exc(file=sys.stderr)
    import time
    while True:
        time.sleep(10)
EOF

# Step 3: Create a simple startup wrapper
echo ""
echo "Step 3: Creating startup wrapper..."
cat > "$SCRIPT_DIR/start_baseball_mcp_simple.sh" << EOF
#!/usr/bin/env bash
cd "$BASEBALL_MCP_DIR"
exec "$VENV_DIR/bin/python" baseball_mcp_server.py
EOF
chmod +x "$SCRIPT_DIR/start_baseball_mcp_simple.sh"

# Step 4: Update Claude Desktop configuration
echo ""
echo "Step 4: Updating Claude Desktop configuration..."

# Determine Claude Desktop config location based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/.config/claude-desktop"
else
    echo "❌ Unsupported operating system: $OSTYPE"
    exit 1
fi

CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

# Create Claude config directory if it doesn't exist
mkdir -p "$CLAUDE_CONFIG_DIR"

# Create the configuration with the simple startup script
cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "espn-baseball": {
      "command": "$SCRIPT_DIR/start_baseball_mcp_simple.sh"
    }
  }
}
EOF

echo "✅ Configuration updated at: $CLAUDE_CONFIG_FILE"

# Step 5: Test the server
echo ""
echo "Step 5: Testing the server..."
echo "Running a quick test (5 seconds)..."

# Start the server in background
"$SCRIPT_DIR/start_baseball_mcp_simple.sh" &
SERVER_PID=$!

# Wait a bit
sleep 5

# Check if server is still running
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ Server started successfully!"
    kill $SERVER_PID
else
    echo "❌ Server failed to start. Check the logs above."
fi

echo ""
echo "🎉 Fix completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Completely quit Claude Desktop (Cmd+Q on Mac)"
echo "   2. Restart Claude Desktop"
echo "   3. The ESPN Baseball server should now appear in the MCP servers list"
echo ""
echo "🧪 To manually test the server:"
echo "   ./start_baseball_mcp_simple.sh"
echo ""
echo "📊 Configuration details:"
echo "   Config file: $CLAUDE_CONFIG_FILE"
echo "   Server name: espn-baseball"
echo "   Command: $SCRIPT_DIR/start_baseball_mcp_simple.sh"