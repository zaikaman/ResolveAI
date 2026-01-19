/**
 * PaymentSchedule component - Table showing monthly payment breakdown
 * Design aligned with landing page styling
 */

import { useState } from 'react';
import { ChevronDown, ChevronUp, Calendar, CheckCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Button } from '../common/Button';
import { cn } from '../../utils/cn';
import type { MonthlyBreakdown } from '../../stores/planStore';

interface PaymentScheduleProps {
    schedule: MonthlyBreakdown[];
    className?: string;
}

export function PaymentSchedule({ schedule, className }: PaymentScheduleProps) {
    const [expandedMonth, setExpandedMonth] = useState<number | null>(null);
    const [showAll, setShowAll] = useState(false);

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND',
            maximumFractionDigits: 0,
        }).format(value);
    };

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('vi-VN', {
            month: 'short',
            year: 'numeric',
        });
    };

    const displayedSchedule = showAll ? schedule : schedule.slice(0, 12);

    if (schedule.length === 0) {
        return (
            <Card className={className}>
                <CardHeader>
                    <CardTitle>Payment Schedule</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8 text-slate-500">
                        No payment schedule available
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className={className}>
            <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Payment Schedule</CardTitle>
                <span className="text-sm text-slate-500">{schedule.length} months</span>
            </CardHeader>
            <CardContent>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-slate-200">
                                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-600">Month</th>
                                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-600">Payment</th>
                                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-600">Remaining</th>
                                <th className="text-center py-3 px-4 text-sm font-semibold text-slate-600"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {displayedSchedule.map((month) => (
                                <>
                                    <tr
                                        key={month.month}
                                        className={cn(
                                            "border-b border-slate-100 cursor-pointer hover:bg-slate-50 transition-colors",
                                            expandedMonth === month.month && "bg-slate-50"
                                        )}
                                        onClick={() => setExpandedMonth(expandedMonth === month.month ? null : month.month)}
                                    >
                                        <td className="py-3 px-4">
                                            <div className="flex items-center gap-2">
                                                <Calendar className="h-4 w-4 text-slate-400" />
                                                <span className="font-medium text-slate-900">{formatDate(month.date)}</span>
                                            </div>
                                        </td>
                                        <td className="py-3 px-4 text-right">
                                            <span className="font-semibold text-main">
                                                {formatCurrency(month.total_payment)}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-right">
                                            <span className={cn(
                                                "font-medium",
                                                month.total_remaining <= 0 ? "text-progress-600" : "text-slate-600"
                                            )}>
                                                {month.total_remaining <= 0 ? (
                                                    <span className="flex items-center justify-end gap-1">
                                                        <CheckCircle className="h-4 w-4" />
                                                        Debt Free!
                                                    </span>
                                                ) : (
                                                    formatCurrency(month.total_remaining)
                                                )}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-center">
                                            {expandedMonth === month.month ? (
                                                <ChevronUp className="h-4 w-4 text-slate-400 inline" />
                                            ) : (
                                                <ChevronDown className="h-4 w-4 text-slate-400 inline" />
                                            )}
                                        </td>
                                    </tr>

                                    {/* Expanded detail */}
                                    {expandedMonth === month.month && (
                                        <tr>
                                            <td colSpan={4} className="bg-slate-50 p-4">
                                                <div className="space-y-2">
                                                    {month.payments.map((payment, idx) => (
                                                        <div
                                                            key={idx}
                                                            className={cn(
                                                                "flex items-center justify-between p-3 bg-white rounded-lg border border-slate-100",
                                                                payment.is_payoff_month && "border-progress-300 bg-progress-50"
                                                            )}
                                                        >
                                                            <div className="flex items-center gap-3">
                                                                {payment.is_payoff_month && (
                                                                    <CheckCircle className="h-5 w-5 text-progress-500" />
                                                                )}
                                                                <div>
                                                                    <p className="font-medium text-slate-900">{payment.debt_name}</p>
                                                                    <p className="text-xs text-slate-500">
                                                                        Principal: {formatCurrency(payment.principal)} | Interest: {formatCurrency(payment.interest)}
                                                                    </p>
                                                                </div>
                                                            </div>
                                                            <div className="text-right">
                                                                <p className="font-semibold text-main">{formatCurrency(payment.payment_amount)}</p>
                                                                {payment.is_payoff_month ? (
                                                                    <p className="text-xs text-progress-600 font-medium">Paid Off!</p>
                                                                ) : (
                                                                    <p className="text-xs text-slate-500">
                                                                        Remaining: {formatCurrency(payment.remaining_balance)}
                                                                    </p>
                                                                )}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Show more button */}
                {schedule.length > 12 && (
                    <div className="mt-4 text-center">
                        <Button
                            variant="outline"
                            onClick={() => setShowAll(!showAll)}
                        >
                            {showAll ? 'Show Less' : `Show All ${schedule.length} Months`}
                        </Button>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
