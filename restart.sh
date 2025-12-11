#!/bin/bash

echo "Restarting containers with fresh build..."
echo ""

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Restart containers
docker-compose down
docker-compose up -d --build --force-recreate

echo ""
echo "✅ Containers restarted!"
echo "Test the sync API: POST http://localhost:8005/api/earthquakes/sync"
