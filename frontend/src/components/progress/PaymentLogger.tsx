/**
 * PaymentLogger component - Quick payment entry modal
 */

import { useState, useEffect } from 'react';
import { DollarSign, Calendar, CreditCard, FileText } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { formatCurrency } from '../../utils/formatting';
import type { Debt } from '../../stores/debtStore';

interface PaymentLoggerProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: PaymentLogData) => Promise<void>;
    debts: Debt[];
    preselectedDebtId?: string;
    suggestedAmount?: number;
}

export interface PaymentLogData {
    debt_id: string;
    amount: number;
    payment_date?: string;
    payment_method?: string;
    notes?: string;
}

const paymentMethods = [
    { value: 'bank_transfer', label: 'Bank Transfer' },
    { value: 'check', label: 'Check' },
    { value: 'debit_card', label: 'Debit Card' },
    { value: 'credit_card', label: 'Credit Card' },
    { value: 'auto_pay', label: 'Auto Pay' },
    { value: 'cash', label: 'Cash' },
    { value: 'other', label: 'Other' },
];

export function PaymentLogger({
    isOpen,
    onClose,
    onSubmit,
    debts,
    preselectedDebtId,
    suggestedAmount
}: PaymentLoggerProps) {
    const [formData, setFormData] = useState<PaymentLogData>({
        debt_id: preselectedDebtId || '',
        amount: suggestedAmount || 0,
        payment_date: new Date().toISOString().split('T')[0],
        payment_method: '',
        notes: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Reset form when modal opens with new data
    useEffect(() => {
        if (isOpen) {
            setFormData({
                debt_id: preselectedDebtId || (debts.length === 1 ? debts[0].id : ''),
                amount: suggestedAmount || 0,
                payment_date: new Date().toISOString().split('T')[0],
                payment_method: '',
                notes: ''
            });
            setError(null);
        }
    }, [isOpen, preselectedDebtId, suggestedAmount, debts]);

    const selectedDebt = debts.find(d => d.id === formData.debt_id);
    const maxAmount = selectedDebt?.balance || 0;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        // Validation
        if (!formData.debt_id) {
            setError('Please select a debt');
            return;
        }
        if (formData.amount <= 0) {
            setError('Payment amount must be greater than 0');
            return;
        }
        if (formData.amount > maxAmount * 1.1) {
            setError(`Payment amount exceeds debt balance of ${formatCurrency(maxAmount)}`);
            return;
        }

        setLoading(true);
        try {
            await onSubmit(formData);
            onClose();
        } catch (err: any) {
            setError(err.message || 'Failed to log payment');
        } finally {
            setLoading(false);
        }
    };

    const handleAmountChange = (value: string) => {
        const amount = parseFloat(value) || 0;
        setFormData(prev => ({ ...prev, amount }));
    };

    const handleQuickAmount = (amount: number) => {
        setFormData(prev => ({ ...prev, amount }));
    };

    // Filter to only active debts
    const activeDebts = debts.filter(d => d.is_active && !d.is_paid_off);

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title="Log Payment"
            description="Record a payment you've made toward your debt"
            size="md"
            footer={
                <div className="flex gap-3">
                    <Button variant="ghost" onClick={onClose} disabled={loading}>
                        Cancel
                    </Button>
                    <Button 
                        onClick={handleSubmit} 
                        isLoading={loading}
                        leftIcon={<DollarSign className="h-4 w-4" />}
                    >
                        Log Payment
                    </Button>
                </div>
            }
        >
            <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                        {error}
                    </div>
                )}

                {/* Debt Selection */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                        Debt
                    </label>
                    <select
                        value={formData.debt_id}
                        onChange={(e) => setFormData(prev => ({ ...prev, debt_id: e.target.value }))}
                        className="w-full h-10 px-3 rounded-lg border border-slate-200 bg-white text-slate-900 focus:border-main focus:ring-2 focus:ring-main/20 outline-none"
                        required
                    >
                        <option value="">Select a debt...</option>
                        {activeDebts.map((debt) => (
                            <option key={debt.id} value={debt.id}>
                                {debt.creditor_name} - Balance: {formatCurrency(debt.balance)}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Amount */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                        Amount
                    </label>
                    <div className="relative">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
                            $
                        </span>
                        <input
                            type="number"
                            step="0.01"
                            min="0.01"
                            max={maxAmount * 1.1}
                            value={formData.amount || ''}
                            onChange={(e) => handleAmountChange(e.target.value)}
                            className="w-full h-10 pl-7 pr-3 rounded-lg border border-slate-200 bg-white text-slate-900 focus:border-main focus:ring-2 focus:ring-main/20 outline-none"
                            placeholder="0.00"
                            required
                        />
                    </div>
                    
                    {/* Quick amount buttons */}
                    {selectedDebt && (
                        <div className="flex flex-wrap gap-2 mt-2">
                            <button
                                type="button"
                                onClick={() => handleQuickAmount(selectedDebt.minimum_payment)}
                                className="px-3 py-1 text-xs font-medium bg-slate-100 hover:bg-slate-200 rounded-full transition-colors"
                            >
                                Min: {formatCurrency(selectedDebt.minimum_payment)}
                            </button>
                            <button
                                type="button"
                                onClick={() => handleQuickAmount(Math.min(selectedDebt.minimum_payment * 1.5, maxAmount))}
                                className="px-3 py-1 text-xs font-medium bg-slate-100 hover:bg-slate-200 rounded-full transition-colors"
                            >
                                1.5x: {formatCurrency(Math.min(selectedDebt.minimum_payment * 1.5, maxAmount))}
                            </button>
                            <button
                                type="button"
                                onClick={() => handleQuickAmount(maxAmount)}
                                className="px-3 py-1 text-xs font-medium bg-green-100 hover:bg-green-200 text-green-700 rounded-full transition-colors"
                            >
                                Pay Off: {formatCurrency(maxAmount)}
                            </button>
                        </div>
                    )}
                </div>

                {/* Payment Date */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                        Payment Date
                    </label>
                    <div className="relative">
                        <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                        <input
                            type="date"
                            value={formData.payment_date}
                            onChange={(e) => setFormData(prev => ({ ...prev, payment_date: e.target.value }))}
                            className="w-full h-10 pl-10 pr-3 rounded-lg border border-slate-200 bg-white text-slate-900 focus:border-main focus:ring-2 focus:ring-main/20 outline-none"
                            max={new Date().toISOString().split('T')[0]}
                        />
                    </div>
                </div>

                {/* Payment Method */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                        Payment Method (optional)
                    </label>
                    <div className="relative">
                        <CreditCard className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                        <select
                            value={formData.payment_method}
                            onChange={(e) => setFormData(prev => ({ ...prev, payment_method: e.target.value }))}
                            className="w-full h-10 pl-10 pr-3 rounded-lg border border-slate-200 bg-white text-slate-900 focus:border-main focus:ring-2 focus:ring-main/20 outline-none"
                        >
                            <option value="">Select method...</option>
                            {paymentMethods.map((method) => (
                                <option key={method.value} value={method.value}>
                                    {method.label}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Notes */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                        Notes (optional)
                    </label>
                    <div className="relative">
                        <FileText className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                        <textarea
                            value={formData.notes}
                            onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                            className="w-full min-h-[80px] pl-10 pr-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-900 focus:border-main focus:ring-2 focus:ring-main/20 outline-none resize-none"
                            placeholder="Add any notes about this payment..."
                            maxLength={500}
                        />
                    </div>
                </div>

                {/* Summary */}
                {selectedDebt && formData.amount > 0 && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                        <p className="text-sm text-green-800">
                            <strong>After this payment:</strong> {selectedDebt.creditor_name} balance will be{' '}
                            <strong>{formatCurrency(Math.max(0, selectedDebt.balance - formData.amount))}</strong>
                            {formData.amount >= selectedDebt.balance && (
                                <span className="ml-2 text-green-600 font-semibold">🎉 Paid off!</span>
                            )}
                        </p>
                    </div>
                )}
            </form>
        </Modal>
    );
}

export default PaymentLogger;
