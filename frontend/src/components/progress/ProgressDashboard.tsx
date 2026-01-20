/**
 * ProgressDashboard component - Overview of debt reduction progress
 */

import { 
    TrendingDown, 
    Wallet, 
    Clock, 
    Flame,
    DollarSign,
    Calendar,
    Award
} from 'lucide-react';
import { Card, CardContent } from '../common/Card';
import { formatCurrency } from '../../utils/formatting';
import type { PaymentStats, RecentPaymentSummary } from '../../services/paymentService';
import type { PlanSummary } from '../../stores/planStore';

interface ProgressDashboardProps {
    paymentStats?: PaymentStats | null;
    paymentSummary?: RecentPaymentSummary | null;
    planSummary?: PlanSummary | null;
    totalDebt?: number;
    originalDebt?: number;
    loading?: boolean;
}

interface StatCardProps {
    icon: React.ReactNode;
    label: string;
    value: string | number;
    subtext?: string;
    variant?: 'default' | 'success' | 'warning' | 'primary';
}

function StatCard({ icon, label, value, subtext, variant = 'default' }: StatCardProps) {
    const variantStyles = {
        default: 'bg-white',
        success: 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-200',
        warning: 'bg-gradient-to-br from-yellow-50 to-amber-50 border-yellow-200',
        primary: 'bg-gradient-to-br from-main to-blue-700 text-white border-none'
    };

    const textStyles = {
        default: 'text-slate-900',
        success: 'text-green-800',
        warning: 'text-yellow-800',
        primary: 'text-white'
    };

    const subtextStyles = {
        default: 'text-slate-500',
        success: 'text-green-600',
        warning: 'text-yellow-600',
        primary: 'text-blue-100'
    };

    return (
        <Card className={variantStyles[variant]}>
            <CardContent className="pt-5">
                <div className="flex items-start justify-between">
                    <div>
                        <p className={`text-sm font-medium ${variant === 'primary' ? 'text-blue-100' : 'text-slate-500'}`}>
                            {label}
                        </p>
                        <p className={`text-2xl font-bold mt-1 ${textStyles[variant]}`}>
                            {value}
                        </p>
                        {subtext && (
                            <p className={`text-sm mt-1 ${subtextStyles[variant]}`}>
                                {subtext}
                            </p>
                        )}
                    </div>
                    <div className={`p-2 rounded-lg ${variant === 'primary' ? 'bg-white/10' : 'bg-slate-100'}`}>
                        {icon}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

function SkeletonCard() {
    return (
        <Card>
            <CardContent className="pt-5">
                <div className="animate-pulse">
                    <div className="h-4 w-24 bg-slate-200 rounded mb-2" />
                    <div className="h-8 w-32 bg-slate-200 rounded mb-2" />
                    <div className="h-3 w-20 bg-slate-100 rounded" />
                </div>
            </CardContent>
        </Card>
    );
}

export function ProgressDashboard({
    paymentStats,
    paymentSummary,
    planSummary,
    totalDebt = 0,
    originalDebt = 0,
    loading = false
}: ProgressDashboardProps) {
    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map(i => <SkeletonCard key={i} />)}
            </div>
        );
    }

    // Calculate progress percentage
    const progressPercentage = originalDebt > 0 
        ? ((originalDebt - totalDebt) / originalDebt) * 100 
        : planSummary?.progress_percentage || 0;

    // Get key metrics
    const totalPaid = paymentStats?.total_amount_paid || 0;
    const interestSaved = paymentStats?.total_interest_saved || 0;
    const currentStreak = paymentStats?.current_streak_days || paymentSummary?.current_streak || 0;
    const monthsRemaining = planSummary?.months_remaining || 0;

    return (
        <div className="space-y-6">
            {/* Main Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Total Progress */}
                <StatCard
                    icon={<TrendingDown className="h-5 w-5 text-green-600" />}
                    label="Total Progress"
                    value={`${progressPercentage.toFixed(1)}%`}
                    subtext={`${formatCurrency(totalPaid)} paid off`}
                    variant="success"
                />

                {/* Remaining Debt */}
                <StatCard
                    icon={<Wallet className="h-5 w-5 text-slate-600" />}
                    label="Remaining Debt"
                    value={formatCurrency(totalDebt)}
                    subtext={planSummary?.debt_free_date ? `Free by ${new Date(planSummary.debt_free_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}` : undefined}
                />

                {/* Interest Saved */}
                <StatCard
                    icon={<DollarSign className="h-5 w-5 text-green-600" />}
                    label="Interest Saved"
                    value={formatCurrency(interestSaved)}
                    subtext="By paying extra"
                    variant="success"
                />

                {/* Time Remaining */}
                <StatCard
                    icon={<Clock className="h-5 w-5 text-blue-600" />}
                    label="Months to Go"
                    value={monthsRemaining > 0 ? monthsRemaining.toString() : '--'}
                    subtext={planSummary?.strategy === 'avalanche' ? 'Avalanche strategy' : planSummary?.strategy === 'snowball' ? 'Snowball strategy' : undefined}
                />
            </div>

            {/* Secondary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Streak */}
                <Card className={currentStreak > 0 ? 'border-orange-200 bg-orange-50' : ''}>
                    <CardContent className="pt-5">
                        <div className="flex items-center gap-4">
                            <div className={`p-3 rounded-full ${currentStreak > 0 ? 'bg-orange-100' : 'bg-slate-100'}`}>
                                <Flame className={`h-6 w-6 ${currentStreak > 0 ? 'text-orange-500' : 'text-slate-400'}`} />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-slate-500">Current Streak</p>
                                <p className="text-xl font-bold text-slate-900">
                                    {currentStreak} {currentStreak === 1 ? 'day' : 'days'}
                                </p>
                                {paymentStats?.longest_streak_days && paymentStats.longest_streak_days > currentStreak && (
                                    <p className="text-xs text-slate-500">
                                        Best: {paymentStats.longest_streak_days} days
                                    </p>
                                )}
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* This Month */}
                <Card>
                    <CardContent className="pt-5">
                        <div className="flex items-center gap-4">
                            <div className="p-3 rounded-full bg-blue-100">
                                <Calendar className="h-6 w-6 text-blue-600" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-slate-500">This Month</p>
                                <p className="text-xl font-bold text-slate-900">
                                    {formatCurrency(paymentStats?.amount_this_month || 0)}
                                </p>
                                <p className="text-xs text-slate-500">
                                    {paymentStats?.payments_this_month || 0} payments
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Average Payment */}
                <Card>
                    <CardContent className="pt-5">
                        <div className="flex items-center gap-4">
                            <div className="p-3 rounded-full bg-purple-100">
                                <Award className="h-6 w-6 text-purple-600" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-slate-500">Average Payment</p>
                                <p className="text-xl font-bold text-slate-900">
                                    {formatCurrency(paymentStats?.average_payment_amount || 0)}
                                </p>
                                <p className="text-xs text-slate-500">
                                    {paymentStats?.total_payments || 0} total payments
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Progress Bar */}
            {originalDebt > 0 && (
                <Card>
                    <CardContent className="pt-5">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-slate-700">
                                Debt Freedom Progress
                            </span>
                            <span className="text-sm font-bold text-main">
                                {progressPercentage.toFixed(1)}%
                            </span>
                        </div>
                        <div className="h-4 bg-slate-100 rounded-full overflow-hidden">
                            <div 
                                className="h-full bg-gradient-to-r from-main to-green-500 rounded-full transition-all duration-500"
                                style={{ width: `${Math.min(progressPercentage, 100)}%` }}
                            />
                        </div>
                        <div className="flex justify-between mt-2 text-xs text-slate-500">
                            <span>Started: {formatCurrency(originalDebt)}</span>
                            <span>Remaining: {formatCurrency(totalDebt)}</span>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}

export default ProgressDashboard;
