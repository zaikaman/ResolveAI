"""
Repayment plan repository for CRUD operations.
"""

from datetime import datetime
from typing import Optional, List
from app.services.supabase_service import SupabaseService
from app.models.plan import (
    PlanStatus, 
    RepaymentStrategy, 
    PlanResponse,
    PlanSummaryResponse,
    MonthlyBreakdown,
    PlanProjection,
    DebtPayoffInfo
)
from app.core.errors import NotFoundError, DatabaseError
import json


class PlanRepository:
    """Repository for repayment plan data operations."""
    
    TABLE = "repayment_plans"
    
    @staticmethod
    async def create(
        user_id: str,
        strategy: RepaymentStrategy,
        debt_free_date: str,
        total_months: int,
        total_interest: float,
        total_paid: float,
        interest_saved: float,
        months_saved: int,
        monthly_payment: float,
        extra_payment: float,
        monthly_schedule: List[MonthlyBreakdown],
        projections: List[PlanProjection],
        payoff_order: List[DebtPayoffInfo]
    ) -> PlanResponse:
        """
        Create a new repayment plan.
        
        Args:
            user_id: User UUID
            strategy: Repayment strategy (avalanche/snowball)
            debt_free_date: Projected debt-free date
            total_months: Total months to payoff
            total_interest: Total interest to be paid
            total_paid: Total amount to be paid
            interest_saved: Interest saved vs minimum-only
            months_saved: Months saved vs minimum-only
            monthly_payment: Total monthly payment
            extra_payment: Extra payment above minimums
            monthly_schedule: Month-by-month breakdown
            projections: Projection data for charts
            payoff_order: Order of debt payoffs
        
        Returns:
            Created plan
        """
        # Serialize complex objects to JSON for storage
        schedule_json = [item.model_dump(mode='json') for item in monthly_schedule]
        projections_json = [item.model_dump(mode='json') for item in projections]
        payoff_json = [item.model_dump(mode='json') for item in payoff_order]
        
        db_data = {
            "user_id": user_id,
            "status": PlanStatus.ACTIVE.value,
            "strategy": strategy.value,
            "debt_free_date": debt_free_date,
            "total_months": total_months,
            "total_interest": total_interest,
            "total_paid": total_paid,
            "interest_saved": interest_saved,
            "months_saved": months_saved,
            "monthly_payment": monthly_payment,
            "extra_payment": extra_payment,
            "monthly_schedule": json.dumps(schedule_json),
            "projections": json.dumps(projections_json),
            "payoff_order": json.dumps(payoff_json),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await SupabaseService.insert(PlanRepository.TABLE, db_data)
        return PlanRepository._parse_plan_response(result)
    
    @staticmethod
    async def get_by_id(plan_id: str, user_id: str) -> Optional[PlanResponse]:
        """
        Get a plan by ID, scoped to user.
        
        Args:
            plan_id: Plan UUID
            user_id: User UUID
        
        Returns:
            Plan or None if not found
        """
        results = await SupabaseService.select(
            PlanRepository.TABLE,
            filters={"id": plan_id, "user_id": user_id}
        )
        
        if not results:
            return None
        
        return PlanRepository._parse_plan_response(results[0])
    
    @staticmethod
    async def get_active_plan(user_id: str) -> Optional[PlanResponse]:
        """
        Get the active plan for a user.
        
        Args:
            user_id: User UUID
        
        Returns:
            Active plan or None if no active plan
        """
        results = await SupabaseService.select(
            PlanRepository.TABLE,
            filters={
                "user_id": user_id,
                "status": PlanStatus.ACTIVE.value
            },
            order_by="created_at",
            limit=1
        )
        
        if not results:
            return None
        
        return PlanRepository._parse_plan_response(results[0])
    
    @staticmethod
    async def get_plan_summary(user_id: str) -> Optional[PlanSummaryResponse]:
        """
        Get a lightweight summary of the active plan.
        
        Args:
            user_id: User UUID
        
        Returns:
            Plan summary or None
        """
        results = await SupabaseService.select(
            PlanRepository.TABLE,
            columns="id,status,strategy,debt_free_date,total_months,monthly_payment,created_at",
            filters={
                "user_id": user_id,
                "status": PlanStatus.ACTIVE.value
            },
            limit=1
        )
        
        if not results:
            return None
        
        row = results[0]
        
        # Calculate months remaining
        from datetime import date
        debt_free = date.fromisoformat(row["debt_free_date"])
        today = date.today()
        months_elapsed = (today.year - debt_free.year) * 12 + (today.month - debt_free.month)
        months_remaining = max(0, row["total_months"] + months_elapsed)
        
        progress = ((row["total_months"] - months_remaining) / row["total_months"]) * 100 if row["total_months"] > 0 else 0
        
        return PlanSummaryResponse(
            id=row["id"],
            status=PlanStatus(row["status"]),
            strategy=RepaymentStrategy(row["strategy"]),
            debt_free_date=date.fromisoformat(row["debt_free_date"]),
            total_months=row["total_months"],
            months_remaining=months_remaining,
            progress_percentage=min(100, max(0, progress)),
            monthly_payment=row["monthly_payment"]
        )
    
    @staticmethod
    async def update_status(
        plan_id: str,
        user_id: str,
        status: PlanStatus
    ) -> PlanResponse:
        """
        Update plan status.
        
        Args:
            plan_id: Plan UUID
            user_id: User UUID
            status: New status
        
        Returns:
            Updated plan
        
        Raises:
            NotFoundError: If plan doesn't exist
        """
        db_data = {
            "status": status.value,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        results = await SupabaseService.update(
            PlanRepository.TABLE,
            filters={"id": plan_id, "user_id": user_id},
            data=db_data
        )
        
        if not results:
            raise NotFoundError("Plan", plan_id)
        
        return PlanRepository._parse_plan_response(results[0])
    
    @staticmethod
    async def archive_active_plans(user_id: str) -> int:
        """
        Archive all active plans for a user (when generating new plan).
        
        Args:
            user_id: User UUID
        
        Returns:
            Number of plans archived
        """
        # Get all active plans
        active_plans = await SupabaseService.select(
            PlanRepository.TABLE,
            columns="id",
            filters={
                "user_id": user_id,
                "status": PlanStatus.ACTIVE.value
            }
        )
        
        count = 0
        for plan in active_plans:
            await SupabaseService.update(
                PlanRepository.TABLE,
                filters={"id": plan["id"]},
                data={
                    "status": PlanStatus.ARCHIVED.value,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            count += 1
        
        return count
    
    @staticmethod
    async def delete(plan_id: str, user_id: str) -> None:
        """
        Delete a plan (hard delete).
        
        Args:
            plan_id: Plan UUID
            user_id: User UUID
        
        Raises:
            NotFoundError: If plan doesn't exist
        """
        results = await SupabaseService.delete(
            PlanRepository.TABLE,
            filters={"id": plan_id, "user_id": user_id}
        )
        
        if not results:
            raise NotFoundError("Plan", plan_id)
    
    @staticmethod
    def _parse_plan_response(row: dict) -> PlanResponse:
        """
        Parse database row into PlanResponse, deserializing JSON fields.
        
        Args:
            row: Database row
        
        Returns:
            PlanResponse object
        """
        from datetime import date
        
        # Parse JSON fields
        schedule_data = row.get("monthly_schedule")
        projections_data = row.get("projections")
        payoff_data = row.get("payoff_order")
        
        if isinstance(schedule_data, str):
            schedule_data = json.loads(schedule_data)
        if isinstance(projections_data, str):
            projections_data = json.loads(projections_data)
        if isinstance(payoff_data, str):
            payoff_data = json.loads(payoff_data)
        
        monthly_schedule = [MonthlyBreakdown(**item) for item in (schedule_data or [])]
        projections = [PlanProjection(**item) for item in (projections_data or [])]
        payoff_order = [DebtPayoffInfo(**item) for item in (payoff_data or [])]
        
        return PlanResponse(
            id=row["id"],
            user_id=row["user_id"],
            status=PlanStatus(row["status"]),
            strategy=RepaymentStrategy(row["strategy"]),
            debt_free_date=date.fromisoformat(row["debt_free_date"]) if isinstance(row["debt_free_date"], str) else row["debt_free_date"],
            total_months=row["total_months"],
            total_interest=row["total_interest"],
            total_paid=row["total_paid"],
            interest_saved=row["interest_saved"],
            months_saved=row["months_saved"],
            monthly_payment=row["monthly_payment"],
            extra_payment=row["extra_payment"],
            monthly_schedule=monthly_schedule,
            projections=projections,
            payoff_order=payoff_order,
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
