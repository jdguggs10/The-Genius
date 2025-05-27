#!/usr/bin/env python3
"""
Quick test of web search functionality based on latest documentation
"""
import os
from openai import OpenAI

def test_web_search_simple():
    """Test web search with the exact format from documentation"""
    client = OpenAI()
    
    print("Testing web search with GPT-4.1...")
    try:
        # Test the exact format from the documentation
        response = client.responses.create(
            model="gpt-4.1",
            tools=[{"type": "web_search_preview"}],
            input="Who do the Yankees play today?",
        )
        
        print(f"✅ Success!")
        print(f"Response: {response.output_text[:200]}...")
        print(f"Full response structure: {type(response)}")
        
        # Check if we have additional outputs (web search results)
        if hasattr(response, 'output') and len(response.output) > 1:
            print(f"Number of outputs: {len(response.output)}")
            for i, output in enumerate(response.output):
                print(f"Output {i}: {type(output)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    test_web_search_simple() 