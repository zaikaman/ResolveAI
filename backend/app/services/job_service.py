"""
Background job processing service.
"""

import asyncio
from typing import Any, Callable, Coroutine
from app.models.job import JobCreate, JobResponse, JobStatus, JobType
from app.db.repositories.job_repo import JobRepository
from app.core.errors import ValidationError
import traceback


class JobService:
    """Service for managing background job execution."""
    
    # Registry of job handlers
    _handlers: dict[JobType, Callable[[str, dict[str, Any]], Coroutine[Any, Any, dict]]] = {}
    
    @classmethod
    def register_handler(
        cls,
        job_type: JobType,
        handler: Callable[[str, dict[str, Any]], Coroutine[Any, Any, dict]]
    ):
        """
        Register a handler for a job type.
        
        Args:
            job_type: Type of job
            handler: Async function that processes the job
        """
        cls._handlers[job_type] = handler
    
    @classmethod
    async def create_job(
        cls,
        user_id: str,
        job_type: JobType,
        input_data: dict[str, Any]
    ) -> JobResponse:
        """
        Create and queue a new job.
        
        Args:
            user_id: User ID
            job_type: Type of job
            input_data: Job input parameters
        
        Returns:
            Created job
        """
        job_data = JobCreate(
            job_type=job_type,
            user_id=user_id,
            input_data=input_data
        )
        
        job = await JobRepository.create(job_data)
        
        # Start processing in background (fire and forget)
        asyncio.create_task(cls._process_job(job.id))
        
        return job
    
    @classmethod
    async def get_job_status(cls, job_id: str, user_id: str) -> JobResponse:
        """
        Get job status and result.
        
        Args:
            job_id: Job ID
            user_id: User ID for authorization
        
        Returns:
            Job details
        """
        return await JobRepository.get_by_id(job_id, user_id)
    
    @classmethod
    async def _process_job(cls, job_id: str):
        """
        Process a job in the background.
        
        Args:
            job_id: Job ID to process
        """
        try:
            # Get job details
            job = await JobRepository.get_by_id(job_id)
            
            # Update status to processing
            await JobRepository.update_status(
                job_id,
                JobStatus.PROCESSING,
                progress=0
            )
            
            # Get handler for this job type
            handler = cls._handlers.get(job.job_type)
            
            if not handler:
                await JobRepository.update_status(
                    job_id,
                    JobStatus.FAILED,
                    error=f"No handler registered for job type: {job.job_type}"
                )
                return
            
            # Execute handler
            result = await handler(job.user_id, job.input_data)
            
            # Update job with result
            await JobRepository.update_status(
                job_id,
                JobStatus.COMPLETED,
                progress=100,
                result=result
            )
            
        except Exception as e:
            # Log error and update job status
            error_msg = f"{type(e).__name__}: {str(e)}"
            error_trace = traceback.format_exc()
            
            print(f"[JobService] Job {job_id} failed: {error_msg}")
            print(error_trace)
            
            await JobRepository.update_status(
                job_id,
                JobStatus.FAILED,
                error=error_msg
            )


# Export singleton instance
job_service = JobService()
