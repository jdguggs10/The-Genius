#!/usr/bin/env python3
"""
Script to generate JSON schema from StructuredAdvice Pydantic model.
This is used for Step 6: Schema-First Response Validation.
"""

import json
import os
from app.models import StructuredAdvice

def generate_response_schema():
    """Generate JSON schema from StructuredAdvice model."""
    schema = StructuredAdvice.model_json_schema()
    
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