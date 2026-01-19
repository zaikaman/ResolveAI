/**
 * Debt API service for CRUD operations (server-side encryption)
 */

import api from './api';
import type { Debt, DebtListResponse } from '../stores/debtStore';

export interface DebtFormData {
    creditor_name: string;
    debt_type: 'credit_card' | 'personal_loan' | 'student_loan' | 'mortgage' | 'auto_loan' | 'medical_bill' | 'other';
    balance: number;
    apr: number;
    minimum_payment: number;
    account_number_last4?: string;
    due_date?: number;
    notes?: string;
}

export interface DebtUpdateData {
    creditor_name?: string;
    debt_type?: 'credit_card' | 'personal_loan' | 'student_loan' | 'mortgage' | 'auto_loan' | 'medical_bill' | 'other';
    balance?: number;
    apr?: number;
    minimum_payment?: number;
    account_number_last4?: string;
    due_date?: number;
    notes?: string;
    is_active?: boolean;
}

class DebtService {
    /**
     * Get all debts for the current user
     */
    async getDebts(includeInactive = false): Promise<DebtListResponse> {
        const response = await api.get<DebtListResponse>('/debts', {
            params: { include_inactive: includeInactive }
        });
        return response.data;
    }

    /**
     * Get a single debt by ID
     */
    async getDebt(debtId: string): Promise<Debt> {
        const response = await api.get<Debt>(`/debts/${debtId}`);
        return response.data;
    }

    /**
     * Create a new debt (server encrypts before storage)
     */
    async createDebt(data: DebtFormData): Promise<Debt> {
        console.log('📝 Creating debt with data:', {
            creditor_name: data.creditor_name,
            debt_type: data.debt_type,
            balance: data.balance,
            apr: data.apr,
            minimum_payment: data.minimum_payment,
            due_date: data.due_date,
            notes: data.notes?.substring(0, 50)
        });

        // Server-only encryption: send plaintext, server encrypts
        const payload = {
            creditor_name: data.creditor_name,
            debt_type: data.debt_type,
            balance: data.balance,
            apr: data.apr,
            minimum_payment: data.minimum_payment,
            account_number_last4: data.account_number_last4,
            due_date: data.due_date,
            notes: data.notes,
        };

        try {
            const response = await api.post<Debt>('/debts', payload);
            console.log('✅ Debt created successfully:', response.data.id);
            return response.data;
        } catch (error: any) {
            console.error('❌ Failed to create debt:', error);
            throw error;
        }
    }

    /**
     * Update an existing debt
     */
    async updateDebt(debtId: string, data: DebtUpdateData): Promise<Debt> {
        const payload: Record<string, unknown> = {};

        // Only include provided fields
        if (data.creditor_name !== undefined) {
            payload.creditor_name = data.creditor_name;
        }
        if (data.debt_type !== undefined) {
            payload.debt_type = data.debt_type;
        }
        if (data.account_number_last4 !== undefined) {
            payload.account_number_last4 = data.account_number_last4;
        }
        if (data.due_date !== undefined) {
            payload.due_date = data.due_date;
        }
        if (data.notes !== undefined) {
            payload.notes = data.notes;
        }
        if (data.is_active !== undefined) {
            payload.is_active = data.is_active;
        }

        // Send plaintext financial fields (server encrypts)
        if (data.balance !== undefined) {
            payload.balance = data.balance;
        }
        if (data.apr !== undefined) {
            payload.apr = data.apr;
        }
        if (data.minimum_payment !== undefined) {
            payload.minimum_payment = data.minimum_payment;
        }

        const response = await api.patch<Debt>(`/debts/${debtId}`, payload);
        return response.data;
    }

    /**
     * Mark a debt as paid off
     */
    async markPaidOff(debtId: string): Promise<Debt> {
        const response = await api.post<Debt>(`/debts/${debtId}/paid-off`);
        return response.data;
    }

    /**
     * Delete a debt
     */
    async deleteDebt(debtId: string): Promise<void> {
        await api.delete(`/debts/${debtId}`);
    }
}

export const debtService = new DebtService();
export default debtService;
