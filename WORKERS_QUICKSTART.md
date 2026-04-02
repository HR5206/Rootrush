# Workers/Pages Quick Start

## 🚀 Fastest Setup (5 minutes)

### Option 1: Pages + External Backend (RECOMMENDED ⭐)

**Best for:** Minimal changes, keep Python backend running

```bash
# 1. Install & Login
npm install -g wrangler
wrangler login

# 2. Create Pages project  
wrangler pages project create rootrush-app

# 3. Connect Git repository (via dashboard or CLI)
# Dashboard → Workers & Pages → Pages → Create → Connect to Git

# 4. Deploy
git push origin main  # Automatic deployment
```

**Then deploy backend to Railway/Heroku (see CLOUDFLARE_DEPLOYMENT.md)**

---

### Option 2: Workers Proxy (JavaScript)

```bash
# 1. Install
npm install -g wrangler
wrangler login

# 2. Create Workers project
wrangler init --name rootrush-workers

# 3. Copy provided functions/[[path]].js to your project

# 4. Set backend URL
wrangler secret put BACKEND_URL --env production

# 5. Deploy
wrangler deploy --env production
```

---

## ⚙️ Configuration Steps

### Step 1: Install Wrangler
```bash
npm install -g wrangler
wrangler --version  # Verify
```

### Step 2: Authenticate
```bash
wrangler login
# Opens browser for authorization
```

### Step 3: Configure Environment
Copy your Account ID:
```bash
wrangler whoami
# Note: Copy the Account ID displayed
```

Update `wrangler.toml` with your Account ID:
```toml
account_id = "your-account-id"
```

### Step 4: Set Secrets
```bash
# Production environment
wrangler secret put BACKEND_URL --env production
wrangler secret put HUGGINGFACE_API_TOKEN --env production
wrangler secret put FLASK_SECRET_KEY --env production
```

### Step 5: Test Locally
```bash
wrangler dev --env development
# Visit: http://localhost:8787
```

### Step 6: Deploy
```bash
wrangler deploy --env production
```

### Step 7: Monitor
```bash
wrangler tail --env production
# Real-time logs from your deployed Worker
```

---

## 📋 File Reference

| File | Purpose |
|------|---------|
| `functions/[[path]].js` | Main Worker handler (provided) |
| `wrangler.toml` | Main configuration |
| `.env.production` | Environment-specific config |

---

## 🔗 Routing

### Static Routes
```
yourdomain.com/          → Backend
yourdomain.com/css/*     → Backend (cached)
yourdomain.com/js/*      → Backend (cached)
yourdomain.com/static/*  → Backend (cached)
```

### API Routes
```
yourdomain.com/api/*     → Backend
yourdomain.com/inputs    → Backend
yourdomain.com/results   → Backend
yourdomain.com/insights  → Backend
```

**All proxied to BACKEND_URL environment variable**

---

## 🎯 Architecture

```
User Request
    ↓
Cloudflare Workers (Proxy/Cache/Security)
    ↓
Your Backend API
    ├─ Railway/Heroku
    ├─ DigitalOcean
    └─ Any HTTP-compatible service
```

---

## 🔒 Security Features

✅ Automatic HTTPS  
✅ DDoS Protection  
✅ Security Headers  
✅ Rate Limiting (optional)  
✅ WAF Rules  

---

## 💾 Caching Strategy

| Asset Type | TTL | Behavior |
|-----------|-----|----------|
| HTML | Not cached | Always fresh |
| CSS/JS | 24 hours | Long-term cache |
| Images | 24 hours | Long-term cache |
| API | 5 minutes | Short cache |

---

## 🧪 Testing Commands

```bash
# Local development
wrangler dev --env development

# Test staging
wrangler deploy --env staging
curl https://staging.yourdomain.com

# Production deployment
wrangler deploy --env production
curl https://yourdomain.com

# View logs
wrangler tail
wrangler tail --env production
wrangler tail --status success --format json
```

---

## 🚨 Troubleshooting

| Issue | Fix |
|-------|-----|
| **Blank page** | Check backend URL, run `wrangler tail` for logs |
| **API errors** | Verify BACKEND_URL environment variable |
| **Slow response** | Check caching settings, backend healthcheck |
| **CORS issues** | Add CORS headers in backend or Worker |
| **502 errors** | Backend is down, check backend logs |

---

## 📊 Monitoring

### View Logs in Real-Time
```bash
wrangler tail --format pretty
```

### Check Status
```bash
wrangler status
```

### View Analytics
```
Dashboard → Workers & Pages → Your Project → Analytics
```

---

## 🔑 Environment Variables

### Development
```bash
wrangler dev --env development
```

### Staging
```bash
wrangler deploy --env staging
```

### Production
```bash
wrangler deploy --env production
```

Each environment reads from its section in `wrangler.toml`

---

## 📚 Learn More

- [Cloudflare Pages](https://developers.cloudflare.com/pages/)
- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/cli-wrangler/)

---

## ✅ Deployment Checklist

- [ ] Wrangler installed & logged in
- [ ] `wrangler.toml` configured with Account ID
- [ ] Backend deployed to Railway/Heroku
- [ ] BACKEND_URL secret set
- [ ] API tokens configured
- [ ] Tested locally with `wrangler dev`
- [ ] Custom domain configured
- [ ] SSL verified
- [ ] Deployed to production
- [ ] Monitoring enabled

**Ready to deploy!** 🚀
