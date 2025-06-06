#!/usr/bin/env python
"""
Backend service verification script for Streamable HTTP protocol.

This script tests the backend service's ability to handle streamed responses
from the PyBaseball MCP server according to the March 2025 specification.

Usage:
  python test_backend_streaming.py [server_url]

If server_url is not specified, it uses the PYBASEBALL_SERVICE_URL environment variable
or falls back to the default URL (http://localhost:8000).
"""
import asyncio
import os
import sys
import json
import time
import httpx
from typing import Dict, Any, List, Optional, Tuple, AsyncGenerator

# Add the parent directory to sys.path to allow importing from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from app.services.pybaseball_service import PyBaseballService
    BACKEND_AVAILABLE = True
except ImportError:
    print("⚠️ Backend service module not available, running direct HTTP tests only")
    BACKEND_AVAILABLE = False

# --- Configuration ---
SERVER_URL = os.environ.get("PYBASEBALL_SERVICE_URL", "http://localhost:8000")
if len(sys.argv) > 1:
    SERVER_URL = sys.argv[1]

class StreamingPyBaseballService:
    """Enhanced service for PyBaseball API with explicit streaming support."""
    
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv("PYBASEBALL_SERVICE_URL", "http://localhost:8000")
        self.timeout = 30  # seconds
        print(f"Streaming PyBaseball service initialized with URL: {self.base_url}")
    
    async def call_with_streaming(self, tool_name: str, params: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        """Call a PyBaseball tool with streaming and yield chunks as they arrive."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/tools/{tool_name}",
                json=params,
                headers={"Accept-Encoding": "chunked"},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Stream the response chunks
            async for chunk in response.aiter_bytes():
                yield chunk
    
    async def stream_mlb_standings(self, year: Optional[int] = None) -> Tuple[bool, Any]:
        """
        Stream MLB standings with chunked transfer encoding.
        
        Returns:
            Tuple of (success, result)
        """
        payload = {}
        if year is not None:
            payload["year"] = year
            
        chunks = []
        raw_response = b""
        
        try:
            async for chunk in self.call_with_streaming("mlb_standings", payload):
                print(f"Received chunk: {len(chunk)} bytes")
                chunks.append(chunk)
                raw_response += chunk
                
            # Try to parse the combined response
            try:
                parsed_result = json.loads(raw_response)
                return True, parsed_result
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse aggregated response: {e}")
                print(f"Raw response: {raw_response.decode('utf-8')}")
                return False, None
                
        except Exception as e:
            print(f"❌ Error streaming MLB standings: {e}")
            return False, None

async def test_backend_service():
    """Test the backend PyBaseballService with the streaming server."""
    if not BACKEND_AVAILABLE:
        print("⚠️ Skipping backend service test as import failed")
        return False
        
    print(f"\n🔍 Testing backend PyBaseballService with {SERVER_URL}...")
    
    try:
        # Create service instance
        service = PyBaseballService()
        service.base_url = SERVER_URL
        
        # Test MLB standings endpoint
        print("Testing MLB standings...")
        start_time = time.time()
        standings = await service.get_mlb_standings(year=2023)
        end_time = time.time()
        
        print(f"Request completed in {end_time - start_time:.2f}s")
        
        if not standings or not isinstance(standings, dict):
            print(f"❌ Invalid response: {standings}")
            return False
            
        # Check for divisions in the response
        if "standings" not in standings:
            print(f"❌ Missing 'standings' in response: {standings}")
            return False
            
        print(f"✅ Successfully retrieved standings with {len(standings['standings'])} divisions")
        return True
        
    except Exception as e:
        print(f"❌ Error in backend service test: {e}")
        return False

async def test_direct_streaming():
    """Test direct streaming with the enhanced service."""
    print(f"\n🔍 Testing direct streaming with {SERVER_URL}...")
    
    try:
        # Create streaming service instance
        service = StreamingPyBaseballService(base_url=SERVER_URL)
        
        # Test MLB standings endpoint with streaming
        print("Testing MLB standings with streaming...")
        start_time = time.time()
        success, result = await service.stream_mlb_standings(year=2023)
        end_time = time.time()
        
        print(f"Streaming request completed in {end_time - start_time:.2f}s")
        
        if not success:
            print(f"❌ Streaming failed")
            return False
            
        # Check the structure of the result
        if "result" not in result:
            print(f"❌ Missing 'result' field in response: {result}")
            return False
            
        standings_data = result["result"]
        
        if "standings" not in standings_data:
            print(f"❌ Missing 'standings' in data: {standings_data}")
            return False
            
        print(f"✅ Successfully streamed standings with {len(standings_data['standings'])} divisions")
        return True
        
    except Exception as e:
        print(f"❌ Error in direct streaming test: {e}")
        return False

async def test_raw_http_client():
    """Test raw HTTP client with chunked encoding explicit handling."""
    print(f"\n🔍 Testing raw HTTP client with {SERVER_URL}...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Make request with explicit chunked encoding header
            response = await client.post(
                f"{SERVER_URL}/tools/mlb_standings",
                json={"year": 2023},
                headers={"Accept-Encoding": "chunked"},
                timeout=30.0
            )
            
            print(f"Status code: {response.status_code}")
            print(f"Headers: {response.headers}")
            
            # Check if we got chunked encoding
            if "transfer-encoding" in response.headers and response.headers["transfer-encoding"] == "chunked":
                print("✅ Response is using chunked transfer encoding")
            else:
                print("⚠️ Response is not using chunked transfer encoding")
                
            # Read chunks explicitly
            print("Reading response chunks...")
            chunks = []
            raw_data = b""
            
            async for chunk in response.aiter_bytes():
                chunk_preview = chunk[:50] + (b'...' if len(chunk) > 50 else b'')
                print(f"Chunk ({len(chunk)} bytes): {chunk_preview}")
                chunks.append(chunk)
                raw_data += chunk
                
            print(f"Received {len(chunks)} chunks, total size: {len(raw_data)} bytes")
            
            try:
                result = json.loads(raw_data)
                # Check for valid structure
                if isinstance(result, dict) and "result" in result:
                    print("✅ Successfully parsed chunked response")
                    return True
                else:
                    print(f"❌ Invalid response structure: {result}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse response: {e}")
                print(f"Raw data: {raw_data.decode('utf-8')[:200]}...")
                return False
                
    except Exception as e:
        print(f"❌ Error in raw HTTP client test: {e}")
        return False

async def test_protocol_version_compatibility():
    """Test protocol version compatibility between backend and server."""
    print(f"\n🔍 Testing protocol version compatibility...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Query the protocol info
            response = await client.get(f"{SERVER_URL}/protocol-info")
            
            if response.status_code != 200:
                print(f"❌ Failed to get protocol info: {response.status_code}")
                return False
                
            protocol_info = response.json()
            
            # Check protocol identifier
            if protocol_info.get("protocol") != "MCP Streamable HTTP":
                print(f"❌ Server protocol mismatch: {protocol_info.get('protocol')}")
                return False
                
            # Check protocol version
            version = protocol_info.get("version")
            if not version:
                print("❌ Missing protocol version")
                return False
            
            print(f"Server protocol: {protocol_info.get('protocol')} {version}")
            print(f"March 2025 specification expected")
            
            # Check streaming support
            if not protocol_info.get("streaming_mode", False):
                print("⚠️ Server reports streaming_mode=False, chunked encoding may not work")
            else:
                print("✅ Server reports streaming_mode=True")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing protocol compatibility: {e}")
        return False
            
async def run_all_tests():
    """Run all backend integration tests and report results."""
    print(f"\n📊 Running backend streaming tests against {SERVER_URL}...\n")
    start_time = time.time()
    
    test_results = {
        "protocol_version": await test_protocol_version_compatibility(),
        "raw_http_client": await test_raw_http_client(),
        "direct_streaming": await test_direct_streaming()
    }
    
    # Only run backend test if available
    if BACKEND_AVAILABLE:
        test_results["backend_service"] = await test_backend_service()
    else:
        test_results["backend_service"] = None
    
    end_time = time.time()
    
    print(f"\n📊 Test Results Summary ({end_time - start_time:.2f}s):")
    
    for test_name, result in test_results.items():
        if result is None:
            status = "⚠️ SKIP"
        else:
            status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        
    # Overall pass/fail (ignoring skipped tests)
    actual_results = [result for result in test_results.values() if result is not None]
    all_passed = all(actual_results)
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(run_all_tests())
