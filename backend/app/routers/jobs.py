"""
Jobs router for background job status polling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.models.job import JobResponse, JobStatusResponse, JobType, JobStatus
from app.models.user import UserResponse
from app.dependencies import get_current_user
from app.db.repositories.job_repo import JobRepository
from app.core.errors import NotFoundError

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    current_user: UserResponse = Depends(get_current_user)
) -> JobResponse:
    """
    Get job status and result.
    
    Poll this endpoint to check if a background job has completed.
    When status is 'completed', the result will be available.
    
    Args:
        job_id: Job ID
        current_user: Authenticated user
    
    Returns:
        Job details with status and result
    
    Raises:
        404: If job not found or not authorized
    """
    try:
        return await JobRepository.get_by_id(job_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status_lightweight(
    job_id: str,
    current_user: UserResponse = Depends(get_current_user)
) -> JobStatusResponse:
    """
    Get lightweight job status (without full result).
    
    Use this for frequent polling to check if job is done.
    Once status is 'completed', use GET /jobs/{job_id} to get full result.
    
    Args:
        job_id: Job ID
        current_user: Authenticated user
    
    Returns:
        Lightweight status response
    
    Raises:
        404: If job not found or not authorized
    """
    try:
        job = await JobRepository.get_by_id(job_id, current_user.id)
        return JobStatusResponse(
            id=job.id,
            status=job.status,
            progress=job.progress,
            result=job.result if job.status == JobStatus.COMPLETED else None,
            error=job.error
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("", response_model=List[JobResponse])
async def get_user_jobs(
    job_type: Optional[JobType] = None,
    status: Optional[JobStatus] = None,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user)
) -> List[JobResponse]:
    """
    Get all jobs for the current user.
    
    Args:
        job_type: Optional filter by job type
        status: Optional filter by status
        limit: Maximum number of jobs (default 50)
        current_user: Authenticated user
    
    Returns:
        List of jobs
    """
    return await JobRepository.get_user_jobs(
        user_id=current_user.id,
        job_type=job_type,
        status=status,
        limit=limit
    )
