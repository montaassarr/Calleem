#!/bin/bash
# AI Receptionist - Cleanup Script
# Removes old, unused, and redundant files safely

set -e

echo "🧹 AI Receptionist - Cleanup Script"
echo "===================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to safely remove file
remove_file() {
    if [ -f "$1" ]; then
        rm "$1"
        echo -e "${GREEN}✓${NC} Removed: $1"
    else
        echo -e "${YELLOW}⊘${NC} Not found: $1"
    fi
}

# Function to safely remove directory
remove_dir() {
    if [ -d "$1" ]; then
        rm -rf "$1"
        echo -e "${GREEN}✓${NC} Removed directory: $1"
    else
        echo -e "${YELLOW}⊘${NC} Not found: $1"
    fi
}

# Confirm with user
echo -e "${YELLOW}WARNING:${NC} This will remove old files and clean up the workspace."
echo "The following will be removed:"
echo "  - Windows-specific scripts (.ps1)"
echo "  - Old shell scripts"
echo "  - Redundant documentation"
echo "  - Log files"
echo "  - Python cache directories"
echo "  - Temporary files"
echo ""
read -p "Do you want to continue? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Starting cleanup..."
echo ""

# Remove Windows-specific files
echo "📁 Removing Windows-specific files..."
remove_file "install_enhanced.ps1"
remove_file "test_voice_endpoints.ps1"
remove_file "backend/venv/bin/Activate.ps1"
remove_file "venv/bin/Activate.ps1"

# Remove redundant documentation
echo ""
echo "📄 Removing redundant documentation..."
remove_file "README.old.md"
remove_file "README_V2.md"
remove_file "WINDOWS_STARTUP_GUIDE.md"

# Remove old scripts (will be replaced with new ones)
echo ""
echo "🔧 Removing old scripts..."
remove_file "setup.sh"
remove_file "setup_complete.sh"
remove_file "start.sh"
remove_file "start_local.sh"
remove_file "install_local.sh"
remove_file "check_appointment.sh"

# Remove temporary files
echo ""
echo "🗑️  Removing temporary files..."
remove_file "backend/ngrok-v3-stable-linux-amd64.tgz"

# Clean log files (keep directory structure)
echo ""
echo "📋 Cleaning log files..."
if [ -d "logs" ]; then
    rm -f logs/*.log
    echo -e "${GREEN}✓${NC} Cleaned logs/ directory"
fi
if [ -d "backend/logs" ]; then
    rm -f backend/logs/*.log
    echo -e "${GREEN}✓${NC} Cleaned backend/logs/ directory"
fi

# Remove Python cache directories
echo ""
echo "🐍 Removing Python cache directories..."
find . -type d -name "__pycache__" -not -path "./venv/*" -not -path "./backend/venv/*" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -not -path "./venv/*" -not -path "./backend/venv/*" -delete 2>/dev/null || true
echo -e "${GREEN}✓${NC} Removed Python cache files"

# Move utility scripts to a backup folder (don't delete, just organize)
echo ""
echo "📦 Moving utility scripts to scripts/ folder..."
mkdir -p scripts/legacy
scripts_to_move=(
    "check_db.py"
    "fix_config.py"
    "reset_vapi_assistant.py"
    "test_phase6.py"
    "test_vapi.py"
    "test_whatsapp.py"
    "verify_installation.py"
    "verify_setup.py"
)

for script in "${scripts_to_move[@]}"; do
    if [ -f "$script" ]; then
        mv "$script" "scripts/legacy/"
        echo -e "${GREEN}✓${NC} Moved: $script → scripts/legacy/"
    fi
done

# Remove old Docker files (backup first)
echo ""
echo "🐳 Backing up old Docker files..."
mkdir -p .docker-backup
if [ -f "docker-compose.yml" ]; then
    cp docker-compose.yml .docker-backup/docker-compose.yml.backup
    echo -e "${GREEN}✓${NC} Backed up: docker-compose.yml"
fi
if [ -f "backend/Dockerfile" ]; then
    cp backend/Dockerfile .docker-backup/Dockerfile.backend.backup
    echo -e "${GREEN}✓${NC} Backed up: backend/Dockerfile"
fi
if [ -f "frontend/Dockerfile" ]; then
    cp frontend/Dockerfile .docker-backup/Dockerfile.frontend.backup
    echo -e "${GREEN}✓${NC} Backed up: frontend/Dockerfile"
fi

echo ""
echo -e "${GREEN}✅ Cleanup completed successfully!${NC}"
echo ""
echo "Summary:"
echo "  - Old files removed"
echo "  - Python cache cleaned"
echo "  - Utility scripts moved to scripts/legacy/"
echo "  - Old Docker files backed up to .docker-backup/"
echo ""
echo "Next steps:"
echo "  1. Review the new Docker architecture files"
echo "  2. Configure your .env files"
echo "  3. Run ./start-dev.sh to start in development mode"
echo ""
