from fastapi.testclient import TestClient
from app.main import app
from app.models import AdviceRequest, Message
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_get_advice():
    test_request = AdviceRequest(
        conversation=[
            Message(role="user", content="Test message")
        ]
    )

    # Create a mock response
    mock_response = MagicMock()
    mock_response.output_text = "Test response"
    mock_response.model = "gpt-4.1"

    with patch('app.services.openai_client.client.responses.create', return_value=mock_response):
        response = client.post("/advice", json=test_request.model_dump())

        assert response.status_code == 200
        assert response.json() == {
            "reply": "Test response",
            "model": "gpt-4.1"
        }

def test_get_custom_advice():
    test_request = AdviceRequest(
        conversation=[
            Message(role="user", content="Test message")
        ]
    )

    # Create a mock response
    mock_response = MagicMock()
    mock_response.output_text = "Custom model response"
    mock_response.model = "gpt-4.1"

    with patch('app.services.openai_client.client.responses.create', return_value=mock_response):
        response = client.post(
            "/custom-advice?model=gpt-4.1&max_tokens=200&temperature=0.8",
            json=test_request.model_dump()
        )

        assert response.status_code == 200
        assert response.json() == {
            "reply": "Custom model response",
            "model": "gpt-4.1"
        }

def test_get_advice_invalid_request():
    response = client.post("/advice", json={"invalid": "request"})
    assert response.status_code == 422 