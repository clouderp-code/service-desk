from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from .middleware import error_handler
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(error_handler)

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    response: str
    error: str = None

@app.get("/")
async def root():
    return {"message": "Service Desk API is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    try:
        # Validate OpenAI API key
        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Convert messages to OpenAI format
        messages = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        return ChatResponse(
            response=response.choices[0].message.content
        )
    except Exception as e:
        return ChatResponse(
            response="",
            error=str(e)
        )

@app.websocket("/api/chat/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                logger.info(f"Received message: {data}")

                # Parse the message
                try:
                    message_data = json.loads(data)
                    content = message_data.get("content", "")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    await websocket.send_json({
                        "response": None,
                        "error": "Invalid message format"
                    })
                    continue

                # Validate OpenAI API key
                if not client.api_key:
                    logger.error("OpenAI API key not configured")
                    await websocket.send_json({
                        "response": None,
                        "error": "OpenAI API key not configured"  # Make sure error is a string
                    })
                    continue

                # Call OpenAI API
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": content}
                        ]
                    )
                    
                    response_text = response.choices[0].message.content
                    logger.info(f"AI response generated: {response_text[:100]}...")
                    
                    await websocket.send_json({
                        "response": response_text,
                        "error": None
                    })
                    
                except Exception as e:
                    logger.error(f"OpenAI API error: {str(e)}")
                    await websocket.send_json({
                        "response": None,
                        "error": f"AI service error: {str(e)}"
                    })

            except WebSocketDisconnect:
                manager.disconnect(websocket)
                break
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                await websocket.send_json({
                    "response": None,
                    "error": f"Unexpected error: {str(e)}"
                })

    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        manager.disconnect(websocket)
