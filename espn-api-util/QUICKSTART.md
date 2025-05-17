# ESPN API Server Quick Start Guide

## Option 1: Using the Workspace File (Recommended)
1. Double-click `the-genius.code-workspace`
2. Once Cursor opens, press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
3. Type "Run Task" and select "Tasks: Run Task"
4. Select "start-espn-server"

## Option 2: Using Launch Configuration
1. Open the project in Cursor
2. Press `F5` or click the "Run and Debug" button in the sidebar
3. Select "Start ESPN API Server" from the dropdown

## Manual Start (Fallback)
If the automated methods don't work:
1. Open terminal in Cursor (`Ctrl+` `)
2. Run: `cd espn-api-util && ./start_mcp.sh`

## Troubleshooting
- If you see "Permission denied": Run `chmod +x start_mcp.sh`
- If Python 3.12 isn't found: Make sure Python 3.12 is installed on your system
- If dependencies fail to install: Check your internet connection and try again 