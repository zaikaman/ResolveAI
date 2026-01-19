"""
Plans router for repayment plan operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.plan import (
    PlanRequest,
    PlanResponse,
    PlanSummaryResponse,
    PlanRecalculationRequest,
    PlanSimulationRequest,
    PlanSimulationResponse
)
from app.services.plan_service import PlanService
from app.services.encryption_service import EncryptionService
from app.dependencies import get_current_user
from app.models.user import UserResponse
from app.db.repositories.user_repo import UserRepository
from app.core.errors import NotFoundError, ValidationError

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
    current_user: UserResponse = Depends(get_current_user)
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
        # Get user's available for debt amount
        user_profile = await UserRepository.get_by_id(current_user.id)
        if not user_profile or not user_profile.available_for_debt_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has not completed onboarding with financial data"
            )
        
        available = float(EncryptionService.decrypt(user_profile.available_for_debt_encrypted))
        
        return await PlanService.generate_plan(current_user.id, request, available)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.post("/recalculate", response_model=PlanResponse)
async def recalculate_plan(
    request: PlanRecalculationRequest,
    current_user: UserResponse = Depends(get_current_user)
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
        # Get user's available for debt amount
        user_profile = await UserRepository.get_by_id(current_user.id)
        available = None
        if user_profile and user_profile.available_for_debt_encrypted:
            available = float(EncryptionService.decrypt(user_profile.available_for_debt_encrypted))
        
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
    current_user: UserResponse = Depends(get_current_user)
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
        # Get user's available for debt amount
        user_profile = await UserRepository.get_by_id(current_user.id)
        if not user_profile or not user_profile.available_for_debt_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has not completed onboarding with financial data"
            )
        
        available = float(EncryptionService.decrypt(user_profile.available_for_debt_encrypted))
        
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
