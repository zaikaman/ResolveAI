"""
Payments router for payment logging and tracking.
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentListResponse,
    PaymentStats,
    RecentPaymentSummary
)
from app.services.payment_service import PaymentService
from app.dependencies import get_current_user
from app.models.user import UserResponse
from app.agents.habit_agent import MilestoneCheckResult
from app.core.errors import NotFoundError, ValidationError

security = HTTPBearer()

router = APIRouter(prefix="/payments", tags=["payments"])


class PaymentWithMilestones(PaymentResponse):
    """Payment response with optional milestone data."""
    milestones: Optional[MilestoneCheckResult] = None


@router.post("", response_model=PaymentWithMilestones, status_code=status.HTTP_201_CREATED)
async def log_payment(
    payment_data: PaymentCreate,
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> PaymentWithMilestones:
    """
    Log a new payment.
    
    This will:
    1. Create a payment record
    2. Update the debt balance
    3. Check for milestones and return any celebrations
    
    Args:
        payment_data: Payment details
        current_user: Authenticated user
    
    Returns:
        Created payment with any milestone celebrations
    
    Raises:
        404: If debt not found
        400: If payment amount exceeds balance
    """
    try:
        payment, milestones = await PaymentService.log_payment(
            user_id=current_user.id,
            payment_data=payment_data,
            token=credentials.credentials
        )
        
        # Build response with milestones
        response_data = payment.model_dump()
        response_data["milestones"] = milestones
        
        return PaymentWithMilestones(**response_data)
    
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=PaymentListResponse)
async def get_payments(
    debt_id: Optional[str] = Query(None, description="Filter by debt ID"),
    limit: Optional[int] = Query(50, ge=1, le=200, description="Maximum payments to return"),
    start_date: Optional[date] = Query(None, description="Filter by payment_date >= start_date"),
    end_date: Optional[date] = Query(None, description="Filter by payment_date <= end_date"),
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> PaymentListResponse:
    """
    Get payments for the current user.
    
    Args:
        debt_id: Optional filter by specific debt
        limit: Maximum number of payments to return
        start_date: Filter by payment date start
        end_date: Filter by payment date end
        current_user: Authenticated user
    
    Returns:
        List of payments with totals
    """
    return await PaymentService.get_payments(
        user_id=current_user.id,
        debt_id=debt_id,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        token=credentials.credentials
    )


@router.get("/recent", response_model=List[PaymentResponse])
async def get_recent_payments(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50, description="Maximum payments to return"),
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> List[PaymentResponse]:
    """
    Get recent payments within the last N days.
    
    Args:
        days: Number of days to look back
        limit: Maximum payments to return
        current_user: Authenticated user
    
    Returns:
        List of recent payments
    """
    return await PaymentService.get_recent_payments(
        user_id=current_user.id,
        days=days,
        limit=limit,
        token=credentials.credentials
    )


@router.get("/stats", response_model=PaymentStats)
async def get_payment_stats(
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> PaymentStats:
    """
    Get payment statistics for the current user.
    
    Includes totals, streaks, averages, and time-based breakdowns.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        PaymentStats with aggregated data
    """
    return await PaymentService.get_payment_stats(
        user_id=current_user.id,
        token=credentials.credentials
    )


@router.get("/summary", response_model=RecentPaymentSummary)
async def get_payment_summary(
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> RecentPaymentSummary:
    """
    Get a summary of recent payment activity for the dashboard.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        RecentPaymentSummary with key metrics
    """
    return await PaymentService.get_recent_summary(
        user_id=current_user.id,
        token=credentials.credentials
    )


@router.get("/milestones", response_model=MilestoneCheckResult)
async def check_milestones(
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> MilestoneCheckResult:
    """
    Check for any new milestones achieved by the user.
    
    Args:
        current_user: Authenticated user
    
    Returns:
        MilestoneCheckResult with any achieved milestones
    """
    return await PaymentService.check_milestones(
        user_id=current_user.id,
        token=credentials.credentials
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> PaymentResponse:
    """
    Get a specific payment by ID.
    
    Args:
        payment_id: Payment UUID
        current_user: Authenticated user
    
    Returns:
        Payment details
    
    Raises:
        404: If payment not found
    """
    payment = await PaymentService.get_payment(
        payment_id=payment_id,
        user_id=current_user.id,
        token=credentials.credentials
    )
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.patch("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: str,
    update_data: PaymentUpdate,
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> PaymentResponse:
    """
    Update a payment record.
    
    Args:
        payment_id: Payment UUID
        update_data: Fields to update
        current_user: Authenticated user
    
    Returns:
        Updated payment
    
    Raises:
        404: If payment not found
    """
    payment = await PaymentService.update_payment(
        payment_id=payment_id,
        user_id=current_user.id,
        update_data=update_data,
        token=credentials.credentials
    )
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: str,
    current_user: UserResponse = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> None:
    """
    Delete a payment record.
    
    This will also revert the debt balance change.
    
    Args:
        payment_id: Payment UUID
        current_user: Authenticated user
    
    Raises:
        404: If payment not found
    """
    try:
        await PaymentService.delete_payment(
            payment_id=payment_id,
            user_id=current_user.id,
            token=credentials.credentials
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
