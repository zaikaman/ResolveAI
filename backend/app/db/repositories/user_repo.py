"""
User repository for CRUD operations with encryption support.
"""

from datetime import datetime
from typing import Optional
from app.services.supabase_service import SupabaseService
from app.models.user import UserCreate, UserProfile, UserUpdate
from app.core.errors import NotFoundError, ConflictError, DatabaseError


class UserRepository:
    """Repository for user data operations."""
    
    TABLE = "users"
    
    @staticmethod
    async def create(user_data: UserCreate) -> UserProfile:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
        
        Returns:
            Created user profile
        
        Raises:
            ConflictError: If email already exists
            DatabaseError: If creation fails
        """
        # Check if user already exists
        existing = await UserRepository.get_by_email(user_data.email)
        if existing:
            raise ConflictError(
                message=f"User with email {user_data.email} already exists",
                details={"email": user_data.email}
            )
        
        # Prepare user data
        db_data = {
            "email": user_data.email,
            "full_name": user_data.full_name,
            "avatar_url": user_data.avatar_url,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert user
        result = await SupabaseService.insert(UserRepository.TABLE, db_data)
        return UserProfile(**result)
    
    @staticmethod
    async def get_by_id(user_id: str) -> Optional[UserProfile]:
        """
        Get user by ID.
        
        Args:
            user_id: User UUID
        
        Returns:
            User profile or None if not found
        """
        result = await SupabaseService.get_by_id(UserRepository.TABLE, user_id)
        return UserProfile(**result) if result else None
    
    @staticmethod
    async def get_by_email(email: str) -> Optional[UserProfile]:
        """
        Get user by email.
        
        Args:
            email: User email address
        
        Returns:
            User profile or None if not found
        """
        results = await SupabaseService.select(
            UserRepository.TABLE,
            filters={"email": email}
        )
        return UserProfile(**results[0]) if results else None
    
    @staticmethod
    async def update(user_id: str, update_data: UserUpdate) -> UserProfile:
        """
        Update user profile.
        
        Args:
            user_id: User UUID
            update_data: Fields to update
        
        Returns:
            Updated user profile
        
        Raises:
            NotFoundError: If user doesn't exist
        """
        # Verify user exists
        existing = await UserRepository.get_by_id(user_id)
        if not existing:
            raise NotFoundError("User", user_id)
        
        # Prepare update data (exclude None values)
        db_data = update_data.model_dump(exclude_none=True)
        db_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update user
        results = await SupabaseService.update(
            UserRepository.TABLE,
            filters={"id": user_id},
            data=db_data
        )
        
        if not results:
            raise DatabaseError(
                message="User update returned no data",
                operation="update"
            )
        
        return UserProfile(**results[0])
    
    @staticmethod
    async def update_last_login(user_id: str) -> None:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User UUID
        """
        await SupabaseService.update(
            UserRepository.TABLE,
            filters={"id": user_id},
            data={"last_login_at": datetime.utcnow().isoformat()}
        )
    
    @staticmethod
    async def complete_onboarding(
        user_id: str,
        monthly_income_encrypted: str,
        monthly_expenses_encrypted: str,
        available_for_debt_encrypted: str
    ) -> UserProfile:
        """
        Mark onboarding as complete with initial financial data.
        
        Args:
            user_id: User UUID
            monthly_income_encrypted: Encrypted monthly income
            monthly_expenses_encrypted: Encrypted monthly expenses
            available_for_debt_encrypted: Encrypted available for debt
        
        Returns:
            Updated user profile
        
        Raises:
            NotFoundError: If user doesn't exist
        """
        db_data = {
            "monthly_income_encrypted": monthly_income_encrypted,
            "monthly_expenses_encrypted": monthly_expenses_encrypted,
            "available_for_debt_encrypted": available_for_debt_encrypted,
            "onboarding_completed": True,
            "terms_accepted_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        results = await SupabaseService.update(
            UserRepository.TABLE,
            filters={"id": user_id},
            data=db_data
        )
        
        if not results:
            raise NotFoundError("User", user_id)
        
        return UserProfile(**results[0])
    
    @staticmethod
    async def delete(user_id: str) -> None:
        """
        Delete user (soft delete by setting deleted_at).
        
        Args:
            user_id: User UUID
        
        Raises:
            NotFoundError: If user doesn't exist
        """
        # For now, hard delete. Add soft delete later if needed.
        results = await SupabaseService.delete(
            UserRepository.TABLE,
            filters={"id": user_id}
        )
        
        if not results:
            raise NotFoundError("User", user_id)
