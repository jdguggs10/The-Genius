#!/usr/bin/env bash

# PyBaseball MCP Server Startup Script for Claude Desktop
set -euo pipefail

# Get the absolute path to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Log startup attempt
echo "Starting PyBaseball MCP Server..." >&2
echo "Script directory: $SCRIPT_DIR" >&2

# Change to the script directory first
cd "$SCRIPT_DIR"

# Define paths
VENV_PATH="$SCRIPT_DIR/venv"
SERVER_SCRIPT="$SCRIPT_DIR/pybaseball_nativemcp_server.py"

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

# Verify Python and MCP are available
if ! python -c "import mcp" 2>/dev/null; then
    echo "Error: MCP library not found in virtual environment" >&2
    exit 1
fi

# Verify our modules are available
if ! python -c "import pybaseball_nativemcp_server" 2>/dev/null; then
    echo "Error: PyBaseball MCP server module not found" >&2
    exit 1
fi

echo "Virtual environment activated successfully" >&2
echo "Starting MCP server in stdio mode..." >&2

# Set environment variables
export MCP_STDIO_MODE=1
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"

# Start the PyBaseball MCP server
exec python "$SERVER_SCRIPT" 