/**
 * Upload API service for document upload and OCR processing
 */

import api from './api';
import { createAndPollJob } from './jobPolling';
import type { JobPollOptions } from './jobPolling';

export interface ExtractedDebt {
    creditor_name: string;
    debt_type: string;
    balance: number;
    apr?: number;
    minimum_payment?: number;
    account_number_last4?: string;
    due_date?: number;
    confidence_score: number;
}

export interface OCRResult {
    upload_id: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    extracted_debts: ExtractedDebt[];
    raw_text?: string;
    overall_confidence: number;
    processing_time_ms?: number;
    error_message?: string;
    processed_at?: string;
}

export interface UploadResponse {
    id: string;
    user_id: string;
    filename: string;
    document_type: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    created_at: string;
    processing_started_at?: string;
    processing_completed_at?: string;
}

export interface UploadStatusResponse {
    id: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress_percentage: number;
    result?: OCRResult;
    error_message?: string;
}

class UploadService {
    /**
     * Upload a document for OCR processing (async with polling)
     */
    async uploadDocument(
        file: File,
        documentType: 'bank_statement' | 'credit_card_statement' | 'loan_statement' | 'other' = 'other',
        options?: JobPollOptions
    ): Promise<OCRResult> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', documentType);

        return createAndPollJob<OCRResult>(
            () => api.post('/uploads/document', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }),
            options
        );
    }

    /**
     * Check the status of an upload
     */
    async getUploadStatus(uploadId: string): Promise<UploadStatusResponse> {
        const response = await api.get<UploadStatusResponse>(`/uploads/${uploadId}/status`);
        return response.data;
    }

    /**
     * Get the OCR result for a completed upload
     */
    async getOCRResult(uploadId: string): Promise<OCRResult> {
        const response = await api.get<OCRResult>(`/uploads/${uploadId}/result`);
        return response.data;
    }

    /**
     * Poll for upload completion
     */
    async waitForCompletion(
        uploadId: string,
        onProgress?: (status: UploadStatusResponse) => void,
        maxAttempts = 30,
        intervalMs = 2000
    ): Promise<UploadStatusResponse> {
        let attempts = 0;

        while (attempts < maxAttempts) {
            const status = await this.getUploadStatus(uploadId);

            if (onProgress) {
                onProgress(status);
            }

            if (status.status === 'completed' || status.status === 'failed') {
                return status;
            }

            await new Promise((resolve) => setTimeout(resolve, intervalMs));
            attempts++;
        }

        throw new Error('Upload processing timed out');
    }
}

export const uploadService = new UploadService();
export default uploadService;
