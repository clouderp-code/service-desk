import os
import argparse
from rag.initialize_rag import RAGInitializer
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Initialize RAG system with PDF files')
    parser.add_argument('--pdf-dir', type=str, default='/app/data',
                      help='Directory containing PDF files')
    parser.add_argument('--db-dir', type=str, default='/app/chroma_db',
                      help='Directory for the vector store')
    args = parser.parse_args()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        return
    
    # Initialize RAG
    initializer = RAGInitializer(args.pdf_dir, args.db_dir)
    
    # Get initial store info
    print("\nCurrent store info:")
    print(initializer.get_store_info())
    
    # Initialize vector store
    print("\nInitializing vector store...")
    success = initializer.initialize_vector_store()
    
    if success:
        print("\nVector store initialized successfully!")
        print("\nUpdated store info:")
        print(initializer.get_store_info())
    else:
        print("\nFailed to initialize vector store")

if __name__ == "__main__":
    main() 