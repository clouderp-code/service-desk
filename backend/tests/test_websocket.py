import pytest
from fastapi.testclient import TestClient
import json
import os
from unittest.mock import patch
from app.main import app

@pytest.fixture
def test_client():
    return TestClient(app)

def test_websocket_connection(test_client):
    with test_client.websocket_connect("/api/chat/ws") as websocket:
        data = {"message": "Hello"}
        websocket.send_json(data)
        response = websocket.receive_json()
        assert "response" in response or "error" in response

def test_websocket_echo():
    with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
        data = {"message": "test message"}
        websocket.send_json(data)
        response = websocket.receive_json()
        assert "response" in response or "error" in response

def test_invalid_message_format():
    with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
        websocket.send_text("invalid json")
        response = websocket.receive_json()
        assert response["error"] == "Invalid JSON format"
        assert response["response"] is None

def test_missing_api_key():
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
        with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
            data = {"message": "test"}
            websocket.send_json(data)
            response = websocket.receive_json()
            assert response["error"] == "OpenAI API key not configured"
            assert response["response"] is None

def test_openai_api_error():
    with patch('openai.ChatCompletion.acreate') as mock_create:
        mock_create.side_effect = Exception("API Error")
        with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
            data = {"message": "test"}
            websocket.send_json(data)
            response = websocket.receive_json()
            assert response["error"] == "API Error"
            assert response["response"] is None 