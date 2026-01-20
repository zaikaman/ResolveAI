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
        payoff_order: List[DebtPayoffInfo],
        ai_explanation: Optional[str] = None,
        token: Optional[str] = None
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
            token: Optional JWT token for authenticated request
        
        Returns:
            Created plan
        """
        # Serialize complex objects to JSON for storage
        schedule_json = [item.model_dump(mode='json') for item in monthly_schedule]
        projections_json = [item.model_dump(mode='json') for item in projections]
        payoff_json = [item.model_dump(mode='json') for item in payoff_order]
        
        db_data = {
            "user_id": user_id,
            "is_active": True,
            "strategy": strategy.value,
            "target_debt_free_date": debt_free_date,
            "total_debt_amount": total_paid,
            "total_interest_projection": total_interest,
            "monthly_payment_total": monthly_payment,
            "payment_schedule": json.dumps(schedule_json),
            "optimization_metadata": json.dumps({
                "interest_saved": interest_saved,
                "months_saved": months_saved,
                "total_months": total_months,
                "extra_payment": extra_payment,
                "projections": projections_json,
                "payoff_order": payoff_json,
                "ai_explanation": ai_explanation
            }),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await SupabaseService.insert(PlanRepository.TABLE, db_data, token=token)
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
                "is_active": True
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
            columns="id,strategy,target_debt_free_date,optimization_metadata,monthly_payment_total,created_at",
            filters={
                "user_id": user_id,
                "is_active": True
            },
            limit=1
        )
        
        if not results:
            return None
        
        row = results[0]
        
        # Extract optimization_metadata
        metadata = row.get("optimization_metadata", {})
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        total_months = metadata.get("total_months", 0)
        
        # Calculate months remaining
        from datetime import date
        debt_free = date.fromisoformat(row["target_debt_free_date"])
        today = date.today()
        months_elapsed = (today.year - debt_free.year) * 12 + (today.month - debt_free.month)
        months_remaining = max(0, total_months + months_elapsed)
        
        progress = ((total_months - months_remaining) / total_months) * 100 if total_months > 0 else 0
        
        return PlanSummaryResponse(
            id=row["id"],
            strategy=RepaymentStrategy(row["strategy"]),
            debt_free_date=date.fromisoformat(row["target_debt_free_date"]),
            total_months=total_months,
            months_remaining=months_remaining,
            progress_percentage=min(100, max(0, progress)),
            monthly_payment=row["monthly_payment_total"]
        )
    
    @staticmethod
    async def update_status(
        plan_id: str,
        user_id: str,
        is_completed: bool
    ) -> PlanResponse:
        """
        Update plan completion status.
        
        Args:
            plan_id: Plan UUID
            user_id: User UUID
            is_completed: Whether the plan is completed
        
        Returns:
            Updated plan
        
        Raises:
            NotFoundError: If plan doesn't exist
        """
        db_data = {
            "is_active": not is_completed,
            "updated_at": datetime.utcnow().isoformat()
        }
        if is_completed:
            db_data["completed_at"] = datetime.utcnow().isoformat()
        
        results = await SupabaseService.update(
            PlanRepository.TABLE,
            filters={"id": plan_id, "user_id": user_id},
            data=db_data
        )
        
        if not results:
            raise NotFoundError("Plan", plan_id)
        
        return PlanRepository._parse_plan_response(results[0])
    
    @staticmethod
    async def archive_active_plans(user_id: str, token: Optional[str] = None) -> int:
        """
        Archive all active plans for a user (when generating new plan).
        
        Args:
            user_id: User UUID
            token: Optional JWT token for authenticated request
        
        Returns:
            Number of plans archived
        """
        # Get all active plans
        active_plans = await SupabaseService.select(
            PlanRepository.TABLE,
            columns="id",
            filters={
                "user_id": user_id,
                "is_active": True
            },
            token=token
        )
        
        count = 0
        for plan in active_plans:
            await SupabaseService.update(
                PlanRepository.TABLE,
                filters={"id": plan["id"]},
                data={
                    "is_active": False,
                    "updated_at": datetime.utcnow().isoformat()
                },
                token=token
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
        
        # Parse JSON fields from schema columns
        schedule_data = row.get("payment_schedule")
        metadata = row.get("optimization_metadata", {})
        
        if isinstance(schedule_data, str):
            schedule_data = json.loads(schedule_data)
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        # Extract metadata fields
        projections_data = metadata.get("projections", [])
        payoff_data = metadata.get("payoff_order", [])
        
        monthly_schedule = [MonthlyBreakdown(**item) for item in (schedule_data or [])]
        projections = [PlanProjection(**item) for item in (projections_data or [])]
        payoff_order = [DebtPayoffInfo(**item) for item in (payoff_data or [])]
        
        # Map is_active to PlanStatus
        if row.get("completed_at"):
            status = PlanStatus.COMPLETED
        elif row.get("is_active"):
            status = PlanStatus.ACTIVE
        else:
            status = PlanStatus.ARCHIVED
        
        return PlanResponse(
            id=row["id"],
            user_id=row["user_id"],
            status=status,
            strategy=RepaymentStrategy(row["strategy"]),
            debt_free_date=date.fromisoformat(row["target_debt_free_date"]) if isinstance(row["target_debt_free_date"], str) else row["target_debt_free_date"],
            total_months=metadata.get("total_months", 0),
            total_interest=row["total_interest_projection"],
            total_paid=row["total_debt_amount"],
            interest_saved=metadata.get("interest_saved", 0),
            months_saved=metadata.get("months_saved", 0),
            monthly_payment=row["monthly_payment_total"],
            extra_payment=metadata.get("extra_payment", 0),
            monthly_schedule=monthly_schedule,
            projections=projections,
            payoff_order=payoff_order,
            ai_explanation=metadata.get("ai_explanation"),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
