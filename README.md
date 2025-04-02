# AI Service Desk Agent

An AI-powered service desk solution that provides 24/7 customer support through an intelligent chatbot system. The system uses RAG (Retrieval Augmented Generation) to process PDF documents and maintain conversation context while providing accurate responses to customer inquiries.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development Setup](#development-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features
- Natural language understanding and processing
- Context-aware conversations with memory retention
- RAG-based knowledge base integration
- PDF document processing and analysis
- Multi-turn dialogue handling
- Automated ticket creation and routing
- Analytics and reporting dashboard

## Prerequisites
- Python 3.11.11
- Node.js 16+
- Docker and Docker Compose
- OpenAI API key
- Git

## Project Structure
service-desk/
├── backend/
│ ├── app/
│ │ ├── main.py
│ │ ├── utils/
│ │ │ └── pdf_processor.py
│ │ └── tests/
│ │ └── test_pdf_rag.py
│ ├── Dockerfile
│ ├── requirements.txt
│ └── pytest.ini
├── frontend/
│ ├── src/
│ │ ├── components/
│ │ ├── App.tsx
│ │ └── index.tsx
│ ├── Dockerfile
│ └── package.json
├── data/
├── docker-compose.yml
└── README.md

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd service-desk
```

2. Create necessary directories:
```bash
mkdir -p data chroma_db
```

3. Set up environment variables:
```bash
# Create .env file in project root
cp .env.example .env

# Add your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" >> .env
```

## Configuration

1. Backend Configuration (.env):
```env
OPENAI_API_KEY=your-api-key-here
PDF_DIRECTORY=/app/data
CHROMA_DIRECTORY=/app/chroma_db
```

2. Frontend Configuration (.env):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/chat/ws
```

## Running the Application

1. Build and start the containers:
```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

2. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Testing

### Backend Tests

1. Run all tests:
```bash
docker-compose exec backend pytest -v
```

2. Run specific test categories:
```bash
# PDF Processing tests
docker-compose exec backend pytest tests/test_pdf_rag.py -k TestPDFProcessing

# RAG tests
docker-compose exec backend pytest tests/test_pdf_rag.py -k TestRAG

# Memory tests
docker-compose exec backend pytest tests/test_pdf_rag.py -k TestMemory
```

3. Run tests with coverage:
```bash
docker-compose exec backend pytest --cov=app tests/
```

### Frontend Tests

1. Run unit tests:
```bash
docker-compose exec frontend npm test
```

2. Run E2E tests:
```bash
docker-compose exec frontend npm run cypress
```

## API Documentation

### Key Endpoints

1. PDF Processing:
```bash
# Process documents in data directory
curl -X POST http://localhost:8000/api/process-documents \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/app/data"}'
```

2. Chat:
```bash
# WebSocket endpoint for chat
ws://localhost:8000/api/chat/ws
```

3. Health Check:
```bash
curl http://localhost:8000/api/health
```

### Test Endpoints

1. Test PDF processing:
```bash
curl http://localhost:8000/api/test/pdf-info
```

2. Test RAG functionality:
```bash
curl http://localhost:8000/api/test/rag
```

## Troubleshooting

### Common Issues

1. Container Build Failures:
```bash
# Clean Docker cache
docker system prune -f

# Rebuild from scratch
docker-compose build --no-cache
```

2. Permission Issues:
```bash
# Fix data directory permissions
chmod -R 755 data/
chmod -R 755 chroma_db/
```

3. Connection Issues:
```bash
# Check container status
docker-compose ps

# Check container logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

4. Memory Issues:
```bash
# Check container memory usage
docker stats
```

### Debug Mode

1. Enable debug logging:
```bash
# In docker-compose.yml
environment:
  - LOG_LEVEL=DEBUG
```

2. Rebuild and restart:
```bash
docker-compose down
docker-compose up -d
```

## Development

### Local Development Setup

1. Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Code Style

- Backend: Follow PEP 8
- Frontend: Follow ESLint configuration

### Contributing

1. Create a feature branch
2. Make changes
3. Run tests
4. Submit pull request

## License

[Your License Here]

