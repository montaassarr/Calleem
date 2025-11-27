#!/bin/bash

# CallFlow AI - One-Click Deploy to Railway
# This script automates the deployment process to Railway

set -e  # Exit on error

echo "🚀 CallFlow AI - Railway Deployment Script"
echo "=========================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "📝 Logging in to Railway..."
railway login

# Create new project or link existing
echo ""
echo "Do you want to:"
echo "1) Create a new Railway project"
echo "2) Link to an existing project"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    echo "🆕 Creating new Railway project..."
    railway init
else
    echo "🔗 Linking to existing project..."
    railway link
fi

# Create services
echo ""
echo "📦 Setting up services..."

# Backend service
echo "Setting up Backend (FastAPI)..."
railway service create backend

# Frontend service
echo "Setting up Frontend (Next.js)..."
railway service create frontend

# MongoDB (optional - can use Atlas)
read -p "Do you want to add MongoDB to Railway? (y/n): " add_mongo
if [ "$add_mongo" == "y" ]; then
    railway add mongodb
    echo "✅ MongoDB added"
else
    echo "ℹ️  Using external MongoDB Atlas"
fi

# Set environment variables for backend
echo ""
echo "🔧 Configuring Backend environment variables..."
echo "Please provide the following values:"

read -p "MONGO_URI: " MONGO_URI
read -p "SECRET_KEY (or press Enter to generate): " SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 32)
    echo "Generated SECRET_KEY: $SECRET_KEY"
fi

read -p "STRIPE_SECRET_KEY: " STRIPE_SECRET_KEY
read -p "TWILIO_ACCOUNT_SID: " TWILIO_ACCOUNT_SID
read -p "TWILIO_AUTH_TOKEN: " TWILIO_AUTH_TOKEN
read -p "RESEND_API_KEY: " RESEND_API_KEY
read -p "N8N_API_KEY: " N8N_API_KEY

# Set backend environment variables
railway service backend
railway variables set MONGO_URI="$MONGO_URI"
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set JWT_SECRET_KEY="$(openssl rand -hex 32)"
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="false"
railway variables set STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY"
railway variables set TWILIO_ACCOUNT_SID="$TWILIO_ACCOUNT_SID"
railway variables set TWILIO_AUTH_TOKEN="$TWILIO_AUTH_TOKEN"
railway variables set RESEND_API_KEY="$RESEND_API_KEY"
railway variables set N8N_API_KEY="$N8N_API_KEY"

echo "✅ Backend environment variables set"

# Set environment variables for frontend
echo ""
echo "🔧 Configuring Frontend environment variables..."
read -p "STRIPE_PUBLIC_KEY: " STRIPE_PUBLIC_KEY

railway service frontend
railway variables set NEXT_PUBLIC_API_URL="https://backend.railway.app/api/v1"
railway variables set NEXT_PUBLIC_STRIPE_PUBLIC_KEY="$STRIPE_PUBLIC_KEY"

echo "✅ Frontend environment variables set"

# Configure build settings
echo ""
echo "⚙️  Configuring build settings..."

# Backend build settings
railway service backend
cat > railway.backend.json <<EOF
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port \$PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

# Frontend build settings
railway service frontend
cat > railway.frontend.json <<EOF
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd frontend_next && npm install && npm run build"
  },
  "deploy": {
    "startCommand": "cd frontend_next && npm start",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
EOF

echo "✅ Build settings configured"

# Deploy
echo ""
echo "🚀 Deploying to Railway..."
read -p "Ready to deploy? (y/n): " deploy_confirm

if [ "$deploy_confirm" == "y" ]; then
    # Deploy backend
    echo "Deploying backend..."
    railway service backend
    railway up --detach
    
    # Deploy frontend
    echo "Deploying frontend..."
    railway service frontend
    railway up --detach
    
    echo ""
    echo "✅ Deployment initiated!"
    echo ""
    echo "📊 Monitor your deployment:"
    echo "   railway logs --tail"
    echo ""
    echo "🌐 Your app will be available at:"
    railway domain
    
    echo ""
    echo "🎉 Deployment complete!"
    echo ""
    echo "Next steps:"
    echo "1. Configure custom domain in Railway dashboard"
    echo "2. Update CORS settings with your domain"
    echo "3. Test the application"
    echo "4. Set up monitoring and alerts"
else
    echo "❌ Deployment cancelled"
fi

echo ""
echo "=========================================="
echo "For more info: https://docs.railway.app"
