# Google OAuth - Quick Reference Card

## 🎯 Your Google OAuth Credentials

```
Project: mens-wear-store-477716
Client ID: 725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com
Client Secret: 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
```

---

## 🔗 URLs to Add to Google Cloud Console

### Local Development

**JavaScript Origins:**
```
http://localhost:5500
http://127.0.0.1:5500
http://localhost:8000
http://127.0.0.1:8000
```

**Redirect URIs:**
```
http://localhost:8000/api/auth/google/callback
http://127.0.0.1:8000/api/auth/google/callback
```

### Railway Production

**JavaScript Origins:**
```
https://YOUR-RAILWAY-URL.up.railway.app
```

**Redirect URIs:**
```
https://YOUR-RAILWAY-URL.up.railway.app/api/auth/google/callback
```

**Find your Railway URL:**
- Go to: https://railway.app/dashboard
- Select: Career OS project
- Look at: "Domains" section

---

## ⚙️ Railway Environment Variables

```env
GOOGLE_CLIENT_ID=725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
```

---

## 🚀 Quick Test (5 Minutes)

```bash
# 1. Start Backend
cd Backend
python -m uvicorn app.main:app --reload --port 8000

# 2. Open Frontend
# Open Frontend/index.html in browser

# 3. Test
# Click "Continue with Google"
# Sign in
# ✅ Done!
```

---

## 🔧 Google Cloud Console Steps

1. Go to: https://console.cloud.google.com/
2. Select: `mens-wear-store-477716`
3. Navigate: APIs & Services > Credentials
4. Click: Your OAuth 2.0 Client ID
5. Click: Edit (pencil icon)
6. Add: JavaScript origins (see above)
7. Add: Redirect URIs (see above)
8. Click: Save

---

## 📊 Branch Status

| Branch | Status | Action Needed |
|--------|--------|---------------|
| member3 | ✅ Merged | None |
| member1 | ❌ Behind | Sync & push |
| member2 | ❌ Behind | Sync & push |
| member4 | ❌ Behind | Sync & push |
| member5 | ❌ Behind | Sync & push |

---

## 🐛 Common Issues

### "redirect_uri_mismatch"
→ Add exact URI to Google Console

### "Cannot connect to server"
→ Check backend is running on port 8000

### "User not redirected back"
→ Check browser console for errors

---

## 📁 Key Files

```
Backend/.env                    ← Google credentials
Backend/app/api/auth.py        ← OAuth endpoints
Frontend/app.js                ← signInWithGoogle()
railway.toml                   ← Railway config
```

---

## 📚 Documentation

- **GOOGLE_OAUTH_COMPLETE_GUIDE.md** ← Start here
- **GOOGLE_LOGIN_QUICK_START.md** ← Testing guide
- **RAILWAY_GOOGLE_OAUTH_SETUP.md** ← Railway setup
- **GIT_BRANCH_STATUS.md** ← Branch analysis

---

## ✅ Checklist

### Local Setup
- [ ] Backend `.env` has credentials
- [ ] Google Console has localhost URLs
- [ ] Tested locally

### Railway Setup
- [ ] Found Railway URL
- [ ] Added Railway URLs to Google Console
- [ ] Set environment variables in Railway
- [ ] Tested on Railway

---

## 🎯 Next Steps

1. ✅ Test locally (5 min)
2. ⏳ Configure Google Console (10 min)
3. ⏳ Deploy to Railway (15 min)

**Total Time: ~30 minutes**

---

**Quick Links:**
- Google Console: https://console.cloud.google.com/
- Railway Dashboard: https://railway.app/dashboard
- GitHub Repo: https://github.com/murtazalirizvi/career-os-

**Status**: ✅ Implementation Complete | ⏳ Configuration Pending
