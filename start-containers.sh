#!/bin/bash

# Script to start Docker containers for AI Receptionist
# Usage: ./start-containers.sh [service_name]
# If no service_name is provided, all services will be started

echo "🚀 Starting AI Receptionist Docker containers..."

if [ -z "$1" ]; then
    # Start all services
    docker-compose up -d
    echo "✅ All services started"
else
    # Start specific service
    docker-compose up -d "$1"
    echo "✅ Service '$1' started"
fi

echo ""
echo "📊 Container status:"
docker-compose ps
