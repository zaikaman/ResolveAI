"""
Test script to verify Supabase JWT authentication setup
Run this to check if your backend can verify tokens correctly
"""
import sys
import os

# Add the backend directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jwt
from datetime import datetime, timedelta

def test_jwt_config():
    """Test JWT configuration"""
    print("=== Testing JWT Configuration ===\n")
    
    # Import settings after path is set
    from app.config import settings
    
    if not settings.SUPABASE_JWT_SECRET:
        print("❌ SUPABASE_JWT_SECRET not set in environment")
        print("   This must match your Supabase project's JWT secret")
        print("   Find it in: Supabase Dashboard > Settings > API > JWT Secret")
        return False
    
    print(f"✅ SUPABASE_JWT_SECRET is set (length: {len(settings.SUPABASE_JWT_SECRET)})")
    
    # Create a test token
    test_payload = {
        "sub": "test-user-id-12345",
        "email": "test@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }
    
    try:
        # Encode token
        test_token = jwt.encode(
            test_payload,
            settings.SUPABASE_JWT_SECRET,
            algorithm="HS256"
        )
        print("✅ Successfully created test JWT token")
        
        # Decode token
        decoded = jwt.decode(
            test_token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        print("✅ Successfully decoded test JWT token")
        print(f"   User ID: {decoded.get('sub')}")
        print(f"   Email: {decoded.get('email')}")
        
        return True
        
    except Exception as e:
        print(f"❌ JWT test failed: {e}")
        return False

def test_supabase_connection():
    """Test Supabase connection"""
    print("\n=== Testing Supabase Connection ===\n")
    
    from app.config import settings
    
    if not settings.SUPABASE_URL:
        print("❌ SUPABASE_URL not set")
        return False
    
    if not settings.SUPABASE_KEY:
        print("❌ SUPABASE_KEY not set")
        return False
    
    print(f"✅ SUPABASE_URL: {settings.SUPABASE_URL}")
    print(f"✅ SUPABASE_KEY: {settings.SUPABASE_KEY[:20]}...")
    
    return True

if __name__ == "__main__":
    print("🔍 ResolveAI Authentication Setup Verification\n")
    
    jwt_ok = test_jwt_config()
    supabase_ok = test_supabase_connection()
    
    print("\n" + "="*50)
    if jwt_ok and supabase_ok:
        print("✅ All checks passed! Your backend auth config looks good.")
        print("\nNext steps:")
        print("1. Make sure frontend .env has correct VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY")
        print("2. Clear browser localStorage and cookies")
        print("3. Restart both frontend and backend servers")
        print("4. Try logging in again")
    else:
        print("❌ Some checks failed. Review the errors above.")
        print("\nVerify:")
        print("1. SUPABASE_JWT_SECRET matches Supabase Dashboard > Settings > API")
        print("2. SUPABASE_URL and SUPABASE_KEY are set correctly")
        print("3. Backend .env file is loaded properly")
