#!/usr/bin/env python3
"""
Test script for Step 6: Schema-First Response Validation
Tests the schema validation service with various inputs.
"""

import json
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.schema_validator import schema_validator

def test_valid_response():
    """Test validation with a valid response."""
    print("Testing valid response...")
    
    valid_response = {
        "main_advice": "Start Josh Allen over Patrick Mahomes this week",
        "reasoning": "Allen has a better matchup against a weaker defense",
        "confidence_score": 0.8,
        "alternatives": ["Consider Lamar Jackson as well"],
        "model_identifier": "gpt-4.1"
    }
    
    is_valid, error = schema_validator.validate_json(valid_response)
    print(f"Valid response test: {'PASS' if is_valid else 'FAIL'}")
    if error:
        print(f"Error: {error}")
    print()

def test_minimal_response():
    """Test validation with minimal required fields only."""
    print("Testing minimal response...")
    
    minimal_response = {
        "main_advice": "Start Josh Allen"
    }
    
    is_valid, error = schema_validator.validate_json(minimal_response)
    print(f"Minimal response test: {'PASS' if is_valid else 'FAIL'}")
    if error:
        print(f"Error: {error}")
    print()

def test_invalid_response():
    """Test validation with invalid response (missing required field)."""
    print("Testing invalid response...")
    
    invalid_response = {
        "reasoning": "Some reasoning without main advice",
        "confidence_score": 0.8
    }
    
    is_valid, error = schema_validator.validate_json(invalid_response)
    print(f"Invalid response test: {'PASS' if not is_valid else 'FAIL'}")
    if error:
        print(f"Expected error: {error}")
    print()

def test_invalid_confidence_score():
    """Test validation with invalid confidence score."""
    print("Testing invalid confidence score...")
    
    invalid_confidence = {
        "main_advice": "Start Josh Allen",
        "confidence_score": 1.5  # Invalid: > 1.0
    }
    
    is_valid, error = schema_validator.validate_json(invalid_confidence)
    print(f"Invalid confidence test: {'PASS' if not is_valid else 'FAIL'}")
    if error:
        print(f"Expected error: {error}")
    print()

def test_streaming_chunks():
    """Test streaming chunk validation."""
    print("Testing streaming chunks...")
    
    # Test incomplete JSON (should be valid during streaming)
    incomplete_json = '{"main_advice": "Start Josh'
    is_valid, error = schema_validator.validate_streaming_chunk(incomplete_json, is_complete=False)
    print(f"Incomplete JSON test: {'PASS' if is_valid else 'FAIL'}")
    
    # Test complete valid JSON
    complete_json = '{"main_advice": "Start Josh Allen"}'
    is_valid, error = schema_validator.validate_streaming_chunk(complete_json, is_complete=True)
    print(f"Complete JSON test: {'PASS' if is_valid else 'FAIL'}")
    
    # Test complete invalid JSON
    invalid_complete = '{"reasoning": "No main advice"}'
    is_valid, error = schema_validator.validate_streaming_chunk(invalid_complete, is_complete=True)
    print(f"Invalid complete JSON test: {'PASS' if not is_valid else 'FAIL'}")
    print()

def test_fallback_response():
    """Test fallback response creation."""
    print("Testing fallback response creation...")
    
    original_text = "Some malformed response"
    error_msg = "Schema validation failed"
    
    fallback = schema_validator.create_fallback_response(original_text, error_msg)
    
    # Validate the fallback response
    is_valid, error = schema_validator.validate_json(fallback)
    print(f"Fallback response test: {'PASS' if is_valid else 'FAIL'}")
    if error:
        print(f"Unexpected error: {error}")
    
    print(f"Fallback response: {json.dumps(fallback, indent=2)}")
    print()

def main():
    """Run all tests."""
    print("=== Step 6: Schema Validation Tests ===\n")
    
    # Test schema loading
    schema = schema_validator.get_schema()
    print(f"Schema loaded successfully: {schema.get('title', 'Unknown')}")
    print(f"Required fields: {schema.get('required', [])}")
    print()
    
    # Run validation tests
    test_valid_response()
    test_minimal_response()
    test_invalid_response()
    test_invalid_confidence_score()
    test_streaming_chunks()
    test_fallback_response()
    
    print("=== Tests Complete ===")

if __name__ == "__main__":
    main() 