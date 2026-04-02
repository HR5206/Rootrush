# Fix: "Backend URL not configured" Error

## ❌ What Went Wrong?

Your Worker deployed successfully, but it's missing the `BACKEND_URL` environment variable. This causes the "Backend URL not configured" error.

**Reason:** The secret wasn't set before deployment or wasn't passed to the Worker correctly.

---

## ✅ Quick Fix (2 minutes)

### Step 1: Set Your Backend URL Secret

```bash
wrangler secret put BACKEND_URL --env production
```

**When prompted, enter your backend URL. Examples:**

- **Railway:** `https://your-project.railway.app`
- **Heroku:** `https://your-app-name.herokuapp.com`
- **DigitalOcean:** `https://your-domain.com`
- **Custom:** `https://api.yourdomain.com`

**Full example:**
```bash
wrangler secret put BACKEND_URL --env production
# Paste this when prompted:
https://my-api.railway.app
# Press Enter
```

### Step 2: Redeploy

```bash
wrangler deploy --env production
```

### Step 3: Verify

```bash
# Check logs for confirmation
wrangler tail --env production

# Then visit your website and test
# https://yourdomain.com
```

---

## 🔍 Verify It's Working

### Check if Secret is Set
```bash
wrangler secret list --env production
```

**Output should include:** `BACKEND_URL`

### Check Logs for Errors
```bash
wrangler tail --env production --status error
```

### Test Backend Connection
In the logs, if you see successful requests being forwarded to your backend, it's working!

---

## 📋 What I Fixed

| Issue | Fix |
|-------|-----|
| wrangler.toml had placeholder BACKEND_URL | ✅ Removed - now uses secret only |
| Production config was incomplete | ✅ Updated to use secrets properly |

Now your Worker will use the actual secret you set with `wrangler secret put`.

---

## 🚀 Complete Step-by-Step

### If You Have Your Backend URL Ready:

```bash
# 1. Set backend URL as secret
wrangler secret put BACKEND_URL --env production
# Paste your backend URL when prompted

# 2. Deploy immediately
wrangler deploy --env production

# 3. Monitor deployment
wrangler tail --env production

# 4. Visit your website
# https://yourdomain.com
```

### If You Don't Have Backend URL Yet:

1. **Deploy Flask app to Railway first:**
   ```bash
   railway login
   railway init
   railway up
   # Get URL from: railway open
   ```

2. **Then set secret:**
   ```bash
   wrangler secret put BACKEND_URL --env production
   # Paste the Railway URL: https://your-project.railway.app
   ```

3. **Redeploy Worker:**
   ```bash
   wrangler deploy --env production
   ```

---

## 🆘 Troubleshooting

### Issue: Still Shows "Backend URL not configured"

**Solution:**
```bash
# 1. Verify secret is set
wrangler secret list --env production
# Should show: BACKEND_URL

# 2. If not shown, set it again
wrangler secret put BACKEND_URL --env production

# 3. Redeploy
wrangler deploy --env production

# 4. Wait 5 seconds and refresh browser
```

### Issue: Secret Was Set But Not Working

**Solution:**
```bash
# 1. Clear Cloudflare cache
# Dashboard → Caching → Purge Cache → Purge All

# 2. Redeploy (secrets update on deploy)
wrangler deploy --env production

# 3. Wait 30 seconds
# 4. Refresh browser (hard refresh: Ctrl+Shift+R or Cmd+Shift+R)
```

### Issue: "Backend URL points to wrong server"

**Solution:**
```bash
# 1. Update the secret with correct URL
wrangler secret put BACKEND_URL --env production
# Paste correct backend URL

# 2. Redeploy
wrangler deploy --env production
```

---

## 🔐 Setting Multiple Secrets

If you need other secrets too:

```bash
# Backend URL
wrangler secret put BACKEND_URL --env production

# HuggingFace API Token
wrangler secret put HUGGINGFACE_API_TOKEN --env production

# Flask Secret Key
wrangler secret put FLASK_SECRET_KEY --env production
```

---

## 📝 What Gets Set

After running `wrangler secret put BACKEND_URL --env production` with value `https://api.example.com`:

✅ Secret stored securely in Cloudflare  
✅ Accessible to Worker as `env.BACKEND_URL`  
✅ Not visible in logs  
✅ Deployed with next `wrangler deploy`  

---

## ✅ Verification Commands

```bash
# See all secrets (values hidden)
wrangler secret list --env production

# View recent logs from Worker
wrangler tail --env production

# View only error logs
wrangler tail --env production --status error

# View successful requests
wrangler tail --env production --status success
```

---

## 🎯 You're Almost There!

Just set the secret and redeploy - should take 30 seconds:

```bash
wrangler secret put BACKEND_URL --env production
# Paste your backend URL (e.g., https://api.railway.app)

wrangler deploy --env production
# Done!
```

Visit your site and it should work! 🚀
