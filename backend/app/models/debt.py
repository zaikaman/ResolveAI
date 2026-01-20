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
    """Payload for creating a new debt (plaintext, server will encrypt)."""
    creditor_name: str = Field(..., min_length=1, max_length=100)
    debt_type: DebtType = DebtType.OTHER
    
    # Financial fields (plaintext, server encrypts before storage)
    balance: float = Field(..., gt=0, description="Current balance")
    apr: float = Field(..., ge=0, le=100, description="Annual percentage rate")
    minimum_payment: float = Field(..., gt=0, description="Minimum monthly payment")
    
    # Optional metadata
    account_number_last4: Optional[str] = Field(None, pattern=r"^\d{4}$")
    due_date: Optional[int] = Field(None, ge=1, le=31, description="Day of month payment is due")
    notes: Optional[str] = Field(None, max_length=500)


class DebtUpdate(BaseModel):
    """Payload for updating an existing debt (plaintext, server will encrypt)."""
    creditor_name: Optional[str] = Field(None, min_length=1, max_length=100)
    debt_type: Optional[DebtType] = None
    
    # Financial fields (plaintext)
    balance: Optional[float] = Field(None, gt=0)
    apr: Optional[float] = Field(None, ge=0, le=100)
    minimum_payment: Optional[float] = Field(None, gt=0)
    
    # Optional metadata
    account_number_last4: Optional[str] = Field(None, pattern=r"^\d{4}$")
    due_date: Optional[int] = Field(None, ge=1, le=31)
    notes: Optional[str] = Field(None, max_length=500)
    
    # Status
    is_active: Optional[bool] = None


class DebtResponse(BaseModel):
    """Debt data returned to frontend (plaintext, server decrypts from storage)."""
    id: str
    user_id: str
    creditor_name: str
    debt_type: DebtType
    
    # Financial fields (plaintext, decrypted by server)
    balance: float
    apr: float
    minimum_payment: float
    
    # Metadata
    account_number_last4: Optional[str] = None
    due_date: Optional[int] = None
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
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class DebtSummary(BaseModel):
    """Summary statistics for user's debts (unencrypted, calculated server-side)."""
    total_debts: int
    active_debts: int
    paid_off_debts: int


class DebtListResponse(BaseModel):
    """Response containing list of debts with summary."""
    debts: list[DebtResponse]
    summary: DebtSummary
