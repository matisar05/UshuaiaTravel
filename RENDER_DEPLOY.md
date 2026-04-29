# 🚀 Deploying Ushuaia Travel to Render

This guide will walk you through deploying both the Django backend and React frontend to Render's free tier.

## 📋 Prerequisites

- GitHub account
- Render account (free): https://render.com
- Project pushed to GitHub

## Part 1: PostgreSQL Database

### 1. Create Database

1. Go to Render Dashboard
2. Click **New** → **PostgreSQL**
3. Configure:
   - **Name**: `ushuaia-travel-db`
   - **Database**: `ushuaia_travel`
   - **User**: `ushuaia_user`
   - **Region**: Choose closest to your users
   - **Plan**: **Free**
4. Click **Create Database**

### 2. Get Database URL

1. Once created, go to database page
2. Scroll to **Connections**
3. Copy the **Internal Database URL** (starts with `postgresql://`)
4. Save this for later ✅

## Part 2: Django Backend API

### 1. Create Web Service

1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `ushuaia-travel-api`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `.` if needed)
   - **Runtime**: **Python 3**
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**:
     ```bash
     gunicorn ushuaia_travel.wsgi:application
     ```
   - **Plan**: **Free**

### 2. Environment Variables

Click **Advanced** → **Add Environment Variable** and add:

```
SECRET_KEY=<generate-a-long-random-string>
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=<paste-internal-database-url-from-step-1.2>
CORS_ALLOWED_ORIGINS=https://ushuaia-travel.onrender.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**To generate SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Deploy

1. Click **Create Web Service**
2. Wait for build (~5 minutes)
3. Once live, note your API URL: `https://ushuaia-travel-api.onrender.com`

### 4. Create Superuser

1. Go to your web service
2. Click **Shell** tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow prompts to create admin user

### 5. Test API

Visit https://your-api-url.onrender.com/api/hotels/

Should return JSON (empty array initially).

## Part 3: React Frontend

### Option A: Static Site on Render

### 1. Update Frontend Environment

Edit `frontend/.env`:
```
VITE_API_URL=https://ushuaia-travel-api.onrender.com/api
```

Commit and push changes.

### 2. Create Static Site

1. Click **New** → **Static Site**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `ushuaia-travel`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

### 3. Deploy
1. Click **Create Static Site**
2. Wait for build
3. Your site will be live at: `https://ushuaia-travel.onrender.com`

### 4. Update Backend CORS

1. Go back to your API web service
2. Update environment variable:
   ```
   CORS_ALLOWED_ORIGINS=https://ushuaia-travel.onrender.com
   ```
3. Service will auto-redeploy

---

## Option B: Vercel/Netlify for Frontend (Recommended)

For better frontend performance, deploy React to Vercel/Netlify:

### Vercel:
1. Import project from GitHub
2. Set root directory to `frontend`
3. Add environment variable:
   ```
   VITE_API_URL=https://ushuaia-travel-api.onrender.com/api
   ```
4. Deploy

### Update CORS:
```
CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
```

---

## 🕷️ GitHub Actions for Scraping

### Setup

1. Go to GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Add secrets:
   - `RENDER_API_KEY`: Get from Render account settings
   - `DATABASE_URL`: Your database internal URL

### Create Workflow

File: `.github/workflows/scrape_hotels.yml`

```yaml
name: Scrape Hotels Monthly

on:
  schedule:
    - cron: '0 3 1 * *'  # 1st of each month at 3 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run scrapers
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
        run: |
          python manage.py scrape_hotels --platform all --max-hotels 100
```

---

## ⚠️ Important Notes - Free Tier Limitations

### Render Free Tier:
- ✅ **Database**: 90 days free trial, then needs paid plan
- ⚠️ **Web services sleep** after 15 min inactivity
- ⚠️ **Slow startup** (~30 sec when waking up)
- ⚠️ **No background workers** (Celery/Redis)
- ✅ **HTTPS** included
- ✅ **Auto-deploy** from GitHub

### Workarounds:
1. Use GitHub Actions for scheduled scraping
2. Use external cron service to ping your API every 14 minutes
3. Upgrade to Railway ($10/mes) when you have traffic

---

## 🔍 Troubleshooting

### Build Fails

**Error: Missing dependencies**
```bash
# Add to requirements.txt any missing packages
```

**Error: Static files not found**
```bash
# Ensure collectstatic runs in build command
```

### API Returns 500

1. Check web service logs in Render dashboard
2. Verify DATABASE_URL is correct
3. Ensure migrations ran: `python manage.py migrate`

### CORS Errors

1. Verify `CORS_ALLOWED_ORIGINS` includes your frontend URL
2. Check frontend is using correct API URL

### Database Connection Fails

1. Use **Internal Database URL** not External
2. Ensure database and web service in same region

---

## 📊 Monitoring

### View Logs
1. Go to web service in Render
2. Click **Logs** tab
3. Monitor requests, errors, etc.

### Admin Panel
Visit: `https://your-api-url.onrender.com/admin`

---

## 🚀 Next Steps

Once deployed and working:

1. Test all API endpoints
2. Add some hotels manually via admin panel
3. Run a test scrape: `python manage.py scrape_hotels --dry-run`
4. Set up GitHub Actions for automated scraping
5. Configure Google AdSense and donation buttons
6. Monitor usage and performance

When you're ready to scale, see [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) for migration guide.

---

**Need help?** Open an issue on GitHub!
