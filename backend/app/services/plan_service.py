"""
Plan service for orchestrating plan generation and management.
"""

from datetime import date
from typing import Optional, List
from app.db.repositories.plan_repo import PlanRepository
from app.db.repositories.debt_repo import DebtRepository
from app.services.optimization_service import OptimizationService, DebtInfo
from app.services.encryption_service import EncryptionService
from app.models.plan import (
    PlanRequest,
    PlanResponse,
    PlanSummaryResponse,
    PlanSimulationRequest,
    PlanSimulationResponse,
    RepaymentStrategy,
    PlanStatus
)
from app.core.errors import ValidationError, NotFoundError


class PlanService:
    """Service for repayment plan generation and management."""
    
    @staticmethod
    async def generate_plan(
        user_id: str,
        request: PlanRequest,
        available_for_debt: float
    ) -> PlanResponse:
        """
        Generate a new repayment plan for a user.
        
        Args:
            user_id: User UUID
            request: Plan generation request
            available_for_debt: User's available monthly amount for debt
        
        Returns:
            Generated plan
        
        Raises:
            ValidationError: If no debts to plan for
        """
        # Get user's active debts
        debts = await DebtRepository.get_active_debts(user_id)
        
        if not debts:
            raise ValidationError(
                message="No active debts to create a plan for",
                details={"user_id": user_id}
            )
        
        # Decrypt debt data for calculations
        debt_infos: List[DebtInfo] = []
        for debt in debts:
            try:
                balance = float(EncryptionService.decrypt(debt.balance_encrypted))
                apr = float(EncryptionService.decrypt(debt.apr_encrypted))
                min_payment = float(EncryptionService.decrypt(debt.minimum_payment_encrypted))
                
                debt_infos.append(DebtInfo(
                    id=debt.id,
                    name=debt.creditor_name,
                    balance=balance,
                    apr=apr,
                    minimum_payment=min_payment
                ))
            except Exception as e:
                raise ValidationError(
                    message=f"Failed to decrypt debt data for {debt.creditor_name}",
                    details={"debt_id": debt.id, "error": str(e)}
                )
        
        # Use custom budget if provided, otherwise use user's available amount
        monthly_budget = request.custom_monthly_budget or available_for_debt
        
        # Calculate optimized plan
        result = OptimizationService.calculate_plan(
            debts=debt_infos,
            available_monthly=monthly_budget,
            strategy=request.strategy,
            extra_payment=request.extra_monthly_payment,
            start_date=request.start_date
        )
        
        # Calculate minimum-only comparison
        min_months, min_interest = OptimizationService.calculate_minimum_only_plan(
            debts=debt_infos,
            start_date=request.start_date
        )
        
        interest_saved = min_interest - result.total_interest
        months_saved = min_months - result.total_months
        
        # Archive existing active plans
        await PlanRepository.archive_active_plans(user_id)
        
        # Save new plan
        plan = await PlanRepository.create(
            user_id=user_id,
            strategy=request.strategy,
            debt_free_date=result.debt_free_date.isoformat(),
            total_months=result.total_months,
            total_interest=result.total_interest,
            total_paid=result.total_paid,
            interest_saved=max(0, interest_saved),
            months_saved=max(0, months_saved),
            monthly_payment=result.monthly_payment,
            extra_payment=request.extra_monthly_payment,
            monthly_schedule=result.monthly_schedule,
            projections=result.projections,
            payoff_order=result.payoff_order
        )
        
        return plan
    
    @staticmethod
    async def get_active_plan(user_id: str) -> Optional[PlanResponse]:
        """
        Get the active plan for a user.
        
        Args:
            user_id: User UUID
        
        Returns:
            Active plan or None
        """
        return await PlanRepository.get_active_plan(user_id)
    
    @staticmethod
    async def get_plan_summary(user_id: str) -> Optional[PlanSummaryResponse]:
        """
        Get a lightweight plan summary for dashboard.
        
        Args:
            user_id: User UUID
        
        Returns:
            Plan summary or None
        """
        return await PlanRepository.get_plan_summary(user_id)
    
    @staticmethod
    async def recalculate_plan(
        user_id: str,
        plan_id: str,
        strategy: Optional[RepaymentStrategy] = None,
        extra_payment: Optional[float] = None,
        available_for_debt: Optional[float] = None
    ) -> PlanResponse:
        """
        Recalculate an existing plan with new parameters.
        
        Args:
            user_id: User UUID
            plan_id: Existing plan ID
            strategy: New strategy (optional)
            extra_payment: New extra payment (optional)
            available_for_debt: New available amount (optional)
        
        Returns:
            New recalculated plan
        """
        # Get existing plan
        existing = await PlanRepository.get_by_id(plan_id, user_id)
        if not existing:
            raise NotFoundError("Plan", plan_id)
        
        # Create new plan request with updated parameters
        request = PlanRequest(
            strategy=strategy or existing.strategy,
            extra_monthly_payment=extra_payment if extra_payment is not None else existing.extra_payment
        )
        
        # Use new available amount or calculate from existing plan
        budget = available_for_debt or (existing.monthly_payment - existing.extra_payment)
        
        return await PlanService.generate_plan(user_id, request, budget)
    
    @staticmethod
    async def simulate_scenario(
        user_id: str,
        request: PlanSimulationRequest,
        available_for_debt: float
    ) -> PlanSimulationResponse:
        """
        Simulate a what-if scenario without saving.
        
        Args:
            user_id: User UUID
            request: Simulation request
            available_for_debt: User's available monthly amount
        
        Returns:
            Simulation comparison results
        """
        # Get current active plan
        current_plan = await PlanRepository.get_active_plan(user_id)
        if not current_plan:
            raise ValidationError(
                message="No active plan to compare against",
                details={"user_id": user_id}
            )
        
        # Get debts
        debts = await DebtRepository.get_active_debts(user_id)
        if not debts:
            raise ValidationError(
                message="No active debts for simulation",
                details={"user_id": user_id}
            )
        
        # Decrypt and prepare debt infos
        debt_infos: List[DebtInfo] = []
        for debt in debts:
            balance = float(EncryptionService.decrypt(debt.balance_encrypted))
            apr = float(EncryptionService.decrypt(debt.apr_encrypted))
            min_payment = float(EncryptionService.decrypt(debt.minimum_payment_encrypted))
            
            # Apply rate reduction if specified
            if request.rate_reduction and debt.id in request.rate_reduction:
                apr = request.rate_reduction[debt.id]
            
            # Apply lump sum if specified
            if request.lump_sum_payment and request.lump_sum_target_debt_id == debt.id:
                balance = max(0, balance - request.lump_sum_payment)
            
            debt_infos.append(DebtInfo(
                id=debt.id,
                name=debt.creditor_name,
                balance=balance,
                apr=apr,
                minimum_payment=min_payment
            ))
        
        # Calculate available with income change
        simulated_available = available_for_debt
        if request.income_change:
            simulated_available += request.income_change
        
        # Run simulation
        result = OptimizationService.calculate_plan(
            debts=debt_infos,
            available_monthly=simulated_available,
            strategy=request.strategy,
            extra_payment=request.extra_monthly_payment
        )
        
        return PlanSimulationResponse(
            original_debt_free_date=current_plan.debt_free_date,
            original_total_interest=current_plan.total_interest,
            original_total_months=current_plan.total_months,
            simulated_debt_free_date=result.debt_free_date,
            simulated_total_interest=result.total_interest,
            simulated_total_months=result.total_months,
            interest_difference=current_plan.total_interest - result.total_interest,
            months_difference=current_plan.total_months - result.total_months,
            projections=result.projections
        )
    
    @staticmethod
    async def complete_plan(user_id: str, plan_id: str) -> PlanResponse:
        """
        Mark a plan as completed.
        
        Args:
            user_id: User UUID
            plan_id: Plan ID
        
        Returns:
            Updated plan
        """
        return await PlanRepository.update_status(plan_id, user_id, PlanStatus.COMPLETED)
