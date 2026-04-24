# Google OAuth Flow Diagram

## Complete Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER JOURNEY                                 │
└─────────────────────────────────────────────────────────────────────┘

1. USER INITIATES LOGIN
   ┌──────────────┐
   │   Frontend   │
   │  (Browser)   │
   └──────┬───────┘
          │ User clicks "Continue with Google"
          │
          ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ JavaScript: signInWithGoogle()                                │
   │ - Fetches: GET /api/auth/google/url                          │
   └──────┬───────────────────────────────────────────────────────┘
          │
          ▼
   ┌──────────────┐
   │   Backend    │
   │  (FastAPI)   │
   └──────┬───────┘
          │ Returns Google OAuth URL with:
          │ - client_id
          │ - redirect_uri
          │ - scope (openid, email, profile)
          │
          ▼
   ┌──────────────┐
   │   Frontend   │
   └──────┬───────┘
          │ window.location.href = google_oauth_url
          │
          ▼

2. GOOGLE AUTHENTICATION
   ┌──────────────────┐
   │  Google OAuth    │
   │  Consent Screen  │
   └──────┬───────────┘
          │ User signs in with Google
          │ User authorizes Career OS
          │
          ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ Google redirects to:                                          │
   │ http://localhost:8000/api/auth/google/callback?code=ABC123   │
   └──────┬───────────────────────────────────────────────────────┘
          │
          ▼

3. BACKEND PROCESSES CALLBACK
   ┌──────────────┐
   │   Backend    │
   │  (FastAPI)   │
   └──────┬───────┘
          │
          ├─► Exchange code for access_token
          │   POST https://oauth2.googleapis.com/token
          │
          ├─► Fetch user info
          │   GET https://www.googleapis.com/oauth2/v3/userinfo
          │   Returns: { email, name, picture }
          │
          ├─► Find or create user in database
          │   - Check if email exists
          │   - Create new user if needed
          │   - Generate candidate_id from email
          │
          ├─► Issue Career OS session token
          │   - Generate secure token
          │   - Store in UserSessionToken table
          │   - Set expiry (7 days)
          │
          ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ Redirect to frontend:                                         │
   │ http://localhost:5500/#google_token=XYZ&candidate_id=user123 │
   └──────┬───────────────────────────────────────────────────────┘
          │
          ▼

4. FRONTEND COMPLETES LOGIN
   ┌──────────────┐
   │   Frontend   │
   │  (Browser)   │
   └──────┬───────┘
          │
          ├─► Parse URL fragment
          │   - Extract google_token
          │   - Extract candidate_id
          │
          ├─► Store in sessionStorage
          │   sessionStorage.setItem('cos_token', token)
          │   sessionStorage.setItem('cos_candidate', id)
          │
          ├─► Clean up URL
          │   window.history.replaceState(...)
          │
          ├─► Update UI
          │   - Hide landing page
          │   - Show app shell
          │   - Populate candidate ID fields
          │
          ▼
   ┌──────────────────┐
   │  User is logged  │
   │  in and ready!   │
   └──────────────────┘
```

## Data Flow

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │         │   Backend   │         │   Google    │
│  (Browser)  │         │  (FastAPI)  │         │   OAuth     │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       │ 1. Get OAuth URL      │                       │
       │──────────────────────>│                       │
       │                       │                       │
       │ 2. Return URL         │                       │
       │<──────────────────────│                       │
       │                       │                       │
       │ 3. Redirect to Google │                       │
       │───────────────────────────────────────────────>│
       │                       │                       │
       │                       │ 4. User authorizes    │
       │                       │<──────────────────────│
       │                       │                       │
       │                       │ 5. Callback with code │
       │                       │<──────────────────────│
       │                       │                       │
       │                       │ 6. Exchange code      │
       │                       │──────────────────────>│
       │                       │                       │
       │                       │ 7. Return access token│
       │                       │<──────────────────────│
       │                       │                       │
       │                       │ 8. Get user info      │
       │                       │──────────────────────>│
       │                       │                       │
       │                       │ 9. Return user data   │
       │                       │<──────────────────────│
       │                       │                       │
       │ 10. Redirect with token                       │
       │<──────────────────────│                       │
       │                       │                       │
       │ 11. Store token & show app                    │
       │                       │                       │
```

## Security Considerations

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                           │
└─────────────────────────────────────────────────────────────┘

1. CLIENT SECRET PROTECTION
   ✓ Stored in .env (never in frontend)
   ✓ Not committed to version control
   ✓ Only backend has access

2. TOKEN SECURITY
   ✓ Session tokens hashed with SHA-256
   ✓ Stored in sessionStorage (cleared on close)
   ✓ 7-day expiry with refresh capability
   ✓ Can be revoked via logout

3. REDIRECT URI VALIDATION
   ✓ Google validates redirect URI
   ✓ Must match configured URIs exactly
   ✓ Prevents redirect attacks

4. STATE PARAMETER (Future Enhancement)
   ⚠ Consider adding CSRF protection
   ⚠ Generate random state token
   ⚠ Validate on callback

5. HTTPS REQUIREMENT
   ⚠ Required in production
   ⚠ Protects tokens in transit
   ⚠ Prevents man-in-the-middle attacks
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                    UserAccount Table                         │
├─────────────────────────────────────────────────────────────┤
│ id              INTEGER PRIMARY KEY                          │
│ candidate_id    TEXT UNIQUE (e.g., "john-doe")              │
│ email           TEXT UNIQUE (from Google)                    │
│ full_name       TEXT (from Google)                           │
│ password_hash   TEXT (random for Google users)              │
│ is_active       BOOLEAN (default: true)                      │
│ created_at      TIMESTAMP                                    │
│ updated_at      TIMESTAMP                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 UserSessionToken Table                       │
├─────────────────────────────────────────────────────────────┤
│ id              INTEGER PRIMARY KEY                          │
│ user_id         INTEGER (FK to UserAccount)                  │
│ token_hash      TEXT (SHA-256 hash)                          │
│ label           TEXT (e.g., "google-oauth")                  │
│ expires_at      TIMESTAMP (7 days from creation)            │
│ revoked_at      TIMESTAMP (NULL if active)                   │
│ created_at      TIMESTAMP                                    │
└─────────────────────────────────────────────────────────────┘
```

## Environment Variables

```
┌─────────────────────────────────────────────────────────────┐
│                    Backend/.env                              │
├─────────────────────────────────────────────────────────────┤
│ # Required                                                   │
│ GOOGLE_CLIENT_ID=725587084001-...                           │
│ GOOGLE_CLIENT_SECRET=GOCSPX-...                             │
│                                                              │
│ # Optional (auto-detected if not set)                       │
│ GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/...     │
│ FRONTEND_URL=http://localhost:5500                          │
│                                                              │
│ # Security                                                   │
│ CAREER_OS_AUTH_SECRET=your-secret-key                       │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling

```
┌─────────────────────────────────────────────────────────────┐
│                    ERROR SCENARIOS                           │
└─────────────────────────────────────────────────────────────┘

1. REDIRECT_URI_MISMATCH
   Cause: URI not in Google Console
   Fix: Add URI to authorized list

2. INVALID_CLIENT
   Cause: Wrong client ID or secret
   Fix: Verify credentials in .env

3. ACCESS_DENIED
   Cause: User declined authorization
   Action: Show friendly message, allow retry

4. NETWORK_ERROR
   Cause: Backend not running
   Fix: Start backend server

5. TOKEN_EXPIRED
   Cause: Session expired (>7 days)
   Action: Redirect to login

6. USER_INACTIVE
   Cause: Account deactivated
   Action: Show account status message
```

## Testing Checklist

```
□ Backend starts without errors
□ Frontend loads without errors
□ "Continue with Google" button visible
□ Clicking button redirects to Google
□ Can sign in with Google account
□ Redirected back to frontend
□ Token stored in sessionStorage
□ App shell displays correctly
□ Candidate ID populated
□ Can access protected endpoints
□ Logout clears session
□ Can log in again
```

## Production Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                 PRODUCTION CHECKLIST                         │
└─────────────────────────────────────────────────────────────┘

1. Google Cloud Console
   □ Add production URLs to authorized origins
   □ Add production callback to redirect URIs
   □ Verify OAuth consent screen
   □ Test with real users

2. Environment Variables
   □ Set GOOGLE_CLIENT_ID
   □ Set GOOGLE_CLIENT_SECRET
   □ Set GOOGLE_REDIRECT_URI (production)
   □ Set FRONTEND_URL (production)
   □ Set CAREER_OS_AUTH_SECRET (strong random)

3. Security
   □ Enable HTTPS
   □ Configure CORS properly
   □ Set secure cookie flags
   □ Enable rate limiting
   □ Monitor for suspicious activity

4. Testing
   □ Test complete OAuth flow
   □ Test error scenarios
   □ Test on multiple browsers
   □ Test on mobile devices
   □ Load test authentication endpoints
```

---

**Implementation Status**: ✅ Complete and Ready
**Last Updated**: 2026-04-25
