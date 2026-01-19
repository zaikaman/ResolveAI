"""
Custom error classes for structured error handling.

Aligned with CQ-003 constitution requirement for typed errors.
"""

from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class AppError(Exception):
    """Base error class for all application errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to API response format."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


class UserError(AppError):
    """
    User-facing errors (invalid input, business rule violations).
    
    Status codes: 400-499
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "USER_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        super().__init__(message, error_code, details, status_code)


class AuthenticationError(UserError):
    """Authentication failures (invalid token, expired session)."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(UserError):
    """Authorization failures (insufficient permissions)."""
    
    def __init__(
        self,
        message: str = "Access denied",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundError(UserError):
    """Resource not found errors."""
    
    def __init__(
        self,
        resource: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"{resource} not found: {resource_id}",
            error_code="NOT_FOUND",
            details=details or {"resource": resource, "id": resource_id},
            status_code=status.HTTP_404_NOT_FOUND
        )


class ValidationError(UserError):
    """Input validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=error_details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class ConflictError(UserError):
    """Resource conflict errors (duplicate email, etc.)."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            details=details,
            status_code=status.HTTP_409_CONFLICT
        )


class SystemError(AppError):
    """
    Internal system errors (database failures, service unavailable).
    
    Status codes: 500-599
    """
    
    def __init__(
        self,
        message: str = "Internal server error",
        error_code: str = "SYSTEM_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        super().__init__(message, error_code, details, status_code)


class DatabaseError(SystemError):
    """Database operation failures."""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=error_details
        )


class ExternalError(AppError):
    """
    External service errors (OpenAI API, Supabase, Opik).
    
    Status codes: 502-504
    """
    
    def __init__(
        self,
        service: str,
        message: str,
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_502_BAD_GATEWAY
    ):
        error_details = details or {}
        error_details["service"] = service
        
        super().__init__(message, error_code, error_details, status_code)


class OpenAIError(ExternalError):
    """OpenAI API failures."""
    
    def __init__(
        self,
        message: str = "OpenAI API request failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            service="OpenAI",
            message=message,
            error_code="OPENAI_ERROR",
            details=details
        )


class SupabaseError(ExternalError):
    """Supabase API failures."""
    
    def __init__(
        self,
        message: str = "Supabase operation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            service="Supabase",
            message=message,
            error_code="SUPABASE_ERROR",
            details=details
        )


class OpikError(ExternalError):
    """Opik tracing failures (non-critical)."""
    
    def __init__(
        self,
        message: str = "Opik tracing failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            service="Opik",
            message=message,
            error_code="OPIK_ERROR",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def app_error_to_http_exception(error: AppError) -> HTTPException:
    """Convert AppError to FastAPI HTTPException."""
    return HTTPException(
        status_code=error.status_code,
        detail=error.to_dict()
    )


# Alias for backward compatibility or cleaner imports
ExternalServiceError = ExternalError
