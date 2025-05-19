#!/usr/bin/env bash

# Baseball MCP Server Startup Script

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# Go to the baseball_mcp directory
cd "$(dirname "$0")/baseball_mcp"

# Check if virtualenv exists in parent directory, create if it doesn't
if [ ! -d "../.venv" ]; then
    echo "Creating virtual environment..."
    cd ..
    python3.12 -m venv .venv
    cd baseball_mcp
fi

# Activate the virtual environment
source ../.venv/bin/activate

# Ensure dependencies are installed
echo "Checking dependencies..."
cd ..
python3 -m pip install -e .
cd baseball_mcp

# Run the Baseball MCP server
echo "Starting ESPN Fantasy Baseball MCP Server..."
exec python3 baseball_mcp_server.py