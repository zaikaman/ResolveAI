-- ResolveAI Debt Freedom Coach - Initial Schema Migration
-- Created: 2026-01-18
-- Description: Core tables for users, debts, plans, payments, actions, transactions, insights, milestones, reminders, negotiation_scripts

-- ==============================================================================
-- USERS TABLE
-- ==============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Profile
    full_name VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'Asia/Ho_Chi_Minh',
    language VARCHAR(10) DEFAULT 'vi',
    
    -- Financial Context (encrypted at application level before storage)
    monthly_income_encrypted TEXT,
    monthly_expenses_encrypted TEXT,
    available_for_debt_encrypted TEXT,
    
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

-- ==============================================================================
-- DEBTS TABLE
-- ==============================================================================
CREATE TABLE debts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Debt Details
    creditor_name VARCHAR(255) NOT NULL,
    debt_type VARCHAR(50) NOT NULL CHECK (debt_type IN ('credit_card', 'personal_loan', 'student_loan', 'medical_bill', 'auto_loan', 'mortgage', 'other')),
    
    -- Financial Data (encrypted)
    current_balance_encrypted TEXT NOT NULL,
    original_balance_encrypted TEXT,
    interest_rate_encrypted TEXT NOT NULL,
    minimum_payment_encrypted TEXT NOT NULL,
    
    -- Dates
    due_date_day INTEGER CHECK (due_date_day BETWEEN 1 AND 31),
    account_opened_date DATE,
    
    -- Metadata
    payment_history_score DECIMAL(3, 2) CHECK (payment_history_score BETWEEN 0 AND 1),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT
);

-- ==============================================================================
-- REPAYMENT PLANS TABLE
-- ==============================================================================
CREATE TABLE repayment_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Plan Configuration
    strategy VARCHAR(20) NOT NULL CHECK (strategy IN ('avalanche', 'snowball')),
    target_debt_free_date DATE NOT NULL,
    
    -- Projections
    total_debt_amount DECIMAL(12, 2) NOT NULL,
    total_interest_projection DECIMAL(12, 2) NOT NULL,
    monthly_payment_total DECIMAL(10, 2) NOT NULL,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    completed_at TIMESTAMPTZ,
    
    -- Plan Details (JSONB for flexibility)
    payment_schedule JSONB NOT NULL,
    optimization_metadata JSONB
);

-- ==============================================================================
-- PAYMENTS TABLE
-- ==============================================================================
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    debt_id UUID NOT NULL REFERENCES debts(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES repayment_plans(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Payment Details
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_method VARCHAR(50),
    
    -- Status
    confirmed BOOLEAN DEFAULT TRUE,
    
    -- Impact Tracking
    new_balance DECIMAL(12, 2) NOT NULL,
    interest_saved DECIMAL(10, 2),
    
    -- Notes
    notes TEXT
);

-- ==============================================================================
-- ACTIONS TABLE
-- ==============================================================================
CREATE TABLE actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES repayment_plans(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Action Details
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('payment', 'review', 'rest', 'milestone', 'nudge')),
    action_date DATE NOT NULL,
    description TEXT NOT NULL,
    
    -- Optional Payment Details
    related_debt_id UUID REFERENCES debts(id) ON DELETE CASCADE,
    suggested_amount DECIMAL(10, 2),
    
    -- Status
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    
    -- Priority
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5)
);

-- ==============================================================================
-- TRANSACTIONS TABLE
-- ==============================================================================
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
    category VARCHAR(50),
    subcategory VARCHAR(50),
    is_leak BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    auto_categorized BOOLEAN DEFAULT TRUE,
    source VARCHAR(50) DEFAULT 'csv_upload'
);

-- ==============================================================================
-- INSIGHTS TABLE
-- ==============================================================================
CREATE TABLE insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Analysis Period
    analysis_start_date DATE NOT NULL,
    analysis_end_date DATE NOT NULL,
    
    -- Findings
    top_categories JSONB NOT NULL,
    identified_leaks JSONB NOT NULL,
    total_leak_amount DECIMAL(10, 2) NOT NULL,
    
    -- Impact on Debt
    months_saved_if_applied DECIMAL(4, 1),
    
    -- Metadata
    transaction_count INTEGER NOT NULL,
    agent_confidence DECIMAL(3, 2) CHECK (agent_confidence BETWEEN 0 AND 1)
);

-- ==============================================================================
-- MILESTONES TABLE
-- ==============================================================================
CREATE TABLE milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Milestone Details
    milestone_type VARCHAR(50) NOT NULL CHECK (milestone_type IN ('debt_paid_off', 'percentage_milestone', 'consistency_streak', 'negotiation_success', 'savings_milestone')),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    
    -- Related Data
    related_debt_id UUID REFERENCES debts(id) ON DELETE SET NULL,
    achievement_value DECIMAL(10, 2),
    
    -- Celebration
    badge_name VARCHAR(100),
    celebration_shown BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    achieved_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================================
-- REMINDERS TABLE
-- ==============================================================================
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

-- ==============================================================================
-- NEGOTIATION SCRIPTS TABLE
-- ==============================================================================
CREATE TABLE negotiation_scripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    debt_id UUID NOT NULL REFERENCES debts(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Script Details
    script_text TEXT NOT NULL,
    talking_points JSONB NOT NULL,
    success_probability DECIMAL(3, 2) CHECK (success_probability BETWEEN 0 AND 1),
    
    -- Vapi Integration
    vapi_session_id VARCHAR(255),
    vapi_session_status VARCHAR(50),
    practice_count INTEGER DEFAULT 0,
    
    -- Outcome Tracking
    attempted BOOLEAN DEFAULT FALSE,
    attempt_date DATE,
    success BOOLEAN,
    old_interest_rate DECIMAL(5, 2),
    new_interest_rate DECIMAL(5, 2),
    outcome_notes TEXT
);
