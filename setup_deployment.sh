#!/bin/bash

# Rootrush Deployment Setup Script
# Automates initial setup for Cloudflare/Railway/Heroku deployment

set -e

echo "🚀 Rootrush Deployment Setup"
echo "============================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo ""
echo "📦 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate 2>/dev/null || true

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Setup environment file
echo ""
echo "🔐 Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created from template"
    echo "   📝 Edit .env file with your actual values before deployment"
else
    echo "✅ .env file already exists"
fi

# Create directories if needed
echo ""
echo "📁 Creating required directories..."
mkdir -p logs
mkdir -p instance
echo "✅ Directories created"

# Test Flask app locally
echo ""
echo "🧪 Testing Flask app locally..."
python3 -c "from app import create_app; app = create_app(); print('✅ Flask app loads successfully')"

# Cloudflare setup prompt
echo ""
echo "☁️ Cloudflare Deployment Options"
echo "=================================="
echo ""
echo "Choose your deployment method:"
echo "1) Railway (⭐ Recommended - easiest)"
echo "2) Heroku (traditional)"
echo "3) Docker + Custom Cloud"
echo "4) Skip for now"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📚 Railway Setup Instructions:"
        echo "1. Install Railway CLI: npm install -g @railway/cli"
        echo "2. Login: railway login"
        echo "3. Create project: railway init"
        echo "4. Deploy: railway up"
        echo ""
        read -p "Install Railway CLI now? (y/n): " install_railway
        if [ "$install_railway" = "y" ]; then
            if command -v npm &> /dev/null; then
                npm install -g @railway/cli
                echo "✅ Railway CLI installed"
                railway login
            else
                echo "❌ npm not found. Please install Node.js"
            fi
        fi
        ;;
    2)
        echo ""
        echo "📚 Heroku Setup Instructions:"
        echo "1. Install Heroku CLI: brew install heroku"
        echo "2. Login: heroku login"
        echo "3. Create app: heroku create your-app-name"
        echo "4. Deploy: git push heroku main"
        ;;
    3)
        echo ""
        echo "📚 Docker Setup Instructions:"
        echo "1. Build: docker build -t rootrush ."
        echo "2. Test: docker run -p 8000:8000 rootrush"
        echo "3. Push to registry and deploy to cloud provider"
        ;;
    4)
        echo "⏭️  Skipping deployment setup for now"
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac

# Summary
echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env with your actual values"
echo "2. Test locally: flask run"
echo "3. Choose deployment method"
echo "4. Follow the instructions in CLOUDFLARE_DEPLOYMENT.md"
echo "5. Configure Cloudflare DNS"
echo ""
echo "📚 For detailed instructions, see: CLOUDFLARE_DEPLOYMENT.md"
echo "📝 For quick reference, see: DEPLOY_QUICKSTART.md"
echo ""
