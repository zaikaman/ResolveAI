"""
Health check router for monitoring and readiness probes.
"""

from fastapi import APIRouter, status
from datetime import datetime
from typing import Any
from app.services.supabase_service import SupabaseService
from app.config import settings


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns service status and timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "resolveai-debt-coach",
        "version": "0.1.0"
    }


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check() -> dict[str, Any]:
    """
    Readiness check endpoint for Kubernetes/container orchestration.
    
    Checks:
    - Database connectivity (Supabase)
    - Configuration validity
    
    Returns:
        Status and dependency health
    """
    checks = {
        "database": "unknown",
        "config": "unknown"
    }
    
    # Check database connectivity
    try:
        # Simple query to verify connection
        result = await SupabaseService.select("users", limit=1)
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # Check configuration
    try:
        required_settings = [
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
            settings.OPENAI_API_KEY,
            settings.JWT_SECRET_KEY
        ]
        if all(required_settings):
            checks["config"] = "healthy"
        else:
            checks["config"] = "unhealthy: missing required settings"
    except Exception as e:
        checks["config"] = f"unhealthy: {str(e)}"
    
    # Overall status
    is_ready = all(v == "healthy" for v in checks.values())
    
    return {
        "ready": is_ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/liveness", status_code=status.HTTP_200_OK)
async def liveness_check() -> dict[str, Any]:
    """
    Liveness check endpoint for Kubernetes health probes.
    
    Simple check that the service is responsive.
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
