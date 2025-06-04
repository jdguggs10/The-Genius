"""
Step 6: Schema-First Response Validation Service
Validates streaming JSON responses against the StructuredAdvice schema.
"""

import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
import jsonschema
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)

class SchemaValidator:
    """
    Service for validating JSON responses against the StructuredAdvice schema.
    Implements Step 6: Schema-First Response Validation from the improvement guide.
    """
    
    def __init__(self):
        """Initialize the schema validator with the response schema."""
        self.schema = self._load_schema()
        logger.info("Schema validator initialized")
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema from file."""
        try:
            schema_path = Path(__file__).parent.parent.parent / "schemas" / "response.schema.json"
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            logger.info(f"Loaded schema from: {schema_path}")
            return schema
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            # Return a minimal fallback schema
            return {
                "type": "object",
                "properties": {
                    "main_advice": {"type": "string"}
                },
                "required": ["main_advice"]
            }
    
    def _transform_json_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform JSON data to match our schema if needed.
        Maps "message" to "main_advice" and "confidence" to "confidence_score" when appropriate.
        
        Args:
            data: The parsed JSON data to transform
            
        Returns:
            Transformed data that better matches our schema
        """
        transformed = data.copy()
        
        # Transform message to main_advice if needed
        if 'message' in transformed and 'main_advice' not in transformed:
            transformed['main_advice'] = transformed['message']
            logger.info("Transformed 'message' field to 'main_advice'")
        
        # Transform confidence to confidence_score if needed
        if 'confidence' in transformed and 'confidence_score' not in transformed:
            transformed['confidence_score'] = transformed['confidence']
            logger.info("Transformed 'confidence' field to 'confidence_score'")
            
        return transformed
    
    def validate_json(self, json_data: Union[str, Dict[str, Any]]) -> tuple[bool, Optional[str]]:
        """
        Validate JSON data against the schema.
        
        Args:
            json_data: JSON string or dict to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse JSON string if needed
            if isinstance(json_data, str):
                try:
                    data = json.loads(json_data)
                except json.JSONDecodeError as e:
                    return False, f"Invalid JSON format: {e}"
            else:
                data = json_data
            
            # Apply transformations to better match our schema
            transformed_data = self._transform_json_format(data)
            
            # Validate against schema
            validate(instance=transformed_data, schema=self.schema)
            return True, None
            
        except ValidationError as e:
            error_msg = f"Schema validation failed: {e.message}"
            logger.warning(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Validation error: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def validate_streaming_chunk(self, accumulated_json: str, is_complete: bool = False) -> tuple[bool, Optional[str]]:
        """
        Validate a streaming JSON chunk.
        
        Args:
            accumulated_json: The accumulated JSON string so far
            is_complete: Whether this is the final complete response
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not accumulated_json.strip():
            return True, None  # Empty chunks are OK during streaming
        
        # For complete responses, do full validation
        if is_complete:
            return self.validate_json(accumulated_json)
        
        # For partial responses, check if it's potentially valid JSON
        try:
            # Try to parse as JSON - if it fails, it might be incomplete
            data = json.loads(accumulated_json)
            
            # Apply transformations for better schema compatibility
            transformed_data = self._transform_json_format(data)
            
            # If it parses, validate against schema
            validate(instance=transformed_data, schema=self.schema)
            return True, None
        except json.JSONDecodeError:
            # Incomplete JSON is expected during streaming
            return True, None
        except ValidationError as e:
            if is_complete:
                # Only report validation errors for complete responses
                error_msg = f"Schema validation failed: {e.message}"
                logger.warning(error_msg)
                return False, error_msg
            else:
                # During streaming, we're lenient with incomplete structures
                return True, None
        except Exception as e:
            if is_complete:
                error_msg = f"Validation error: {e}"
                logger.error(error_msg)
                return False, error_msg
            else:
                return True, None
    
    def create_fallback_response(self, original_text: str, error_msg: str) -> Dict[str, Any]:
        """
        Create a fallback response when validation fails.
        
        Args:
            original_text: The original response text
            error_msg: The validation error message
            
        Returns:
            Valid StructuredAdvice dict
        """
        # Try to extract useful content from original_text if it's JSON
        try:
            if original_text.strip().startswith('{'):
                data = json.loads(original_text)
                
                # Extract message or main_advice
                main_advice = data.get('main_advice', data.get('message', ''))
                
                # Extract confidence or confidence_score
                confidence = data.get('confidence_score', data.get('confidence', 0.1))
                
                # Extract reasoning if available
                reasoning = data.get('reasoning', f"Response validation failed: {error_msg}")
                
                return {
                    "main_advice": main_advice or "Sorry, I encountered an error generating a response.",
                    "reasoning": reasoning,
                    "confidence_score": confidence,
                    "alternatives": None,
                    "model_identifier": "validation_fallback"
                }
        except Exception:
            # If parsing fails, use the default fallback
            pass
            
        return {
            "main_advice": original_text.strip() or "Sorry, I encountered an error generating a response.",
            "reasoning": f"Response validation failed: {error_msg}",
            "confidence_score": 0.1,
            "alternatives": None,
            "model_identifier": "validation_fallback"
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the loaded schema."""
        return self.schema


# Global instance
schema_validator = SchemaValidator() 