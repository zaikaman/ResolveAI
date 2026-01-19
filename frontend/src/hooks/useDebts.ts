/**
 * useDebts hook - Manage debt operations with store integration
 */

import { useCallback } from 'react';
import { useDebtStore } from '../stores/debtStore';
import debtService from '../services/debtService';
import type { DebtFormData, DebtUpdateData } from '../services/debtService';

export function useDebts() {
    const {
        debts,
        summary,
        loading,
        error,
        selectedDebt,
        setDebts,
        addDebt,
        updateDebt,
        removeDebt,
        setSelectedDebt,
        setLoading,
        setError
    } = useDebtStore();

    /**
     * Fetch all debts for the current user
     */
    const fetchDebts = useCallback(async (includeInactive = false) => {
        setLoading(true);
        try {
            const response = await debtService.getDebts(includeInactive);
            setDebts(response.debts, response.summary);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch debts');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [setDebts, setLoading, setError]);

    /**
     * Create a new debt
     */
    const createDebt = useCallback(async (data: DebtFormData) => {
        setLoading(true);
        try {
            const debt = await debtService.createDebt(data);
            addDebt(debt);
            return debt;
        } catch (err: any) {
            setError(err.message || 'Failed to create debt');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [addDebt, setLoading, setError]);

    /**
     * Update an existing debt
     */
    const editDebt = useCallback(async (debtId: string, data: DebtUpdateData) => {
        setLoading(true);
        try {
            const debt = await debtService.updateDebt(debtId, data);
            updateDebt(debt);
            return debt;
        } catch (err: any) {
            setError(err.message || 'Failed to update debt');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [updateDebt, setLoading, setError]);

    /**
     * Mark a debt as paid off
     */
    const markPaidOff = useCallback(async (debtId: string) => {
        setLoading(true);
        try {
            const debt = await debtService.markPaidOff(debtId);
            updateDebt(debt);
            return debt;
        } catch (err: any) {
            setError(err.message || 'Failed to mark debt as paid off');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [updateDebt, setLoading, setError]);

    /**
     * Delete a debt
     */
    const deleteDebt = useCallback(async (debtId: string) => {
        setLoading(true);
        try {
            await debtService.deleteDebt(debtId);
            removeDebt(debtId);
        } catch (err: any) {
            setError(err.message || 'Failed to delete debt');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [removeDebt, setLoading, setError]);
    return {
        // State
        debts,
        summary,
        loading,
        error,
        selectedDebt,

        // Actions
        fetchDebts,
        createDebt,
        editDebt,
        markPaidOff,
        deleteDebt,
        setSelectedDebt,

        // Computed
        hasDebts: debts.length > 0,
        activeDebts: debts.filter(d => d.is_active && !d.is_paid_off),
        paidOffDebts: debts.filter(d => d.is_paid_off),
    };
}
