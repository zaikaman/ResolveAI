/**
 * DebtForm component - Manual debt entry with validation
 * Design aligned with landing page styling
 */

import { useState } from 'react';
import { CreditCard, DollarSign, Percent, Calendar } from 'lucide-react';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../common/Card';
import { cn } from '../../utils/cn';

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

interface DebtFormProps {
    initialData?: Partial<DebtFormData>;
    onSubmit: (data: DebtFormData) => Promise<void>;
    onCancel?: () => void;
    isEditing?: boolean;
    className?: string;
}

const debtTypes = [
    { value: 'credit_card', label: 'Credit Card' },
    { value: 'personal_loan', label: 'Personal Loan' },
    { value: 'student_loan', label: 'Student Loan' },
    { value: 'mortgage', label: 'Mortgage' },
    { value: 'auto_loan', label: 'Auto Loan' },
    { value: 'medical_bill', label: 'Medical' },
    { value: 'other', label: 'Other' },
] as const;

export function DebtForm({
    initialData,
    onSubmit,
    onCancel,
    isEditing = false,
    className,
}: DebtFormProps) {
    const [formData, setFormData] = useState<DebtFormData>({
        creditor_name: initialData?.creditor_name || '',
        debt_type: initialData?.debt_type || 'credit_card',
        balance: initialData?.balance || 0,
        apr: initialData?.apr || 0,
        minimum_payment: initialData?.minimum_payment || 0,
        account_number_last4: initialData?.account_number_last4 || '',
        due_date: initialData?.due_date,
        notes: initialData?.notes || '',
    });

    const [errors, setErrors] = useState<Partial<Record<keyof DebtFormData, string>>>({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    const validate = (): boolean => {
        const newErrors: Partial<Record<keyof DebtFormData, string>> = {};

        if (!formData.creditor_name.trim()) {
            newErrors.creditor_name = 'Creditor name is required';
        }

        if (formData.balance <= 0) {
            newErrors.balance = 'Balance must be greater than 0';
        }

        if (formData.apr < 0 || formData.apr > 100) {
            newErrors.apr = 'APR must be between 0 and 100';
        }

        if (formData.minimum_payment <= 0) {
            newErrors.minimum_payment = 'Minimum payment must be greater than 0';
        }

        if (formData.due_date && (formData.due_date < 1 || formData.due_date > 31)) {
            newErrors.due_date = 'Due date must be between 1 and 31';
        }

        if (formData.account_number_last4 && !/^\d{4}$/.test(formData.account_number_last4)) {
            newErrors.account_number_last4 = 'Must be 4 digits';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validate()) return;

        setIsSubmitting(true);
        try {
            await onSubmit(formData);
        } catch (error) {
            console.error('Failed to submit debt:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleChange = (field: keyof DebtFormData, value: string | number | undefined) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        // Clear error when user starts typing
        if (errors[field]) {
            setErrors(prev => ({ ...prev, [field]: undefined }));
        }
    };

    return (
        <Card className={className}>
            <form onSubmit={handleSubmit}>
                <CardHeader>
                    <CardTitle>{isEditing ? 'Edit Debt' : 'Add New Debt'}</CardTitle>
                </CardHeader>

                <CardContent className="space-y-4">
                    {/* Creditor Name */}
                    <Input
                        label="Creditor Name"
                        placeholder="e.g., VietcomBank, FE Credit"
                        value={formData.creditor_name}
                        onChange={(e) => handleChange('creditor_name', e.target.value)}
                        error={errors.creditor_name}
                        leftIcon={<CreditCard className="h-4 w-4" />}
                    />

                    {/* Debt Type */}
                    <div className="space-y-1.5">
                        <label className="text-sm font-medium text-slate-700">Debt Type</label>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                            {debtTypes.map(type => (
                                <button
                                    key={type.value}
                                    type="button"
                                    onClick={() => handleChange('debt_type', type.value)}
                                    className={cn(
                                        "px-3 py-2 text-sm rounded-lg border transition-all",
                                        formData.debt_type === type.value
                                            ? "bg-main text-white border-main"
                                            : "bg-white text-slate-600 border-slate-200 hover:border-main hover:text-main"
                                    )}
                                >
                                    {type.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Financial Fields */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <Input
                            type="number"
                            label="Current Balance"
                            placeholder="0"
                            value={formData.balance || ''}
                            onChange={(e) => handleChange('balance', parseFloat(e.target.value) || 0)}
                            error={errors.balance}
                            leftIcon={<DollarSign className="h-4 w-4" />}
                        />

                        <Input
                            type="number"
                            label="APR (%)"
                            placeholder="0.00"
                            step="0.01"
                            value={formData.apr || ''}
                            onChange={(e) => handleChange('apr', parseFloat(e.target.value) || 0)}
                            error={errors.apr}
                            leftIcon={<Percent className="h-4 w-4" />}
                        />

                        <Input
                            type="number"
                            label="Minimum Payment"
                            placeholder="0"
                            value={formData.minimum_payment || ''}
                            onChange={(e) => handleChange('minimum_payment', parseFloat(e.target.value) || 0)}
                            error={errors.minimum_payment}
                            leftIcon={<DollarSign className="h-4 w-4" />}
                        />
                    </div>

                    {/* Optional Fields */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <Input
                            label="Account Last 4 Digits (Optional)"
                            placeholder="1234"
                            maxLength={4}
                            value={formData.account_number_last4 || ''}
                            onChange={(e) => handleChange('account_number_last4', e.target.value)}
                            error={errors.account_number_last4}
                        />

                        <Input
                            type="number"
                            label="Due Date (Day of Month)"
                            placeholder="15"
                            min={1}
                            max={31}
                            value={formData.due_date || ''}
                            onChange={(e) => handleChange('due_date', parseInt(e.target.value) || undefined)}
                            error={errors.due_date}
                            leftIcon={<Calendar className="h-4 w-4" />}
                        />
                    </div>

                    {/* Notes */}
                    <div className="space-y-1.5">
                        <label className="text-sm font-medium text-slate-700">Notes (Optional)</label>
                        <textarea
                            placeholder="Any additional notes about this debt..."
                            value={formData.notes}
                            onChange={(e) => handleChange('notes', e.target.value)}
                            className="flex w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-main focus-visible:ring-offset-2 min-h-[80px] resize-none"
                        />
                    </div>
                </CardContent>

                <CardFooter className="flex justify-end gap-3">
                    {onCancel && (
                        <Button type="button" variant="outline" onClick={onCancel}>
                            Cancel
                        </Button>
                    )}
                    <Button type="submit" isLoading={isSubmitting}>
                        {isEditing ? 'Save Changes' : 'Add Debt'}
                    </Button>
                </CardFooter>
            </form>
        </Card>
    );
}
