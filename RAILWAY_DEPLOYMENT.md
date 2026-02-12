# 🚀 Railway Deployment Guide - Step by Step

**Time to Deploy: ~15 minutes**

---

## 📋 Prerequisites

- [ ] GitHub account (free): https://github.com
- [ ] Railway account (free): https://railway.app
- [ ] Git installed on Windows: https://git-scm.com/download/win

---

## STEP 1: Install Git on Windows

1. Go to: https://git-scm.com/download/win
2. Click **64-bit Git for Windows Setup**
3. Run the installer (accept defaults)
4. **Restart your terminal** (close and reopen PowerShell)

**Verify installation:**
```powershell
git --version
```

Should print: `git version 2.xx.x`

---

## STEP 2: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `productivity-tracker`
3. Description: `A web-based productivity tracking and time management system`
4. Choose: **Public** (for free Railway deployment)
5. Click **Create repository**

You'll see a page with commands. **Copy your repo URL** - looks like:
```
https://github.com/YOUR-USERNAME/productivity-tracker.git
```

---

## STEP 3: Push Code to GitHub

**In PowerShell, navigate to your project:**
```powershell
cd c:\Users\edwin\Desktop\productivity_tracker
```

**Configure Git (first time only):**
```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Initialize and push:**
```powershell
git init
git add .
git commit -m "Initial commit - productivity tracker app"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/productivity-tracker.git
git push -u origin main
```

⏳ Wait for upload to complete. Then verify at: `https://github.com/YOUR-USERNAME/productivity-tracker`

---

## STEP 4: Sign Up for Railway

1. Go to: https://railway.app
2. Click **Login** (top right)
3. Click **Login with GitHub**
4. Authorize Railway to access your GitHub
5. You're in! ✅

---

## STEP 5: Create Railway Project

1. In Railway dashboard, click **New Project** (or + button)
2. Click **Deploy from GitHub repo**
3. Search for and select: `productivity-tracker`
4. Click **Deploy**

⏳ Railway will start deploying (watch the logs)

---

## STEP 6: Generate Secret Key

Before your app works, you need a strong SECRET_KEY.

**In PowerShell, run Python:**
```powershell
python
```

**Then in Python shell:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**Copy the output** - it'll look like: `a-long-random-string-of-characters`

Type: `exit()` to leave Python

---

## STEP 7: Configure Environment Variables

**In Railway dashboard:**

1. Click on your **productivity-tracker** project
2. Click **Variables** tab (left sidebar)
3. Add these variables one by one:

| Variable | Value |
|----------|-------|
| `FLASK_ENV` | `production` |
| `FLASK_APP` | `wsgi.py` |
| `SECRET_KEY` | *Paste the key from STEP 6* |

**For DATABASE_URL:**
- Railway auto-manages PostgreSQL
- If not auto-set, Railway will create it
- Leave blank for now, it auto-configures

**After adding variables:**
- Hit **Deploy** button to restart the app
- Wait 30-60 seconds

---

## STEP 8: Verify Deployment ✅

1. Go back to Railway project overview
2. Look for **Public Domain** (middle right)
3. Click the domain link - your app is **LIVE!** 🎉

You'll see the login page.

---

## STEP 9: Create Admin User

Your app is running but Database needs initialization.

**In Railway:**

1. Click your project
2. Go to **Settings** tab
3. Find "Environment" section
4. Click **Add environment variables**
5. Look for a **Terminal/Shell** option, or...

**Alternative: Use Railway CLI**

1. Install Railway CLI: https://docs.railway.app/cli
2. In PowerShell:
```powershell
railway login
railway link
```

3. Then run database init:
```powershell
railway run python init_db.py
```

Or create admin user:
```powershell
railway run python create_test_user.py
```

---

## STEP 10: Login to Your App 🎊

1. Visit your Railway domain
2. Use credentials created in **Step 9**:
   - **Login ID**: `admin` (or what you set)
   - **Password**: Your chosen password
3. You're in! 

---

## 📱 Share Your App

Your app is now **publicly accessible**!

Share the Railway domain link with your team:
```
https://your-app-name.railway.app
```

---

## 🔒 Security Checklist

- ✅ SECRET_KEY is random and strong
- ✅ Database is PostgreSQL (not SQLite)
- ✅ HTTPS enabled automatically
- ✅ Code on GitHub (backed up)
- ✅ Environment variables secure (not in code)

---

## 📊 Monitor Your App

**View logs in Railway:**
1. Click your project
2. Click **Deployments** tab
3. Click latest deployment
4. View **Logs** tab

**Common issues:**
- If app crashes, logs will show errors
- Check database connection first
- Verify all environment variables are set

---

## 💰 Railway Pricing

- **Starter**: $5/month (recommended)
- **Includes**: 
  - Web dyno
  - PostgreSQL database
  - 100GB bandwidth
- **Pay as you go**: Extra fees only if you exceed

---

## 🆘 Troubleshooting

### App won't start
- Check logs in Railway → Deployments → Logs
- Verify all environment variables are set
- Ensure Procfile is correct

### Database connection error
- Wait 60 seconds after setting variables
- Railway may still be provisioning database
- Click **Deploy** to restart

### 404 on routes
- Make sure you're hitting the right domain
- Check logs for routing errors

### Static files not loading (CSS/JS missing)
- This is normal - Railway handles static files
- Refresh page with Ctrl+Shift+R (hard refresh)

---

## 📚 Next Steps

After deployment succeeds:

1. **Add users**: Use admin panel to create users
2. **Customize**: Update app title, add your logo
3. **Backup**: Railway auto-backs up PostgreSQL
4. **Monitor**: Check logs weekly
5. **Update**: Push new code to GitHub → Railway auto-deploys

---

## 🔗 Useful Links

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.app
- Your GitHub: https://github.com/YOUR-USERNAME/productivity-tracker
- Python/Flask: https://flask.palletsprojects.com

---

## ✅ Success Checklist

- [ ] Git installed
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Railway account created
- [ ] Project deployed
- [ ] Environment variables set
- [ ] Admin user created
- [ ] Can login to app
- [ ] Share domain with team

**Questions?** Check Railway docs or GitHub issues.

