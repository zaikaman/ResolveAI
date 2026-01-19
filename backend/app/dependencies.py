"""
FastAPI dependencies for authentication and authorization.
"""

from datetime import datetime
from typing import Optional
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_supabase_jwt, extract_user_id_from_token
from app.core.errors import AuthenticationError, ConflictError
from app.db.repositories.user_repo import UserRepository
from app.models.user import UserProfile


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserProfile:
    """
    Get current authenticated user from JWT token.
    
    This dependency validates the Supabase JWT token and returns the user profile.
    Use this for protected routes that require authentication.
    
    Args:
        credentials: HTTP Authorization header with Bearer token
    
    Returns:
        User profile
    
    Raises:
        AuthenticationError: If token is invalid or user not found
    
    Example:
        @router.get("/me")
        async def get_me(current_user: UserProfile = Depends(get_current_user)):
            return current_user
    """
    token = credentials.credentials
    
    # Verify Supabase JWT token
    try:
        payload = verify_supabase_jwt(token)
    except Exception as e:
        print(f"[AUTH] Token verification failed: {e}")
        raise e
        
    user_id = payload.get("sub")
    print(f"[AUTH] Token verified for user_id: {user_id}")
    
    if not user_id:
        print("[AUTH] User ID missing in token")
        raise AuthenticationError(
            message="Invalid token: missing user ID",
            details={"error": "invalid_token"}
        )
    
    # Get user from database (with token for RLS)
    user = await UserRepository.get_by_id(user_id, token=token)
    print(f"[AUTH] User found in DB: {user is not None}")
    
    if not user:
        # Lazy creation: User exists in Supabase Auth but not in public.users
        # Create the user record using token data
        print(f"[AUTH] Initiating lazy creation for user_id: {user_id}")
        from app.models.user import UserCreate
        
        email = payload.get("email")
        user_metadata = payload.get("user_metadata", {})
        print(f"[AUTH] User metadata: email={email}, name={user_metadata.get('full_name')}")
        print(f"[AUTH] Full payload keys: {list(payload.keys())}")
        
        if not email:
            print("[AUTH] Email missing in token payload")
            raise AuthenticationError(
                message="Token missing email",
                details={"error": "invalid_token_payload"}
            )
            
        try:
            user_data = UserCreate(
                id=user_id,
                email=email,
                full_name=user_metadata.get("full_name") or user_metadata.get("name") or email.split("@")[0],
                avatar_url=user_metadata.get("avatar_url") or user_metadata.get("picture")
            )
            
            print(f"[AUTH] Attempting to create user with data: id={user_data.id}, email={user_data.email}, name={user_data.full_name}")
            user = await UserRepository.create(user_data, token=token)
            print(f"[AUTH] Lazy creation successful for user_id: {user.id}")
        except ConflictError:
            # User might have been created concurrently
            user = await UserRepository.get_by_id(user_id, token=token)
            if not user:
                raise AuthenticationError("User creation failed: Conflict detected but user not found")
        except Exception as e:
            print(f"[AUTH] Lazy creation failed: {e}")
            raise AuthenticationError(f"Failed to create user record: {str(e)}")
    
    return user


async def get_current_user_optional(
    authorization: Optional[str] = Header(None)
) -> Optional[UserProfile]:
    """
    Get current user if authenticated, otherwise return None.
    
    Use this for routes that work both for authenticated and anonymous users.
    
    Args:
        authorization: Authorization header (optional)
    
    Returns:
        User profile or None
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        payload = verify_supabase_jwt(token)
        user_id = payload.get("sub")
        
        if user_id:
            return await UserRepository.get_by_id(user_id)
    except Exception:
        # Silent fail for optional auth
        pass
    
    return None


async def require_onboarding_complete(
    current_user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """
    Require user to have completed onboarding.
    
    Use this for routes that require full user profile setup.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User profile
    
    Raises:
        AuthenticationError: If onboarding not complete
    """
    if not current_user.onboarding_completed:
        raise AuthenticationError(
            message="Please complete onboarding first",
            details={
                "error": "onboarding_incomplete",
                "redirect": "/onboarding"
            }
        )
    
    return current_user
