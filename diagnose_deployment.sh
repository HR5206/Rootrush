#!/bin/bash

# Cloudflare Workers Diagnostics & Fix Script
# Helps diagnose and fix "Backend URL not configured" error

set -e

echo "🔍 Cloudflare Workers Diagnostics"
echo "=================================="
echo ""

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler not installed. Run: npm install -g wrangler"
    exit 1
fi

echo "✅ Wrangler installed"

# Check if logged in
if ! wrangler whoami &> /dev/null; then
    echo "❌ Not logged in to Cloudflare. Run: wrangler login"
    exit 1
fi

ACCOUNT_ID=$(wrangler whoami 2>/dev/null | grep "Account ID:" | awk '{print $NF}' || echo "unknown")
echo "✅ Logged in to Cloudflare (Account: $ACCOUNT_ID)"

# Check wrangler.toml
echo ""
echo "📋 Checking wrangler.toml..."
if [ ! -f "wrangler.toml" ]; then
    echo "❌ wrangler.toml not found"
    exit 1
fi

# Check required fields
if grep -q "type = \"service\"" wrangler.toml; then
    echo "✅ type = service"
else
    echo "❌ Missing: type = \"service\""
fi

if grep -q "account_id" wrangler.toml; then
    echo "✅ account_id configured"
else
    echo "❌ Missing: account_id"
fi

if grep -q "main = " wrangler.toml; then
    echo "✅ main entry point configured"
else
    echo "❌ Missing: main entry point"
fi

# Check Worker file
echo ""
echo "📄 Checking Worker file..."
if [ -f "functions/[[path]].js" ]; then
    echo "✅ functions/[[path]].js exists"
else
    echo "❌ functions/[[path]].js not found"
    exit 1
fi

# Check for BACKEND_URL secret
echo ""
echo "🔐 Checking BACKEND_URL secret..."
SECRETS=$(wrangler secret list --env production 2>/dev/null)

if echo "$SECRETS" | grep -q "BACKEND_URL"; then
    echo "✅ BACKEND_URL secret is set"
else
    echo "❌ BACKEND_URL secret is NOT set"
    echo ""
    echo "📝 To fix, run:"
    echo "   wrangler secret put BACKEND_URL --env production"
    echo ""
    echo "Then enter your backend URL (examples):"
    echo "   - https://your-project.railway.app"
    echo "   - https://your-app.herokuapp.com"
    echo "   - https://api.yourdomain.com"
fi

# Check static directory
echo ""
echo "📁 Checking static directory..."
if [ -d "static" ]; then
    echo "✅ static directory exists"
else
    echo "⚠️  static directory not found"
    echo "   Creating: mkdir -p static"
    mkdir -p static
fi

# List recent deployments
echo ""
echo "📊 Recent deployments:"
wrangler deployments list --env production 2>/dev/null | head -5 || echo "Unable to list deployments"

# Show action items
echo ""
echo "🎯 ACTION ITEMS:"
echo ""

if ! echo "$SECRETS" | grep -q "BACKEND_URL"; then
    echo "1️⃣  SET BACKEND_URL SECRET:"
    echo "   wrangler secret put BACKEND_URL --env production"
    echo "   Then paste your backend URL"
    echo ""
fi

echo "2️⃣  REDEPLOY:"
echo "   wrangler deploy --env production"
echo ""

echo "3️⃣  MONITOR:"
echo "   wrangler tail --env production"
echo ""

echo "4️⃣  TEST:"
echo "   Visit: https://yourdomain.com"
echo ""

# Check health
echo "💡 To view logs in real-time:"
echo "   wrangler tail --env production"
echo ""

echo "✅ Diagnostics complete!"
