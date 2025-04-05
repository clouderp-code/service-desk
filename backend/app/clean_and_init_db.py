import shutil
import os
from pathlib import Path
from typing import Optional
import logging
from app.rag.initialize_rag import RAGInitializer
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def close_existing_connections(db_path: str):
    """Close any existing Chroma connections"""
    try:
        # Initialize Chroma client
        vector_store = Chroma(
            persist_directory=db_path,
            embedding_function=OpenAIEmbeddings()
        )
        # Explicitly close the client
        vector_store._client.close()
        logger.info("Closed existing Chroma connections")
    except Exception as e:
        logger.warning(f"Error closing Chroma connections: {e}")

def clean_vector_store(db_path: str) -> bool:
    """Clean the vector store directory"""
    try:
        db_dir = Path(db_path)
        if db_dir.exists():
            # Close any existing connections first
            close_existing_connections(db_path)
            
            # Add a small delay to ensure connections are closed
            import time
            time.sleep(2)
            
            logger.info(f"Removing existing vector store at {db_path}")
            shutil.rmtree(db_path, ignore_errors=True)
            logger.info("Vector store removed successfully")
        return True
    except Exception as e:
        logger.error(f"Error cleaning vector store: {e}")
        return False

def verify_pdf_directory(pdf_path: str) -> Optional[list]:
    """Verify PDF directory exists and contains PDF files"""
    try:
        pdf_dir = Path(pdf_path)
        if not pdf_dir.exists():
            logger.error(f"PDF directory does not exist: {pdf_path}")
            return None
            
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.error(f"No PDF files found in {pdf_path}")
            return None
            
        logger.info(f"Found {len(pdf_files)} PDF files: {[f.name for f in pdf_files]}")
        return pdf_files
    except Exception as e:
        logger.error(f"Error verifying PDF directory: {e}")
        return None

def main():
    # Load environment variables
    load_dotenv()
    
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment variables")
        return False
        
    # Configure paths
    pdf_dir = "/app/data"
    db_dir = "/app/chroma_db"
    
    # Verify PDF directory
    if not verify_pdf_directory(pdf_dir):
        return False
    
    # Clean existing vector store
    if not clean_vector_store(db_dir):
        return False
    
    # Initialize RAG
    logger.info("Initializing new vector store...")
    initializer = RAGInitializer(pdf_dir=pdf_dir, db_dir=db_dir)
    
    # Get initial state
    initial_info = initializer.get_store_info()
    logger.info(f"Initial state: {initial_info}")
    
    # Initialize vector store
    success = initializer.initialize_vector_store()
    if not success:
        logger.error("Failed to initialize vector store")
        return False
    
    # Get final state
    final_info = initializer.get_store_info()
    logger.info(f"Final state: {final_info}")
    
    # Verify initialization
    if final_info["total_documents"] > 0:
        logger.info("Vector store initialized successfully!")
        logger.info(f"Processed {len(final_info['pdf_files'])} PDF files")
        logger.info(f"Created {final_info['total_documents']} document chunks")
        return True
    else:
        logger.error("Vector store initialization failed - no documents created")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean and reinitialize vector store')
    parser.add_argument('--force', action='store_true', 
                      help='Force reinitialization without confirmation')
    
    args = parser.parse_args()
    
    if not args.force:
        confirm = input("This will delete the existing vector store. Continue? [y/N] ")
        if confirm.lower() != 'y':
            logger.info("Operation cancelled")
            exit(0)
    
    success = main()
    exit(0 if success else 1) 