from fastapi.testclient import TestClient
from app.main import app
from app.models import AdviceRequest, Message
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_get_advice():
    base_conversation = [Message(role="user", content="Test message")]
    
    # Test case 1: Simple request
    test_request_simple = AdviceRequest(conversation=base_conversation)
    
    # Test case 2: Request with model and web_search enabled
    test_request_with_options = AdviceRequest(
        conversation=base_conversation,
        model="gpt-4-turbo",
        enable_web_search=True
    )

    # Mock response for the OpenAI client
    mock_openai_response = MagicMock()
    
    with patch('app.services.openai_client.get_response') as mock_get_response:
        # Configure mock for simple request
        mock_get_response.return_value = ("Test response", "gpt-4.1")
        response_simple = client.post("/advice", json=test_request_simple.model_dump())

        assert response_simple.status_code == 200
        assert response_simple.json() == {
            "reply": "Test response",
            "model": "gpt-4.1"
        }
        mock_get_response.assert_called_once_with(
            prompt="Test message",
            model="gpt-4.1",  # Default model in main.py if not provided
            enable_web_search=False # Default enable_web_search in AdviceRequest
        )
        
        # Configure mock for request with options
        mock_get_response.reset_mock()
        mock_get_response.return_value = ("Test response with options", "gpt-4-turbo")
        response_with_options = client.post("/advice", json=test_request_with_options.model_dump())
        
        assert response_with_options.status_code == 200
        assert response_with_options.json() == {
            "reply": "Test response with options",
            "model": "gpt-4-turbo"
        }
        mock_get_response.assert_called_once_with(
            prompt="Test message",
            model="gpt-4-turbo",
            enable_web_search=True
        )

def test_get_advice_invalid_request():
    response = client.post("/advice", json={"invalid": "request"})
    assert response.status_code == 422 