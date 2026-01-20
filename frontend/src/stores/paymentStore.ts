/**
 * Payment store - Zustand store for payment state management
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import paymentService, {
    type Payment,
    type PaymentStats,
    type DailyActionsResponse,
    type RecentPaymentSummary,
    type MilestoneCheckResult,
    type LogPaymentRequest,
} from '../services/paymentService';

interface PaymentState {
    // Data
    payments: Payment[];
    stats: PaymentStats | null;
    dailyActions: DailyActionsResponse | null;
    summary: RecentPaymentSummary | null;
    milestones: MilestoneCheckResult | null;
    
    // UI State
    loading: boolean;
    error: string | null;
    
    // Actions
    fetchPayments: (days?: number, limit?: number) => Promise<void>;
    fetchStats: () => Promise<void>;
    fetchDailyActions: () => Promise<void>;
    fetchSummary: () => Promise<void>;
    fetchMilestones: () => Promise<void>;
    fetchAll: () => Promise<void>;
    logPayment: (data: LogPaymentRequest) => Promise<Payment>;
    clearError: () => void;
    reset: () => void;
}

const initialState = {
    payments: [],
    stats: null,
    dailyActions: null,
    summary: null,
    milestones: null,
    loading: false,
    error: null,
};

export const usePaymentStore = create<PaymentState>()(
    devtools(
        (set, get) => ({
            ...initialState,

            fetchPayments: async (days = 90, limit = 50) => {
                set({ loading: true, error: null });
                try {
                    const payments = await paymentService.getRecentPayments(days, limit);
                    set({ payments, loading: false });
                } catch (error) {
                    const message = error instanceof Error ? error.message : 'Failed to fetch payments';
                    set({ error: message, loading: false });
                    throw error;
                }
            },

            fetchStats: async () => {
                set({ loading: true, error: null });
                try {
                    const stats = await paymentService.getPaymentStats();
                    set({ stats, loading: false });
                } catch (error) {
                    const message = error instanceof Error ? error.message : 'Failed to fetch stats';
                    set({ error: message, loading: false });
                    throw error;
                }
            },

            fetchDailyActions: async () => {
                set({ loading: true, error: null });
                try {
                    const dailyActions = await paymentService.getDailyActions();
                    set({ dailyActions, loading: false });
                } catch (error) {
                    const message = error instanceof Error ? error.message : 'Failed to fetch daily actions';
                    set({ error: message, loading: false });
                    throw error;
                }
            },

            fetchSummary: async () => {
                set({ loading: true, error: null });
                try {
                    const summary = await paymentService.getPaymentSummary();
                    set({ summary, loading: false });
                } catch (error) {
                    const message = error instanceof Error ? error.message : 'Failed to fetch summary';
                    set({ error: message, loading: false });
                    throw error;
                }
            },

            fetchMilestones: async () => {
                set({ loading: true, error: null });
                try {
                    const milestones = await paymentService.checkMilestones();
                    set({ milestones, loading: false });
                } catch (error) {
                    const message = error instanceof Error ? error.message : 'Failed to fetch milestones';
                    set({ error: message, loading: false });
                    throw error;
                }
            },

            fetchAll: async () => {
                set({ loading: true, error: null });
                try {
                    const [payments, stats, dailyActions, summary] = await Promise.all([
                        paymentService.getRecentPayments(90, 50).catch(() => []),
                        paymentService.getPaymentStats().catch(() => null),
                        paymentService.getDailyActions().catch(() => null),
                        paymentService.getPaymentSummary().catch(() => null),
                    ]);
                    
                    set({
                        payments: payments || [],
                        stats,
                        dailyActions,
                        summary,
                        loading: false,
                    });
                } catch (error) {
                    const message = error instanceof Error ? error.message : 'Failed to fetch data';
                    set({ error: message, loading: false });
                    throw error;
                }
            },

            logPayment: async (data: LogPaymentRequest) => {
                set({ loading: true, error: null });
                try {
                    const payment = await paymentService.logPayment(data);
                    
                    // Add to payments list
                    const currentPayments = get().payments;
                    set({ 
                        payments: [payment, ...currentPayments],
                        loading: false 
                    });

                    // Check for milestones after payment
                    try {
                        const milestones = await paymentService.checkMilestones();
                        set({ milestones });
                    } catch {
                        // Milestone check is optional
                    }

                    // Refresh stats
                    try {
                        const stats = await paymentService.getPaymentStats();
                        set({ stats });
                    } catch {
                        // Stats refresh is optional
                    }

                    return payment;
                } catch (error) {
                    const message = error instanceof Error ? error.message : 'Failed to log payment';
                    set({ error: message, loading: false });
                    throw error;
                }
            },

            clearError: () => set({ error: null }),

            reset: () => set(initialState),
        }),
        { name: 'payment-store' }
    )
);
