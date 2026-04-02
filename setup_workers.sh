#!/bin/bash

# Cloudflare Workers/Pages Deployment Setup Script
# Automates setup for deploying to Cloudflare

set -e

echo "☁️  Cloudflare Workers/Pages Setup"
echo "===================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo "✅ npm found: $(npm --version)"

# Install Wrangler
echo ""
echo "📦 Installing Wrangler CLI..."
npm install -g wrangler
echo "✅ Wrangler installed"

# Create package.json if not exists
if [ ! -f "package.json" ]; then
    echo ""
    echo "📝 Creating package.json..."
    npm init -y
fi

# Login to Cloudflare
echo ""
echo "🔐 Logging in to Cloudflare..."
echo "Opening browser for authentication..."
wrangler login

# Show account info
echo ""
echo "📊 Your Cloudflare Account:"
wrangler whoami

# Get account ID
echo ""
read -p "Enter your Cloudflare Account ID (from 'wrangler whoami'): " ACCOUNT_ID

# Create/Update wrangler.toml
echo ""
echo "⚙️  Configuring wrangler.toml..."

cat > wrangler.toml << EOF
name = "rootrush"
main = "src/index.js"
compatibility_date = "2024-04-01"
account_id = "$ACCOUNT_ID"
workers_dev = true

[env.development]
name = "rootrush-dev"
vars = { ENVIRONMENT = "development" }

[env.staging]
name = "rootrush-staging"
vars = { ENVIRONMENT = "staging" }

[env.production]
name = "rootrush"
vars = { ENVIRONMENT = "production" }
EOF

echo "✅ wrangler.toml created"

# Create functions directory
mkdir -p functions
echo "✅ Created functions directory"

# Set environment variables
echo ""
echo "🔐 Setting up environment variables..."
echo ""

read -p "Enter your backend API URL (e.g., https://api.example.com): " BACKEND_URL
read -sp "Enter HUGGINGFACE_API_TOKEN: " HF_TOKEN
echo ""
read -sp "Enter FLASK_SECRET_KEY: " FLASK_SECRET

wrangler secret put BACKEND_URL --env production < <(echo "$BACKEND_URL")
wrangler secret put HUGGINGFACE_API_TOKEN --env production < <(echo "$HF_TOKEN")
wrangler secret put FLASK_SECRET_KEY --env production < <(echo "$FLASK_SECRET")

echo "✅ Secrets configured"

# Test locally
echo ""
echo "🧪 Testing Workers locally..."
read -p "Run 'wrangler dev' to test? (y/n): " test_local

if [ "$test_local" = "y" ]; then
    echo ""
    echo "Starting local development server..."
    echo "Visit: http://localhost:8787"
    wrangler dev --env development
fi

# Deploy instructions
echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Update your backend URL in BACKEND_URL secret"
echo "2. Configure your custom domain in Cloudflare dashboard"
echo "3. Deploy: wrangler deploy --env production"
echo "4. View logs: wrangler tail --env production"
echo ""
echo "📚 Documentation:"
echo "   - See: CLOUDFLARE_WORKERS_PAGES.md"
echo ""
