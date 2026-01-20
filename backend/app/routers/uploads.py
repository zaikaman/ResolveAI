"""
Uploads router for document upload and OCR processing.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from app.models.upload import (
    UploadResponse,
    UploadStatusResponse,
    DocumentType,
    UploadStatus,
    OCRResult
)
from app.models.job import JobResponse, JobType
from app.services.ocr_service import OCRService
from app.services.job_service import job_service
from app.dependencies import get_current_user
from app.models.user import UserResponse
from datetime import datetime
import uuid
import base64

router = APIRouter(prefix="/uploads", tags=["uploads"])

# In-memory store for demo (replace with database in production)
_upload_cache: dict[str, dict] = {}


@router.post("/document", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(DocumentType.OTHER),
    current_user: UserResponse = Depends(get_current_user)
) -> JobResponse:
    """
    Upload a document for OCR processing (async).
    
    Creates a background job to process the document. Poll the returned
    job_id at /api/jobs/{job_id} to check status and get the extracted data.
    
    Supported formats: PNG, JPEG, WebP images.
    Maximum file size: 10MB.
    
    Args:
        file: Document file
        document_type: Type of document
        current_user: Authenticated user
    
    Returns:
        Job ID to poll for results
    
    Raises:
        400: If file validation fails
    """
    # Read file content
    content = await file.read()
    content_type = file.content_type or "application/octet-stream"
    
    # Validate file
    validation_error = OCRService.validate_file(content, content_type)
    if validation_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation_error
        )
    
    # Generate upload ID
    upload_id = str(uuid.uuid4())
    
    # Create background job for OCR processing
    job = await job_service.create_job(
        user_id=current_user.id,
        job_type=JobType.OCR_PROCESSING,
        input_data={
            "file_content": base64.b64encode(content).decode('utf-8'),
            "file_type": content_type,
            "upload_id": upload_id,
            "filename": file.filename or "document",
            "document_type": document_type.value
        }
    )
    
    return job


@router.get("/{upload_id}/status", response_model=UploadStatusResponse)
async def get_upload_status(
    upload_id: str,
    current_user: UserResponse = Depends(get_current_user)
) -> UploadStatusResponse:
    """
    Check the status of an upload/OCR job.
    
    Args:
        upload_id: Upload UUID
        current_user: Authenticated user
    
    Returns:
        Upload status with OCR result if completed
    
    Raises:
        404: If upload not found
    """
    if upload_id not in _upload_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload {upload_id} not found"
        )
    
    upload_info = _upload_cache[upload_id]
    
    # Verify ownership
    if upload_info["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload {upload_id} not found"
        )
    
    status_val = upload_info["status"]
    progress = 100 if status_val in [UploadStatus.COMPLETED, UploadStatus.FAILED] else 50
    
    return UploadStatusResponse(
        id=upload_id,
        status=status_val,
        progress_percentage=progress,
        result=upload_info.get("result"),
        error_message=upload_info.get("error")
    )


@router.get("/{upload_id}/result", response_model=OCRResult)
async def get_ocr_result(
    upload_id: str,
    current_user: UserResponse = Depends(get_current_user)
) -> OCRResult:
    """
    Get the OCR result for a completed upload.
    
    Args:
        upload_id: Upload UUID
        current_user: Authenticated user
    
    Returns:
        OCR result with extracted debts
    
    Raises:
        404: If upload not found or not completed
    """
    if upload_id not in _upload_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload {upload_id} not found"
        )
    
    upload_info = _upload_cache[upload_id]
    
    # Verify ownership
    if upload_info["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload {upload_id} not found"
        )
    
    if upload_info["status"] != UploadStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload is not completed. Current status: {upload_info['status'].value}"
        )
    
    result = upload_info.get("result")
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR result not available"
        )
    
    return result
