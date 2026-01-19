"""
Authentication router for Google OAuth with Supabase.

Handles user authentication flow with Supabase Auth.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any
from app.models.user import UserResponse, OnboardingComplete, UserUpdate
from app.db.repositories.user_repo import UserRepository
from app.dependencies import get_current_user, require_onboarding_complete
from app.models.user import UserProfile
from app.core.errors import app_error_to_http_exception, AppError


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserProfile = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user profile.
    
    Returns:
        Current user information
    """
    try:
        # Update last login timestamp
        await UserRepository.update_last_login(current_user.id)
        
        return UserResponse(**current_user.model_dump())
    except AppError as e:
        raise app_error_to_http_exception(e)


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: UserProfile = Depends(get_current_user)
) -> UserResponse:
    """
    Update current user profile.
    
    Args:
        update_data: Fields to update
    
    Returns:
        Updated user profile
    """
    try:
        updated_user = await UserRepository.update(current_user.id, update_data)
        return UserResponse(**updated_user.model_dump())
    except AppError as e:
        raise app_error_to_http_exception(e)


@router.post("/onboarding/complete", response_model=UserResponse)
async def complete_onboarding(
    onboarding_data: OnboardingComplete,
    current_user: UserProfile = Depends(get_current_user)
) -> UserResponse:
    """
    Complete user onboarding with initial financial data.
    
    Args:
        onboarding_data: Encrypted financial data and terms acceptance
    
    Returns:
        Updated user profile with onboarding_completed = true
    """
    try:
        updated_user = await UserRepository.complete_onboarding(
            user_id=current_user.id,
            monthly_income_encrypted=onboarding_data.monthly_income_encrypted,
            monthly_expenses_encrypted=onboarding_data.monthly_expenses_encrypted,
            available_for_debt_encrypted=onboarding_data.available_for_debt_encrypted
        )
        
        return UserResponse(**updated_user.model_dump())
    except AppError as e:
        raise app_error_to_http_exception(e)


@router.get("/onboarding/status")
async def get_onboarding_status(
    current_user: UserProfile = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Check if user has completed onboarding.
    
    Returns:
        Onboarding completion status
    """
    return {
        "completed": current_user.onboarding_completed,
        "has_financial_data": bool(current_user.monthly_income_encrypted)
    }


@router.delete("/me")
async def delete_account(
    current_user: UserProfile = Depends(get_current_user)
) -> dict[str, str]:
    """
    Delete user account.
    
    Returns:
        Success message
    """
    try:
        await UserRepository.delete(current_user.id)
        return {"message": "Account deleted successfully"}
    except AppError as e:
        raise app_error_to_http_exception(e)
