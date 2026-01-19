"""
Debt Pydantic models for debt management.

Aligned with data-model.md schema.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from decimal import Decimal


class DebtType(str, Enum):
    """Types of debt supported by the system."""
    CREDIT_CARD = "credit_card"
    PERSONAL_LOAN = "personal_loan"
    STUDENT_LOAN = "student_loan"
    MORTGAGE = "mortgage"
    AUTO_LOAN = "auto_loan"
    MEDICAL = "medical_bill"
    OTHER = "other"


class DebtCreate(BaseModel):
    """Payload for creating a new debt."""
    creditor_name: str = Field(..., min_length=1, max_length=100)
    debt_type: DebtType = DebtType.OTHER
    
    # Encrypted financial fields (encrypted by client before sending)
    balance_encrypted: str = Field(..., min_length=1, description="AES-256-GCM encrypted balance")
    apr_encrypted: str = Field(..., min_length=1, description="AES-256-GCM encrypted APR")
    minimum_payment_encrypted: str = Field(..., min_length=1, description="AES-256-GCM encrypted minimum payment")
    
    # Optional metadata
    account_number_last4: Optional[str] = Field(None, pattern=r"^\d{4}$")
    due_date: Optional[int] = Field(None, ge=1, le=31, description="Day of month payment is due")
    notes: Optional[str] = Field(None, max_length=500)


class DebtUpdate(BaseModel):
    """Payload for updating an existing debt."""
    creditor_name: Optional[str] = Field(None, min_length=1, max_length=100)
    debt_type: Optional[DebtType] = None
    
    # Encrypted financial fields
    balance_encrypted: Optional[str] = None
    apr_encrypted: Optional[str] = None
    minimum_payment_encrypted: Optional[str] = None
    
    # Optional metadata
    account_number_last4: Optional[str] = Field(None, pattern=r"^\d{4}$")
    due_date: Optional[int] = Field(None, ge=1, le=31)
    notes: Optional[str] = Field(None, max_length=500)
    
    # Status
    is_active: Optional[bool] = None


class DebtResponse(BaseModel):
    """Debt data returned to frontend."""
    id: str
    user_id: str
    creditor_name: str
    debt_type: DebtType
    
    # Encrypted financial fields (client decrypts)
    balance_encrypted: str = Field(validation_alias="current_balance_encrypted")
    apr_encrypted: str = Field(validation_alias="interest_rate_encrypted")
    minimum_payment_encrypted: str
    
    # Metadata
    account_number_last4: Optional[str] = None
    due_date: Optional[int] = Field(None, validation_alias="due_date_day")
    notes: Optional[str] = None
    
    # Status
    is_active: bool = True
    is_paid_off: bool = False
    paid_off_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True


class DebtSummary(BaseModel):
    """Summary statistics for user's debts (unencrypted, calculated server-side)."""
    total_debts: int
    active_debts: int
    paid_off_debts: int


class DebtListResponse(BaseModel):
    """Response containing list of debts with summary."""
    debts: list[DebtResponse]
    summary: DebtSummary
