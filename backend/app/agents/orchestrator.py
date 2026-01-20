"""
Multi-Agent Orchestrator - Coordinates specialized AI agents using ReAct pattern.

Implements adaptive workflow where agents collaborate to transform raw user input
into actionable debt resolution plans. Uses Reason → Act → Observe loops for
dynamic adaptation.
"""

from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel
from enum import Enum
from datetime import date, datetime

from app.agents.base_agent import BaseAgent
from app.agents.assessment_agent import assessment_agent, FinancialAssessment
from app.agents.optimization_agent import optimization_agent, OptimizationResult
from app.agents.action_agent import action_agent, DailyActionsResponse
from app.agents.habit_agent import habit_agent, MilestoneCheckResult
from app.agents.negotiation_agent import negotiation_agent, NegotiationPlan
from app.models.debt import DebtResponse
from app.models.plan import PlanResponse
from app.models.payment import PaymentStats


class AgentPhase(str, Enum):
    """Phases in the orchestrated workflow."""
    ASSESSMENT = "assessment"
    OPTIMIZATION = "optimization"
    ACTION_PLANNING = "action_planning"
    HABIT_MONITORING = "habit_monitoring"
    NEGOTIATION = "negotiation"
    RE_ASSESSMENT = "re_assessment"


class OrchestratorDecision(BaseModel):
    """Orchestrator's reasoning and decision."""
    phase: AgentPhase
    reasoning: str
    next_agent: str
    context_update: Dict[str, Any]
    user_message: Optional[str] = None


class OrchestratorResult(BaseModel):
    """Complete orchestrated result."""
    assessment: Optional[FinancialAssessment] = None
    optimization: Optional[OptimizationResult] = None
    daily_actions: Optional[DailyActionsResponse] = None
    milestones: Optional[MilestoneCheckResult] = None
    negotiation_plans: List[NegotiationPlan] = []
    workflow_trace: List[OrchestratorDecision]
    final_summary: str
    recommended_next_steps: List[str]


class DebtResolutionOrchestrator(BaseAgent):
    """
    Master orchestrator coordinating all specialized agents.
    
    Uses ReAct pattern:
    - Reason: Analyzes current state and decides next action
    - Act: Invokes appropriate specialized agent
    - Observe: Processes agent result and updates context
    - Loop: Continues until goal achieved or max iterations
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Orchestrator",
            description="Coordinates multi-agent workflow for debt resolution"
        )
        self.max_iterations = 10
    
    async def execute_full_workflow(
        self,
        user_id: str,
        debts: List[DebtResponse],
        monthly_income: Optional[float] = None,
        monthly_expenses: Optional[float] = None,
        existing_plan: Optional[PlanResponse] = None,
        user_goal: str = "minimize_debt",
        trigger_event: Optional[str] = None
    ) -> OrchestratorResult:
        """
        Execute complete debt resolution workflow with agent coordination.
        
        Args:
            user_id: User UUID
            debts: User's debts
            monthly_income: Monthly income
            monthly_expenses: Monthly expenses
            existing_plan: Current plan (if any)
            user_goal: User's primary goal (minimize_debt, fast_payoff, etc.)
            trigger_event: What triggered this (new_user, income_change, unexpected_expense, etc.)
        
        Returns:
            Complete orchestrated result with all agent outputs
        """
        return await self.trace_execution(
            self._orchestrate_workflow,
            user_id=user_id,
            debts=debts,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            existing_plan=existing_plan,
            user_goal=user_goal,
            trigger_event=trigger_event
        )
    
    async def handle_user_event(
        self,
        user_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        current_context: Dict[str, Any]
    ) -> OrchestratorResult:
        """
        Handle dynamic user events with adaptive re-planning.
        
        Args:
            user_id: User UUID
            event_type: Type of event (income_change, unexpected_expense, payment_missed, etc.)
            event_data: Event-specific data
            current_context: Current state (debts, plan, etc.)
        
        Returns:
            Updated plan and actions
        """
        return await self.trace_execution(
            self._handle_adaptive_event,
            user_id=user_id,
            event_type=event_type,
            event_data=event_data,
            current_context=current_context
        )
    
    async def _orchestrate_workflow(
        self,
        user_id: str,
        debts: List[DebtResponse],
        monthly_income: Optional[float],
        monthly_expenses: Optional[float],
        existing_plan: Optional[PlanResponse],
        user_goal: str,
        trigger_event: Optional[str]
    ) -> OrchestratorResult:
        """Internal orchestration logic using ReAct pattern."""
        
        workflow_trace: List[OrchestratorDecision] = []
        context = {
            "user_id": user_id,
            "debts": debts,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "existing_plan": existing_plan,
            "user_goal": user_goal,
            "trigger_event": trigger_event or "new_workflow",
            "iteration": 0
        }
        
        assessment_result = None
        optimization_result = None
        daily_actions_result = None
        milestones_result = None
        negotiation_plans = []
        
        # ReAct Loop
        current_phase = self._determine_starting_phase(context)
        
        for iteration in range(self.max_iterations):
            context["iteration"] = iteration
            
            # REASON: Decide what to do next
            decision = self._reason_next_step(context, current_phase)
            workflow_trace.append(decision)
            
            # ACT: Execute the chosen agent
            if decision.phase == AgentPhase.ASSESSMENT:
                assessment_result = await assessment_agent.assess_financial_situation(
                    debts=debts,
                    monthly_income=monthly_income,
                    monthly_expenses=monthly_expenses,
                    ocr_data=context.get("ocr_data")
                )
                context["assessment"] = assessment_result
                current_phase = AgentPhase.OPTIMIZATION
            
            elif decision.phase == AgentPhase.OPTIMIZATION:
                if not assessment_result:
                    # Need assessment first
                    current_phase = AgentPhase.ASSESSMENT
                    continue
                
                optimization_result = await optimization_agent.optimize_repayment_plan(
                    user_id=user_id,
                    debts=debts,
                    monthly_budget=context.get("assessment").available_for_debt or 500,
                    strategy=user_goal,
                    constraints={}
                )
                context["optimization"] = optimization_result
                current_phase = AgentPhase.ACTION_PLANNING
            
            elif decision.phase == AgentPhase.ACTION_PLANNING:
                if not optimization_result:
                    current_phase = AgentPhase.OPTIMIZATION
                    continue
                
                # Convert optimization to plan format (simplified)
                from app.models.plan import PlanResponse, PlanProjection
                plan = existing_plan  # Use existing or create from optimization
                
                daily_actions_result = await action_agent.generate_daily_actions(
                    plan=plan,
                    debts=debts,
                    current_streak=0,
                    last_payment_date=None,
                    payments_this_month=0
                )
                context["daily_actions"] = daily_actions_result
                current_phase = AgentPhase.HABIT_MONITORING
            
            elif decision.phase == AgentPhase.HABIT_MONITORING:
                # Check for milestones
                total_paid = sum(d.balance for d in debts if d.is_paid_off)
                total_current = sum(d.balance for d in debts if not d.is_paid_off)
                total_original = total_paid + total_current
                
                milestones_result = await habit_agent.check_milestones(
                    user_id=user_id,
                    total_debt_original=total_original,
                    total_debt_current=total_current,
                    total_paid=total_paid,
                    total_interest_saved=0,
                    debts_paid_off=len([d for d in debts if d.is_paid_off]),
                    payment_stats=PaymentStats(
                        total_payments=0,
                        total_amount_paid=total_paid,
                        total_interest_saved=0,
                        payments_this_month=0,
                        amount_this_month=0,
                        payments_last_30_days=0,
                        amount_last_30_days=0,
                        current_streak_days=0,
                        longest_streak_days=0,
                        on_track_percentage=0,
                        average_payment_amount=0
                    ),
                    existing_badges=[]
                )
                context["milestones"] = milestones_result
                
                # Check if negotiation needed
                if assessment_result and any(r.severity in ["high", "critical"] for r in assessment_result.risk_factors):
                    current_phase = AgentPhase.NEGOTIATION
                else:
                    break  # Workflow complete
            
            elif decision.phase == AgentPhase.NEGOTIATION:
                # Generate negotiation plans for high-interest debts
                if assessment_result:
                    high_interest_ids = assessment_result.categorized_debts.get("high_interest_credit", [])
                    high_interest_debts = [d for d in debts if str(d.id) in high_interest_ids][:2]  # Top 2
                    
                    for debt in high_interest_debts:
                        plan = await negotiation_agent.create_negotiation_plan(
                            debt=debt,
                            user_situation={
                                "income": monthly_income,
                                "payment_history": "good",
                                "hardship": context.get("trigger_event")
                            },
                            negotiation_goal="reduce_apr"
                        )
                        negotiation_plans.append(plan)
                
                break  # Workflow complete
            
            # OBSERVE: Update context with results
            context.update(decision.context_update)
        
        # Generate final summary
        final_summary = self._generate_final_summary(
            assessment_result,
            optimization_result,
            daily_actions_result,
            milestones_result,
            negotiation_plans
        )
        
        recommended_next_steps = self._generate_next_steps(context)
        
        return OrchestratorResult(
            assessment=assessment_result,
            optimization=optimization_result,
            daily_actions=daily_actions_result,
            milestones=milestones_result,
            negotiation_plans=negotiation_plans,
            workflow_trace=workflow_trace,
            final_summary=final_summary,
            recommended_next_steps=recommended_next_steps
        )
    
    def _determine_starting_phase(self, context: Dict[str, Any]) -> AgentPhase:
        """Determine where to start based on context."""
        if context.get("trigger_event") == "income_change":
            return AgentPhase.RE_ASSESSMENT
        elif context.get("trigger_event") == "new_user":
            return AgentPhase.ASSESSMENT
        elif context.get("existing_plan"):
            return AgentPhase.ACTION_PLANNING
        else:
            return AgentPhase.ASSESSMENT
    
    def _reason_next_step(
        self,
        context: Dict[str, Any],
        current_phase: AgentPhase
    ) -> OrchestratorDecision:
        """ReAct reasoning: Decide next action based on context."""
        
        if current_phase == AgentPhase.ASSESSMENT:
            return OrchestratorDecision(
                phase=AgentPhase.ASSESSMENT,
                reasoning="Need to assess financial situation first to understand debt landscape",
                next_agent="AssessmentAgent",
                context_update={},
                user_message="Analyzing your financial situation..."
            )
        
        elif current_phase == AgentPhase.OPTIMIZATION:
            return OrchestratorDecision(
                phase=AgentPhase.OPTIMIZATION,
                reasoning="Assessment complete. Now optimizing repayment strategy.",
                next_agent="OptimizationAgent",
                context_update={},
                user_message="Finding the best repayment plan..."
            )
        
        elif current_phase == AgentPhase.ACTION_PLANNING:
            return OrchestratorDecision(
                phase=AgentPhase.ACTION_PLANNING,
                reasoning="Plan created. Generating actionable daily steps.",
                next_agent="ActionAgent",
                context_update={},
                user_message="Creating your action plan..."
            )
        
        elif current_phase == AgentPhase.HABIT_MONITORING:
            return OrchestratorDecision(
                phase=AgentPhase.HABIT_MONITORING,
                reasoning="Checking for milestones and habit reinforcement opportunities.",
                next_agent="HabitAgent",
                context_update={},
                user_message="Checking your progress..."
            )
        
        elif current_phase == AgentPhase.NEGOTIATION:
            return OrchestratorDecision(
                phase=AgentPhase.NEGOTIATION,
                reasoning="High-interest debt detected. Preparing negotiation strategies.",
                next_agent="NegotiationAgent",
                context_update={},
                user_message="Preparing negotiation scripts..."
            )
        
        else:
            return OrchestratorDecision(
                phase=current_phase,
                reasoning="Continuing workflow",
                next_agent="Unknown",
                context_update={}
            )
    
    async def _handle_adaptive_event(
        self,
        user_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        current_context: Dict[str, Any]
    ) -> OrchestratorResult:
        """Handle dynamic events with adaptive re-planning."""
        
        # Update context with event
        current_context["trigger_event"] = event_type
        current_context["event_data"] = event_data
        
        # Determine if re-assessment or just re-optimization needed
        if event_type in ["income_change", "unexpected_expense", "new_debt"]:
            # Major change - full re-assessment
            return await self._orchestrate_workflow(
                user_id=user_id,
                debts=current_context.get("debts", []),
                monthly_income=event_data.get("new_income") or current_context.get("monthly_income"),
                monthly_expenses=current_context.get("monthly_expenses"),
                existing_plan=current_context.get("existing_plan"),
                user_goal=current_context.get("user_goal", "minimize_debt"),
                trigger_event=event_type
            )
        
        elif event_type in ["payment_missed", "payment_made"]:
            # Minor event - just update actions and habits
            daily_actions = await action_agent.generate_daily_actions(
                plan=current_context.get("existing_plan"),
                debts=current_context.get("debts", []),
                current_streak=event_data.get("streak", 0),
                last_payment_date=event_data.get("last_payment_date"),
                payments_this_month=event_data.get("payments_this_month", 0)
            )
            
            return OrchestratorResult(
                assessment=None,
                optimization=None,
                daily_actions=daily_actions,
                milestones=None,
                negotiation_plans=[],
                workflow_trace=[],
                final_summary="Updated daily actions based on recent activity",
                recommended_next_steps=["Follow today's action plan"]
            )
        
        else:
            # Unknown event - just return current state
            return OrchestratorResult(
                assessment=None,
                optimization=None,
                daily_actions=None,
                milestones=None,
                negotiation_plans=[],
                workflow_trace=[],
                final_summary="No action needed for this event",
                recommended_next_steps=[]
            )
    
    def _generate_final_summary(
        self,
        assessment: Optional[FinancialAssessment],
        optimization: Optional[OptimizationResult],
        actions: Optional[DailyActionsResponse],
        milestones: Optional[MilestoneCheckResult],
        negotiations: List[NegotiationPlan]
    ) -> str:
        """Generate human-readable summary of workflow results."""
        
        summary_parts = []
        
        if assessment:
            summary_parts.append(
                f"Financial Assessment: {assessment.assessment_summary} "
                f"Total debt: ${assessment.total_debt:,.2f}. "
                f"Found {len(assessment.spending_leaks)} areas to optimize spending."
            )
        
        if optimization:
            summary_parts.append(
                f"Optimization: Created {optimization.strategy} strategy plan. "
                f"Projected debt-free in {optimization.total_months} months, "
                f"saving ${optimization.total_interest_saved:,.2f} in interest."
            )
        
        if actions:
            summary_parts.append(
                f"Action Plan: {len(actions.actions)} prioritized actions for today. "
                f"{actions.summary}"
            )
        
        if milestones and milestones.has_new_milestones:
            summary_parts.append(
                f"Milestones: Achieved {len(milestones.milestones)} new milestone(s)! 🎉"
            )
        
        if negotiations:
            summary_parts.append(
                f"Negotiation: Prepared {len(negotiations)} negotiation plan(s) for high-interest debts."
            )
        
        return " ".join(summary_parts) if summary_parts else "Workflow completed successfully."
    
    def _generate_next_steps(self, context: Dict[str, Any]) -> List[str]:
        """Generate recommended next steps."""
        steps = []
        
        if context.get("assessment"):
            steps.append("Review your assessment and spending leak recommendations")
        
        if context.get("optimization"):
            steps.append("Activate your optimized repayment plan")
        
        if context.get("daily_actions"):
            steps.append("Complete today's prioritized actions")
        
        if context.get("negotiation_plans"):
            steps.append("Review negotiation scripts and schedule creditor calls")
        
        if not steps:
            steps.append("Continue following your current plan")
        
        return steps


# Singleton instance
orchestrator = DebtResolutionOrchestrator()
