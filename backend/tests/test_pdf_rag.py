import pytest
import os
from pathlib import Path
import pdfplumber
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
import psutil
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
SAMPLE_TEXT = """
Retrieval-Augmented Generation (RAG) is a technique that combines retrieval-based 
and generation-based approaches in AI systems. It first retrieves relevant information 
from a knowledge base, then uses that information to generate more accurate responses.
"""

class TestPDFProcessing:
    @pytest.fixture
    def pdf_path(self):
        return "/app/data/promodeagro-pitch-deck.pdf"

    def test_pdf_exists(self, pdf_path):
        """Test if PDF file exists"""
        assert os.path.exists(pdf_path), f"PDF file not found at {pdf_path}"
        assert os.path.getsize(pdf_path) > 0, "PDF file is empty"

    def test_pdf_readable(self, pdf_path):
        """Test if PDF can be read"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                assert len(pdf.pages) > 0, "PDF has no pages"
                # Try to extract text from first page
                text = pdf.pages[0].extract_text()
                assert text, "No text extracted from first page"
        except Exception as e:
            pytest.fail(f"Failed to read PDF: {str(e)}")

    def test_pdf_permissions(self, pdf_path):
        """Test PDF file permissions"""
        stats = os.stat(pdf_path)
        assert stats.st_mode & 0o400, "PDF file is not readable"

class TestRAG:
    @pytest.fixture
    def embeddings(self):
        return OpenAIEmbeddings()

    @pytest.fixture
    def text_splitter(self):
        return CharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            separator="\n"
        )

    @pytest.fixture
    def vector_store(self, embeddings, text_splitter):
        # Add more test data to ensure we have enough content
        test_texts = [
            "Retrieval-Augmented Generation (RAG) is a technique that combines retrieval and generation.",
            "RAG systems first retrieve relevant information from a knowledge base.",
            "Then RAG uses that information to generate accurate responses.",
            "RAG is particularly useful for maintaining up-to-date information."
        ]
        
        # Create fresh collection for each test
        return Chroma.from_texts(
            texts=test_texts,
            embedding=embeddings,
            persist_directory="./test_chroma_db"
        )

    def test_embedding_generation(self, embeddings):
        """Test embedding generation"""
        embedding = embeddings.embed_query("test query")
        assert len(embedding) == 1536, "Unexpected embedding dimension"

    def test_text_splitting(self, text_splitter):
        """Test text splitting"""
        chunks = text_splitter.split_text(SAMPLE_TEXT)
        assert len(chunks) > 0, "No chunks created"
        assert all(len(chunk) <= 1000 for chunk in chunks), "Chunk size exceeded"

    def test_vector_store_creation(self, vector_store):
        """Test vector store creation and search"""
        try:
            # Log the search query
            query = "What is RAG?"
            logger.info(f"Searching vector store with query: {query}")
            
            # Perform search with error handling
            results = vector_store.similarity_search(query, k=1)
            
            # Log results for debugging
            logger.info(f"Search returned {len(results)} results")
            if results:
                logger.info(f"First result content: {results[0].page_content}")
            
            # Assert with more detailed message
            assert len(results) > 0, f"No results returned from vector store for query: {query}"
            assert isinstance(results[0].page_content, str), "Invalid result format"
            assert "RAG" in results[0].page_content, "Result doesn't contain relevant content"
            
        except Exception as e:
            logger.error(f"Vector store search failed: {str(e)}")
            raise

    def test_qa_chain(self, vector_store):
        """Test QA chain functionality"""
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(model="gpt-4o-mini"),
            chain_type="stuff",
            retriever=vector_store.as_retriever()
        )
        response = qa_chain.run("What is RAG?")
        assert response, "No response from QA chain"
        assert len(response) > 10, "Response too short"

class TestMemory:
    def test_memory_usage(self):
        """Test memory usage during RAG operations"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform RAG operations
        embeddings = OpenAIEmbeddings()
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(SAMPLE_TEXT)
        vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            persist_directory="./test_chroma_db"
        )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        logger.info(f"Memory usage: Initial={initial_memory:.2f}MB, Final={final_memory:.2f}MB, Increase={memory_increase:.2f}MB")
        assert memory_increase < 1000, "Memory usage increased by more than 1GB"

    def test_memory_cleanup(self):
        """Test memory cleanup after RAG operations"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024

        # Create and delete vector store
        embeddings = OpenAIEmbeddings()
        vector_store = Chroma.from_texts(
            texts=[SAMPLE_TEXT],
            embedding=embeddings,
            persist_directory="./test_chroma_db"
        )
        del vector_store
        import gc
        gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_diff = final_memory - initial_memory

        logger.info(f"Memory after cleanup: Initial={initial_memory:.2f}MB, Final={final_memory:.2f}MB, Diff={memory_diff:.2f}MB")
        assert abs(memory_diff) < 100, "Significant memory not released after cleanup" 