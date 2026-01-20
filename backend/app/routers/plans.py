"""
Plans router for repayment plan operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.plan import (
    PlanRequest,
    PlanResponse,
    PlanSummaryResponse,
    PlanRecalculationRequest,
    PlanSimulationRequest,
    PlanSimulationResponse
)
from app.models.job import JobResponse, JobType
from app.services.plan_service import PlanService
from app.services.job_service import job_service
from app.services.encryption_service import encryption_service
from app.dependencies import get_current_user
from app.models.user import UserResponse
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.debt_repo import DebtRepository
from app.db.repositories.payment_repo import PaymentRepository
from app.agents.action_agent import action_agent, DailyActionsResponse
from app.core.errors import NotFoundError, ValidationError
from datetime import date

security = HTTPBearer()

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/active", response_model=PlanResponse)
async def get_active_plan(
    current_user: UserResponse = Depends(get_current_user)
) -> PlanResponse:
    """
    Get the active repayment plan for the current user.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        Active plan
    
    Raises:
        404: If no active plan exists
    """
    plan = await PlanService.get_active_plan(current_user.id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active plan found"
        )
    return plan


@router.get("/summary", response_model=PlanSummaryResponse)
async def get_plan_summary(
    current_user: UserResponse = Depends(get_current_user)
) -> PlanSummaryResponse:
    """
    Get a lightweight summary of the active plan (for dashboard).
    
    Args:
        current_user: Authenticated user
    
    Returns:
        Plan summary
    
    Raises:
        404: If no active plan exists
    """
    summary = await PlanService.get_plan_summary(current_user.id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active plan found"
        )
    return summary


@router.post("/generate", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_plan(
    request: PlanRequest,
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> JobResponse:
    """
    Generate a new repayment plan (async).
    
    This creates a background job to generate the plan. Poll the returned
    job_id at /api/jobs/{job_id} to check status and get the result.
    
    Args:
        request: Plan generation parameters
        current_user: Authenticated user
    
    Returns:
        Job ID to poll for results
    
    Raises:
        400: If no debts to plan for or validation fails
    """
    try:
        # Get available_for_debt from request or decrypt from user profile
        if request.available_for_debt:
            available = request.available_for_debt
        elif request.custom_monthly_budget:
            available = request.custom_monthly_budget
        else:
            # Get from user profile (server-encrypted)
            token = credentials.credentials
            user_profile = await UserRepository.get_by_id(current_user.id, token=token)
            if not user_profile or not user_profile.available_for_debt_encrypted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User has not completed onboarding with financial data"
                )
            # Decrypt server-encrypted value
            available = float(encryption_service.decrypt_server_only(user_profile.available_for_debt_encrypted))
        
        token = credentials.credentials
        
        # Create background job
        job = await job_service.create_job(
            user_id=current_user.id,
            job_type=JobType.PLAN_GENERATION,
            input_data={
                "strategy": request.strategy.value if hasattr(request.strategy, 'value') else str(request.strategy),
                "extra_monthly_payment": request.extra_monthly_payment,
                "start_date": request.start_date.isoformat() if request.start_date else date.today().isoformat(),
                "custom_monthly_budget": request.custom_monthly_budget,
                "available_for_debt": available,
                "token": token
            }
        )
        
        return job
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.post("/recalculate", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def recalculate_plan(
    request: PlanRecalculationRequest,
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> JobResponse:
    """
    Recalculate an existing plan with updated parameters (async).
    
    Creates a background job to recalculate the plan. Poll the returned
    job_id at /api/jobs/{job_id} to check status and get the result.
    
    Args:
        request: Recalculation parameters
        current_user: Authenticated user
    
    Returns:
        Job ID to poll for results
    
    Raises:
        404: If referenced plan not found
        400: If validation fails
    """
    try:
        # Get available_for_debt from request or user profile
        available = request.available_for_debt
        if not available:
            token = credentials.credentials
            user_profile = await UserRepository.get_by_id(current_user.id, token=token)
            if user_profile and user_profile.available_for_debt_encrypted:
                available = float(encryption_service.decrypt_server_only(user_profile.available_for_debt_encrypted))
        
        # Create background job
        job = await job_service.create_job(
            user_id=current_user.id,
            job_type=JobType.PLAN_RECALCULATION,
            input_data={
                "plan_id": request.plan_id,
                "strategy": request.strategy.value if request.strategy and hasattr(request.strategy, 'value') else None,
                "extra_monthly_payment": request.extra_monthly_payment,
                "available_for_debt": available,
                "token": credentials.credentials
            }
        )
        
        return job
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {request.plan_id} not found"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.post("/simulate", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def simulate_scenario(
    request: PlanSimulationRequest,
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> JobResponse:
    """
    Simulate a what-if scenario without saving (async).
    
    Creates a background job to simulate different strategies or see the impact
    of income changes, lump sum payments, or rate reductions.
    
    Args:
        request: Simulation parameters
        current_user: Authenticated user
    
    Returns:
        Job ID to poll for results
    
    Raises:
        400: If no active plan to compare against
    """
    try:
        # Get available_for_debt from request or user profile
        available = request.available_for_debt
        if not available:
            token = credentials.credentials
            user_profile = await UserRepository.get_by_id(current_user.id, token=token)
            if not user_profile or not user_profile.available_for_debt_encrypted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User has not completed onboarding with financial data"
                )
            available = float(encryption_service.decrypt_server_only(user_profile.available_for_debt_encrypted))
        
        # Create background job
        job = await job_service.create_job(
            user_id=current_user.id,
            job_type=JobType.PLAN_SIMULATION,
            input_data={
                "strategy": request.strategy.value if request.strategy and hasattr(request.strategy, 'value') else "avalanche",
                "extra_monthly_payment": request.extra_monthly_payment,
                "income_change": request.income_change,
                "lump_sum_payment": request.lump_sum_payment,
                "lump_sum_target_debt_id": request.lump_sum_target_debt_id,
                "rate_reduction": request.rate_reduction,
                "available_for_debt": available,
                "token": credentials.credentials
            }
        )
        
        return job
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.post("/{plan_id}/complete", response_model=PlanResponse)
async def complete_plan(
    plan_id: str,
    current_user: UserResponse = Depends(get_current_user)
) -> PlanResponse:
    """
    Mark a plan as completed.
    
    Args:
        plan_id: Plan UUID
        current_user: Authenticated user
    
    Returns:
        Updated plan
    
    Raises:
        404: If plan not found
    """
    try:
        return await PlanService.complete_plan(current_user.id, plan_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} not found"
        )


@router.get("/actions/daily", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def get_daily_actions(
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> JobResponse:
    """
    Get recommended daily actions based on the user's plan (async).
    
    Creates a background job to generate personalized actions. Poll the returned
    job_id at /api/jobs/{job_id} to check status and get the result.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        Job ID to poll for results
    """
    token = credentials.credentials
    
    # Create background job
    job = await job_service.create_job(
        user_id=current_user.id,
        job_type=JobType.DAILY_ACTIONS,
        input_data={
            "token": token
        }
    )
    
    return job
