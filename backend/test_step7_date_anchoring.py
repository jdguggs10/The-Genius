"""
Step 7: Date Anchoring Regression Tests
Tests that ensure current date is automatically prepended to user messages.
"""

import pytest
from datetime import datetime
from app.main import add_date_anchoring_to_conversation


def test_date_anchoring_adds_current_date():
    """Test that date anchoring adds current date to the latest user message"""
    conversation = [
        {"role": "user", "content": "What's the best lineup for today?"},
        {"role": "assistant", "content": "Here's my recommendation..."},
        {"role": "user", "content": "Should I start Player X?"}
    ]
    
    result = add_date_anchoring_to_conversation(conversation)
    
    # Check that the last user message has the date prefix
    current_date = datetime.now().strftime("%Y-%m-%d")
    expected_content = f"Current Date: {current_date}\n\nShould I start Player X?"
    
    assert result[-1]["content"] == expected_content
    assert result[-1]["role"] == "user"
    
    # Check that other messages are unchanged
    assert result[0]["content"] == "What's the best lineup for today?"
    assert result[1]["content"] == "Here's my recommendation..."


def test_date_anchoring_handles_empty_conversation():
    """Test that date anchoring handles empty conversation gracefully"""
    conversation = []
    result = add_date_anchoring_to_conversation(conversation)
    assert result == []


def test_date_anchoring_handles_no_user_messages():
    """Test that date anchoring handles conversation with no user messages"""
    conversation = [
        {"role": "assistant", "content": "Hello, how can I help?"},
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    result = add_date_anchoring_to_conversation(conversation)
    
    # Messages should be unchanged since there are no user messages
    assert result == conversation


def test_date_anchoring_only_affects_latest_user_message():
    """Test that only the latest user message gets the date prefix"""
    conversation = [
        {"role": "user", "content": "First question"},
        {"role": "assistant", "content": "First response"},
        {"role": "user", "content": "Second question"}
    ]
    
    result = add_date_anchoring_to_conversation(conversation)
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # First user message should be unchanged
    assert result[0]["content"] == "First question"
    
    # Last user message should have date prefix
    expected_content = f"Current Date: {current_date}\n\nSecond question"
    assert result[2]["content"] == expected_content


def test_date_anchoring_preserves_message_order():
    """Test that date anchoring preserves the original message order"""
    conversation = [
        {"role": "system", "content": "System message"},
        {"role": "user", "content": "User message"},
        {"role": "assistant", "content": "Assistant message"}
    ]
    
    result = add_date_anchoring_to_conversation(conversation)
    
    # Check that roles are in the same order
    roles = [msg["role"] for msg in result]
    assert roles == ["system", "user", "assistant"]


def test_date_anchoring_format_matches_guide():
    """Test that the date format matches exactly what's specified in the guide"""
    conversation = [{"role": "user", "content": "Test message"}]
    result = add_date_anchoring_to_conversation(conversation)
    
    # Should match the format from the guide: "Current Date: YYYY-MM-DD\n\n{original_content}"
    current_date = datetime.now().strftime("%Y-%m-%d")
    expected_prefix = f"Current Date: {current_date}\n\n"
    
    assert result[0]["content"].startswith(expected_prefix)
    assert result[0]["content"].endswith("Test message")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 