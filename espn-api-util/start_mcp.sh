#!/usr/bin/env bash
# Script to run the generic espn_fantasy_server.py
# Assumes ./setup.sh has been run to create .venv and install dependencies.

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" # Ensure we are in espn-api-util root

echo "Running in directory: $(pwd)"

# Define paths
VENV_PATH="$SCRIPT_DIR/.venv"
SERVER_SCRIPT="$SCRIPT_DIR/espn_fantasy_server.py"

# Check if virtualenv exists
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "   Please run ./setup.sh from the espn-api-util directory first."
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Check if server script exists
if [ ! -f "$SERVER_SCRIPT" ]; then
    echo "❌ Server script not found at $SERVER_SCRIPT" >&2
    exit 1
fi

# Run the MCP server using uv
echo "Starting generic ESPN Fantasy MCP Server (espn_fantasy_server.py) using uv..."
exec uv run espn_fantasy_server.py