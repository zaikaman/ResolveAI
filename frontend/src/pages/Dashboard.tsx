/**
 * Dashboard page - Daily actions + progress overview
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, RefreshCw, ArrowRight } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useDebts } from '../hooks/useDebts';
import { usePlan } from '../hooks/usePlan';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { DailyActions } from '../components/progress/DailyActions';
import { PaymentLogger, type PaymentLogData } from '../components/progress/PaymentLogger';
import { ProgressDashboard } from '../components/progress/ProgressDashboard';
import { ProgressChart } from '../components/progress/ProgressChart';
import { CelebrationModal } from '../components/progress/MilestoneCard';
import paymentService, { 
    type DailyActionsResponse, 
    type PaymentStats, 
    type RecentPaymentSummary,
    type Payment,
    type MilestoneCheckResult,
    type DailyAction
} from '../services/paymentService';

export default function Dashboard() {
    const { user } = useAuth();
    const { debts, fetchDebts } = useDebts();
    const { planSummary, fetchPlanSummary } = usePlan();
    const navigate = useNavigate();

    // State
    const [loading, setLoading] = useState(true);
    const [dailyActions, setDailyActions] = useState<DailyActionsResponse | null>(null);
    const [paymentStats, setPaymentStats] = useState<PaymentStats | null>(null);
    const [paymentSummary, setPaymentSummary] = useState<RecentPaymentSummary | null>(null);
    const [recentPayments, setRecentPayments] = useState<Payment[]>([]);
    const [showPaymentModal, setShowPaymentModal] = useState(false);
    const [selectedDebtId, setSelectedDebtId] = useState<string | undefined>();
    const [suggestedAmount, setSuggestedAmount] = useState<number | undefined>();
    const [celebrationMilestones, setCelebrationMilestones] = useState<MilestoneCheckResult | null>(null);
    const [showCelebration, setShowCelebration] = useState(false);

    // Fetch all dashboard data
    const fetchDashboardData = useCallback(async () => {
        setLoading(true);
        try {
            // Fetch in parallel
            const [
                actionsData,
                statsData,
                summaryData,
                paymentsData,
            ] = await Promise.all([
                paymentService.getDailyActions().catch(() => null),
                paymentService.getPaymentStats().catch(() => null),
                paymentService.getPaymentSummary().catch(() => null),
                paymentService.getRecentPayments(90, 20).catch(() => []),
            ]);

            setDailyActions(actionsData);
            setPaymentStats(statsData);
            setPaymentSummary(summaryData);
            setRecentPayments(paymentsData);

            // Also fetch debts and plan if not already loaded
            await Promise.all([
                fetchDebts().catch(() => {}),
                fetchPlanSummary().catch(() => {}),
            ]);
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
        } finally {
            setLoading(false);
        }
    }, [fetchDebts, fetchPlanSummary]);

    useEffect(() => {
        fetchDashboardData();
    }, [fetchDashboardData]);

    // Handle payment action from daily actions
    const handlePayAction = (action: DailyAction) => {
        setSelectedDebtId(action.debt_id);
        setSuggestedAmount(action.suggested_amount);
        setShowPaymentModal(true);
    };

    // Handle view action from daily actions
    const handleViewAction = (action: DailyAction) => {
        if (action.action_type === 'review') {
            navigate('/plan');
        } else if (action.debt_id) {
            navigate('/debts');
        }
    };

    // Handle payment submission
    const handlePaymentSubmit = async (data: PaymentLogData) => {
        const result = await paymentService.logPayment(data);
        
        // Check for milestones
        if (result.milestones?.has_new_milestones) {
            setCelebrationMilestones(result.milestones);
            setShowCelebration(true);
        }

        // Refresh dashboard data
        await fetchDashboardData();
    };

    // Calculate total debt
    const totalDebt = debts.reduce((sum, d) => d.is_active && !d.is_paid_off ? sum + d.balance : sum, 0);
    const originalDebt = totalDebt + (paymentStats?.total_amount_paid || 0);

    // Check if user has started (has debts or payments)
    const hasStarted = debts.length > 0 || (paymentStats?.total_payments || 0) > 0;

    return (
        <div className="space-y-8">
            {/* Welcome Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">
                        Welcome back, {user?.full_name?.split(' ')[0] || 'there'}!
                    </h1>
                    <p className="text-slate-500 mt-1">
                        {dailyActions?.summary || "Here's your debt freedom progress."}
                    </p>
                </div>
                <div className="flex gap-3">
                    <Button 
                        variant="secondary"
                        onClick={() => fetchDashboardData()}
                        leftIcon={<RefreshCw className="h-4 w-4" />}
                    >
                        Refresh
                    </Button>
                    <Button 
                        onClick={() => {
                            setSelectedDebtId(undefined);
                            setSuggestedAmount(undefined);
                            setShowPaymentModal(true);
                        }}
                        leftIcon={<Plus className="h-4 w-4" />}
                    >
                        Log Payment
                    </Button>
                </div>
            </div>

            {/* Progress Dashboard */}
            <ProgressDashboard
                paymentStats={paymentStats}
                paymentSummary={paymentSummary}
                planSummary={planSummary}
                totalDebt={totalDebt}
                originalDebt={originalDebt}
                loading={loading}
            />

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Daily Actions - 2 columns */}
                <div className="lg:col-span-2">
                    <DailyActions
                        actionsData={dailyActions}
                        loading={loading}
                        onPayAction={handlePayAction}
                        onViewAction={handleViewAction}
                    />
                </div>

                {/* Quick Stats & Recent Activity - 1 column */}
                <div className="space-y-6">
                    {/* Recent Payments */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Recent Activity</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {recentPayments.length === 0 ? (
                                <div className="text-center py-6">
                                    <p className="text-slate-500 text-sm">No payments yet</p>
                                    <Button 
                                        variant="secondary" 
                                        size="sm" 
                                        className="mt-2"
                                        onClick={() => setShowPaymentModal(true)}
                                    >
                                        Log your first payment
                                    </Button>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {recentPayments.slice(0, 5).map((payment) => (
                                        <div 
                                            key={payment.id} 
                                            className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0"
                                        >
                                            <div>
                                                <p className="font-medium text-slate-900 text-sm">
                                                    {payment.debt_name || 'Payment'}
                                                </p>
                                                <p className="text-xs text-slate-500">
                                                    {new Date(payment.payment_date).toLocaleDateString()}
                                                </p>
                                            </div>
                                            <span className="font-semibold text-green-600">
                                                -${payment.amount.toFixed(2)}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Quick Actions */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Quick Actions</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            <Button 
                                variant="secondary" 
                                className="w-full justify-start"
                                onClick={() => navigate('/debts')}
                            >
                                Manage Debts
                            </Button>
                            <Button 
                                variant="secondary" 
                                className="w-full justify-start"
                                onClick={() => navigate('/plan')}
                            >
                                View Full Plan
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>

            {/* Payment History Chart */}
            {recentPayments.length > 0 && (
                <ProgressChart
                    payments={recentPayments}
                    loading={loading}
                    title="Payment History"
                />
            )}

            {/* Getting Started Section (shown when user hasn't started yet) */}
            {!hasStarted && !loading && (
                <div>
                    <h2 className="text-xl font-bold text-slate-900 mb-4">Get Started</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <Card hoverable onClick={() => navigate('/debts')} className="cursor-pointer group">
                            <CardHeader>
                                <CardTitle className="flex items-center justify-between">
                                    1. Add Your Debts
                                    <ArrowRight className="h-5 w-5 text-slate-400 group-hover:text-main transition-colors" />
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-slate-500">
                                    List all your current debts or scan your statements to get a clear picture of what you owe.
                                </p>
                            </CardContent>
                        </Card>

                        <Card hoverable onClick={() => navigate('/plan')} className="cursor-pointer group">
                            <CardHeader>
                                <CardTitle className="flex items-center justify-between">
                                    2. Create Your Plan
                                    <ArrowRight className="h-5 w-5 text-slate-400 group-hover:text-main transition-colors" />
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-slate-500">
                                    Generate a personalized repayment strategy to become debt-free faster and save on interest.
                                </p>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            )}

            {/* Payment Logger Modal */}
            <PaymentLogger
                isOpen={showPaymentModal}
                onClose={() => {
                    setShowPaymentModal(false);
                    setSelectedDebtId(undefined);
                    setSuggestedAmount(undefined);
                }}
                onSubmit={handlePaymentSubmit}
                debts={debts}
                preselectedDebtId={selectedDebtId}
                suggestedAmount={suggestedAmount}
            />

            {/* Celebration Modal */}
            {celebrationMilestones && (
                <CelebrationModal
                    isOpen={showCelebration}
                    onClose={() => {
                        setShowCelebration(false);
                        setCelebrationMilestones(null);
                    }}
                    milestones={celebrationMilestones}
                />
            )}
        </div>
    );
}
