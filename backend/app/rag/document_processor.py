import os
from typing import List, Optional
import logging
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        logger.info(f"Initialized DocumentProcessor with persist_directory: {persist_directory}")

    def process_pdf(self, file_path: str) -> Optional[List[Document]]:
        """Process a single PDF file with detailed error handling."""
        steps_completed = []
        try:
            # Step 1: Verify file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            steps_completed.append("file_verified")

            # Step 2: Load PDF
            loader = PyPDFLoader(file_path)
            steps_completed.append("loader_created")

            # Step 3: Extract text
            documents = loader.load()
            if not documents:
                raise ValueError("No text extracted from PDF")
            steps_completed.append("text_extracted")
            logger.info(f"Extracted {len(documents)} pages from {file_path}")

            # Step 4: Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            if not chunks:
                raise ValueError("No chunks created from documents")
            steps_completed.append("chunks_created")
            logger.info(f"Created {len(chunks)} chunks")

            # Log success
            logger.info(f"Successfully processed {file_path}")
            logger.info(f"Steps completed: {', '.join(steps_completed)}")
            
            return chunks

        except Exception as e:
            logger.error(f"Error processing {file_path}")
            logger.error(f"Error occurred at step: {steps_completed[-1] if steps_completed else 'start'}")
            logger.error(f"Error details: {str(e)}")
            logger.error(f"Steps completed before error: {', '.join(steps_completed)}")
            return None

    def process_directory(self, directory_path: str) -> List[Document]:
        """Process all PDFs in a directory with detailed logging."""
        all_chunks = []
        processed_files = []
        failed_files = []

        try:
            pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]
            logger.info(f"Found {len(pdf_files)} PDF files in {directory_path}")

            for filename in pdf_files:
                file_path = os.path.join(directory_path, filename)
                logger.info(f"Processing {filename}")
                
                chunks = self.process_pdf(file_path)
                if chunks:
                    all_chunks.extend(chunks)
                    processed_files.append(filename)
                else:
                    failed_files.append(filename)

            logger.info(f"Successfully processed files: {processed_files}")
            if failed_files:
                logger.error(f"Failed to process files: {failed_files}")

            return all_chunks

        except Exception as e:
            logger.error(f"Error processing directory: {str(e)}")
            return []

    def create_or_update_vectorstore(self, documents: List[Document]):
        """Create or update the vector store with documents."""
        try:
            if not documents:
                logger.error("No documents provided to create_or_update_vectorstore")
                return None

            logger.info(f"Creating vector store with {len(documents)} documents")
            logger.info(f"Using persist directory: {self.persist_directory}")
            
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            logger.info("Persisting vector store")
            vectorstore.persist()
            
            logger.info("Vector store successfully created and persisted")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}", exc_info=True)
            return None 