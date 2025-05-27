#!/usr/bin/env bash

# ESPN Fantasy Baseball MCP Server Startup Script for Claude Desktop

# Set error handling
set -e

# Export PATH to include common locations
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Navigate to the espn-api-util directory
cd "$(dirname "$0")"

# Activate the virtual environment
source .venv/bin/activate

# Navigate to the baseball_mcp directory
cd baseball_mcp

# Add current directory to Python path for module imports
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Log startup attempt
echo "Starting ESPN Fantasy Baseball MCP Server..." >&2
echo "Working directory: $(pwd)" >&2
echo "Python path: $(which python)" >&2

# Start the baseball MCP server
exec python baseball_mcp_server.py 