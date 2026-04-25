# 🚀 Railway Deployment Checklist - Career OS

**Date:** April 25, 2026  
**Status:** ✅ Ready for Deployment

---

## ✅ Pre-Deployment Verification

### 1. Branch Status
- ✅ All member branches merged into main
  - ✅ member1/ui-polish - Merged
  - ✅ member2/feature2-feature4-interviews - Merged
  - ✅ member3/feature3-skill-arbitrage - Merged
  - ✅ member4/feature5-job-tracker - Merged
  - ✅ member5/dashboard-analytics-demo - Merged
- ✅ Main branch pushed to GitHub
- ✅ No pending commits

### 2. Railway Configuration Files
- ✅ `Dockerfile.railway` - Present and configured
- ✅ `railway.toml` - Present and configured
- ✅ `Backend/requirements.txt` - All dependencies listed
- ✅ Build context: Repository root
- ✅ Health check endpoint: `/health`

### 3. Application Structure
- ✅ Backend code in `/Backend` directory
- ✅ Frontend code in `/Frontend` directory
- ✅ Database migrations ready
- ✅ Static file serving configured

---

## 🔧 Railway Setup Steps

### Step 1: Create New Project on Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository: `murtazalirizvi/career-os-`
5. Select branch: `main`

### Step 2: Configure Environment Variables

Add these environment variables in Railway dashboard:

```bash
# Required - AI Services
GEMINI_API_KEY=your_gemini_api_key_here
# OR
GOOGLE_API_KEY=your_google_api_key_here

# Optional - OpenRouter Fallback
OPENROUTER_API_KEY=your_openrouter_key_here

# Google OAuth (if using)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://your-app.railway.app/api/auth/google/callback

# Frontend URL
FRONTEND_URL=https://your-app.railway.app

# Database (auto-configured by Railway)
DATA_DIR=/app/data
DATABASE_URL=sqlite:////app/data/career_os.db

# Auth Secret (generate a random string)
CAREER_OS_AUTH_SECRET=your_random_secret_here_min_32_chars
```

### Step 3: Configure Build Settings

Railway should auto-detect:
- ✅ Builder: Dockerfile
- ✅ Dockerfile path: `Dockerfile.railway`
- ✅ Build context: Root directory

### Step 4: Configure Deploy Settings

- ✅ Health check path: `/health`
- ✅ Health check timeout: 60 seconds
- ✅ Restart policy: On failure
- ✅ Max retries: 3

### Step 5: Add Domain (Optional)

1. Go to Settings → Domains
2. Click "Generate Domain" for Railway subdomain
3. Or add custom domain

---

## 📋 Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key for AI features | `AIza...` |
| `GOOGLE_API_KEY` | Alternative to GEMINI_API_KEY | `AIza...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Fallback AI provider | None |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | None |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | None |
| `GOOGLE_REDIRECT_URI` | OAuth callback URL | Auto-detected |
| `FRONTEND_URL` | Frontend base URL | Auto-detected |
| `DATA_DIR` | Data storage directory | `/app/data` |
| `DATABASE_URL` | SQLite database path | `sqlite:////app/data/career_os.db` |
| `CAREER_OS_AUTH_SECRET` | JWT signing secret | `career-os-dev-secret-change-me` |

---

## 🧪 Post-Deployment Testing

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```
Expected response:
```json
{"status": "healthy", "timestamp": "2026-04-25T..."}
```

### 2. API Documentation
Visit: `https://your-app.railway.app/docs`
- Should show Swagger UI with all endpoints

### 3. Frontend Access
Visit: `https://your-app.railway.app/`
- Should load the Career OS landing page
- Check console for errors

### 4. Test Feature Endpoints

**Feature 1 - Resume Analysis:**
```bash
curl -X POST "https://your-app.railway.app/api/feature1/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf" \
  -F "candidate_id=test-user" \
  -F "job_category=Software Engineer"
```

**Feature 2 - Interview Autopsy:**
```bash
curl "https://your-app.railway.app/api/feature2/candidate/test-user/interviews"
```

**Feature 3 - Skill Arbitrage:**
```bash
curl "https://your-app.railway.app/api/feature3/candidate/test-user/snapshots"
```

**Feature 4 - Mock Interviews:**
```bash
curl "https://your-app.railway.app/api/feature4/candidate/test-user/sessions"
```

**Feature 5 - Narrative Architect:**
```bash
curl "https://your-app.railway.app/api/feature5/candidate/test-user/sessions"
```

**Job Tracker:**
```bash
curl "https://your-app.railway.app/api/jobs"
```

---

## 🔍 Monitoring & Logs

### View Logs in Railway
1. Go to your project dashboard
2. Click on the deployment
3. View "Logs" tab for real-time logs

### Key Metrics to Monitor
- ✅ Response times (should be < 5s for most requests)
- ✅ Error rates (should be < 1%)
- ✅ Memory usage (should stay under 512MB)
- ✅ CPU usage (should stay under 80%)

### Common Issues

**Issue: 502 Bad Gateway**
- Solution: Check if health check is passing
- Check logs for startup errors

**Issue: Database errors**
- Solution: Verify DATA_DIR is writable
- Check if database file exists

**Issue: AI features not working**
- Solution: Verify GEMINI_API_KEY is set
- Check API key validity

---

## 🔒 Security Checklist

- ✅ Environment variables stored securely in Railway
- ✅ No secrets committed to repository
- ✅ OAuth secrets removed from code
- ✅ CORS configured properly
- ✅ Rate limiting enabled
- ✅ Input validation on all endpoints
- ✅ SQL injection protection (SQLModel)
- ✅ XSS protection (HTML escaping)

---

## 📊 Performance Optimization

### Enabled Features
- ✅ LRU caching for PDF parsing
- ✅ Database connection pooling
- ✅ Async request handling
- ✅ Static file compression
- ✅ Graceful AI service degradation

### Expected Performance
- Health check: < 100ms
- Resume analysis: 3-10 seconds
- Interview autopsy: 2-5 seconds
- Skill arbitrage: 5-15 seconds
- Mock interview: 1-3 seconds per turn
- Narrative generation: 10-30 seconds

---

## 🚀 Deployment Commands

### Deploy to Railway
```bash
# Railway will auto-deploy on push to main
git push origin main
```

### Manual Redeploy
1. Go to Railway dashboard
2. Click "Redeploy" button
3. Wait for build to complete

### Rollback
1. Go to Deployments tab
2. Find previous successful deployment
3. Click "Redeploy"

---

## 📞 Support & Troubleshooting

### Railway Support
- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Application Logs
```bash
# View logs in Railway dashboard
# Or use Railway CLI:
railway logs
```

### Database Backup
```bash
# Download database from Railway
railway run python -c "import shutil; shutil.copy('data/career_os.db', 'backup.db')"
```

---

## ✅ Final Checklist

Before going live:

- [ ] All environment variables configured
- [ ] Health check passing
- [ ] API documentation accessible
- [ ] Frontend loads correctly
- [ ] All 5 features tested
- [ ] Job tracker tested
- [ ] Authentication working
- [ ] Google OAuth configured (if using)
- [ ] Logs reviewed for errors
- [ ] Performance metrics acceptable
- [ ] Domain configured (if using custom domain)
- [ ] Team notified of deployment URL

---

## 🎉 Deployment Complete!

Your Career OS application is now live on Railway!

**Next Steps:**
1. Share deployment URL with team
2. Monitor logs for first 24 hours
3. Gather user feedback
4. Plan next iteration

**Deployment URL:** `https://your-app.railway.app`
**API Docs:** `https://your-app.railway.app/docs`
**Health Check:** `https://your-app.railway.app/health`
