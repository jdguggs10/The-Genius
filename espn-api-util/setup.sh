#!/usr/bin/env bash

# Exit on error
set -e

echo "Setting up ESPN API Server environment..."

# Check if Python 3.12 is available
if ! command -v python3.12 &> /dev/null; then
    echo "Error: Python 3.12 is required but not found"
    echo "Please install Python 3.12 and try again"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3.12 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -e .

# Create .vscode directory if it doesn't exist
mkdir -p .vscode

# Create/update settings.json
echo "Configuring VS Code/Cursor settings..."
cat > .vscode/settings.json << EOL
{
    "python.defaultInterpreterPath": "\${workspaceFolder}/.venv/bin/python3",
    "python.analysis.extraPaths": [
        "\${workspaceFolder}/.venv/lib/python3.12/site-packages"
    ],
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true
}
EOL

echo "Setup complete! You can now run ./start_mcp.sh to start the server." 