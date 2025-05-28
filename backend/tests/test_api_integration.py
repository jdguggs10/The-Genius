import pytest
import requests
import os

# It's good practice to get the base URL from an environment variable
# or a config file for integration tests.
BASE_URL = os.getenv("TEST_API_BASE_URL", "http://localhost:8000") 

@pytest.mark.integration # Example marker, requires pytest configuration
def test_api_advice_without_web_search():
    """Test the /advice API endpoint without web search."""
    payload = {
        "conversation": [
            {"role": "user", "content": "Who won the world series in 2020?"}
        ],
        "enable_web_search": False
        # Model not specified, will use backend default
    }
    
    response = requests.post(
        f"{BASE_URL}/advice",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30  # Standard timeout
    )
    
    assert response.status_code == 200, f"API Error: {response.status_code} - {response.text}"
    data = response.json()
    assert "reply" in data
    assert "model" in data
    # Add more specific assertions about the reply if possible, 
    # though exact AI output is hard to pin down.
    # For example, if web search is false, the answer shouldn't be too current if the question implies it
    print(f"API Response (no web search): {data.get('reply')[:100]}...")

@pytest.mark.integration # Example marker
def test_api_advice_with_web_search():
    """Test the /advice API endpoint with web search enabled."""
    payload = {
        "conversation": [
            {"role": "user", "content": "Who do the Los Angeles Lakers play next?"} 
        ],
        "enable_web_search": True
        # Model not specified, will use backend default
    }
    
    response = requests.post(
        f"{BASE_URL}/advice",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60  # Longer timeout for potential web search
    )
    
    assert response.status_code == 200, f"API Error: {response.status_code} - {response.text}"
    data = response.json()
    assert "reply" in data
    assert "model" in data
    # If web search is true, you might expect a more current or specific answer
    print(f"API Response (web search): {data.get('reply')[:100]}...")

# Note: To run these tests, the FastAPI server must be running at BASE_URL.
# You might manage this by:
# 1. Starting the server manually before running pytest.
# 2. Using a pytest fixture to start/stop the server (more advanced).
# 3. Running these tests as part of a CI pipeline that deploys the app first. 