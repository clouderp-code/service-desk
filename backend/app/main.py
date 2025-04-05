from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import json
import openai
import os
from app.rag.initialize_rag import RAGInitializer
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

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
            model="gpt-4o-mini",
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
                # Get message
                data = await websocket.receive_text()
                parsed_data = json.loads(data)
                
                if "message" not in parsed_data:
                    await websocket.send_json({
                        "error": "Message must contain 'message' key",
                        "response": None
                    })
                    continue
                
                user_message = parsed_data["message"]
                
                # Get context from RAG
                context = await get_rag_context(user_message)
                if not context:
                    await websocket.send_json({
                        "error": "No relevant information found in the documents",
                        "response": None
                    })
                    continue
                
                # Create messages for OpenAI with strict instructions
                messages = [
                    {
                        "role": "system",
                        "content": """You are an AI assistant that ONLY answers questions based on the provided context. 
                        If the context doesn't contain enough information to answer the question, say 'I don't have enough information in the provided documents to answer this question.'
                        Do not make up information or use external knowledge.
                        
                        Context:
                        {context}""".format(context=context)
                    },
                    {"role": "user", "content": user_message}
                ]
                
                logger.info(f"Context used: {context}")
                logger.info(f"Messages sent to OpenAI: {messages}")
                
                # Get OpenAI response
                response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.0  # Set to 0 for more focused answers
                )
                
                await websocket.send_json({
                    "error": None,
                    "response": response.choices[0].message.content
                })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "error": "Invalid JSON format",
                    "response": None
                })
            except Exception as e:
                logger.error(f"Error in websocket: {str(e)}")
                await websocket.send_json({
                    "error": str(e),
                    "response": None
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

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

@app.get("/api/debug-rag")
async def debug_rag():
    """Debug endpoint to check RAG system state"""
    try:
        vector_store = Chroma(
            persist_directory="/app/chroma_db",
            embedding_function=OpenAIEmbeddings()
        )
        
        # Get collection stats
        collection = vector_store._collection
        
        # Get a sample document to verify content
        sample_results = vector_store.similarity_search(
            "what is this document about",
            k=1
        )
        
        return {
            "status": "success",
            "document_count": collection.count(),
            "sample_content": sample_results[0].page_content if sample_results else None,
            "embedding_function": str(vector_store._embedding_function),
            "persist_directory": vector_store._persist_directory
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

async def get_rag_context(query: str) -> str:
    """Get relevant context from RAG for the query"""
    try:
        vector_store = Chroma(
            persist_directory="/app/chroma_db",
            embedding_function=OpenAIEmbeddings()
        )
        
        # Get more relevant documents and with higher similarity threshold
        docs = vector_store.similarity_search_with_score(
            query, 
            k=3,  # Get top 3 most relevant chunks
            score_threshold=0.7  # Only return relatively good matches
        )
        
        if not docs:
            logger.warning(f"No relevant documents found for query: {query}")
            return ""
        
        # Combine context from documents, including relevance scores
        context_parts = []
        for doc, score in docs:
            logger.info(f"Document chunk (score {score}): {doc.page_content}")
            context_parts.append(doc.page_content)
            
        context = "\n\nRelevant passage:\n".join(context_parts)
        return context
        
    except Exception as e:
        logger.error(f"Error getting RAG context: {str(e)}")
        return ""

@app.post("/api/clean-and-init-rag")
async def clean_and_init_rag():
    """Clean and reinitialize the RAG system"""
    try:
        from app.clean_and_init_db import clean_vector_store, verify_pdf_directory
        from app.rag.initialize_rag import RAGInitializer
        
        pdf_dir = "/app/data"
        db_dir = "/app/chroma_db"
        
        # Verify PDF directory
        pdf_files = verify_pdf_directory(pdf_dir)
        if not pdf_files:
            return {
                "status": "error",
                "message": "No PDF files found or invalid directory"
            }
        
        # Clean existing vector store
        if not clean_vector_store(db_dir):
            return {
                "status": "error",
                "message": "Failed to clean vector store"
            }
        
        # Initialize new vector store
        initializer = RAGInitializer(pdf_dir=pdf_dir, db_dir=db_dir)
        
        # Get initial state
        initial_info = initializer.get_store_info()
        
        # Initialize vector store
        success = initializer.initialize_vector_store()
        if not success:
            return {
                "status": "error",
                "message": "Failed to initialize vector store"
            }
        
        # Get final state
        final_info = initializer.get_store_info()
        
        return {
            "status": "success",
            "message": "Vector store reinitialized successfully",
            "initial_state": initial_info,
            "final_state": final_info
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Remove all other endpoints for now
