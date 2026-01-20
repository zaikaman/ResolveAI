/**
 * usePlan hook - Manage plan operations with store integration
 */

import { useCallback } from 'react';
import { flushSync } from 'react-dom';
import { usePlanStore } from '../stores/planStore';
import planService from '../services/planService';
import type { PlanRequest, SimulationRequest } from '../services/planService';

export function usePlan() {
    const {
        activePlan,
        planSummary,
        simulationResult,
        loading,
        generating,
        error,
        setActivePlan,
        setPlanSummary,
        setSimulationResult,
        setLoading,
        setGenerating,
        setError,
    } = usePlanStore();

    /**
     * Fetch the active plan
     */
    const fetchActivePlan = useCallback(async () => {
        setLoading(true);
        try {
            const plan = await planService.getActivePlan();
            setActivePlan(plan);
            return plan;
        } catch (err: any) {
            if (err.response?.status === 404) {
                // No active plan is not an error - don't call setError
                setActivePlan(null);
                return null;
            }
            setError(err.message || 'Failed to fetch plan');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [setActivePlan, setLoading, setError]);

    /**
     * Fetch plan summary (lightweight)
     */
    const fetchPlanSummary = useCallback(async () => {
        try {
            const summary = await planService.getPlanSummary();
            setPlanSummary(summary);
            return summary;
        } catch (err: any) {
            if (err.response?.status === 404) {
                setPlanSummary(null);
                return null;
            }
            throw err;
        }
    }, [setPlanSummary]);

    /**
     * Generate a new plan
     */
    const generatePlan = useCallback(async (request: PlanRequest = {}) => {
        console.log('[usePlan] Setting generating to true');
        flushSync(() => {
            setGenerating(true);
            setError(null);
        });
        console.log('[usePlan] After flushSync, should be true now');
        try {
            console.log('[usePlan] Calling planService.generatePlan');
            const plan = await planService.generatePlan(request);
            console.log('[usePlan] Plan generated successfully');
            setActivePlan(plan);
            return plan;
        } catch (err: any) {
            console.log('[usePlan] Error generating plan:', err);
            setError(err.message || 'Failed to generate plan');
            throw err;
        } finally {
            console.log('[usePlan] Setting generating to false');
            setGenerating(false);
        }
    }, [setActivePlan, setGenerating, setError]);

    /**
     * Recalculate the current plan with new parameters
     */
    const recalculatePlan = useCallback(async (
        planId: string,
        options: {
            strategy?: 'avalanche' | 'snowball';
            extraPayment?: number;
            customBudget?: number;
        }
    ) => {
        setGenerating(true);
        setError(null);
        try {
            const plan = await planService.recalculatePlan({
                plan_id: planId,
                strategy: options.strategy,
                extra_monthly_payment: options.extraPayment,
                custom_monthly_budget: options.customBudget,
            });
            setActivePlan(plan);
            return plan;
        } catch (err: any) {
            setError(err.message || 'Failed to recalculate plan');
            throw err;
        } finally {
            setGenerating(false);
        }
    }, [setActivePlan, setGenerating, setError]);

    /**
     * Simulate a what-if scenario
     */
    const simulate = useCallback(async (request: SimulationRequest) => {
        setLoading(true);
        setError(null);
        try {
            const result = await planService.simulate(request);
            setSimulationResult(result);
            return result;
        } catch (err: any) {
            setError(err.message || 'Failed to run simulation');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [setSimulationResult, setLoading, setError]);

    /**
     * Clear simulation result
     */
    const clearSimulation = useCallback(() => {
        setSimulationResult(null);
    }, [setSimulationResult]);

    /**
     * Mark plan as completed
     */
    const completePlan = useCallback(async (planId: string) => {
        setLoading(true);
        try {
            const plan = await planService.completePlan(planId);
            setActivePlan(plan);
            return plan;
        } catch (err: any) {
            setError(err.message || 'Failed to complete plan');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [setActivePlan, setLoading, setError]);

    return {
        // State
        activePlan,
        planSummary,
        simulationResult,
        loading,
        generating,
        error,

        // Actions
        fetchActivePlan,
        fetchPlanSummary,
        generatePlan,
        recalculatePlan,
        simulate,
        clearSimulation,
        completePlan,

        // Computed
        hasPlan: !!activePlan,
        isActive: activePlan?.status === 'active',
    };
}
