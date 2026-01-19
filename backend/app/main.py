"""
FastAPI application entry point for ResolveAI
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.core.errors import AppError

# Create FastAPI app
app = FastAPI(
    title="ResolveAI Debt Freedom Coach API",
    description="AI-powered debt management and repayment planning",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS
cors_origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for AppError
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle custom AppError exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    if settings.DEBUG:
        # In debug mode, show full error
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        # In production, hide error details
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "message": "ResolveAI Debt Freedom Coach API",
        "version": "0.1.0",
        "status": "operational"
    }


# Import and register routers
from app.routers import auth, health

app.include_router(auth.router, prefix="/api")
app.include_router(health.router, prefix="/api")

# Additional routers will be added in later phases
# from app.routers import debts, plans, payments
# app.include_router(debts.router, prefix="/api")
# app.include_router(plans.router, prefix="/api")
# app.include_router(payments.router, prefix="/api")
