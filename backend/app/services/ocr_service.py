"""
OCR service for document processing using GPT-4 Vision.
"""

from typing import List, Optional
import base64
from datetime import datetime
from app.core.openai_client import get_openai_client
from app.models.upload import ExtractedDebt, OCRResult, UploadStatus
from app.core.errors import ExternalServiceError
import json


class OCRService:
    """Service for extracting debt information from documents using AI vision."""
    
    EXTRACTION_PROMPT = """You are a financial document analyzer. Extract debt information from this document image.

For each debt found, extract:
- creditor_name: The name of the creditor/bank
- debt_type: One of: credit_card, personal_loan, student_loan, mortgage, auto_loan, medical, other
- balance: The current outstanding balance (number only, no currency symbols)
- apr: The annual percentage rate if visible (number only, e.g., 18.99)
- minimum_payment: The minimum monthly payment if visible (number only)
- account_number_last4: Last 4 digits of account number if visible
- due_date: Day of month payment is due (1-31) if visible

Return a JSON object with:
{
  "debts": [
    {
      "creditor_name": "...",
      "debt_type": "...",
      "balance": 1234.56,
      "apr": 18.99,
      "minimum_payment": 50.00,
      "account_number_last4": "1234",
      "due_date": 15,
      "confidence": 0.95
    }
  ],
  "raw_text": "Brief summary of what was found in the document"
}

If you cannot extract certain fields, omit them. Provide confidence scores (0-1) for each debt.
Only extract debts you are reasonably confident about (confidence > 0.6).
"""
    
    @staticmethod
    async def process_document(
        file_content: bytes,
        file_type: str,
        upload_id: str
    ) -> OCRResult:
        """
        Process a document image and extract debt information.
        
        Args:
            file_content: Raw file bytes
            file_type: MIME type (image/png, image/jpeg, application/pdf)
            upload_id: Upload ID for tracking
        
        Returns:
            OCRResult with extracted debts
        """
        start_time = datetime.utcnow()
        
        try:
            # Encode image to base64
            base64_image = base64.b64encode(file_content).decode('utf-8')
            
            # Determine media type
            if file_type in ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']:
                media_type = file_type
            else:
                # For PDFs, we'd need to convert first - for now, require images
                return OCRResult(
                    upload_id=upload_id,
                    status=UploadStatus.FAILED,
                    error_message="Only image files (PNG, JPEG, WebP) are currently supported"
                )
            
            # Call OpenAI Vision API
            client = get_openai_client()
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",  # Using mini for cost efficiency
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": OCRService.EXTRACTION_PROMPT
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            result_data = json.loads(result_text)
            
            # Convert to ExtractedDebt models
            extracted_debts: List[ExtractedDebt] = []
            for debt_data in result_data.get("debts", []):
                confidence = debt_data.get("confidence", 0.8)
                if confidence >= 0.6:
                    extracted_debts.append(ExtractedDebt(
                        creditor_name=debt_data.get("creditor_name", "Unknown"),
                        debt_type=debt_data.get("debt_type", "other"),
                        balance=float(debt_data.get("balance", 0)),
                        apr=float(debt_data.get("apr")) if debt_data.get("apr") else None,
                        minimum_payment=float(debt_data.get("minimum_payment")) if debt_data.get("minimum_payment") else None,
                        account_number_last4=debt_data.get("account_number_last4"),
                        due_date=int(debt_data.get("due_date")) if debt_data.get("due_date") else None,
                        confidence_score=confidence
                    ))
            
            # Calculate processing time
            end_time = datetime.utcnow()
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Calculate overall confidence
            overall_confidence = 0.0
            if extracted_debts:
                overall_confidence = sum(d.confidence_score for d in extracted_debts) / len(extracted_debts)
            
            return OCRResult(
                upload_id=upload_id,
                status=UploadStatus.COMPLETED,
                extracted_debts=extracted_debts,
                raw_text=result_data.get("raw_text", ""),
                overall_confidence=overall_confidence,
                processing_time_ms=processing_time_ms,
                processed_at=end_time
            )
            
        except json.JSONDecodeError as e:
            return OCRResult(
                upload_id=upload_id,
                status=UploadStatus.FAILED,
                error_message=f"Failed to parse AI response: {str(e)}"
            )
        except Exception as e:
            return OCRResult(
                upload_id=upload_id,
                status=UploadStatus.FAILED,
                error_message=f"OCR processing failed: {str(e)}"
            )
    
    @staticmethod
    def validate_file(file_content: bytes, file_type: str) -> Optional[str]:
        """
        Validate file before processing.
        
        Args:
            file_content: Raw file bytes
            file_type: MIME type
        
        Returns:
            Error message if invalid, None if valid
        """
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024
        if len(file_content) > max_size:
            return f"File too large. Maximum size is 10MB, got {len(file_content) / 1024 / 1024:.1f}MB"
        
        # Check file type
        allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']
        if file_type not in allowed_types:
            return f"Unsupported file type: {file_type}. Allowed: PNG, JPEG, WebP"
        
        # Check minimum size (likely empty or corrupted if too small)
        min_size = 1024  # 1KB minimum
        if len(file_content) < min_size:
            return "File appears to be empty or too small"
        
        return None
