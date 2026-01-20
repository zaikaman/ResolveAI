"""
Payment service for logging payments and managing payment-related operations.

Handles payment creation, debt balance updates, plan recalculation triggers,
and interest savings calculations.
"""

from datetime import date, datetime
from typing import Optional, List, Tuple

from app.models.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentListResponse,
    PaymentStats,
    RecentPaymentSummary
)
from app.models.debt import DebtResponse
from app.db.repositories.payment_repo import PaymentRepository
from app.db.repositories.debt_repo import DebtRepository
from app.db.repositories.plan_repo import PlanRepository
from app.services.encryption_service import encryption_service
from app.agents.habit_agent import habit_agent, MilestoneCheckResult
from app.core.errors import ValidationError, NotFoundError


class PaymentService:
    """Service for payment operations."""
    
    @staticmethod
    async def log_payment(
        user_id: str,
        payment_data: PaymentCreate,
        token: Optional[str] = None
    ) -> Tuple[PaymentResponse, Optional[MilestoneCheckResult]]:
        """
        Log a new payment and update debt balance.
        
        Args:
            user_id: User UUID
            payment_data: Payment creation data
            token: Optional JWT token
        
        Returns:
            Tuple of (created payment, milestone check result if any)
        
        Raises:
            NotFoundError: If debt not found
            ValidationError: If payment amount exceeds balance
        """
        # 1. Get the debt to validate and calculate new balance
        debt = await DebtRepository.get_by_id(
            payment_data.debt_id,
            user_id,
            token=token
        )
        
        if not debt:
            raise NotFoundError(
                message="Debt not found",
                resource_type="debt",
                resource_id=payment_data.debt_id
            )
        
        if debt.is_paid_off:
            raise ValidationError(
                message="This debt is already paid off",
                field="debt_id"
            )
        
        # 2. Calculate new balance
        current_balance = debt.balance
        payment_amount = payment_data.amount
        
        if payment_amount > current_balance * 1.1:  # Allow 10% overpayment for rounding
            raise ValidationError(
                message=f"Payment amount (${payment_amount:.2f}) exceeds debt balance (${current_balance:.2f})",
                field="amount"
            )
        
        new_balance = max(0, current_balance - payment_amount)
        payment_data.new_balance = new_balance
        
        # 3. Calculate interest saved (simplified - based on APR and early payment)
        # More accurate calculation would need the full amortization schedule
        monthly_rate = (debt.apr / 100) / 12
        interest_saved = payment_amount * monthly_rate  # One month of interest on the principal paid
        
        # 4. Get active plan ID if exists
        active_plan = await PlanRepository.get_active_plan(user_id)
        plan_id = active_plan.id if active_plan else None
        
        # 5. Create the payment record
        payment = await PaymentRepository.create(
            user_id=user_id,
            payment_data=payment_data,
            plan_id=plan_id,
            interest_saved=interest_saved,
            token=token
        )
        
        # 6. Update debt balance
        debt_paid_off = new_balance == 0
        await DebtRepository.update_balance(
            debt_id=payment_data.debt_id,
            user_id=user_id,
            new_balance=new_balance,
            is_paid_off=debt_paid_off,
            token=token
        )
        
        # 7. Check for milestones
        milestone_result = None
        try:
            # Get payment stats for milestone checking
            payment_stats = await PaymentRepository.get_stats(user_id, token=token)
            
            # Get total debt info for percentage calculation
            debts_response = await DebtRepository.get_all_by_user(user_id, include_inactive=True)
            all_debts = debts_response.debts
            
            total_current = sum(d.balance for d in all_debts if d.is_active and not d.is_paid_off)
            total_original = sum(d.balance for d in all_debts)  # Simplified - would need original balances
            debts_paid_off_count = sum(1 for d in all_debts if d.is_paid_off)
            
            milestone_result = await habit_agent.check_milestones(
                user_id=user_id,
                total_debt_original=total_original + payment_stats.total_amount_paid,  # Approximate
                total_debt_current=total_current,
                total_paid=payment_stats.total_amount_paid,
                total_interest_saved=payment_stats.total_interest_saved,
                debts_paid_off=debts_paid_off_count,
                payment_stats=payment_stats,
                recently_paid_debt_id=payment_data.debt_id if debt_paid_off else None,
                recently_paid_debt_name=debt.creditor_name if debt_paid_off else None,
                existing_badges=[]  # Would need to track in DB
            )
        except Exception as e:
            # Don't fail the payment if milestone check fails
            print(f"Milestone check failed: {e}")
        
        # Add debt name to response
        payment.debt_name = debt.creditor_name
        
        return payment, milestone_result
    
    @staticmethod
    async def get_payment(
        payment_id: str,
        user_id: str,
        token: Optional[str] = None
    ) -> Optional[PaymentResponse]:
        """
        Get a single payment by ID.
        
        Args:
            payment_id: Payment UUID
            user_id: User UUID
            token: Optional JWT token
        
        Returns:
            Payment or None
        """
        return await PaymentRepository.get_by_id(payment_id, user_id, token=token)
    
    @staticmethod
    async def get_payments(
        user_id: str,
        debt_id: Optional[str] = None,
        limit: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        token: Optional[str] = None
    ) -> PaymentListResponse:
        """
        Get payments for a user with optional filters.
        
        Args:
            user_id: User UUID
            debt_id: Optional filter by debt
            limit: Max payments to return
            start_date: Filter by payment_date >= start_date
            end_date: Filter by payment_date <= end_date
            token: Optional JWT token
        
        Returns:
            PaymentListResponse with payments and totals
        """
        if debt_id:
            payments = await PaymentRepository.get_by_debt(
                debt_id, user_id, limit=limit, token=token
            )
            return PaymentListResponse(
                payments=payments,
                total_count=len(payments),
                total_amount=sum(p.amount for p in payments)
            )
        
        return await PaymentRepository.get_by_user(
            user_id,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            token=token
        )
    
    @staticmethod
    async def get_recent_payments(
        user_id: str,
        days: int = 30,
        limit: int = 10,
        token: Optional[str] = None
    ) -> List[PaymentResponse]:
        """
        Get recent payments for a user.
        
        Args:
            user_id: User UUID
            days: Number of days to look back
            limit: Max payments to return
            token: Optional JWT token
        
        Returns:
            List of recent payments
        """
        return await PaymentRepository.get_recent(user_id, days=days, limit=limit, token=token)
    
    @staticmethod
    async def get_payment_stats(
        user_id: str,
        token: Optional[str] = None
    ) -> PaymentStats:
        """
        Get payment statistics for a user.
        
        Args:
            user_id: User UUID
            token: Optional JWT token
        
        Returns:
            PaymentStats with aggregated data
        """
        return await PaymentRepository.get_stats(user_id, token=token)
    
    @staticmethod
    async def get_recent_summary(
        user_id: str,
        token: Optional[str] = None
    ) -> RecentPaymentSummary:
        """
        Get recent payment summary for dashboard.
        
        Args:
            user_id: User UUID
            token: Optional JWT token
        
        Returns:
            RecentPaymentSummary
        """
        return await PaymentRepository.get_recent_summary(user_id, token=token)
    
    @staticmethod
    async def update_payment(
        payment_id: str,
        user_id: str,
        update_data: PaymentUpdate,
        token: Optional[str] = None
    ) -> Optional[PaymentResponse]:
        """
        Update a payment record.
        
        Args:
            payment_id: Payment UUID
            user_id: User UUID
            update_data: Fields to update
            token: Optional JWT token
        
        Returns:
            Updated payment or None
        """
        return await PaymentRepository.update(
            payment_id, user_id, update_data, token=token
        )
    
    @staticmethod
    async def delete_payment(
        payment_id: str,
        user_id: str,
        token: Optional[str] = None
    ) -> bool:
        """
        Delete a payment record.
        
        Note: This should also revert the debt balance change,
        but for now we'll just delete the record.
        
        Args:
            payment_id: Payment UUID
            user_id: User UUID
            token: Optional JWT token
        
        Returns:
            True if deleted
        """
        # Get the payment first to potentially revert balance
        payment = await PaymentRepository.get_by_id(payment_id, user_id, token=token)
        
        if not payment:
            raise NotFoundError(
                message="Payment not found",
                resource_type="payment",
                resource_id=payment_id
            )
        
        # Delete the payment
        deleted = await PaymentRepository.delete(payment_id, user_id, token=token)
        
        if deleted:
            # Revert the debt balance
            debt = await DebtRepository.get_by_id(payment.debt_id, user_id, token=token)
            if debt:
                new_balance = debt.balance + payment.amount
                await DebtRepository.update_balance(
                    debt_id=payment.debt_id,
                    user_id=user_id,
                    new_balance=new_balance,
                    is_paid_off=False,
                    token=token
                )
        
        return deleted

    @staticmethod
    async def check_milestones(
        user_id: str,
        token: Optional[str] = None
    ) -> MilestoneCheckResult:
        """
        Check for any achieved milestones for a user.
        
        Args:
            user_id: User UUID
            token: Optional JWT token
        
        Returns:
            MilestoneCheckResult with any achieved milestones
        """
        try:
            # Get payment stats
            payment_stats = await PaymentRepository.get_stats(user_id, token=token)
            
            # Get debt info
            debts_response = await DebtRepository.get_all_by_user(user_id, include_inactive=True)
            all_debts = debts_response.debts
            
            total_current = sum(d.balance for d in all_debts if d.is_active and not d.is_paid_off)
            total_original = sum(d.balance for d in all_debts)
            debts_paid_off_count = sum(1 for d in all_debts if d.is_paid_off)
            
            return await habit_agent.check_milestones(
                user_id=user_id,
                total_debt_original=total_original + payment_stats.total_amount_paid,
                total_debt_current=total_current,
                total_paid=payment_stats.total_amount_paid,
                total_interest_saved=payment_stats.total_interest_saved,
                debts_paid_off=debts_paid_off_count,
                payment_stats=payment_stats,
                recently_paid_debt_id=None,
                recently_paid_debt_name=None,
                existing_badges=[]
            )
        except Exception as e:
            print(f"Milestone check failed: {e}")
            return MilestoneCheckResult(
                milestones=[],
                has_new_milestones=False,
                celebration_priority=0
            )


# Convenience functions
async def log_payment(
    user_id: str,
    payment_data: PaymentCreate,
    token: Optional[str] = None
) -> Tuple[PaymentResponse, Optional[MilestoneCheckResult]]:
    """Log a new payment."""
    return await PaymentService.log_payment(user_id, payment_data, token=token)


async def get_payment_stats(user_id: str, token: Optional[str] = None) -> PaymentStats:
    """Get payment statistics."""
    return await PaymentService.get_payment_stats(user_id, token=token)
