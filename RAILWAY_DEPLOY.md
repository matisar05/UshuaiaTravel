# 🚂 Migrating from Render to Railway

This guide covers migrating your Ushuaia Travel app from Render (free tier) to Railway for production deployment with better performance and features.

## 🎯 Why Railway?

**Advantages over Render Free Tier:**
- ✅ No app sleep after inactivity
- ✅ Faster startup times
- ✅ Celery + Redis support (background tasks)
- ✅ Better performance overall
- ✅ Simple pricing: ~$10-15/month for everything
- ✅ GitHub auto-deployment

## 📋 Prerequisites

- Railway account: https://railway.app
- Your project currently running on Render
- GitHub repository access

---

## Step 1: Export Database from Render

### 1.1 Create Database Backup

```bash
# Install PostgreSQL tools locally
# Ubuntu/Debian:
sudo apt-get install postgresql-client

# Mac:
brew install postgresql

# Connect to Render database and create dump
pg_dump <RENDER_EXTERNAL_DATABASE_URL> > ushuaia_backup.sql
```

**Get External Database URL:**
1. Go to Render database
2. Copy **External Database URL**
3. Use in command above

### 1.2 Download Backup

Keep the `ushuaia_backup.sql` file  safe.

---

## Step 2: Set Up Railway Project

### 2.1 Create New Project

1. Go to https://railway.app
2. Click **New Project**
3. Select **Deploy from GitHub repo**
4. Choose your `ushuaia-travel` repository
5. Railway will detect it's a Python project

### 2.2 Configure Build Settings

Railway auto-detects Django, but verify:

**Start Command:**
```bash
gunicorn ushuaia_travel.wsgi:application
```

**Build Command** (if needed):
```bash
python manage.py collectstatic --noinput && python manage.py migrate
```

---

## Step 3: Add PostgreSQL Database

### 3.1 Add Database Service

1. In your Railway project dashboard
2. Click **New** → **Database** → **Add PostgreSQL**
3. Railway will create and configure automatically

### 3.2 Get Connection String

1. Click on PostgreSQL service
2. Go to **Variables** tab
3. You'll see `DATABASE_URL` automatically generated
4. Railway automatically injects this into your Django service ✅

---

## Step 4: Import Data

### 4.1 Connect to Railway Database

1. In PostgreSQL service, go to **Settings** → **Database**
2. Note connection details or use Railway CLI

**Option A: Railway CLI (Recommended)**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Connect to database
railway run psql -d <database_name> -f ushuaia_backup.sql
```

**Option B: Direct Connection**

```bash
# Use connection string from Railway
psql <RAILWAY_DATABASE_URL> < ushuaia_backup.sql
```

---

## Step 5: Environment Variables

### 5.1 Add Variables to Django Service

In Railway dashboard, go to your Django service → **Variables**:

```
SECRET_KEY=<new-secret-key>
DEBUG=False
ALLOWED_HOSTS=.railway.app,.up.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend.railway.app
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SCRAPER_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
SCRAPER_DELAY_MS=2000
```

**Note:** `DATABASE_URL` is automatically set by Railway ✅

---

## Step 6: Deploy Frontend

### Option A: Deploy on Railway

1. In same project, click **New Service**
2. Select **GitHub Repo** → choose same repo
3. Configure:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview` (or use serve)

4. Add environment variable:
   ```
   VITE_API_URL=https://your-django-service.up.railway.app/api
   ```

### Option B: Keep on Vercel/Netlify

Just update the API URL:
```
VITE_API_URL=https://your-django-service.up.railway.app/api
```

---

## Step 7: Set Up Redis (Optional but Recommended)

For future Celery support:

1. Click **New** → **Database** → **Add Redis**
2. Railway auto-configures with `REDIS_URL`
3. Update `settings.py` when ready to use Celery

---

## Step 8: Configure Custom Domains (Optional)

### 8.1 Backend Domain

1. Go to Django service → **Settings** → **Networking**
2. Click **Generate Domain** or add custom domain
3. Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`

### 8.2 Frontend Domain

Same process for frontend service.

---

## Step 9: Set Up Celery for Automated Scraping

With Railway, you can now run background tasks!

### 9.1 Add Celery to requirements.txt

```txt
celery==5.3.4
redis==5.0.1
```

### 9.2 Create Celery Config

**File: `ushuaia_travel/celery.py`**

```python
import os
from celery import Celery

os.setdefault('DJANGO_SETTINGS_MODULE', 'ushuaia_travel.settings')

app = Celery('ushuaia_travel')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### 9.3 Add to settings.py

```python
# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
```

### 9.4 Create Celery Worker Service

1. In Railway, click **New Service** → **GitHub Repo** (same repo)
2. Configure:
   - **Start Command**: `celery -A ushuaia_travel worker -l info`
   - All same environment variables as Django service

### 9.5 Create Celery Beat Service (Scheduler)

1. Another new service
2. **Start Command**: `celery -A ushuaia_travel beat -l info`

### 9.6 Create Periodic Task

**File: `hotels/tasks.py`**

```python
from celery import shared_task
from .management.commands.scrape_hotels import Command

@shared_task
def scrape_all_hotels():
    """Scheduled task to scrape hotels."""
    command = Command()
    command.handle(platform='all', max_hotels=100)
```

**Configure Schedule in settings.py:**

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'scrape-hotels-monthly': {
        'task': 'hotels.tasks.scrape_all_hotels',
        'schedule': crontab(day_of_month='1', hour='3', minute='0'),
    },
}
```

---

## Step 10: Verify Deployment

### 10.1 Test API

```bash
curl https://your-django-service.up.railway.app/api/hotels/
```

### 10.2 Check Admin Panel

Visit: `https://your-django-service.up.railway.app/admin`

### 10.3 Test Frontend

Visit your frontend URL and ensure hotels load.

---

## 💰 Cost Estimation

**Railway Pricing (Pay for what you use):**

- PostgreSQL: ~$5/month
- Django Web Service: ~$5/month
- Redis: ~$2/month
- Celery Worker: ~$3/month
- Celery Beat: ~$2/month
- Frontend (if hosted): ~$3/month

**Total: ~$15-20/month** for full production setup with background tasks.

**Note:** Railway gives $5 free credit/month, so effectively ~$10-15/month.

---

## 📊 Monitoring on Railway

### View Logs

Each service has a **Logs** tab with real-time output.

### Metrics

Go to **Metrics** tab to see:
- CPU usage
- Memory usage
- Network traffic
- Response times

### Alerts

Set up alerts for when services go down or exceed usage thresholds.

---

## 🔄 Rollback Plan

If something goes wrong:

1. Keep Render running during migration
2. Test Railway thoroughly
3. Update DNS/URLs only when confident
4. Can always switch back by updating environment variables

---

## 🎉 Post-Migration Checklist

- [ ] All services running on Railway
- [ ] Database migrated successfully
- [ ] API endpoints working
- [ ] Frontend connected to new API
- [ ] Admin panel accessible
- [ ] Celery workers running (if configured)
- [ ] Scheduled scraping working
- [ ] Custom domains configured (if applicable)
- [ ] Monitoring set up
- [ ] Old Render services paused/deleted

---

## 🆘 Troubleshooting

### Database Connection Issues

- Check `DATABASE_URL` is set correctly
- Ensure all services in same Railway project
- Try restarting Django service

### Celery Not Working

- Verify Redis is running
- Check `REDIS_URL` environment variable
- View Celery worker logs

### Build Failures

- Check Railway build logs
- Ensure `requirements.txt` is up to date
- Verify Python version compatibility

---

## 📚 Additional Resources

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Celery Docs: https://docs.celeryq.dev

---

**Welcome to production! 🚀**
