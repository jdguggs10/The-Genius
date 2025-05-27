#!/usr/bin/env bash

# PyBaseball MCP Server Startup Script for Claude Desktop

# Set error handling
set -e

# Get the absolute path to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Export PATH to include common locations
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Define paths
VENV_PATH="$SCRIPT_DIR/venv"
SERVER_SCRIPT="$SCRIPT_DIR/pybaseball_mcp_server.py"

# Log startup attempt
echo "Starting PyBaseball MCP Server..." >&2
echo "Script directory: $SCRIPT_DIR" >&2
echo "Virtual environment: $VENV_PATH" >&2
echo "Server script: $SERVER_SCRIPT" >&2

# Check if virtual environment exists
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH" >&2
    echo "Creating virtual environment..." >&2
    python3 -m venv "$VENV_PATH"
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Install dependencies if requirements.txt exists
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "Installing/updating dependencies..." >&2
    pip install -r "$SCRIPT_DIR/requirements.txt" -q >&2
fi

# Check if server script exists
if [ ! -f "$SERVER_SCRIPT" ]; then
    echo "Error: Server script not found at $SERVER_SCRIPT" >&2
    exit 1
fi

# Change to the script directory
cd "$SCRIPT_DIR"

# Add current directory to Python path for module imports
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

echo "Python path: $(which python)" >&2
echo "Working directory: $(pwd)" >&2

# Set environment variable to run in MCP stdio mode instead of HTTP server mode
export MCP_STDIO_MODE=1

# Start the PyBaseball MCP server in stdio mode
exec python pybaseball_mcp_server_v2.py 