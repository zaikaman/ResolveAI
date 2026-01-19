/**
 * PlanSummary component - Key plan metrics display
 * Design aligned with landing page styling
 */

import { Calendar, TrendingDown, PiggyBank, Clock, Sparkles } from 'lucide-react';
import { Card, CardContent } from '../common/Card';
import { cn } from '../../utils/cn';
import { formatCurrency, formatDate } from '../../utils/formatting';

interface PlanSummaryProps {
    debtFreeDate: string;
    totalMonths: number;
    totalInterest: number;
    interestSaved: number;
    monthsSaved: number;
    monthlyPayment: number;
    strategy: 'avalanche' | 'snowball';
    className?: string;
}

export function PlanSummary({
    debtFreeDate,
    totalMonths,
    totalInterest,
    interestSaved,
    monthsSaved,
    monthlyPayment,
    strategy,
    className,
}: PlanSummaryProps) {
    return (
        <div className={cn("space-y-6", className)}>
            {/* Debt-free date highlight */}
            <Card className="bg-gradient-to-br from-progress-500 via-progress-600 to-emerald-700 text-white border-0 overflow-hidden relative">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" />
                <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />
                <CardContent className="py-8 relative">
                    <div className="flex items-center gap-2 text-progress-100 mb-2">
                        <Sparkles className="h-5 w-5" />
                        <span className="text-sm font-medium uppercase tracking-wide">Debt-Free Date</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-progress-100 text-sm font-medium mb-1">Debt-Free Date</span>
                        <span className="text-3xl font-bold tracking-tight">
                            {formatDate(debtFreeDate, { month: 'long', year: 'numeric' })}
                        </span>
                    </div>
                    <p className="text-progress-100">
                        {totalMonths} months until financial freedom
                    </p>
                </CardContent>
            </Card>

            {/* Key metrics grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Monthly Payment */}
                <Card>
                    <CardContent className="py-4">
                        <div className="flex items-center gap-2 text-slate-500 text-sm mb-1">
                            <Calendar className="h-4 w-4" />
                            <span>Monthly Payment</span>
                        </div>
                        <div className="flex flex-wrap gap-4 mt-6">
                            <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2 border border-white/10">
                                <span className="text-[10px] uppercase tracking-wider font-semibold block text-blue-100">Monthly</span>
                                <span className="font-bold text-lg">{formatCurrency(monthlyPayment)}</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Total Interest */}
                <Card>
                    <CardContent className="py-4">
                        <div className="flex items-center gap-2 text-slate-500 text-sm mb-1">
                            <TrendingDown className="h-4 w-4" />
                            <span>Total Interest</span>
                        </div>
                        <div className="text-sm">
                            <p className="text-slate-500">Total Interest</p>
                            <p className="font-bold text-slate-900">{formatCurrency(totalInterest)}</p>
                        </div>
                    </CardContent>
                </Card>

                {/* Interest Saved */}
                <Card className="bg-gradient-to-br from-progress-50 to-white border-progress-200">
                    <CardContent className="py-4">
                        <div className="flex items-center gap-2 text-progress-600 text-sm mb-1">
                            <PiggyBank className="h-4 w-4" />
                            <span>Interest Saved</span>
                        </div>
                        <div className="text-sm">
                            <p className="text-emerald-500">Savings</p>
                            <p className="font-bold text-emerald-600">{formatCurrency(interestSaved)}</p>
                        </div>
                    </CardContent>
                </Card>

                {/* Time Saved */}
                <Card className="bg-gradient-to-br from-main3 to-white border-main/20">
                    <CardContent className="py-4">
                        <div className="flex items-center gap-2 text-main text-sm mb-1">
                            <Clock className="h-4 w-4" />
                            <span>Time Saved</span>
                        </div>
                        <p className="text-2xl font-bold text-main">{monthsSaved} months</p>
                        <p className="text-xs text-blue-500">vs. minimum payments</p>
                    </CardContent>
                </Card>
            </div>

            {/* Strategy indicator */}
            <Card>
                <CardContent className="py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-slate-500 mb-1">Current Strategy</p>
                            <p className="text-lg font-semibold text-slate-900 capitalize">{strategy}</p>
                        </div>
                        <div className={cn(
                            "px-4 py-2 rounded-full text-sm font-medium",
                            strategy === 'avalanche'
                                ? "bg-red-100 text-red-700"
                                : "bg-blue-100 text-blue-700"
                        )}>
                            {strategy === 'avalanche' ? 'Highest APR First' : 'Lowest Balance First'}
                        </div>
                    </div>
                    <p className="text-sm text-slate-500 mt-2">
                        {strategy === 'avalanche'
                            ? 'Paying the highest interest rate debts first saves the most money.'
                            : 'Paying the smallest balances first builds momentum with quick wins.'}
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
