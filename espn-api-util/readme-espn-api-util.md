# ESPN Fantasy Baseball MCP Server

A Model Context Protocol (MCP) server that provides seamless access to ESPN Fantasy Baseball data through Claude Desktop and other MCP-compatible AI assistants. This README provides essential information for an AI assistant to understand and utilize this tool.

## 🚀 Getting Started

1.  **Initial Environment Setup**:
    Navigate to the `espn-api-util` directory and run the main setup script. This will create a virtual environment, install dependencies, and configure VS Code/Cursor settings.
    ```bash
    cd espn-api-util  # If not already in this directory
    ./setup.sh
    ```

2.  **Manual Server Start (Optional)**:
    To run the server manually (e.g., for testing outside Claude Desktop):
    ```bash
    ./start_baseball_mcp.sh 
    ```
    This script activates the virtual environment and starts the `baseball_mcp_server.py`.

3.  **Configure Claude Desktop (Automatic Startup)**:
    To integrate with Claude Desktop for automatic server startup:
    ```bash
    ./setup_claude_desktop.sh
    ```
    This script configures Claude Desktop to use `./start_claude_mcp.sh` for launching the server.

4.  **Restart Claude Desktop**:
    Quit and relaunch Claude Desktop. The `espn-baseball` server should now start automatically and be available.

### ✅ Verification

-   The server should appear in Claude Desktop as `espn-baseball`.
-   Verify functionality by asking the AI assistant to:
    -   `Use the metadata_get_positions tool to show available positions`
    -   `Get league info for league ID [your-league-id]` (Replace `[your-league-id]` with an actual ID if testing private leagues after authentication).

### 🔄 When to Re-run Setup Scripts

-   Run `./setup.sh` again if dependencies in `pyproject.toml` change or if the Python version for the project changes.
-   Run `./setup_claude_desktop.sh` again if the project directory is moved or if Claude Desktop is reinstalled.

## 🔐 Authentication (For Private Leagues)

Accessing private league data requires ESPN cookies (`ESPN_S2` and `SWID`).

1.  **Obtain Cookies**:
    -   Log into your ESPN Fantasy Baseball league page.
    -   Open browser developer tools (e.g., F12 or Right-click -> Inspect).
    -   Navigate to the "Application" (or "Storage") tab.
    -   Under "Cookies", find `espn.com`.
    -   Copy the `value` for `ESPN_S2` and `SWID`.
2.  **Store Credentials via AI Assistant**:
    Instruct the AI assistant:
    ```
    Use the auth_store_credentials tool with my ESPN_S2 and SWID cookies. Provide the actual cookie values when prompted or directly in the instruction if your assistant supports it.
    ```
    Example: `Use the auth_store_credentials tool. My ESPN_S2 is 'your_espn_s2_value' and my SWID is 'your_swid_value'.`

**Note**: Credentials are session-based and not persisted between server restarts. You will need to re-authenticate if the server restarts or if your cookies expire.

## 🛠️ Available Tools

This server provides the following tools, callable by an AI assistant:

### Authentication
-   `auth_store_credentials`: Stores ESPN `ESPN_S2` and `SWID` cookies for private league access.
    -   *Parameters*: `espn_s2_cookie (str)`, `swid_cookie (str)`
-   `auth_logout`: Clears stored ESPN credentials.

### League Information
-   `league_get_info`: Retrieves basic information for the configured league.
-   `league_get_settings`: Fetches detailed league configuration and settings.
-   `league_get_standings`: Gets current league standings and team rankings.
-   `league_get_scoreboard`: Provides an overview of the current or a specified week's matchups.
    -   *Optional Parameters*: `week (int)`

### Team Management
-   `team_get_roster`: Retrieves a team's current roster with player details.
    -   *Optional Parameters*: `team_id (int)` (Defaults to user's primary team if authenticated)
-   `team_get_info`: Gets metadata and performance statistics for a specific team.
    -   *Required Parameters*: `team_id (int)`
-   `team_get_schedule`: Fetches a team's schedule and past results.
    -   *Optional Parameters*: `team_id (int)`

### Player Analysis
-   `player_get_stats`: Provides detailed statistics for a specific player.
    -   *Required Parameters*: `player_id (int)` or `player_name (str)`
    -   *Optional Parameters*: `projection_season (int)` (for projected stats)
-   `player_get_free_agents`: Lists available free agents, with filtering options.
    -   *Optional Parameters*: `position (str)`, `sort_by (str)`, `limit (int)`
-   `player_get_top_performers`: Identifies top-performing players based on specified metrics.
    -   *Optional Parameters*: `position (str)`, `stat (str)`, `limit (int)`
-   `player_search`: Searches for players by name.
    -   *Required Parameters*: `query (str)`
-   `player_get_waiver_claims`: Shows recent waiver wire claims and activity.

### Transaction History
-   `transaction_get_recent_activity`: Fetches all recent league transactions.
    -   *Optional Parameters*: `limit (int)`, `activity_type (str)`
-   `transaction_get_waiver_activity`: Retrieves waiver wire specific moves.
-   `transaction_get_trade_activity`: Shows trade-related activity.
-   `transaction_get_add_drop_activity`: Lists add/drop transactions.
-   `transaction_get_team_transactions`: Fetches transactions for a specific team.
    -   *Required Parameters*: `team_id (int)`
-   `transaction_get_player_history`: Gets the transaction history for a specific player.
    -   *Required Parameters*: `player_id (int)` or `player_name (str)`
-   `transaction_get_lineup_activity`: Shows recent lineup changes.
-   `transaction_get_settings_activity`: Lists changes to league settings.
-   `transaction_get_keeper_activity`: Retrieves keeper or dynasty league related activity.

### Draft Analysis
-   `draft_get_results`: Provides complete draft results for the league.
-   `draft_get_round`: Fetches picks from a specific round of the draft.
    -   *Required Parameters*: `round_num (int)`
-   `draft_get_team_picks`: Shows a specific team's draft picks.
    -   *Required Parameters*: `team_id (int)`
-   `draft_get_analysis`: Offers draft statistics and insights.
-   `draft_get_scarcity_analysis`: Analyzes position scarcity based on the draft.

### Matchups & Scoring
-   `matchup_get_week_results`: Gets the results for all matchups in a given week.
    -   *Required Parameters*: `week (int)`
-   `matchup_get_boxscore`: Provides a detailed breakdown of a specific matchup.
    -   *Required Parameters*: `team_id_1 (int)`, `team_id_2 (int)`, `week (int)`

### Metadata
-   `metadata_get_positions`: Returns mappings for player positions.
-   `metadata_get_stats`: Provides mappings for statistical categories (stat IDs).
-   `metadata_get_activity_types`: Lists mappings for different league activity types.

## 📂 Project Structure (Key Files for AI)

The most relevant components for an AI assistant are:

```
espn-api-util/
├── baseball_mcp/               # Core MCP server logic for baseball
│   ├── baseball_mcp_server.py  # Main FastMCP server application for baseball
│   ├── auth.py                # Handles ESPN authentication for the baseball server
│   ├── league.py              # Implements league information tools
│   ├── ... (other .py files for different tool categories) ...
│   └── tests/                 # Unit/integration tests for baseball_mcp modules
│       ├── test_utils.py
│       ├── test_metadata.py
│       └── test_transactions.py
├── .venv/                      # Python virtual environment (created by setup.sh)
├── setup.sh                    # Primary script for initial environment setup (venv, dependencies, VSCode config)
├── start_baseball_mcp.sh       # Manual startup script for the baseball MCP server.
├── start_claude_mcp.sh         # Wrapper script used by Claude Desktop to start the baseball server.
├── setup_claude_desktop.sh     # Script to configure Claude Desktop integration.
├── diagnose_mcp.py             # Diagnostic script for checking environment and setup.
├── test_server_protocol.py     # Tests basic MCP server protocol compliance.
├── espn_fantasy_server.py      # Alternative generic server (football/baseball, not primary for Claude setup)
├── start_mcp.sh                # Manual startup script for espn_fantasy_server.py.
└── pyproject.toml              # Project metadata and dependencies.
```

## 🧪 Testing and Debugging

-   **Environment Diagnostics**:
    Run this to check Python version, file presence, dependencies, and basic server startup.
    ```bash
    ./diagnose_mcp.py
    ```
-   **MCP Server Protocol Test**:
    Tests the `baseball_mcp_server.py` for basic MCP initialization compliance.
    ```bash
    ./test_server_protocol.py
    ```
-   **Unit/Integration Tests**:
    The primary automated tests for the `baseball_mcp` module logic are located in `espn-api-util/baseball_mcp/tests/`. Run them using a test runner like `pytest` from the `espn-api-util` directory, or execute individual test files directly.
    ```bash
    # Example: running all tests with pytest (if installed and configured)
    pytest
    # Example: running specific test file
    python -m unittest espn-api-util/baseball_mcp/tests/test_utils.py
    ```
-   **Manual Server Start for Debugging**:
    ```bash
    ./start_baseball_mcp.sh
    ```
    This starts the `baseball_mcp_server.py` directly, allowing you to see console output.

## ⚙️ Configuration Details

-   **Claude Desktop Configuration File**:
    -   macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
    -   Linux: `~/.config/claude-desktop/claude_desktop_config.json`
    The `./setup_claude_desktop.sh` script modifies this file to point to `./start_claude_mcp.sh`.
-   **Server Environment**:
    -   The server runs using the Python interpreter from the `./.venv/` virtual environment, created by `./setup.sh`.
    -   The startup scripts (`./start_baseball_mcp.sh`, `./start_claude_mcp.sh`) handle activation of this virtual environment.

## ⚠️ Key Limitations & Considerations for AI

-   **Baseball Focus**: This MCP server is specifically for ESPN Fantasy Baseball.
-   **Private League Access**: Requires `ESPN_S2` and `SWID` cookies for private leagues. The AI should guide the user through `auth_store_credentials` if access is denied.
-   **Session-Based Authentication**: Credentials are not persisted across server restarts. The AI should remind users to re-authenticate if needed.
-   **ESPN API Dependency**: Functionality is subject to the capabilities and rate limits of the underlying ESPN API. The AI should be mindful of making too many rapid requests.
-   **Error Handling**: The AI should be prepared to handle errors from the tools, which may indicate issues like invalid league IDs, player not found, or authentication problems.

## 🔧 Troubleshooting Tips for AI Guidance

| Issue Reported by User | AI Guidance/Troubleshooting Steps                                                                                                |
|------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| "Server not in Claude" | "Please ensure you have run `./setup.sh` and then `./setup_claude_desktop.sh` from the `espn-api-util` directory. After that, restart Claude Desktop completely." |
| "Authentication failed"  | "Let's try re-authenticating. Please provide your `ESPN_S2` and `SWID` cookies again using the `auth_store_credentials` tool." |
| "Tool X isn't working"   | "Could you confirm the parameters you used? For example, `player_get_stats` needs a `player_id` or `player_name`. Also, ensure the server is running and you are authenticated if it's a private league." |
| "Python import error" or "Command not found" | "This usually means the environment isn't set up correctly. Please run `./setup.sh` from the `espn-api-util` directory. If you're trying to run a server manually, ensure you're using the provided start scripts like `./start_baseball_mcp.sh` which activate the virtual environment." |

## 📋 Requirements

-   Python 3.12+
-   An active ESPN Fantasy Baseball account (for private league testing).
-   Claude Desktop or another MCP-compatible AI assistant.
-   Dependencies installed via `pip install -e .` within the virtual environment.

## 📄 License

MIT License. See the `LICENSE` file for full details.

## 🙏 Acknowledgments

-   Built upon the [cwendt94/espn-api](https://github.com/cwendt94/espn-api) Python wrapper for the ESPN Fantasy API.
-   Uses the [Anthropic MCP](https://github.com/anthropics/mcp) framework for AI tool integration.
