# Career OS - Localhost Setup & Links

## 🚀 Quick Start - Run Locally

### Step 1: Start the Backend

Open a terminal and run:

```bash
cd Backend
python -m uvicorn app.main:app --reload --port 8000
```

**Backend will be available at:**
- 🔗 **API**: http://localhost:8000
- 🔗 **API Docs**: http://localhost:8000/docs
- 🔗 **Health Check**: http://localhost:8000/health

### Step 2: Open the Frontend

**Option A: Direct File Access**
- Navigate to the `Frontend` folder
- Double-click `index.html`
- Or right-click → Open with → Your browser

**Option B: Live Server (Recommended)**
If you have VS Code with Live Server extension:
1. Open `Frontend/index.html` in VS Code
2. Right-click → "Open with Live Server"
3. Frontend will open at: http://localhost:5500/Frontend/index.html

**Option C: Python HTTP Server**
```bash
cd Frontend
python -m http.server 5500
```
Then open: http://localhost:5500

---

## 🔗 All Localhost Links

### Backend URLs
| Service | URL | Description |
|---------|-----|-------------|
| API Base | http://localhost:8000 | Main API endpoint |
| API Documentation | http://localhost:8000/docs | Interactive API docs (Swagger) |
| Alternative Docs | http://localhost:8000/redoc | ReDoc API documentation |
| Health Check | http://localhost:8000/health | Server health status |
| Google OAuth URL | http://localhost:8000/api/auth/google/url | Get Google login URL |
| Google Callback | http://localhost:8000/api/auth/google/callback | OAuth callback (auto) |

### Frontend URLs
| Service | URL | Description |
|---------|-----|-------------|
| Main App | http://localhost:5500/Frontend/index.html | Career OS application |
| Alternative | http://127.0.0.1:5500/Frontend/index.html | Same as above |
| Direct File | file:///path/to/Frontend/index.html | Direct file access |

---

## 🧪 Test the Application

### 1. Verify Backend is Running

Open in browser: http://localhost:8000/health

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-25T..."
}
```

### 2. Check API Documentation

Open: http://localhost:8000/docs

You should see:
- Interactive API documentation
- All available endpoints
- Try out features

### 3. Open the Frontend

Open: http://localhost:5500/Frontend/index.html

You should see:
- Beautiful landing page
- "Get Started Free" button
- "Sign In" button

### 4. Test Google OAuth

1. Click "Get Started Free" or "Sign In"
2. Click "Continue with Google"
3. Sign in with your Google account
4. You should be redirected back and logged in!

---

## 🔧 Troubleshooting

### Backend Not Starting

**Problem**: `python -m uvicorn app.main:app --reload --port 8000` fails

**Solutions:**
```bash
# Check if Python is installed
python --version

# Check if uvicorn is installed
pip install uvicorn

# Check if port 8000 is already in use
# Windows:
netstat -ano | findstr :8000

# Kill the process if needed (replace PID)
taskkill /PID <PID> /F
```

### Frontend Not Loading

**Problem**: Frontend shows blank page or errors

**Solutions:**
1. Check browser console (F12) for errors
2. Verify backend is running on port 8000
3. Check CORS settings
4. Try a different browser

### Google OAuth Not Working

**Problem**: "redirect_uri_mismatch" error

**Solution:**
Add these to Google Cloud Console:
```
http://localhost:8000/api/auth/google/callback
http://127.0.0.1:8000/api/auth/google/callback
```

### Cannot Connect to Server

**Problem**: Frontend shows "Cannot connect to server"

**Solutions:**
1. Verify backend is running: http://localhost:8000/health
2. Check `API_BASE` in `Frontend/app.js` is set to `http://127.0.0.1:8000`
3. Check firewall isn't blocking port 8000

---

## 📱 Access from Mobile/Other Devices

### Find Your Local IP

**Windows:**
```bash
ipconfig
# Look for "IPv4 Address" (e.g., 192.168.1.100)
```

**Mac/Linux:**
```bash
ifconfig
# Look for "inet" address
```

### Update Backend CORS

Add your IP to `Backend/.env`:
```env
ALLOWED_ORIGINS=http://localhost:5500,http://192.168.1.100:5500
```

### Access from Mobile

1. Make sure mobile is on same WiFi network
2. Open: http://YOUR-IP:5500/Frontend/index.html
3. Example: http://192.168.1.100:5500/Frontend/index.html

---

## 🎯 Quick Links Summary

### For Development
- **Frontend**: http://localhost:5500/Frontend/index.html
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### For Testing
- **Health Check**: http://localhost:8000/health
- **Google OAuth**: Click "Continue with Google" in app

### For Debugging
- **Browser Console**: Press F12
- **Backend Logs**: Check terminal where uvicorn is running
- **Network Tab**: F12 → Network tab

---

## 📋 Complete Setup Checklist

### Backend Setup
- [ ] Python 3.12+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with API keys
- [ ] Backend running on port 8000
- [ ] Health check returns "healthy"

### Frontend Setup
- [ ] Frontend folder accessible
- [ ] `index.html` opens in browser
- [ ] No console errors (F12)
- [ ] Can see landing page

### Google OAuth Setup
- [ ] Google credentials in `Backend/.env`
- [ ] Localhost URLs in Google Cloud Console
- [ ] "Continue with Google" button visible
- [ ] Can sign in with Google account

### Testing
- [ ] Backend health check works
- [ ] API docs accessible
- [ ] Frontend loads correctly
- [ ] Google login works
- [ ] Can access all features

---

## 🚀 Start Commands (Copy & Paste)

### Terminal 1: Backend
```bash
cd Backend
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend (Optional - if using Python server)
```bash
cd Frontend
python -m http.server 5500
```

### Or Just Open in Browser
```
file:///C:/Users/SIKANDAR/Desktop/Career/career-os-/Frontend/index.html
```

---

## 🎉 You're Ready!

Once both backend and frontend are running:

1. **Open**: http://localhost:5500/Frontend/index.html
2. **Click**: "Get Started Free"
3. **Sign in**: With Google or create account
4. **Enjoy**: Career OS features!

---

## 📞 Need Help?

### Check Logs
- **Backend**: Terminal where uvicorn is running
- **Frontend**: Browser console (F12)

### Common Issues
- Port already in use → Kill the process or use different port
- CORS errors → Check `ALLOWED_ORIGINS` in `.env`
- Google OAuth errors → Check Google Cloud Console URLs

### Documentation
- See `GOOGLE_OAUTH_COMPLETE_GUIDE.md` for OAuth setup
- See `GOOGLE_LOGIN_QUICK_START.md` for testing guide
- See `Backend/DEPLOYMENT.md` for deployment info

---

**Status**: ✅ Ready to run locally
**Last Updated**: April 25, 2026
