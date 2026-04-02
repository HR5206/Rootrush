# 🔧 Fix: "Backend URL not configured" - Complete Solution

## ❌ Problem

Your Cloudflare Worker deployed successfully, but shows this error:

```
Backend URL not configured
```

**Why?** The Worker doesn't have the `BACKEND_URL` environment variable set.

---

## ✅ Solution (30 seconds)

### Step 1: Get Your Backend URL

First, find where your Flask backend is running:

**Option A: Railway**
```bash
railway open  # Opens your app URL
# Example: https://rootrush-production-abc123.railway.app
```

**Option B: Heroku**
```bash
heroku open  # Opens your app URL
# Example: https://my-rootrush-app.herokuapp.com
```

**Option C: Custom Hosting**
- Your backend URL (e.g., `https://api.yourdomain.com`)

### Step 2: Set Backend URL as Secret

```bash
wrangler secret put BACKEND_URL --env production
```

When prompted, paste your backend URL and press Enter:
```
? Enter a secret value: › https://your-app-url.railway.app
```

### Step 3: Redeploy

```bash
wrangler deploy --env production
```

### Step 4: Test

```bash
# Monitor logs
wrangler tail --env production

# Visit your website
# https://yourdomain.com
```

**Done!** 🎉 Your site should now work.

---

## 🚀 Quick Commands (Copy & Paste)

### Command 1: Set Secret
```bash
wrangler secret put BACKEND_URL --env production
# Paste your backend URL when prompted
```

### Command 2: Redeploy
```bash
wrangler deploy --env production
```

### Command 3: Check Logs
```bash
wrangler tail --env production
```

---

## 🔍 Verify It's Working

### Check if Secret is Set
```bash
wrangler secret list --env production
```

**Should show:** `BACKEND_URL`

### Monitor Deployment
```bash
wrangler tail --env production --status success
```

**Should show:** Requests being forwarded to your backend

### Test Full Flow
```bash
# 1. Visit your site
curl https://yourdomain.com

# 2. Check logs
wrangler tail --env production

# 3. Should see successful requests
```

---

## 🟢 Status Indicators

### ✅ Working:
- Secret is set: `wrangler secret list | grep BACKEND_URL`
- Worker deployed: `wrangler deployments list`
- Logs show forwarded requests: `wrangler tail`
- Website loads without errors

### ❌ Not Working:
- Secret not in list: Set it with `wrangler secret put`
- Still shows 500 error: Check if backend is running
- Logs show errors: Check backend URL is correct

---

## 🆘 Troubleshooting

### Issue: "Backend URL not configured" still shows

**Check:**
```bash
# 1. Is secret set?
wrangler secret list --env production | grep BACKEND_URL

# 2. Is it the right URL?
# Visit your backend URL directly to verify it works

# 3. Did you redeploy?
wrangler deploy --env production

# 4. Hard refresh browser
# Ctrl+Shift+R (Windows/Linux)
# Cmd+Shift+R (Mac)
```

### Issue: "Deployment succeeded but backend unreachable"

**Check:**
```bash
# 1. Is your backend running?
curl https://your-backend-url.railway.app

# 2. Are you online?
ping google.com

# 3. Is backend URL correct?
wrangler secret list --env production

# 4. Check backend logs for errors
railway logs  # or heroku logs --tail
```

### Issue: "Backend URL points to wrong service"

**Fix:**
```bash
# 1. Update the secret
wrangler secret put BACKEND_URL --env production
# Paste the CORRECT URL

# 2. Redeploy
wrangler deploy --env production

# 3. Wait & test
```

---

## 📋 What Gets Set

When you run:
```bash
wrangler secret put BACKEND_URL --env production
```

✅ Secret stored securely on Cloudflare  
✅ Worker can access it as `env.BACKEND_URL`  
✅ Not logged, not visible to public  
✅ Takes effect on next deployment  

---

## 🎯 Complete Workflow

```
1. Deploy Flask backend to Railway/Heroku
   ↓
2. Get backend URL
   ↓
3. Set secret: wrangler secret put BACKEND_URL
   ↓
4. Redeploy: wrangler deploy --env production
   ↓
5. Monitor: wrangler tail --env production
   ↓
6. Test: Visit https://yourdomain.com
   ↓
✅ Working!
```

---

## 🛠️ Automated Fix

Instead of manual steps, run:

```bash
chmod +x diagnose_deployment.sh
./diagnose_deployment.sh
```

This script will:
1. Check Wrangler is installed
2. Verify you're logged in
3. Check wrangler.toml
4. Check if BACKEND_URL secret is set
5. Tell you what to do next

---

## 📚 Related Docs

- [FIX_BACKEND_URL.md](./FIX_BACKEND_URL.md) - Detailed troubleshooting
- [DEPLOY_NOW.md](./DEPLOY_NOW.md) - Deployment overview
- [WORKERS_COMPLETE_GUIDE.md](./WORKERS_COMPLETE_GUIDE.md) - Full reference

---

## ✨ Summary

| Step | Command | Time |
|------|---------|------|
| 1. Get backend URL | Visit Railway/Heroku | 10s |
| 2. Set secret | `wrangler secret put BACKEND_URL` | 10s |
| 3. Redeploy | `wrangler deploy --env production` | 10s |
| 4. Test | Visit website | 10s |
| **Total** | | **40s** |

**Ready?** Run: `wrangler secret put BACKEND_URL --env production` 🚀
