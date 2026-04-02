# Complete Cloudflare Workers/Pages Deployment Guide

## TL;DR - Deploy in 10 Minutes

### Quick Command Reference:
```bash
# 1. Install & Login (2 min)
npm install -g wrangler
wrangler login

# 2. Configure (2 min)
wrangler whoami  # Copy Account ID
# Update wrangler.toml with Account ID

# 3. Set Secrets (3 min)
wrangler secret put BACKEND_URL --env production
# Enter: https://your-api.railway.app (or Heroku/custom)

# 4. Deploy (3 min)
wrangler deploy --env production
```

**Done!** Your app is live on `https://rootrush.yourdomain.com`

---

## What is Cloudflare Workers/Pages?

### Cloudflare Pages
- Free static hosting for frontend
- Automatic GitHub integration
- Build & deploy on every push

### Cloudflare Workers
- Serverless compute at the edge
- Acts as reverse proxy
- Handles routing, caching, security

### Hybrid Approach (RECOMMENDED for your app)
- **Frontend Assets** → Cloudflare Pages (cached globally)
- **API Proxy** → Cloudflare Workers (smart routing)
- **Backend** → Python Flask running on Railway/Heroku

---

## 2-Step Deployment

### STEP 1: Deploy Backend (Flask Python)
Keep your Flask app running on external service (5 min):

**Option A: Railway** (⭐ Easiest)
```bash
npm install -g @railway/cli
railway login
railway init
railway variable add BACKEND_URL https://your-app-url
railway up
```

**Option B: Heroku**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

**Get your backend URL:**
- Railway: `https://your-project.railway.app`
- Heroku: `https://your-app-name.herokuapp.com`

### STEP 2: Deploy to Cloudflare Workers (5 min)

```bash
# 1. Login to Cloudflare
npm install -g wrangler
wrangler login

# 2. Copy Account ID
wrangler whoami
# Output: Account ID: aaaaaaa...

# 3. Update wrangler.toml
account_id = "your-account-id-here"

# 4. Set backend URL
wrangler secret put BACKEND_URL --env production
# When prompted, enter: https://your-backend-url.railway.app

# 5. Deploy
wrangler deploy --env production

# 6. Verify
wrangler tail --env production
```

**Your app is now live!** Visit `https://yourdomain.com`

---

## Detailed Setup

### Prerequisites
```bash
# Node.js 16+ (check with: node --version)
brew install node  # Mac
# or download from nodejs.org

# Wrangler CLI
npm install -g wrangler

# Verify installation
wrangler --version
wrangler whoami  # Should prompt to login
```

### Authentication
```bash
wrangler login
# Opens browser → Authorize with Cloudflare
# Automatically creates credentials
```

### Get Your Account ID
```bash
wrangler whoami
# Output example:
# ┌─────────────────────────────────────┐
# │ 👤 Account                          │
# ├─────────────────────────────────────┤
# │ Account ID: 1a2b3c4d5e6f7g8h9i...  │
# │ Account: example@gmail.com          │
# └─────────────────────────────────────┘

# Copy the Account ID and add to wrangler.toml
```

### Configure wrangler.toml

Update `/workspaces/Rootrush/wrangler.toml`:

```toml
name = "rootrush"
main = "functions/[[path]].js"
account_id = "your-account-id"  # ← PASTE HERE
compatibility_date = "2024-04-01"

[env.development]
name = "rootrush-dev"
vars = { BACKEND_URL = "http://localhost:5000" }

[env.staging]
name = "rootrush-staging"
routes = [{ pattern = "staging.yourdomain.com/*", zone_name = "yourdomain.com" }]
vars = { BACKEND_URL = "https://staging-api.yourdomain.com" }

[env.production]
name = "rootrush"
routes = [{ pattern = "yourdomain.com/*", zone_name = "yourdomain.com" }]
vars = { BACKEND_URL = "https://your-api.railway.app" }  # ← UPDATE
```

### Set Environment Secrets

```bash
# Production environment
wrangler secret put BACKEND_URL --env production
# Enter: https://your-api.railway.app

wrangler secret put HUGGINGFACE_API_TOKEN --env production
# Enter: Your HuggingFace API token

wrangler secret put FLASK_SECRET_KEY --env production
# Enter: Your Flask secret key
```

### Test Locally

```bash
# Start local dev server
wrangler dev --env development

# Visit: http://localhost:8787
# All requests proxied to http://localhost:5000 (Flask dev server)
```

### Deploy to Production

```bash
# Deploy to Cloudflare
wrangler deploy --env production

# Output:
# ✨ Successfully published your Worker to
# https://rootrush.yourdomain.workers.dev
```

---

## DNS Configuration

### Option A: Cloudflare Nameservers (Full Control)

1. **Transfer domain to Cloudflare** (or point nameservers)
2. **Go to Dashboard → DNS**
3. **Add CNAME Record:**
   ```
   Name: yourdomain.com
   Type: CNAME
   Target: yourapp.workers.dev
   Proxy: ON (orange cloud)
   ```
4. **Update wrangler.toml:**
   ```toml
   routes = [
     { pattern = "yourdomain.com/*", zone_name = "yourdomain.com" }
   ]
   ```

### Option B: CNAME at Existing Registrar

1. **Keep domain at current registrar**
2. **Add CNAME record** pointing to `yourapp.workers.dev`
3. **Wait for DNS propagation** (5-30 minutes)

### Option C: Subdomain Only

```toml
routes = [
  { pattern = "app.yourdomain.com/*", zone_name = "yourdomain.com" }
]
```

---

## File Structure

```
/workspaces/Rootrush/
├── functions/
│   └── [[path]].js           # Worker handler (proxy & cache)
├── app.py                     # Your Flask backend
├── wrangler.toml             # Cloudflare config (MAIN)
├── wrangler-workers.toml     # Alternative config format
├── package.json              # Node.js config
├── requirements.txt          # Python dependencies
├── CLOUDFLARE_WORKERS_PAGES.md  # Full documentation
├── WORKERS_QUICKSTART.md     # Quick reference
└── setup_workers.sh          # Setup automation
```

---

## How It Works

### Request Flow

```
1. User visits: https://yourdomain.com/inputs
        ↓
2. Cloudflare Workers intercepts request
        ↓
3. Worker checks functions/[[path]].js rules
        ↓
4. Routes to BACKEND_URL (your Flask app)
        ↓
5. Flask processes request
        ↓
6. Response cached & returned to user
```

### Request Routing

**Static Assets** (cached 24 hours):
```
/css/* → Backend → Cache → User
/js/*  → Backend → Cache → User
```

**API Requests** (cached 5 minutes):
```
/api/* → Backend → Cache (5 min) → User
/inputs → Backend → User
```

**Dynamic** (not cached):
```
POST requests → Backend → User
Form submissions → Backend → User
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Backend running on Railway/Heroku
- [ ] Backend URL is publicly accessible
- [ ] All environment variables set in `.env`
- [ ] wrangler.toml has correct Account ID
- [ ] Custom domain configured in Cloudflare DNS
- [ ] SSL/TLS mode set to "Full"
- [ ] Tested locally with `wrangler dev`
- [ ] No secrets in version control

### Deploy Commands

```bash
# Deploy to production
wrangler deploy --env production

# Verify deployment
wrangler tail --env production

# Check status
wrangler status

# View real-time logs
wrangler logs

# Monitor from dashboard
# Cloudflare Dashboard → Workers & Pages → Analytics
```

### Monitoring

```bash
# Real-time logs
wrangler tail --env production

# Filter by status
wrangler tail --env production --status success
wrangler tail --env production --status error

# Export logs
wrangler tail --env production --format json > logs.json
```

---

## Troubleshooting

### Issue: "Worker not deployed"
```bash
# Solution: Verify Account ID
wrangler whoami
# Check if ID matches wrangler.toml
```

### Issue: "Blank page / 502 Bad Gateway"
```bash
# Check logs
wrangler tail --env production

# Verify backend is running
curl https://your-api.railway.app

# Verify BACKEND_URL secret
wrangler secret list --env production
```

### Issue: "Cannot reach backend"
```bash
# Test backend connectivity
curl -X GET https://your-api.railway.app/

# If fails, backend is down. Restart on Railway/Heroku
Railway: railway restart
Heroku: heroku restart
```

### Issue: "CORS errors"
Add to functions/[[path]].js:
```javascript
headers.set('Access-Control-Allow-Origin', '*');
headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
```

### Issue: "Changes not reflected"
```bash
# Clear Cloudflare cache
Dashboard → Caching → Purge Cache → Purge All

# Redeploy
wrangler deploy --env production
```

---

## Performance Optimization

### Enable Caching
In `functions/[[path]].js`, static assets use:
```javascript
cf: {
  cacheEverything: true,
  cacheTtl: 86400  // 24 hours
}
```

### Monitor Performance
1. **Dashboard → Workers → Analytics**
2. Check CPU time, bandwidth usage
3. Optimize slow endpoints

### Reduce Latency
- Cloudflare automatically serves from nearest edge location
- Global distribution across 300+ data centers
- Automatic GZIP compression

---

## Security Features

### Automatic
✅ HTTPS/SSL  
✅ DDoS protection  
✅ WAF (Web Application Firewall)  
✅ Rate limiting options  

### Manual Configuration

**Enable WAF:**
- Dashboard → Security → WAF → Managed Rules

**Add Rate Limiting:**
```bash
Dashboard → Rate Limiting → Create Rule
```

**Security Headers** (already in functions/[[path]].js):
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

---

## Comparison: Other Deployment Options

| Method | Setup | Cost | Scalability | Recommendation |
|--------|-------|------|-------------|-----------------|
| **Workers + Backend** | 10 min | $$ | Excellent | ⭐ Best |
| **Pages + External API** | 5 min | $ | High | Good |
| **Pure Workers JS** | 2+ hours | $ | High | Only if no Python |
| **Traditional Hosting** | 30 min | $$$| Medium | Legacy |

---

## Next Steps

1. **Deploy Backend:**
   - [ ] Choose Railway or Heroku
   - [ ] Deploy Flask app
   - [ ] Get backend URL

2. **Configure Workers:**
   - [ ] Update wrangler.toml with Account ID
   - [ ] Set BACKEND_URL secret
   - [ ] Test locally

3. **Deploy to Production:**
   - [ ] Deploy to Cloudflare
   - [ ] Configure custom domain
   - [ ] Enable SSL

4. **Monitor & Maintain:**
   - [ ] Check logs regularly
   - [ ] Monitor performance
   - [ ] Update as needed

---

## Resources

- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/cli-wrangler/)
- [Workers Examples](https://developers.cloudflare.com/workers/examples/)

---

## Support

**Questions?** Check:
1. [CLOUDFLARE_WORKERS_PAGES.md](./CLOUDFLARE_WORKERS_PAGES.md) - Full technical guide
2. [WORKERS_QUICKSTART.md](./WORKERS_QUICKSTART.md) - Quick reference
3. Run setup script: `./setup_workers.sh`
