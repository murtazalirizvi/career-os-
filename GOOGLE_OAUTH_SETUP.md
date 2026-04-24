# Google OAuth Integration - Complete Setup

## Overview
Google OAuth login has been successfully integrated into Career OS, allowing users to sign in with their Google accounts.

## Backend Configuration

### Environment Variables
The following Google OAuth credentials have been added to `Backend/.env`:

```env
GOOGLE_CLIENT_ID=725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
```

Optional environment variables (auto-detected if not set):
- `GOOGLE_REDIRECT_URI` - Override the redirect URI (defaults to `{base_url}/api/auth/google/callback`)
- `FRONTEND_URL` - Frontend URL for post-login redirect (defaults to request base URL)

### Backend Endpoints
The backend already has these Google OAuth endpoints implemented in `Backend/app/api/auth.py`:

1. **GET /api/auth/google/url**
   - Returns the Google OAuth consent URL
   - Frontend redirects users to this URL to start OAuth flow

2. **GET /api/auth/google/callback**
   - Handles the OAuth callback from Google
   - Exchanges authorization code for access token
   - Fetches user info from Google
   - Creates or finds user account
   - Issues Career OS session token
   - Redirects to frontend with token in URL fragment

## Frontend Implementation

### Changes Made

#### 1. Added `signInWithGoogle()` function in `Frontend/app.js`:
```javascript
async function signInWithGoogle() {
  const errEl = document.getElementById("auth-error");
  errEl.style.display = "none";

  if (!API_BASE) {
    errEl.textContent = "No backend available on GitHub Pages. Use 'Continue without account' or run locally.";
    errEl.style.display = "block";
    return;
  }

  try {
    // Get the Google OAuth URL from backend
    const res = await fetch(`${API_BASE}/api/auth/google/url`);
    if (!res.ok) {
      throw new Error("Failed to get Google OAuth URL");
    }
    const data = await res.json();
    
    // Redirect to Google OAuth consent screen
    window.location.href = data.url;
  } catch (error) {
    errEl.textContent = "Cannot connect to server. Make sure the backend is running.";
    errEl.style.display = "block";
  }
}
```

#### 2. Added OAuth callback handler in DOMContentLoaded:
The app now checks for `#google_token` and `#candidate_id` in the URL fragment when the page loads. If found:
- Stores the token and candidate ID in sessionStorage
- Cleans up the URL
- Shows the app interface
- Updates all candidate ID input fields

#### 3. Google Sign-In Button
The button already exists in `Frontend/index.html` (line ~927):
```html
<button onclick="signInWithGoogle()" ...>
  <svg><!-- Google logo --></svg>
  Continue with Google
</button>
```

## OAuth Flow

1. **User clicks "Continue with Google"**
   - Frontend calls `/api/auth/google/url`
   - Receives Google OAuth consent URL
   - Redirects user to Google

2. **User authorizes on Google**
   - Google redirects back to `/api/auth/google/callback?code=...`
   - Backend exchanges code for access token
   - Backend fetches user profile from Google
   - Backend creates/finds user account
   - Backend issues Career OS session token

3. **Backend redirects to frontend**
   - URL: `{FRONTEND_URL}/#google_token={token}&candidate_id={id}`
   - Frontend detects token in URL fragment
   - Stores token and shows app

## Google Cloud Console Setup

### Required Configuration
In your Google Cloud Console project (mens-wear-store-477716):

1. **Authorized JavaScript origins:**
   - `http://localhost:5500` (local development)
   - `http://127.0.0.1:5500` (local development)
   - `http://localhost:8000` (backend)
   - Your production domain (e.g., `https://yourdomain.com`)

2. **Authorized redirect URIs:**
   - `http://localhost:8000/api/auth/google/callback`
   - `http://127.0.0.1:8000/api/auth/google/callback`
   - Your production backend URL + `/api/auth/google/callback`

### OAuth Consent Screen
- Application name: Career OS
- Scopes required:
  - `openid`
  - `email`
  - `profile`

## Testing

### Local Development
1. Start backend: `cd Backend && python -m uvicorn app.main:app --reload --port 8000`
2. Start frontend: Open `Frontend/index.html` in browser or use Live Server on port 5500
3. Click "Continue with Google" in the auth modal
4. Authorize with your Google account
5. You should be redirected back and logged in

### Verify It Works
- Check browser console for any errors
- Verify sessionStorage has `cos_token` and `cos_candidate`
- Check backend logs for OAuth flow
- Verify user is created in database

## Security Notes

1. **Client Secret**: The `GOOGLE_CLIENT_SECRET` is stored in `.env` and should NEVER be committed to version control
2. **Token Storage**: Session tokens are stored in sessionStorage (cleared on browser close)
3. **HTTPS Required**: In production, all OAuth flows must use HTTPS
4. **Redirect URI Validation**: Google validates redirect URIs against your configured list

## Troubleshooting

### "redirect_uri_mismatch" error
- Ensure the redirect URI in Google Cloud Console exactly matches what the backend sends
- Check for trailing slashes, http vs https, port numbers

### "Cannot connect to server"
- Verify backend is running on port 8000
- Check CORS settings in backend allow your frontend origin
- Verify `API_BASE` is correctly set in frontend

### User not redirected back
- Check browser console for errors
- Verify `FRONTEND_URL` environment variable (or let it auto-detect)
- Check backend logs for callback errors

## Production Deployment

When deploying to production:

1. Update Google Cloud Console with production URLs
2. Set environment variables:
   ```env
   GOOGLE_CLIENT_ID=725587084001-uom0v453423j1g26rfdgd7m6981rh5ea.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=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
   GOOGLE_REDIRECT_URI=https://your-backend.com/api/auth/google/callback
   FRONTEND_URL=https://your-frontend.com
   ```
3. Ensure HTTPS is enabled
4. Test the complete OAuth flow

## Files Modified

1. `Backend/.env` - Added Google OAuth credentials
2. `Backend/.env.example` - Added Google OAuth configuration template
3. `Frontend/app.js` - Added `signInWithGoogle()` function and callback handler
4. `Frontend/index.html` - Already had Google Sign-In button (no changes needed)

## Next Steps

- Test the Google login flow locally
- Update Google Cloud Console with production URLs when ready
- Consider adding error handling for edge cases
- Add loading states during OAuth redirect
- Consider adding "Sign in with Google" to the landing page CTAs
