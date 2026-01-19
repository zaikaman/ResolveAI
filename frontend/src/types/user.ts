/**
 * User types aligned with backend models
 */

export type RepaymentStrategy = 'avalanche' | 'snowball';
export type NotificationFrequency = 'daily' | 'weekly' | 'custom';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  timezone: string;
  language: string;
  repayment_strategy: RepaymentStrategy;
  notification_enabled: boolean;
  notification_frequency: NotificationFrequency;
  onboarding_completed: boolean;
  created_at: string;
}

export interface UserUpdate {
  full_name?: string;
  timezone?: string;
  language?: string;
  monthly_income_encrypted?: string;
  monthly_expenses_encrypted?: string;
  available_for_debt_encrypted?: string;
  repayment_strategy?: RepaymentStrategy;
  notification_enabled?: boolean;
  notification_time?: string;
  notification_frequency?: NotificationFrequency;
}

export interface OnboardingData {
  monthly_income: number;
  monthly_expenses: number;
  available_for_debt: number;
  terms_accepted: boolean;
}
