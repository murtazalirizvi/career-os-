#!/usr/bin/env python3
"""Quick test to verify Google OAuth setup"""

import os
import sys

# Add Backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

def test_env_vars():
    """Check if Google OAuth env vars are set"""
    print("🔍 Checking environment variables...")
    
    # Load .env file
    env_path = os.path.join('Backend', '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            content = f.read()
            has_client_id = 'GOOGLE_CLIENT_ID' in content
            has_client_secret = 'GOOGLE_CLIENT_SECRET' in content
            
            if has_client_id and has_client_secret:
                print("✓ Google OAuth credentials found in .env")
                return True
            else:
                print("✗ Missing Google OAuth credentials in .env")
                return False
    else:
        print("✗ .env file not found")
        return False

def test_backend_imports():
    """Test if backend modules can be imported"""
    print("\n🔍 Testing backend imports...")
    
    try:
        from app.api import auth
        print("✓ Auth module imports successfully")
        
        # Check if Google OAuth endpoints exist
        routes = [route.path for route in auth.router.routes]
        
        if '/google/url' in routes and '/google/callback' in routes:
            print("✓ Google OAuth endpoints found:")
            print("  - GET /api/auth/google/url")
            print("  - GET /api/auth/google/callback")
            return True
        else:
            print("✗ Google OAuth endpoints not found")
            return False
            
    except Exception as e:
        print(f"✗ Failed to import auth module: {e}")
        return False

def test_frontend_integration():
    """Check if frontend has Google OAuth integration"""
    print("\n🔍 Checking frontend integration...")
    
    app_js_path = os.path.join('Frontend', 'app.js')
    if os.path.exists(app_js_path):
        with open(app_js_path) as f:
            content = f.read()
            
            has_signin_function = 'signInWithGoogle' in content
            has_callback_handler = 'google_token' in content
            
            if has_signin_function and has_callback_handler:
                print("✓ Frontend Google OAuth integration found:")
                print("  - signInWithGoogle() function")
                print("  - OAuth callback handler")
                return True
            else:
                print("✗ Frontend integration incomplete")
                return False
    else:
        print("✗ Frontend/app.js not found")
        return False

def main():
    print("=" * 60)
    print("Google OAuth Integration Test")
    print("=" * 60)
    
    results = []
    
    results.append(test_env_vars())
    results.append(test_backend_imports())
    results.append(test_frontend_integration())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! Google OAuth is ready to use.")
        print("\nNext steps:")
        print("1. Start backend: cd Backend && python -m uvicorn app.main:app --reload --port 8000")
        print("2. Open frontend: http://localhost:5500/Frontend/index.html")
        print("3. Click 'Continue with Google' to test")
    else:
        print("❌ Some tests failed. Please review the output above.")
    print("=" * 60)

if __name__ == '__main__':
    main()
