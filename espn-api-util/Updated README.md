# ESPN Fantasy Football API Integration

## Overview

This repository contains a Model Context Protocol (MCP) server that serves as a bridge between language models like Claude and the ESPN Fantasy Football API. As of May 13, 2025, this codebase provides tools for seamlessly accessing and retrieving fantasy football data through conversational interfaces.

The server is built on the FastMCP framework and wraps the ESPN Fantasy API Python package to provide structured access to fantasy football data. This allows AI assistants to retrieve information about leagues, teams, players, and matchups in a standardized format.

## Technical Architecture

### Core Components

1. **FastMCP Server**: The main server that exposes endpoints for AI assistants to query fantasy football data.
2. **ESPN API Wrapper**: Uses the `espn-api` Python package to interact with ESPN's Fantasy Football platform.
3. **Session Management**: Handles authentication credentials for accessing private leagues.

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
Retrieves basic information about a fantasy football league.

**Parameters:**
- `league_id`: The ESPN fantasy football league ID (integer)
- `year`: Year for historical data (defaults to current season)

**Returns:**
- League name
- Current week
- NFL week
- Team count
- List of teams
- Scoring type

### 3. `get_team_roster`
Gets a team's current roster with player details.

**Parameters:**
- `league_id`: The ESPN fantasy football league ID
- `team_id`: The team ID in the league (usually 1-12)
- `year`: Year for historical data (defaults to current season)

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
- `league_id`: The ESPN fantasy football league ID
- `team_id`: The team ID in the league (usually 1-12)
- `year`: Year for historical data (defaults to current season)

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
- `league_id`: The ESPN fantasy football league ID
- `player_name`: Name of the player to search for
- `year`: Year for historical data (defaults to current season)

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
- `league_id`: The ESPN fantasy football league ID
- `year`: Year for historical data (defaults to current season)

**Returns:**
- Ranked list of teams with:
  - Team name
  - Owner information
  - Win/loss record
  - Points for/against

### 7. `get_matchup_info`
Gets matchup information for a specific week.

**Parameters:**
- `league_id`: The ESPN fantasy football league ID
- `week`: The week number (if not provided, uses current week)
- `year`: Year for historical data (defaults to current season)

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

## Technical Implementation Details

### Data Handling

- League objects are cached by ID and year for better performance
- Credentials are stored separately per session for security
- Robust error handling for API requests with meaningful error messages

### Session Management

- Credentials are maintained only for the current session
- The API includes methods to store, retrieve, and clear credentials
- Team IDs are 1-based in the ESPN API

## Frontend Integration Considerations

When building a frontend to interface with this API:

1. **Authentication Flow**:
   - Implement a secure way to collect ESPN_S2 and SWID cookies from users
   - Use the authenticate tool before accessing private leagues
   - Include a logout function to clear credentials

2. **League Selection**:
   - Allow users to input their league ID
   - Consider saving frequently used league IDs

3. **Data Visualization**:
   - Build components to display team rosters, player stats, and matchups
   - Consider UI elements for comparing players or teams
   - Implement standings tables and matchup cards

4. **Error Handling**:
   - Handle authentication errors for private leagues
   - Provide appropriate messaging when players aren't found
   - Validate team ID ranges based on league size

5. **Historical Data**:
   - Include year selection for historical data access
   - Consider showing year-over-year trends for teams or players

## Dependencies

- Python 3.12 or higher
- `espn-api` package (v0.44.1 or higher)
- `mcp[cli]` package (v1.5.0 or higher)
- `uv` package manager for dependency management

## Limitations

- The server only supports ESPN Fantasy Football (not other ESPN fantasy sports)
- Private leagues require valid ESPN_S2 and SWID cookies for access
- Week numbers are limited to 1-17 for most leagues
- Some player statistics might be limited based on ESPN's API