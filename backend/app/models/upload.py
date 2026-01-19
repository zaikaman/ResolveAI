"""
Upload Pydantic models for document upload and OCR processing.

Aligned with data-model.md schema.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class UploadStatus(str, Enum):
    """Status of an upload/OCR job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, Enum):
    """Types of documents that can be uploaded."""
    BANK_STATEMENT = "bank_statement"
    CREDIT_CARD_STATEMENT = "credit_card_statement"
    LOAN_STATEMENT = "loan_statement"
    OTHER = "other"


class UploadRequest(BaseModel):
    """Metadata sent with file upload."""
    document_type: DocumentType = DocumentType.OTHER
    notes: Optional[str] = Field(None, max_length=500)


class UploadResponse(BaseModel):
    """Response after initiating an upload."""
    id: str
    user_id: str
    filename: str
    document_type: DocumentType
    status: UploadStatus
    created_at: datetime
    
    # Processing info
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ExtractedDebt(BaseModel):
    """Debt information extracted from OCR."""
    creditor_name: str
    debt_type: str
    balance: float
    apr: Optional[float] = None
    minimum_payment: Optional[float] = None
    account_number_last4: Optional[str] = None
    due_date: Optional[int] = None
    confidence_score: float = Field(..., ge=0, le=1)


class OCRResult(BaseModel):
    """Result of OCR processing."""
    upload_id: str
    status: UploadStatus
    
    # Extracted data
    extracted_debts: list[ExtractedDebt] = []
    raw_text: Optional[str] = None
    
    # Confidence and metadata
    overall_confidence: float = Field(0.0, ge=0, le=1)
    processing_time_ms: Optional[int] = None
    
    # Error info if failed
    error_message: Optional[str] = None
    
    # Timestamps
    processed_at: Optional[datetime] = None


class UploadStatusResponse(BaseModel):
    """Response for checking upload status."""
    id: str
    status: UploadStatus
    progress_percentage: int = Field(0, ge=0, le=100)
    
    # If completed, include result
    result: Optional[OCRResult] = None
    
    # If failed, include error
    error_message: Optional[str] = None
