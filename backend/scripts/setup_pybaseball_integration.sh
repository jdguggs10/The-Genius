#!/bin/bash
# Setup script for PyBaseball integration

echo "🔧 Setting up PyBaseball integration..."

# Check if .env file exists
if [ -f "../.env" ]; then
    # Check if PYBASEBALL_SERVICE_URL is already in .env
    if grep -q "PYBASEBALL_SERVICE_URL" "../.env"; then
        # Update the URL if it exists
        sed -i '' 's|PYBASEBALL_SERVICE_URL=.*|PYBASEBALL_SERVICE_URL=https://genius-pybaseball.onrender.com|g' "../.env"
        echo "✅ Updated PYBASEBALL_SERVICE_URL in .env"
    else
        # Add PYBASEBALL_SERVICE_URL to .env
        echo -e "\n# PyBaseball Service URL\nPYBASEBALL_SERVICE_URL=https://genius-pybaseball.onrender.com" >> "../.env"
        echo "✅ Added PYBASEBALL_SERVICE_URL to .env"
    fi
else
    # Create .env file with PYBASEBALL_SERVICE_URL
    echo -e "# PyBaseball Service URL\nPYBASEBALL_SERVICE_URL=https://genius-pybaseball.onrender.com" > "../.env"
    echo "✅ Created .env file with PYBASEBALL_SERVICE_URL"
    echo "⚠️ Please add your OPENAI_API_KEY to the .env file"
fi

# Install httpx if not already installed
if ! pip freeze | grep -q "httpx"; then
    echo "📦 Installing httpx..."
    pip install httpx
    echo "✅ httpx installed"
else
    echo "✅ httpx already installed"
fi

echo "🧪 Running PyBaseball integration test..."
python test_pybaseball_integration.py

echo -e "\n✨ Setup complete! Your backend is now configured to use PyBaseball data."
echo "📝 Note: If you use Poetry for dependency management, run 'poetry add httpx' manually." 