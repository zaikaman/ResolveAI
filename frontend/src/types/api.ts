/**
 * API request/response types and error handling
 */

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, any>;
  detail?: any; // For standard FastAPI/Pydantic errors
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}
