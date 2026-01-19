/**
 * DebtCard component - Displays a single debt with balance, rate, and creditor
 * Design aligned with landing page styling
 */

import { CreditCard, TrendingDown, Calendar, Trash2, Edit2, CheckCircle } from 'lucide-react';
import { Card, CardContent } from '../common/Card';
import { Button } from '../common/Button';
import { cn } from '../../utils/cn';
import { formatCurrency } from '../../utils/formatting';
import type { Debt } from '../../stores/debtStore';

interface DebtCardProps {
    debt: Debt;
    onEdit?: (debt: Debt) => void;
    onDelete?: (debt: Debt) => void;
    onMarkPaidOff?: (debt: Debt) => void;
    className?: string;
}

const debtTypeLabels: Record<string, string> = {
    credit_card: 'Credit Card',
    personal_loan: 'Personal Loan',
    student_loan: 'Student Loan',
    mortgage: 'Mortgage',
    auto_loan: 'Auto Loan',
    medical: 'Medical',
    other: 'Other',
};

const debtTypeColors: Record<string, string> = {
    credit_card: 'bg-red-100 text-red-700',
    personal_loan: 'bg-blue-100 text-blue-700',
    student_loan: 'bg-purple-100 text-purple-700',
    mortgage: 'bg-green-100 text-green-700',
    auto_loan: 'bg-orange-100 text-orange-700',
    medical: 'bg-pink-100 text-pink-700',
    other: 'bg-slate-100 text-slate-700',
};

export function DebtCard({
    debt,
    onEdit,
    onDelete,
    onMarkPaidOff,
    className,
}: DebtCardProps) {
    // Use plaintext fields directly
    const balance = debt.balance;
    const apr = debt.apr;
    const minimumPayment = debt.minimum_payment;

    return (
        <Card
            className={cn(
                "relative overflow-hidden transition-all duration-200",
                debt.is_paid_off && "opacity-60",
                className
            )}
            hoverable={!debt.is_paid_off}
        >
            {/* Colored top border based on debt type */}
            <div className={cn(
                "absolute top-0 left-0 right-0 h-1",
                debtTypeColors[debt.debt_type]?.replace('bg-', 'bg-').replace('-100', '-500')
            )} />

            <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className={cn(
                            "p-2 rounded-lg",
                            debtTypeColors[debt.debt_type] || debtTypeColors.other
                        )}>
                            <CreditCard className="h-5 w-5" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-slate-900">{debt.creditor_name}</h3>
                            <span className={cn(
                                "text-xs px-2 py-0.5 rounded-full",
                                debtTypeColors[debt.debt_type] || debtTypeColors.other
                            )}>
                                {debtTypeLabels[debt.debt_type] || 'Other'}
                            </span>
                        </div>
                    </div>

                    {/* Actions dropdown */}
                    <div className="flex items-center gap-1">
                        {!debt.is_paid_off && (
                            <>
                                {onEdit && (
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => onEdit(debt)}
                                        className="h-8 w-8"
                                    >
                                        <Edit2 className="h-4 w-4" />
                                    </Button>
                                )}
                                {onMarkPaidOff && (
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => onMarkPaidOff(debt)}
                                        className="h-8 w-8 text-progress-600 hover:text-progress-700 hover:bg-progress-50"
                                    >
                                        <CheckCircle className="h-4 w-4" />
                                    </Button>
                                )}
                            </>
                        )}
                        {onDelete && (
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => onDelete(debt)}
                                className="h-8 w-8 text-red-500 hover:text-red-600 hover:bg-red-50"
                            >
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        )}
                    </div>
                </div>

                {/* Balance - Main metric */}
                <div className="mb-4">
                    <p className="text-sm text-slate-500 mb-1">Outstanding Balance</p>
                    <p className={cn(
                        "text-2xl font-bold",
                        debt.is_paid_off ? "text-progress-600 line-through" : "text-slate-900"
                    )}>
                        {debt.is_paid_off ? 'PAID OFF' : formatCurrency(balance)}
                    </p>
                </div>

                {/* Stats row */}
                <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-100">
                    <div>
                        <div className="flex items-center gap-1 text-slate-500 text-xs mb-1">
                            <TrendingDown className="h-3 w-3" />
                            <span>APR</span>
                        </div>
                        <p className="font-semibold text-slate-900">{apr.toFixed(2)}%</p>
                    </div>
                    <div>
                        <div className="flex items-center gap-1 text-slate-500 text-xs mb-1">
                            <Calendar className="h-3 w-3" />
                            <span>Min. Payment</span>
                        </div>
                        <p className="font-semibold text-slate-900">{formatCurrency(minimumPayment)}</p>
                    </div>
                    {debt.due_date && (
                        <div>
                            <div className="flex items-center gap-1 text-slate-500 text-xs mb-1">
                                <Calendar className="h-3 w-3" />
                                <span>Due Date</span>
                            </div>
                            <p className="font-semibold text-slate-900">Day {debt.due_date}</p>
                        </div>
                    )}
                </div>

                {/* Paid off badge */}
                {debt.is_paid_off && (
                    <div className="absolute inset-0 flex items-center justify-center bg-white/80">
                        <div className="bg-progress-500 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2">
                            <CheckCircle className="h-5 w-5" />
                            Paid Off!
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
