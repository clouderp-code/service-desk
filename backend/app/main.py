from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import json
import openai
import os

# Basic FastAPI app
app = FastAPI()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    messages: List[Dict[str, str]]

class ChatResponse(BaseModel):
    response: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {"status": "ok"}

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/test/env")
async def test_env():
    """Test environment and OpenAI key"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        return {
            "status": "ok",
            "openai_key_exists": bool(api_key),
            "key_length": len(api_key) if api_key else 0
        }
    except Exception as e:
        logger.error(f"Environment test failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/test/imports")
async def test_imports():
    """Test importing required packages"""
    results = {}
    try:
        # Test langchain import
        try:
            import langchain
            results["langchain"] = "ok"
        except ImportError as e:
            results["langchain"] = str(e)

        # Test OpenAI import
        try:
            import openai
            results["openai"] = "ok"
        except ImportError as e:
            results["openai"] = str(e)

        return {
            "status": "ok",
            "import_results": results
        }
    except Exception as e:
        logger.error(f"Import test failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/test/embedding")
async def test_embedding():
    """Test OpenAI embeddings"""
    try:
        from langchain.embeddings import OpenAIEmbeddings
        
        embeddings = OpenAIEmbeddings()
        test_text = "Hello, world!"
        
        # Try to generate an embedding
        result = embeddings.embed_query(test_text)
        
        return {
            "status": "ok",
            "embedding_size": len(result),
            "sample": result[:3]  # First 3 dimensions
        }
    except Exception as e:
        logger.error(f"Embedding test failed: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    try:
        if not openai.api_key:
            return ChatResponse(error="OpenAI API key not configured")

        if not message.messages:
            return ChatResponse(error="No message provided")

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in message.messages]
        )
        
        return ChatResponse(response=response.choices[0].message.content, error=None)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return ChatResponse(error=str(e))

@app.websocket("/api/chat/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    
    try:
        while True:
            try:
                # Get and log the raw message
                raw_data = await websocket.receive_text()
                logger.info(f"Raw data received: {raw_data}")
                
                # Parse and log the JSON
                parsed_data = json.loads(raw_data)
                logger.info(f"Parsed data: {parsed_data}")
                
                # Check if we have a message
                if not isinstance(parsed_data, dict):
                    raise ValueError(f"Expected dict, got {type(parsed_data)}")
                
                if "message" not in parsed_data:
                    raise ValueError(f"Missing 'message' key. Keys received: {list(parsed_data.keys())}")
                
                user_message = parsed_data["message"]
                logger.info(f"User message: {user_message}")
                
                # Create OpenAI message format
                openai_messages = [
                    {"role": "user", "content": user_message}
                ]
                logger.info(f"OpenAI messages: {openai_messages}")
                
                # Call OpenAI
                response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=openai_messages
                )
                
                # Send response
                ai_response = response.choices[0].message.content
                logger.info(f"AI response: {ai_response}")
                
                await websocket.send_json({
                    "error": None,
                    "response": ai_response
                })
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                await websocket.send_json({
                    "error": f"Invalid JSON format: {str(e)}",
                    "response": None
                })
            except ValueError as e:
                logger.error(f"Validation error: {str(e)}")
                await websocket.send_json({
                    "error": str(e),
                    "response": None
                })
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json({
                    "error": str(e),
                    "response": None
                })
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")

# Remove all other endpoints for now
