-- ResolveAI Debt Freedom Coach - Row-Level Security Migration
-- Created: 2026-01-18
-- Description: RLS policies for user data isolation (SEC-005 compliance)

-- ==============================================================================
-- ENABLE RLS ON ALL TABLES
-- ==============================================================================
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

-- ==============================================================================
-- USERS POLICIES
-- ==============================================================================
CREATE POLICY users_select ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY users_update ON users FOR UPDATE USING (auth.uid() = id);
CREATE POLICY users_insert ON users FOR INSERT WITH CHECK (auth.uid() = id);

-- ==============================================================================
-- DEBTS POLICIES
-- ==============================================================================
CREATE POLICY debts_select ON debts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY debts_insert ON debts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY debts_update ON debts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY debts_delete ON debts FOR DELETE USING (auth.uid() = user_id);

-- ==============================================================================
-- REPAYMENT PLANS POLICIES
-- ==============================================================================
CREATE POLICY plans_select ON repayment_plans FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY plans_insert ON repayment_plans FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY plans_update ON repayment_plans FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY plans_delete ON repayment_plans FOR DELETE USING (auth.uid() = user_id);

-- ==============================================================================
-- PAYMENTS POLICIES
-- ==============================================================================
CREATE POLICY payments_select ON payments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY payments_insert ON payments FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY payments_update ON payments FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY payments_delete ON payments FOR DELETE USING (auth.uid() = user_id);

-- ==============================================================================
-- ACTIONS POLICIES
-- ==============================================================================
CREATE POLICY actions_select ON actions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY actions_insert ON actions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY actions_update ON actions FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY actions_delete ON actions FOR DELETE USING (auth.uid() = user_id);

-- ==============================================================================
-- TRANSACTIONS POLICIES
-- ==============================================================================
CREATE POLICY transactions_select ON transactions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY transactions_insert ON transactions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY transactions_update ON transactions FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY transactions_delete ON transactions FOR DELETE USING (auth.uid() = user_id);

-- ==============================================================================
-- INSIGHTS POLICIES
-- ==============================================================================
CREATE POLICY insights_select ON insights FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY insights_insert ON insights FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY insights_update ON insights FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY insights_delete ON insights FOR DELETE USING (auth.uid() = user_id);

-- ==============================================================================
-- MILESTONES POLICIES
-- ==============================================================================
CREATE POLICY milestones_select ON milestones FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY milestones_insert ON milestones FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY milestones_update ON milestones FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY milestones_delete ON milestones FOR DELETE USING (auth.uid() = user_id);

-- ==============================================================================
-- REMINDERS POLICIES
-- ==============================================================================
CREATE POLICY reminders_select ON reminders FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY reminders_insert ON reminders FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY reminders_update ON reminders FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY reminders_delete ON reminders FOR DELETE USING (auth.uid() = user_id);

-- ==============================================================================
-- NEGOTIATION SCRIPTS POLICIES
-- ==============================================================================
CREATE POLICY negotiation_select ON negotiation_scripts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY negotiation_insert ON negotiation_scripts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY negotiation_update ON negotiation_scripts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY negotiation_delete ON negotiation_scripts FOR DELETE USING (auth.uid() = user_id);
