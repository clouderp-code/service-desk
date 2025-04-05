import pytest
import os
import json
from pathlib import Path
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from app.main import app
from app.rag.initialize_rag import RAGInitializer
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def rag_initializer():
    """Initialize RAG with actual PDF files"""
    pdf_dir = "/app/data"
    db_dir = "/app/chroma_db"
    
    # Verify PDF directory exists and contains files
    pdf_path = Path(pdf_dir)
    assert pdf_path.exists(), f"PDF directory {pdf_dir} does not exist"
    pdf_files = list(pdf_path.glob("*.pdf"))
    assert pdf_files, f"No PDF files found in {pdf_dir}"
    
    # Initialize RAG
    initializer = RAGInitializer(pdf_dir=pdf_dir, db_dir=db_dir)
    success = initializer.initialize_vector_store()
    assert success, "Failed to initialize vector store"
    
    return initializer

def test_rag_initialization(rag_initializer):
    """Test that RAG system initializes with actual PDF content"""
    store_info = rag_initializer.get_store_info()
    assert store_info["total_documents"] > 0, "No documents in vector store"
    assert len(store_info["pdf_files"]) > 0, "No PDF files processed"
    print(f"\nProcessed PDFs: {store_info['pdf_files']}")
    print(f"Total chunks: {store_info['total_documents']}")

@pytest.mark.asyncio
async def test_chat_about_promodeagro():
    """Test chat responses about ProModeAgro content"""
    with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
        # Send a query about ProModeAgro
        websocket.send_json({
            "message": "What is ProModeAgro and what do they do?"
        })
        
        response = websocket.receive_json()
        assert response.get("error") is None, f"Error in response: {response.get('error')}"
        
        # The response should contain relevant information from the pitch deck
        response_text = response.get("response", "")
        print(f"\nResponse: {response_text}")
        
        # Check for relevant keywords that should be in the response
        relevant_terms = ["ProModeAgro", "agriculture", "farm", "technology"]
        found_terms = [term for term in relevant_terms if term.lower() in response_text.lower()]
        assert found_terms, f"Response doesn't contain any relevant terms from {relevant_terms}"

@pytest.mark.asyncio
async def test_chat_specific_details():
    """Test chat responses about specific details from the PDF"""
    with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
        # Send a query about specific details
        websocket.send_json({
            "message": "What farming methods do you use?"
        })
        
        response = websocket.receive_json()
        assert response.get("error") is None
        
        response_text = response.get("response", "")
        print(f"\nResponse about challenges: {response_text}")
        
        # The response should be detailed and relevant
        assert len(response_text) > 100, "Response seems too short for a detailed answer"

@pytest.mark.asyncio
async def test_chat_multiple_related_queries():
    """Test chat maintains context across multiple related queries"""
    with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
        # First query about the company
        websocket.send_json({
            "message": "How do you ensure soil fertility?"
        })
        response1 = websocket.receive_json()
        
        # Follow-up query
        websocket.send_json({
            "message": "What are the benefits of this solution?"
        })
        response2 = websocket.receive_json()
        
        print(f"\nFirst response: {response1.get('response')}")
        print(f"Follow-up response: {response2.get('response')}")
        
        # Both responses should be meaningful and related
        assert response1.get("error") is None
        assert response2.get("error") is None
        assert len(response1.get("response", "")) > 50
        assert len(response2.get("response", "")) > 50

@pytest.mark.asyncio
async def test_chat_unrelated_query():
    """Test chat response to queries unrelated to the PDF content"""
    with TestClient(app).websocket_connect("/api/chat/ws") as websocket:
        websocket.send_json({
            "message": "What quality checks do you perform?"
        })
        
        response = websocket.receive_json()
        response_text = response.get("response", "")
        print(f"\nUnrelated query response: {response_text}")
        
        # Response should indicate limited knowledge or redirect to PDF content
        assert response.get("error") is None
        assert len(response_text) > 0

def test_vector_store_content():
    """Test the actual content stored in the vector store"""
    try:
        # Initialize vector store
        vector_store = Chroma(
            persist_directory="/app/chroma_db",
            embedding_function=OpenAIEmbeddings()
        )
        
        # Test a few relevant queries
        test_queries = [
            "ProModeAgro main product",
            "agriculture challenges",
            "technology solution",
            "business model"
        ]
        
        for query in test_queries:
            results = vector_store.similarity_search(query, k=2)
            print(f"\nQuery: {query}")
            print(f"Found {len(results)} relevant chunks")
            for i, doc in enumerate(results):
                print(f"Chunk {i+1}: {doc.page_content[:100]}...")
            
            assert results, f"No results found for query: {query}"
            assert len(results[0].page_content) > 0, "Empty content in vector store"

    except Exception as e:
        pytest.fail(f"Error accessing vector store: {str(e)}")

def test_initialize_rag_endpoint(test_client):
    """Test the RAG initialization endpoint with actual PDFs"""
    response = test_client.post("/api/initialize-rag")
    assert response.status_code == 200
    
    data = response.json()
    print(f"\nInitialization response: {json.dumps(data, indent=2)}")
    
    assert data["status"] == "success"
    assert data["final_state"]["total_documents"] > 0
    assert len(data["final_state"]["pdf_files"]) > 0 