"""
User Pydantic models for authentication and profile management.

Aligned with data-model.md schema and Google OAuth flow.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum


class RepaymentStrategy(str, Enum):
    """Debt repayment strategies."""
    AVALANCHE = "avalanche"  # Highest interest rate first
    SNOWBALL = "snowball"    # Lowest balance first


class NotificationFrequency(str, Enum):
    """Notification frequency options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class UserCreate(BaseModel):
    """User creation payload (Google OAuth profile)."""
    email: EmailStr
    id: Optional[str] = None  # Supabase Auth User ID
    full_name: Optional[str] = None
    google_id: Optional[str] = None  # Google OAuth sub claim
    avatar_url: Optional[str] = None  # Google profile picture


class UserUpdate(BaseModel):
    """User profile update payload."""
    full_name: Optional[str] = None
    timezone: Optional[str] = Field(default="America/New_York", pattern=r"^[A-Za-z_]+/[A-Za-z_]+$")
    language: Optional[str] = Field(default="en", pattern=r"^[a-z]{2}$")
    
    # Financial context (encrypted by client before sending)
    monthly_income_encrypted: Optional[str] = None
    monthly_expenses_encrypted: Optional[str] = None
    available_for_debt_encrypted: Optional[str] = None
    
    # Preferences
    repayment_strategy: Optional[RepaymentStrategy] = RepaymentStrategy.AVALANCHE
    notification_enabled: Optional[bool] = True
    notification_time: Optional[str] = Field(default="09:00:00", pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$")
    notification_frequency: Optional[NotificationFrequency] = NotificationFrequency.DAILY


class UserProfile(BaseModel):
    """Complete user profile (internal use)."""
    id: str
    email: str
    created_at: datetime
    updated_at: datetime
    
    # Profile
    full_name: Optional[str] = None
    timezone: str = "America/New_York"
    language: str = "en"
    avatar_url: Optional[str] = None
    
    # Financial context (encrypted)
    monthly_income_encrypted: Optional[str] = None
    monthly_expenses_encrypted: Optional[str] = None
    available_for_debt_encrypted: Optional[str] = None
    
    # Preferences
    repayment_strategy: RepaymentStrategy = RepaymentStrategy.AVALANCHE
    notification_enabled: bool = True
    notification_time: str = "09:00:00"
    notification_frequency: NotificationFrequency = NotificationFrequency.DAILY
    
    # Metadata
    last_login_at: Optional[datetime] = None
    onboarding_completed: bool = False
    terms_accepted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User data returned to frontend (excludes sensitive fields)."""
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str = "America/New_York"
    language: str = "en"
    repayment_strategy: RepaymentStrategy = RepaymentStrategy.AVALANCHE
    notification_enabled: bool = True
    notification_frequency: NotificationFrequency = NotificationFrequency.DAILY
    onboarding_completed: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class OnboardingComplete(BaseModel):
    """Mark onboarding as complete with initial financial data."""
    monthly_income_encrypted: str = Field(..., min_length=1)
    monthly_expenses_encrypted: str = Field(..., min_length=1)
    available_for_debt_encrypted: str = Field(..., min_length=1)
    terms_accepted: bool = True
    
    @field_validator("terms_accepted")
    @classmethod
    def validate_terms(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Must accept terms and conditions")
        return v
