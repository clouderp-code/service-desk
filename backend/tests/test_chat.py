import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_chat_endpoint_success():
    # Mock message
    test_message = {
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
        ]
    }
    
    response = client.post("/api/chat", json=test_message)
    assert response.status_code == 200
    assert "response" in response.json()
    assert response.json()["error"] is None

def test_chat_endpoint_empty_message():
    test_message = {
        "messages": []
    }
    
    response = client.post("/api/chat", json=test_message)
    assert response.status_code == 200
    assert "error" in response.json()

def test_chat_endpoint_invalid_format():
    test_message = {
        "invalid_key": "invalid_value"
    }
    
    response = client.post("/api/chat", json=test_message)
    assert response.status_code == 422  # Validation error

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
def test_chat_endpoint_with_real_api():
    test_message = {
        "messages": [
            {
                "role": "user",
                "content": "What is 2+2?"
            }
        ]
    }
    
    response = client.post("/api/chat", json=test_message)
    assert response.status_code == 200
    assert response.json()["response"] != ""
    assert response.json()["error"] is None 