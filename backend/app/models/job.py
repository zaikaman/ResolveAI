"""
Job models for async background task processing.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job execution status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, Enum):
    """Types of background jobs."""
    PLAN_GENERATION = "plan_generation"
    PLAN_RECALCULATION = "plan_recalculation"
    PLAN_SIMULATION = "plan_simulation"
    DAILY_ACTIONS = "daily_actions"
    MILESTONE_CHECK = "milestone_check"
    OCR_PROCESSING = "ocr_processing"
    DEBT_ANALYSIS = "debt_analysis"


class JobCreate(BaseModel):
    """Request to create a new job."""
    job_type: JobType
    user_id: str
    input_data: dict[str, Any]


class JobResponse(BaseModel):
    """Job status and result response."""
    id: str
    job_type: JobType
    status: JobStatus
    user_id: str
    input_data: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    progress: Optional[int] = Field(default=0, ge=0, le=100)
    
    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    """Lightweight job status check response."""
    id: str
    status: JobStatus
    progress: Optional[int] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
