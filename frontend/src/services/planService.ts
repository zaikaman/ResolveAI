/**
 * Plan API service for plan generation and management
 */

import api from './api';
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
     * Generate a new repayment plan
     */
    async generatePlan(request: PlanRequest = {}): Promise<Plan> {
        const response = await api.post<Plan>('/plans/generate', request);
        return response.data;
    }

    /**
     * Recalculate an existing plan with new parameters
     */
    async recalculatePlan(request: RecalculationRequest): Promise<Plan> {
        const response = await api.post<Plan>('/plans/recalculate', request);
        return response.data;
    }

    /**
     * Simulate a what-if scenario without saving
     */
    async simulate(request: SimulationRequest): Promise<SimulationResult> {
        const response = await api.post<SimulationResult>('/plans/simulate', request);
        return response.data;
    }

    /**
     * Mark a plan as completed
     */
    async completePlan(planId: string): Promise<Plan> {
        const response = await api.post<Plan>(`/plans/${planId}/complete`);
        return response.data;
    }
}

export const planService = new PlanService();
export default planService;
