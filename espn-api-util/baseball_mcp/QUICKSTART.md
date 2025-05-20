# ESPN Fantasy Baseball MCP Server Quick Start Guide

## Starting the Baseball Server

### Option 1: Direct Command (Simplest)
1. Open terminal in Cursor (`Ctrl+` `)
2. Run: `cd espn-api-util && ./start_baseball_mcp.sh`

### Option 2: Update Workspace Configuration
If you want to use the existing workspace setup:
1. Edit `the-genius.code-workspace`
2. Update the tasks section to use the new script:
   ```json
   "tasks": {
     "version": "2.0.0",
     "tasks": [
       {
         "label": "start-baseball-server",
         "type": "shell",
         "command": "./start_baseball_mcp.sh",
         "options": {
           "cwd": "${workspaceFolder}/espn-api-util"
         },
         "presentation": {
           "reveal": "always",
           "panel": "new"
         }
       }
     ]
   }
   ```
3. Then use `Cmd+Shift+P` → "Tasks: Run Task" → "start-baseball-server"

## Configure Claude Desktop

### Step 1: Find Your Config File
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Step 2: Update the Configuration
Replace the content with (update the path to match your system):
```json
{
  "globalShortcut": "Ctrl+Space",
  "mcpServers": {
    "espn-baseball": {
      "command": "/Users/YOUR_USERNAME/Code/the-genius/espn-api-util/start_baseball_mcp.sh"
    }
  }
}
```

**To find your exact path:**
```bash
cd espn-api-util
pwd
# This will show your full path, then add /start_baseball_mcp.sh to the end
```

### Step 3: Restart Claude Desktop
1. **Completely quit** Claude Desktop (not just close the window)
2. **Restart** Claude Desktop
3. **Open a new chat**
4. Look for the ESPN baseball tools in the tools list

## Verify Everything Works

### Check File Structure
Your directory should look like this:
```
espn-api-util/
├── baseball_mcp/
│   ├── auth.py
│   ├── utils.py
│   ├── metadata.py
│   ├── league.py
│   ├── roster.py
│   ├── matchups.py
│   ├── transactions.py
│   ├── players.py
│   ├── draft.py
│   └── baseball_mcp_server.py
├── start_baseball_mcp.sh
└── (other files...)
```

### Test the Server
Run this command to test:
```bash
cd espn-api-util
./start_baseball_mcp.sh
```

You should see:
```
Checking dependencies...
Starting ESPN Fantasy Baseball MCP Server...
```

### Check Claude Desktop Tools
In Claude Desktop, you should see tools like:
- `auth_store_credentials`
- `league_get_info`
- `team_get_roster`
- `player_get_stats`
- `transaction_get_recent_activity`
- And 36 more baseball-specific tools!

## Troubleshooting

### Common Issues

**"Permission denied" when running script:**
```bash
chmod +x start_baseball_mcp.sh
```

**"No such file or directory" for baseball_mcp_server.py:**
- Make sure you created all 10 files in the `baseball_mcp` directory
- Check that `baseball_mcp_server.py` exists (not `main_server.py`)

**Files have wrong names (like auth_module.py):**
```bash
cd baseball_mcp
mv auth_module.py auth.py
mv utils_module.py utils.py
# (repeat for all files)
mv main_server.py baseball_mcp_server.py
```

**Import errors:**
- Make sure all 10 Python files are in the `baseball_mcp` directory
- Ensure each file contains the correct code
- Run `./setup.sh` again

**Claude Desktop doesn't show the tools:**
1. Check that your config file path is correct
2. Make sure you completely restarted Claude Desktop
3. Verify the startup script path in your config matches your actual file location

**Python version issues:**
- Make sure Python 3.12 is installed
- The script specifically calls `python3.12`

### Getting Help

If you run into issues:
1. Check that all files exist with correct names
2. Test the startup script manually in terminal
3. Verify your Claude Desktop config file path and content
4. Make sure the startup script is executable (`ls -la start_baseball_mcp.sh` should show `-rwx`)

## Quick Test

Once everything is set up, try this in Claude Desktop:
```
Use the league_get_info tool to get information about league 123456
```

If you see league information returned, congratulations! Your baseball MCP server is working perfectly. 🎉