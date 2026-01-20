"""
Job repository for managing background job storage.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from app.models.job import JobCreate, JobResponse, JobStatus, JobType
from app.core.errors import NotFoundError


class JobRepository:
    """In-memory job storage (replace with database in production)."""
    
    _jobs: dict[str, dict] = {}
    
    @classmethod
    async def create(cls, job_data: JobCreate) -> JobResponse:
        """
        Create a new job.
        
        Args:
            job_data: Job creation data
        
        Returns:
            Created job
        """
        job_id = str(uuid4())
        now = datetime.utcnow()
        
        job = {
            "id": job_id,
            "job_type": job_data.job_type,
            "status": JobStatus.PENDING,
            "user_id": job_data.user_id,
            "input_data": job_data.input_data,
            "created_at": now,
            "updated_at": now,
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "progress": 0
        }
        
        cls._jobs[job_id] = job
        return JobResponse(**job)
    
    @classmethod
    async def get_by_id(cls, job_id: str, user_id: Optional[str] = None) -> JobResponse:
        """
        Get job by ID.
        
        Args:
            job_id: Job ID
            user_id: Optional user ID for authorization check
        
        Returns:
            Job details
        
        Raises:
            NotFoundError: If job not found or unauthorized
        """
        job = cls._jobs.get(job_id)
        
        if not job:
            raise NotFoundError(
                resource_type="Job",
                resource_id=job_id
            )
        
        # Check user authorization
        if user_id and job["user_id"] != user_id:
            raise NotFoundError(
                resource_type="Job",
                resource_id=job_id
            )
        
        return JobResponse(**job)
    
    @classmethod
    async def update_status(
        cls,
        job_id: str,
        status: JobStatus,
        progress: Optional[int] = None,
        result: Optional[dict] = None,
        error: Optional[str] = None
    ) -> JobResponse:
        """
        Update job status.
        
        Args:
            job_id: Job ID
            status: New status
            progress: Optional progress percentage (0-100)
            result: Optional result data
            error: Optional error message
        
        Returns:
            Updated job
        
        Raises:
            NotFoundError: If job not found
        """
        job = cls._jobs.get(job_id)
        
        if not job:
            raise NotFoundError(
                resource_type="Job",
                resource_id=job_id
            )
        
        now = datetime.utcnow()
        job["status"] = status
        job["updated_at"] = now
        
        if progress is not None:
            job["progress"] = progress
        
        if status == JobStatus.PROCESSING and not job["started_at"]:
            job["started_at"] = now
        
        if status in (JobStatus.COMPLETED, JobStatus.FAILED):
            job["completed_at"] = now
            job["progress"] = 100 if status == JobStatus.COMPLETED else job["progress"]
        
        if result is not None:
            job["result"] = result
        
        if error is not None:
            job["error"] = error
        
        return JobResponse(**job)
    
    @classmethod
    async def get_user_jobs(
        cls,
        user_id: str,
        job_type: Optional[JobType] = None,
        status: Optional[JobStatus] = None,
        limit: int = 50
    ) -> List[JobResponse]:
        """
        Get jobs for a user.
        
        Args:
            user_id: User ID
            job_type: Optional filter by job type
            status: Optional filter by status
            limit: Maximum number of jobs to return
        
        Returns:
            List of jobs
        """
        jobs = []
        
        for job in cls._jobs.values():
            if job["user_id"] != user_id:
                continue
            
            if job_type and job["job_type"] != job_type:
                continue
            
            if status and job["status"] != status:
                continue
            
            jobs.append(JobResponse(**job))
        
        # Sort by created_at descending
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        
        return jobs[:limit]
    
    @classmethod
    async def cleanup_old_jobs(cls, days: int = 7) -> int:
        """
        Clean up completed/failed jobs older than specified days.
        
        Args:
            days: Age in days
        
        Returns:
            Number of jobs deleted
        """
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        to_delete = []
        
        for job_id, job in cls._jobs.items():
            if job["status"] in (JobStatus.COMPLETED, JobStatus.FAILED):
                if job["completed_at"] and job["completed_at"] < cutoff:
                    to_delete.append(job_id)
        
        for job_id in to_delete:
            del cls._jobs[job_id]
        
        return len(to_delete)
