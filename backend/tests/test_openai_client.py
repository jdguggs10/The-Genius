import pytest
import json # Added import
from app.services.openai_client import get_response, OPENAI_DEFAULT_MODEL_INTERNAL
from app.models import StructuredAdvice
from unittest.mock import patch, MagicMock
from openai import APIError, APIConnectionError, RateLimitError, AuthenticationError

# Helper to create the nested mock structure for OpenAI API response
def create_mock_openai_response(text_content: str, model_name: str = OPENAI_DEFAULT_MODEL_INTERNAL):
    mock_response = MagicMock()
    
    # Simulate the structure that get_response expects
    # response.output[0].content[0].text
    mock_content_item = MagicMock()
    mock_content_item.text = text_content
    
    mock_output_item = MagicMock()
    mock_output_item.content = [mock_content_item]
    
    mock_response.output = [mock_output_item]
    # The model attribute on the response object itself is not directly used by get_response
    # for the model_identifier in StructuredAdvice, but good to keep for completeness if other parts rely on it.
    # However, get_response passes the 'model' parameter to StructuredAdvice constructor.
    return mock_response

def test_get_response_success():
    expected_text = "Test response"
    expected_model = OPENAI_DEFAULT_MODEL_INTERNAL
    mock_api_response = create_mock_openai_response(expected_text, expected_model)
    
    with patch('app.services.openai_client.client.responses.create', return_value=mock_api_response) as mock_create:
        response_obj = get_response("Test prompt")
        
        assert isinstance(response_obj, StructuredAdvice)
        assert response_obj.main_advice == expected_text
        assert response_obj.model_identifier == expected_model
        mock_create.assert_called_once()
        _, kwargs = mock_create.call_args
        assert kwargs['model'] == expected_model
        assert kwargs['max_output_tokens'] == 2000 # Default

def test_get_response_custom_model():
    expected_text = "Custom model response"
    custom_model = "gpt-custom-test"
    mock_api_response = create_mock_openai_response(expected_text, custom_model)
    
    with patch('app.services.openai_client.client.responses.create', return_value=mock_api_response) as mock_create:
        response_obj = get_response("Test prompt", model=custom_model)
        
        assert isinstance(response_obj, StructuredAdvice)
        assert response_obj.main_advice == expected_text
        assert response_obj.model_identifier == custom_model
        mock_create.assert_called_once()
        _, kwargs = mock_create.call_args
        assert kwargs['model'] == custom_model

def test_get_response_api_error():
    error_message = "Simulated API Error"
    with patch('app.services.openai_client.client.responses.create', side_effect=APIError(message=error_message, response=MagicMock(), body=None)) as mock_create:
        response_obj = get_response("Test prompt for API error")
        
        assert isinstance(response_obj, StructuredAdvice)
        assert "Error: OpenAI API Error" in response_obj.main_advice # Check generic part
        assert error_message in response_obj.main_advice # Check specific error message
        mock_create.assert_called_once()

def test_get_response_connection_error():
    error_message = "Simulated Connection Error"
    with patch('app.services.openai_client.client.responses.create', side_effect=APIConnectionError(message=error_message)) as mock_create:
        response_obj = get_response("Test prompt for connection error")
        
        assert isinstance(response_obj, StructuredAdvice)
        assert "Error: API Connection Error" in response_obj.main_advice
        assert error_message in response_obj.main_advice
        mock_create.assert_called_once()

def test_get_response_rate_limit_error():
    error_message = "Simulated Rate Limit Error"
    with patch('app.services.openai_client.client.responses.create', side_effect=RateLimitError(message=error_message, response=MagicMock(), body=None)) as mock_create:
        response_obj = get_response("Test prompt for rate limit error")
        
        assert isinstance(response_obj, StructuredAdvice)
        assert "Error: Rate Limit Exceeded" in response_obj.main_advice
        assert error_message in response_obj.main_advice
        mock_create.assert_called_once()

def test_get_response_authentication_error():
    error_message = "Simulated Authentication Error"
    with patch('app.services.openai_client.client.responses.create', side_effect=AuthenticationError(message=error_message, response=MagicMock(), body=None)) as mock_create:
        response_obj = get_response("Test prompt for auth error")
        
        assert isinstance(response_obj, StructuredAdvice)
        assert "Error: Authentication Failed" in response_obj.main_advice
        assert error_message in response_obj.main_advice
        mock_create.assert_called_once()

def test_get_response_generic_exception():
    error_message = "Some generic exception"
    with patch('app.services.openai_client.client.responses.create', side_effect=Exception(error_message)) as mock_create:
        response_obj = get_response("Test prompt for generic error")
        
        assert isinstance(response_obj, StructuredAdvice)
        assert "Error: An unexpected error occurred" in response_obj.main_advice
        assert error_message in response_obj.main_advice
        mock_create.assert_called_once()

def test_get_response_web_search_enabled():
    expected_text = "Web search response"
    expected_model = OPENAI_DEFAULT_MODEL_INTERNAL
    mock_api_response = create_mock_openai_response(expected_text, expected_model)

    with patch('app.services.openai_client.client.responses.create', return_value=mock_api_response) as mock_create:
        response_obj = get_response("Test prompt with web search", enable_web_search=True)
        
        assert isinstance(response_obj, StructuredAdvice)
        assert response_obj.main_advice == expected_text
        assert response_obj.model_identifier == expected_model
        
        mock_create.assert_called_once()
        _, kwargs = mock_create.call_args
        assert kwargs.get("tools") == [{"type": "web_search"}]
        assert kwargs.get("max_output_tokens") == 2000 # Default in get_response

def test_get_response_web_search_disabled():
    expected_text = "No web search response"
    expected_model = OPENAI_DEFAULT_MODEL_INTERNAL
    mock_api_response = create_mock_openai_response(expected_text, expected_model)

    with patch('app.services.openai_client.client.responses.create', return_value=mock_api_response) as mock_create:
        response_obj = get_response("Test prompt no web search", enable_web_search=False)
        
        assert isinstance(response_obj, StructuredAdvice)
        assert response_obj.main_advice == expected_text
        assert response_obj.model_identifier == expected_model
        
        mock_create.assert_called_once()
        _, kwargs = mock_create.call_args
        # When tools are not passed or passed as None to OpenAI client,
        # the 'tools' key might be absent in kwargs or its value might be None.
        # The implementation of get_response sets tools=None if enable_web_search is False.
        assert kwargs.get("tools") is None
        assert kwargs.get("max_output_tokens") == 2000 # Default in get_response

def test_get_response_max_tokens_override():
    expected_text = "Max tokens override response"
    expected_model = OPENAI_DEFAULT_MODEL_INTERNAL
    custom_max_tokens = 150
    mock_api_response = create_mock_openai_response(expected_text, expected_model)
    
    with patch('app.services.openai_client.client.responses.create', return_value=mock_api_response) as mock_create:
        response_obj = get_response("Test prompt", max_tokens=custom_max_tokens)
        
        assert isinstance(response_obj, StructuredAdvice)
        assert response_obj.main_advice == expected_text
        assert response_obj.model_identifier == expected_model
        mock_create.assert_called_once()
        _, kwargs = mock_create.call_args
        assert kwargs['max_output_tokens'] == custom_max_tokens

def test_get_response_json_parsable_response():
    json_string = '{"main_advice": "Parsed JSON advice", "reasoning": "It was JSON.", "model_identifier": "gpt-json-model"}'
    # The model_identifier from JSON should take precedence if StructuredAdvice.model_validate_json sets it.
    # Current get_response implementation:
    # 1. Tries model_validate_json. If this sets model_identifier, it's used.
    # 2. If model_identifier is None after validation, it's set to the 'model' parameter.
    # Let's assume model_validate_json correctly populates all fields from valid JSON.
    
    mock_api_response = create_mock_openai_response(json_string) # model_name in create_mock_openai_response is not used by this path

    with patch('app.services.openai_client.client.responses.create', return_value=mock_api_response) as mock_create:
        # We pass a model to get_response, but the JSON contains one.
        response_obj = get_response("Test prompt for JSON", model="gpt-param-model")
        
        assert isinstance(response_obj, StructuredAdvice)
        assert response_obj.main_advice == "Parsed JSON advice"
        assert response_obj.reasoning == "It was JSON."
        # The model_identifier from the JSON string should be used by model_validate_json
        assert response_obj.model_identifier == "gpt-json-model" 
        mock_create.assert_called_once()

def test_get_response_json_malformed_response_fallback():
    malformed_json_string = '{"main_advice": "This is not really JSON....'
    expected_model = "gpt-fallback-model"
    mock_api_response = create_mock_openai_response(malformed_json_string, expected_model)

    with patch('app.services.openai_client.client.responses.create', return_value=mock_api_response) as mock_create:
        response_obj = get_response("Test prompt for malformed JSON", model=expected_model)
        
        assert isinstance(response_obj, StructuredAdvice)
        # It should fall back to treating the text as plain main_advice
        assert response_obj.main_advice == malformed_json_string
        assert response_obj.model_identifier == expected_model # Falls back to model parameter
        assert response_obj.reasoning is None # Or whatever default Pydantic sets
        mock_create.assert_called_once()

def test_get_response_empty_api_response():
    # Simulate a response that is technically successful but has no output content
    mock_empty_response = MagicMock()
    mock_empty_response.output = [] # No output items

    with patch('app.services.openai_client.client.responses.create', return_value=mock_empty_response) as mock_create:
        response_obj = get_response("Test prompt for empty API response")

        assert isinstance(response_obj, StructuredAdvice)
        assert "Error: No valid response received from OpenAI" in response_obj.main_advice
        assert response_obj.reasoning == "The API response was empty or malformed"
        # model_identifier will be the default model since the response is empty
        assert response_obj.model_identifier == OPENAI_DEFAULT_MODEL_INTERNAL 
        mock_create.assert_called_once()

def test_get_response_api_response_none_output():
    # Simulate a response that is technically successful but output is None
    mock_none_output_response = MagicMock()
    mock_none_output_response.output = None # Output is None

    with patch('app.services.openai_client.client.responses.create', return_value=mock_none_output_response) as mock_create:
        response_obj = get_response("Test prompt for None API output")

        assert isinstance(response_obj, StructuredAdvice)
        assert "Error: No valid response received from OpenAI" in response_obj.main_advice
        assert response_obj.reasoning == "The API response was empty or malformed"
        assert response_obj.model_identifier == OPENAI_DEFAULT_MODEL_INTERNAL
        mock_create.assert_called_once()

def test_get_response_api_response_output_with_no_content():
    # Simulate output item exists, but its 'content' attribute is None or empty
    mock_output_item_no_content = MagicMock()
    mock_output_item_no_content.content = None # or []
    
    mock_response = MagicMock()
    mock_response.output = [mock_output_item_no_content]

    with patch('app.services.openai_client.client.responses.create', return_value=mock_response) as mock_create:
        response_obj = get_response("Test prompt for output with no content")

        assert isinstance(response_obj, StructuredAdvice)
        assert "Error: No valid response received from OpenAI" in response_obj.main_advice
        assert response_obj.reasoning == "The API response was empty or malformed"
        assert response_obj.model_identifier == OPENAI_DEFAULT_MODEL_INTERNAL
        mock_create.assert_called_once()

def test_get_response_api_response_content_with_no_text():
    # Simulate content item exists, but its 'text' attribute is None or not present
    mock_content_item_no_text = MagicMock()
    # To make hasattr(content_item, 'text') true, but its value could be None
    mock_content_item_no_text.text = None 
    
    mock_output_item = MagicMock()
    mock_output_item.content = [mock_content_item_no_text]
    
    mock_response = MagicMock()
    mock_response.output = [mock_output_item]

    with patch('app.services.openai_client.client.responses.create', return_value=mock_response) as mock_create:
        response_obj = get_response("Test prompt for content with no text")

        assert isinstance(response_obj, StructuredAdvice)
        # If .text is None, it might be treated as empty string by strip()
        # The current code `response_text = content_item.text` then `response_text.strip()`
        # If response_text is None, strip() would error. If it's "", then it's empty.
        # Let's assume .text = None leads to an empty string after strip or similar handling
        # or that the condition `if hasattr(content_item, 'text'):` is false if text is None.
        # If `content_item.text` is `None`, `response_text.strip()` will indeed cause an AttributeError.
        # This will be caught by the generic `except Exception as e:`
        assert "Error: An unexpected error occurred" in response_obj.main_advice
        assert response_obj.model_identifier == OPENAI_DEFAULT_MODEL_INTERNAL # Default model in case of such error
        mock_create.assert_called_once()

# To make the last test more robust, let's refine the mock for content_item_no_text
# to ensure `hasattr` is true but value is `None`
class MockContentItemNoText:
    def __init__(self):
        self.text = None

def test_get_response_api_response_content_item_text_is_none():
    mock_content_item_no_text = MockContentItemNoText() # text attribute is None
    
    mock_output_item = MagicMock()
    mock_output_item.content = [mock_content_item_no_text]
    
    mock_response = MagicMock()
    mock_response.output = [mock_output_item]

    with patch('app.services.openai_client.client.responses.create', return_value=mock_response) as mock_create:
        response_obj = get_response("Test prompt for content_item.text is None")

        assert isinstance(response_obj, StructuredAdvice)
        # This scenario should be caught by the generic exception handler in get_response
        # because `response_text.strip()` would be `None.strip()`.
        assert "Error: An unexpected error occurred" in response_obj.main_advice
        # The error message should contain "AttributeError" or similar
        assert "'NoneType' object has no attribute 'strip'" in response_obj.main_advice
        assert response_obj.model_identifier == OPENAI_DEFAULT_MODEL_INTERNAL
        mock_create.assert_called_once()

# Test for when JSON parsing itself fails with json.JSONDecodeError
def test_get_response_json_decode_error_fallback():
    # This text will cause model_validate_json to raise JSONDecodeError
    invalid_json_string = '{"main_advice": "Valid start", "invalid_json": True, ... }' 
    mock_api_response = create_mock_openai_response(invalid_json_string)

    # Mock StructuredAdvice.model_validate_json to raise json.JSONDecodeError
    with patch('app.services.openai_client.client.responses.create', return_value=mock_api_response) as mock_api_call, \
         patch('app.models.StructuredAdvice.model_validate_json', side_effect=json.JSONDecodeError("Simulated decode error", "doc", 0)) as mock_validate:
        
        response_obj = get_response("Test for JSONDecodeError fallback")

        assert isinstance(response_obj, StructuredAdvice)
        # Fallback path: treat the invalid JSON string as main_advice
        assert response_obj.main_advice == invalid_json_string
        assert response_obj.model_identifier == OPENAI_DEFAULT_MODEL_INTERNAL # Default model used in fallback
        mock_api_call.assert_called_once()
        mock_validate.assert_called_once_with(invalid_json_string)
        # This test name is updated to reflect it tests the fallback path when model_validate_json fails,
        # not a separate top-level `except json.JSONDecodeError`.
```

The only change was adding `import json` at the top of the file.
All tests defined in the file `backend/tests/test_openai_client.py` already fulfill the requirements of the subtask.
I can now submit the report.
