"""
FastAPI application entry point for ResolveAI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Create FastAPI app
app = FastAPI(
    title="ResolveAI Debt Freedom Coach API",
    description="AI-powered debt management and repayment planning",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ResolveAI Debt Freedom Coach API",
        "version": "0.1.0",
        "status": "operational"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# Import and register routers (will be added in Phase 2)
# from app.routers import auth, debts, plans, payments
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(debts.router, prefix="/api/debts", tags=["debts"])
# app.include_router(plans.router, prefix="/api/plans", tags=["plans"])
# app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
