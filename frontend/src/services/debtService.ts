/**
 * Debt API service for CRUD operations with encryption
 */

import api from './api';
import { encryptValue } from '../utils/encryption';
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
    private encryptionKey: string | null = null;

    setEncryptionKey(key: string) {
        this.encryptionKey = key;
    }

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
     * Create a new debt (encrypts sensitive fields)
     */
    async createDebt(data: DebtFormData): Promise<Debt> {
        if (!this.encryptionKey) {
            throw new Error('Encryption key not set');
        }

        console.log('📝 Creating debt with data:', {
            creditor_name: data.creditor_name,
            debt_type: data.debt_type,
            balance: data.balance,
            apr: data.apr,
            minimum_payment: data.minimum_payment,
            due_date: data.due_date,
            notes: data.notes?.substring(0, 50)
        });

        const payload = {
            creditor_name: data.creditor_name,
            debt_type: data.debt_type,
            balance_encrypted: encryptValue(data.balance.toString(), this.encryptionKey),
            apr_encrypted: encryptValue(data.apr.toString(), this.encryptionKey),
            minimum_payment_encrypted: encryptValue(data.minimum_payment.toString(), this.encryptionKey),
            account_number_last4: data.account_number_last4,
            due_date: data.due_date,
            notes: data.notes,
        };

        console.log('🔐 Encrypted payload prepared (lengths):', {
            balance_encrypted: payload.balance_encrypted.length,
            apr_encrypted: payload.apr_encrypted.length,
            minimum_payment_encrypted: payload.minimum_payment_encrypted.length
        });

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

        // Encrypt financial fields if provided
        if (this.encryptionKey) {
            if (data.balance !== undefined) {
                payload.balance_encrypted = encryptValue(data.balance.toString(), this.encryptionKey);
            }
            if (data.apr !== undefined) {
                payload.apr_encrypted = encryptValue(data.apr.toString(), this.encryptionKey);
            }
            if (data.minimum_payment !== undefined) {
                payload.minimum_payment_encrypted = encryptValue(data.minimum_payment.toString(), this.encryptionKey);
            }
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
