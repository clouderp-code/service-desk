
# Stop all services

docker-compose down

docker builder prune -f

# Rebuild frontend with no-cache flag
docker-compose build --no-cache frontend

# Restart services
docker-compose up -d
