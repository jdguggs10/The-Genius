# ESPN Fantasy Baseball MCP Server - Quick Start Guide

## 🚀 First Time Setup

### 1. Install Dependencies
```bash
cd espn-api-util
source .venv/bin/activate
pip install -e .
```

### 2. Configure Claude Desktop (Automatic Startup)
```bash
./setup_claude_desktop.sh
```

### 3. Restart Claude Desktop
- Quit Claude Desktop completely
- Relaunch Claude Desktop
- The `espn-baseball` server will now start automatically

## ✅ Verification

### Check Server Status
The server should appear in Claude Desktop as `espn-baseball`. You can verify it's working by asking Claude to:
- `Use the metadata_get_positions tool to show available positions`
- `Get league info for league ID [your-league-id]`

### Manual Testing (Optional)
```bash
# Test server independently
./start_baseball_mcp.sh

# Run JSON validation tests
python3 test_mcp_json.py
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Server not appearing in Claude Desktop | Run `./setup_claude_desktop.sh` again, then restart Claude Desktop |
| Permission denied | Run `chmod +x setup_claude_desktop.sh start_baseball_mcp.sh` |
| Python/import errors | Ensure virtual environment is activated: `source .venv/bin/activate` |
| Authentication needed | Use the `auth_store_credentials` tool with your ESPN_S2 and SWID cookies |

## 📝 Available Tools

The server provides tools for:
- **Authentication**: Store ESPN credentials
- **League Info**: Standings, settings, scoreboard
- **Teams**: Rosters, schedules, team info  
- **Players**: Stats, free agents, search
- **Transactions**: Recent activity, trades, waivers
- **Draft**: Results, analysis, team picks
- **Metadata**: Positions, stats, activity types

## 🔄 Re-setup Required If:
- You move the project directory
- You change Python versions
- You reinstall Claude Desktop

Simply run `./setup_claude_desktop.sh` again. 