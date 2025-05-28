# PyBaseball MCP Server

This server, `pybaseball_mcp_server_v2.py`, provides Major League Baseball (MLB) statistics through the Model Context Protocol (MCP). It allows AI assistants and other tools to access real-time and historical baseball data using the powerful `pybaseball` library. If MCP libraries are unavailable, it can fall back to a FastAPI-based REST API.

## Features

The server exposes the following tools via MCP:

- **`player_stats`**: Get season statistics (batting or pitching) for a specific MLB player by name and year.
- **`player_recent_performance`**: Retrieve recent game performance for an MLB player over a specified number of days, utilizing Statcast data.
- **`search_players`**: Search for MLB players by full or partial name.
- **`mlb_standings`**: Get current MLB standings by division for a given year.
- **`stat_leaders`**: Find MLB leaders for a specific statistic (e.g., HR, AVG, ERA, SO) for a given year and player type (batting/pitching).
- **`team_statistics`**: Get aggregate batting and pitching statistics for an MLB team for a specified year.
- **`clear_stats_cache`**: Clear the `pybaseball` library's local cache to force fresh data retrieval.
- **`get_cache_info`**: Get information about the `pybaseball` cache status and location.
- **`health_check`**: A simple endpoint to confirm the server is operational.

## Caching

The server leverages `pybaseball`'s built-in caching mechanism to improve performance and reduce redundant data fetching.
- The cache is typically stored in `~/.pybaseball/cache/`.
- Cache expiry is configured (e.g., to 24 hours).
The server also employs a small, short-lived (5 minutes TTL) in-memory cache for its own processed results.

## Setup and Installation

1.  **Clone the repository (if you haven't already).**
2.  **Navigate to the `pybaseball-api-util` directory:**
    ```bash
    cd pybaseball-api-util
    ```
3.  **Create and activate a Python virtual environment:**
    It's recommended to create it in the current directory named `venv`, as expected by the startup scripts.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Install dependencies:**
    The primary list of dependencies is in `pybaseball-api-util/pybaseball_mcp/requirements.txt`. It's advisable to consolidate this into the top-level `requirements.txt`. For now, you can install using the more comprehensive list:
    ```bash
    pip install -r pybaseball_mcp/requirements.txt 
    # Or, once consolidated:
    # pip install -r requirements.txt
    ```
    Ensure you have `mcp>=1.5.0` for full functionality.

## Running the Server

The server is designed to be run in MCP STDIO mode, especially when used with tools like Claude Desktop.

**Using the provided script (recommended):**

The `start_pybaseball_mcp_claude.sh` script handles activating the virtual environment, setting necessary environment variables (`MCP_STDIO_MODE=1`, `PYTHONPATH`), and running `pybaseball_mcp_server_v2.py`.

```bash
./start_pybaseball_mcp_claude.sh
```

**Manual Execution (for development/debugging):**

If you need to run it manually:

```bash
# Ensure venv is activated
source venv/bin/activate

# Set environment variables
export MCP_STDIO_MODE=1
export PYTHONPATH=\"$(pwd):$(pwd)/pybaseball_mcp:${PYTHONPATH:-}\" # Ensure both current dir and pybaseball_mcp are on path

# Run the server
python pybaseball_mcp_server_v2.py
```

If MCP libraries are not found, the server will attempt to start a FastAPI server on port 8002 (or as specified by the `PORT` environment variable).

## Core Logic

The core data fetching and processing logic resides in the `pybaseball_mcp` subdirectory:
- `pybaseball_mcp/players.py`: Handles player-specific data (seasonal stats, recent performance, search).
- `pybaseball_mcp/teams.py`: Handles team data (standings, league leaders, team stats).
- `pybaseball_mcp/utils.py`: Provides caching utilities, data formatting, and other helpers, including `pybaseball` cache configuration.

This structure modularizes the data access layer from the server implementation.

## Quick Start

### 1. Install Dependencies

```bash
cd pybaseball-api-util
pip install -r requirements.txt