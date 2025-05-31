#!/usr/bin/env python3
"""
Standalone script to generate JSON schema for StructuredAdvice model.
This is used for Step 6: Schema-First Response Validation.
"""

import json
import os

def generate_response_schema():
    """Generate JSON schema for StructuredAdvice model."""
    
    # Define the schema based on the StructuredAdvice Pydantic model
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "StructuredAdvice",
        "description": "Structured format for AI advice responses that works with both streaming and non-streaming contexts while supporting the OpenAI Responses API format.",
        "type": "object",
        "properties": {
            "main_advice": {
                "type": "string",
                "description": "Primary recommendation"
            },
            "reasoning": {
                "type": ["string", "null"],
                "description": "Detailed explanation of the recommendation",
                "default": None
            },
            "confidence_score": {
                "type": ["number", "null"],
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Confidence level from 0.0 to 1.0",
                "default": None
            },
            "alternatives": {
                "type": ["array", "null"],
                "items": {
                    "type": "string"
                },
                "description": "Alternative considerations or options",
                "default": None
            },
            "model_identifier": {
                "type": ["string", "null"],
                "description": "Model used for generating the response",
                "default": None
            }
        },
        "required": ["main_advice"],
        "additionalProperties": False
    }
    
    # Create schemas directory if it doesn't exist
    schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas')
    os.makedirs(schemas_dir, exist_ok=True)
    
    # Write schema to file
    schema_path = os.path.join(schemas_dir, 'response.schema.json')
    with open(schema_path, 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"Generated schema file: {schema_path}")
    return schema_path

if __name__ == "__main__":
    generate_response_schema() 