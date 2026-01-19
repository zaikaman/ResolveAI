"""
Input validators for financial data.

Aligned with constitution CQ-001 test coverage requirement and data-model.md constraints.
"""

from decimal import Decimal, InvalidOperation
from typing import Optional
from .errors import ValidationError


def validate_positive_decimal(
    value: str | float | Decimal,
    field_name: str,
    allow_zero: bool = False
) -> Decimal:
    """
    Validate that a value is a positive decimal.
    
    Args:
        value: Value to validate (string, float, or Decimal)
        field_name: Field name for error messages
        allow_zero: Whether to allow zero values
    
    Returns:
        Validated Decimal value
    
    Raises:
        ValidationError: If value is invalid
    """
    try:
        decimal_value = Decimal(str(value))
    except (ValueError, InvalidOperation):
        raise ValidationError(
            message=f"{field_name} must be a valid number",
            field=field_name
        )
    
    if allow_zero:
        if decimal_value < 0:
            raise ValidationError(
                message=f"{field_name} must be greater than or equal to 0",
                field=field_name
            )
    else:
        if decimal_value <= 0:
            raise ValidationError(
                message=f"{field_name} must be greater than 0",
                field=field_name
            )
    
    return decimal_value


def validate_balance(balance: str | float | Decimal) -> Decimal:
    """
    Validate debt balance (must be > 0).
    
    Per data-model.md: Debt balances must be positive.
    """
    return validate_positive_decimal(balance, "balance", allow_zero=False)


def validate_apr(apr: str | float | Decimal) -> Decimal:
    """
    Validate APR (must be 0-50%).
    
    Per data-model.md: APR typically 0-50% (0-5000 basis points).
    """
    decimal_apr = validate_positive_decimal(apr, "APR", allow_zero=True)
    
    if decimal_apr > 50:
        raise ValidationError(
            message="APR must be between 0% and 50%",
            field="apr",
            details={"value": str(decimal_apr), "max": "50"}
        )
    
    return decimal_apr


def validate_income(income: str | float | Decimal) -> Decimal:
    """
    Validate monthly income (must be ≥ 0).
    
    Per data-model.md: Income can be 0 for non-working users.
    """
    return validate_positive_decimal(income, "monthly_income", allow_zero=True)


def validate_expenses(expenses: str | float | Decimal) -> Decimal:
    """
    Validate monthly expenses (must be ≥ 0).
    
    Per data-model.md: Expenses must be non-negative.
    """
    return validate_positive_decimal(expenses, "monthly_expenses", allow_zero=True)


def validate_payment_amount(amount: str | float | Decimal) -> Decimal:
    """
    Validate payment amount (must be > 0).
    
    Payments must be positive values.
    """
    return validate_positive_decimal(amount, "payment_amount", allow_zero=False)


def validate_minimum_payment(minimum_payment: str | float | Decimal) -> Decimal:
    """
    Validate minimum payment (must be ≥ 0).
    
    Some debts may have no minimum payment requirement.
    """
    return validate_positive_decimal(minimum_payment, "minimum_payment", allow_zero=True)


def validate_available_for_debt(
    income: Decimal,
    expenses: Decimal,
    available: Decimal
) -> None:
    """
    Validate that available for debt doesn't exceed income - expenses.
    
    Args:
        income: Monthly income
        expenses: Monthly expenses
        available: Amount available for debt repayment
    
    Raises:
        ValidationError: If available > income - expenses
    """
    max_available = income - expenses
    
    if available > max_available:
        raise ValidationError(
            message=f"Available for debt ({available}) cannot exceed income minus expenses ({max_available})",
            field="available_for_debt",
            details={
                "income": str(income),
                "expenses": str(expenses),
                "available": str(available),
                "max_available": str(max_available)
            }
        )
    
    if available < 0:
        raise ValidationError(
            message="Available for debt must be non-negative",
            field="available_for_debt"
        )


def validate_debt_sustainability(
    total_minimum_payments: Decimal,
    available_for_debt: Decimal
) -> tuple[bool, Optional[str]]:
    """
    Check if debt repayment is sustainable.
    
    Args:
        total_minimum_payments: Sum of all minimum payments
        available_for_debt: Amount available for debt repayment
    
    Returns:
        (is_sustainable, warning_message)
    """
    if available_for_debt < total_minimum_payments:
        deficit = total_minimum_payments - available_for_debt
        return False, (
            f"Minimum payments ({total_minimum_payments}) exceed available funds "
            f"({available_for_debt}) by {deficit}. Consider debt consolidation or "
            f"increasing income."
        )
    
    # Warn if very tight (less than 10% buffer)
    buffer = available_for_debt - total_minimum_payments
    buffer_percentage = (buffer / total_minimum_payments * 100) if total_minimum_payments > 0 else 100
    
    if buffer_percentage < 10:
        return True, (
            f"Warning: Only {buffer} buffer above minimum payments. "
            f"Consider building emergency fund first."
        )
    
    return True, None


def validate_creditor_name(name: str) -> str:
    """
    Validate creditor name (non-empty, max 255 chars).
    
    Args:
        name: Creditor name
    
    Returns:
        Validated creditor name
    
    Raises:
        ValidationError: If name is invalid
    """
    if not name or not name.strip():
        raise ValidationError(
            message="Creditor name cannot be empty",
            field="creditor_name"
        )
    
    name = name.strip()
    
    if len(name) > 255:
        raise ValidationError(
            message="Creditor name must be 255 characters or less",
            field="creditor_name",
            details={"length": len(name), "max": 255}
        )
    
    return name
