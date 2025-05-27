#!/usr/bin/env bash

# Setup script to configure Claude Desktop to automatically start ESPN Baseball MCP Server

echo "ESPN Fantasy Baseball MCP Server - Claude Desktop Setup"
echo "======================================================="

# Get the absolute path to this directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASEBALL_MCP_DIR="$SCRIPT_DIR/baseball_mcp"
VENV_DIR="$SCRIPT_DIR/.venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "   Please run ./setup.sh first to create the virtual environment"
    exit 1
fi

# Check if baseball_mcp_server.py exists
if [ ! -f "$BASEBALL_MCP_DIR/baseball_mcp_server.py" ]; then
    echo "❌ Baseball MCP server not found at $BASEBALL_MCP_DIR/baseball_mcp_server.py"
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
cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "espn-baseball": {
      "command": "$VENV_DIR/bin/python3",
      "args": ["baseball_mcp_server.py"],
      "cwd": "$BASEBALL_MCP_DIR",
      "env": {
        "PYTHONPATH": "$BASEBALL_MCP_DIR",
        "PATH": "$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
EOF

echo ""
echo "✅ Claude Desktop configuration created successfully!"
echo ""
echo "📋 Configuration Details:"
echo "   Server Name: espn-baseball"
echo "   Command: $VENV_DIR/bin/python3"
echo "   Working Directory: $BASEBALL_MCP_DIR"
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