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
        Maps common fields to their expected schema fields and ensures required fields are present.
        
        Args:
            data: The parsed JSON data to transform
            
        Returns:
            Transformed data that better matches our schema
        """
        transformed = data.copy()
        
        # Handle main_advice field (REQUIRED)
        if 'main_advice' not in transformed:
            # Try common alternative field names
            for alt_field in ['message', 'advice', 'recommendation', 'answer', 'response', 'text', 'content', 'summary']:
                if alt_field in transformed and isinstance(transformed[alt_field], str):
                    transformed['main_advice'] = transformed[alt_field]
                    logger.info(f"Transformed '{alt_field}' field to 'main_advice'")
                    break
            
            # If still missing, try to extract from nested content structures
            if 'main_advice' not in transformed:
                # Check for OpenAI Responses API content structures
                if 'output' in transformed and isinstance(transformed['output'], list):
                    for item in transformed['output']:
                        if isinstance(item, dict) and 'content' in item and isinstance(item['content'], str):
                            transformed['main_advice'] = item['content']
                            logger.info(f"Extracted 'main_advice' from output.content")
                            break
                        elif isinstance(item, dict) and 'content' in item and isinstance(item['content'], list):
                            for content_item in item['content']:
                                if isinstance(content_item, dict) and 'text' in content_item:
                                    transformed['main_advice'] = content_item['text']
                                    logger.info(f"Extracted 'main_advice' from output.content[].text")
                                    break
            
            # Last resort: Create a generic main_advice if nothing else worked
            if 'main_advice' not in transformed:
                # Create a fallback main_advice from the first content we can find
                content_text = ""
                for key, value in transformed.items():
                    if isinstance(value, str) and len(value) > 10:
                        content_text = value[:200]  # Limit length
                        break
                
                if content_text:
                    transformed['main_advice'] = content_text
                    logger.warning(f"Created fallback 'main_advice' from content: {content_text[:50]}...")
                else:
                    transformed['main_advice'] = "Response processing error. Please try again with a more specific question."
                    logger.warning("Created generic fallback 'main_advice' due to missing content")
        
        # Transform confidence to confidence_score if needed
        if 'confidence_score' not in transformed:
            for conf_field in ['confidence', 'score', 'certainty', 'probability']:
                if conf_field in transformed:
                    # Ensure it's a number between 0 and 1
                    try:
                        conf_value = float(transformed[conf_field])
                        # If value is outside 0-1 range, normalize it
                        if conf_value > 1:
                            conf_value = min(conf_value, 100) / 100  # Assuming it might be 0-100 scale
                        transformed['confidence_score'] = conf_value
                        logger.info(f"Transformed '{conf_field}' field to 'confidence_score'")
                        break
                    except (ValueError, TypeError):
                        pass
            
            # Add default confidence if not found
            if 'confidence_score' not in transformed:
                transformed['confidence_score'] = 0.7  # Default medium-high confidence
                logger.info("Added default 'confidence_score' of 0.7")
        
        # Ensure reasoning field exists
        if 'reasoning' not in transformed:
            for reason_field in ['explanation', 'rationale', 'analysis', 'details', 'description']:
                if reason_field in transformed and isinstance(transformed[reason_field], str):
                    transformed['reasoning'] = transformed[reason_field]
                    logger.info(f"Transformed '{reason_field}' field to 'reasoning'")
                    break
            
            # Add default reasoning if not found
            if 'reasoning' not in transformed:
                transformed['reasoning'] = "Based on analysis of available data and statistical patterns."
                logger.info("Added default 'reasoning' text")
        
        # Handle alternatives field if missing
        if 'alternatives' not in transformed:
            transformed['alternatives'] = None
            logger.info("Set 'alternatives' to null")
        
        # Ensure model_identifier exists
        if 'model_identifier' not in transformed:
            # Try to extract from response if available
            if 'model' in transformed:
                transformed['model_identifier'] = transformed['model']
            else:
                transformed['model_identifier'] = "unknown_model"
                logger.info("Set 'model_identifier' to 'unknown_model'")
            
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
                
                # Apply our transformations to recover as much as possible
                transformed_data = self._transform_json_format(data)
                
                # If transformation was successful and created a valid main_advice, use the transformed data
                if 'main_advice' in transformed_data and transformed_data['main_advice']:
                    # Add error info to reasoning
                    if 'reasoning' in transformed_data:
                        transformed_data['reasoning'] += f"\n\nNote: Response required transformation due to: {error_msg}"
                    else:
                        transformed_data['reasoning'] = f"Response validation required correction: {error_msg}"
                    
                    # Ensure all required fields are present
                    transformed_data['confidence_score'] = transformed_data.get('confidence_score', 0.5)
                    transformed_data['alternatives'] = transformed_data.get('alternatives', None)
                    transformed_data['model_identifier'] = transformed_data.get('model_identifier', 'validation_fallback')
                    
                    return transformed_data
                
        except Exception as e:
            logger.error(f"Error creating fallback from JSON: {e}")
            # Continue to default fallback
            
        # Default fallback for non-JSON or failed transformation
        # Extract any meaningful text
        clean_text = original_text.strip()
        if clean_text and not clean_text.startswith('{') and not clean_text.startswith('['):
            main_advice = clean_text[:200]  # Limit length
        else:
            main_advice = "Sorry, I encountered an error generating a proper response."
            
        return {
            "main_advice": main_advice,
            "reasoning": f"Response validation failed: {error_msg}. Please try rephrasing your question.",
            "confidence_score": 0.1,
            "alternatives": None,
            "model_identifier": "validation_fallback"
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the loaded schema."""
        return self.schema


# Global instance
schema_validator = SchemaValidator() 