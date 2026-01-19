"""
Debts router for debt CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import List
from app.models.debt import DebtCreate, DebtUpdate, DebtResponse, DebtListResponse
from app.services.debt_service import DebtService
from app.dependencies import get_current_user
from app.models.user import UserResponse
from app.core.errors import NotFoundError, ValidationError

router = APIRouter(prefix="/debts", tags=["debts"])


@router.get("", response_model=DebtListResponse)
async def get_debts(
    include_inactive: bool = False,
    current_user: UserResponse = Depends(get_current_user)
) -> DebtListResponse:
    """
    Get all debts for the current user.
    
    Args:
        include_inactive: Include paid-off debts
        current_user: Authenticated user
    
    Returns:
        List of debts with summary
    """
    return await DebtService.get_all_debts(current_user.id, include_inactive)


@router.get("/{debt_id}", response_model=DebtResponse)
async def get_debt(
    debt_id: str,
    current_user: UserResponse = Depends(get_current_user)
) -> DebtResponse:
    """
    Get a specific debt by ID.
    
    Args:
        debt_id: Debt UUID
        current_user: Authenticated user
    
    Returns:
        Debt details
    
    Raises:
        404: If debt not found
    """
    debt = await DebtService.get_debt(debt_id, current_user.id)
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Debt {debt_id} not found"
        )
    return debt


@router.post("", response_model=DebtResponse, status_code=status.HTTP_201_CREATED)
async def create_debt(
    debt_data: DebtCreate,
    current_user: UserResponse = Depends(get_current_user),
    authorization: str = Header(...)
) -> DebtResponse:
    """
    Create a new debt.
    
    Args:
        debt_data: Debt creation data (with encrypted fields)
        current_user: Authenticated user
    
    Returns:
        Created debt
    
    Raises:
        400: If validation fails (e.g., max debts exceeded)
    """
    try:
        print(f"[DEBTS] Creating debt for user {current_user.id}")
        print(f"[DEBTS] Creditor: {debt_data.creditor_name}")
        print(f"[DEBTS] Auth header present: {bool(authorization)}")
        return await DebtService.create_debt(current_user.id, debt_data, token=authorization.split(" ")[1])
    except ValidationError as e:
        print(f"[DEBTS] ValidationError: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        print(f"[DEBTS] Unexpected error creating debt: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal system error: {str(e)}"
        )


@router.patch("/{debt_id}", response_model=DebtResponse)
async def update_debt(
    debt_id: str,
    update_data: DebtUpdate,
    current_user: UserResponse = Depends(get_current_user),
    authorization: str = Header(...)
) -> DebtResponse:
    """
    Update a debt.
    
    Args:
        debt_id: Debt UUID
        update_data: Fields to update
        current_user: Authenticated user
    
    Returns:
        Updated debt
    
    Raises:
        404: If debt not found
    """
    try:
        return await DebtService.update_debt(debt_id, current_user.id, update_data, token=authorization.split(" ")[1])
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Debt {debt_id} not found"
        )


@router.post("/{debt_id}/mark-paid", response_model=DebtResponse)
async def mark_debt_paid_off(
    debt_id: str,
    current_user: UserResponse = Depends(get_current_user),
    authorization: str = Header(...)
) -> DebtResponse:
    """
    Mark a debt as paid off.
    
    Args:
        debt_id: Debt UUID
        current_user: Authenticated user
    
    Returns:
        Updated debt
    
    Raises:
        404: If debt not found
    """
    try:
        return await DebtService.mark_debt_paid_off(debt_id, current_user.id, token=authorization.split(" ")[1])
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Debt {debt_id} not found"
        )


@router.delete("/{debt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_debt(
    debt_id: str,
    current_user: UserResponse = Depends(get_current_user),
    authorization: str = Header(...)
) -> None:
    """
    Delete a debt.
    
    Args:
        debt_id: Debt UUID
        current_user: Authenticated user
    
    Raises:
        404: If debt not found
    """
    try:
        await DebtService.delete_debt(debt_id, current_user.id, token=authorization.split(" ")[1])
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Debt {debt_id} not found"
        )
