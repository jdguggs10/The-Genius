# PyBaseball MCP Server

This server, `pybaseball_nativemcp_server.py`, provides Major League Baseball (MLB) statistics through the Model Context Protocol (MCP). It allows AI assistants and other tools to access real-time and historical baseball data using the powerful `pybaseball` library. It implements the Native MCP pattern with full support for Streamable HTTP transport as specified in the March 2025 MCP specification. The server can operate in both local STDIO mode for Claude Desktop integration and remote Streamable HTTP mode for web deployments.

## Features

The server exposes the following tools via MCP and REST API:

- **`player_stats`**: Get season statistics (batting or pitching) for a specific MLB player by name and year.
- **`player_recent_performance`**: Retrieve recent game performance for an MLB player over a specified number of days, utilizing Statcast data.
- **`search_players`**: Search for MLB players by full or partial name.
- **`mlb_standings`**: Get current MLB standings by division for a given year.
- **`stat_leaders`**: Find MLB leaders for a specific statistic (e.g., HR, AVG, ERA, SO) for a given year and player type (batting/pitching).
- **`team_statistics`**: Get aggregate batting and pitching statistics for an MLB team for a specified year.
- **`clear_stats_cache`**: Clear the `pybaseball` library's local cache to force fresh data retrieval.
- **`get_cache_info`**: Get information about the `pybaseball` cache status and location.
- **`health_check`**: A simple endpoint to confirm the server is operational.

## API Endpoints

All tools are exposed as REST API endpoints at:

```
POST https://genius-pybaseball.onrender.com/tools/{tool_name}
```

Where `{tool_name}` is the function name without any leading `get_` prefix. For example, `mlb_standings` instead of `get_mlb_standings`.

### Core MLB Data Endpoints

| Endpoint (tool_name) | Parameters | What it returns | Underlying pybaseball call |
|----------------------|------------|-----------------|----------------------------|
| `mlb_standings` | `{"year": 2025}` (year optional ⇒ current season) | Division and league standings for the season | `standings()` |
| `schedule_and_record` | `{"season": 2024, "team": "NYY"}` | Team-by-team game results & upcoming schedule | `schedule_and_record()` |
| `statcast` | `{"start_dt": "2025-04-01", "end_dt": "2025-04-07"}` | All Statcast pitches in the date window | `statcast()` |
| `statcast_pitcher` | `{"player_id": 518886, "start_dt": "2025-05-01", "end_dt": "2025-05-31"}` | Pitch-level Statcast for one pitcher | `statcast_pitcher()` |
| `statcast_batter` | `{"player_id": 664058, "start_dt": "2025-05-01", "end_dt": "2025-05-31"}` | Batter-level Statcast | `statcast_batter()` |
| `pitching_stats` | `{"start_season": 2024, "end_season": 2024}` | Season-level FanGraphs pitching metrics | `pitching_stats()` |
| `batting_stats` | `{"start_season": 2024, "end_season": 2024}` | Season-level FanGraphs batting metrics | `batting_stats()` |
| `playerid_lookup` | `{"last_name": "Ohtani", "first_name": "Shohei"}` | MLBAM, FanGraphs, B-Ref IDs, etc. | `playerid_lookup()` |
| `team_ids` | `{}` | Master lookup of MLB team IDs & abbreviations | `team_ids()` |

### API Usage Examples

#### List Available Tools
```bash
curl -s https://genius-pybaseball.onrender.com/mcp | jq '.all_tools[].name'
```

#### Get Current Standings
```bash
curl -X POST https://genius-pybaseball.onrender.com/tools/mlb_standings \
     -H "Content-Type: application/json" \
     -d '{}'
```

#### Get Pitcher Statcast Data
```bash
curl -X POST https://genius-pybaseball.onrender.com/tools/statcast_pitcher \
     -H "Content-Type: application/json" \
     -d '{"player_id": 477132, "start_dt":"2025-05-01", "end_dt":"2025-05-31"}'
```

### Troubleshooting

If a call returns 404, check that:
1. You dropped any `get_` prefix.
2. You're posting to `/tools/{name}`, not `/tools/get_{name}`.
3. The JSON body keys match the parameter names in pybaseball.

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

The server supports multiple transport protocols as defined in the March 2025 MCP specification. It can run in either STDIO mode for local development and Claude Desktop integration, or in Streamable HTTP mode for web deployments.

### Local Development with STDIO Mode

**Using the provided script (recommended):**

The `start_pybaseball_mcp_claude.sh` script handles activating the virtual environment, setting necessary environment variables (`MCP_STDIO_MODE=1`, `PYTHONPATH`), and running `pybaseball_nativemcp_server.py`.

```bash
./start_pybaseball_mcp_claude.sh
```

**Manual Execution:**

```bash
# Ensure venv is activated
source venv/bin/activate

# Set environment variables
export MCP_STDIO_MODE=1
export PYTHONPATH=\"$(pwd):$(pwd)/pybaseball_mcp:${PYTHONPATH:-}\"

# Run the server
python pybaseball_nativemcp_server.py
```

### Web Deployment with Streamable HTTP

To run the server with Streamable HTTP transport (replacing the deprecated HTTP+SSE from previous versions):

```bash
# Standard web deployment
./start_pybaseball_mcp.sh
```

This starts the server on port 8002 (or as specified by the `PORT` environment variable). The server implements the Streamable HTTP protocol as specified in the March 2025 MCP specification, making it compatible with the latest OpenAI and Microsoft AI systems.

## Core Logic and Architecture

The server follows the three-layer Native MCP architecture as recommended in the March 2025 specification:

1. **Protocol Layer**: Handles JSON-RPC 2.0 message framing and request/response linking
2. **Transport Layer**: Manages communication through either STDIO or Streamable HTTP
3. **Capability Interfaces**: Provides the core MCP primitives (Tools) for MLB statistics

The implementation is modular with clear separation of concerns:

- **Main Server**: `pybaseball_nativemcp_server.py` - Contains the Native MCP Server implementation with tool definitions
- **Transport Layer**: `streamable_http.py` - Implements the Streamable HTTP protocol with proper CORS configuration
- **Data Access Layer**: The core data fetching logic resides in the `pybaseball_mcp` subdirectory:
  - `pybaseball_mcp/players.py`: Handles player-specific data (seasonal stats, recent performance, search)
  - `pybaseball_mcp/teams.py`: Handles team data (standings, league leaders, team stats)
  - `pybaseball_mcp/utils.py`: Provides caching utilities, data formatting, and other helpers

This structure follows the recommended patterns for Native MCP servers, making it highly compatible with both local and remote AI systems.

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