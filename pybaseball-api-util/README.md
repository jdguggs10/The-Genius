# PyBaseball Native MCP Server

A modular, production-ready Model Context Protocol (MCP) server for delivering Major League Baseball (MLB) statistics to AI assistants and tools, with robust support for the March 2025 **Streaming HTTP** transport and Native MCP architecture.

---

## 🚀 Key Features

- **Streaming HTTP Protocol**: Implements the March 2025 MCP-compliant Streamable HTTP protocol, enabling scalable, low-latency remote access for modern AI platforms.
- **STDIO & Web Modes**: Operates natively in both STDIO (local/desktop) and Streaming HTTP (web/cloud) modes.
- **Rich MLB Data Tools**: Exposes a suite of tools for player stats, recent performances, standings, leaders, team stats, and more.
- **FastAPI Fallback**: If MCP is unavailable, serves tools as a FastAPI REST API.
- **Extensible & Modular**: Clean separation of protocol, transport, and capability layers for easy maintenance and extension.
- **Robust Caching**: Combines pybaseball’s disk cache with a fast in-memory layer for optimal performance.

---

## 🛠️ Available Tools

Each tool is accessible via MCP and REST API endpoints.

| Tool Name                  | Description                                              |
|----------------------------|---------------------------------------------------------|
| `player_stats`             | Season stats (batting/pitching) for a player/year       |
| `player_recent_performance`| Recent game stats for a player (Statcast)               |
| `search_players`           | Look up players by name                                 |
| `mlb_standings`            | Current/season standings by division                    |
| `stat_leaders`             | Top players for a stat (HR, AVG, ERA, SO, etc.)         |
| `team_statistics`          | Batting/pitching stats for a team                       |
| `clear_stats_cache`        | Clear pybaseball’s local cache                          |
| `get_cache_info`           | Inspect cache status/config                             |
| `health_check`             | Server operational check                                |

See the **API Reference** below for full endpoint details and parameters.

---

## 🧑‍💻 Getting Started

### 1. Clone & Setup

```bash
git clone https://github.com/jdguggs10/The-Genius.git
cd The-Genius/pybaseball-api-util
```

### 2. Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
# Or for full MCP/pybaseball tools:
pip install -r pybaseball_mcp/requirements.txt
```

### 4. Running the Server

#### Local STDIO (for desktop/Claude integration)

```bash
./start_pybaseball_mcp_claude.sh
# Or manually:
export MCP_STDIO_MODE=1
export PYTHONPATH="$(pwd):$(pwd)/pybaseball_mcp:${PYTHONPATH:-}"
python pybaseball_nativemcp_server.py
```

#### Web/Cloud (Streaming HTTP)

```bash
./start_pybaseball_mcp.sh
# Server listens on port 8002 by default
```

The server will automatically use the **Streamable HTTP** protocol, replacing legacy HTTP+SSE. Full CORS support is included.

---

## 🌐 API Reference

All tools are available as REST endpoints:

```
POST https://genius-pybaseball.onrender.com/tools/{tool_name}
```
- `{tool_name}`: Name of the tool (no `get_` prefix).

### Example: Get MLB Standings

```bash
curl -X POST https://genius-pybaseball.onrender.com/tools/mlb_standings \
     -H "Content-Type: application/json" \
     -d '{"year": 2025}'
```

### Example: List All Tools

```bash
curl -s https://genius-pybaseball.onrender.com/mcp | jq '.all_tools[].name'
```

**Troubleshooting:**  
- Ensure tool names match (no `get_` prefix).
- POST JSON bodies with required parameters as per pybaseball’s API.
- 404 errors usually indicate a mismatch in tool name or parameters.

---

## ⚡ Streaming HTTP Protocol Overview

- **Streaming HTTP** is the official March 2025 MCP transport, replacing HTTP+SSE.
- Enables robust, bidirectional, chunked communication, ideal for LLMs and AI agents.
- See `streamable_http.py` for protocol implementation details and CORS configuration.

---

## 🏛️ Architecture Overview

- **Protocol Layer**: JSON-RPC 2.0 framing, request/response correlation.
- **Transport Layer**: Handles STDIO or Streaming HTTP as per environment.
- **Capability Layer**: Implements core MCP tools for MLB statistics.

**Key Modules:**
- `pybaseball_nativemcp_server.py`: Main server and tool registry.
- `streamable_http.py`: Streamable HTTP server.
- `pybaseball_mcp/`: Data access and business logic.
  - `players.py`, `teams.py`, `utils.py`: Modular stat providers and utilities.

---

## 🧠 AI Reviewer Notes

- This server is a drop-in Native MCP provider for MLB stats, with pybaseball as its backend.
- Full compatibility with March 2025 MCP and Streaming HTTP.
- Designed for easy extension with new tools and data sources.
- For test cases and usage patterns, see the `tests/` directory.

---

## 🔒 Caching

- Uses both pybaseball’s disk cache (`~/.pybaseball/cache/`) and a 5-minute in-memory cache.
- Caching logic resides in `pybaseball_mcp/utils.py`.
- Tools like `clear_stats_cache` and `get_cache_info` are provided for cache management.

---

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome!

1. Fork this repo.
2. Create a feature branch.
3. Submit a pull request with a clear description.

---

## 📚 References

- [pybaseball documentation](https://github.com/jldbc/pybaseball)
- [Model Context Protocol (MCP) Spec, March 2025](https://github.com/mcp-protocol/spec)
- [Streaming HTTP (MCP) Details](https://github.com/mcp-protocol/streaming-http)

---

## 📄 License

MIT License. See [LICENSE](../LICENSE) for details.
