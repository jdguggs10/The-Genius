#!/usr/bin/env bash

# ESPN Fantasy Baseball MCP Server Startup Script for Claude Desktop

# Set error handling
set -e

# Get the absolute path to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Export PATH to include common locations
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Define paths
VENV_PATH="$SCRIPT_DIR/.venv"
BASEBALL_MCP_DIR="$SCRIPT_DIR/baseball_mcp"
SERVER_SCRIPT="$BASEBALL_MCP_DIR/baseball_mcp_server.py"

# Log startup attempt
echo "Starting ESPN Fantasy Baseball MCP Server..." >&2
echo "Script directory: $SCRIPT_DIR" >&2
echo "Virtual environment: $VENV_PATH" >&2
echo "Baseball MCP directory: $BASEBALL_MCP_DIR" >&2
echo "Server script: $SERVER_SCRIPT" >&2

# Check if virtual environment exists
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH" >&2
    exit 1
fi

# Check if server script exists
if [ ! -f "$SERVER_SCRIPT" ]; then
    echo "Error: Server script not found at $SERVER_SCRIPT" >&2
    exit 1
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Change to the baseball_mcp directory
cd "$BASEBALL_MCP_DIR"

# Add current directory to Python path for module imports
export PYTHONPATH="$BASEBALL_MCP_DIR:$PYTHONPATH"

echo "Python path: $(which python)" >&2
echo "Working directory: $(pwd)" >&2

# Start the baseball MCP server
exec python baseball_mcp_server.py 