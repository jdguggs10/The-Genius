#!/usr/bin/env bash

# Baseball MCP Server Startup Script
# Assumes ./setup.sh has been run to create .venv and install dependencies.

SCRIPT_PARENT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Define paths
VENV_PATH="$SCRIPT_PARENT_DIR/.venv"
BASEBALL_MCP_DIR="$SCRIPT_PARENT_DIR/baseball_mcp"
SERVER_SCRIPT="$BASEBALL_MCP_DIR/baseball_mcp_server.py"

# Check if virtualenv exists
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "   Please run ./setup.sh from the espn-api-util directory first."
    exit 1
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Check if server script exists
if [ ! -f "$SERVER_SCRIPT" ]; then
    echo "❌ Server script not found at $SERVER_SCRIPT" >&2
    exit 1
fi

# Change to the baseball_mcp directory
cd "$BASEBALL_MCP_DIR"

# Add current directory to Python path for module imports (optional, server might handle it)
# export PYTHONPATH="$BASEBALL_MCP_DIR:$PYTHONPATH"

# Run the Baseball MCP server
echo "Starting ESPN Fantasy Baseball MCP Server from $BASEBALL_MCP_DIR..."
exec python3 baseball_mcp_server.py