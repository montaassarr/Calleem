#!/bin/bash
# Quick script to get your tenant_id and test endpoints

echo "🔍 Getting Your Tenant ID"
echo "=========================="
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend is not running!"
    echo ""
    echo "💡 Start the backend first:"
    echo "   ./start.sh"
    echo ""
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Run the Python test script
python3 test_tenant_config.py


