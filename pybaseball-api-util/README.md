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
    The primary list of dependencies for this utility is located in `pybaseball-api-util/pybaseball_mcp/requirements.txt`.
    ```bash
    pip install -r pybaseball_mcp/requirements.txt
    ```
    Ensure that `mcp>=1.5.0` is installed as part of these dependencies for full MCP functionality.

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

## 🤖 AI Reviewer Notes

For AI agents reviewing this utility, the following points are key for understanding its design and operation:

-   **MCP Server for MLB Statistics**: This utility acts as a Model Context Protocol (MCP) server, providing tools to access Major League Baseball statistics. Its primary data source is the `pybaseball` Python library.
-   **Key Server Script**: The main server script is `pybaseball_mcp_server_v2.py`. This script initializes the MCP tools and handles communication.
-   **Core Logic Modules**: The data fetching and processing logic is predominantly located within the `pybaseball_mcp` directory, specifically in:
    -   `players.py`: For player-related statistics and searches.
    -   `teams.py`: For team-related statistics and standings.
    -   `utils.py`: Contains helper functions, data formatting, and critically, the configuration and management of `pybaseball`'s caching features.
-   **Caching Strategy**: The `pybaseball` library's own caching mechanism is a vital aspect of this utility, configured in `pybaseball_mcp/utils.py`. This helps in reducing redundant API calls and speeding up responses. An additional short-term in-memory cache is also used by the server for its processed results. Understanding the cache behavior (location: `~/.pybaseball/cache/`, expiry) is important for data freshness considerations.
-   **Operating Mode (MCP STDIO)**: When launched using the `start_pybaseball_mcp_claude.sh` script, the server operates in MCP STDIO mode. This script sets essential environment variables like `MCP_STDIO_MODE=1` and modifies `PYTHONPATH` to ensure correct module resolution.
-   **Fallback to FastAPI**: If MCP libraries are not detected (e.g., `mcp` package not installed or `MCP_STDIO_MODE` not set), the server is designed to fall back to running as a FastAPI-based REST API on port 8002 by default.
-   **`pybaseball` Library Familiarity**: A good understanding of the `pybaseball` library's functions and data structures will be highly beneficial when analyzing the tool implementations, as this utility serves as a wrapper around it.
-   **Tool Definitions**: The available MCP tools (like `player_stats`, `mlb_standings`, etc.) are defined within `pybaseball_mcp_server_v2.py`, mapping to functions in the core logic modules.