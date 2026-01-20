/**
 * Plan API service for plan generation and management
 */

import api from './api';
import { createAndPollJob } from './jobPolling';
import type { JobPollOptions } from './jobPolling';
import type { Plan, PlanSummary, SimulationResult } from '../stores/planStore';

export interface PlanRequest {
    strategy?: 'avalanche' | 'snowball';
    extra_monthly_payment?: number;
    start_date?: string;
    custom_monthly_budget?: number;
}

export interface RecalculationRequest {
    plan_id: string;
    strategy?: 'avalanche' | 'snowball';
    extra_monthly_payment?: number;
    custom_monthly_budget?: number;
    reason?: string;
}

export interface SimulationRequest {
    strategy?: 'avalanche' | 'snowball';
    extra_monthly_payment?: number;
    income_change?: number;
    lump_sum_payment?: number;
    lump_sum_target_debt_id?: string;
    rate_reduction?: Record<string, number>;
}

class PlanService {
    /**
     * Get the active plan for the current user
     */
    async getActivePlan(): Promise<Plan> {
        const response = await api.get<Plan>('/plans/active');
        return response.data;
    }

    /**
     * Get a lightweight plan summary for dashboard
     */
    async getPlanSummary(): Promise<PlanSummary> {
        const response = await api.get<PlanSummary>('/plans/summary');
        return response.data;
    }

    /**
     * Generate a new repayment plan (async with polling)
     */
    async generatePlan(
        request: PlanRequest = {},
        options?: JobPollOptions
    ): Promise<Plan> {
        return createAndPollJob<Plan>(
            () => api.post('/plans/generate', request),
            options
        );
    }

    /**
     * Recalculate an existing plan with new parameters (async with polling)
     */
    async recalculatePlan(
        request: RecalculationRequest,
        options?: JobPollOptions
    ): Promise<Plan> {
        return createAndPollJob<Plan>(
            () => api.post('/plans/recalculate', request),
            options
        );
    }

    /**
     * Simulate a what-if scenario without saving (async with polling)
     */
    async simulate(
        request: SimulationRequest,
        options?: JobPollOptions
    ): Promise<SimulationResult> {
        return createAndPollJob<SimulationResult>(
            () => api.post('/plans/simulate', request),
            options
        );
    }

    /**
     * Mark a plan as completed
     */
    async completePlan(planId: string): Promise<Plan> {
        const response = await api.post<Plan>(`/plans/${planId}/complete`);
        return response.data;
    }

    /**
     * Get daily actions (async with polling)
     */
    async getDailyActions(options?: JobPollOptions): Promise<any> {
        return createAndPollJob(
            () => api.get('/plans/actions/daily'),
            options
        );
    }
}

export const planService = new PlanService();
export default planService;
