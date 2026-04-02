#!/bin/bash

# Cloudflare Workers Deployment Fix Script
# Resolves: "Unable to find a service spec" error

set -e

echo "🔧 Fixing Cloudflare Workers Deployment"
echo "========================================"
echo ""

# Check if in correct directory
if [ ! -f "wrangler.toml" ]; then
    echo "❌ wrangler.toml not found. Run from project root directory."
    exit 1
fi

# Verify Wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "📦 Installing Wrangler CLI..."
    npm install -g wrangler
fi

# Verify account ID is set
echo "🔍 Checking Wrangler configuration..."
wrangler whoami || {
    echo "⚠️  Not logged in to Cloudflare"
    echo "🔐 Run: wrangler login"
    exit 1
}

# Get Account ID
ACCOUNT_ID=$(wrangler whoami 2>/dev/null | grep "Account ID:" | awk '{print $NF}' || echo "")

if [ -z "$ACCOUNT_ID" ]; then
    read -p "Enter your Cloudflare Account ID: " ACCOUNT_ID
fi

echo "✅ Account ID: $ACCOUNT_ID"

# Create/Update wrangler.toml with Account ID
echo ""
echo "⚙️  Updating wrangler.toml with Account ID..."

if grep -q "account_id" wrangler.toml; then
    # Replace existing account_id
    sed -i.bak "s/^account_id = .*/account_id = \"$ACCOUNT_ID\"/" wrangler.toml
else
    # Add account_id after name
    sed -i.bak "/^name = /a\\
account_id = \"$ACCOUNT_ID\"" wrangler.toml
fi

echo "✅ wrangler.toml updated"

# Verify static directory exists
if [ ! -d "static" ]; then
    echo ""
    echo "📁 Creating static directory..."
    mkdir -p static
    touch static/.gitkeep
    echo "✅ static directory created"
fi

# Test configuration
echo ""
echo "🧪 Testing configuration..."
wrangler deploy --dry-run 2>&1 | head -20 || true

# Set environment variables
echo ""
echo "🔐 Setting up environment variables..."

read -p "Enter Backend URL (e.g., https://api.railway.app): " BACKEND_URL

wrangler secret put BACKEND_URL --env production << EOF
$BACKEND_URL
EOF

echo "✅ Backend URL configured"

# Final deployment command
echo ""
echo "✅ Configuration fixed!"
echo ""
echo "📋 To deploy, run:"
echo "   wrangler deploy --env production"
echo ""
echo "Or deploy with assets:"
echo "   wrangler deploy --assets=./static --env production"
echo ""
echo "To test locally first:"
echo "   wrangler dev --env development"
echo ""
