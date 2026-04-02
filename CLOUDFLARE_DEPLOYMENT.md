# Cloudflare Deployment Guide for Rootrush

## Overview
This guide explains how to deploy the Rootrush Flask application to Cloudflare.

## Deployment Options

### Option 1: Cloudflare Pages + External Backend (RECOMMENDED)
**Best for:** Full-featured Flask apps with database operations
- Deploy frontend static files to Cloudflare Pages
- Keep backend API running on traditional hosting
- Use Cloudflare as reverse proxy

### Option 2: Cloudflare Workers + Python Conversion
**Best for:** Lightweight API operations
- Convert Flask app to work with Cloudflare Workers
- Limited to serverless constraints
- Requires significant refactoring

### Option 3: Traditional Hosting with Cloudflare DNS
**Best for:** Minimal changes, keep everything as-is
- Deploy to Heroku, Railway, DigitalOcean, etc.
- Use Cloudflare as DNS/security layer

## Prerequisites

### For All Options:
- [ ] Node.js 16+ installed
- [ ] npm or yarn installed
- [ ] Git repository initialized
- [ ] Cloudflare account with active domain

### For Option 1:
- [ ] Hosting provider account (Heroku, Railway, DigitalOcean, etc.)
- [ ] PostgreSQL/MySQL database (optional)

### For Option 3:
- [ ] Hosting provider account
- [ ] Domain registered or transferred to Cloudflare

## Step-by-Step Setup

### Step 1: Install Wrangler CLI
```bash
npm install -g wrangler
# or
yarn global add wrangler
```

### Step 2: Authenticate with Cloudflare
```bash
wrangler login
```
This opens your browser to authenticate with Cloudflare.

### Step 3: Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your actual values
```

Required variables:
- `FLASK_SECRET_KEY`: Strong secret key for Flask sessions
- `HUGGINGFACE_API_TOKEN`: Your HuggingFace API token
- `FLASK_ENV`: Set to "production" for deployment

### Step 4: Install Python Dependencies Locally
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 5: Test Locally
```bash
flask run
# or
python -m flask run
# or
gunicorn --bind 0.0.0.0:8000 app:create_app()
```
Visit `http://localhost:5000` (Flask default) or `http://localhost:8000` (Gunicorn)

---

## Deployment Methods

### METHOD A: Deploy to Heroku (Option 3 - Easiest)

#### 1. Install Heroku CLI
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2. Create Heroku App
```bash
heroku login
heroku create your-app-name
```

#### 3. Set Environment Variables
```bash
heroku config:set FLASK_ENV=production
heroku config:set FLASK_SECRET_KEY=your-strong-secret-key
heroku config:set HUGGINGFACE_API_TOKEN=your-token
```

#### 4. Deploy
```bash
git push heroku main
```

#### 5. Configure Cloudflare DNS
- Go to your Cloudflare dashboard
- Add CNAME record pointing to `your-app-name.herokuapp.com`
- Enable Cloudflare proxy (orange cloud icon)

---

### METHOD B: Deploy to Railway (Option 3 - Recommended)

#### 1. Install Railway CLI
```bash
npm install -g @railway/cli
# or
brew install railway
```

#### 2. Link Railway Project
```bash
railway link
railway up
```

#### 3. Set Up Environment Variables
```bash
railway variable add FLASK_ENV production
railway variable add FLASK_SECRET_KEY your-secret
railway variable add HUGGINGFACE_API_TOKEN your-token
```

#### 4. Deploy
```bash
railway up --detach
```

#### 5. Configure Cloudflare
- Get your Railway domain: `railway link` to view
- Create CNAME record in Cloudflare pointing to Railway domain
- Enable Cloudflare proxy

---

### METHOD C: Deploy to Cloudflare Pages Function (Option 1 - Advanced)

**Note:** This requires running backend separately (Option 3)

#### 1. Create Pages Project
```bash
wrangler pages project create rootrush
```

#### 2. Configure Build Settings
```bash
wrangler pages build
```

#### 3. Connect Repository
- Go to Cloudflare dashboard > Pages
- Connect your GitHub repository
- Set build command: `pip install -r requirements.txt && gunicorn app:create_app()`
- Set output directory: (leave empty for API)

---

## Step 6: Set Up Cloudflare DNS Records

### In Cloudflare Dashboard:

1. **Go to DNS Records**
2. **Add A Record:**
   - Name: @ (root) or subdomain
   - IPv4: Your hosting provider's IP
   - Proxy: Enabled (orange cloud)

3. **Add CNAME Record (if using managed hosting):**
   - Name: www (or subdomain)
   - Target: your-domain.herokuapp.com (or your host's domain)
   - Proxy: Enabled (orange cloud)

4. **Enable SSL/TLS:**
   - SSL/TLS Mode: Full (or Full - Strict if using let's encrypt)

---

## Step 7: Configure Cloudflare Rules (Optional)

### Enable Security Features:
- Go to Security section
- Enable WAF (Web Application Firewall)
- Set up rate limiting
- Enable DDoS protection

### Redirect HTTP to HTTPS:
- Rules > Create Rule
- Rule name: "Force HTTPS"
- Condition: `http_request_uri.scheme = "http"`
- Action: Managed Transform > Modify Request Header
- Set `Upgrade-Insecure-Requests` header

---

## Step 8: Deploy Application

### For Heroku:
```bash
git push heroku main
heroku logs --tail
```

### For Railway:
```bash
railway up
railway status
```

### For DigitalOcean/Custom VPS:
```bash
ssh your-server
git clone https://github.com/your-repo.git
cd rootrush
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:8000 app:create_app() &
```

---

## Step 9: Verify Deployment

1. **Check Domain:**
   - Visit your domain (http://yourdomain.com)
   - Should redirect to HTTPS automatically

2. **Test Application:**
   - Navigate through the application
   - Check console for errors (F12 developer tools)

3. **Check Cloudflare Analytics:**
   - Dashboard > Analytics
   - Verify requests are being routed through Cloudflare

4. **Monitor Backend Logs:**
   ```bash
   heroku logs --tail        # For Heroku
   railway logs              # For Railway
   ```

---

## Troubleshooting

### 502 Bad Gateway Error
- Backend service is down
- Check application logs: `railway logs` or `heroku logs`
- Verify environment variables are set

### CORS Issues
- Ensure `PREFERRED_URL_SCHEME = "https"` in config
- Check Flask app for proper CORS headers

### Slow Performance
- Check Railway/Heroku resource usage
- Enable caching in Cloudflare for static assets
- Optimize database queries

### HuggingFace API Timeouts
- Increase timeout in huggingface_integration.py
- Use async requests
- Add caching for API responses

---

## Production Checklist

- [ ] Environment variables configured securely
- [ ] SECRET_KEY is strong and unique
- [ ] SSL/TLS enabled (Cloudflare Full mode)
- [ ] DEBUG mode set to False
- [ ] Database backups configured (if using database)
- [ ] Logging configured for monitoring
- [ ] Rate limiting enabled
- [ ] WAF rules configured
- [ ] Domain properly configured in Cloudflare
- [ ] Tested full deployment workflow
- [ ] Monitoring and alerting set up

---

## Useful Commands

```bash
# Local testing
python app.py
flask run
gunicorn --bind 0.0.0.0:8000 app:create_app()

# Heroku
heroku logs --tail
heroku config
heroku restart

# Railway  
railway logs
railway status
railway link

# Cloudflare
wrangler login
wrangler pages project list
wrangler tail
```

---

## Support & Resources

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Railway Deployment Guide](https://docs.railway.app/)
- [Heroku Python Support](https://devcenter.heroku.com/articles/python-support)
- [Flask Production Deployment](https://flask.palletsprojects.com/deployment/)
