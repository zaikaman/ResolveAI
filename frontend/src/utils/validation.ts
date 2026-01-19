/**
 * Zod validation schemas for forms
 */

import { z } from 'zod';
import { VALIDATION } from './constants';

// User profile validation
export const userUpdateSchema = z.object({
  full_name: z.string().min(1, 'Full name is required').max(255, 'Name too long').optional(),
  timezone: z.string().regex(/^[A-Za-z_]+\/[A-Za-z_]+$/, 'Invalid timezone').optional(),
  language: z.string().regex(/^[a-z]{2}$/, 'Invalid language code').optional(),
  repayment_strategy: z.enum(['avalanche', 'snowball']).optional(),
  notification_enabled: z.boolean().optional(),
  notification_time: z.string().regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/, 'Invalid time format').optional(),
  notification_frequency: z.enum(['daily', 'weekly', 'custom']).optional(),
});

// Onboarding validation (plaintext, server encrypts)
export const onboardingSchema = z.object({
  monthly_income: z.number().min(0.01, 'Monthly income is required'),
  monthly_expenses: z.number().min(0, 'Monthly expenses are required'),
  available_for_debt: z.number().min(0.01, 'Available amount is required'),
  terms_accepted: z.literal(true, {
    errorMap: () => ({ message: 'You must accept the terms and conditions' }),
  }),
});

// Financial data validation (before encryption)
export const financialDataSchema = z.object({
  monthly_income: z.number()
    .min(VALIDATION.BALANCE_MIN, 'Income must be 0 or greater')
    .finite('Income must be a valid number'),
  monthly_expenses: z.number()
    .min(VALIDATION.BALANCE_MIN, 'Expenses must be 0 or greater')
    .finite('Expenses must be a valid number'),
  available_for_debt: z.number()
    .min(VALIDATION.BALANCE_MIN, 'Available amount must be 0 or greater')
    .finite('Available amount must be a valid number'),
}).refine(
  (data) => data.available_for_debt <= (data.monthly_income - data.monthly_expenses),
  {
    message: 'Available for debt cannot exceed income minus expenses',
    path: ['available_for_debt'],
  }
);

// Debt validation
export const debtSchema = z.object({
  creditor_name: z.string()
    .min(1, 'Creditor name is required')
    .max(VALIDATION.CREDITOR_NAME_MAX_LENGTH, 'Creditor name too long'),
  debt_type: z.enum([
    'credit_card',
    'personal_loan',
    'mortgage',
    'auto_loan',
    'student_loan',
    'business_loan',
    'informal',
    'other',
  ]),
  current_balance: z.number()
    .min(0.01, 'Balance must be greater than 0')
    .finite('Balance must be a valid number'),
  apr: z.number()
    .min(VALIDATION.APR_MIN, `APR must be between ${VALIDATION.APR_MIN}% and ${VALIDATION.APR_MAX}%`)
    .max(VALIDATION.APR_MAX, `APR must be between ${VALIDATION.APR_MIN}% and ${VALIDATION.APR_MAX}%`)
    .finite('APR must be a valid number'),
  minimum_payment: z.number()
    .min(VALIDATION.PAYMENT_AMOUNT_MIN, 'Minimum payment must be 0 or greater')
    .finite('Minimum payment must be a valid number')
    .optional(),
});

// Payment validation
export const paymentSchema = z.object({
  debt_id: z.string().uuid('Invalid debt ID'),
  amount: z.number()
    .min(0.01, 'Payment amount must be greater than 0')
    .finite('Amount must be a valid number'),
  payment_date: z.date().optional(),
  notes: z.string().max(500, 'Notes too long').optional(),
});

export type UserUpdateInput = z.infer<typeof userUpdateSchema>;
export type OnboardingInput = z.infer<typeof onboardingSchema>;
export type FinancialDataInput = z.infer<typeof financialDataSchema>;
export type DebtInput = z.infer<typeof debtSchema>;
export type PaymentInput = z.infer<typeof paymentSchema>;
