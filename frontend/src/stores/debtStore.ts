/**
 * Debt store using Zustand for state management
 */

import { create } from 'zustand';

export interface Debt {
    id: string;
    user_id: string;
    creditor_name: string;
    debt_type: 'credit_card' | 'personal_loan' | 'student_loan' | 'mortgage' | 'auto_loan' | 'medical_bill' | 'other';
    balance_encrypted: string;
    apr_encrypted: string;
    minimum_payment_encrypted: string;
    account_number_last4?: string;
    due_date?: number;
    notes?: string;
    is_active: boolean;
    is_paid_off: boolean;
    paid_off_at?: string;
    created_at: string;
    updated_at: string;
}

export interface DebtSummary {
    total_debts: number;
    active_debts: number;
    paid_off_debts: number;
}

export interface DebtListResponse {
    debts: Debt[];
    summary: DebtSummary;
}

interface DebtState {
    debts: Debt[];
    summary: DebtSummary | null;
    loading: boolean;
    error: string | null;
    selectedDebt: Debt | null;

    // Actions
    setDebts: (debts: Debt[], summary: DebtSummary) => void;
    addDebt: (debt: Debt) => void;
    updateDebt: (debt: Debt) => void;
    removeDebt: (debtId: string) => void;
    setSelectedDebt: (debt: Debt | null) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
    reset: () => void;
}

const initialState = {
    debts: [],
    summary: null,
    loading: false,
    error: null,
    selectedDebt: null,
};

export const useDebtStore = create<DebtState>((set) => ({
    ...initialState,

    setDebts: (debts, summary) => set({ debts, summary, error: null }),

    addDebt: (debt) => set((state) => ({
        debts: [...state.debts, debt],
        summary: state.summary ? {
            ...state.summary,
            total_debts: state.summary.total_debts + 1,
            active_debts: debt.is_active && !debt.is_paid_off
                ? state.summary.active_debts + 1
                : state.summary.active_debts,
        } : null,
        error: null,
    })),

    updateDebt: (updatedDebt) => set((state) => ({
        debts: state.debts.map((d) => d.id === updatedDebt.id ? updatedDebt : d),
        selectedDebt: state.selectedDebt?.id === updatedDebt.id ? updatedDebt : state.selectedDebt,
        error: null,
    })),

    removeDebt: (debtId) => set((state) => {
        const debtToRemove = state.debts.find((d) => d.id === debtId);
        return {
            debts: state.debts.filter((d) => d.id !== debtId),
            summary: state.summary && debtToRemove ? {
                ...state.summary,
                total_debts: state.summary.total_debts - 1,
                active_debts: debtToRemove.is_active && !debtToRemove.is_paid_off
                    ? state.summary.active_debts - 1
                    : state.summary.active_debts,
                paid_off_debts: debtToRemove.is_paid_off
                    ? state.summary.paid_off_debts - 1
                    : state.summary.paid_off_debts,
            } : null,
            selectedDebt: state.selectedDebt?.id === debtId ? null : state.selectedDebt,
            error: null,
        };
    }),

    setSelectedDebt: (debt) => set({ selectedDebt: debt }),

    setLoading: (loading) => set({ loading }),

    setError: (error) => set({ error, loading: false }),

    reset: () => set(initialState),
}));
