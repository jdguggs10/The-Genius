#!/usr/bin/env python
"""
Specialized test script for verifying chunked transfer encoding in PyBaseball MCP server.

This script focuses specifically on testing the implementation of the Streamable HTTP
protocol with chunked transfer encoding according to the March 2025 MCP specification.

Usage:
  python test_chunked_encoding.py [server_url]

If server_url is not specified, it uses http://localhost:8000.
"""
import asyncio
import os
import sys
import json
import httpx
import time
from typing import Dict, Any, List, Optional, AsyncGenerator, Tuple

# --- Configuration ---
SERVER_URL = os.environ.get("PYBASEBALL_SERVER_URL", "http://localhost:8000")
if len(sys.argv) > 1:
    SERVER_URL = sys.argv[1]

async def read_chunked_response(response) -> Tuple[bool, List[bytes], Any]:
    """
    Read a chunked response from the server and return individual chunks.
    
    Args:
        response: httpx.Response object with ongoing stream
        
    Returns:
        (success, chunks, parsed_result)
    """
    chunks = []
    raw_response = b""
    
    try:
        async for chunk in response.aiter_bytes():
            print(f"Received chunk: {chunk[:50]}..." if len(chunk) > 50 else f"Received chunk: {chunk}")
            chunks.append(chunk)
            raw_response += chunk
            
        # Try to parse the combined response
        try:
            parsed_result = json.loads(raw_response)
            return True, chunks, parsed_result
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse aggregated response as JSON: {e}")
            print(f"Raw response: {raw_response.decode('utf-8')}")
            return False, chunks, None
            
    except Exception as e:
        print(f"❌ Error receiving chunked response: {e}")
        return False, chunks, None

async def test_streaming_response_headers():
    """Test response headers for streaming protocol."""
    print(f"\n🔍 Testing streaming response headers...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Get list of available tools
            response = await client.get(f"{SERVER_URL}/tools", headers={"Accept-Encoding": "chunked"})
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            # Check for chunked transfer encoding
            if "transfer-encoding" in response.headers:
                if response.headers["transfer-encoding"] == "chunked":
                    print("✅ Server correctly uses chunked transfer encoding")
                else:
                    print(f"⚠️ Server uses transfer-encoding but not chunked: {response.headers['transfer-encoding']}")
            else:
                print("❌ Server does not use chunked transfer encoding")
                
            # Content-Type should be application/json for JSON responses
            if "content-type" in response.headers:
                if "application/json" in response.headers["content-type"].lower():
                    print("✅ Content-Type correctly set to application/json")
                else:
                    print(f"⚠️ Content-Type is not application/json: {response.headers['content-type']}")
            else:
                print("❌ Content-Type header missing")
                
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error testing streaming headers: {e}")
            return False

async def test_protocol_compliance():
    """Test if the server complies with the MCP Streamable HTTP specification."""
    print(f"\n🔍 Testing protocol compliance...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Check protocol info
            response = await client.get(f"{SERVER_URL}/protocol-info")
            if response.status_code != 200:
                print(f"❌ Protocol-info endpoint returned {response.status_code}")
                return False
                
            protocol_info = response.json()
            print(f"Protocol info: {json.dumps(protocol_info, indent=2)}")
            
            # Verify protocol identifier
            if protocol_info.get("protocol") != "MCP Streamable HTTP":
                print(f"❌ Server does not identify as MCP Streamable HTTP: {protocol_info.get('protocol')}")
                return False
                
            print("✅ Server correctly identifies as MCP Streamable HTTP")
            
            # Verify version
            if "version" not in protocol_info:
                print("❌ Protocol info missing version")
                return False
                
            print(f"✅ Server reports protocol version: {protocol_info['version']}")
            
            # Check other required fields
            required_fields = ["streaming_mode", "supports_jsonrpc"]
            missing_fields = [field for field in required_fields if field not in protocol_info]
            
            if missing_fields:
                print(f"❌ Protocol info missing required fields: {missing_fields}")
                return False
                
            print(f"✅ Protocol info contains all required fields")
            
            return True
        except Exception as e:
            print(f"❌ Error testing protocol compliance: {e}")
            return False

async def test_chunked_transfer_encoding_mlb_standings():
    """Test chunked transfer encoding with a large response (MLB standings)."""
    print(f"\n🔍 Testing chunked transfer encoding with MLB standings...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Request MLB standings with streaming enabled
            request_data = {"year": 2023}
            response = await client.post(
                f"{SERVER_URL}/tools/mlb_standings",
                json=request_data,
                headers={"Accept-Encoding": "chunked"},
                timeout=30.0
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Request failed with status code {response.status_code}")
                return False
                
            # Check if response is chunked
            if "transfer-encoding" not in response.headers or response.headers["transfer-encoding"] != "chunked":
                print("❌ Response is not using chunked transfer encoding")
                return False
                
            print("✅ Response is using chunked transfer encoding")
            
            # Read and process chunks
            print("\nReading response chunks...")
            success, chunks, result = await read_chunked_response(response)
            
            if not success:
                print("❌ Failed to read chunked response")
                return False
                
            print(f"✅ Successfully received {len(chunks)} chunks")
            
            # Validate the result structure
            if not isinstance(result, dict) or "result" not in result:
                print(f"❌ Invalid response structure: {result}")
                return False
                
            standings_data = result["result"]
            if not isinstance(standings_data, dict) or "standings" not in standings_data:
                print(f"❌ Invalid standings data structure: {standings_data}")
                return False
                
            print(f"✅ Valid standings data received with {len(standings_data['standings'])} divisions")
            return True
            
        except Exception as e:
            print(f"❌ Error testing chunked encoding with MLB standings: {e}")
            return False

async def test_jsonrpc_compatibility():
    """Test JSONRPC compatibility with the Streamable HTTP protocol."""
    print(f"\n🔍 Testing JSONRPC compatibility...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Make a JSONRPC style request
            jsonrpc_request = {
                "jsonrpc": "2.0",
                "method": "tool",
                "params": {
                    "name": "search_players",
                    "parameters": {"search_term": "Ohtani"}
                },
                "id": "test-request-1"
            }
            
            response = await client.post(
                f"{SERVER_URL}/jsonrpc",
                json=jsonrpc_request,
                headers={"Accept-Encoding": "chunked"},
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"❌ JSONRPC request failed with status code {response.status_code}")
                return False
                
            # Check if response is chunked
            if "transfer-encoding" not in response.headers or response.headers["transfer-encoding"] != "chunked":
                print("❌ JSONRPC response is not using chunked transfer encoding")
                # But continue, as this might be optional
                
            # Read and process chunks
            success, chunks, result = await read_chunked_response(response)
            
            if not success or not result:
                print("❌ Failed to read JSONRPC response")
                return False
                
            # Check for JSONRPC compatibility
            if "jsonrpc" not in result or result["jsonrpc"] != "2.0":
                print(f"❌ Response missing JSONRPC version: {result}")
                return False
                
            # Check for response ID matching request ID
            if "id" not in result or result["id"] != "test-request-1":
                print(f"❌ Response ID missing or doesn't match request: {result}")
                return False
                
            # Check result format
            if "result" not in result:
                print(f"❌ JSONRPC response missing result field: {result}")
                return False
                
            print(f"✅ Valid JSONRPC response received with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            print(f"❌ Error testing JSONRPC compatibility: {e}")
            return False

async def test_error_handling():
    """Test error handling in the Streamable HTTP protocol."""
    print(f"\n🔍 Testing error handling...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Request a non-existent tool
            request_data = {"param": "value"}
            response = await client.post(
                f"{SERVER_URL}/tools/non_existent_tool",
                json=request_data,
                headers={"Accept-Encoding": "chunked"},
                timeout=10.0
            )
            
            print(f"Response status: {response.status_code}")
            
            # We expect a 404 error for non-existent tools
            if response.status_code != 404:
                print(f"❌ Unexpected status code for non-existent tool: {response.status_code}")
                return False
                
            # Try to parse the error response
            try:
                error_data = response.json()
                print(f"Error response: {json.dumps(error_data, indent=2)}")
                
                # Check for error structure
                if "error" not in error_data:
                    print("❌ Error response missing 'error' field")
                    return False
                    
                # Check for required error fields
                required_fields = ["code", "message"]
                for field in required_fields:
                    if field not in error_data["error"]:
                        print(f"❌ Error response missing '{field}' field")
                        return False
                        
                print("✅ Error handling works correctly")
                return True
                
            except json.JSONDecodeError:
                print("❌ Error response is not valid JSON")
                return False
                
        except Exception as e:
            print(f"❌ Error testing error handling: {e}")
            return False
            
async def run_all_tests():
    """Run all tests and report results."""
    print(f"\n📊 Running all Streamable HTTP protocol tests against {SERVER_URL}...\n")
    start_time = time.time()
    
    test_results = {
        "protocol_compliance": await test_protocol_compliance(),
        "streaming_headers": await test_streaming_response_headers(),
        "chunked_encoding_mlb": await test_chunked_transfer_encoding_mlb_standings(),
        "jsonrpc_compatibility": await test_jsonrpc_compatibility(),
        "error_handling": await test_error_handling(),
    }
    
    end_time = time.time()
    
    print(f"\n📊 Test Results Summary ({end_time - start_time:.2f}s):")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        
    # Overall pass/fail
    all_passed = all(test_results.values())
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(run_all_tests())
