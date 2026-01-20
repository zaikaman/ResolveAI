"""
Payment repository for CRUD operations and statistics.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List
from app.services.supabase_service import SupabaseService
from app.models.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentListResponse,
    PaymentStats,
    RecentPaymentSummary
)
from app.core.errors import NotFoundError, DatabaseError


class PaymentRepository:
    """Repository for payment data operations."""
    
    TABLE = "payments"
    
    @staticmethod
    def _parse_payment(db_payment: dict, debt_name: Optional[str] = None) -> PaymentResponse:
        """
        Parse database payment record to PaymentResponse.
        
        Args:
            db_payment: Raw payment record from database
            debt_name: Optional debt name for display
        
        Returns:
            PaymentResponse model
        """
        return PaymentResponse(
            id=db_payment["id"],
            user_id=db_payment["user_id"],
            debt_id=db_payment["debt_id"],
            plan_id=db_payment.get("plan_id"),
            amount=float(db_payment["amount"]),
            payment_date=db_payment["payment_date"],
            payment_method=db_payment.get("payment_method"),
            confirmed=db_payment.get("confirmed", True),
            new_balance=float(db_payment["new_balance"]),
            interest_saved=float(db_payment["interest_saved"]) if db_payment.get("interest_saved") else None,
            notes=db_payment.get("notes"),
            created_at=db_payment["created_at"],
            debt_name=debt_name
        )
    
    @staticmethod
    async def create(
        user_id: str,
        payment_data: PaymentCreate,
        plan_id: Optional[str] = None,
        interest_saved: Optional[float] = None,
        token: Optional[str] = None
    ) -> PaymentResponse:
        """
        Create a new payment record.
        
        Args:
            user_id: User UUID
            payment_data: Payment creation data
            plan_id: Optional active plan ID
            interest_saved: Calculated interest saved (if any)
            token: Optional JWT token
        
        Returns:
            Created payment
        """
        db_data = {
            "user_id": user_id,
            "debt_id": payment_data.debt_id,
            "plan_id": plan_id,
            "amount": payment_data.amount,
            "payment_date": (payment_data.payment_date or date.today()).isoformat(),
            "payment_method": payment_data.payment_method.value if payment_data.payment_method else None,
            "confirmed": True,
            "new_balance": payment_data.new_balance or 0,
            "interest_saved": interest_saved,
            "notes": payment_data.notes,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = await SupabaseService.insert(PaymentRepository.TABLE, db_data, token=token)
        return PaymentRepository._parse_payment(result)
    
    @staticmethod
    async def get_by_id(
        payment_id: str,
        user_id: str,
        token: Optional[str] = None
    ) -> Optional[PaymentResponse]:
        """
        Get a payment by ID, scoped to user.
        
        Args:
            payment_id: Payment UUID
            user_id: User UUID
            token: Optional JWT token
        
        Returns:
            Payment or None
        """
        results = await SupabaseService.select(
            PaymentRepository.TABLE,
            filters={"id": payment_id, "user_id": user_id},
            token=token
        )
        return PaymentRepository._parse_payment(results[0]) if results else None
    
    @staticmethod
    async def get_by_debt(
        debt_id: str,
        user_id: str,
        limit: Optional[int] = None,
        token: Optional[str] = None
    ) -> List[PaymentResponse]:
        """
        Get all payments for a specific debt.
        
        Args:
            debt_id: Debt UUID
            user_id: User UUID
            limit: Max payments to return
            token: Optional JWT token
        
        Returns:
            List of payments
        """
        results = await SupabaseService.select(
            PaymentRepository.TABLE,
            filters={"debt_id": debt_id, "user_id": user_id},
            order_by="payment_date",
            limit=limit,
            token=token
        )
        return [PaymentRepository._parse_payment(row) for row in results]
    
    @staticmethod
    async def get_by_user(
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        token: Optional[str] = None
    ) -> PaymentListResponse:
        """
        Get all payments for a user with optional filters.
        
        Args:
            user_id: User UUID
            limit: Max payments to return
            offset: Number of records to skip
            start_date: Filter by payment_date >= start_date
            end_date: Filter by payment_date <= end_date
            token: Optional JWT token
        
        Returns:
            PaymentListResponse with payments and totals
        """
        # Build base query
        filters = {"user_id": user_id}
        
        results = await SupabaseService.select(
            PaymentRepository.TABLE,
            filters=filters,
            order_by="payment_date",
            limit=limit,
            token=token
        )
        
        # Filter by date range if provided (done in Python since Supabase SDK doesn't support range easily)
        if start_date or end_date:
            filtered_results = []
            for row in results:
                payment_date = date.fromisoformat(row["payment_date"]) if isinstance(row["payment_date"], str) else row["payment_date"]
                if start_date and payment_date < start_date:
                    continue
                if end_date and payment_date > end_date:
                    continue
                filtered_results.append(row)
            results = filtered_results
        
        payments = [PaymentRepository._parse_payment(row) for row in results]
        total_amount = sum(p.amount for p in payments)
        
        return PaymentListResponse(
            payments=payments,
            total_count=len(payments),
            total_amount=total_amount
        )
    
    @staticmethod
    async def get_recent(
        user_id: str,
        days: int = 30,
        limit: int = 10,
        token: Optional[str] = None
    ) -> List[PaymentResponse]:
        """
        Get recent payments within the last N days.
        
        Args:
            user_id: User UUID
            days: Number of days to look back
            limit: Max payments to return
            token: Optional JWT token
        
        Returns:
            List of recent payments
        """
        results = await SupabaseService.select(
            PaymentRepository.TABLE,
            filters={"user_id": user_id},
            order_by="payment_date",
            limit=limit * 2,  # Get extra to filter by date
            token=token
        )
        
        cutoff_date = date.today() - timedelta(days=days)
        filtered = []
        for row in results:
            payment_date = date.fromisoformat(row["payment_date"]) if isinstance(row["payment_date"], str) else row["payment_date"]
            if payment_date >= cutoff_date:
                filtered.append(row)
            if len(filtered) >= limit:
                break
        
        return [PaymentRepository._parse_payment(row) for row in filtered]
    
    @staticmethod
    async def update(
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
        update_dict = {}
        if update_data.amount is not None:
            update_dict["amount"] = update_data.amount
        if update_data.payment_date is not None:
            update_dict["payment_date"] = update_data.payment_date.isoformat()
        if update_data.payment_method is not None:
            update_dict["payment_method"] = update_data.payment_method.value
        if update_data.notes is not None:
            update_dict["notes"] = update_data.notes
        if update_data.confirmed is not None:
            update_dict["confirmed"] = update_data.confirmed
        
        if not update_dict:
            # No updates, return existing
            return await PaymentRepository.get_by_id(payment_id, user_id, token=token)
        
        result = await SupabaseService.update(
            PaymentRepository.TABLE,
            update_dict,
            filters={"id": payment_id, "user_id": user_id},
            token=token
        )
        return PaymentRepository._parse_payment(result) if result else None
    
    @staticmethod
    async def delete(
        payment_id: str,
        user_id: str,
        token: Optional[str] = None
    ) -> bool:
        """
        Delete a payment record.
        
        Args:
            payment_id: Payment UUID
            user_id: User UUID
            token: Optional JWT token
        
        Returns:
            True if deleted
        """
        return await SupabaseService.delete(
            PaymentRepository.TABLE,
            filters={"id": payment_id, "user_id": user_id},
            token=token
        )
    
    @staticmethod
    async def get_stats(
        user_id: str,
        token: Optional[str] = None
    ) -> PaymentStats:
        """
        Calculate payment statistics for a user.
        
        Args:
            user_id: User UUID
            token: Optional JWT token
        
        Returns:
            PaymentStats with aggregated data
        """
        # Get all payments for the user
        all_payments = await SupabaseService.select(
            PaymentRepository.TABLE,
            filters={"user_id": user_id},
            order_by="payment_date",
            token=token
        )
        
        if not all_payments:
            return PaymentStats()
        
        today = date.today()
        month_start = today.replace(day=1)
        thirty_days_ago = today - timedelta(days=30)
        
        total_payments = len(all_payments)
        total_amount = sum(float(p["amount"]) for p in all_payments)
        total_interest_saved = sum(float(p.get("interest_saved") or 0) for p in all_payments)
        
        # Time-based stats
        payments_this_month = 0
        amount_this_month = 0.0
        payments_last_30 = 0
        amount_last_30 = 0.0
        payments_by_debt: dict[str, int] = {}
        payment_dates: list[date] = []
        
        for p in all_payments:
            payment_date = date.fromisoformat(p["payment_date"]) if isinstance(p["payment_date"], str) else p["payment_date"]
            payment_dates.append(payment_date)
            
            amount = float(p["amount"])
            debt_id = p["debt_id"]
            
            # Track by debt
            payments_by_debt[debt_id] = payments_by_debt.get(debt_id, 0) + 1
            
            # This month
            if payment_date >= month_start:
                payments_this_month += 1
                amount_this_month += amount
            
            # Last 30 days
            if payment_date >= thirty_days_ago:
                payments_last_30 += 1
                amount_last_30 += amount
        
        # Calculate streaks
        current_streak = 0
        longest_streak = 0
        
        if payment_dates:
            # Sort dates in descending order
            sorted_dates = sorted(set(payment_dates), reverse=True)
            
            # Check if there was a payment today or yesterday for current streak
            if sorted_dates[0] >= today - timedelta(days=1):
                current_streak = 1
                for i in range(1, len(sorted_dates)):
                    if (sorted_dates[i-1] - sorted_dates[i]).days <= 7:  # Weekly payment is considered streak
                        current_streak += 1
                    else:
                        break
            
            # Calculate longest streak (simplified - consecutive weeks with payments)
            streak = 1
            sorted_asc = sorted(set(payment_dates))
            for i in range(1, len(sorted_asc)):
                if (sorted_asc[i] - sorted_asc[i-1]).days <= 7:
                    streak += 1
                else:
                    longest_streak = max(longest_streak, streak)
                    streak = 1
            longest_streak = max(longest_streak, streak)
        
        return PaymentStats(
            total_payments=total_payments,
            total_amount_paid=total_amount,
            total_interest_saved=total_interest_saved,
            payments_this_month=payments_this_month,
            amount_this_month=amount_this_month,
            payments_last_30_days=payments_last_30,
            amount_last_30_days=amount_last_30,
            current_streak_days=current_streak,
            longest_streak_days=longest_streak,
            on_track_percentage=100.0 if total_payments > 0 else 0.0,  # Simplified - would need plan comparison
            average_payment_amount=total_amount / total_payments if total_payments > 0 else 0.0,
            payments_by_debt=payments_by_debt
        )
    
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
        # Get recent payments
        recent = await PaymentRepository.get_recent(user_id, days=7, limit=10, token=token)
        
        stats = await PaymentRepository.get_stats(user_id, token=token)
        
        last_payment = recent[0] if recent else None
        
        return RecentPaymentSummary(
            last_payment_date=last_payment.payment_date if last_payment else None,
            last_payment_amount=last_payment.amount if last_payment else None,
            last_payment_debt_name=last_payment.debt_name if last_payment else None,
            payments_this_week=len(recent),
            amount_this_week=sum(p.amount for p in recent),
            total_principal_paid=stats.total_amount_paid,
            total_interest_paid=0,  # Would need to track separately
            current_streak=stats.current_streak_days,
            is_on_streak=stats.current_streak_days > 0
        )
