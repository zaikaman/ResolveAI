/**
 * usePayments hook - Custom hook for payment operations
 */

import { useCallback, useEffect } from 'react';
import { usePaymentStore } from '../stores/paymentStore';
import type { LogPaymentRequest } from '../services/paymentService';

interface UsePaymentsOptions {
    autoFetch?: boolean;
    days?: number;
    limit?: number;
}

export function usePayments(options: UsePaymentsOptions = {}) {
    const {
        autoFetch = true,
        days = 90,
        limit = 50,
    } = options;

    const {
        payments,
        stats,
        dailyActions,
        summary,
        milestones,
        loading,
        error,
        fetchPayments,
        fetchStats,
        fetchDailyActions,
        fetchSummary,
        fetchMilestones,
        fetchAll,
        logPayment: storeLogPayment,
        clearError,
        reset,
    } = usePaymentStore();

    // Auto-fetch on mount if enabled
    useEffect(() => {
        if (autoFetch) {
            fetchAll().catch(console.error);
        }
    }, [autoFetch, fetchAll]);

    // Wrapped fetch with custom days/limit
    const refreshPayments = useCallback(async () => {
        await fetchPayments(days, limit);
    }, [fetchPayments, days, limit]);

    // Log payment and refresh data
    const logPayment = useCallback(async (data: LogPaymentRequest) => {
        const payment = await storeLogPayment(data);
        return payment;
    }, [storeLogPayment]);

    // Refresh all data
    const refreshAll = useCallback(async () => {
        await fetchAll();
    }, [fetchAll]);

    // Calculate derived values
    const totalPaid = stats?.total_amount_paid || 0;
    const paymentCount = stats?.total_payments || 0;
    const monthlyAverage = stats?.average_payment_amount || 0;
    const streakDays = stats?.current_streak_days || 0;

    // Get priority actions (high priority only - 1 or 2)
    const priorityActions = dailyActions?.actions?.filter(
        (action) => action.priority <= 2
    ) || [];

    // Check if there are new milestones to celebrate
    const hasNewMilestones = milestones?.has_new_milestones || false;

    // Get recent payments (last 5)
    const recentPayments = payments.slice(0, 5);

    return {
        // Data
        payments,
        stats,
        dailyActions,
        summary,
        milestones,
        
        // Derived values
        totalPaid,
        paymentCount,
        monthlyAverage,
        streakDays,
        priorityActions,
        hasNewMilestones,
        recentPayments,
        
        // State
        loading,
        error,
        
        // Actions
        logPayment,
        refreshPayments,
        refreshAll,
        fetchStats,
        fetchDailyActions,
        fetchSummary,
        fetchMilestones,
        clearError,
        reset,
    };
}
