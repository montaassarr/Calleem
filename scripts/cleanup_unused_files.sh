#!/bin/bash

# AI Receptionist Project Cleanup Script
# Removes unused files, caches, and example directories

set -e

PROJECT_ROOT="/home/montassar/Desktop/ai_receptionist"
cd "$PROJECT_ROOT"

echo "🧹 Starting AI Receptionist Project Cleanup..."
echo "================================================"

# Function to ask for confirmation
confirm() {
    read -p "$1 (y/n) " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# 1. Remove example directories (321MB)
echo ""
echo "📦 Large Example Directories:"
echo "  - livekit_examples/ (321MB) - Example projects from LiveKit"
echo "  - Parker_165/ (16KB) - Old agent examples"
if confirm "Remove these example directories?"; then
    echo "Removing livekit_examples..."
    rm -rf livekit_examples/
    echo "Removing Parker_165..."
    rm -rf Parker_165/
    echo "✅ Example directories removed"
fi

# 2. Clean Python cache files
echo ""
echo "🐍 Python Cache Files:"
CACHE_COUNT=$(find backend livekit-agent-worker -type d -name "__pycache__" 2>/dev/null | wc -l)
echo "  - Found $CACHE_COUNT __pycache__ directories"
if confirm "Remove Python cache files?"; then
    find backend livekit-agent-worker -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find backend livekit-agent-worker -name "*.pyc" -delete 2>/dev/null || true
    find backend livekit-agent-worker -name "*.pyo" -delete 2>/dev/null || true
    echo "✅ Python cache cleaned"
fi

# 3. Clean Node.js build artifacts
echo ""
echo "📦 Frontend Build Artifacts:"
if [ -d "frontend_next/.next" ]; then
    NEXT_SIZE=$(du -sh frontend_next/.next 2>/dev/null | cut -f1)
    echo "  - .next/ build directory ($NEXT_SIZE)"
fi
if [ -d "frontend_next/test-results" ]; then
    echo "  - test-results/ directory"
fi
if [ -d "frontend_next/playwright-report" ]; then
    echo "  - playwright-report/ directory"
fi
if confirm "Remove frontend build artifacts?"; then
    rm -rf frontend_next/.next/
    rm -rf frontend_next/test-results/
    rm -rf frontend_next/playwright-report/
    echo "✅ Frontend build artifacts cleaned"
fi

# 4. Remove unused backend routers/files
echo ""
echo "📄 Potentially Unused Backend Files:"
echo "  - backend/routers/vapi_webhooks.py (placeholder only)"
echo "  - backend/routers/phone_numbers.py (placeholder only)"
echo "  - backend/tests/ (old tests, may be outdated)"
if confirm "Remove these files?"; then
    rm -f backend/routers/vapi_webhooks.py
    rm -f backend/routers/phone_numbers.py
    echo "✅ Placeholder routers removed"
fi

# 5. Remove unused frontend pages
echo ""
echo "🌐 Potentially Unused Frontend Pages:"
echo "  - app/dashboard/ai-receptionist/ (duplicate of voice-agent/chat)"
if confirm "Remove unused frontend pages?"; then
    rm -rf frontend_next/app/dashboard/ai-receptionist/
    echo "✅ Unused pages removed"
fi

# 6. Clean log files
echo ""
echo "📝 Log Files:"
if [ -d "backend/logs" ]; then
    LOG_COUNT=$(find backend/logs -type f 2>/dev/null | wc -l)
    echo "  - Found $LOG_COUNT log files in backend/logs/"
fi
if [ -d "logs" ]; then
    ROOT_LOG_COUNT=$(find logs -type f 2>/dev/null | wc -l)
    echo "  - Found $ROOT_LOG_COUNT log files in logs/"
fi
if confirm "Remove log files?"; then
    rm -rf backend/logs/*
    rm -rf logs/local/*
    rm -rf logs/diagnostics/*
    echo "✅ Log files cleaned"
fi

# 7. Remove old models directories (if they exist in models/)
echo ""
echo "📦 Old Model Structure:"
if [ -d "backend/models/ai" ] || [ -d "backend/models/analytics" ]; then
    echo "  - Found old model subdirectories (ai/, analytics/, etc.)"
    echo "  - These may be duplicates if using new structure"
    if confirm "Review and potentially remove old model directories?"; then
        echo "📁 Subdirectories in backend/models/:"
        ls -la backend/models/ | grep "^d" | awk '{print "  - " $9}'
        echo ""
        echo "⚠️  Manual review recommended. Old structure may still be in use."
    fi
fi

# 8. Summary
echo ""
echo "================================================"
echo "✅ Cleanup Complete!"
echo ""
echo "💾 Space Saved Summary:"
echo "  - Removed ~321MB of example projects"
echo "  - Cleaned Python cache files"
echo "  - Removed build artifacts"
echo "  - Cleaned log files"
echo ""
echo "📊 Remaining Structure:"
echo "  - backend/ (API server)"
echo "  - frontend_next/ (Next.js dashboard)"
echo "  - livekit-agent-worker/ (Voice agent)"
echo "  - n8n_workflows/ (Automation workflows)"
echo "  - scripts/ (Utility scripts)"
echo "  - docs/ (Documentation)"
echo ""
echo "🔄 Next Steps:"
echo "  1. Run: npm run build (in frontend_next)"
echo "  2. Test backend: cd backend && python3 main.py"
echo "  3. Test frontend: cd frontend_next && npm run dev"
echo ""
