/**
 * Application constants
 */

// API Configuration
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Debt Types
export const DEBT_TYPES = [
  { value: 'credit_card', label: 'Credit Card' },
  { value: 'personal_loan', label: 'Personal Loan' },
  { value: 'mortgage', label: 'Mortgage' },
  { value: 'auto_loan', label: 'Auto Loan' },
  { value: 'student_loan', label: 'Student Loan' },
  { value: 'business_loan', label: 'Business Loan' },
  { value: 'informal', label: 'Personal Debt' },
  { value: 'other', label: 'Other' },
] as const;

// Repayment Strategies
export const REPAYMENT_STRATEGIES = [
  {
    value: 'avalanche',
    label: 'High Interest First (Avalanche)',
    description: 'Pay off debts with highest interest rate first, save the most on interest',
  },
  {
    value: 'snowball',
    label: 'Lowest Balance First (Snowball)',
    description: 'Pay off smallest debts first, build psychological momentum',
  },
] as const;

// Notification Frequencies
export const NOTIFICATION_FREQUENCIES = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'custom', label: 'Custom' },
] as const;

// Languages
export const LANGUAGES = [
  { value: 'vi', label: 'Vietnamese' },
  { value: 'en', label: 'English' },
] as const;

// Timezones
export const TIMEZONES = [
  { value: 'Asia/Ho_Chi_Minh', label: 'Vietnam (GMT+7)' },
  { value: 'Asia/Bangkok', label: 'Bangkok (GMT+7)' },
  { value: 'Asia/Singapore', label: 'Singapore (GMT+8)' },
  { value: 'Asia/Tokyo', label: 'Tokyo (GMT+9)' },
] as const;

// Validation Constraints
export const VALIDATION = {
  APR_MIN: 0,
  APR_MAX: 50,
  BALANCE_MIN: 0,
  CREDITOR_NAME_MAX_LENGTH: 255,
  PAYMENT_AMOUNT_MIN: 0,
} as const;

// UI Constants
export const TOAST_DURATION = 5000; // milliseconds
export const DEBOUNCE_DELAY = 300; // milliseconds
export const PAGE_SIZE = 20;

// File Upload
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
export const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
export const ACCEPTED_DOCUMENT_TYPES = ['application/pdf', ...ACCEPTED_IMAGE_TYPES];

// Chart Colors (TailwindCSS green scale for progress)
export const CHART_COLORS = {
  progress: ['#10b981', '#059669', '#047857', '#065f46'],
  warm: ['#f59e0b', '#f97316', '#dc2626'],
  neutral: ['#6b7280', '#9ca3af', '#d1d5db'],
};

// Performance Thresholds (from spec)
export const PERFORMANCE = {
  PLAN_GENERATION_MAX_MS: 3000,
  PAYMENT_LOGGING_MAX_MS: 500,
  OCR_PROCESSING_MAX_MS: 10000,
  API_RESPONSE_P95_MS: 500,
  UI_INTERACTION_P95_MS: 200,
} as const;
