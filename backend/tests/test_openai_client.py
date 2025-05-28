import pytest
from app.services.openai_client import get_response
from unittest.mock import patch, MagicMock
import os
from openai import OpenAI

def test_get_response_success():
    # Mock response creation
    mock_response = MagicMock()
    mock_response.output_text = "Test response"
    mock_response.model = "gpt-4.1"
    
    with patch('app.services.openai_client.client.responses.create', return_value=mock_response):
        response_text, model_used = get_response("Test prompt")
        
        assert response_text == "Test response"
        assert model_used == "gpt-4.1"

def test_get_response_error():
    with patch('app.services.openai_client.client.responses.create', side_effect=Exception("API Error")):
        with pytest.raises(Exception) as exc_info:
            get_response("Test prompt")
        assert str(exc_info.value) == "API Error"

def test_get_response_custom_model():
    # Mock response creation
    mock_response = MagicMock()
    mock_response.output_text = "Custom model response"
    mock_response.model = "gpt-4.1"
    
    with patch('app.services.openai_client.client.responses.create', return_value=mock_response):
        response_text, model_used = get_response("Test prompt", model="gpt-4.1")
        
        assert response_text == "Custom model response"
        assert model_used == "gpt-4.1"

def test_get_response_web_search_enabled():
    mock_openai_response = MagicMock()
    mock_openai_response.output_text = "Web search response"
    mock_openai_response.model = "gpt-4.1"

    with patch('app.services.openai_client.client.responses.create', return_value=mock_openai_response) as mock_create:
        response_text, model_used = get_response("Test prompt with web search", enable_web_search=True)
        
        assert response_text == "Web search response"
        assert model_used == "gpt-4.1"
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        assert kwargs.get("tools") == [{"type": "web_search_preview"}]
        # Check that max_output_tokens is potentially increased
        assert kwargs.get("max_output_tokens", 0) >= 1000 # Default is 1000, web search might increase it to 1500

def test_get_response_web_search_disabled():
    mock_openai_response = MagicMock()
    mock_openai_response.output_text = "No web search response"
    mock_openai_response.model = "gpt-4.1"

    with patch('app.services.openai_client.client.responses.create', return_value=mock_openai_response) as mock_create:
        response_text, model_used = get_response("Test prompt no web search", enable_web_search=False)
        
        assert response_text == "No web search response"
        assert model_used == "gpt-4.1"
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        assert "tools" not in kwargs # Or assert kwargs.get("tools") is None, depending on implementation
        assert kwargs.get("max_output_tokens", 0) == 1000 # Default is 1000

