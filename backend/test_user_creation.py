"""
Test script to verify user creation in the database
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_user_creation():
    """Test creating a user in the database"""
    print("=== Testing User Creation ===\n")
    
    # Initialize Supabase
    from app.services.supabase_service import init_supabase
    from app.db.repositories.user_repo import UserRepository
    from app.models.user import UserCreate
    
    try:
        print("1. Initializing Supabase client...")
        await init_supabase()
        print("   ✅ Supabase client initialized\n")
    except Exception as e:
        print(f"   ❌ Failed to initialize Supabase: {e}\n")
        return False
    
    # Test user data
    import uuid
    test_user = UserCreate(
        id=str(uuid.uuid4()),  # Use proper UUID
        email="test@example.com",
        full_name="Test User",
        avatar_url=None
    )
    
    print(f"2. Attempting to create test user...")
    print(f"   ID: {test_user.id}")
    print(f"   Email: {test_user.email}")
    print(f"   Name: {test_user.full_name}\n")
    
    try:
        user = await UserRepository.create(test_user)
        print(f"   ✅ User created successfully!")
        print(f"   Created user ID: {user.id}")
        print(f"   Created at: {user.created_at}\n")
        
        # Try to fetch the user back
        print("3. Fetching user back from database...")
        fetched_user = await UserRepository.get_by_id(user.id)
        if fetched_user:
            print(f"   ✅ User fetched successfully!")
            print(f"   Fetched user: {fetched_user.email}\n")
        else:
            print(f"   ❌ Could not fetch user back\n")
        
        return True
    except Exception as e:
        print(f"   ❌ Failed to create user: {type(e).__name__}")
        print(f"   Error: {str(e)}\n")
        import traceback
        print(f"   Traceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_user_creation())
    sys.exit(0 if success else 1)
