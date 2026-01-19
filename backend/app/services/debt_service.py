"""
Debt service for business logic operations.
"""

from typing import List, Optional
from app.db.repositories.debt_repo import DebtRepository
from app.models.debt import DebtCreate, DebtUpdate, DebtResponse, DebtListResponse
from app.core.errors import ValidationError


class DebtService:
    """Service for debt-related business logic."""
    
    MAX_DEBTS_PER_USER = 50  # Reasonable limit
    
    @staticmethod
    async def create_debt(user_id: str, debt_data: DebtCreate, token: Optional[str] = None) -> DebtResponse:
        """
        Create a new debt for a user with validation.
        
        Args:
            user_id: User UUID
            debt_data: Debt creation data
        
        Returns:
            Created debt
        
        Raises:
            ValidationError: If debt limit exceeded
        """
        # Check debt limit
        current_count = await DebtRepository.count_by_user(user_id)
        if current_count >= DebtService.MAX_DEBTS_PER_USER:
            raise ValidationError(
                message=f"Maximum {DebtService.MAX_DEBTS_PER_USER} debts allowed per user",
                details={"current_count": current_count, "max_allowed": DebtService.MAX_DEBTS_PER_USER}
            )
        
        return await DebtRepository.create(user_id, debt_data, token=token)
    
    @staticmethod
    async def get_debt(debt_id: str, user_id: str) -> Optional[DebtResponse]:
        """
        Get a specific debt.
        
        Args:
            debt_id: Debt UUID
            user_id: User UUID
        
        Returns:
            Debt or None if not found
        """
        return await DebtRepository.get_by_id(debt_id, user_id)
    
    @staticmethod
    async def get_all_debts(
        user_id: str,
        include_inactive: bool = False
    ) -> DebtListResponse:
        """
        Get all debts for a user.
        
        Args:
            user_id: User UUID
            include_inactive: Include paid-off debts
        
        Returns:
            DebtListResponse with debts and summary
        """
        return await DebtRepository.get_all_by_user(user_id, include_inactive)
    
    @staticmethod
    async def get_active_debts(user_id: str) -> List[DebtResponse]:
        """
        Get only active debts for plan generation.
        
        Args:
            user_id: User UUID
        
        Returns:
            List of active debts
        """
        return await DebtRepository.get_active_debts(user_id)
    
    @staticmethod
    async def update_debt(
        debt_id: str,
        user_id: str,
        update_data: DebtUpdate,
        token: Optional[str] = None
    ) -> DebtResponse:
        """
        Update a debt.
        
        Args:
            debt_id: Debt UUID
            user_id: User UUID
            update_data: Fields to update
        
        Returns:
            Updated debt
        """
        return await DebtRepository.update(debt_id, user_id, update_data, token=token)
    
    @staticmethod
    async def mark_debt_paid_off(debt_id: str, user_id: str, token: Optional[str] = None) -> DebtResponse:
        """
        Mark a debt as paid off.
        
        Args:
            debt_id: Debt UUID
            user_id: User UUID
        
        Returns:
            Updated debt
        """
        return await DebtRepository.mark_paid_off(debt_id, user_id, token=token)
    
    @staticmethod
    async def delete_debt(debt_id: str, user_id: str, token: Optional[str] = None) -> None:
        """
        Delete a debt.
        
        Args:
            debt_id: Debt UUID
            user_id: User UUID
        """
        await DebtRepository.delete(debt_id, user_id, token=token)
    
    @staticmethod
    async def has_debts(user_id: str) -> bool:
        """
        Check if user has any debts.
        
        Args:
            user_id: User UUID
        
        Returns:
            True if user has debts
        """
        count = await DebtRepository.count_by_user(user_id)
        return count > 0
