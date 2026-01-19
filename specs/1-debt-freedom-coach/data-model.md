# Data Model: ResolveAI Debt Freedom Coach

**Feature**: ResolveAI Debt Freedom Coach  
**Created**: 2026-01-18  
**Database**: Supabase PostgreSQL 15+

## Overview

This document defines the database schema for ResolveAI, including entity relationships, field-level encryption strategy, indexes for performance, and validation constraints aligned with constitutional requirements.

## Entity Relationship Diagram

```
┌─────────────┐
│    users    │ 1
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────┐       ┌──────────────┐
│    debts    │ N ────┤ repayment_   │ 1
└──────┬──────┘   N   │   plans      │
       │              └──────┬───────┘
       │ 1:N                 │ 1:N
       │                     │
┌──────▼──────┐       ┌──────▼───────┐
│  payments   │       │   actions    │
└─────────────┘       └──────────────┘

┌─────────────┐       ┌──────────────┐
│transactions │ N ────┤   insights   │ 1
└──────┬──────┘       └──────────────┘
       │
       │ N:1
       │
┌──────▼──────┐
│    users    │
└─────────────┘

┌─────────────┐       ┌──────────────┐
│  milestones │ N ────┤    users     │ 1
└─────────────┘       └──────────────┘

┌─────────────┐       ┌──────────────┐
│  reminders  │ N ────┤    users     │ 1
└─────────────┘       └──────────────┘

┌─────────────┐       ┌──────────────┐
│negotiation_ │ N ────┤    debts     │ 1
│  scripts    │       └──────────────┘
└─────────────┘
```

## Core Entities

### users

**Purpose**: User accounts with authentication and profile information.

**Fields**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Profile
    full_name VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    language VARCHAR(10) DEFAULT 'en',
    
    -- Financial Context (encrypted at application level before storage)
    monthly_income_encrypted TEXT, -- AES-256 encrypted decimal value
    monthly_expenses_encrypted TEXT, -- AES-256 encrypted decimal value
    available_for_debt_encrypted TEXT, -- AES-256 encrypted decimal value
    
    -- Preferences
    repayment_strategy VARCHAR(20) DEFAULT 'avalanche' CHECK (repayment_strategy IN ('avalanche', 'snowball')),
    notification_enabled BOOLEAN DEFAULT TRUE,
    notification_time TIME DEFAULT '09:00:00',
    notification_frequency VARCHAR(20) DEFAULT 'daily' CHECK (notification_frequency IN ('daily', 'weekly', 'custom')),
    
    -- Metadata
    last_login_at TIMESTAMPTZ,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    terms_accepted_at TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**Validation**:
- Email format validated in application layer (Pydantic EmailStr)
- Income/expenses/available decrypted values must be ≥ 0 (validated after decryption)
- Repayment strategy enum enforced by CHECK constraint

**Encryption Strategy**:
- `monthly_income_encrypted`, `monthly_expenses_encrypted`, `available_for_debt_encrypted`: Client-side AES-256-GCM encryption with user-derived key (PBKDF2 from password), then server re-encrypts with app-level key before storage
- Rationale: Defense in depth (even with DB breach, data unreadable without both keys)

---

### debts

**Purpose**: Individual debt obligations (credit cards, loans, etc.)

**Fields**:
```sql
CREATE TABLE debts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Debt Details
    creditor_name VARCHAR(255) NOT NULL,
    debt_type VARCHAR(50) NOT NULL CHECK (debt_type IN ('credit_card', 'personal_loan', 'student_loan', 'medical_bill', 'auto_loan', 'mortgage', 'other')),
    
    -- Financial Data (encrypted)
    current_balance_encrypted TEXT NOT NULL, -- AES-256 encrypted decimal
    original_balance_encrypted TEXT, -- AES-256 encrypted decimal (for tracking progress)
    interest_rate_encrypted TEXT NOT NULL, -- AES-256 encrypted decimal (APR as percentage, e.g., 18.5)
    minimum_payment_encrypted TEXT NOT NULL, -- AES-256 encrypted decimal
    
    -- Dates
    due_date_day INTEGER CHECK (due_date_day BETWEEN 1 AND 31), -- Day of month (e.g., 15 for 15th)
    account_opened_date DATE, -- For negotiation scripts (account age calculation)
    
    -- Metadata
    payment_history_score DECIMAL(3, 2) CHECK (payment_history_score BETWEEN 0 AND 1), -- 0.0 to 1.0 (1.0 = perfect payment history)
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT -- User notes (not encrypted, low sensitivity)
);

CREATE INDEX idx_debts_user_id ON debts(user_id);
CREATE INDEX idx_debts_user_active ON debts(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_debts_due_date ON debts(user_id, due_date_day) WHERE is_active = TRUE;
```

**Validation**:
- Balance, interest rate, minimum payment decrypted values must be > 0
- Interest rate must be 0-50% (validated post-decryption, aligns with spec edge case)
- Payment history score 0.0-1.0 (1.0 = always on time, 0.0 = frequent late payments)

**Encryption Strategy**:
- Same dual-layer encryption as `users` financial fields
- `creditor_name` NOT encrypted (needed for display in lists, low sensitivity)

---

### repayment_plans

**Purpose**: Generated debt repayment plans with projected timelines

**Fields**:
```sql
CREATE TABLE repayment_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Plan Configuration
    strategy VARCHAR(20) NOT NULL CHECK (strategy IN ('avalanche', 'snowball')),
    target_debt_free_date DATE NOT NULL,
    
    -- Projections (not encrypted, derived from encrypted debts)
    total_debt_amount DECIMAL(12, 2) NOT NULL, -- Sum of all debts at plan creation
    total_interest_projection DECIMAL(12, 2) NOT NULL, -- Total interest if following plan
    monthly_payment_total DECIMAL(10, 2) NOT NULL, -- Total monthly payment across all debts
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE, -- Only one active plan per user at a time
    completed_at TIMESTAMPTZ, -- When user pays off all debts
    
    -- Plan Details (JSONB for flexibility)
    payment_schedule JSONB NOT NULL, -- Array of {month: 1, debt_id: uuid, amount: 250.00, ...}
    optimization_metadata JSONB -- PuLP solver details, algorithm choices
);

CREATE INDEX idx_plans_user_id ON repayment_plans(user_id);
CREATE UNIQUE INDEX idx_plans_active_user ON repayment_plans(user_id) WHERE is_active = TRUE; -- Only 1 active plan
CREATE INDEX idx_plans_created_at ON repayment_plans(created_at);
```

**Validation**:
- Only one active plan per user (enforced by unique index)
- `total_debt_amount`, `total_interest_projection`, `monthly_payment_total` must be ≥ 0
- `payment_schedule` JSONB schema validated in application layer

**Payment Schedule JSONB Structure**:
```json
{
  "months": [
    {
      "month": 1,
      "date": "2026-02-01",
      "payments": [
        {"debt_id": "uuid-1", "amount": 500.00, "is_minimum": false},
        {"debt_id": "uuid-2", "amount": 100.00, "is_minimum": true}
      ],
      "total_paid": 600.00,
      "remaining_debt": 24400.00
    },
    ...
  ],
  "milestones": [
    {"month": 8, "description": "First debt paid off", "debt_id": "uuid-2"},
    {"month": 12, "description": "50% debt reduction"}
  ]
}
```

---

### payments

**Purpose**: User-logged debt payments

**Fields**:
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    debt_id UUID NOT NULL REFERENCES debts(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES repayment_plans(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Payment Details
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_method VARCHAR(50), -- e.g., 'bank_transfer', 'credit_card', 'cash'
    
    -- Status
    confirmed BOOLEAN DEFAULT TRUE, -- For future: allow pending payments
    
    -- Impact Tracking (calculated at payment time)
    new_balance DECIMAL(12, 2) NOT NULL, -- Balance after this payment
    interest_saved DECIMAL(10, 2), -- Interest saved vs minimum-only approach
    
    -- Notes
    notes TEXT
);

CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_debt_id ON payments(debt_id);
CREATE INDEX idx_payments_date ON payments(user_id, payment_date DESC);
CREATE INDEX idx_payments_created_at ON payments(created_at);
```

**Validation**:
- Amount must be > 0 (CHECK constraint)
- Payment date cannot be in future (validated in application layer)
- New balance must be ≥ 0 (validated in application layer)

**Performance Note**:
- Index on `(user_id, payment_date DESC)` optimizes dashboard query (recent payments)

---

### actions

**Purpose**: Daily/weekly actionable recommendations generated by agents

**Fields**:
```sql
CREATE TABLE actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES repayment_plans(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Action Details
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('payment', 'review', 'rest', 'milestone', 'nudge')),
    action_date DATE NOT NULL,
    description TEXT NOT NULL, -- e.g., "Pay $250 to Chase card today"
    
    -- Optional Payment Details (if action_type = 'payment')
    related_debt_id UUID REFERENCES debts(id) ON DELETE CASCADE,
    suggested_amount DECIMAL(10, 2),
    
    -- Status
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    
    -- Priority
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5) -- 1 = highest
);

CREATE INDEX idx_actions_user_date ON actions(user_id, action_date) WHERE completed = FALSE;
CREATE INDEX idx_actions_plan_id ON actions(plan_id);
```

**Validation**:
- Action date should be current date or near future (validated in application)
- Suggested amount must be > 0 if present

**Usage**:
- Dashboard queries: `SELECT * FROM actions WHERE user_id = ? AND action_date = CURRENT_DATE AND completed = FALSE ORDER BY priority`

---

### transactions

**Purpose**: Bank transaction data for spending analysis (optional, P4 user story)

**Fields**:
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Transaction Details
    transaction_date DATE NOT NULL,
    merchant VARCHAR(255),
    amount DECIMAL(10, 2) NOT NULL,
    description TEXT,
    
    -- Categorization
    category VARCHAR(50), -- 'subscriptions', 'dining', 'groceries', 'entertainment', etc.
    subcategory VARCHAR(50),
    is_leak BOOLEAN DEFAULT FALSE, -- Flagged by agent as spending leak
    
    -- Metadata
    auto_categorized BOOLEAN DEFAULT TRUE, -- True if ML categorized, False if user corrected
    source VARCHAR(50) DEFAULT 'csv_upload' -- 'plaid', 'csv_upload'
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date DESC);
CREATE INDEX idx_transactions_category ON transactions(user_id, category) WHERE is_leak = TRUE;
```

**Validation**:
- Amount must be > 0 (spending transactions)
- Category validated against predefined list (application layer)

**Privacy Note**:
- Transactions deleted after 90 days (application-level job) to minimize PII retention

---

### insights

**Purpose**: Aggregated spending insights and leak detection results

**Fields**:
```sql
CREATE TABLE insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Analysis Period
    analysis_start_date DATE NOT NULL,
    analysis_end_date DATE NOT NULL,
    
    -- Findings
    top_categories JSONB NOT NULL, -- [{"category": "dining", "monthly_avg": 320.00, "percentage": 15}, ...]
    identified_leaks JSONB NOT NULL, -- [{"type": "subscription", "name": "Netflix", "monthly_cost": 15.99, "suggestion": "..."}, ...]
    total_leak_amount DECIMAL(10, 2) NOT NULL, -- Total monthly savings if leaks eliminated
    
    -- Impact on Debt
    months_saved_if_applied DECIMAL(4, 1), -- How many months faster if leaks eliminated
    
    -- Metadata
    transaction_count INTEGER NOT NULL,
    agent_confidence DECIMAL(3, 2) CHECK (agent_confidence BETWEEN 0 AND 1) -- 0.0-1.0 (Opik quality score)
);

CREATE INDEX idx_insights_user_id ON insights(user_id);
CREATE INDEX idx_insights_created_at ON insights(created_at DESC);
```

**Top Categories JSONB Example**:
```json
{
  "categories": [
    {"name": "dining", "monthly_avg": 320.00, "percentage": 15.2, "transaction_count": 42},
    {"name": "subscriptions", "monthly_avg": 180.00, "percentage": 8.5, "transaction_count": 8},
    ...
  ]
}
```

**Identified Leaks JSONB Example**:
```json
{
  "leaks": [
    {
      "type": "duplicate_subscription",
      "name": "Netflix",
      "monthly_cost": 15.99,
      "suggestion": "Cancel duplicate Netflix subscription charged to 2 cards"
    },
    {
      "type": "excessive_spending",
      "category": "dining",
      "monthly_avg": 320.00,
      "market_avg": 150.00,
      "suggestion": "Reduce dining out by 50% to save $160/month"
    }
  ]
}
```

---

### milestones

**Purpose**: Achievement tracking and gamification

**Fields**:
```sql
CREATE TABLE milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Milestone Details
    milestone_type VARCHAR(50) NOT NULL CHECK (milestone_type IN ('debt_paid_off', 'percentage_milestone', 'consistency_streak', 'negotiation_success', 'savings_milestone')),
    title VARCHAR(255) NOT NULL, -- e.g., "First Victory!", "50% Debt-Free"
    description TEXT NOT NULL,
    
    -- Related Data
    related_debt_id UUID REFERENCES debts(id) ON DELETE SET NULL,
    achievement_value DECIMAL(10, 2), -- e.g., amount paid off, percentage completed
    
    -- Celebration
    badge_name VARCHAR(100), -- e.g., "First Victory", "Consistency Champion"
    celebration_shown BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    achieved_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_milestones_user_id ON milestones(user_id);
CREATE INDEX idx_milestones_type ON milestones(user_id, milestone_type);
CREATE INDEX idx_milestones_achieved_at ON milestones(achieved_at DESC);
```

**Milestone Types**:
- `debt_paid_off`: User completely paid off a specific debt
- `percentage_milestone`: 25%, 50%, 75% of total debt eliminated
- `consistency_streak`: 3, 6, 12 months of consistent payments
- `negotiation_success`: Successfully negotiated lower interest rate
- `savings_milestone`: Saved $500, $1000, $2000 in interest vs minimum payments

---

### reminders

**Purpose**: Scheduled notifications and nudges

**Fields**:
```sql
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Reminder Details
    reminder_type VARCHAR(50) NOT NULL CHECK (reminder_type IN ('payment_due', 'progress_check', 're_engagement', 'milestone_upcoming', 'custom')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    
    -- Scheduling
    scheduled_for TIMESTAMPTZ NOT NULL,
    sent_at TIMESTAMPTZ,
    
    -- Status
    is_sent BOOLEAN DEFAULT FALSE,
    is_read BOOLEAN DEFAULT FALSE,
    
    -- Related Data
    related_debt_id UUID REFERENCES debts(id) ON DELETE CASCADE,
    related_action_id UUID REFERENCES actions(id) ON DELETE CASCADE
);

CREATE INDEX idx_reminders_user_scheduled ON reminders(user_id, scheduled_for) WHERE is_sent = FALSE;
CREATE INDEX idx_reminders_sent ON reminders(sent_at DESC);
```

**Reminder Scheduling Strategy**:
- Background job (Supabase Edge Function or backend cron) checks `reminders` table every hour
- Sends reminders where `scheduled_for <= NOW()` and `is_sent = FALSE`
- Marks `is_sent = TRUE` and sets `sent_at` after sending

---

### negotiation_scripts

**Purpose**: Personalized creditor negotiation scripts and Vapi session tracking

**Fields**:
```sql
CREATE TABLE negotiation_scripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    debt_id UUID NOT NULL REFERENCES debts(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Script Details
    script_text TEXT NOT NULL, -- Full negotiation script generated by agent
    talking_points JSONB NOT NULL, -- [{"point": "Loyal customer for 5 years"}, {"point": "Strong payment history"}, ...]
    success_probability DECIMAL(3, 2) CHECK (success_probability BETWEEN 0 AND 1), -- 0.0-1.0 (agent's confidence)
    
    -- Vapi Integration (P5 user story)
    vapi_session_id VARCHAR(255), -- Vapi.ai session ID for voice simulation
    vapi_session_status VARCHAR(50), -- 'pending', 'completed', 'failed'
    practice_count INTEGER DEFAULT 0, -- Number of times user practiced
    
    -- Outcome Tracking
    attempted BOOLEAN DEFAULT FALSE,
    attempt_date DATE,
    success BOOLEAN,
    old_interest_rate DECIMAL(5, 2),
    new_interest_rate DECIMAL(5, 2),
    outcome_notes TEXT
);

CREATE INDEX idx_negotiation_user_id ON negotiation_scripts(user_id);
CREATE INDEX idx_negotiation_debt_id ON negotiation_scripts(debt_id);
CREATE INDEX idx_negotiation_vapi ON negotiation_scripts(vapi_session_id) WHERE vapi_session_id IS NOT NULL;
```

**Talking Points JSONB Example**:
```json
{
  "points": [
    {"key": "loyalty", "text": "I've been a loyal customer for 5 years"},
    {"key": "payment_history", "text": "I have 85% on-time payment history"},
    {"key": "competitive_offer", "text": "I've received 15% APR offers from competitors"},
    {"key": "commitment", "text": "I'm committed to paying off this balance faster with a lower rate"}
  ],
  "optimal_timing": "Call 2-3 days after your next on-time payment",
  "confidence_factors": ["account_age > 3 years", "payment_history > 80%"]
}
```

---

## Encryption Implementation

### Client-Side Encryption (Frontend)

**Key Derivation**:
```typescript
// utils/encryption.ts
import { AES, enc, PBKDF2 } from 'crypto-js';

function deriveKey(password: string, salt: string): string {
  return PBKDF2(password, salt, {
    keySize: 256 / 32,
    iterations: 100000
  }).toString();
}

function encryptValue(value: number, userKey: string): string {
  const encrypted = AES.encrypt(value.toString(), userKey).toString();
  return encrypted;
}

function decryptValue(encrypted: string, userKey: string): number {
  const decrypted = AES.decrypt(encrypted, userKey).toString(enc.Utf8);
  return parseFloat(decrypted);
}
```

**Usage Flow**:
1. User signs up → Frontend generates random salt, derives key from password
2. User enters income/debt → Frontend encrypts with user key before sending to backend
3. Backend receives encrypted value → Re-encrypts with app-level key (Fernet or similar) → Stores in DB
4. On read: Backend decrypts with app key → Returns to frontend → Frontend decrypts with user key

**Rationale**: Even if DB breached, attacker needs both app key (stored in backend env vars) AND user password (never stored) to decrypt data.

### Server-Side Encryption (Backend)

**Implementation**:
```python
# app/services/encryption_service.py
from cryptography.fernet import Fernet
import os

class EncryptionService:
    def __init__(self):
        self.app_key = os.getenv("APP_ENCRYPTION_KEY").encode()  # 32-byte key
        self.fernet = Fernet(self.app_key)
    
    def encrypt(self, client_encrypted: str) -> str:
        """Re-encrypt client-encrypted data with app key"""
        return self.fernet.encrypt(client_encrypted.encode()).decode()
    
    def decrypt(self, db_value: str) -> str:
        """Decrypt to get client-encrypted value (frontend decrypts further)"""
        return self.fernet.decrypt(db_value.encode()).decode()
```

**Key Management**:
- App encryption key stored in Render/Railway environment variables
- Key rotation: Generate new key → decrypt all data with old key → re-encrypt with new key → update env var (offline operation, run migration script)

---

## Indexes for Performance

**Critical Indexes** (aligned with constitution performance standards):

```sql
-- Users
CREATE INDEX idx_users_email ON users(email); -- Login queries
CREATE INDEX idx_users_created_at ON users(created_at); -- Analytics

-- Debts
CREATE INDEX idx_debts_user_id ON debts(user_id); -- List user's debts
CREATE INDEX idx_debts_user_active ON debts(user_id, is_active) WHERE is_active = TRUE; -- Active debts only
CREATE INDEX idx_debts_due_date ON debts(user_id, due_date_day) WHERE is_active = TRUE; -- Upcoming payments

-- Payments
CREATE INDEX idx_payments_user_id ON payments(user_id); -- User's payment history
CREATE INDEX idx_payments_debt_id ON payments(debt_id); -- Debt-specific payments
CREATE INDEX idx_payments_date ON payments(user_id, payment_date DESC); -- Dashboard recent payments

-- Actions
CREATE INDEX idx_actions_user_date ON actions(user_id, action_date) WHERE completed = FALSE; -- Daily actions query

-- Transactions
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date DESC); -- Recent transactions

-- Milestones
CREATE INDEX idx_milestones_user_id ON milestones(user_id); -- User's achievements

-- Reminders
CREATE INDEX idx_reminders_user_scheduled ON reminders(user_id, scheduled_for) WHERE is_sent = FALSE; -- Pending reminders
```

**Query Performance Targets**:
- User dashboard (debts + plan + actions + milestones): <200ms (single query via Supabase RPC)
- Debt list for user: <50ms (indexed on `user_id`)
- Payment logging + recalculation trigger: <500ms total (spec PERF-002)

---

## Row-Level Security (RLS) Policies

**Supabase RLS Configuration** (meets SEC-005: user isolation):

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE debts ENABLE ROW LEVEL SECURITY;
ALTER TABLE repayment_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE negotiation_scripts ENABLE ROW LEVEL SECURITY;

-- Users: Can only read/update their own record
CREATE POLICY users_select ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY users_update ON users FOR UPDATE USING (auth.uid() = id);

-- Debts: Users can CRUD their own debts
CREATE POLICY debts_select ON debts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY debts_insert ON debts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY debts_update ON debts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY debts_delete ON debts FOR DELETE USING (auth.uid() = user_id);

-- (Repeat similar policies for all other tables with user_id foreign key)
```

**Rationale**: RLS ensures user A cannot query user B's data even with direct SQL access (defense in depth).

---

## Migration Strategy

**Initial Schema Deployment**:
1. Create all tables in order (respecting foreign key dependencies): `users` → `debts` → `repayment_plans` → `payments` → ...
2. Create indexes after table creation (faster bulk inserts if seeding test data)
3. Enable RLS policies last (after testing without RLS)

**Migration Files** (in `backend/app/db/migrations/`):
- `001_init.sql`: Core tables (users, debts, plans, payments, actions)
- `002_transactions.sql`: Transaction tracking (optional, P4)
- `003_indexes.sql`: All performance indexes
- `004_rls.sql`: Row-level security policies

**Tooling**: Use Supabase CLI (`supabase migration new <name>`) or manual SQL files applied via Supabase dashboard.

---

## Data Retention & Privacy

**Compliance with SEC-006, SEC-007**:

**Uploaded Documents**:
- Stored in Supabase Storage with 24-hour TTL (auto-delete via bucket policy)
- After OCR extraction, original file deleted immediately
- Only extracted data (balance, APR, etc.) retained in `debts` table

**User Data Export** (CCPA/GDPR compliance):
```sql
-- Export endpoint generates JSON with all user data
SELECT 
  u.*, 
  array_agg(d.*) as debts,
  array_agg(p.*) as payments,
  array_agg(t.*) as transactions
FROM users u
LEFT JOIN debts d ON d.user_id = u.id
LEFT JOIN payments p ON p.user_id = u.id
LEFT JOIN transactions t ON t.user_id = u.id
WHERE u.id = <user_id>
GROUP BY u.id;
```

**User Data Deletion** (Right to be Forgotten):
```sql
-- Cascade deletes handle all related data
DELETE FROM users WHERE id = <user_id>; 
-- Triggers cascade delete on debts, payments, plans, actions, transactions, insights, milestones, reminders, negotiation_scripts
```

**Transaction Retention**:
- Transactions older than 90 days automatically deleted (background job)
- Aggregated insights retained (no PII in aggregates)

---

## Testing Data Models

**Unit Tests** (pytest):
```python
# tests/unit/test_encryption.py
def test_encrypt_decrypt_roundtrip():
    service = EncryptionService()
    original = "123.45"
    encrypted = service.encrypt(original)
    decrypted = service.decrypt(encrypted)
    assert decrypted == original

# tests/unit/test_debt_validation.py
def test_debt_balance_must_be_positive():
    with pytest.raises(ValidationError):
        DebtCreate(balance=-100, interest_rate=15, ...)
```

**Integration Tests** (Supabase test database):
```python
# tests/integration/test_rls.py
async def test_user_cannot_access_other_users_debts(supabase_client):
    # User A creates debt
    debt_a = await debt_repo.create(user_id=user_a_id, ...)
    
    # User B tries to access User A's debt
    with pytest.raises(PermissionError):
        await debt_repo.get(debt_id=debt_a.id, user_id=user_b_id)
```

---

## Summary

**Total Tables**: 10 core tables + potential future additions (e.g., `notifications`, `audit_logs`)

**Encryption Coverage**: All sensitive financial data (income, balances, interest rates, minimum payments) encrypted with dual-layer approach

**Performance Optimization**: 20+ indexes targeting critical queries (dashboard, payment logging, action retrieval)

**Security**: Row-level security policies enforce user isolation, compliance with SEC-005

**Compliance**: Data export/deletion endpoints for CCPA/GDPR, document auto-deletion for SEC-006

**Validation**: Application-layer validation (Pydantic models) + database constraints (CHECK, UNIQUE, NOT NULL) provide defense in depth

This data model supports all 6 user stories (P1-P6) with room for extension (e.g., household accounts, budgeting features in future phases).
