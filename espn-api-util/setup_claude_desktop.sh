#!/usr/bin/env bash

# Setup script to configure Claude Desktop to automatically start ESPN Baseball MCP Server

echo "ESPN Fantasy Baseball MCP Server - Claude Desktop Setup"
echo "======================================================="

# Get the absolute path to this directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# VENV_DIR and BASEBALL_MCP_DIR are not directly needed here if start_claude_mcp.sh handles its paths

# Check if start_claude_mcp.sh exists (this will be the command)
START_SCRIPT_PATH="$SCRIPT_DIR/start_claude_mcp.sh"
if [ ! -f "$START_SCRIPT_PATH" ]; then
    echo "❌ Startup script not found at $START_SCRIPT_PATH"
    echo "   Ensure start_claude_mcp.sh is present in the same directory as this setup script."
    exit 1
fi

# Check if virtual environment exists (as start_claude_mcp.sh will need it)
# This is an indirect check to ensure the target script has what it needs
VENV_DIR_CHECK="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR_CHECK" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR_CHECK (needed by $START_SCRIPT_PATH)"
    echo "   Please run ./setup.sh or ./start_baseball_mcp.sh (which includes setup) first."
    exit 1
fi

# Determine Claude Desktop config location based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CLAUDE_CONFIG_DIR="$HOME/.config/claude-desktop"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    CLAUDE_CONFIG_DIR="$APPDATA/Claude"
else
    echo "❌ Unsupported operating system: $OSTYPE"
    exit 1
fi

CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

echo "📁 Claude Desktop config directory: $CLAUDE_CONFIG_DIR"
echo "📄 Claude Desktop config file: $CLAUDE_CONFIG_FILE"

# Create Claude config directory if it doesn't exist
mkdir -p "$CLAUDE_CONFIG_DIR"

# Create the configuration JSON
# The command will now be the start_claude_mcp.sh script.
# It is responsible for setting its own CWD, PYTHONPATH, and activating the venv.
cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "espn-baseball": {
      "command": "$START_SCRIPT_PATH"
    }
  }
}
EOF

echo ""
echo "✅ Claude Desktop configuration created successfully!"
echo ""
echo "📋 Configuration Details:"
echo "   Server Name: espn-baseball"
echo "   Command: $START_SCRIPT_PATH"
echo "   Working Directory: $SCRIPT_DIR"
echo "   Config File: $CLAUDE_CONFIG_FILE"
echo ""
echo "🚀 Next Steps:"
echo "   1. Restart Claude Desktop if it's currently running"
echo "   2. The ESPN Baseball MCP server will now start automatically when Claude Desktop launches"
echo "   3. You should see the server available in Claude Desktop's MCP servers list"
echo ""
echo "🧪 To test the configuration:"
echo "   You can manually test the server by running: ./start_baseball_mcp.sh"
echo ""
echo "📖 Note: If you move this project directory, you'll need to run this setup script again" 