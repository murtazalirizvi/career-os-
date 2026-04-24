# Google Login - Quick Start Guide

## ✅ Implementation Complete

Google OAuth login has been successfully integrated into Career OS!

## What Was Done

### 1. Backend Configuration ✓
- Added Google OAuth credentials to `Backend/.env`:
  - `GOOGLE_CLIENT_ID=725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com`
  - `GOOGLE_CLIENT_SECRET=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`
- Backend endpoints already exist (no changes needed):
  - `GET /api/auth/google/url` - Returns Google OAuth URL
  - `GET /api/auth/google/callback` - Handles OAuth callback

### 2. Frontend Integration ✓
- Added `signInWithGoogle()` function in `Frontend/app.js`
- Added OAuth callback handler to process tokens from Google
- Google Sign-In button already exists in the UI

## How to Test

### Step 1: Start the Backend
```bash
cd Backend
python -m uvicorn app.main:app --reload --port 8000
```

### Step 2: Open the Frontend
Open `Frontend/index.html` in your browser or use Live Server:
- http://localhost:5500/Frontend/index.html
- or http://127.0.0.1:5500/Frontend/index.html

### Step 3: Test Google Login
1. Click "Get Started Free" or "Sign In" on the landing page
2. In the auth modal, click "Continue with Google"
3. You'll be redirected to Google's login page
4. Sign in with your Google account
5. Authorize Career OS to access your profile
6. You'll be redirected back and automatically logged in!

## How It Works

```
User clicks "Continue with Google"
    ↓
Frontend fetches OAuth URL from backend
    ↓
User redirected to Google login
    ↓
User authorizes Career OS
    ↓
Google redirects to backend callback
    ↓
Backend creates/finds user account
    ↓
Backend redirects to frontend with token
    ↓
Frontend stores token and shows app
```

## Google Cloud Console Setup

Your Google OAuth app is already configured with these credentials:
- **Project**: mens-wear-store-477716
- **Client ID**: 725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com

### Required Settings in Google Cloud Console

1. **Authorized JavaScript origins** (add these if not present):
   ```
   http://localhost:5500
   http://127.0.0.1:5500
   http://localhost:8000
   http://127.0.0.1:8000
   ```

2. **Authorized redirect URIs** (add these if not present):
   ```
   http://localhost:8000/api/auth/google/callback
   http://127.0.0.1:8000/api/auth/google/callback
   ```

3. **OAuth consent screen**:
   - Scopes: `openid`, `email`, `profile`

## Troubleshooting

### "redirect_uri_mismatch" Error
**Problem**: Google shows an error about redirect URI mismatch

**Solution**: 
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project "mens-wear-store-477716"
3. Go to APIs & Services > Credentials
4. Click on your OAuth 2.0 Client ID
5. Add the redirect URI exactly as shown above

### "Cannot connect to server"
**Problem**: Frontend can't reach backend

**Solution**:
1. Make sure backend is running: `cd Backend && python -m uvicorn app.main:app --reload --port 8000`
2. Check that port 8000 is not blocked by firewall
3. Verify `API_BASE` in `Frontend/app.js` points to `http://127.0.0.1:8000`

### User Not Redirected Back
**Problem**: After Google login, nothing happens

**Solution**:
1. Check browser console for JavaScript errors
2. Verify backend logs show the callback was received
3. Check that `FRONTEND_URL` is not set (let it auto-detect) or set correctly

### Token Not Stored
**Problem**: User redirected but not logged in

**Solution**:
1. Open browser DevTools > Application > Session Storage
2. Check if `cos_token` and `cos_candidate` are present
3. If not, check browser console for errors
4. Verify the URL fragment contains `#google_token=...`

## Files Modified

1. ✅ `Backend/.env` - Added Google OAuth credentials
2. ✅ `Backend/.env.example` - Added Google OAuth template
3. ✅ `Frontend/app.js` - Added Google OAuth functions
4. ✅ `Frontend/index.html` - Already had Google button (no changes)

## Security Notes

- ⚠️ Never commit `.env` file to version control
- ⚠️ Client secret must remain private
- ⚠️ Use HTTPS in production
- ✅ Tokens stored in sessionStorage (cleared on browser close)
- ✅ Backend validates all OAuth responses

## Production Deployment

When deploying to production:

1. Update Google Cloud Console with production URLs
2. Set environment variables on your hosting platform
3. Ensure HTTPS is enabled
4. Test the complete flow

## Support

For detailed documentation, see `GOOGLE_OAUTH_SETUP.md`

---

**Status**: ✅ Ready to use
**Last Updated**: 2026-04-25
