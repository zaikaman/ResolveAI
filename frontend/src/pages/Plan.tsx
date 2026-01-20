/**
 * Plan page - Full plan view with timeline, schedule, and summary
 * Design aligned with landing page styling
 */

import { useEffect, useState } from 'react';
import { RefreshCw, Settings, Sparkles, Lightbulb, Brain, Calculator, TrendingUp, Target } from 'lucide-react';
import { PlanSummary } from '../components/plan/PlanSummary';
import { PlanTimeline } from '../components/plan/PlanTimeline';
import { PaymentSchedule } from '../components/plan/PaymentSchedule';
import { Modal } from '../components/common/Modal';
import { Button } from '../components/common/Button';
import { Card, CardContent } from '../components/common/Card';
import { usePlan } from '../hooks/usePlan';
import { useDebts } from '../hooks/useDebts';
import { cn } from '../utils/cn';

const loadingSteps = [
    { icon: Brain, text: 'Analyzing your debts...', duration: 2000 },
    { icon: Calculator, text: 'Calculating optimal strategy...', duration: 2500 },
    { icon: TrendingUp, text: 'Generating payment schedule...', duration: 2000 },
    { icon: Target, text: 'Finalizing your plan...', duration: 1500 },
];

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
    const [loadingStep, setLoadingStep] = useState(0);
    const [progress, setProgress] = useState(0);

    // Debug logging
    console.log('Plan component render - generating:', generating, 'loading:', loading, 'activePlan:', !!activePlan, 'activeDebts:', activeDebts.length);

    useEffect(() => {
        fetchActivePlan().catch(err => {
            console.error('Error fetching active plan:', err);
        });
        fetchDebts().catch(err => {
            console.error('Error fetching debts:', err);
        });
    }, [fetchActivePlan, fetchDebts]);

    useEffect(() => {
        if (activePlan) {
            setSelectedStrategy(activePlan.strategy);
            setExtraPayment(activePlan.extra_payment);
        }
    }, [activePlan]);

    // Animated loading progress
    useEffect(() => {
        if (!generating) {
            setLoadingStep(0);
            setProgress(0);
            return;
        }

        let currentStep = 0;
        let currentProgress = 0;
        setLoadingStep(0);
        setProgress(0);

        const progressPerStep = 100 / loadingSteps.length;
        
        const stepInterval = setInterval(() => {
            currentStep++;
            if (currentStep < loadingSteps.length) {
                setLoadingStep(currentStep);
            } else {
                clearInterval(stepInterval);
            }
        }, 2000);

        const progressInterval = setInterval(() => {
            currentProgress += 1;
            if (currentProgress <= 95) {
                setProgress(currentProgress);
            } else {
                clearInterval(progressInterval);
            }
        }, 80);

        return () => {
            clearInterval(stepInterval);
            clearInterval(progressInterval);
        };
    }, [generating]);

    const handleGeneratePlan = async () => {
        try {
            console.log('Generating plan, generating state:', generating);
            await generatePlan({
                strategy: selectedStrategy,
                extra_monthly_payment: extraPayment,
            });
            console.log('Plan generated, generating state:', generating);
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

    // Show loading state when generating (whether or not there's an existing plan)
    if (generating) {
        const currentStepData = loadingSteps[loadingStep];
        const StepIcon = currentStepData.icon;

        return (
            <div className="space-y-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">My Plan</h1>
                    <p className="text-slate-500">Your optimized debt repayment strategy</p>
                </div>

                <Card className="text-center py-16 overflow-hidden relative">
                    {/* Animated background gradient */}
                    <div className="absolute inset-0 bg-gradient-to-br from-main/5 via-blue-50 to-purple-50 animate-pulse" />
                    
                    <CardContent className="relative space-y-8">
                        {/* Animated icon */}
                        <div className="mx-auto w-24 h-24 bg-gradient-to-br from-main to-blue-700 rounded-full flex items-center justify-center mb-4 animate-bounce shadow-lg">
                            <StepIcon className="h-12 w-12 text-white" />
                        </div>

                        {/* Current step text */}
                        <div className="space-y-2">
                            <h3 className="text-2xl font-bold text-slate-900 animate-pulse">
                                {currentStepData.text}
                            </h3>
                            <p className="text-slate-500">
                                Our AI is working on your personalized plan
                            </p>
                        </div>

                        {/* Progress bar */}
                        <div className="max-w-md mx-auto space-y-3">
                            <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                                <div 
                                    className="h-full bg-gradient-to-r from-main via-blue-600 to-purple-600 rounded-full transition-all duration-300 ease-out relative overflow-hidden"
                                    style={{ width: `${progress}%` }}
                                >
                                    {/* Shimmer effect */}
                                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                                </div>
                            </div>
                            <div className="flex justify-between text-sm text-slate-600">
                                <span>Progress</span>
                                <span className="font-semibold">{progress}%</span>
                            </div>
                        </div>

                        {/* Step indicators */}
                        <div className="flex justify-center gap-2 max-w-xs mx-auto">
                            {loadingSteps.map((step, idx) => (
                                <div
                                    key={idx}
                                    className={cn(
                                        "flex-1 h-1.5 rounded-full transition-all duration-300",
                                        idx <= loadingStep
                                            ? "bg-gradient-to-r from-main to-blue-600"
                                            : "bg-slate-200"
                                    )}
                                />
                            ))}
                        </div>

                        {/* Tips while waiting */}
                        <div className="max-w-sm mx-auto text-sm text-slate-600 bg-blue-50 p-4 rounded-lg">
                            <p className="flex items-center gap-2 justify-center">
                                <Lightbulb className="h-4 w-4 text-blue-600" />
                                <span className="font-medium">Tip:</span>
                                <span>Small extra payments can shave months off your timeline!</span>
                            </p>
                        </div>
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
                            disabled={generating}
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

                    {/* AI Insights */}
                    {activePlan.ai_explanation && (
                        <Card className="bg-gradient-to-br from-main3 to-blue-50 border-main/20">
                            <CardContent className="py-6">
                                <div className="flex items-start gap-4">
                                    <div className="flex-shrink-0">
                                        <div className="w-12 h-12 bg-gradient-to-br from-main to-blue-700 rounded-full flex items-center justify-center">
                                            <Lightbulb className="h-6 w-6 text-white" />
                                        </div>
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-lg font-semibold text-slate-900 mb-2 flex items-center gap-2">
                                            AI Plan Insights
                                            <span className="text-xs font-normal text-main bg-white px-2 py-1 rounded-full">
                                                Powered by AI
                                            </span>
                                        </h3>
                                        <div className="text-slate-700 whitespace-pre-line leading-relaxed">
                                            {activePlan.ai_explanation}
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}

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
