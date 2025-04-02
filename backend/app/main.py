from fastapi import FastAPI
import logging
import sys
import os

# Basic FastAPI app
app = FastAPI()

# Simple logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

# Remove all other endpoints for now
