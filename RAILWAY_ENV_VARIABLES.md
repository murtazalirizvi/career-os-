# Railway Environment Variables Configuration

**Project URL:** https://career-os-production.up.railway.app/

---

## 🔑 Required Environment Variables

Copy and paste these into your Railway project settings:

### 1. AI Services (Required)

```bash
# Google Gemini API Key (Primary AI provider)
GEMINI_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Alternative: Google API Key (if GEMINI_API_KEY not set)
GOOGLE_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Get your API key:**
1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy and paste above

---

### 2. Google OAuth (For "Sign in with Google")

```bash
# Google OAuth Client ID
GOOGLE_CLIENT_ID=725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com

# Google OAuth Client Secret
GOOGLE_CLIENT_SECRET=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

# OAuth Redirect URI (Update with your Railway URL)
GOOGLE_REDIRECT_URI=https://career-os-production.up.railway.app/api/auth/google/callback

# Frontend URL (Update with your Railway URL)
FRONTEND_URL=https://career-os-production.up.railway.app
```

**Important:** Update the redirect URI in Google Cloud Console:
1. Go to https://console.cloud.google.com/apis/credentials
2. Select your OAuth 2.0 Client ID
3. Add to "Authorized redirect URIs":
   - `https://career-os-production.up.railway.app/api/auth/google/callback`
4. Add to "Authorized JavaScript origins":
   - `https://career-os-production.up.railway.app`

---

### 3. Authentication Secret

```bash
# JWT Signing Secret (Generate a random 32+ character string)
CAREER_OS_AUTH_SECRET=your_random_secret_min_32_characters_here_change_this
```

**Generate a secure secret:**
```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows PowerShell:
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

---

## 🔧 Optional Environment Variables

### OpenRouter Fallback (Optional)

```bash
# OpenRouter API Key (Fallback AI provider)
OPENROUTER_API_KEY=sk-or-v1-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Get OpenRouter key:**
- Go to https://openrouter.ai/keys
- Create new API key

---

### Database Configuration (Auto-configured)

```bash
# Data directory (Railway default)
DATA_DIR=/app/data

# Database URL (Railway default)
DATABASE_URL=sqlite:////app/data/career_os.db
```

**Note:** These are automatically set by Railway, no need to add manually.

---

## 📋 Quick Copy-Paste Template

Copy this template and fill in your actual values:

```bash
# === REQUIRED ===

# AI Service (Choose one)
GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE
# OR
GOOGLE_API_KEY=YOUR_GOOGLE_KEY_HERE

# Google OAuth
GOOGLE_CLIENT_ID=725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://career-os-production.up.railway.app/api/auth/google/callback
FRONTEND_URL=https://career-os-production.up.railway.app

# Auth Secret (Generate random string)
CAREER_OS_AUTH_SECRET=GENERATE_RANDOM_32_CHAR_STRING_HERE

# === OPTIONAL ===

# OpenRouter Fallback
OPENROUTER_API_KEY=YOUR_OPENROUTER_KEY_HERE
```

---

## 🚀 How to Add Variables in Railway

### Method 1: Railway Dashboard (Recommended)

1. Go to https://railway.app/project/your-project-id
2. Click on your service
3. Go to "Variables" tab
4. Click "New Variable"
5. Add each variable one by one:
   - Variable name: `GEMINI_API_KEY`
   - Value: `your_actual_key`
6. Click "Add"
7. Repeat for all variables

### Method 2: Bulk Add

1. Go to "Variables" tab
2. Click "Raw Editor"
3. Paste all variables in format:
   ```
   GEMINI_API_KEY=your_key
   GOOGLE_CLIENT_ID=your_id
   GOOGLE_CLIENT_SECRET=your_secret
   ```
4. Click "Update Variables"

---

## ✅ Verification Steps

After adding variables:

### 1. Check Health Endpoint
```bash
curl https://career-os-production.up.railway.app/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2026-04-25T..."}
```

### 2. Check API Documentation
Visit: https://career-os-production.up.railway.app/docs

Should show Swagger UI with all endpoints.

### 3. Test Google Sign In

1. Visit: https://career-os-production.up.railway.app/
2. Click "Sign In"
3. Click "Sign in with Google"
4. Should redirect to Google OAuth consent screen

### 4. Test AI Features

Try uploading a resume:
```bash
curl -X POST "https://career-os-production.up.railway.app/api/feature1/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf" \
  -F "candidate_id=test-user" \
  -F "job_category=Software Engineer"
```

---

## 🔒 Security Notes

1. **Never commit secrets to Git**
   - All secrets should only be in Railway environment variables
   - `.env` files are gitignored

2. **Rotate secrets regularly**
   - Change `CAREER_OS_AUTH_SECRET` every 90 days
   - Regenerate OAuth credentials if compromised

3. **Use least privilege**
   - Gemini API key should have minimal permissions
   - OAuth credentials should only have required scopes

4. **Monitor usage**
   - Check Railway logs for unauthorized access
   - Monitor API usage in Google Cloud Console

---

## 🐛 Troubleshooting

### Google Sign In Not Working

**Symptom:** "Sign in with Google" button doesn't appear or fails

**Solutions:**
1. Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
2. Check redirect URI in Google Cloud Console matches exactly:
   - `https://career-os-production.up.railway.app/api/auth/google/callback`
3. Verify `FRONTEND_URL` is set correctly
4. Check Railway logs for OAuth errors

### AI Features Not Working

**Symptom:** Resume analysis returns empty recommendations

**Solutions:**
1. Verify `GEMINI_API_KEY` or `GOOGLE_API_KEY` is set
2. Check API key is valid at https://makersuite.google.com/app/apikey
3. Verify API key has Gemini API enabled
4. Check Railway logs for API errors

### Authentication Errors

**Symptom:** "Invalid token" or "Unauthorized" errors

**Solutions:**
1. Verify `CAREER_OS_AUTH_SECRET` is set and at least 32 characters
2. Clear browser cookies and try again
3. Check Railway logs for JWT errors

---

## 📞 Support

If you encounter issues:

1. **Check Railway Logs:**
   - Go to your Railway project
   - Click "Logs" tab
   - Look for error messages

2. **Verify Environment Variables:**
   - Go to "Variables" tab
   - Ensure all required variables are set
   - Check for typos in variable names

3. **Test Locally:**
   - Clone the repo
   - Add variables to `Backend/.env`
   - Run locally to isolate Railway-specific issues

---

## 🎉 All Set!

Once you've added all environment variables:

1. Railway will automatically redeploy
2. Wait 2-3 minutes for deployment to complete
3. Visit https://career-os-production.up.railway.app/
4. Test Google Sign In
5. Test all features

**Your Career OS is now fully configured and ready to use!** 🚀
