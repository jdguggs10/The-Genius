#!/usr/bin/env bash
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# start_mcp.sh

# 1) Go to the repo
cd /Users/geraldgugger/code/gg_espn_fb

# 2) Activate your virtualenv
source .venv/bin/activate

# 3) Run the MCP server
exec uv run espn_fantasy_server.py