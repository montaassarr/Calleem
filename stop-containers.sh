#!/bin/bash

# Script to stop Docker containers for AI Receptionist
# Usage: ./stop-containers.sh [service_name]
# If no service_name is provided, all services will be stopped

echo "🛑 Stopping AI Receptionist Docker containers..."

if [ -z "$1" ]; then
    # Stop all services
    docker-compose down
    echo "✅ All services stopped"
else
    # Stop specific service
    docker-compose stop "$1"
    echo "✅ Service '$1' stopped"
fi

echo ""
echo "📊 Container status:"
docker-compose ps
