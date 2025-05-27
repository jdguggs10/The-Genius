@echo off
echo Starting PyBaseball MCP Server...

REM Navigate to the script directory
cd /d %~dp0

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set default port if not specified  
if "%PORT%"=="" set PORT=8002

REM Run the server
echo Starting server on port %PORT%...
python pybaseball_mcp_server.py