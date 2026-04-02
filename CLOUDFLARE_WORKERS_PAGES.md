# Cloudflare Workers/Pages Deployment Guide

## Overview

Cloudflare Workers is a serverless platform, but since your Flask app is Python-based, you have two main approaches:

### ✅ Recommended: Hybrid Deployment
- **Frontend:** Static assets on Cloudflare Pages
- **API/Backend:** Store on Workers or route to external Python backend
- **Workers:** Handle logic, proxying, caching

### Alternative: Pure Workers (requires refactoring to JavaScript)

---

## Approach 1: Cloudflare Pages + Workers (RECOMMENDED)

### Prerequisites
```bash
npm install -g wrangler
npm install -g @cloudflare/wrangler
wrangler login
```

### Step 1: Create Pages Project

**Method A: Via CLI**
```bash
wrangler pages project create rootrush-app
```

**Method B: Via Cloudflare Dashboard**
1. Go to Cloudflare Dashboard
2. Workers & Pages → Pages
3. Create application → Connect to Git
4. Select your GitHub repository
5. Set Build Command: `pip install -r requirements.txt`
6. Set Output Directory: `static` (or where your frontend files are)

### Step 2: Create Worker Function (Handles API Calls)

Create `/functions/_middleware.js`:
```javascript
export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);

  // Route API requests to backend
  if (url.pathname.startsWith('/api/')) {
    return handleAPIRequest(request, context);
  }

  // Serve static assets
  return context.next();
}

async function handleAPIRequest(request, context) {
  const backendUrl = `${context.env.BACKEND_URL}${new URL(request.url).pathname}`;
  
  return fetch(backendUrl, {
    method: request.method,
    headers: request.headers,
    body: request.body,
  });
}
```

### Step 3: Create wrangler.toml (Pages Configuration)

Already created, but update with your details:

```toml
name = "rootrush"
type = "javascript"
account_id = "your-account-id"
workers_dev = true

[env.production]
name = "rootrush-production"
routes = [
  { pattern = "yourdomain.com/*", zone_name = "yourdomain.com" }
]

[[env.production.vars]]
BACKEND_URL = "https://your-backend-api.com"

[env.staging]
name = "rootrush-staging"
routes = [
  { pattern = "staging.yourdomain.com/*", zone_name = "yourdomain.com" }
]
```

### Step 4: Deploy to Pages

```bash
# Build locally
npm run build

# Deploy to Pages
wrangler pages deploy dist

# Or deploy from Git (automatic)
git push origin main
```

### Step 5: Configure Backend

**Option A: Keep Backend Separate**
```bash
# Deploy Flask app to Railway/Heroku (see CLOUDFLARE_DEPLOYMENT.md)
# Set BACKEND_URL environment variable in Cloudflare
```

**Option B: Deploy Backend to Worker KV + Python Runtime**
```bash
# Use Cloudflare's Python runtime support (beta)
# Or deploy to external service
```

---

## Approach 2: Python-based Workers (Using @cloudflare/workers-types)

**Note:** Cloudflare Workers primarily support JavaScript/TypeScript. For Python, use external backend + Workers proxy.

### Setup Steps:

1. **Initialize Workers Project**
```bash
wrangler init rootrush-workers
cd rootrush-workers
npm install
```

2. **Create src/index.js** (Main Worker)
```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Route to Flask backend
    if (url.pathname.startsWith('/inputs') || url.pathname.startsWith('/api')) {
      return forwardToBackend(request, env);
    }

    // Serve static assets
    return serveStatic(request, env);
  }
};

async function forwardToBackend(request, env) {
  const backendURL = new URL(request.url);
  backendURL.host = env.BACKEND_HOST;
  
  return fetch(new Request(backendURL, request));
}

async function serveStatic(request, env) {
  // Serve from KV, R2, or external source
  return new Response('Not found', { status: 404 });
}
```

3. **Configure wrangler.toml**
```toml
name = "rootrush-workers"
main = "src/index.js"
compatibility_date = "2024-04-01"

[env.production]
vars = { BACKEND_HOST = "api.yourdomain.com" }

[env.staging]
vars = { BACKEND_HOST = "staging-api.yourdomain.com" }
```

4. **Add Environment Variables**
```bash
wrangler secret put BACKEND_URL --env production
wrangler secret put BACKEND_URL --env staging
```

5. **Deploy**
```bash
wrangler deploy --env production
```

---

## Approach 3: Full Migration to JavaScript (Complete Rewrite)

**When to use:** Need 100% Workers-native deployment

### Rewrite Strategy:

1. **Convert Flask to Express.js** (or similar Node framework)
```bash
npm init -y
npm install express cors dotenv
```

2. **Adapt Core Logic**
- Keep business logic from Python files
- Rewrite Flask routes as Express handlers
- Port HuggingFace integration to JavaScript

3. **Deploy to Workers**
```bash
wrangler init
# Copy Express app into workers project
wrangler deploy
```

---

## Custom Domain Configuration

### Step 1: Update DNS Records
```
Type: CNAME
Name: yourdomain.com (or subdomain)
Target: yourproject.pages.dev
SSL: Enabled (Cloudflare proxy)
```

### Step 2: Configure in Cloudflare Workers/Pages

1. Go to your Pages project
2. Settings → Domains & accounts
3. Add custom domain: `yourdomain.com`
4. Cloudflare automatically handles SSL

### Step 3: Verify SSL
- Analytics → Overview
- Should show "Flexible" or "Full" SSL

---

## Environment Variables in Workers/Pages

### Set Secrets (Production Only)
```bash
wrangler secret put HUGGINGFACE_API_TOKEN --env production
wrangler secret put FLASK_SECRET_KEY --env production
wrangler secret put BACKEND_URL --env production
```

### Set Public Variables
In `wrangler.toml`:
```toml
[env.production]
vars = {
  API_VERSION = "1.0",
  LOG_LEVEL = "info"
}
```

---

## Performance Optimization for Workers

### 1. Implement Caching
```javascript
export async function onRequest(context) {
  const { request, next } = context;
  const cache = caches.default;
  
  // Check cache
  let response = await cache.match(request);
  if (response) return response;

  // Get from origin
  response = await next();
  
  // Cache successful responses
  if (response.ok) {
    context.waitUntil(cache.put(request, response.clone()));
  }
  
  return response;
}
```

### 2. Add Workers Analytics
In `wrangler.toml`:
```toml
[analytics]
enabled = true
```

### 3. Use Durable Objects (Optional - Advanced)
```javascript
export class DurableCounter {
  async initialize(state) {
    this.storage = state.storage;
    this.count = await this.storage.get("count") || 0;
  }
  
  async increment() {
    this.count++;
    await this.storage.put("count", this.count);
    return this.count;
  }
}
```

---

## Security Best Practices

### 1. Headers Security
```javascript
function setSecurityHeaders(response) {
  const headers = new Headers(response.headers);
  headers.set('X-Content-Type-Options', 'nosniff');
  headers.set('X-Frame-Options', 'DENY');
  headers.set('X-XSS-Protection', '1; mode=block');
  headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  return new Response(response.body, { status: response.status, headers });
}
```

### 2. Rate Limiting
```bash
wrangler secret put RATE_LIMIT_ENABLED true
```

In Worker:
```javascript
function rateLimit(request, env) {
  if (!env.RATE_LIMIT_ENABLED) return true;
  // Implement rate limiting logic
  return false;
}
```

### 3. Environment Secrets
```bash
# Never commit secrets!
wrangler secret put BACKEND_SECRET
wrangler secret put API_KEY
```

---

## Monitoring & Debugging

### 1. View Logs
```bash
wrangler tail --env production
```

### 2. Real-Time Analytics
Cloudflare Dashboard → Workers/Pages → Analytics

### 3. Error Tracking
```javascript
export default {
  async fetch(request, env) {
    try {
      return await handleRequest(request, env);
    } catch (error) {
      console.error('Worker error:', error);
      return new Response('Internal Server Error', { status: 500 });
    }
  }
};
```

---

## Comparison: Deployment Options

| Method | Setup Time | Cost | Scalability | Python Support |
|--------|-----------|------|-------------|-----------------|
| **Pages + External Backend** | 10 min | $$ | Excellent | ✅ Full |
| **Workers Proxy** | 15 min | $ | High | ✅ Via Backend |
| **Workers + Node.js** | 30 min | $ | High | ❌ Needs Rewrite |
| **Full JavaScript Rewrite** | 2-3 days | $ | Excellent | ❌ Complete |

---

## Deployment Checklist

- [ ] Wrangler CLI installed & logged in
- [ ] `wrangler.toml` configured
- [ ] Environment variables set
- [ ] Backend deployed (if using external)
- [ ] Custom domain configured
- [ ] SSL enabled
- [ ] Security headers added
- [ ] Rate limiting configured
- [ ] Monitoring enabled
- [ ] Tested in staging environment
- [ ] Ready for production deployment

---

## Quick Start Commands

```bash
# Install Wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Create project
wrangler init rootrush-workers

# Add secrets
wrangler secret put BACKEND_URL --env production
wrangler secret put HUGGINGFACE_API_TOKEN --env production

# Development
wrangler dev

# Deploy
wrangler deploy --env production

# View logs
wrangler tail --env production

# Publish to Pages
wrangler pages deploy ./public --project-name rootrush
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Blank page** | Check Routes tab, verify domain configured |
| **API 502** | Backend unreachable, check BACKEND_URL |
| **Slow performance** | Enable caching, check Worker execution time |
| **CORS errors** | Add CORS headers in Worker middleware |
| **Secrets not working** | Use wrangler secret command, restart Worker |

---

## Resources

- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/cli-wrangler/)
