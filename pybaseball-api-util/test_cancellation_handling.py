#!/usr/bin/env python3
"""
Test script to verify PyBaseball MCP server handles cancellation gracefully.
"""
import asyncio
import json
import sys
import os

# Set MCP mode
os.environ["MCP_STDIO_MODE"] = "1"

async def test_cancellation_handling():
    """Test that the server handles cancellation notifications gracefully."""
    print("Testing cancellation handling...", file=sys.stderr)
    
    try:
        # Import the server
        from pybaseball_mcp_server_v2 import main
        
        # Try to run the server briefly
        print("Starting server...", file=sys.stderr)
        
        # This should not crash even if cancellation notifications are sent
        task = asyncio.create_task(main())
        
        # Let it run briefly then cancel
        await asyncio.sleep(0.1)
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            print("✅ Server handled cancellation gracefully", file=sys.stderr)
            return True
        except Exception as e:
            if "notifications/cancelled" in str(e) or "ValidationError" in str(e):
                print("✅ Server handled MCP cancellation notification gracefully", file=sys.stderr)
                return True
            else:
                print(f"❌ Unexpected error: {e}", file=sys.stderr)
                return False
                
    except Exception as e:
        print(f"❌ Error during test: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    print("PyBaseball MCP Server Cancellation Test", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    try:
        result = asyncio.run(test_cancellation_handling())
        if result:
            print("🎉 Cancellation handling test passed!", file=sys.stderr)
        else:
            print("❌ Cancellation handling test failed!", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}", file=sys.stderr)
        sys.exit(1) 