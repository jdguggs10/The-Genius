#!/usr/bin/env python3
"""
Tests for metadata.py functions, ensuring their output is JSON serializable.
"""

import unittest
import json
import sys
import os

# Adjust path to import from baseball_mcp
BASEBALL_MCP_DIR = os.path.join(os.path.dirname(__file__), '..') # Goes up one level to baseball_mcp dir
sys.path.insert(0, BASEBALL_MCP_DIR)

from metadata import get_positions, get_stat_map, get_activity_types

class TestMetadataJSONSerialization(unittest.TestCase):

    def test_get_positions_json_serializable(self):
        """Test that get_positions() output is JSON serializable."""
        positions = get_positions()
        try:
            json_output = json.dumps(positions)
            self.assertIsNotNone(json_output, "JSON output should not be None")
            # Optionally, check if the deserialized version matches the original if complex
            # deserialized_positions = json.loads(json_output)
            # self.assertEqual(positions, deserialized_positions)
        except TypeError as e:
            self.fail(f"get_positions() output is not JSON serializable: {e}")
        print("✅ get_positions() is JSON serializable")

    def test_get_stat_map_json_serializable(self):
        """Test that get_stat_map() output is JSON serializable."""
        stats = get_stat_map()
        try:
            json_output = json.dumps(stats)
            self.assertIsNotNone(json_output, "JSON output should not be None")
        except TypeError as e:
            self.fail(f"get_stat_map() output is not JSON serializable: {e}")
        print("✅ get_stat_map() is JSON serializable")

    def test_get_activity_types_json_serializable(self):
        """Test that get_activity_types() output is JSON serializable."""
        activities = get_activity_types()
        try:
            json_output = json.dumps(activities)
            self.assertIsNotNone(json_output, "JSON output should not be None")
        except TypeError as e:
            self.fail(f"get_activity_types() output is not JSON serializable: {e}")
        print("✅ get_activity_types() is JSON serializable")

if __name__ == "__main__":
    # You can run this file directly using: python -m unittest espn-api-util/baseball_mcp/tests/test_metadata.py
    # Or simply: python espn-api-util/baseball_mcp/tests/test_metadata.py if PYTHONPATH is set up
    print(f"Running tests from: {os.path.abspath(__file__)}")
    print(f"Python sys.path includes: {BASEBALL_MCP_DIR}")
    unittest.main() 