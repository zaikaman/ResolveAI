"""
Optimization service for debt repayment calculations using mathematical optimization.

Implements avalanche (highest APR first) and snowball (lowest balance first) strategies.
"""

from datetime import date, timedelta
from typing import List, Tuple
from dataclasses import dataclass
from app.models.plan import (
    RepaymentStrategy,
    PaymentScheduleItem,
    MonthlyBreakdown,
    PlanProjection,
    DebtPayoffInfo
)


@dataclass
class DebtInfo:
    """Internal representation of a debt for optimization."""
    id: str
    name: str
    balance: float
    apr: float
    minimum_payment: float


@dataclass
class OptimizationResult:
    """Result of the debt optimization calculation."""
    debt_free_date: date
    total_months: int
    total_interest: float
    total_paid: float
    monthly_payment: float
    monthly_schedule: List[MonthlyBreakdown]
    projections: List[PlanProjection]
    payoff_order: List[DebtPayoffInfo]


class OptimizationService:
    """Service for calculating optimized debt repayment plans."""
    
    @staticmethod
    def calculate_plan(
        debts: List[DebtInfo],
        available_monthly: float,
        strategy: RepaymentStrategy,
        extra_payment: float = 0.0,
        start_date: date | None = None
    ) -> OptimizationResult:
        """
        Calculate an optimized repayment plan.
        
        Args:
            debts: List of debts with balance, APR, minimum payment
            available_monthly: Total available for debt payments per month
            strategy: Avalanche or snowball
            extra_payment: Additional payment above minimums
            start_date: Start date for the plan (default: next month)
        
        Returns:
            OptimizationResult with full plan details
        """
        if not debts:
            today = start_date or date.today()
            return OptimizationResult(
                debt_free_date=today,
                total_months=0,
                total_interest=0.0,
                total_paid=0.0,
                monthly_payment=0.0,
                monthly_schedule=[],
                projections=[],
                payoff_order=[]
            )
        
        # Initialize
        if start_date is None:
            today = date.today()
            start_date = date(today.year, today.month, 1) + timedelta(days=32)
            start_date = date(start_date.year, start_date.month, 1)
        
        # Sort debts based on strategy
        sorted_debts = OptimizationService._sort_debts(debts, strategy)
        
        # Calculate minimum payments total
        min_payment_total = sum(d.minimum_payment for d in sorted_debts)
        
        # Total monthly payment is available_monthly + extra_payment
        monthly_payment = min(available_monthly + extra_payment, 
                             sum(d.balance for d in sorted_debts) + 1000)  # Don't overpay
        
        # If we can't afford minimums, use what we have
        if monthly_payment < min_payment_total:
            monthly_payment = min_payment_total
        
        # Run the simulation
        return OptimizationService._simulate_payoff(
            sorted_debts,
            monthly_payment,
            start_date,
            strategy
        )
    
    @staticmethod
    def calculate_minimum_only_plan(
        debts: List[DebtInfo],
        start_date: date | None = None
    ) -> Tuple[int, float]:
        """
        Calculate months and interest if only paying minimums.
        Used for comparison / "interest saved" calculation.
        
        Args:
            debts: List of debts
            start_date: Start date
        
        Returns:
            Tuple of (total_months, total_interest)
        """
        if not debts:
            return (0, 0.0)
        
        if start_date is None:
            today = date.today()
            start_date = date(today.year, today.month, 1) + timedelta(days=32)
            start_date = date(start_date.year, start_date.month, 1)
        
        # Create copies of balances
        balances = {d.id: d.balance for d in debts}
        total_interest = 0.0
        month = 0
        max_months = 600  # 50 years cap
        
        while any(b > 0.01 for b in balances.values()) and month < max_months:
            month += 1
            
            for debt in debts:
                if balances[debt.id] <= 0.01:
                    continue
                
                # Calculate monthly interest
                monthly_rate = debt.apr / 12 / 100
                interest = balances[debt.id] * monthly_rate
                total_interest += interest
                
                # Apply minimum payment
                payment = min(debt.minimum_payment, balances[debt.id] + interest)
                principal = payment - interest
                balances[debt.id] = max(0, balances[debt.id] - principal)
        
        return (month, total_interest)
    
    @staticmethod
    def _sort_debts(
        debts: List[DebtInfo],
        strategy: RepaymentStrategy
    ) -> List[DebtInfo]:
        """Sort debts based on strategy."""
        if strategy == RepaymentStrategy.AVALANCHE:
            # Highest APR first
            return sorted(debts, key=lambda d: d.apr, reverse=True)
        else:
            # Snowball: lowest balance first
            return sorted(debts, key=lambda d: d.balance)
    
    @staticmethod
    def _simulate_payoff(
        debts: List[DebtInfo],
        monthly_payment: float,
        start_date: date,
        strategy: RepaymentStrategy
    ) -> OptimizationResult:
        """
        Simulate the payoff process month by month.
        
        Returns full optimization result with schedules and projections.
        """
        # Initialize balances
        balances = {d.id: d.balance for d in debts}
        debt_names = {d.id: d.name for d in debts}
        debt_aprs = {d.id: d.apr for d in debts}
        debt_mins = {d.id: d.minimum_payment for d in debts}
        
        monthly_schedule: List[MonthlyBreakdown] = []
        projections: List[PlanProjection] = []
        payoff_order: List[DebtPayoffInfo] = []
        
        total_interest_paid = 0.0
        total_principal_paid = 0.0
        month = 0
        max_months = 600
        
        current_date = start_date
        
        while any(b > 0.01 for b in balances.values()) and month < max_months:
            month += 1
            
            # Calculate interest for this month
            interest_this_month = {}
            for debt in debts:
                if balances[debt.id] > 0.01:
                    monthly_rate = debt.apr / 12 / 100
                    interest_this_month[debt.id] = balances[debt.id] * monthly_rate
                else:
                    interest_this_month[debt.id] = 0
            
            # Allocate payments
            remaining_budget = monthly_payment
            month_payments: List[PaymentScheduleItem] = []
            
            # First, pay minimums on all active debts
            for debt in debts:
                if balances[debt.id] <= 0.01:
                    continue
                
                interest = interest_this_month[debt.id]
                min_payment = min(debt_mins[debt.id], balances[debt.id] + interest)
                
                if remaining_budget >= min_payment:
                    principal = max(0, min_payment - interest)
                    balances[debt.id] -= principal
                    remaining_budget -= min_payment
                    total_interest_paid += interest
                    total_principal_paid += principal
                    
                    is_payoff = balances[debt.id] <= 0.01
                    
                    month_payments.append(PaymentScheduleItem(
                        month=month,
                        date=current_date,
                        debt_id=debt.id,
                        debt_name=debt_names[debt.id],
                        payment_amount=min_payment,
                        principal=principal,
                        interest=interest,
                        remaining_balance=max(0, balances[debt.id]),
                        is_payoff_month=is_payoff
                    ))
                    
                    if is_payoff and debt.id not in [p.debt_id for p in payoff_order]:
                        payoff_order.append(DebtPayoffInfo(
                            debt_id=debt.id,
                            debt_name=debt_names[debt.id],
                            payoff_month=month,
                            payoff_date=current_date,
                            total_interest_paid=total_interest_paid,
                            total_paid=total_principal_paid + total_interest_paid
                        ))
            
            # Then, apply extra to priority debt (based on strategy order)
            if remaining_budget > 0:
                for debt in debts:
                    if balances[debt.id] <= 0.01:
                        continue
                    
                    # Find existing payment for this debt
                    existing_payment = next(
                        (p for p in month_payments if p.debt_id == debt.id),
                        None
                    )
                    
                    if existing_payment is None:
                        continue
                    
                    extra = min(remaining_budget, balances[debt.id])
                    if extra > 0:
                        balances[debt.id] -= extra
                        remaining_budget -= extra
                        total_principal_paid += extra
                        
                        # Update the payment record
                        idx = month_payments.index(existing_payment)
                        is_payoff = balances[debt.id] <= 0.01
                        
                        month_payments[idx] = PaymentScheduleItem(
                            month=month,
                            date=current_date,
                            debt_id=debt.id,
                            debt_name=debt_names[debt.id],
                            payment_amount=existing_payment.payment_amount + extra,
                            principal=existing_payment.principal + extra,
                            interest=existing_payment.interest,
                            remaining_balance=max(0, balances[debt.id]),
                            is_payoff_month=is_payoff
                        )
                        
                        if is_payoff and debt.id not in [p.debt_id for p in payoff_order]:
                            payoff_order.append(DebtPayoffInfo(
                                debt_id=debt.id,
                                debt_name=debt_names[debt.id],
                                payoff_month=month,
                                payoff_date=current_date,
                                total_interest_paid=total_interest_paid,
                                total_paid=total_principal_paid + total_interest_paid
                            ))
                    
                    # Only apply extra to first (priority) debt
                    break
            
            # Record monthly breakdown
            total_remaining = sum(max(0, b) for b in balances.values())
            monthly_schedule.append(MonthlyBreakdown(
                month=month,
                date=current_date,
                total_payment=sum(p.payment_amount for p in month_payments),
                payments=month_payments,
                total_remaining=total_remaining
            ))
            
            # Record projection
            projections.append(PlanProjection(
                month=month,
                date=current_date,
                total_remaining=total_remaining,
                cumulative_interest_paid=total_interest_paid,
                cumulative_principal_paid=total_principal_paid
            ))
            
            # Advance date
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
        
        debt_free_date = current_date
        
        return OptimizationResult(
            debt_free_date=debt_free_date,
            total_months=month,
            total_interest=total_interest_paid,
            total_paid=total_principal_paid + total_interest_paid,
            monthly_payment=monthly_payment,
            monthly_schedule=monthly_schedule,
            projections=projections,
            payoff_order=payoff_order
        )
