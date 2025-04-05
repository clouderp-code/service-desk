
# Stop all services

docker-compose down

# Rebuild the backend container
docker-compose build backend

# Restart services
docker-compose up -d

# Run tests
docker-compose exec backend pytest -v