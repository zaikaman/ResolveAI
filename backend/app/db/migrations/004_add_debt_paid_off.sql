-- Migration: Add is_paid_off and paid_off_at columns to debts table
-- Created: 2026-01-19
-- Description: Add columns to track when debts are fully paid off

ALTER TABLE debts 
ADD COLUMN IF NOT EXISTS is_paid_off BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS paid_off_at TIMESTAMPTZ;

-- Add comments
COMMENT ON COLUMN debts.is_paid_off IS 'Whether this debt has been fully paid off';
COMMENT ON COLUMN debts.paid_off_at IS 'Timestamp when the debt was marked as paid off';
