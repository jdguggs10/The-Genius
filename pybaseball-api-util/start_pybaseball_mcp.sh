#!/bin/bash
# Startup script for PyBaseball MCP Server

echo "Starting PyBaseball MCP Server..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to the pybaseball-api-util directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Set default port if not specified
export PORT="${PORT:-8002}"

# Kill any existing process on the port
echo "Checking for existing processes on port $PORT..."
lsof -ti:$PORT | xargs kill -9 2>/dev/null || echo "No existing process found on port $PORT"

# Run the server
echo "Starting server on port $PORT..."
python pybaseball_mcp_server.py