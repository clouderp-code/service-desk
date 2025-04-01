import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import json
from app.main import app

@pytest.mark.asyncio
async def test_websocket_connection():
    client = TestClient(app)
    with client.websocket_connect("/api/chat/ws?client_id=test123") as websocket:
        # Test connection is established
        assert websocket.connected

        # Send a test message
        test_message = {
            "content": "Hello, how are you?"
        }
        websocket.send_text(json.dumps(test_message))

        # Receive response
        response = json.loads(websocket.receive_text())
        assert "response" in response
        assert "error" not in response or response["error"] is None

@pytest.mark.asyncio
async def test_websocket_invalid_message():
    client = TestClient(app)
    with client.websocket_connect("/api/chat/ws?client_id=test124") as websocket:
        # Send invalid JSON
        websocket.send_text("invalid json")

        # Should receive error response
        response = json.loads(websocket.receive_text())
        assert "error" in response
        assert response["error"] == "Invalid JSON format" 