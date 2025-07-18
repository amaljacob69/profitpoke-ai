# ProfitPoke AI - Render Deployment Guide

## 🚀 Deploy to Render

### Prerequisites
1. GitHub account
2. Render account (sign up at [render.com](https://render.com))
3. Your code pushed to a GitHub repository

### Step-by-Step Deployment

#### 1. Prepare Your Repository
```bash
# Add all files to git
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

#### 2. Deploy on Render

**Option A: Using render.yaml (Recommended)**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Click "Apply" to deploy

**Option B: Manual Web Service**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `profitpoke-ai`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Instance Type**: `Free` (or paid for better performance)

#### 3. Set Environment Variables
In Render dashboard, go to your service → Environment tab and add:

```
FLASK_SECRET_KEY=your_flask_secret_key_here
KITE_API_KEY=your_kite_api_key_here
KITE_API_SECRET=your_kite_api_secret_here
GROK_API_KEY=your_grok_api_key_here
FLASK_ENV=production
```

#### 4. Deploy
- Render will automatically build and deploy your app
- Your app will be available at: `https://profitpoke-ai.onrender.com`

### 📁 Files Created for Deployment

1. **`render.yaml`** - Render service configuration
2. **`Procfile`** - Process file for web server
3. **`runtime.txt`** - Python version specification
4. **`requirements.txt`** - Updated with gunicorn
5. **`app.py`** - Updated for production deployment

### 🔧 Configuration Details

- **Web Server**: Gunicorn (production WSGI server)
- **Python Version**: 3.13.2
- **Port**: Dynamic (from Render's $PORT environment variable)
- **Health Check**: Root path (`/`)
- **Auto-deploy**: Enabled on git push

### 🔒 Security Notes

- Environment variables are stored securely in Render
- `.env` file is excluded from deployment via `.gitignore`
- Flask secret key is set for session security
- CSRF protection is enabled via Flask-WTF

### 🚨 Important Notes

1. **Free Tier Limitations**:
   - Service spins down after 15 minutes of inactivity
   - Cold starts may take 30+ seconds
   - 750 hours/month limit

2. **First Deployment**:
   - May take 5-10 minutes to complete
   - Watch build logs in Render dashboard

3. **Debugging**:
   - Check Render logs if deployment fails
   - Ensure all dependencies are in requirements.txt
   - Verify environment variables are set correctly

### 📊 Post-Deployment

1. Test your app at the provided URL
2. Check that all features work correctly
3. Monitor logs for any errors
4. Set up custom domain (optional, paid feature)

### 🔄 Updates

To deploy updates:
```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically redeploy your application.

---

## 🎯 Alternative Deployment Platforms

If you prefer other platforms, the same files work for:
- **Heroku**: Uses `Procfile` and `runtime.txt`
- **Railway**: Uses same configuration
- **Fly.io**: Can use similar setup
- **PythonAnywhere**: Manual deployment with requirements.txt

Good luck with your deployment! 🚀
