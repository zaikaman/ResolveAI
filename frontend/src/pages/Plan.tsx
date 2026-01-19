/**
 * Plan page - Full plan view with timeline, schedule, and summary
 * Design aligned with landing page styling
 */

import { useEffect, useState } from 'react';
import { RefreshCw, Settings, Sparkles } from 'lucide-react';
import { PlanSummary } from '../components/plan/PlanSummary';
import { PlanTimeline } from '../components/plan/PlanTimeline';
import { PaymentSchedule } from '../components/plan/PaymentSchedule';
import { Modal } from '../components/common/Modal';
import { Button } from '../components/common/Button';
import { Card, CardContent } from '../components/common/Card';
import { usePlan } from '../hooks/usePlan';
import { useDebts } from '../hooks/useDebts';
import { cn } from '../utils/cn';

export default function Plan() {
    const {
        activePlan,
        loading,
        generating,
        fetchActivePlan,
        generatePlan,
        recalculatePlan,
    } = usePlan();

    const { activeDebts, fetchDebts } = useDebts();

    const [showSettingsModal, setShowSettingsModal] = useState(false);
    const [selectedStrategy, setSelectedStrategy] = useState<'avalanche' | 'snowball'>('avalanche');
    const [extraPayment, setExtraPayment] = useState(0);

    useEffect(() => {
        fetchActivePlan();
        fetchDebts();
    }, [fetchActivePlan, fetchDebts]);

    useEffect(() => {
        if (activePlan) {
            setSelectedStrategy(activePlan.strategy);
            setExtraPayment(activePlan.extra_payment);
        }
    }, [activePlan]);

    const handleGeneratePlan = async () => {
        try {
            await generatePlan({
                strategy: selectedStrategy,
                extra_monthly_payment: extraPayment,
            });
        } catch (err) {
            console.error('Failed to generate plan:', err);
        }
    };

    const handleRecalculate = async () => {
        if (activePlan) {
            try {
                await recalculatePlan(activePlan.id, {
                    strategy: selectedStrategy,
                    extraPayment,
                });
                setShowSettingsModal(false);
            } catch (err) {
                console.error('Failed to recalculate:', err);
            }
        }
    };

    // No debts state
    if (!loading && activeDebts.length === 0) {
        return (
            <div className="space-y-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">My Plan</h1>
                    <p className="text-slate-500">Your optimized debt repayment strategy</p>
                </div>

                <Card className="text-center py-16">
                    <CardContent>
                        <div className="mx-auto w-16 h-16 bg-main2 rounded-full flex items-center justify-center mb-4">
                            <Sparkles className="h-8 w-8 text-main" />
                        </div>
                        <h3 className="text-xl font-semibold text-slate-900 mb-2">Add Debts First</h3>
                        <p className="text-slate-500 mb-6 max-w-sm mx-auto">
                            Before we can create your personalized repayment plan, you need to add your debts.
                        </p>
                        <Button onClick={() => window.location.href = '/debts'}>
                            Go to My Debts
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    // No plan yet state
    if (!loading && !activePlan && activeDebts.length > 0) {
        return (
            <div className="space-y-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">My Plan</h1>
                    <p className="text-slate-500">Your optimized debt repayment strategy</p>
                </div>

                <Card className="text-center py-16">
                    <CardContent className="space-y-6">
                        <div className="mx-auto w-20 h-20 bg-gradient-to-br from-main to-blue-700 rounded-full flex items-center justify-center mb-4">
                            <Sparkles className="h-10 w-10 text-white" />
                        </div>
                        <div>
                            <h3 className="text-xl font-semibold text-slate-900 mb-2">Ready to Create Your Plan</h3>
                            <p className="text-slate-500 max-w-md mx-auto">
                                You have {activeDebts.length} active debt{activeDebts.length !== 1 ? 's' : ''}.
                                Let our AI create an optimized repayment strategy for you.
                            </p>
                        </div>

                        {/* Strategy selector */}
                        <div className="max-w-md mx-auto space-y-4">
                            <p className="text-sm font-medium text-slate-700">Choose your strategy:</p>
                            <div className="grid grid-cols-2 gap-3">
                                <button
                                    type="button"
                                    onClick={() => setSelectedStrategy('avalanche')}
                                    className={cn(
                                        "p-4 rounded-lg border-2 text-left transition-all",
                                        selectedStrategy === 'avalanche'
                                            ? "border-main bg-main3"
                                            : "border-slate-200 hover:border-main/50"
                                    )}
                                >
                                    <p className="font-semibold text-slate-900">Avalanche</p>
                                    <p className="text-sm text-slate-500">Pay highest APR first</p>
                                    <p className="text-xs text-main mt-1">Saves the most money</p>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setSelectedStrategy('snowball')}
                                    className={cn(
                                        "p-4 rounded-lg border-2 text-left transition-all",
                                        selectedStrategy === 'snowball'
                                            ? "border-main bg-main3"
                                            : "border-slate-200 hover:border-main/50"
                                    )}
                                >
                                    <p className="font-semibold text-slate-900">Snowball</p>
                                    <p className="text-sm text-slate-500">Pay lowest balance first</p>
                                    <p className="text-xs text-main mt-1">Quick wins for motivation</p>
                                </button>
                            </div>

                            {/* Extra payment input */}
                            <div>
                                <label className="text-sm font-medium text-slate-700 block mb-2">
                                    Extra monthly payment (optional)
                                </label>
                                <input
                                    type="number"
                                    value={extraPayment || ''}
                                    onChange={(e) => setExtraPayment(parseFloat(e.target.value) || 0)}
                                    placeholder="0"
                                    className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-main"
                                />
                                <p className="text-xs text-slate-500 mt-1">
                                    Extra payment above minimum amounts each month
                                </p>
                            </div>
                        </div>

                        <Button
                            size="lg"
                            onClick={handleGeneratePlan}
                            isLoading={generating}
                            leftIcon={<Sparkles className="h-5 w-5" />}
                        >
                            Generate My Plan
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">My Plan</h1>
                    <p className="text-slate-500">Your optimized debt repayment strategy</p>
                </div>
                <div className="flex gap-3">
                    <Button
                        variant="outline"
                        onClick={() => setShowSettingsModal(true)}
                        leftIcon={<Settings className="h-4 w-4" />}
                    >
                        Adjust Plan
                    </Button>
                </div>
            </div>

            {loading ? (
                // Loading skeleton
                <div className="space-y-6">
                    <Card className="animate-pulse">
                        <CardContent className="py-8">
                            <div className="h-8 bg-slate-200 rounded w-1/3 mb-4" />
                            <div className="h-12 bg-slate-200 rounded w-1/2" />
                        </CardContent>
                    </Card>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        {[1, 2, 3, 4].map(i => (
                            <Card key={i} className="animate-pulse">
                                <CardContent className="py-4">
                                    <div className="h-4 bg-slate-200 rounded w-1/2 mb-2" />
                                    <div className="h-8 bg-slate-200 rounded w-2/3" />
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            ) : activePlan ? (
                <>
                    {/* Plan Summary */}
                    <PlanSummary
                        debtFreeDate={activePlan.debt_free_date}
                        totalMonths={activePlan.total_months}
                        totalInterest={activePlan.total_interest}
                        interestSaved={activePlan.interest_saved}
                        monthsSaved={activePlan.months_saved}
                        monthlyPayment={activePlan.monthly_payment}
                        strategy={activePlan.strategy}
                    />

                    {/* Timeline Chart */}
                    <PlanTimeline projections={activePlan.projections} />

                    {/* Payment Schedule */}
                    <PaymentSchedule schedule={activePlan.monthly_schedule} />
                </>
            ) : null}

            {/* Settings Modal */}
            <Modal
                isOpen={showSettingsModal}
                onClose={() => setShowSettingsModal(false)}
                title="Adjust Your Plan"
                size="md"
                footer={
                    <div className="flex justify-end gap-3">
                        <Button variant="outline" onClick={() => setShowSettingsModal(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleRecalculate} isLoading={generating}>
                            <RefreshCw className="h-4 w-4 mr-2" />
                            Recalculate
                        </Button>
                    </div>
                }
            >
                <div className="space-y-6">
                    {/* Strategy selector */}
                    <div>
                        <label className="text-sm font-medium text-slate-700 block mb-2">
                            Repayment Strategy
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                type="button"
                                onClick={() => setSelectedStrategy('avalanche')}
                                className={cn(
                                    "p-4 rounded-lg border-2 text-left transition-all",
                                    selectedStrategy === 'avalanche'
                                        ? "border-main bg-main3"
                                        : "border-slate-200 hover:border-main/50"
                                )}
                            >
                                <p className="font-semibold text-slate-900">Avalanche</p>
                                <p className="text-sm text-slate-500">Highest APR first</p>
                            </button>
                            <button
                                type="button"
                                onClick={() => setSelectedStrategy('snowball')}
                                className={cn(
                                    "p-4 rounded-lg border-2 text-left transition-all",
                                    selectedStrategy === 'snowball'
                                        ? "border-main bg-main3"
                                        : "border-slate-200 hover:border-main/50"
                                )}
                            >
                                <p className="font-semibold text-slate-900">Snowball</p>
                                <p className="text-sm text-slate-500">Lowest balance first</p>
                            </button>
                        </div>
                    </div>

                    {/* Extra payment */}
                    <div>
                        <label className="text-sm font-medium text-slate-700 block mb-2">
                            Extra Monthly Payment
                        </label>
                        <input
                            type="number"
                            value={extraPayment || ''}
                            onChange={(e) => setExtraPayment(parseFloat(e.target.value) || 0)}
                            placeholder="0"
                            className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-main"
                        />
                        <p className="text-xs text-slate-500 mt-1">
                            Additional amount to pay above minimums each month
                        </p>
                    </div>
                </div>
            </Modal>
        </div>
    );
}
