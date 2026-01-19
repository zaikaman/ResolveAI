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
from app.services.ocr_service import OCRService
from app.dependencies import get_current_user
from app.models.user import UserResponse
from datetime import datetime
import uuid

router = APIRouter(prefix="/uploads", tags=["uploads"])

# In-memory store for demo (replace with database in production)
_upload_cache: dict[str, dict] = {}


@router.post("/document", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(DocumentType.OTHER),
    current_user: UserResponse = Depends(get_current_user)
) -> UploadResponse:
    """
    Upload a document for OCR processing.
    
    Supported formats: PNG, JPEG, WebP images.
    Maximum file size: 10MB.
    
    Args:
        file: Document file
        document_type: Type of document
        current_user: Authenticated user
    
    Returns:
        Upload details with processing status
    
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
    
    # Store upload info
    upload_info = {
        "id": upload_id,
        "user_id": current_user.id,
        "filename": file.filename or "document",
        "document_type": document_type,
        "status": UploadStatus.PROCESSING,
        "created_at": datetime.utcnow(),
        "content": content,
        "content_type": content_type
    }
    _upload_cache[upload_id] = upload_info
    
    # Process immediately (in production, use background task)
    try:
        result = await OCRService.process_document(content, content_type, upload_id)
        _upload_cache[upload_id]["result"] = result
        _upload_cache[upload_id]["status"] = result.status
    except Exception as e:
        _upload_cache[upload_id]["status"] = UploadStatus.FAILED
        _upload_cache[upload_id]["error"] = str(e)
    
    return UploadResponse(
        id=upload_id,
        user_id=current_user.id,
        filename=file.filename or "document",
        document_type=document_type,
        status=_upload_cache[upload_id]["status"],
        created_at=upload_info["created_at"],
        processing_started_at=upload_info["created_at"],
        processing_completed_at=datetime.utcnow() if _upload_cache[upload_id]["status"] != UploadStatus.PROCESSING else None
    )


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
