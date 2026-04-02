# Cloudflare Workers Deployment Fix

## ❌ Problem
```
Failed: error occurred while running deploy command
Unable to find a service spec in your configuration
```

## ✅ Solution

The error occurs because Wrangler can't find proper service configuration. Here are the fixes:

---

## Quick Fix (1 minute)

### Option 1: Run the Fix Script
```bash
chmod +x fix_deployment.sh
./fix_deployment.sh
```

### Option 2: Manual Steps

**Step 1: Verify wrangler.toml has required fields**
```toml
name = "rootrush"
type = "service"  # ← Required!
main = "functions/[[path]].js"
account_id = "your-account-id"  # ← Add this!
compatibility_date = "2024-04-01"

[assets]
directory = "static"
```

**Step 2: Add your Account ID**
```bash
wrangler whoami
# Copy the Account ID and add to wrangler.toml
```

**Step 3: Ensure static directory exists**
```bash
mkdir -p static
```

**Step 4: Try deploying again**
```bash
wrangler deploy --env production
```

---

## Configuration Files Provided

| File | Purpose |
|------|---------|
| **wrangler.toml** | Main TOML configuration (RECOMMENDED) |
| **wrangler.jsonc** | JSON configuration (alternative) |
| **wrangler-workers.toml** | Workers-only configuration |
| **fix_deployment.sh** | Automated fix script |

---

## Deployment Commands

### Option 1: Deploy with TOML Config (Recommended)
```bash
wrangler deploy --env production
```

### Option 2: Deploy with Assets Specified
```bash
wrangler deploy --assets=./static --env production
```

### Option 3: Deploy with JSONC Config
```bash
# Use wrangler.jsonc instead
wrangler deploy --config wrangler.jsonc --env production
```

### Option 4: Test Locally First
```bash
wrangler dev --env development
# Visit: http://localhost:8787
```

---

## Full Deployment Steps

```bash
# 1. Ensure you're logged in
wrangler login

# 2. Verify your Account ID
wrangler whoami

# 3. Update wrangler.toml with Account ID (or use fix script)
# vim wrangler.toml  # Add: account_id = "your-id"

# 4. Set Backend URL secret
wrangler secret put BACKEND_URL --env production
# Enter: https://your-api.railway.app

# 5. Deploy to production
wrangler deploy --env production

# 6. Monitor deployment
wrangler tail --env production

# 7. Visit your domain
# https://yourdomain.com
```

---

## What Each Config File Does

### wrangler.toml (Main - Recommended)
```toml
type = "service"              # Service type (required)
main = "functions/[[path]].js" # Entry point
account_id = "YOUR_ID"        # Your Cloudflare account
[assets]
directory = "static"          # Static files directory
```

### wrangler.jsonc (Alternative JSON Format)
Same configuration but in JSON format. Use if you prefer JSON over TOML.

### wrangler-workers.toml (Workers-Only)
Alternative if you want Workers-specific configuration only.

---

## Environment Variables

### Set Before Deployment
```bash
# Production
wrangler secret put BACKEND_URL --env production
wrangler secret put HUGGINGFACE_API_TOKEN --env production
wrangler secret put FLASK_SECRET_KEY --env production

# Staging
wrangler secret put BACKEND_URL --env staging
```

### Verify Secrets Are Set
```bash
wrangler secret list --env production
```

---

## Directory Structure (After Setup)

```
/workspaces/Rootrush/
├── functions/
│   └── [[path]].js          # Main Worker handler ✅
├── static/                  # Static files (auto-created)
│   └── .gitkeep
├── templates/               # Your HTML templates
├── app.py                   # Flask backend
├── requirements.txt         # Python deps
├── package.json             # Node deps
├── wrangler.toml            # ✅ Use this one
├── wrangler.jsonc           # Alternative
├── wrangler-workers.toml    # Alternative
└── .github/
    └── workflows/
        └── deploy.yml       # CI/CD automation
```

---

## Common Issues & Fixes

### Issue: "Unable to find a service spec"
```bash
# Add to wrangler.toml:
type = "service"
account_id = "your-account-id"
```

### Issue: "Assets directory not found"
```bash
mkdir -p static  # Create the directory
```

### Issue: "Deployment succeeded but shows errors"
```bash
# Check logs for backend errors
wrangler tail --env production --status error
```

### Issue: "Static files not serving"
```bash
# Ensure assets config in wrangler.toml:
[assets]
directory = "static"

# Then redeploy
wrangler deploy --env production
```

---

## Verify Deployment

### Check if Live
```bash
curl https://yourdomain.com
# Should return your webpage
```

### Monitor Logs
```bash
wrangler tail --env production
# Shows real-time request logs
```

### View Analytics
```
Cloudflare Dashboard → Workers → Analytics
```

---

## Next Steps

1. **Run:** `./fix_deployment.sh`  OR  manually add `account_id` to `wrangler.toml`
2. **Deploy:** `wrangler deploy --env production`
3. **Monitor:** `wrangler tail --env production`
4. **Verify:** Visit `https://yourdomain.com`

---

## Need Help?

```bash
# View configuration
cat wrangler.toml

# Verify Wrangler setup
wrangler whoami

# Test deployment (dry-run)
wrangler deploy --dry-run --env production

# View all secrets
wrangler secret list --env production
```

---

**Your deployment should now work!** 🚀
