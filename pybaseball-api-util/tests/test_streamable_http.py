#!/usr/bin/env python
"""
Test script for verifying PyBaseball MCP server using the Streamable HTTP protocol
This script tests the March 2025 MCP specification compatibility.
"""
import httpx
import asyncio
import json
import sys
import os
from typing import Dict, Any, List, Optional

SERVER_URL = os.environ.get("PYBASEBALL_SERVER_URL", "http://localhost:8000")

async def test_http_endpoints():
    """Test basic HTTP endpoints."""
    print(f"\n🔍 Testing HTTP endpoints at {SERVER_URL}...")
    
    async with httpx.AsyncClient() as client:
        # Test root endpoint
        response = await client.get(f"{SERVER_URL}/")
        print(f"Root endpoint: {response.status_code} - {response.json() if response.status_code == 200 else response.text}")
        
        # Test health endpoint
        response = await client.get(f"{SERVER_URL}/health")
        print(f"Health endpoint: {response.status_code} - {response.json() if response.status_code == 200 else response.text}")
        
        # Test tools listing endpoint
        response = await client.get(f"{SERVER_URL}/tools")
        if response.status_code == 200:
            try:
                tools_data = response.json()
                tools_preview = str(tools_data)[:100] + "..." if len(str(tools_data)) > 100 else str(tools_data)
                print(f"Tools endpoint: {response.status_code} - {tools_preview}")
            except Exception as e:
                print(f"Tools endpoint: {response.status_code} - Error parsing response: {e} - Raw: {response.text[:100]}...")

async def test_tool_invocation():
    """Test tool invocation via Streamable HTTP."""
    print(f"\n🛠️ Testing tool invocation via Streamable HTTP...")
    
    async with httpx.AsyncClient() as client:
        # Test search_players tool
        search_data = {"search_term": "Ohtani"}
        response = await client.post(
            f"{SERVER_URL}/tools/search_players", 
            json=search_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ search_players tool invocation successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ search_players tool invocation failed: {response.status_code} - {response.text}")
            return False

async def test_header_compatibility():
    """Test if the server supports the required headers for Streamable HTTP."""
    print(f"\n🔄 Testing Streamable HTTP header compatibility...")
    
    # Test the protocol-info endpoint first to verify if server supports the spec
    async with httpx.AsyncClient() as client:
        # Get protocol info
        response = await client.get(f"{SERVER_URL}/protocol-info")
        if response.status_code == 200:
            print(f"Protocol info: {response.json()}")
        else:
            print(f"Protocol info endpoint not found: {response.status_code}")
        
        # Headers required by March 2025 spec
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Test with a tool endpoint
        response = await client.post(
            f"{SERVER_URL}/tools/health_check", 
            headers=headers,
            json={}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Check for streaming capability headers in response
        if response.status_code == 200:
            # Transfer-Encoding is set by the server, not always visible in response headers
            # Check for proper response format instead
            transfer_encoding = response.headers.get("transfer-encoding")
            if transfer_encoding and "chunked" in transfer_encoding:
                print("✅ Server supports Streamable HTTP (Transfer-Encoding: chunked)")
                return True
            else:
                # Try checking the protocol-info endpoint
                print("⚠️ Transfer-Encoding header not found, checking if server declares Streamable HTTP support")
                try:
                    protocol_resp = await client.get(f"{SERVER_URL}/protocol-info")
                    if protocol_resp.status_code == 200:
                        protocol_info = protocol_resp.json()
                        if protocol_info.get("protocol") == "MCP Streamable HTTP":
                            print(f"✅ Server declares Streamable HTTP support in protocol-info")
                            return True
                except:
                    pass
                    
                print("⚠️ Server responded but may not be fully compliant with Streamable HTTP spec")
                return False
        else:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            return False

async def main():
    """Run all tests."""
    print("🧪 Testing PyBaseball MCP Server Streamable HTTP Implementation")
    print("============================================================")
    
    success = True
    
    # Test basic HTTP endpoints
    await test_http_endpoints()
    
    # Test tool invocation
    tool_result = await test_tool_invocation()
    success = success and tool_result
    
    # Test Streamable HTTP compatibility
    http_compat = await test_header_compatibility()
    success = success and http_compat
    
    # Print summary
    print("\n============================================================")
    print(f"Test results: {'✅ PASSED' if success else '❌ SOME TESTS FAILED'}")
    print(f"Server URL: {SERVER_URL}")
    
    return 0 if success else 1

if __name__ == "__main__":
    # Check if server URL was provided as argument
    if len(sys.argv) > 1:
        SERVER_URL = sys.argv[1]
        
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
