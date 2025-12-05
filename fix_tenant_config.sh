#!/bin/bash
# Script to fix tenant configuration issues
# This ensures business_config exists for your tenant

echo "🔧 Fixing Tenant Configuration"
echo "=============================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Run the debug script
python3 debug_tenant_config.py

echo ""
echo "✅ Done! Check the output above."
echo ""
echo "If business_config was missing, it has been created."
echo "Now try testing the voice agent again."


