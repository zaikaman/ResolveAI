"""
JWT validation and security utilities for Google OAuth with Supabase.

Aligned with Supabase Auth integration.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from ..config import settings
from .errors import AuthenticationError


# Password hashing context (for future use if adding email/password)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    result: bool = pwd_context.verify(plain_password, hashed_password)
    return result


def get_password_hash(password: str) -> str:
    """Hash a password."""
    result: str = pwd_context.hash(password)
    return result


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Payload to encode (should include 'sub' for user ID)
        expires_delta: Token expiration time (default: 15 minutes)
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token.
    
    Args:
        data: Payload to encode (should include 'sub' for user ID)
        expires_delta: Token expiration time (default: 7 days)
    
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token to decode
    
    Returns:
        Decoded token payload
    
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return dict(payload)
    except jwt.ExpiredSignatureError:
        raise AuthenticationError(
            message="Token has expired",
            details={"error": "token_expired"}
        )
    except InvalidTokenError as e:
        raise AuthenticationError(
            message="Invalid token",
            details={"error": "invalid_token", "reason": str(e)}
        )


def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """
    Verify Supabase JWT token.
    
    Supabase tokens are signed with the project's JWT secret.
    
    Args:
        token: Supabase JWT token
    
    Returns:
        Decoded token payload with user info
    
    Raises:
        AuthenticationError: If token is invalid
    """
    try:
        # Supabase uses the same JWT secret from settings
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return dict(payload)
    except jwt.ExpiredSignatureError:
        raise AuthenticationError(
            message="Session expired. Please log in again.",
            details={"error": "session_expired"}
        )
    except InvalidTokenError as e:
        raise AuthenticationError(
            message="Invalid session token",
            details={"error": "invalid_session", "reason": str(e)}
        )


def extract_user_id_from_token(token: str) -> str:
    """
    Extract user ID from JWT token.
    
    Args:
        token: JWT token
    
    Returns:
        User ID from token 'sub' claim
    
    Raises:
        AuthenticationError: If token is invalid or missing user ID
    """
    payload = decode_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise AuthenticationError(
            message="Token missing user identifier",
            details={"error": "invalid_token_payload"}
        )
    
    return str(user_id)


def validate_token_type(token: str, expected_type: str) -> None:
    """
    Validate token type (access vs refresh).
    
    Args:
        token: JWT token
        expected_type: Expected token type ("access" or "refresh")
    
    Raises:
        AuthenticationError: If token type doesn't match
    """
    payload = decode_token(token)
    token_type = payload.get("type", "access")
    
    if token_type != expected_type:
        raise AuthenticationError(
            message=f"Invalid token type. Expected {expected_type}, got {token_type}",
            details={"error": "invalid_token_type"}
        )
