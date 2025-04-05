import os
import logging
from typing import List, Dict
from pathlib import Path
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGInitializer:
    def __init__(self, pdf_dir: str, db_dir: str):
        self.pdf_dir = Path(pdf_dir)
        self.db_dir = Path(db_dir)
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
    def load_pdfs(self) -> List[Dict]:
        """Load all PDFs from the directory and return their chunks."""
        all_chunks = []
        
        if not self.pdf_dir.exists():
            logger.error(f"PDF directory {self.pdf_dir} does not exist")
            return all_chunks
            
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.pdf_dir}")
            return all_chunks
            
        for pdf_path in pdf_files:
            try:
                logger.info(f"Processing {pdf_path}")
                loader = PyPDFLoader(str(pdf_path))
                pages = loader.load()
                chunks = self.text_splitter.split_documents(pages)
                all_chunks.extend(chunks)
                logger.info(f"Successfully processed {pdf_path}: {len(chunks)} chunks created")
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {str(e)}")
                
        return all_chunks
        
    def initialize_vector_store(self) -> bool:
        """Initialize the vector store with PDF contents."""
        try:
            # Create db directory if it doesn't exist
            self.db_dir.mkdir(parents=True, exist_ok=True)
            
            # Load and chunk PDFs
            chunks = self.load_pdfs()
            if not chunks:
                logger.warning("No chunks created from PDFs")
                return False
                
            # Create or update vector store
            logger.info(f"Creating vector store in {self.db_dir}")
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=str(self.db_dir)
            )
            vector_store.persist()
            
            logger.info(f"Successfully initialized vector store with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            return False
            
    def get_store_info(self) -> Dict:
        """Get information about the current vector store."""
        try:
            vector_store = Chroma(
                persist_directory=str(self.db_dir),
                embedding_function=self.embeddings
            )
            
            return {
                "total_documents": len(vector_store.get()["ids"]),
                "pdf_files": [f.name for f in self.pdf_dir.glob("*.pdf")],
                "db_location": str(self.db_dir)
            }
        except Exception as e:
            logger.error(f"Error getting store info: {str(e)}")
            return {
                "error": str(e),
                "total_documents": 0,
                "pdf_files": [],
                "db_location": str(self.db_dir)
            } 