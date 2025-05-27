# ESPN Fantasy Baseball MCP Server

A Model Context Protocol (MCP) server that provides seamless access to ESPN Fantasy Baseball data through Claude Desktop and other MCP-compatible AI assistants.

## 🚀 Quick Start

```bash
# 1. Install dependencies
cd espn-api-util
source .venv/bin/activate
pip install -e .

# 2. Configure Claude Desktop for automatic startup
./setup_claude_desktop.sh

# 3. Restart Claude Desktop
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## 🏗️ Architecture

- **MCP Server**: Uses FastMCP to expose ESPN Fantasy Baseball API through MCP protocol
- **ESPN API Integration**: Built on top of the `espn-api` Python package
- **Session Management**: Secure credential handling for private league access
- **Claude Desktop Integration**: Automatic server startup and management

## 🛠️ Available Tools

### Authentication
- `auth_store_credentials` - Store ESPN cookies for private league access
- `auth_logout` - Clear stored credentials

### League Information
- `league_get_info` - Basic league information
- `league_get_settings` - Detailed league configuration  
- `league_get_standings` - Current standings and rankings
- `league_get_scoreboard` - Weekly matchup overview

### Team Management
- `team_get_roster` - Current roster with player details
- `team_get_info` - Team metadata and performance stats
- `team_get_schedule` - Team schedule and results

### Player Analysis
- `player_get_stats` - Detailed player statistics
- `player_get_free_agents` - Available free agents with filtering
- `player_get_top_performers` - Top performing players by metric
- `player_search` - Search players by name
- `player_get_waiver_claims` - Recent waiver activity

### Transaction History
- `transaction_get_recent_activity` - All recent league activity
- `transaction_get_waiver_activity` - Waiver wire moves
- `transaction_get_trade_activity` - Trade activity
- `transaction_get_add_drop_activity` - Add/drop moves
- `transaction_get_team_transactions` - Team-specific transactions
- `transaction_get_player_history` - Player transaction history
- `transaction_get_lineup_activity` - Lineup changes
- `transaction_get_settings_activity` - League setting changes
- `transaction_get_keeper_activity` - Keeper/dynasty activity

### Draft Analysis
- `draft_get_results` - Complete draft results
- `draft_get_round` - Specific round picks
- `draft_get_team_picks` - Team's draft picks
- `draft_get_analysis` - Draft statistics and insights
- `draft_get_scarcity_analysis` - Position scarcity analysis

### Matchups & Scoring
- `matchup_get_week_results` - Weekly matchup results
- `matchup_get_boxscore` - Detailed matchup breakdown

### Metadata
- `metadata_get_positions` - Position mappings
- `metadata_get_stats` - Stat ID mappings
- `metadata_get_activity_types` - Activity type mappings

## 🔐 Authentication

For private leagues, you'll need ESPN cookies:

1. **Get your cookies**:
   - Log into ESPN Fantasy
   - Open browser developer tools (F12)
   - Go to Application/Storage → Cookies → espn.com
   - Copy `ESPN_S2` and `SWID` values

2. **Authenticate in Claude**:
   ```
   Use the auth_store_credentials tool with my ESPN_S2 and SWID cookies
   ```

## 📂 Project Structure

```
espn-api-util/
├── baseball_mcp/           # Main MCP server code
│   ├── baseball_mcp_server.py  # FastMCP server
│   ├── auth.py            # Authentication handling
│   ├── league.py          # League information tools
│   ├── roster.py          # Team and roster tools
│   ├── players.py         # Player analysis tools
│   ├── transactions.py    # Transaction history tools
│   ├── draft.py           # Draft analysis tools
│   ├── matchups.py        # Matchup and scoring tools
│   ├── metadata.py        # Data mappings and metadata
│   └── utils.py           # Utility functions
├── setup_claude_desktop.sh   # Claude Desktop configuration
├── start_baseball_mcp.sh     # Manual server startup
├── test_mcp_json.py          # JSON validation tests
└── QUICKSTART.md             # Detailed setup guide
```

## 🧪 Testing

```bash
# Test JSON output and MCP protocol compliance
python3 test_mcp_json.py

# Manual server testing
./start_baseball_mcp.sh
```

## 🔄 Configuration Files

### Claude Desktop
Configuration is automatically created at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude-desktop/claude_desktop_config.json`

### Server Configuration
- Automatically uses virtual environment Python
- Configures proper module paths
- Sets up environment variables for MCP protocol

## ⚠️ Known Limitations

- **Baseball Only**: Currently supports ESPN Fantasy Baseball only
- **Private Leagues**: Requires valid ESPN cookies for access
- **Session Based**: Credentials not persisted between server restarts
- **ESPN Dependency**: Limited by ESPN's API capabilities and rate limits

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Server not appearing in Claude Desktop | Run `./setup_claude_desktop.sh` and restart Claude Desktop |
| Authentication errors | Refresh ESPN cookies and re-authenticate |
| Python import errors | Ensure virtual environment is activated |
| JSON validation errors | Run `python3 test_mcp_json.py` for diagnosis |

## 📋 Requirements

- Python 3.12+
- ESPN Fantasy Baseball account
- Claude Desktop (for best experience)
- Virtual environment with dependencies installed

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [cwendt94/espn-api](https://github.com/cwendt94/espn-api) - ESPN Fantasy API Python wrapper
- [Anthropic MCP](https://github.com/anthropics/mcp) - Model Context Protocol framework
