from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import json
import openai
import os
from app.rag.initialize_rag import RAGInitializer

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
                
                # Check OpenAI API key first
                if not os.getenv("OPENAI_API_KEY"):
                    await websocket.send_json({
                        "error": "OpenAI API key not configured",
                        "response": None
                    })
                    continue

                # Parse and validate JSON
                try:
                    parsed_data = json.loads(raw_data)
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "error": "Invalid JSON format",
                        "response": None
                    })
                    continue
                
                logger.info(f"Parsed data: {parsed_data}")
                
                # Validate message format
                if not isinstance(parsed_data, dict) or "message" not in parsed_data:
                    await websocket.send_json({
                        "error": "Message must contain 'message' key",
                        "response": None
                    })
                    continue
                
                user_message = parsed_data["message"]
                logger.info(f"User message: {user_message}")
                
                # Create OpenAI message format
                openai_messages = [
                    {"role": "user", "content": user_message}
                ]
                logger.info(f"OpenAI messages: {openai_messages}")
                
                try:
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
                except Exception as e:
                    # Return the exact error message from the exception
                    error_message = str(e)
                    logger.error(f"OpenAI API error: {error_message}")
                    await websocket.send_json({
                        "error": error_message,  # Changed from "OpenAI API error" to the actual error message
                        "response": None
                    })
                    
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                break
            except Exception as e:
                logger.error(f"Server error: {str(e)}")
                await websocket.send_json({
                    "error": str(e),
                    "response": None
                })
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")

@app.post("/api/initialize-rag")
async def initialize_rag():
    """Initialize or update the RAG system with PDF files."""
    try:
        initializer = RAGInitializer(
            pdf_dir="/app/data",
            db_dir="/app/chroma_db"
        )
        
        # Get initial state
        initial_info = initializer.get_store_info()
        
        # Initialize vector store
        success = initializer.initialize_vector_store()
        
        if success:
            # Get updated state
            final_info = initializer.get_store_info()
            return {
                "status": "success",
                "initial_state": initial_info,
                "final_state": final_info
            }
        else:
            return {
                "status": "error",
                "message": "Failed to initialize vector store",
                "initial_state": initial_info
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Remove all other endpoints for now
