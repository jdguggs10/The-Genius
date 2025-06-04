#!/usr/bin/env python3
"""
Health Check Script for PyBaseball MCP Server
Used to verify that the server is running correctly
"""
import os
import sys
import requests
import time

def check_server_health(url=None, max_retries=5, retry_delay=5):
    """Check if the PyBaseball MCP server is running and healthy"""
    if url is None:
        # Default to localhost for local testing
        port = os.environ.get("PORT", "8000")
        url = f"http://localhost:{port}/health"
    
    # For Render deployment
    if os.environ.get("RENDER") == "true":
        # Use the service URL provided by Render in environment variables
        render_url = os.environ.get("RENDER_EXTERNAL_URL")
        if render_url:
            url = f"{render_url}/health"
    
    print(f"Checking server health at: {url}")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server is healthy!")
                print(f"Status: {data.get('status')}")
                print(f"PyBaseball version: {data.get('version')}")
                return True
            else:
                print(f"❌ Server returned status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Connection error (attempt {attempt+1}/{max_retries}): {e}")
        
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    print("❌ Server health check failed after maximum retries")
    return False

if __name__ == "__main__":
    # Allow specifying a custom URL as command line argument
    url = sys.argv[1] if len(sys.argv) > 1 else None
    
    if check_server_health(url):
        sys.exit(0)
    else:
        sys.exit(1) 