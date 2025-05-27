#!/usr/bin/env python3
"""
Comprehensive test script to verify web search functionality
Tests both the OpenAI client and the main API endpoint
"""
import os
import sys
import json
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.openai_client import get_response

def test_openai_client():
    """Test the OpenAI client directly"""
    print("=" * 60)
    print("TESTING OPENAI CLIENT DIRECTLY")
    print("=" * 60)
    
    # Test 1: Without web search
    print("\n1. Testing without web search:")
    try:
        response, model = get_response(
            prompt="Who do the Yankees play today?",
            enable_web_search=False,
            model="gpt-4.1"
        )
        print(f"✅ Model: {model}")
        print(f"✅ Response: {response[:150]}...")
        print("✅ Non-web search request succeeded")
    except Exception as e:
        print(f"❌ Error without web search: {e}")
    
    # Test 2: With web search
    print("\n2. Testing with web search:")
    try:
        response, model = get_response(
            prompt="Who do the Yankees play today?",
            enable_web_search=True,
            model="gpt-4.1"
        )
        print(f"✅ Model: {model}")
        print(f"✅ Response: {response[:150]}...")
        print("✅ Web search request succeeded")
    except Exception as e:
        print(f"❌ Error with web search: {e}")

def test_api_endpoint():
    """Test the FastAPI endpoint"""
    print("\n" + "=" * 60)
    print("TESTING FASTAPI ENDPOINT")
    print("=" * 60)
    
    # Test local endpoint (adjust URL as needed)
    base_url = "http://localhost:8000"  # Change to your local development URL
    # base_url = "https://genius-backend-nhl3.onrender.com"  # Production URL
    
    # Test 1: Without web search
    print("\n1. Testing API without web search:")
    try:
        payload = {
            "conversation": [
                {
                    "role": "user",
                    "content": "Who do the Yankees play today?"
                }
            ],
            "enable_web_search": False
        }
        
        response = requests.post(
            f"{base_url}/advice",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Model: {data.get('model', 'Unknown')}")
            print(f"✅ Response: {data.get('reply', '')[:150]}...")
            print("✅ API non-web search request succeeded")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API without web search: {e}")
    
    # Test 2: With web search
    print("\n2. Testing API with web search:")
    try:
        payload = {
            "conversation": [
                {
                    "role": "user",
                    "content": "Who do the Yankees play today?"
                }
            ],
            "enable_web_search": True
        }
        
        response = requests.post(
            f"{base_url}/advice",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for web search
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Model: {data.get('model', 'Unknown')}")
            print(f"✅ Response: {data.get('reply', '')[:150]}...")
            print("✅ API web search request succeeded")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API with web search: {e}")

def test_frontend_logic():
    """Test the frontend logic for detecting web search keywords"""
    print("\n" + "=" * 60)
    print("TESTING FRONTEND LOGIC")
    print("=" * 60)
    
    def should_enable_web_search(input_text):
        """Simulate the frontend logic"""
        # Handle explicit "search:" prefix
        if input_text.lower().startswith('search:'):
            return True, input_text[7:].strip()
        
        # Auto-detect if web search should be enabled based on keywords
        web_search_keywords = [
            'stats', 'current', 'latest', 'today', 'now', 'recent', 'this week',
            'who plays', 'schedule', 'game', 'match', 'upcoming', 'when',
            'injury report', 'news', 'update', 'status'
        ]
        enable_search = any(keyword in input_text.lower() for keyword in web_search_keywords)
        return enable_search, input_text
    
    test_cases = [
        "search: who do the Yankees play today",
        "Who do the Yankees play today?",
        "What are the current NFL stats?",
        "Tell me about Patrick Mahomes",
        "When is the next game?",
        "Show me the latest injury report",
        "What happened in the game yesterday?"
    ]
    
    for test_case in test_cases:
        enable_search, clean_text = should_enable_web_search(test_case)
        status = "✅ ENABLED" if enable_search else "❌ DISABLED"
        print(f"{status}: '{test_case}' -> '{clean_text}'")

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE WEB SEARCH FUNCTIONALITY TEST")
    print("This test verifies the OpenAI client, API endpoint, and frontend logic")
    
    # Test the OpenAI client
    test_openai_client()
    
    # Test frontend logic
    test_frontend_logic()
    
    # Test API endpoint (optional - only if server is running)
    print("\n" + "=" * 60)
    print("API ENDPOINT TEST (optional)")
    print("Start your backend server first: python -m uvicorn app.main:app --reload")
    print("=" * 60)
    
    user_input = input("\nDo you want to test the API endpoint? (y/N): ").lower().strip()
    if user_input == 'y':
        test_api_endpoint()
    else:
        print("⏭️  Skipping API endpoint test")
    
    print("\n🎉 Test completed!") 