# Quick Start: Cloudflare Deployment Setup

## 📋 Files Generated

✅ Created the following files for Cloudflare deployment:

1. **requirements.txt** - Python dependencies (Flask, Gunicorn, HuggingFace)
2. **.env.example** - Environment variables template
3. **.gitignore** - Git ignore configuration
4. **config.py** - Flask configuration management
5. **wrangler.toml** - Cloudflare Wrangler configuration
6. **Procfile** - Heroku/Railway deployment file
7. **runtime.txt** - Python runtime version
8. **Dockerfile** - Docker containerization
9. **docker-compose.yml** - Local Docker development
10. **build.sh** - Build script
11. **.github/workflows/deploy.yml** - CI/CD pipeline
12. **CLOUDFLARE_DEPLOYMENT.md** - Detailed deployment guide

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Environment
```bash
cp .env.example .env
# Edit .env with your values
```

### Step 3: Test Locally
```bash
python app.py
# or
flask run
```

✅ Visit: `http://localhost:5000`

---

## ☁️ Choose Your Deployment Method

### OPTION A: Railway (Easiest ⭐ RECOMMENDED)
**5-10 minutes setup, free tier available**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Create project
railway init

# 4. Add environment variables
railway variable add FLASK_ENV production
railway variable add FLASK_SECRET_KEY <strong-secret>
railway variable add HUGGINGFACE_API_TOKEN <your-token>

# 5. Deploy
railway up

# 6. Get deployment URL
railway open
```

**Point Cloudflare DNS to Railway domain → Done!**

---

### OPTION B: Heroku (Traditional)
**Quick migration from existing setup**

```bash
# 1. Install Heroku CLI
brew install heroku
# or use: curl https://cli-assets.heroku.com/install.sh | sh

# 2. Login
heroku login

# 3. Create app
heroku create your-app-name

# 4. Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set FLASK_SECRET_KEY=<strong-secret>
heroku config:set HUGGINGFACE_API_TOKEN=<your-token>

# 5. Deploy
git push heroku main

# 6. Monitor
heroku logs --tail
```

**Point Cloudflare DNS to: your-app-name.herokuapp.com**

---

### OPTION C: Docker + Any Cloud Provider
**Most flexible (DigitalOcean, AWS, Google Cloud, etc.)**

```bash
# Build locally
docker build -t rootrush .
docker run -p 8000:8000 rootrush

# Deploy to cloud provider
# (e.g., DigitalOcean App Platform, AWS ECS, etc.)
```

---

## 🔧 Cloudflare DNS Configuration

1. **Go to:** Cloudflare Dashboard → Your Domain → DNS
2. **Add Record:**
   - Type: CNAME (or A record)
   - Name: yourdomain.com (or subdomain)
   - Target: <your-deployed-app-domain>
   - Proxy: ON (orange cloud)

3. **Enable HTTPS:**
   - SSL/TLS → Mode: Full (Strict)

---

## ✅ Deployment Checklist

- [ ] Environment variables set correctly
- [ ] `FLASK_SECRET_KEY` is strong/unique
- [ ] `HUGGINGFACE_API_TOKEN` configured
- [ ] Local testing passed
- [ ] Cloudflare DNS records updated
- [ ] SSL/TLS enabled
- [ ] Application accessible via HTTPS

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| **502 Error** | Backend down. Check logs: `railway logs` or `heroku logs --tail` |
| **404 on routes** | Verify routes in `app.py` are correct |
| **API timeouts** | Increase timeout in `huggingface_integration.py` |
| **CORS errors** | Check Flask app security headers in `config.py` |
| **Can't connect** | Verify DNS propagated (wait 5-10 min) and Cloudflare proxy enabled |

---

## 📚 Full Documentation

**See:** [CLOUDFLARE_DEPLOYMENT.md](./CLOUDFLARE_DEPLOYMENT.md) for:
- Detailed step-by-step guides
- Multiple deployment options
- Production checklist
- Advanced security configurations
- Monitoring & logging setup

---

## 🎯 Next Steps

1. Read [CLOUDFLARE_DEPLOYMENT.md](./CLOUDFLARE_DEPLOYMENT.md)
2. Choose deployment method (Railway recommended)
3. Run setup commands
4. Configure Cloudflare DNS
5. Test deployment
6. Monitor logs

---

## 💡 Pro Tips

- Use **Railway** for fastest setup (start free)
- Keep `.env` file secure (add to `.gitignore`)
- Enable Cloudflare WAF for security
- Set up monitoring/alerting for production
- Regular database backups (if using database)
- Monitor HuggingFace API quota

**Questions?** Check the full guide or cloud provider docs.
