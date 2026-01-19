/**
 * Plan store using Zustand for state management
 */

import { create } from 'zustand';

export interface PaymentScheduleItem {
    month: number;
    date: string;
    debt_id: string;
    debt_name: string;
    payment_amount: number;
    principal: number;
    interest: number;
    remaining_balance: number;
    is_payoff_month: boolean;
}

export interface MonthlyBreakdown {
    month: number;
    date: string;
    total_payment: number;
    payments: PaymentScheduleItem[];
    total_remaining: number;
}

export interface PlanProjection {
    month: number;
    date: string;
    total_remaining: number;
    cumulative_interest_paid: number;
    cumulative_principal_paid: number;
}

export interface DebtPayoffInfo {
    debt_id: string;
    debt_name: string;
    payoff_month: number;
    payoff_date: string;
    total_interest_paid: number;
    total_paid: number;
}

export interface Plan {
    id: string;
    user_id: string;
    status: 'draft' | 'active' | 'completed' | 'archived';
    strategy: 'avalanche' | 'snowball';
    debt_free_date: string;
    total_months: number;
    total_interest: number;
    total_paid: number;
    interest_saved: number;
    months_saved: number;
    monthly_payment: number;
    extra_payment: number;
    monthly_schedule: MonthlyBreakdown[];
    projections: PlanProjection[];
    payoff_order: DebtPayoffInfo[];
    created_at: string;
    updated_at: string;
}

export interface PlanSummary {
    id: string;
    status: 'draft' | 'active' | 'completed' | 'archived';
    strategy: 'avalanche' | 'snowball';
    debt_free_date: string;
    total_months: number;
    months_remaining: number;
    progress_percentage: number;
    monthly_payment: number;
    next_payment_date?: string;
}

export interface SimulationResult {
    original_debt_free_date: string;
    original_total_interest: number;
    original_total_months: number;
    simulated_debt_free_date: string;
    simulated_total_interest: number;
    simulated_total_months: number;
    interest_difference: number;
    months_difference: number;
    projections: PlanProjection[];
}

interface PlanState {
    activePlan: Plan | null;
    planSummary: PlanSummary | null;
    simulationResult: SimulationResult | null;
    loading: boolean;
    generating: boolean;
    error: string | null;

    // Actions
    setActivePlan: (plan: Plan | null) => void;
    setPlanSummary: (summary: PlanSummary | null) => void;
    setSimulationResult: (result: SimulationResult | null) => void;
    setLoading: (loading: boolean) => void;
    setGenerating: (generating: boolean) => void;
    setError: (error: string | null) => void;
    reset: () => void;
}

const initialState = {
    activePlan: null,
    planSummary: null,
    simulationResult: null,
    loading: false,
    generating: false,
    error: null,
};

export const usePlanStore = create<PlanState>((set) => ({
    ...initialState,

    setActivePlan: (plan) => set({ activePlan: plan, error: null }),

    setPlanSummary: (summary) => set({ planSummary: summary }),

    setSimulationResult: (result) => set({ simulationResult: result }),

    setLoading: (loading) => set({ loading }),

    setGenerating: (generating) => set({ generating }),

    setError: (error) => set({ error, loading: false, generating: false }),

    reset: () => set(initialState),
}));
