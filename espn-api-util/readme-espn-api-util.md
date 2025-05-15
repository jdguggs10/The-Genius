# ESPN Fantasy Sports API Integration

## Overview

This repository contains a Model Context Protocol (MCP) server that serves as a bridge between language models like Claude and the ESPN Fantasy Sports API. As of May 2025, this codebase provides tools for seamlessly accessing and retrieving fantasy sports data through conversational interfaces.

The server wraps the ESPN Fantasy API Python package to provide structured access to fantasy sports data across multiple sports (currently football and baseball). This allows AI assistants to retrieve information about leagues, teams, players, and matchups in a standardized format.

## What's New

> **Multi-Sport Support:** The ESPN API utility now supports both fantasy football and baseball leagues, with the architecture in place to extend to other ESPN fantasy sports in the future.

## Technical Architecture

### Core Components

1. **FastMCP Server**: The main server that exposes endpoints for AI assistants to query fantasy sports data
2. **ESPN API Wrapper**: Uses the `espn-api` Python package to interact with ESPN's Fantasy Sports platforms
3. **Session Management**: Handles authentication credentials for accessing private leagues

### Key Files

- `espn_fantasy_server.py`: The main server implementation containing all API tools
- `pyproject.toml`: Project configuration and dependencies
- `start_mcp.sh`: Bash script to start the server locally

## Authentication System

The server includes a secure credential management system that:

- Stores ESPN authentication credentials (ESPN_S2 and SWID cookies) for the current session only
- Does not persist credentials between sessions for security
- Provides a logout function to clear credentials

These credentials are required to access private leagues. Public leagues can be accessed without authentication.

## Available API Tools

The server exposes the following tools through the MCP interface:

### 1. `authenticate`
Stores ESPN authentication credentials for accessing private leagues.

**Parameters:**
- `espn_s2`: The ESPN_S2 cookie value from an ESPN account
- `swid`: The SWID cookie value from an ESPN account

### 2. `get_league_info`
Retrieves basic information about a fantasy sports league.

**Parameters:**
- `league_id`: The ESPN fantasy league ID (integer)
- `year`: Year for historical data (defaults to current season)
- `sport`: Sport type ("football" or "baseball", defaults to "football")

**Returns:**
- League name
- Current week
- NFL week (football only)
- Team count
- List of teams
- Scoring type

### 3. `get_team_roster`
Gets a team's current roster with player details.

**Parameters:**
- `league_id`: The ESPN fantasy league ID
- `team_id`: The team ID in the league (usually 1-12)
- `year`: Year for historical data (defaults to current season)
- `sport`: Sport type ("football" or "baseball", defaults to "football")

**Returns:**
- Team name
- Owner information
- Wins/losses record
- Detailed roster including:
  - Player names
  - Positions
  - Pro teams
  - Points
  - Projected points
  - Statistics

### 4. `get_team_info`
Retrieves general information about a team including performance metrics.

**Parameters:**
- `league_id`: The ESPN fantasy league ID
- `team_id`: The team ID in the league (usually 1-12)
- `year`: Year for historical data (defaults to current season)
- `sport`: Sport type ("football" or "baseball", defaults to "football")

**Returns:**
- Team name
- Owner information
- Win/loss/tie record
- Points for/against
- Acquisition/drop/trade counts
- Playoff percentage
- Final standing
- Game outcomes

### 5. `get_player_stats`
Gets detailed statistics for a specific player.

**Parameters:**
- `league_id`: The ESPN fantasy league ID
- `player_name`: Name of the player to search for
- `year`: Year for historical data (defaults to current season)
- `sport`: Sport type ("football" or "baseball", defaults to "football")

**Returns:**
- Player name
- Position
- Pro team
- Total points
- Projected points
- Detailed statistics
- Injury status

### 6. `get_league_standings`
Retrieves current standings and rankings for a league.

**Parameters:**
- `league_id`: The ESPN fantasy league ID
- `year`: Year for historical data (defaults to current season)
- `sport`: Sport type ("football" or "baseball", defaults to "football")

**Returns:**
- Ranked list of teams with:
  - Team name
  - Owner information
  - Win/loss record
  - Points for/against
  - Roto points (for rotisserie baseball leagues)

### 7. `get_matchup_info`
Gets matchup information for a specific week.

**Parameters:**
- `league_id`: The ESPN fantasy league ID
- `week`: The week number (if not provided, uses current week)
- `year`: Year for historical data (defaults to current season)
- `sport`: Sport type ("football" or "baseball", defaults to "football")

**Returns:**
- List of matchups with:
  - Home team name
  - Home score
  - Away team name
  - Away score
  - Winner (HOME/AWAY/TIE)

### 8. `logout`
Clears stored authentication credentials for the current session.

## Integration with Claude Desktop

The server is designed to work with Claude Desktop through the MCP protocol:

1. **Configuration**: Update the Claude Desktop config file to include a reference to the MCP server:
   - MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Add the server to the `mcpServers` section

2. **Server Arguments**:
   - `--directory`: Absolute path to the ESPN fantasy server directory
   - `espn_fantasy_server.py`: The main server script to run

Example configuration:
```json
{
  "mcpServers": {
    "espn-fantasy": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/directory",
        "run",
        "espn_fantasy_server.py"
        ]
      }
    } 
  }
```

## Installation

### Prerequisites

- Python 3.12 or higher
- `uv` package manager
- [Claude Desktop](https://claude.ai/download) for the best experience

### Setup

1. Clone this repository
2. Install dependencies:
   ```
   uv pip install -e .
   ```
3. Update your Claude Desktop configuration as described above
4. Start the server:
   ```
   ./start_mcp.sh
   ```
   or
   ```
   uv run espn_fantasy_server.py
   ```

## Usage Examples

### Football Example

```
Get information about a football league with ID 123456:

get_league_info(league_id=123456, sport="football")
```

### Baseball Example

```
Get team roster for a baseball league:

get_team_roster(league_id=81134470, team_id=1, year=2025, sport="baseball")
```

### Private League Example

```
First authenticate:
authenticate(espn_s2="AEBxxxxxxxxxxx", swid="{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}")

Then access the private league:
get_league_standings(league_id=123456, sport="football")
```

## Sport-Specific Considerations

### Football

- Season typically runs from September to February
- Default year calculation is current year if after July, previous year if before July
- Contains NFL week information
- Regular season typically spans 17-18 weeks

### Baseball

- Season typically runs from March/April to October within the same calendar year
- Default year is almost always the current calendar year
- Supports both head-to-head and rotisserie scoring formats
- For rotisserie leagues, standings are determined by category points rather than wins/losses

## Technical Implementation Details

### Data Handling

- League objects are cached by ID, year, and sport for better performance
- Credentials are stored separately per session for security
- Robust error handling for API requests with meaningful error messages

### Known Limitations

- The server only supports ESPN Fantasy Football and Baseball (not other ESPN fantasy sports yet)
- Private leagues require valid ESPN_S2 and SWID cookies for access
- Week numbers are limited by the sport's regular season length
- Some player statistics might be limited based on ESPN's API

## Integration with FantasyAI Platform

This ESPN API utility is part of the larger FantasyAI platform, which includes:

- **AI-powered advice engine** - Using OpenAI's GPT-4.1 to analyze player stats
- **RESTful backend API** - Handling requests between frontends and AI/data services
- **iOS application** - Mobile interface for interacting with the AI assistant
- **Web application** - (Planned) Browser-based interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

[cwendt94/espn-api](https://github.com/cwendt94/espn-api) for the Python wrapper around the ESPN Fantasy API
