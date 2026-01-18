-- ResolveAI Debt Freedom Coach - Performance Indexes Migration
-- Created: 2026-01-18
-- Description: Critical indexes for <200ms query performance

-- ==============================================================================
-- USERS INDEXES
-- ==============================================================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ==============================================================================
-- DEBTS INDEXES
-- ==============================================================================
CREATE INDEX idx_debts_user_id ON debts(user_id);
CREATE INDEX idx_debts_user_active ON debts(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_debts_due_date ON debts(user_id, due_date_day) WHERE is_active = TRUE;

-- ==============================================================================
-- REPAYMENT PLANS INDEXES
-- ==============================================================================
CREATE INDEX idx_plans_user_id ON repayment_plans(user_id);
CREATE UNIQUE INDEX idx_plans_active_user ON repayment_plans(user_id) WHERE is_active = TRUE;
CREATE INDEX idx_plans_created_at ON repayment_plans(created_at);

-- ==============================================================================
-- PAYMENTS INDEXES
-- ==============================================================================
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_debt_id ON payments(debt_id);
CREATE INDEX idx_payments_date ON payments(user_id, payment_date DESC);
CREATE INDEX idx_payments_created_at ON payments(created_at);

-- ==============================================================================
-- ACTIONS INDEXES
-- ==============================================================================
CREATE INDEX idx_actions_user_date ON actions(user_id, action_date) WHERE completed = FALSE;
CREATE INDEX idx_actions_plan_id ON actions(plan_id);

-- ==============================================================================
-- TRANSACTIONS INDEXES
-- ==============================================================================
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date DESC);
CREATE INDEX idx_transactions_category ON transactions(user_id, category) WHERE is_leak = TRUE;

-- ==============================================================================
-- INSIGHTS INDEXES
-- ==============================================================================
CREATE INDEX idx_insights_user_id ON insights(user_id);
CREATE INDEX idx_insights_created_at ON insights(created_at DESC);

-- ==============================================================================
-- MILESTONES INDEXES
-- ==============================================================================
CREATE INDEX idx_milestones_user_id ON milestones(user_id);
CREATE INDEX idx_milestones_type ON milestones(user_id, milestone_type);
CREATE INDEX idx_milestones_achieved_at ON milestones(achieved_at DESC);

-- ==============================================================================
-- REMINDERS INDEXES
-- ==============================================================================
CREATE INDEX idx_reminders_user_scheduled ON reminders(user_id, scheduled_for) WHERE is_sent = FALSE;
CREATE INDEX idx_reminders_sent ON reminders(sent_at DESC);

-- ==============================================================================
-- NEGOTIATION SCRIPTS INDEXES
-- ==============================================================================
CREATE INDEX idx_negotiation_user_id ON negotiation_scripts(user_id);
CREATE INDEX idx_negotiation_debt_id ON negotiation_scripts(debt_id);
CREATE INDEX idx_negotiation_vapi ON negotiation_scripts(vapi_session_id) WHERE vapi_session_id IS NOT NULL;
