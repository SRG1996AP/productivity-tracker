# 🚀 RAILWAY DEPLOYMENT - QUICK REFERENCE

## The 10-Minute Deployment Process

### Step 1️⃣: Install Git
https://git-scm.com/download/win → Run installer → Restart PowerShell

**Test:** `git --version` ✅

---

### Step 2️⃣: Create GitHub Repo
1. https://github.com/new
2. Name: `productivity-tracker`
3. Public
4. Create
5. **Copy your repo URL** (https://github.com/YOUR-USERNAME/productivity-tracker.git)

---

### Step 3️⃣: Push Code to GitHub

**Option A - Auto Script (Easiest):**
```powershell
cd c:\Users\edwin\Desktop\productivity_tracker
powershell -ExecutionPolicy Bypass -File setup-railway.ps1
```

**Option B - Manual:**
```powershell
cd c:\Users\edwin\Desktop\productivity_tracker
git init
git add .
git commit -m "Initial commit - productivity tracker"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/productivity-tracker.git
git push -u origin main
```

---

### Step 4️⃣: Create Railway Account
1. https://railway.app
2. Login with GitHub
3. Authorize

---

### Step 5️⃣: Deploy on Railway
1. New Project
2. Deploy from GitHub repo
3. Select `productivity-tracker`
4. Deploy

⏳ **Wait for deployment to complete (2-3 min)**

---

### Step 6️⃣: Generate SECRET_KEY

In PowerShell:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Copy the output**

---

### Step 7️⃣: Set Environment Variables

In Railway dashboard:
1. Click project
2. Variables tab
3. Add:
   - `FLASK_ENV` = `production`
   - `FLASK_APP` = `wsgi.py`
   - `SECRET_KEY` = **paste from Step 6**

4. Deploy

⏳ **Wait 60 seconds**

---

### Step 8️⃣: Create Admin User

**Option A - Via Railway CLI:**
```powershell
# Install: https://docs.railway.app/cli
railway login
railway link
railway run python create_test_user.py
```

**Option B - Via Database:**
Use the admin panel after logging in

---

### Step 9️⃣: Login!

1. Click Railway project
2. Find **Public Domain**
3. Visit the link
4. Login with admin credentials

---

### Step 🔟: Share with Team

```
Your app is now live at:
https://your-app-name.railway.app
```

---

## 🆘 If Something Goes Wrong

| Problem | Solution |
|---------|----------|
| Git not found | Restart PowerShell after installing Git |
| Push fails | Check repo URL is correct, verify GitHub settings |
| App won't start | Check Logs tab in Railway for errors |
| Database error | Wait 60 seconds after setting variables |
| Login doesn't work | Create admin user with `create_test_user.py` |

---

## 📄 Full Guides

- Complete steps: See **RAILWAY_DEPLOYMENT.md**
- General info: See **DEPLOYMENT.md**

---

## 🎯 Success Indicators

✅ Git installed and working
✅ Code on GitHub
✅ Railway project created
✅ Environment variables set
✅ App loads at public URL
✅ Can login to app
✅ Team can access it

---

**You've got this! 🚀**

