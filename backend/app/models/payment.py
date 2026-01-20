"""
Payment Pydantic models for payment tracking.

Aligned with data-model.md schema.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class PaymentMethod(str, Enum):
    """Payment methods supported."""
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    CASH = "cash"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    AUTO_PAY = "auto_pay"
    OTHER = "other"


class PaymentCreate(BaseModel):
    """Payload for logging a new payment."""
    debt_id: str = Field(..., description="UUID of the debt being paid")
    amount: float = Field(..., gt=0, description="Payment amount")
    payment_date: Optional[date] = Field(None, description="Date of payment (defaults to today)")
    payment_method: Optional[PaymentMethod] = Field(None, description="How the payment was made")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")
    
    # New balance after payment (optional - can be calculated)
    new_balance: Optional[float] = Field(None, ge=0, description="Updated balance after payment")


class PaymentUpdate(BaseModel):
    """Payload for updating an existing payment."""
    amount: Optional[float] = Field(None, gt=0)
    payment_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = Field(None, max_length=500)
    confirmed: Optional[bool] = None


class PaymentResponse(BaseModel):
    """Payment data returned to frontend."""
    id: str
    user_id: str
    debt_id: str
    plan_id: Optional[str] = None
    
    # Payment details
    amount: float
    payment_date: date
    payment_method: Optional[str] = None
    confirmed: bool = True
    
    # Impact
    new_balance: float
    interest_saved: Optional[float] = None
    
    # Metadata
    notes: Optional[str] = None
    created_at: datetime
    
    # Related debt info (populated when joined)
    debt_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    """List of payments with summary."""
    payments: List[PaymentResponse]
    total_count: int
    total_amount: float


class PaymentStats(BaseModel):
    """Statistics for user's payment history."""
    # Totals
    total_payments: int = 0
    total_amount_paid: float = 0.0
    total_interest_saved: float = 0.0
    
    # Time-based stats
    payments_this_month: int = 0
    amount_this_month: float = 0.0
    payments_last_30_days: int = 0
    amount_last_30_days: float = 0.0
    
    # Streaks and consistency
    current_streak_days: int = 0
    longest_streak_days: int = 0
    on_track_percentage: float = 0.0  # % of scheduled payments made on time
    
    # Average
    average_payment_amount: float = 0.0
    
    # By debt breakdown
    payments_by_debt: Optional[dict[str, int]] = None


class RecentPaymentSummary(BaseModel):
    """Summary of recent payment activity for dashboard."""
    last_payment_date: Optional[date] = None
    last_payment_amount: Optional[float] = None
    last_payment_debt_name: Optional[str] = None
    
    # This week
    payments_this_week: int = 0
    amount_this_week: float = 0.0
    
    # Progress
    total_principal_paid: float = 0.0
    total_interest_paid: float = 0.0
    
    # Streaks
    current_streak: int = 0
    is_on_streak: bool = False
