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

app = FastAPI()

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(error_handler)

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

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
async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    if not client_id:
        client_id = str(id(websocket))
    
    try:
        await manager.connect(websocket, client_id)
        print(f"Client {client_id} connected")  # Debug log
        
        while True:
            try:
                data = await websocket.receive_text()
                print(f"Received message from {client_id}: {data}")  # Debug log
                
                try:
                    message_data = json.loads(data)
                    content = message_data.get("content", "")
                except json.JSONDecodeError:
                    content = data

                # Validate OpenAI API key
                if not client.api_key:
                    await manager.send_message(
                        json.dumps({"error": "OpenAI API key not configured"}),
                        client_id
                    )
                    continue

                # Process message with OpenAI
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": content}
                        ]
                    )
                    
                    response_text = response.choices[0].message.content
                    print(f"AI response: {response_text}")  # Debug log
                    
                    # Send response back to client
                    response_data = json.dumps({
                        "response": response_text,
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "error": None
                    })
                    await websocket.send_text(response_data)
                    print(f"Sent response to {client_id}")  # Debug log
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"Error processing message: {error_msg}")  # Debug log
                    await websocket.send_text(json.dumps({
                        "error": error_msg,
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }))

            except Exception as e:
                print(f"Error in message loop: {str(e)}")  # Debug log
                await websocket.send_text(json.dumps({
                    "error": str(e),
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        print(f"Client {client_id} disconnected")  # Debug log
