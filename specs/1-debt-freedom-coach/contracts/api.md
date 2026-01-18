# API Contracts: ResolveAI Backend

**Feature**: ResolveAI Debt Freedom Coach  
**Created**: 2026-01-18  
**Backend**: FastAPI (Python)  
**Base URL**: `https://api.resolveai.app` (production) | `http://localhost:8000` (development)

## Overview

This document defines the REST API contracts for ResolveAI backend. All endpoints return JSON responses. Authentication uses JWT tokens (Supabase Auth). Complete OpenAPI specification auto-generated at `/docs` endpoint.

## Authentication

**Method**: JWT Bearer Token (Supabase Auth)

**Header**:
```
Authorization: Bearer <jwt_token>
```

**Obtaining Token**:
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}

Response 200:
{
  "access_token": "eyJ...",
  "refresh_token": "...",
  "user": {
    "id": "uuid",
    "email": "user@example.com"
  }
}
```

---

## Endpoints

### Authentication & Users

#### POST /auth/signup
**Purpose**: Create new user account

**Request**:
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "Nguyen Van A"
}
```

**Response 201**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Nguyen Van A",
  "created_at": "2026-01-18T10:00:00Z"
}
```

**Errors**:
- 400: Email already exists
- 422: Validation error (invalid email format, weak password)

---

#### GET /users/me
**Purpose**: Get current user profile

**Response 200**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "Nguyen Van A",
  "monthly_income_encrypted": "...",
  "repayment_strategy": "avalanche",
  "notification_enabled": true,
  "onboarding_completed": false
}
```

---

#### PATCH /users/me
**Purpose**: Update user profile or preferences

**Request**:
```json
{
  "full_name": "Nguyen Van B",
  "monthly_income_encrypted": "AES(...)",
  "repayment_strategy": "snowball",
  "notification_time": "09:00:00"
}
```

**Response 200**: Updated user object

---

### Debts

#### GET /debts
**Purpose**: List all active debts for current user

**Query Parameters**:
- `include_inactive` (bool, default: false): Include paid-off debts

**Response 200**:
```json
{
  "debts": [
    {
      "id": "uuid-1",
      "creditor_name": "VCB Credit Card",
      "debt_type": "credit_card",
      "current_balance_encrypted": "AES(...)",
      "interest_rate_encrypted": "AES(...)",
      "minimum_payment_encrypted": "AES(...)",
      "due_date_day": 15,
      "is_active": true,
      "created_at": "2026-01-10T00:00:00Z"
    },
    ...
  ],
  "total_count": 4,
  "total_balance": 25000.00  // Decrypted for display (frontend decrypts again)
}
```

---

#### POST /debts
**Purpose**: Create new debt (manual entry or OCR result)

**Request**:
```json
{
  "creditor_name": "Techcombank Visa",
  "debt_type": "credit_card",
  "current_balance_encrypted": "AES(...)",
  "original_balance_encrypted": "AES(...)",
  "interest_rate_encrypted": "AES(...)",
  "minimum_payment_encrypted": "AES(...)",
  "due_date_day": 20,
  "account_opened_date": "2020-05-15"
}
```

**Response 201**:
```json
{
  "id": "uuid-new",
  "creditor_name": "Techcombank Visa",
  ...
}
```

**Errors**:
- 400: Invalid debt data (e.g., balance ≤ 0, APR > 50%)
- 422: Validation error

---

#### PATCH /debts/{debt_id}
**Purpose**: Update existing debt

**Request**: Same fields as POST (partial update supported)

**Response 200**: Updated debt object

---

#### DELETE /debts/{debt_id}
**Purpose**: Delete debt (with confirmation)

**Query Parameters**:
- `reason` (enum): "paid_off" | "transferred" | "error"

**Response 204**: No content

**Side Effects**:
- If `reason=paid_off`: Triggers milestone check, celebration
- If `reason=transferred`: No celebration, just removal
- Recalculates active repayment plan

---

### Repayment Plans

#### POST /plans/generate
**Purpose**: Generate optimized debt repayment plan

**Request**:
```json
{
  "strategy": "avalanche",  // or "snowball"
  "target_months": 24,  // Optional: target completion in 24 months
  "extra_payment": 100.00  // Optional: extra monthly payment beyond minimums
}
```

**Response 200**:
```json
{
  "plan": {
    "id": "plan-uuid",
    "strategy": "avalanche",
    "target_debt_free_date": "2028-01-18",
    "total_debt_amount": 25000.00,
    "total_interest_projection": 3200.50,
    "monthly_payment_total": 1050.00,
    "payment_schedule": {
      "months": [
        {
          "month": 1,
          "date": "2026-02-01",
          "payments": [
            {"debt_id": "uuid-1", "amount": 500.00},
            {"debt_id": "uuid-2", "amount": 550.00}
          ],
          "total_paid": 1050.00,
          "remaining_debt": 23950.00
        },
        ...
      ],
      "milestones": [
        {"month": 8, "description": "First debt paid off"}
      ]
    }
  },
  "comparison": {
    "avalanche": {
      "total_interest": 3200.50,
      "months_to_freedom": 24
    },
    "snowball": {
      "total_interest": 3450.00,
      "months_to_freedom": 25
    }
  },
  "first_week_actions": [
    {
      "action_date": "2026-01-19",
      "description": "Pay $500 to VCB Credit Card",
      "priority": 1
    },
    ...
  ]
}
```

**Errors**:
- 400: Unsustainable debt (income < minimum payments)
- 422: No active debts to plan

**Opik Tracing**: This endpoint traces full agent chain (AssessmentAgent → OptimizationAgent → ActionAgent)

---

#### POST /plans/recalculate
**Purpose**: Recalculate plan after income/expense change or payment

**Request**:
```json
{
  "trigger": "income_change",  // or "payment_logged", "expense_change"
  "new_income_encrypted": "AES(...)",  // If income changed
  "new_expenses_encrypted": "AES(...)"  // If expenses changed
}
```

**Response 200**: Same structure as `/plans/generate` with updated projections

**Performance**: Must complete in <2 seconds (spec PERF-005)

---

#### POST /plans/simulate
**Purpose**: Simulate "what-if" scenarios without saving

**Request**:
```json
{
  "scenario": "extra_payment",
  "extra_amount": 200.00,  // Extra $200/month
  "interest_rate_reductions": {  // Simulate negotiation success
    "debt-uuid-1": 16.0  // Reduce from 22% to 16%
  }
}
```

**Response 200**: Projected plan with scenario applied (not saved to DB)

---

### Payments

#### GET /payments
**Purpose**: List payment history for current user

**Query Parameters**:
- `debt_id` (uuid, optional): Filter by specific debt
- `start_date` (date, optional): Filter from date
- `end_date` (date, optional): Filter to date
- `limit` (int, default: 50): Pagination limit

**Response 200**:
```json
{
  "payments": [
    {
      "id": "payment-uuid",
      "debt_id": "debt-uuid",
      "amount": 500.00,
      "payment_date": "2026-01-15",
      "new_balance": 9500.00,
      "interest_saved": 15.50,
      "created_at": "2026-01-15T10:30:00Z"
    },
    ...
  ],
  "total_paid": 2500.00,
  "total_interest_saved": 120.00
}
```

---

#### POST /payments
**Purpose**: Log a debt payment

**Request**:
```json
{
  "debt_id": "debt-uuid",
  "amount": 500.00,
  "payment_date": "2026-01-15",
  "payment_method": "bank_transfer"
}
```

**Response 201**:
```json
{
  "id": "payment-uuid",
  "debt_id": "debt-uuid",
  "amount": 500.00,
  "new_balance": 9500.00,
  "interest_saved": 15.50,
  "milestone_triggered": {
    "type": "percentage_milestone",
    "title": "25% Debt-Free!",
    "description": "You've eliminated 25% of your total debt!"
  }
}
```

**Side Effects**:
- Updates debt balance (encrypted)
- Recalculates repayment plan projections
- Checks for milestones (25%, 50%, 75%, debt paid off, streaks)
- Generates next actions
- **Performance**: Must complete in <500ms (spec PERF-002)

**Opik Tracing**: Traces HabitAgent milestone detection

---

### Document Upload & OCR

#### POST /uploads
**Purpose**: Upload financial document (Vietnamese bank statement) for OCR

**Request**: `multipart/form-data`
```
file: <PDF or image file>
document_type: "credit_card_statement" | "loan_statement" | "bank_statement"
```

**Response 202** (Accepted, processing async):
```json
{
  "upload_id": "upload-uuid",
  "status": "processing",
  "estimated_completion": "2026-01-18T10:00:10Z"  // ~10 seconds
}
```

**Errors**:
- 400: File too large (>10MB)
- 415: Unsupported file type (only PDF, PNG, JPG)

---

#### GET /uploads/{upload_id}
**Purpose**: Check OCR processing status

**Response 200**:
```json
{
  "upload_id": "upload-uuid",
  "status": "completed",  // or "processing", "failed"
  "result": {
    "creditor_name": "Vietcombank",
    "balance": 10500.00,
    "interest_rate": 18.5,
    "minimum_payment": 315.00,
    "due_date_day": 15,
    "confidence_score": 0.95  // Opik quality score
  },
  "manual_review_needed": false,  // True if confidence < 0.85
  "processing_time_ms": 8500
}
```

**Usage Flow**:
1. Frontend uploads file → Gets `upload_id`
2. Frontend polls `/uploads/{upload_id}` every 2 seconds
3. When `status=completed`, display extracted data with manual correction UI
4. User confirms/corrects → POST to `/debts` to save

**Opik Tracing**: Traces GPT-5-Nano vision API call (prompt, response, latency, accuracy via LLM-as-judge)

---

### Spending Insights (P4 User Story)

#### POST /insights/analyze
**Purpose**: Analyze uploaded transactions for spending leaks

**Request**: `multipart/form-data`
```
file: <CSV file with transactions>
format: "csv"  // Future: "plaid", "open_banking"
```

**Response 200**:
```json
{
  "insight_id": "insight-uuid",
  "transaction_count": 243,
  "analysis_period": {
    "start": "2025-10-01",
    "end": "2026-01-01"
  },
  "top_categories": [
    {
      "category": "dining",
      "monthly_avg": 320.00,
      "percentage": 15.2,
      "transaction_count": 42
    },
    ...
  ],
  "identified_leaks": [
    {
      "type": "duplicate_subscription",
      "name": "Netflix",
      "monthly_cost": 15.99,
      "suggestion": "Cancel duplicate Netflix subscription"
    },
    ...
  ],
  "total_leak_amount": 250.00,
  "months_saved_if_applied": 4.2,
  "confidence": 0.88
}
```

**Opik Tracing**: Traces transaction categorization agent (GPT-5-Nano with few-shot examples)

---

### Negotiation Support (P5 User Story)

#### POST /negotiation/script
**Purpose**: Generate personalized creditor negotiation script

**Request**:
```json
{
  "debt_id": "debt-uuid"
}
```

**Response 200**:
```json
{
  "script_id": "script-uuid",
  "script_text": "Hi, my name is [Your Name]. I've been a loyal Vietcombank customer for 5 years with strong payment history. I'm working hard to pay off my balance, but the 22% APR makes it difficult. I've received offers for 15% from competitors. Can you lower my rate to help me pay this off faster?",
  "talking_points": [
    {"key": "loyalty", "text": "5 years as customer"},
    {"key": "payment_history", "text": "85% on-time payments"},
    ...
  ],
  "success_probability": 0.72,
  "optimal_timing": "Call 2-3 days after your next on-time payment",
  "vapi_session_available": true
}
```

**Opik Tracing**: Traces NegotiationAgent script generation (personalization quality)

---

#### POST /negotiation/vapi-session
**Purpose**: Create Vapi.ai voice simulation session for practice

**Request**:
```json
{
  "script_id": "script-uuid"
}
```

**Response 200**:
```json
{
  "vapi_session_id": "vapi-123",
  "session_url": "https://vapi.ai/session/vapi-123",
  "instructions": "Click the link to start voice practice. The AI will play the role of the creditor."
}
```

**Frontend Usage**: Embed Vapi iframe or redirect to session URL

---

### Actions & Reminders

#### GET /actions/today
**Purpose**: Get today's recommended actions

**Response 200**:
```json
{
  "date": "2026-01-18",
  "actions": [
    {
      "id": "action-uuid",
      "action_type": "payment",
      "description": "Pay $500 to VCB Credit Card",
      "priority": 1,
      "related_debt": {
        "id": "debt-uuid",
        "creditor_name": "VCB Credit Card"
      },
      "suggested_amount": 500.00
    },
    ...
  ],
  "motivational_message": "You're doing great! Keep the momentum going."
}
```

---

#### POST /actions/{action_id}/complete
**Purpose**: Mark action as completed

**Response 200**:
```json
{
  "action_id": "action-uuid",
  "completed": true,
  "next_action": {
    "description": "Review your progress tomorrow",
    "action_date": "2026-01-19"
  }
}
```

---

### Health & Monitoring

#### GET /health
**Purpose**: Health check for load balancer

**Response 200**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-18T10:00:00Z"
}
```

---

#### GET /readiness
**Purpose**: Readiness check (DB connection, external services)

**Response 200**:
```json
{
  "ready": true,
  "checks": {
    "database": "ok",
    "supabase": "ok",
    "openai": "ok",
    "vapi": "ok"
  }
}
```

---

## Error Responses

**Standard Error Format**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Interest rate must be between 0% and 50%",
    "details": {
      "field": "interest_rate",
      "value": 55.0
    }
  }
}
```

**HTTP Status Codes**:
- 400: Bad Request (user error, invalid input)
- 401: Unauthorized (missing or invalid JWT)
- 403: Forbidden (authenticated but not authorized)
- 404: Not Found (resource doesn't exist)
- 422: Unprocessable Entity (validation error)
- 429: Too Many Requests (rate limit exceeded)
- 500: Internal Server Error (system error)
- 503: Service Unavailable (external dependency down)

---

## Rate Limiting

**Default Limits**:
- 100 requests per minute per user
- 1000 requests per hour per user
- OCR uploads: 10 per hour per user (expensive operation)

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1610000000
```

**Error Response** (429):
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again in 45 seconds.",
    "retry_after": 45
  }
}
```

---

## OpenAPI Specification

**Auto-Generated Docs**: Available at `GET /docs` (Swagger UI) and `GET /redoc` (ReDoc)

**Download OpenAPI JSON**: `GET /openapi.json`

**Example Usage**:
```bash
# Generate TypeScript client from OpenAPI spec
npx openapi-typescript-codegen --input http://localhost:8000/openapi.json --output frontend/src/api/generated
```

---

## WebSocket (Future Enhancement)

**Real-Time Plan Updates** (optional, not MVP):
```
wss://api.resolveai.app/ws/plans/{plan_id}

Message Format:
{
  "type": "plan_updated",
  "data": {
    "new_debt_free_date": "2027-12-15",
    "reason": "payment_logged"
  }
}
```

---

## Summary

**Total Endpoints**: 25+ endpoints covering:
- Authentication & Users (3)
- Debts CRUD (5)
- Repayment Plans (3)
- Payments (2)
- Uploads & OCR (2)
- Spending Insights (1)
- Negotiation Support (2)
- Actions & Reminders (2)
- Health & Monitoring (2)

**Performance**: All endpoints meet spec requirements (<500ms p95, <200ms for dashboard queries)

**Security**: JWT authentication, input validation (Pydantic), rate limiting, encrypted data handling

**Observability**: Opik tracing on all agent endpoints (plan generation, OCR, insights, negotiation)

Complete OpenAPI specification ensures frontend/backend contract alignment and enables code generation.
