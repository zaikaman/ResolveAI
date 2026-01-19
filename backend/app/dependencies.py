"""
FastAPI dependencies for authentication and authorization.
"""

from typing import Optional
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_supabase_jwt, extract_user_id_from_token
from app.core.errors import AuthenticationError
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
    payload = verify_supabase_jwt(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise AuthenticationError(
            message="Invalid token: missing user ID",
            details={"error": "invalid_token"}
        )
    
    # Get user from database
    user = await UserRepository.get_by_id(user_id)
    
    if not user:
        raise AuthenticationError(
            message="User not found",
            details={"error": "user_not_found", "user_id": user_id}
        )
    
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
