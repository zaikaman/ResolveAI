"""
Debt repository for CRUD operations with server-side encryption.
"""

from datetime import datetime
from typing import Optional, List
from app.services.supabase_service import SupabaseService
from app.services.encryption_service import encryption_service
from app.models.debt import DebtCreate, DebtUpdate, DebtResponse, DebtListResponse, DebtSummary
from app.core.errors import NotFoundError, DatabaseError


class DebtRepository:
    """Repository for debt data operations."""
    
    TABLE = "debts"
    
    @staticmethod
    def _decrypt_debt(db_debt: dict) -> DebtResponse:
        """
        Decrypt encrypted fields from database record.
        
        Args:
            db_debt: Raw debt record from database
        
        Returns:
            DebtResponse with decrypted financial fields
        """
        return DebtResponse(
            id=db_debt["id"],
            user_id=db_debt["user_id"],
            creditor_name=db_debt["creditor_name"],
            debt_type=db_debt["debt_type"],
            balance=float(encryption_service.decrypt_server_only(db_debt["current_balance_encrypted"])),
            apr=float(encryption_service.decrypt_server_only(db_debt["interest_rate_encrypted"])),
            minimum_payment=float(encryption_service.decrypt_server_only(db_debt["minimum_payment_encrypted"])),
            account_number_last4=db_debt.get("account_number_last4"),
            due_date=db_debt.get("due_date_day"),
            notes=db_debt.get("notes"),
            is_active=db_debt["is_active"],
            is_paid_off=db_debt["is_paid_off"],
            paid_off_at=db_debt.get("paid_off_at"),
            created_at=db_debt["created_at"],
            updated_at=db_debt["updated_at"]
        )
    
    @staticmethod
    async def create(user_id: str, debt_data: DebtCreate, token: Optional[str] = None) -> DebtResponse:
        """
        Create a new debt for a user.
        Encrypts plaintext financial data with server key before storage.
        
        Args:
            user_id: User UUID
            debt_data: Debt creation data (plaintext)
            token: Optional JWT token
        
        Returns:
            Created debt (with decrypted values)
        
        Raises:
            DatabaseError: If creation fails
        """
        # Encrypt plaintext values before storage
        db_data = {
            "user_id": user_id,
            "creditor_name": debt_data.creditor_name,
            "debt_type": debt_data.debt_type.value,
            "current_balance_encrypted": encryption_service.encrypt_server_only(str(debt_data.balance)),
            "interest_rate_encrypted": encryption_service.encrypt_server_only(str(debt_data.apr)),
            "minimum_payment_encrypted": encryption_service.encrypt_server_only(str(debt_data.minimum_payment)),
            "due_date_day": debt_data.due_date,
            "notes": debt_data.notes,
            "is_active": True,
            "is_paid_off": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await SupabaseService.insert(DebtRepository.TABLE, db_data, token=token)
        # Decrypt before returning
        return DebtRepository._decrypt_debt(result)
    
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
        return DebtRepository._decrypt_debt(results[0]) if results else None
    
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
        
        debts = [DebtRepository._decrypt_debt(row) for row in results]
        
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
    async def get_active_debts(user_id: str, token: Optional[str] = None) -> List[DebtResponse]:
        """
        Get only active (non-paid-off) debts for a user.
        
        Args:
            user_id: User UUID
            token: Optional JWT token for authenticated request
        
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
            order_by="created_at",
            token=token
        )
        
        return [DebtRepository._decrypt_debt(row) for row in results]
    
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
        
        # Prepare update data (exclude None values and encrypt financial fields)
        db_data = {}
        update_dict = update_data.model_dump(exclude_none=True)
        
        for key, value in update_dict.items():
            if key == "debt_type" and value is not None:
                db_data[key] = value.value
            elif key == "balance":
                db_data["current_balance_encrypted"] = encryption_service.encrypt_server_only(str(value))
            elif key == "apr":
                db_data["interest_rate_encrypted"] = encryption_service.encrypt_server_only(str(value))
            elif key == "minimum_payment":
                db_data["minimum_payment_encrypted"] = encryption_service.encrypt_server_only(str(value))
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
        
        return DebtRepository._decrypt_debt(results[0])
    
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
        
        return DebtRepository._decrypt_debt(results[0])
    
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
