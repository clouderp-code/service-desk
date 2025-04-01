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
        # Send a ping message to verify connection
        websocket.send_json({"content": "ping"})
        response = websocket.receive_json()
        assert response is not None

@pytest.mark.asyncio
async def test_websocket_echo():
    with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
        test_message = {"content": "Hello, how are you?"}
        websocket.send_json(test_message)
        
        response = websocket.receive_json()
        assert isinstance(response, dict)
        assert "response" in response or "error" in response

@pytest.mark.asyncio
async def test_invalid_message_format():
    with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
        websocket.send_text("invalid json")
        response = websocket.receive_json()
        
        assert isinstance(response, dict)
        assert "error" in response
        assert response["error"] == "Invalid message format"

@pytest.mark.asyncio
async def test_missing_api_key():
    with patch('app.main.client.api_key', None):
        with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
            websocket.send_json({"content": "test"})
            response = websocket.receive_json()
            
            assert isinstance(response, dict)
            assert "error" in response
            assert isinstance(response["error"], str)
            assert "OpenAI API key not configured" in response["error"]
            assert response["response"] is None

@pytest.mark.asyncio
async def test_openai_api_error():
    with patch('app.main.client.chat.completions.create') as mock_create:
        mock_create.side_effect = Exception("API Error")
        
        with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
            websocket.send_json({"content": "test"})
            response = websocket.receive_json()
            
            assert isinstance(response, dict)
            assert "error" in response
            assert isinstance(response["error"], str)
            assert "AI service error" in response["error"] 