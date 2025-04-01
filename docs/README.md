# AI Service Desk Agent

An AI-powered service desk solution that provides 24/7 customer support through an intelligent chatbot system. The system maintains conversation context, accesses a knowledge base, and provides accurate responses to customer inquiries.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Development Setup](#development-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Features
- Natural language understanding and processing
- Context-aware conversations with memory retention
- Knowledge base integration and management
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

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-service-desk.git
cd ai-service-desk
```

2. Create environment files:
```bash
# Create backend environment file
cp backend/.env.example backend/.env

# Create frontend environment file
cp frontend/.env.example frontend/.env
```

3. Configure environment variables:
```bash
# backend/.env
OPENAI_API_KEY=your_openai_api_key
ENVIRONMENT=development
DEBUG=True
```

## Development Setup

### Using Docker (Recommended)

1. Build and start the containers:
```bash
docker-compose build
docker-compose up -d
```

2. Check container status:
```bash
docker-compose ps
```

3. View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Manual Setup

#### Backend Setup
1. Create a Python virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Running the Application

After setup, the application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- ChromaDB: http://localhost:8001

## Environment Variables

### Backend Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `ENVIRONMENT`: development/production
- `DEBUG`: True/False
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key

### Frontend Variables
- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_WS_URL`: WebSocket URL

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Container not starting**
```bash
# Check container logs
docker-compose logs -f [service_name]
```

2. **Port conflicts**
```bash
# Check if ports are in use
netstat -ano | findstr "8000"  # Windows
lsof -i :8000                  # Linux/Mac
```

3. **Database connection issues**
- Verify environment variables
- Check if ChromaDB container is running
- Ensure proper network connectivity between containers

4. **OpenAI API issues**
- Verify API key in .env file
- Check API key permissions
- Monitor API usage and limits

### Maintenance

1. **Update dependencies**
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
npm update
```

2. **Clean up Docker**
```bash
# Remove unused containers and images
docker-compose down
docker system prune -f
```

3. **Reset ChromaDB data**
```bash
docker-compose down -v
docker-compose up -d
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[MIT License](LICENSE)
