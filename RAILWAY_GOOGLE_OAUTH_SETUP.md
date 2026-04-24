# Railway Deployment - Google OAuth Configuration

## Railway Deployment URL

Based on your Railway deployment, you'll need to configure Google OAuth with your Railway URLs.

### Finding Your Railway URL

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Select your Career OS project
3. Click on your service
4. Look for the "Domains" section
5. Your URL will be something like: `https://career-os-production.up.railway.app`

**Common Railway URL patterns:**
- `https://your-service-name.up.railway.app`
- `https://your-service-name.railway.app`
- Custom domain if configured

## Google Cloud Console Configuration for Railway

Once you have your Railway URL, add these to your Google Cloud Console:

### 1. Authorized JavaScript Origins

Add these URLs to your Google OAuth Client:

```
Local Development:
http://localhost:5500
http://127.0.0.1:5500
http://localhost:8000
http://127.0.0.1:8000

Railway Production:
https://YOUR-SERVICE-NAME.up.railway.app
https://YOUR-SERVICE-NAME.railway.app
```

**Example** (replace with your actual Railway URL):
```
https://career-os-production.up.railway.app
```

### 2. Authorized Redirect URIs

Add these callback URLs:

```
Local Development:
http://localhost:8000/api/auth/google/callback
http://127.0.0.1:8000/api/auth/google/callback

Railway Production:
https://YOUR-SERVICE-NAME.up.railway.app/api/auth/google/callback
https://YOUR-SERVICE-NAME.railway.app/api/auth/google/callback
```

**Example** (replace with your actual Railway URL):
```
https://career-os-production.up.railway.app/api/auth/google/callback
```

## How to Add URLs to Google Cloud Console

### Step-by-Step Instructions:

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select project: `mens-wear-store-477716`

2. **Navigate to OAuth Credentials**
   - Click "APIs & Services" in left menu
   - Click "Credentials"
   - Find your OAuth 2.0 Client ID: `725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com`
   - Click the edit icon (pencil)

3. **Add Authorized JavaScript Origins**
   - Scroll to "Authorized JavaScript origins"
   - Click "+ ADD URI"
   - Add each origin URL (one at a time)
   - Click "Save" after adding all

4. **Add Authorized Redirect URIs**
   - Scroll to "Authorized redirect URIs"
   - Click "+ ADD URI"
   - Add each callback URL (one at a time)
   - Click "Save" after adding all

## Railway Environment Variables

Make sure these are set in your Railway service:

```env
GOOGLE_CLIENT_ID=725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
```

**Optional** (auto-detected if not set):
```env
GOOGLE_REDIRECT_URI=https://your-service.up.railway.app/api/auth/google/callback
FRONTEND_URL=https://your-service.up.railway.app
```

### How to Set Railway Environment Variables:

1. Go to Railway Dashboard
2. Select your Career OS project
3. Click on your service
4. Go to "Variables" tab
5. Click "New Variable"
6. Add each variable:
   - Variable: `GOOGLE_CLIENT_ID`
   - Value: `725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com`
7. Repeat for `GOOGLE_CLIENT_SECRET`
8. Click "Deploy" to apply changes

## Complete Configuration Checklist

### Local Development ✅
- [x] Backend `.env` has Google credentials
- [x] Frontend has `signInWithGoogle()` function
- [x] Google Console has localhost URLs

### Railway Production ⏳
- [ ] Find your Railway deployment URL
- [ ] Add Railway URL to Google Console (JavaScript origins)
- [ ] Add Railway callback URL to Google Console (redirect URIs)
- [ ] Set `GOOGLE_CLIENT_ID` in Railway environment variables
- [ ] Set `GOOGLE_CLIENT_SECRET` in Railway environment variables
- [ ] Deploy and test Google login on Railway

## Testing on Railway

Once configured:

1. **Visit your Railway URL**
   ```
   https://your-service.up.railway.app
   ```

2. **Click "Continue with Google"**
   - Should redirect to Google login
   - No "redirect_uri_mismatch" error

3. **Sign in with Google**
   - Authorize Career OS
   - Should redirect back to your Railway app
   - Should be logged in automatically

4. **Verify Success**
   - Check browser console for errors
   - Verify you can access all features
   - Check Railway logs for any issues

## Troubleshooting Railway Deployment

### "redirect_uri_mismatch" Error
**Cause**: Railway URL not in Google Console

**Solution**:
1. Copy your exact Railway URL from browser
2. Add to Google Console authorized redirect URIs
3. Make sure to include `/api/auth/google/callback`
4. Wait 1-2 minutes for Google to update

### "Cannot connect to server"
**Cause**: Railway service not running

**Solution**:
1. Check Railway dashboard for service status
2. Check deployment logs for errors
3. Verify environment variables are set
4. Redeploy if necessary

### HTTPS Required
**Note**: Google OAuth requires HTTPS in production. Railway automatically provides HTTPS, so this should work out of the box.

## Quick Reference

### Your Google OAuth Credentials
```
Client ID: 725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com
Client Secret: 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
Project: mens-wear-store-477716
```

### URLs to Configure (Template)
Replace `YOUR-SERVICE-NAME` with your actual Railway service name:

**JavaScript Origins:**
```
https://YOUR-SERVICE-NAME.up.railway.app
```

**Redirect URIs:**
```
https://YOUR-SERVICE-NAME.up.railway.app/api/auth/google/callback
```

## Finding Your Railway Service Name

If you don't know your Railway URL:

1. **Check Railway Dashboard**
   - Login to Railway
   - Find your Career OS project
   - Look at the "Domains" section

2. **Check Railway CLI** (if installed)
   ```bash
   railway status
   ```

3. **Check Git Logs**
   - Railway deployment logs show the URL
   - Check recent deployment notifications

4. **Check Browser History**
   - If you've visited your Railway app before
   - Look for `*.railway.app` or `*.up.railway.app`

## Support

- **Google Cloud Console**: https://console.cloud.google.com/
- **Railway Dashboard**: https://railway.app/dashboard
- **Documentation**: See `GOOGLE_OAUTH_SETUP.md` for detailed technical docs

---

**Next Steps:**
1. Find your Railway deployment URL
2. Add URLs to Google Cloud Console
3. Set environment variables in Railway
4. Test Google login on Railway

**Status**: ⏳ Waiting for Railway URL to complete configuration
