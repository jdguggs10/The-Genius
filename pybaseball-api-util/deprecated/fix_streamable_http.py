#!/usr/bin/env python3
"""
Fix script for the Streamable HTTP implementation in PyBaseball MCP server.
This script applies the necessary fixes to make the server compliant with
the March 2025 MCP specification.
"""
import os
import sys
import json
import re

# Paths to files to modify
STREAMABLE_HTTP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streamable_http.py")
SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pybaseball_nativemcp_server.py")

def fix_protocol_info():
    """Fix the protocol-info endpoint in streamable_http.py."""
    with open(STREAMABLE_HTTP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add missing required fields
    pattern = re.compile(r'@app\.get\("/protocol-info"\)[^{]*?{([^}]*?)}', re.DOTALL)
    match = pattern.search(content)
    if match:
        protocol_info_content = match.group(1)
        if 'streaming_mode' not in protocol_info_content and 'supports_jsonrpc' not in protocol_info_content:
            # Add new fields before the closing brace
            updated_content = content.replace(
                '"oauth_supported": True',
                '"oauth_supported": True,\n            "streaming_mode": True,\n            "supports_jsonrpc": True'
            )
            
            with open(STREAMABLE_HTTP_PATH, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print("✅ Fixed protocol-info endpoint")
        else:
            print("✓ Protocol-info already has required fields")
    else:
        print("❌ Could not find protocol-info endpoint")

def fix_mlb_standings_response():
    """Fix the MLB standings response format in the tools endpoints."""
    with open(STREAMABLE_HTTP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find both occurrences of the tool response handling
    # First occurrence (in /tools/{tool_name})
    tools_pattern = re.compile(r'@app\.post\("/tools/\{tool_name\}"[^{]*?stream_generator\(\):.*?elif hasattr\(result\[0\], \'text\'\):.*?async for chunk in streaming_json_response\((.*?)\):.*?yield chunk', re.DOTALL)
    match = tools_pattern.search(content)
    
    if match:
        response_format = match.group(1)
        if '{"data": result[0].text}' in response_format:
            # Replace with proper handling for MLB standings
            updated_content = content.replace(
                'elif hasattr(result[0], \'text\'):  # TextContent\n                    async for chunk in streaming_json_response({"data": result[0].text}):\n                        yield chunk',
                '''elif hasattr(result[0], 'text'):  # TextContent
                    # Special handling for MLB standings which needs to be properly parsed
                    if tool_name == "mlb_standings" and result[0].text:
                        try:
                            # Try to parse the text as JSON to properly structure the response
                            parsed_data = json.loads(result[0].text)
                            async for chunk in streaming_json_response(parsed_data):
                                yield chunk
                        except json.JSONDecodeError:
                            # If parsing fails, send as regular text
                            async for chunk in streaming_json_response(result[0].text):
                                yield chunk
                    else:
                        # Regular text content
                        async for chunk in streaming_json_response(result[0].text):
                            yield chunk'''
            )
            
            # Also replace the second occurrence in the legacy endpoint 
            updated_content = updated_content.replace(
                'elif hasattr(result[0], \'text\'):  # TextContent\n                    async for chunk in streaming_json_response({"data": result[0].text}):\n                        yield chunk',
                '''elif hasattr(result[0], 'text'):  # TextContent
                    # Special handling for MLB standings which needs to be properly parsed
                    if tool_name == "mlb_standings" and result[0].text:
                        try:
                            # Try to parse the text as JSON to properly structure the response
                            parsed_data = json.loads(result[0].text)
                            async for chunk in streaming_json_response(parsed_data):
                                yield chunk
                        except json.JSONDecodeError:
                            # If parsing fails, send as regular text
                            async for chunk in streaming_json_response(result[0].text):
                                yield chunk
                    else:
                        # Regular text content
                        async for chunk in streaming_json_response(result[0].text):
                            yield chunk'''
            )
            
            with open(STREAMABLE_HTTP_PATH, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print("✅ Fixed MLB standings response format")
        else:
            print("✓ MLB standings response format already updated")
    else:
        print("❌ Could not find tool response handling code")

def add_error_handling_for_nonexistent_tools():
    """Add proper error handling for nonexistent tools."""
    with open(SERVER_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the error handling section and ensure it returns 404 for non-existent tools
    if "TOOL_NOT_FOUND" in content and "return [ErrorData(error={" in content:
        # Check if we're correctly returning error code
        if '"code": ErrorCode.TOOL_NOT_FOUND.value' not in content:
            # Add proper error code handling
            updated_content = content.replace(
                'return [ErrorData(error={"message": f"Tool {name} not found"})]',
                'return [ErrorData(error={"code": ErrorCode.TOOL_NOT_FOUND.value, "message": f"Tool {name} not found"})]'
            )
            
            with open(SERVER_PATH, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print("✅ Fixed error handling for nonexistent tools")
        else:
            print("✓ Error handling for nonexistent tools already updated")
    else:
        print("❌ Could not find error handling section")

def implement_jsonrpc_endpoint():
    """Check for JSONRPC endpoint implementation."""
    with open(STREAMABLE_HTTP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if '@app.post("/jsonrpc"' in content:
        print("✓ JSONRPC endpoint already implemented")
    else:
        print("❌ JSONRPC endpoint not implemented - please add it manually")

def main():
    """Apply all fixes."""
    print("🔧 Applying fixes to Streamable HTTP implementation...")
    
    # Fix protocol-info endpoint
    fix_protocol_info()
    
    # Fix MLB standings response format
    fix_mlb_standings_response()
    
    # Add proper error handling
    add_error_handling_for_nonexistent_tools()
    
    # Check for JSONRPC endpoint
    implement_jsonrpc_endpoint()
    
    print("🔧 Fixes applied. Please restart the server to apply changes.")

if __name__ == "__main__":
    main()
