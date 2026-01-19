"""
Plan Pydantic models for repayment plan management.

Aligned with data-model.md schema.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class PlanStatus(str, Enum):
    """Status of a repayment plan."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class RepaymentStrategy(str, Enum):
    """Debt repayment strategies."""
    AVALANCHE = "avalanche"  # Highest interest rate first
    SNOWBALL = "snowball"    # Lowest balance first


class PlanRequest(BaseModel):
    """Request payload for generating a new plan."""
    strategy: RepaymentStrategy = RepaymentStrategy.AVALANCHE
    extra_monthly_payment: float = Field(0.0, ge=0, description="Extra amount above minimums")
    
    # Optional overrides
    start_date: Optional[date] = None
    custom_monthly_budget: Optional[float] = Field(None, gt=0)
    available_for_debt: Optional[float] = Field(None, gt=0, description="User's available monthly amount (plaintext)")


class PaymentScheduleItem(BaseModel):
    """Single payment in the schedule."""
    month: int = Field(..., ge=1, description="Month number from start")
    date: date
    debt_id: str
    debt_name: str
    payment_amount: float
    principal: float
    interest: float
    remaining_balance: float
    is_payoff_month: bool = False


class MonthlyBreakdown(BaseModel):
    """Breakdown of payments for a single month."""
    month: int
    date: date
    total_payment: float
    payments: list[PaymentScheduleItem]
    total_remaining: float


class PlanProjection(BaseModel):
    """Projection data for charts."""
    month: int
    date: date
    total_remaining: float
    cumulative_interest_paid: float
    cumulative_principal_paid: float


class DebtPayoffInfo(BaseModel):
    """Information about when each debt gets paid off."""
    debt_id: str
    debt_name: str
    payoff_month: int
    payoff_date: date
    total_interest_paid: float
    total_paid: float


class PlanResponse(BaseModel):
    """Complete repayment plan response."""
    id: str
    user_id: str
    status: PlanStatus
    strategy: RepaymentStrategy
    
    # Key metrics
    debt_free_date: date
    total_months: int
    total_interest: float
    total_paid: float
    
    # Comparison with minimum-only approach
    interest_saved: float
    months_saved: int
    
    # Monthly budget
    monthly_payment: float
    extra_payment: float
    
    # Detailed breakdown
    monthly_schedule: list[MonthlyBreakdown]
    projections: list[PlanProjection]
    payoff_order: list[DebtPayoffInfo]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PlanRecalculationRequest(BaseModel):
    """Request to recalculate an existing plan."""
    plan_id: str
    
    # What changed
    strategy: Optional[RepaymentStrategy] = None
    extra_monthly_payment: Optional[float] = Field(None, ge=0)
    custom_monthly_budget: Optional[float] = Field(None, gt=0)
    available_for_debt: Optional[float] = Field(None, gt=0, description="User's available monthly amount (plaintext)")
    
    # Reason for recalculation
    reason: Optional[str] = None


class PlanSimulationRequest(BaseModel):
    """Request for what-if simulation without saving."""
    # Scenario parameters
    strategy: RepaymentStrategy = RepaymentStrategy.AVALANCHE
    extra_monthly_payment: float = Field(0.0, ge=0)
    available_for_debt: Optional[float] = Field(None, gt=0, description="User's available monthly amount (plaintext)")
    
    # Income change simulation
    income_change: Optional[float] = None  # Positive or negative
    
    # One-time extra payment
    lump_sum_payment: Optional[float] = Field(None, ge=0)
    lump_sum_target_debt_id: Optional[str] = None
    
    # Interest rate reduction simulation
    rate_reduction: Optional[dict[str, float]] = None  # debt_id -> new APR


class PlanSimulationResponse(BaseModel):
    """Response for what-if simulation."""
    # Original plan metrics
    original_debt_free_date: date
    original_total_interest: float
    original_total_months: int
    
    # Simulated plan metrics
    simulated_debt_free_date: date
    simulated_total_interest: float
    simulated_total_months: int
    
    # Comparison
    interest_difference: float
    months_difference: int
    
    # Simulated projections for chart
    projections: list[PlanProjection]


class PlanSummaryResponse(BaseModel):
    """Lightweight plan summary for dashboard."""
    id: str
    strategy: RepaymentStrategy
    debt_free_date: date
    total_months: int
    months_remaining: int
    progress_percentage: float
    monthly_payment: float
    next_payment_date: Optional[date] = None
