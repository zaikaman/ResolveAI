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
from app.services.plan_service import PlanService
from app.services.encryption_service import encryption_service
from app.dependencies import get_current_user
from app.models.user import UserResponse
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.debt_repo import DebtRepository
from app.db.repositories.payment_repo import PaymentRepository
from app.agents.action_agent import action_agent, DailyActionsResponse
from app.core.errors import NotFoundError, ValidationError

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


@router.post("/generate", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def generate_plan(
    request: PlanRequest,
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> PlanResponse:
    """
    Generate a new repayment plan.
    
    This will archive any existing active plans and create a new one
    based on the user's current debts and financial situation.
    
    Args:
        request: Plan generation parameters
        current_user: Authenticated user
    
    Returns:
        Generated plan
    
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
        return await PlanService.generate_plan(current_user.id, request, available, token=token)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.post("/recalculate", response_model=PlanResponse)
async def recalculate_plan(
    request: PlanRecalculationRequest,
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> PlanResponse:
    """
    Recalculate an existing plan with updated parameters.
    
    Args:
        request: Recalculation parameters
        current_user: Authenticated user
    
    Returns:
        New recalculated plan
    
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
        
        return await PlanService.recalculate_plan(
            user_id=current_user.id,
            plan_id=request.plan_id,
            strategy=request.strategy,
            extra_payment=request.extra_monthly_payment,
            available_for_debt=available
        )
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


@router.post("/simulate", response_model=PlanSimulationResponse)
async def simulate_scenario(
    request: PlanSimulationRequest,
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> PlanSimulationResponse:
    """
    Simulate a what-if scenario without saving.
    
    Useful for exploring different strategies or seeing the impact
    of income changes, lump sum payments, or rate reductions.
    
    Args:
        request: Simulation parameters
        current_user: Authenticated user
    
    Returns:
        Simulation results with comparison to current plan
    
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
        
        return await PlanService.simulate_scenario(current_user.id, request, available)
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


@router.get("/actions/daily", response_model=DailyActionsResponse)
async def get_daily_actions(
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> DailyActionsResponse:
    """
    Get recommended daily actions based on the user's plan.
    
    Returns personalized actions including:
    - Scheduled payments for this month
    - Review reminders
    - Milestone celebrations
    
    Args:
        current_user: Authenticated user
    
    Returns:
        DailyActionsResponse with prioritized actions
    """
    token = credentials.credentials
    
    # Get active plan
    active_plan = await PlanService.get_active_plan(current_user.id)
    
    # Get active debts
    debts_response = await DebtRepository.get_all_by_user(current_user.id)
    debts = debts_response.debts
    
    # Get payment stats for streak info
    payment_stats = await PaymentRepository.get_stats(current_user.id, token=token)
    
    # Get last payment date
    recent_payments = await PaymentRepository.get_recent(current_user.id, days=30, limit=1, token=token)
    last_payment_date = recent_payments[0].payment_date if recent_payments else None
    
    # Generate daily actions
    return await action_agent.generate_daily_actions(
        plan=active_plan,
        debts=debts,
        current_streak=payment_stats.current_streak_days,
        last_payment_date=last_payment_date,
        payments_this_month=payment_stats.payments_this_month
    )
