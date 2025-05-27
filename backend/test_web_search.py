#!/usr/bin/env python3
"""
Test script to verify web search functionality
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.openai_client import get_response

def test_web_search():
    """Test the web search functionality"""
    print("Testing web search functionality...")
    
    # Test without web search
    print("\n1. Testing without web search:")
    try:
        response, model = get_response(
            prompt="Who do the Yankees play today?",
            enable_web_search=False
        )
        print(f"Model: {model}")
        print(f"Response: {response[:200]}...")
    except Exception as e:
        print(f"Error without web search: {e}")
    
    # Test with web search
    print("\n2. Testing with web search:")
    try:
        response, model = get_response(
            prompt="Who do the Yankees play today?",
            enable_web_search=True
        )
        print(f"Model: {model}")
        print(f"Response: {response[:200]}...")
    except Exception as e:
        print(f"Error with web search: {e}")

if __name__ == "__main__":
    test_web_search() 