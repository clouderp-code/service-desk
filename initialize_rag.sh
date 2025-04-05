# Initialize with default directories
docker-compose exec backend python app/initialize_db.py

# Or specify custom directories
#docker-compose exec backend python app/initialize_db.py --pdf-dir /custom/pdf/dir --db-dir /custom/db/dir

# Initialize RAG with curl
#curl -X POST http://localhost:8000/api/initialize-rag