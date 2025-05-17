#!/usr/bin/env bash
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# start_mcp.sh

# 1) Go to the repo
cd /Users/geraldgugger/code/the-genius/espn-api-util

# 2) Check if virtualenv exists, create if it doesn't
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3.12 -m venv .venv
fi

# 3) Activate your virtualenv
source .venv/bin/activate

# 4) Ensure dependencies are installed
echo "Checking dependencies..."
python3 -m pip install -e .

# 5) Run the MCP server
exec uv run espn_fantasy_server.py