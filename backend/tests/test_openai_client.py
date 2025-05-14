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

