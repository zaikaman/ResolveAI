/**
 * Progress page - Comprehensive progress tracking and analytics
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    ArrowLeft, 
    RefreshCw, 
    Calendar, 
    DollarSign,
    Target,
    Award,
    Filter,
    Download,
    TrendingUp
} from 'lucide-react';
import { useDebts } from '../hooks/useDebts';
import { usePlan } from '../hooks/usePlan';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { ProgressChart } from '../components/progress/ProgressChart';
import { formatCurrency } from '../utils/formatting';
import paymentService, { 
    type PaymentStats, 
    type Payment,
    type MilestoneCheckResult
} from '../services/paymentService';

// Date range options
type DateRange = '30' | '90' | '180' | '365' | 'all';

export default function Progress() {
    const { debts } = useDebts();
    const { planSummary } = usePlan();
    const navigate = useNavigate();

    // State
    const [loading, setLoading] = useState(true);
    const [paymentStats, setPaymentStats] = useState<PaymentStats | null>(null);
    const [payments, setPayments] = useState<Payment[]>([]);
    const [milestones, setMilestones] = useState<MilestoneCheckResult | null>(null);
    const [dateRange, setDateRange] = useState<DateRange>('90');

    // Fetch progress data
    const fetchProgressData = useCallback(async () => {
        setLoading(true);
        try {
            const days = dateRange === 'all' ? 3650 : parseInt(dateRange);
            
            const [statsData, _summaryData, paymentsData, milestonesData] = await Promise.all([
                paymentService.getPaymentStats().catch(() => null),
                paymentService.getPaymentSummary().catch(() => null),
                paymentService.getRecentPayments(days, 100).catch(() => []),
                paymentService.checkMilestones().catch(() => null),
            ]);

            setPaymentStats(statsData);
            setPayments(paymentsData);
            setMilestones(milestonesData);
        } catch (error) {
            console.error('Failed to fetch progress data:', error);
        } finally {
            setLoading(false);
        }
    }, [dateRange]);

    useEffect(() => {
        fetchProgressData();
    }, [fetchProgressData]);

    // Calculate progress metrics
    const calculateMetrics = () => {
        if (!paymentStats || !planSummary) {
            return {
                totalPaid: 0,
                remainingDebt: 0,
                percentComplete: 0,
                avgMonthlyPayment: 0,
                projectedPayoffDate: null,
                streakDays: 0,
            };
        }

        const totalPaid = paymentStats.total_amount_paid || 0;
        // Calculate total debt from debts list since planSummary doesn't have total_debt
        const totalDebt = debts.reduce((sum, d) => sum + (d.balance || 0), 0);
        const remainingDebt = totalDebt - totalPaid;
        const percentComplete = totalDebt > 0 ? (totalPaid / totalDebt) * 100 : 0;
        
        // Calculate average monthly payment
        const avgMonthlyPayment = paymentStats.average_payment_amount || 0;
        
        // Estimate payoff date
        let projectedPayoffDate: Date | null = null;
        if (avgMonthlyPayment > 0 && remainingDebt > 0) {
            const monthsRemaining = remainingDebt / avgMonthlyPayment;
            projectedPayoffDate = new Date();
            projectedPayoffDate.setMonth(projectedPayoffDate.getMonth() + Math.ceil(monthsRemaining));
        }

        return {
            totalPaid,
            remainingDebt: Math.max(0, remainingDebt),
            percentComplete: Math.min(100, percentComplete),
            avgMonthlyPayment,
            projectedPayoffDate,
            streakDays: paymentStats.current_streak_days || 0,
        };
    };

    const metrics = calculateMetrics();

    // Format date
    const formatDate = (date: Date | string) => {
        return new Date(date).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
        });
    };

    // Export payments data
    const handleExport = () => {
        const csvContent = [
            ['Date', 'Debt', 'Amount', 'Method', 'Notes'].join(','),
            ...payments.map(p => [
                formatDate(p.payment_date),
                debts.find(d => d.id === p.debt_id)?.creditor_name || 'Unknown',
                p.amount,
                p.payment_method || 'N/A',
                `"${(p.notes || '').replace(/"/g, '""')}"`,
            ].join(',')),
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `debt-payments-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => navigate('/dashboard')}
                            >
                                <ArrowLeft className="w-4 h-4 mr-2" />
                                Dashboard
                            </Button>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">
                                    Progress Tracker
                                </h1>
                                <p className="text-gray-500 text-sm">
                                    Track your debt payoff journey
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            {/* Date Range Filter */}
                            <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
                                <Filter className="w-4 h-4 text-gray-500 ml-2" />
                                {(['30', '90', '180', '365'] as DateRange[]).map((range) => (
                                    <button
                                        key={range}
                                        onClick={() => setDateRange(range)}
                                        className={`px-3 py-1 text-sm rounded-md transition-colors ${
                                            dateRange === range
                                                ? 'bg-white shadow text-primary-600'
                                                : 'text-gray-600 hover:text-gray-900'
                                        }`}
                                    >
                                        {range === '365' ? '1Y' : `${range}D`}
                                    </button>
                                ))}
                            </div>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={handleExport}
                                disabled={payments.length === 0}
                            >
                                <Download className="w-4 h-4 mr-2" />
                                Export
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={fetchProgressData}
                                disabled={loading}
                            >
                                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {loading ? (
                    <div className="flex items-center justify-center h-64">
                        <RefreshCw className="w-8 h-8 text-primary-500 animate-spin" />
                    </div>
                ) : (
                    <div className="space-y-6">
                        {/* Progress Overview */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {/* Total Paid */}
                            <Card>
                                <CardContent className="p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm text-gray-500">Total Paid</p>
                                            <p className="text-2xl font-bold text-success-600">
                                                {formatCurrency(metrics.totalPaid)}
                                            </p>
                                        </div>
                                        <div className="p-3 bg-success-100 rounded-full">
                                            <DollarSign className="w-6 h-6 text-success-600" />
                                        </div>
                                    </div>
                                    <div className="mt-4">
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-gray-500">Progress</span>
                                            <span className="font-medium">
                                                {metrics.percentComplete.toFixed(1)}%
                                            </span>
                                        </div>
                                        <div className="mt-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-success-500 transition-all"
                                                style={{ width: `${metrics.percentComplete}%` }}
                                            />
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Remaining Debt */}
                            <Card>
                                <CardContent className="p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm text-gray-500">Remaining</p>
                                            <p className="text-2xl font-bold text-gray-900">
                                                {formatCurrency(metrics.remainingDebt)}
                                            </p>
                                        </div>
                                        <div className="p-3 bg-gray-100 rounded-full">
                                            <Target className="w-6 h-6 text-gray-600" />
                                        </div>
                                    </div>
                                    {metrics.projectedPayoffDate && (
                                        <p className="mt-4 text-sm text-gray-500">
                                            Est. payoff:{' '}
                                            <span className="font-medium text-gray-700">
                                                {metrics.projectedPayoffDate.toLocaleDateString('en-US', {
                                                    month: 'short',
                                                    year: 'numeric',
                                                })}
                                            </span>
                                        </p>
                                    )}
                                </CardContent>
                            </Card>

                            {/* Monthly Average */}
                            <Card>
                                <CardContent className="p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm text-gray-500">Monthly Avg</p>
                                            <p className="text-2xl font-bold text-primary-600">
                                                {formatCurrency(metrics.avgMonthlyPayment)}
                                            </p>
                                        </div>
                                        <div className="p-3 bg-primary-100 rounded-full">
                                            <TrendingUp className="w-6 h-6 text-primary-600" />
                                        </div>
                                    </div>
                                    <p className="mt-4 text-sm text-gray-500">
                                        Based on your payment history
                                    </p>
                                </CardContent>
                            </Card>

                            {/* Payment Streak */}
                            <Card>
                                <CardContent className="p-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm text-gray-500">Streak</p>
                                            <p className="text-2xl font-bold text-warning-600">
                                                {metrics.streakDays} days
                                            </p>
                                        </div>
                                        <div className="p-3 bg-warning-100 rounded-full">
                                            <Award className="w-6 h-6 text-warning-600" />
                                        </div>
                                    </div>
                                    <p className="mt-4 text-sm text-gray-500">
                                        {metrics.streakDays > 0 
                                            ? 'Keep it up! 🔥' 
                                            : 'Log a payment to start'}
                                    </p>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Charts Section */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Payment History Chart */}
                            <ProgressChart 
                                payments={payments}
                                title="Payment History"
                            />

                            {/* Debt Reduction Chart */}
                            <ProgressChart 
                                payments={payments}
                                title="Monthly Progress"
                                showPrincipalInterest
                            />
                        </div>

                        {/* Milestones */}
                        {milestones && milestones.milestones.length > 0 && (
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Award className="w-5 h-5" />
                                        Achievements
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                        {milestones.milestones.map((milestone, index) => (
                                            <div
                                                key={index}
                                                className="flex items-center gap-3 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200"
                                            >
                                                <div className="text-2xl">{milestone.badge_name || '🏆'}</div>
                                                <div>
                                                    <p className="font-medium text-gray-900">
                                                        {milestone.title}
                                                    </p>
                                                    <p className="text-sm text-gray-600">
                                                        {milestone.description}
                                                    </p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        {/* Payment History Table */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Calendar className="w-5 h-5" />
                                    Payment History
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {payments.length === 0 ? (
                                    <div className="text-center py-8 text-gray-500">
                                        <DollarSign className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                                        <p>No payments recorded yet</p>
                                        <p className="text-sm mt-1">
                                            Start logging payments from the dashboard
                                        </p>
                                    </div>
                                ) : (
                                    <div className="overflow-x-auto">
                                        <table className="w-full">
                                            <thead>
                                                <tr className="border-b border-gray-200">
                                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                                                        Date
                                                    </th>
                                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                                                        Debt
                                                    </th>
                                                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                                                        Amount
                                                    </th>
                                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                                                        Method
                                                    </th>
                                                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                                                        Notes
                                                    </th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {payments.slice(0, 20).map((payment) => {
                                                    const debt = debts.find(d => d.id === payment.debt_id);
                                                    return (
                                                        <tr 
                                                            key={payment.id}
                                                            className="border-b border-gray-100 hover:bg-gray-50"
                                                        >
                                                            <td className="py-3 px-4 text-sm text-gray-900">
                                                                {formatDate(payment.payment_date)}
                                                            </td>
                                                            <td className="py-3 px-4 text-sm text-gray-900">
                                                                {debt?.creditor_name || 'Unknown Debt'}
                                                            </td>
                                                            <td className="py-3 px-4 text-sm text-right font-medium text-success-600">
                                                                {formatCurrency(payment.amount)}
                                                            </td>
                                                            <td className="py-3 px-4 text-sm text-gray-600">
                                                                {payment.payment_method || '-'}
                                                            </td>
                                                            <td className="py-3 px-4 text-sm text-gray-500 max-w-xs truncate">
                                                                {payment.notes || '-'}
                                                            </td>
                                                        </tr>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                        {payments.length > 20 && (
                                            <p className="text-center text-sm text-gray-500 py-4">
                                                Showing 20 of {payments.length} payments
                                            </p>
                                        )}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                )}
            </main>
        </div>
    );
}
