"""
Debt repository for CRUD operations with encryption support.
"""

from datetime import datetime
from typing import Optional, List
from app.services.supabase_service import SupabaseService
from app.models.debt import DebtCreate, DebtUpdate, DebtResponse, DebtListResponse, DebtSummary
from app.core.errors import NotFoundError, DatabaseError


class DebtRepository:
    """Repository for debt data operations."""
    
    TABLE = "debts"
    
    @staticmethod
    async def create(user_id: str, debt_data: DebtCreate, token: Optional[str] = None) -> DebtResponse:
        """
        Create a new debt for a user.
        
        Args:
            user_id: User UUID
            debt_data: Debt creation data (with encrypted fields)
        
        Returns:
            Created debt
        
        Raises:
            DatabaseError: If creation fails
        """
        db_data = {
            "user_id": user_id,
            "creditor_name": debt_data.creditor_name,
            "debt_type": debt_data.debt_type.value,
            "current_balance_encrypted": debt_data.balance_encrypted,
            "interest_rate_encrypted": debt_data.apr_encrypted,
            "minimum_payment_encrypted": debt_data.minimum_payment_encrypted,
            "due_date_day": debt_data.due_date,
            "notes": debt_data.notes,
            "is_active": True,
            "is_paid_off": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await SupabaseService.insert(DebtRepository.TABLE, db_data, token=token)
        return DebtResponse(**result)
    
    @staticmethod
    async def get_by_id(debt_id: str, user_id: str, token: Optional[str] = None) -> Optional[DebtResponse]:
        """
        Get a debt by ID, scoped to user.
        
        Args:
            debt_id: Debt UUID
            user_id: User UUID (for RLS)
        
        Returns:
            Debt or None if not found
        """
        results = await SupabaseService.select(
            DebtRepository.TABLE,
            filters={"id": debt_id, "user_id": user_id}
        )
        return DebtResponse(**results[0]) if results else None
    
    @staticmethod
    async def get_all_by_user(
        user_id: str,
        include_inactive: bool = False
    ) -> DebtListResponse:
        """
        Get all debts for a user.
        
        Args:
            user_id: User UUID
            include_inactive: Include inactive/paid off debts
        
        Returns:
            DebtListResponse with debts and summary
        """
        filters = {"user_id": user_id}
        if not include_inactive:
            filters["is_active"] = True
        
        results = await SupabaseService.select(
            DebtRepository.TABLE,
            filters=filters,
            order_by="created_at"
        )
        
        debts = [DebtResponse(**row) for row in results]
        
        # Calculate summary
        total_debts = len(debts)
        active_debts = sum(1 for d in debts if d.is_active and not d.is_paid_off)
        paid_off_debts = sum(1 for d in debts if d.is_paid_off)
        
        summary = DebtSummary(
            total_debts=total_debts,
            active_debts=active_debts,
            paid_off_debts=paid_off_debts
        )
        
        return DebtListResponse(debts=debts, summary=summary)
    
    @staticmethod
    async def get_active_debts(user_id: str) -> List[DebtResponse]:
        """
        Get only active (non-paid-off) debts for a user.
        
        Args:
            user_id: User UUID
        
        Returns:
            List of active debts
        """
        results = await SupabaseService.select(
            DebtRepository.TABLE,
            filters={
                "user_id": user_id,
                "is_active": True,
                "is_paid_off": False
            },
            order_by="created_at"
        )
        
        return [DebtResponse(**row) for row in results]
    
    @staticmethod
    async def update(
        debt_id: str,
        user_id: str,
        update_data: DebtUpdate,
        token: Optional[str] = None
    ) -> DebtResponse:
        """
        Update a debt.
        
        Args:
            debt_id: Debt UUID
            user_id: User UUID (for RLS)
            update_data: Fields to update
        
        Returns:
            Updated debt
        
        Raises:
            NotFoundError: If debt doesn't exist
        """
        # Verify debt exists and belongs to user
        existing = await DebtRepository.get_by_id(debt_id, user_id)
        if not existing:
            raise NotFoundError("Debt", debt_id)
        
        # Prepare update data (exclude None values)
        db_data = {}
        update_dict = update_data.model_dump(exclude_none=True)
        
        for key, value in update_dict.items():
            if key == "debt_type" and value is not None:
                db_data[key] = value.value
            elif key == "balance_encrypted":
                db_data["current_balance_encrypted"] = value
            elif key == "apr_encrypted":
                db_data["interest_rate_encrypted"] = value
            elif key == "due_date":
                db_data["due_date_day"] = value
            else:
                db_data[key] = value
        
        db_data["updated_at"] = datetime.utcnow().isoformat()
        
        results = await SupabaseService.update(
            DebtRepository.TABLE,
            filters={"id": debt_id, "user_id": user_id},
            data=db_data,
            token=token
        )
        
        if not results:
            raise DatabaseError(
                message="Debt update returned no data",
                operation="update"
            )
        
        return DebtResponse(**results[0])
    
    @staticmethod
    async def mark_paid_off(debt_id: str, user_id: str, token: Optional[str] = None) -> DebtResponse:
        """
        Mark a debt as paid off.
        
        Args:
            debt_id: Debt UUID
            user_id: User UUID
        
        Returns:
            Updated debt
        
        Raises:
            NotFoundError: If debt doesn't exist
        """
        db_data = {
            "is_paid_off": True,
            "paid_off_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        results = await SupabaseService.update(
            DebtRepository.TABLE,
            filters={"id": debt_id, "user_id": user_id},
            data=db_data,
            token=token
        )
        
        if not results:
            raise NotFoundError("Debt", debt_id)
        
        return DebtResponse(**results[0])
    
    @staticmethod
    async def delete(debt_id: str, user_id: str, token: Optional[str] = None) -> None:
        """
        Delete a debt (hard delete).
        
        Args:
            debt_id: Debt UUID
            user_id: User UUID
        
        Raises:
            NotFoundError: If debt doesn't exist
        """
        results = await SupabaseService.delete(
            DebtRepository.TABLE,
            filters={"id": debt_id, "user_id": user_id},
            token=token
        )
        
        if not results:
            raise NotFoundError("Debt", debt_id)
    
    @staticmethod
    async def count_by_user(user_id: str) -> int:
        """
        Count total debts for a user.
        
        Args:
            user_id: User UUID
        
        Returns:
            Number of debts
        """
        results = await SupabaseService.select(
            DebtRepository.TABLE,
            columns="id",
            filters={"user_id": user_id}
        )
        return len(results)
