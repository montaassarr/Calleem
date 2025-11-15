#!/bin/bash

# AI Receptionist - Complete Setup Script
# This script sets up the entire project from scratch

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   🤖 AI Receptionist - Complete Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print step
print_step() {
    echo -e "${YELLOW}━━━ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 1. Check Prerequisites
print_step "Step 1: Checking Prerequisites"

MISSING_DEPS=()

if ! command_exists python3; then
    MISSING_DEPS+=("python3 (3.10 or higher)")
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION installed"
fi

if ! command_exists node; then
    MISSING_DEPS+=("node.js (18 or higher)")
else
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION installed"
fi

if ! command_exists npm; then
    MISSING_DEPS+=("npm")
else
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION installed"
fi

if ! command_exists mongod && ! command_exists mongo && ! command_exists mongosh; then
    MISSING_DEPS+=("MongoDB")
else
    print_success "MongoDB installed"
fi

if ! command_exists git; then
    MISSING_DEPS+=("git")
else
    print_success "Git installed"
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    print_error "Missing required dependencies:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "  - $dep"
    done
    echo ""
    echo "Please install missing dependencies and run setup again."
    echo "See INSTALLATION.md for detailed instructions."
    exit 1
fi

print_success "All prerequisites installed!"
echo ""

# 2. Check MongoDB is running
print_step "Step 2: Checking MongoDB Service"

if pgrep -x mongod > /dev/null; then
    print_success "MongoDB is running"
elif systemctl is-active --quiet mongod 2>/dev/null; then
    print_success "MongoDB is running (systemd)"
else
    print_error "MongoDB is not running"
    echo "Starting MongoDB..."
    if command_exists systemctl; then
        sudo systemctl start mongod || print_error "Failed to start MongoDB. Please start it manually."
    else
        print_error "Please start MongoDB manually: sudo systemctl start mongod"
        exit 1
    fi
fi

# Test MongoDB connection
if mongosh --eval "db.adminCommand('ping')" --quiet > /dev/null 2>&1; then
    print_success "MongoDB connection successful"
elif mongo --eval "db.adminCommand('ping')" --quiet > /dev/null 2>&1; then
    print_success "MongoDB connection successful"
else
    print_error "Cannot connect to MongoDB"
    print_info "Make sure MongoDB is running on localhost:27017"
    exit 1
fi
echo ""

# 3. Setup Python Virtual Environment
print_step "Step 3: Setting up Python Virtual Environment"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
source .venv/bin/activate
print_success "Virtual environment activated"
echo ""

# 4. Install Python Dependencies
print_step "Step 4: Installing Python Dependencies"

cd backend
pip install --upgrade pip > /dev/null 2>&1
print_info "Installing backend dependencies (this may take a few minutes)..."
pip install -r requirements.txt
print_success "Backend dependencies installed"
cd ..
echo ""

# 5. Install Frontend Dependencies
print_step "Step 5: Installing Frontend Dependencies"

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_info "Installing frontend dependencies (this may take a few minutes)..."
    npm install
    print_success "Frontend dependencies installed"
else
    print_info "node_modules already exists. Run 'npm install' to update if needed."
fi

cd ..
echo ""

# 6. Setup Environment Variables
print_step "Step 6: Setting up Environment Variables"

if [ ! -f "backend/.env" ]; then
    print_info "Creating .env file from template..."
    
    # Generate a secure random SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
    
    cat > backend/.env << EOF
# Application Settings
APP_NAME="AI Barber Receptionist"
DEBUG=True
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ai_barber_receptionist

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# WhatsApp Cloud API
WHATSAPP_API_URL=https://graph.facebook.com/v22.0
WHATSAPP_PHONE_NUMBER_ID=YOUR_PHONE_NUMBER_ID_HERE
WHATSAPP_ACCESS_TOKEN=REDACTED
WHATSAPP_VERIFY_TOKEN=YOUR_VERIFY_TOKEN_HERE
WHATSAPP_BUSINESS_PHONE=+1234567890

# Groq AI
GROQ_API_KEY=REDACTED
GROQ_MODEL=llama-3.3-70b-versatile

# Business Settings
BUSINESS_NAME="Your Barber Shop"
BUSINESS_PHONE=+1234567890
BUSINESS_EMAIL=contact@yourbarbershop.com
BUSINESS_ADDRESS="123 Main St, City, State 12345"

# Default Admin User (for initial setup)
ADMIN_EMAIL=admin@example.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme123
EOF

    print_success ".env file created"
    print_error "⚠️  IMPORTANT: Edit backend/.env and add your API keys:"
    echo "   - WHATSAPP_PHONE_NUMBER_ID"
    echo "   - WHATSAPP_ACCESS_TOKEN"
    echo "   - WHATSAPP_VERIFY_TOKEN"
    echo "   - GROQ_API_KEY"
    echo "   - Change ADMIN_PASSWORD"
else
    print_info ".env file already exists"
fi
echo ""

# 7. Initialize Database
print_step "Step 7: Initializing Database"

print_info "Creating database and collections..."
mongosh ai_barber_receptionist --quiet --eval "
db.createCollection('users');
db.createCollection('conversations');
db.createCollection('appointments');
db.createCollection('services');
print('Collections created');
" || print_error "Failed to create collections (they may already exist)"

print_success "Database initialized"
echo ""

# 8. Setup Default Services
print_step "Step 8: Creating Default Services"

mongosh ai_barber_receptionist --quiet --eval "
if (db.services.countDocuments() === 0) {
    db.services.insertMany([
        {
            service_id: 'srv_haircut_001',
            name: 'Haircut',
            description: 'Professional haircut and styling',
            duration_minutes: 30,
            price: 35.00,
            active: true,
            created_at: new Date(),
            updated_at: new Date()
        },
        {
            service_id: 'srv_shave_001',
            name: 'Beard Trim',
            description: 'Beard trimming and shaping',
            duration_minutes: 20,
            price: 25.00,
            active: true,
            created_at: new Date(),
            updated_at: new Date()
        },
        {
            service_id: 'srv_combo_001',
            name: 'Haircut & Beard',
            description: 'Complete haircut and beard service',
            duration_minutes: 45,
            price: 50.00,
            active: true,
            created_at: new Date(),
            updated_at: new Date()
        }
    ]);
    print('Services created');
} else {
    print('Services already exist');
}
" || print_error "Failed to create services"

print_success "Default services configured"
echo ""

# 9. Make scripts executable
print_step "Step 9: Setting up executable scripts"

chmod +x start.sh 2>/dev/null || true
chmod +x setup.sh 2>/dev/null || true
chmod +x run_tests.sh 2>/dev/null || true
chmod +x test_system.sh 2>/dev/null || true
chmod +x system_check.sh 2>/dev/null || true
chmod +x watch_logs.sh 2>/dev/null || true
chmod +x check_appointment.sh 2>/dev/null || true
chmod +x test_name_extraction.sh 2>/dev/null || true

print_success "Scripts are executable"
echo ""

# 10. Create admin user (optional)
print_step "Step 10: Creating Admin User"

if [ -f "backend/create_admin.py" ]; then
    cd backend
    python create_admin.py 2>/dev/null || print_info "Admin user may already exist"
    cd ..
    print_success "Admin user setup complete"
else
    print_info "Skipping admin user creation (script not found)"
fi
echo ""

# Final Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo ""
echo "1. Configure API Keys:"
echo "   Edit: backend/.env"
echo "   Add your WhatsApp and Groq API keys"
echo ""
echo "2. Start the application:"
echo "   ./start.sh"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "4. Test the system:"
echo "   ./system_check.sh"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "   - README.md - Project overview"
echo "   - INSTALLATION.md - Detailed installation guide"
echo "   - COMPLETE_FIX_README.md - Testing and troubleshooting"
echo "   - docs/ - Additional documentation"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""
