/**
 * Payment API service for payment logging and tracking
 */

import api from './api';

// Types
export interface PaymentMethod {
    type: 'bank_transfer' | 'check' | 'cash' | 'debit_card' | 'credit_card' | 'auto_pay' | 'other';
}

export interface PaymentCreate {
    debt_id: string;
    amount: number;
    payment_date?: string;
    payment_method?: string;
    notes?: string;
    new_balance?: number;
}

export interface PaymentUpdate {
    amount?: number;
    payment_date?: string;
    payment_method?: string;
    notes?: string;
    confirmed?: boolean;
}

export interface Payment {
    id: string;
    user_id: string;
    debt_id: string;
    plan_id?: string;
    amount: number;
    payment_date: string;
    payment_method?: string;
    confirmed: boolean;
    new_balance: number;
    interest_saved?: number;
    notes?: string;
    created_at: string;
    debt_name?: string;
}

export interface PaymentListResponse {
    payments: Payment[];
    total_count: number;
    total_amount: number;
}

export interface PaymentStats {
    total_payments: number;
    total_amount_paid: number;
    total_interest_saved: number;
    payments_this_month: number;
    amount_this_month: number;
    payments_last_30_days: number;
    amount_last_30_days: number;
    current_streak_days: number;
    longest_streak_days: number;
    on_track_percentage: number;
    average_payment_amount: number;
    payments_by_debt?: Record<string, number>;
}

export interface RecentPaymentSummary {
    last_payment_date?: string;
    last_payment_amount?: number;
    last_payment_debt_name?: string;
    payments_this_week: number;
    amount_this_week: number;
    total_principal_paid: number;
    total_interest_paid: number;
    current_streak: number;
    is_on_streak: boolean;
}

export interface MilestoneType {
    type: 'debt_paid_off' | 'percentage_milestone' | 'consistency_streak' | 'negotiation_success' | 'savings_milestone' | 'first_payment' | 'monthly_goal';
}

export interface Milestone {
    milestone_type: string;
    title: string;
    description: string;
    badge_name?: string;
    achievement_value?: number;
    related_debt_id?: string;
    related_debt_name?: string;
    celebration_message: string;
    interest_saved?: number;
    achieved_at: string;
}

export interface MilestoneCheckResult {
    milestones: Milestone[];
    has_new_milestones: boolean;
    celebration_priority: number;
}

export interface PaymentWithMilestones extends Payment {
    milestones?: MilestoneCheckResult;
}

// Daily Actions Types
export interface DailyAction {
    action_type: 'payment' | 'review' | 'rest' | 'milestone' | 'nudge';
    priority: 1 | 2 | 3 | 4 | 5;
    title: string;
    description: string;
    suggested_amount?: number;
    debt_id?: string;
    debt_name?: string;
    due_date?: string;
    is_overdue: boolean;
    motivational_message?: string;
}

export interface DailyActionsResponse {
    actions: DailyAction[];
    date: string;
    summary: string;
    progress_message?: string;
    streak_message?: string;
}

class PaymentService {
    /**
     * Log a new payment
     */
    async logPayment(data: PaymentCreate): Promise<PaymentWithMilestones> {
        const response = await api.post<PaymentWithMilestones>('/payments', data);
        return response.data;
    }

    /**
     * Get all payments with optional filters
     */
    async getPayments(options?: {
        debt_id?: string;
        limit?: number;
        start_date?: string;
        end_date?: string;
    }): Promise<PaymentListResponse> {
        const params = new URLSearchParams();
        if (options?.debt_id) params.append('debt_id', options.debt_id);
        if (options?.limit) params.append('limit', options.limit.toString());
        if (options?.start_date) params.append('start_date', options.start_date);
        if (options?.end_date) params.append('end_date', options.end_date);

        const response = await api.get<PaymentListResponse>(`/payments?${params.toString()}`);
        return response.data;
    }

    /**
     * Get recent payments
     */
    async getRecentPayments(days: number = 30, limit: number = 10): Promise<Payment[]> {
        const response = await api.get<Payment[]>(`/payments/recent?days=${days}&limit=${limit}`);
        return response.data;
    }

    /**
     * Get payment statistics
     */
    async getPaymentStats(): Promise<PaymentStats> {
        const response = await api.get<PaymentStats>('/payments/stats');
        return response.data;
    }

    /**
     * Get recent payment summary for dashboard
     */
    async getPaymentSummary(): Promise<RecentPaymentSummary> {
        const response = await api.get<RecentPaymentSummary>('/payments/summary');
        return response.data;
    }

    /**
     * Get a single payment by ID
     */
    async getPayment(paymentId: string): Promise<Payment> {
        const response = await api.get<Payment>(`/payments/${paymentId}`);
        return response.data;
    }

    /**
     * Update a payment
     */
    async updatePayment(paymentId: string, data: PaymentUpdate): Promise<Payment> {
        const response = await api.patch<Payment>(`/payments/${paymentId}`, data);
        return response.data;
    }

    /**
     * Delete a payment
     */
    async deletePayment(paymentId: string): Promise<void> {
        await api.delete(`/payments/${paymentId}`);
    }

    /**
     * Get daily actions
     */
    async getDailyActions(): Promise<DailyActionsResponse> {
        const response = await api.get<DailyActionsResponse>('/plans/actions/daily');
        return response.data;
    }

    /**
     * Check for new milestones
     */
    async checkMilestones(): Promise<MilestoneCheckResult> {
        const response = await api.get<MilestoneCheckResult>('/payments/milestones');
        return response.data;
    }
}

// Export PaymentCreate as LogPaymentRequest alias for compatibility
export type LogPaymentRequest = PaymentCreate;

export const paymentService = new PaymentService();
export default paymentService;
