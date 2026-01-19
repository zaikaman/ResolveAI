"""
User repository for CRUD operations with encryption support.
"""

from datetime import datetime
from typing import Optional
from app.services.supabase_service import SupabaseService
from app.models.user import UserCreate, UserProfile, UserUpdate
from app.core.errors import NotFoundError, ConflictError, DatabaseError
from app.services.encryption_service import encryption_service


class UserRepository:
    """Repository for user data operations."""
    
    TABLE = "users"
    
    @staticmethod
    async def create(user_data: UserCreate, token: Optional[str] = None) -> UserProfile:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            token: Optional JWT token for authenticated request
        
        Returns:
            Created user profile
        
        Raises:
            ConflictError: If email already exists
            DatabaseError: If creation fails
        """
        # Check if user already exists by email (with token for RLS)
        existing = await UserRepository.get_by_email(user_data.email, token=token)
        if existing:
            print(f"[USER_REPO] User already exists with email {user_data.email}, returning existing user")
            return existing
        
        # If user_data has an ID, also check by ID (with token for RLS)
        if user_data.id:
            existing_by_id = await UserRepository.get_by_id(user_data.id, token=token)
            if existing_by_id:
                print(f"[USER_REPO] User already exists with ID {user_data.id}, returning existing user")
                return existing_by_id
        
        # Prepare user data
        db_data = {
            "email": user_data.email,
            "full_name": user_data.full_name,
            "timezone": "UTC",  # Use shorter default to avoid varchar(10) constraint
            "language": "en",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if user_data.id:
            db_data["id"] = user_data.id
        
        # Insert user
        try:
            print(f"[USER_REPO] Creating user in DB: {db_data}")
            result = await SupabaseService.insert(UserRepository.TABLE, db_data, token=token)
            print(f"[USER_REPO] User created successfully: {result.get('id')}")
            return UserProfile(**result)
        except Exception as e:
            print(f"[USER_REPO] Error creating user: {e}")
            # If insert fails due to duplicate, try to fetch the user one more time
            if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                print(f"[USER_REPO] Duplicate detected, fetching existing user")
                existing = await UserRepository.get_by_email(user_data.email, token=token)
                if existing:
                    return existing
                if user_data.id:
                    existing_by_id = await UserRepository.get_by_id(user_data.id, token=token)
                    if existing_by_id:
                        return existing_by_id
            raise DatabaseError(
                message=f"Failed to create user: {str(e)}",
                operation="insert"
            )
    
    @staticmethod
    async def get_by_id(user_id: str, token: Optional[str] = None) -> Optional[UserProfile]:
        """
        Get user by ID.
        
        Args:
            user_id: User UUID
            token: Optional JWT token for RLS
        
        Returns:
            User profile or None if not found
        """
        result = await SupabaseService.get_by_id(UserRepository.TABLE, user_id, token=token)
        return UserProfile(**result) if result else None
    
    @staticmethod
    async def get_by_email(email: str, token: Optional[str] = None) -> Optional[UserProfile]:
        """
        Get user by email.
        
        Args:
            email: User email address
            token: Optional JWT token for RLS
        
        Returns:
            User profile or None if not found
        """
        results = await SupabaseService.select(
            UserRepository.TABLE,
            filters={"email": email},
            token=token
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
        monthly_income: float,
        monthly_expenses: float,
        available_for_debt: float
    ) -> UserProfile:
        """
        Mark onboarding as complete with initial financial data.
        Encrypts plaintext values with server key before storage.
        
        Args:
            user_id: User UUID
            monthly_income: Monthly income (plaintext)
            monthly_expenses: Monthly expenses (plaintext)
            available_for_debt: Available for debt (plaintext)
        
        Returns:
            Updated user profile
        
        Raises:
            NotFoundError: If user doesn't exist
        """
        # Encrypt plaintext values with server key before storage
        db_data = {
            "monthly_income_encrypted": encryption_service.encrypt_server_only(str(monthly_income)),
            "monthly_expenses_encrypted": encryption_service.encrypt_server_only(str(monthly_expenses)),
            "available_for_debt_encrypted": encryption_service.encrypt_server_only(str(available_for_debt)),
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
