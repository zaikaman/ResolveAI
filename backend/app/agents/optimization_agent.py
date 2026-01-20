"""
Optimization Agent - AI-powered debt repayment plan optimization.

Uses GPT to analyze user's financial situation and generate complete
debt repayment plans with detailed schedules and reasoning.
"""

from typing import List, Optional, Dict, Any
from datetime import date, timedelta
import json
import time

from app.agents.base_agent import BaseAgent
from app.services.optimization_service import OptimizationService, OptimizationResult, DebtInfo
from app.models.debt import DebtResponse
from app.models.plan import RepaymentStrategy, PaymentScheduleItem, MonthlyBreakdown, PlanProjection, DebtPayoffInfo
from app.core.openai_client import openai_client


class OptimizationAgent(BaseAgent):
    """
    AI-powered agent for creating optimized debt repayment plans.
    
    Uses GPT to:
    1. Analyze user's financial psychology and situation
    2. Recommend optimal strategy (avalanche vs snowball)
    3. Suggest budget optimizations and extra payment amounts
    4. Provide personalized reasoning for the plan
    
    Then executes mathematical optimization for precise schedules.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__(
            agent_name="OptimizationAgent",
            description="AI-powered debt repayment plan creator with mathematical optimization"
        )
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def optimize_repayment_plan(
        self,
        user_id: str,
        debts: List[DebtResponse],
        monthly_budget: float,
        strategy: str = "auto",
        constraints: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """
        Create an AI-optimized repayment plan.
        
        Args:
            user_id: User UUID
            debts: List of user's debts
            monthly_budget: Available monthly payment amount
            strategy: Repayment strategy ("auto" for AI selection, "avalanche", or "snowball")
            constraints: Optional constraints (extra_payment, start_date, etc.)
            user_context: Additional context (payment_history, risk_factors, goals, etc.)
        
        Returns:
            OptimizationResult with complete plan details and AI reasoning
        """
        return await self.trace_execution(
            self._optimize_plan,
            user_id=user_id,
            debts=debts,
            monthly_budget=monthly_budget,
            strategy=strategy,
            constraints=constraints or {},
            user_context=user_context or {}
        )
    
    async def _optimize_plan(
        self,
        user_id: str,
        debts: List[DebtResponse],
        monthly_budget: float,
        strategy: str,
        constraints: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> OptimizationResult:
        """Internal optimization logic with AI-powered plan generation."""
        
        # Convert DebtResponse to DebtInfo
        debt_infos = [
            DebtInfo(
                id=str(debt.id),
                name=debt.creditor_name,
                balance=debt.balance,
                apr=debt.apr,
                minimum_payment=debt.minimum_payment
            )
            for debt in debts
            if not debt.is_paid_off  # Only include active debts
        ]
        
        # If strategy is "auto", use AI to determine best approach
        if strategy.lower() == "auto":
            ai_recommendation = await self._get_ai_strategy_recommendation(
                debts=debts,
                monthly_budget=monthly_budget,
                user_context=user_context
            )
            strategy = ai_recommendation["strategy"]
            # AI might suggest extra payment optimization
            if "suggested_extra_payment" in ai_recommendation and "extra_payment" not in constraints:
                constraints["extra_payment"] = ai_recommendation["suggested_extra_payment"]
        
        # Parse strategy
        repayment_strategy = RepaymentStrategy.AVALANCHE if strategy.lower() == "avalanche" else RepaymentStrategy.SNOWBALL
        
        # Extract constraints
        extra_payment = constraints.get("extra_payment", 0.0)
        start_date = constraints.get("start_date")
        
        # Use AI to generate the complete repayment plan
        result = await self._generate_ai_plan(
            debts=debts,
            debt_infos=debt_infos,
            monthly_budget=monthly_budget,
            strategy=repayment_strategy,
            extra_payment=extra_payment,
            start_date=start_date,
            user_context=user_context
        )
        
        # Add strategy name to result
        result.strategy = strategy.lower()
        
        return result
    
    async def _get_ai_strategy_recommendation(
        self,
        debts: List[DebtResponse],
        monthly_budget: float,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use AI to recommend optimal repayment strategy."""
        
        total_debt = sum(d.balance for d in debts if not d.is_paid_off)
        total_minimum = sum(d.minimum_payment for d in debts if not d.is_paid_off)
        avg_apr = sum(d.apr for d in debts if not d.is_paid_off) / len([d for d in debts if not d.is_paid_off]) if debts else 0
        highest_apr = max((d.apr for d in debts if not d.is_paid_off), default=0)
        lowest_balance = min((d.balance for d in debts if not d.is_paid_off), default=0)
        
        prompt = self._build_strategy_prompt(
            debts=debts,
            monthly_budget=monthly_budget,
            total_debt=total_debt,
            total_minimum=total_minimum,
            avg_apr=avg_apr,
            highest_apr=highest_apr,
            lowest_balance=lowest_balance,
            user_context=user_context
        )
        
        try:
            response = await openai_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial advisor AI specializing in debt repayment strategies. Analyze the user's situation and recommend either 'avalanche' (highest interest first) or 'snowball' (lowest balance first) strategy. Return ONLY a JSON object."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            recommendation = self._parse_strategy_response(response)
            return recommendation
        
        except Exception as e:
            print(f"AI strategy recommendation failed: {e}")
            # Fallback: avalanche for high APR, snowball for psychological wins
            return {
                "strategy": "avalanche" if highest_apr > 15 else "snowball",
                "reasoning": "Default strategy selected based on interest rates.",
                "suggested_extra_payment": max(0, monthly_budget - total_minimum) * 0.1
            }
    
    def _build_strategy_prompt(
        self,
        debts: List[DebtResponse],
        monthly_budget: float,
        total_debt: float,
        total_minimum: float,
        avg_apr: float,
        highest_apr: float,
        lowest_balance: float,
        user_context: Dict[str, Any]
    ) -> str:
        """Build prompt for AI strategy recommendation."""
        
        debt_summary = "\n".join([
            f"- {d.creditor_name}: ${d.balance:,.2f} at {d.apr}% APR (min payment: ${d.minimum_payment:,.2f})"
            for d in debts if not d.is_paid_off
        ])
        
        context_info = ""
        if user_context:
            if "monthly_income" in user_context and "monthly_expenses" in user_context:
                income = user_context["monthly_income"]
                expenses = user_context["monthly_expenses"]
                context_info += f"\n\n**User's Financial Profile:**"
                context_info += f"\n- Monthly Income: ${income:,.2f}"
                context_info += f"\n- Monthly Expenses: ${expenses:,.2f}"
                context_info += f"\n- Expense Ratio: {(expenses/income*100):.1f}% of income"
                context_info += f"\n- Savings Rate: {((income-expenses)/income*100):.1f}%"
            if "payment_history" in user_context:
                context_info += f"\nPayment History: {user_context['payment_history']}"
            if "risk_factors" in user_context:
                context_info += f"\nRisk Factors: {', '.join([r.get('factor', '') for r in user_context['risk_factors']])}"
            if "goals" in user_context:
                context_info += f"\nUser Goals: {user_context['goals']}"
            if "financial_stress_level" in user_context:
                context_info += f"\nStress Level: {user_context['financial_stress_level']}"
        
        return f"""Analyze this debt situation and recommend the optimal repayment strategy:

**Debts:**
{debt_summary}

**Financial Capacity:**
- Total Debt: ${total_debt:,.2f}
- Monthly Budget: ${monthly_budget:,.2f}
- Required Minimums: ${total_minimum:,.2f}
- Available Extra: ${max(0, monthly_budget - total_minimum):,.2f}
- Average APR: {avg_apr:.1f}%
- Highest APR: {highest_apr:.1f}%
- Lowest Balance: ${lowest_balance:,.2f}
{context_info}

**Strategy Options:**
1. **Avalanche** (highest interest first): Mathematically optimal, saves most money, but slower psychological wins
2. **Snowball** (lowest balance first): Quick wins for motivation, builds momentum, slightly more interest paid

Return a JSON object with:
{{
  "strategy": "avalanche" or "snowball",
  "reasoning": "2-3 sentence explanation of why this strategy fits the user's situation",
  "confidence": 0.0-1.0,
  "suggested_extra_payment": optional number (suggest if user has extra capacity),
  "psychological_factors": ["list", "of", "considerations"],
  "estimated_interest_difference": optional number (if significant difference between strategies)
}}

Consider:
- High APR debts (>20%) strongly favor avalanche
- Users with stress/overwhelm benefit from snowball's quick wins
- Limited extra payment capacity: avalanche saves more
- Multiple small debts: snowball builds momentum
- Personal financial goals and psychological preferences
- If expense ratio is high (>70%), suggest expense reduction opportunities
- If savings rate is low (<20%), consider recommending budget review"""
        
    def _parse_strategy_response(self, response: str) -> Dict[str, Any]:
        """Parse AI strategy recommendation response."""
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                # Validate required fields
                if "strategy" in data and data["strategy"] in ["avalanche", "snowball"]:
                    return data
            
            # Fallback parsing
            if "avalanche" in response.lower():
                return {"strategy": "avalanche", "reasoning": "AI recommended avalanche strategy"}
            else:
                return {"strategy": "snowball", "reasoning": "AI recommended snowball strategy"}
        
        except Exception as e:
            print(f"Failed to parse strategy response: {e}")
            return {"strategy": "avalanche", "reasoning": "Default strategy"}
    
    async def _generate_plan_explanation(
        self,
        debts: List[DebtResponse],
        result: OptimizationResult,
        strategy: str,
        user_context: Dict[str, Any]
    ) -> str:
        """Generate AI explanation of the repayment plan."""
        
        # Add financial context if available
        financial_context = ""
        if "monthly_income" in user_context and "monthly_expenses" in user_context:
            income = user_context["monthly_income"]
            expenses = user_context["monthly_expenses"]
            expense_ratio = (expenses / income * 100) if income > 0 else 0
            financial_context = f"""
**Financial Context:**
- Monthly Income: ${income:,.2f}
- Monthly Expenses: ${expenses:,.2f}
- Expense Ratio: {expense_ratio:.1f}% ({'healthy' if expense_ratio < 70 else 'high - consider optimization'})
"""
        
        prompt = f"""Explain this debt repayment plan in a motivating, clear way:

**Strategy:** {strategy.upper()}
**Timeline:** {result.total_months} months to debt freedom
**Total Interest:** ${result.total_interest:,.2f}
**Monthly Payment:** ${result.monthly_payment:,.2f}
**Total Paid:** ${result.total_paid:,.2f}
{financial_context}
**Payoff Order:**
{chr(10).join([f"{i+1}. {p.debt_name} - {p.payoff_month} months" for i, p in enumerate(result.payoff_order)])}

Write a personalized 3-4 sentence explanation that:
1. Explains WHY this strategy works for their situation
2. Highlights the key benefit (interest saved, timeline, quick wins)
3. Provides encouraging motivation
4. Is practical and actionable

Keep it concise, authentic, and universally relatable."""
        
        try:
            response = await openai_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a supportive financial coach who explains debt plans clearly and motivates users."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )
            
            return response.strip()
        
        except Exception as e:
            print(f"Failed to generate plan explanation: {e}")
            return f"Your {strategy} plan will eliminate all debts in {result.total_months} months, saving ${result.total_interest:,.2f} in interest. Stay consistent with your ${result.monthly_payment:,.2f} monthly payments."
    
    async def _generate_ai_plan(
        self,
        debts: List[DebtResponse],
        debt_infos: List[DebtInfo],
        monthly_budget: float,
        strategy: RepaymentStrategy,
        extra_payment: float,
        start_date: date | None,
        user_context: Dict[str, Any]
    ) -> OptimizationResult:
        """Use AI to generate the complete repayment plan with reasoning."""
        
        if start_date is None:
            today = date.today()
            start_date = date(today.year, today.month, 1) + timedelta(days=32)
            start_date = date(start_date.year, start_date.month, 1)
        
        # Prepare debt summary for AI with IDs
        debt_summary = "\n".join([
            f"- ID: {d.id}, Name: {d.creditor_name}, Balance: ${d.balance:,.2f}, APR: {d.apr}%, Minimum Payment: ${d.minimum_payment:,.2f}"
            for d in debts if not d.is_paid_off
        ])
        
        # Create a mapping for reference
        debt_id_mapping = "\n".join([
            f"  {d.creditor_name} -> {d.id}"
            for d in debts if not d.is_paid_off
        ])
        
        total_debt = sum(d.balance for d in debts if not d.is_paid_off)
        total_minimum = sum(d.minimum_payment for d in debts if not d.is_paid_off)
        available_extra = monthly_budget + extra_payment - total_minimum
        
        # Build user financial context string
        financial_context = ""
        if user_context:
            if "monthly_income" in user_context and "monthly_expenses" in user_context:
                income = user_context["monthly_income"]
                expenses = user_context["monthly_expenses"]
                debt_to_income_ratio = (total_minimum / income * 100) if income > 0 else 0
                financial_context = f"""

**User's Complete Financial Picture:**
- Monthly Income: ${income:,.2f}
- Monthly Expenses: ${expenses:,.2f}
- Available for Debt: ${monthly_budget:,.2f}
- Expense Ratio: {(expenses/income*100):.1f}% of income
- Debt-to-Income Ratio: {debt_to_income_ratio:.1f}%
- Financial Flexibility: ${max(0, income - expenses - monthly_budget):,.2f}/month cushion
"""
        
        # Build AI prompt for plan generation
        num_debts = len([d for d in debts if not d.is_paid_off])
        
        prompt = f"""You are a financial planning AI. Generate a complete debt repayment plan using the {strategy.value} strategy.

**Debts to pay off ({num_debts} debt(s)):**
{debt_summary}

**CRITICAL - Debt ID Mapping (you MUST use these exact UUIDs in your payoff_order):**
{debt_id_mapping}
{financial_context}
**Financial Situation:**
- Total Debt: ${total_debt:,.2f}
- Monthly Budget: ${monthly_budget:,.2f}
- Extra Payment: ${extra_payment:,.2f}
- Total Available: ${monthly_budget + extra_payment:,.2f}
- Required Minimums: ${total_minimum:,.2f}
- Available for Extra Payments: ${max(0, available_extra):,.2f}
- Start Date: {start_date.strftime('%Y-%m-%d')}

**Strategy: {strategy.value.upper()}**
{'- Pay off debts with highest APR first to minimize interest' if strategy == RepaymentStrategy.AVALANCHE else '- Pay off smallest debts first for psychological wins'}

**MANDATORY REQUIREMENTS:**
1. Your payoff_order array MUST contain ALL {num_debts} debt(s)
2. EVERY debt_id in payoff_order MUST be one of the UUIDs from the mapping above
3. Calculate month-by-month payment schedule for ALL debts
4. Apply minimum payments to all debts first each month
5. Apply extra payment to the priority debt (based on strategy)
6. Track interest accrued each month (balance × APR / 12 / 100)
7. Continue until ALL debts are paid off
8. Provide a motivating explanation

Return a JSON object with the following structure:

**EXAMPLE OUTPUT (for reference - use this exact format):**
{{
  "total_months": 24,
  "total_interest": 1250.50,
  "total_paid": 10250.50,
  "monthly_payment": 500.00,
  "debt_free_date": "2026-01-15",
  "payoff_order": [
    {{
      "debt_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "debt_name": "Credit Card",
      "payoff_month": 12,
      "total_interest": 450.25
    }},
    {{
      "debt_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "debt_name": "Personal Loan",
      "payoff_month": 24,
      "total_interest": 800.25
    }}
  ],
  "ai_explanation": "Your avalanche strategy targets the highest interest debts first, saving you money over time. You'll be debt-free in 24 months by staying consistent with your payments. This approach minimizes total interest while building strong financial habits.",
  "key_insights": [
    "Prioritizing high-interest debt saves $500 compared to other strategies",
    "First debt payoff in 12 months will free up extra cash for remaining debts",
    "Consider automating payments to stay on track"
  ],
  "monthly_schedule": [
    {{
      "month": 1,
      "date": "2026-02-01",
      "total_payment": 500.00,
      "total_remaining": 9800.00,
      "payments": [
        {{
          "debt_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
          "debt_name": "Credit Card",
          "payment_amount": 300.00,
          "principal": 275.50,
          "interest": 24.50,
          "remaining_balance": 4724.50,
          "is_payoff_month": false
        }},
        {{
          "debt_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
          "debt_name": "Personal Loan",
          "payment_amount": 200.00,
          "principal": 183.33,
          "interest": 16.67,
          "remaining_balance": 5075.50,
          "is_payoff_month": false
        }}
      ]
    }},
    {{
      "month": 2,
      "date": "2026-03-01",
      "total_payment": 500.00,
      "total_remaining": 9350.00,
      "payments": [
        {{
          "debt_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
          "debt_name": "Credit Card",
          "payment_amount": 300.00,
          "principal": 276.75,
          "interest": 23.25,
          "remaining_balance": 4447.75,
          "is_payoff_month": false
        }},
        {{
          "debt_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
          "debt_name": "Personal Loan",
          "payment_amount": 200.00,
          "principal": 183.89,
          "interest": 16.11,
          "remaining_balance": 4891.61,
          "is_payoff_month": false
        }}
      ]
    }}
  ]
}}

**YOUR ACTUAL OUTPUT SCHEMA:**
{{
  "total_months": <number>,
  "total_interest": <number>,
  "total_paid": <number>,
  "monthly_payment": <number>,
  "debt_free_date": "<YYYY-MM-DD string>",
  "payoff_order": [ ... ],
  "ai_explanation": "<string>",
  "key_insights": [ ... ],
  "monthly_schedule": [ ... ]
}}

**CRITICAL RULES:**
1. ALL date fields MUST be strings in "YYYY-MM-DD" format
2. Use exact debt IDs from the mapping above
3. Calculate interest as: balance × (APR / 12 / 100)
4. Round all currency to 2 decimal places
5. Include ALL months until all debts are paid off"""
        
        # Retry loop for robust AI plan generation
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"AI plan generation attempt {attempt}/{self.max_retries}")
                
                response = await openai_client.chat_completion(
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a financial planning AI that generates precise debt repayment schedules. You understand compound interest, payment allocation strategies, and financial psychology. Always return valid JSON with accurate calculations. CRITICAL FORMATTING RULES: 1) All date fields MUST be strings in YYYY-MM-DD format (e.g., '2026-01-15'), NEVER date objects. 2) All numeric fields must be numbers, not strings. 3) Follow the provided example structure exactly. 4) MANDATORY: The payoff_order array MUST contain ALL {num_debts} debt(s) with their exact UUIDs from the debt ID mapping. DO NOT return an empty payoff_order array."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                # Log the raw AI response for debugging
                print(f"Raw AI response (first 500 chars): {response[:500]}")
                
                # Parse AI response
                ai_plan = self._parse_ai_plan_response(response, debt_infos, start_date)
                
                # Validate AI plan
                if ai_plan and self._validate_ai_plan(ai_plan, debt_infos):
                    print(f"AI plan generation succeeded on attempt {attempt}")
                    return ai_plan
                else:
                    print(f"AI plan validation failed on attempt {attempt}")
                    if ai_plan:
                        print(f"Failed plan details - payoff_order length: {len(ai_plan.payoff_order) if ai_plan.payoff_order else 0}")
                    if attempt < self.max_retries:
                        print(f"Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                        continue
            
            except Exception as e:
                print(f"AI plan generation error on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    continue
        
        # All retries exhausted, fallback to mathematical optimization
        print(f"AI plan generation failed after {self.max_retries} attempts, falling back to mathematical calculation")
        return self._fallback_to_math_calculation(
            debt_infos, monthly_budget, strategy, extra_payment, start_date
        )
    
    def _parse_ai_plan_response(
        self, response: str, debt_infos: List[DebtInfo], start_date: date
    ) -> OptimizationResult | None:
        """Parse AI-generated plan response into OptimizationResult."""
        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start < 0 or json_end <= json_start:
                print("No JSON found in AI response")
                return None
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Debug: Log parsed data structure
            print(f"Parsed AI data keys: {list(data.keys())}")
            print(f"Payoff order count: {len(data.get('payoff_order', []))}")
            
            # Validate that payoff_order exists and is not empty
            if not data.get("payoff_order"):
                print(f"WARNING: AI response has empty payoff_order. Will attempt reconstruction from monthly_schedule.")
                # Don't return None yet - let the reconstruction logic handle it
            
            # Parse debt free date with type validation
            debt_free_date_raw = data.get("debt_free_date")
            if not debt_free_date_raw:
                print("Missing debt_free_date in AI response")
                return None
            
            if isinstance(debt_free_date_raw, str):
                debt_free_date = date.fromisoformat(debt_free_date_raw)
            elif isinstance(debt_free_date_raw, date):
                debt_free_date = debt_free_date_raw
            else:
                print(f"Invalid debt_free_date type: {type(debt_free_date_raw)}, value: {debt_free_date_raw}")
                return None
            
            # Parse monthly schedule
            monthly_schedule = []
            for month_data in data.get("monthly_schedule", []):
                # Get the month number from month_data, not from individual payments
                month_num = month_data.get("month")
                if not isinstance(month_num, int) or month_num <= 0:
                    print(f"Invalid month number: {month_num}")
                    return None
                
                # Parse month date with type checking
                month_date_raw = month_data.get("date")
                if isinstance(month_date_raw, str):
                    month_date = date.fromisoformat(month_date_raw)
                elif isinstance(month_date_raw, date):
                    month_date = month_date_raw
                else:
                    print(f"Invalid month date type: {type(month_date_raw)}")
                    return None
                
                # Validate and parse payments with error handling
                payments = []
                for p in month_data.get("payments", []):
                    try:
                        # Validate numeric fields
                        payment_amount = p.get("payment_amount", 0)
                        principal = p.get("principal", 0)
                        interest = p.get("interest", 0)
                        remaining_balance = p.get("remaining_balance", 0)
                        
                        if not all(isinstance(v, (int, float)) for v in [payment_amount, principal, interest, remaining_balance]):
                            print(f"Invalid numeric values in payment for debt {p.get('debt_name')}")
                            continue
                        
                        payments.append(PaymentScheduleItem(
                            month=month_num,
                            date=month_date,
                            debt_id=p["debt_id"],
                            debt_name=p["debt_name"],
                            payment_amount=float(payment_amount),
                            principal=float(principal),
                            interest=float(interest),
                            remaining_balance=float(remaining_balance),
                            is_payoff_month=p.get("is_payoff_month", False)
                        ))
                    except Exception as e:
                        print(f"Error parsing payment item: {e}")
                        continue
                
                if not payments:
                    print(f"No valid payments found for month {month_num}")
                    return None
                
                # Validate total payment and remaining
                total_payment = month_data.get("total_payment", 0)
                total_remaining = month_data.get("total_remaining", 0)
                
                if not isinstance(total_payment, (int, float)) or total_payment < 0:
                    print(f"Invalid total_payment for month {month_num}: {total_payment}")
                    return None
                
                if not isinstance(total_remaining, (int, float)) or total_remaining < 0:
                    print(f"Invalid total_remaining for month {month_num}: {total_remaining}")
                    return None
                
                monthly_schedule.append(MonthlyBreakdown(
                    month=month_num,
                    date=month_date,
                    total_payment=float(total_payment),
                    payments=payments,
                    total_remaining=float(total_remaining)
                ))
            
            # Generate projections from schedule
            projections = []
            cumulative_interest = 0.0
            cumulative_principal = 0.0
            
            for breakdown in monthly_schedule:
                month_interest = sum(p.interest for p in breakdown.payments)
                month_principal = sum(p.principal for p in breakdown.payments)
                cumulative_interest += month_interest
                cumulative_principal += month_principal
                
                projections.append(PlanProjection(
                    month=breakdown.month,
                    date=breakdown.date,
                    total_remaining=breakdown.total_remaining,
                    cumulative_interest_paid=cumulative_interest,
                    cumulative_principal_paid=cumulative_principal
                ))
            
            # Parse payoff order
            payoff_order = []
            payoff_data_list = data.get("payoff_order", [])
            
            # If payoff_order is empty but we have a monthly_schedule, try to reconstruct it
            if not payoff_data_list and monthly_schedule:
                print("WARNING: payoff_order is empty, attempting to reconstruct from monthly_schedule")
                # Track which debts have been paid off
                debt_payoffs = {}
                for breakdown in monthly_schedule:
                    for payment in breakdown.payments:
                        if payment.is_payoff_month and payment.debt_id not in debt_payoffs:
                            debt_payoffs[payment.debt_id] = {
                                "debt_id": payment.debt_id,
                                "debt_name": payment.debt_name,
                                "payoff_month": breakdown.month,
                                "total_interest": 0.0  # Will calculate below
                            }
                
                # Calculate total interest for each debt
                for breakdown in monthly_schedule:
                    for payment in breakdown.payments:
                        if payment.debt_id in debt_payoffs:
                            debt_payoffs[payment.debt_id]["total_interest"] += payment.interest
                
                payoff_data_list = list(debt_payoffs.values())
                print(f"Reconstructed {len(payoff_data_list)} payoff entries from schedule")
            
            # Final check: if we still don't have all debts, this is a critical error
            if not payoff_data_list:
                print("CRITICAL ERROR: Unable to determine payoff order - both AI response and reconstruction failed")
                return None
            
            for payoff_data in payoff_data_list:
                # Find the payoff date from schedule
                payoff_month = payoff_data["payoff_month"]
                payoff_date = start_date
                if payoff_month > 0 and payoff_month <= len(monthly_schedule):
                    payoff_date = monthly_schedule[payoff_month - 1].date
                
                payoff_order.append(DebtPayoffInfo(
                    debt_id=payoff_data["debt_id"],
                    debt_name=payoff_data["debt_name"],
                    payoff_month=payoff_month,
                    payoff_date=payoff_date,
                    total_interest_paid=payoff_data.get("total_interest", 0.0),
                    total_paid=0.0  # Will be calculated later
                ))
            
            # Validate and extract numeric fields with type checking
            total_months = data.get("total_months")
            if not isinstance(total_months, (int, float)) or total_months <= 0:
                print(f"Invalid total_months: {total_months}")
                return None
            
            total_interest = data.get("total_interest")
            if not isinstance(total_interest, (int, float)) or total_interest < 0:
                print(f"Invalid total_interest: {total_interest}")
                return None
            
            total_paid = data.get("total_paid")
            if not isinstance(total_paid, (int, float)) or total_paid <= 0:
                print(f"Invalid total_paid: {total_paid}")
                return None
            
            monthly_payment = data.get("monthly_payment")
            if not isinstance(monthly_payment, (int, float)) or monthly_payment <= 0:
                print(f"Invalid monthly_payment: {monthly_payment}")
                return None
            
            # Create result
            result = OptimizationResult(
                debt_free_date=debt_free_date,
                total_months=int(total_months),
                total_interest=float(total_interest),
                total_paid=float(total_paid),
                monthly_payment=float(monthly_payment),
                monthly_schedule=monthly_schedule,
                projections=projections,
                payoff_order=payoff_order
            )
            
            # Add AI explanation
            result.ai_explanation = data.get("ai_explanation", "")
            if "key_insights" in data:
                result.ai_explanation += "\n\nKey Insights:\n" + "\n".join(
                    f"• {insight}" for insight in data["key_insights"]
                )
            
            return result
        
        except Exception as e:
            print(f"Failed to parse AI plan response: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def _validate_ai_plan(self, plan: OptimizationResult, debt_infos: List[DebtInfo]) -> bool:
        """Validate AI-generated plan for correctness."""
        try:
            # Check basic fields exist
            if not plan:
                print("Validation failed: plan is None")
                return False
                
            if plan.total_months <= 0:
                print(f"Validation failed: total_months={plan.total_months}")
                return False
                
            if plan.total_interest < 0:
                print(f"Validation failed: total_interest={plan.total_interest}")
                return False
            
            # Check that all debts are in payoff order
            debt_ids = {d.id for d in debt_infos}
            payoff_ids = {p.debt_id for p in plan.payoff_order}
            if debt_ids != payoff_ids:
                print(f"Validation failed: debt IDs mismatch. Expected: {debt_ids}, Got: {payoff_ids}")
                return False
            
            # Check that final balance is near zero
            if plan.monthly_schedule:
                final_remaining = plan.monthly_schedule[-1].total_remaining
                if final_remaining > 1.0:  # Allow small rounding error
                    print(f"Validation failed: final_remaining={final_remaining} (should be near 0)")
                    return False
            else:
                print("Validation failed: no monthly_schedule")
                return False
            
            print("AI plan validation passed!")
            return True
        
        except Exception as e:
            print(f"Validation error: {e}")
            import traceback
            print(traceback.format_exc())
            return False
    
    def _fallback_to_math_calculation(
        self,
        debt_infos: List[DebtInfo],
        monthly_budget: float,
        strategy: RepaymentStrategy,
        extra_payment: float,
        start_date: date
    ) -> OptimizationResult:
        """Fallback to mathematical optimization if AI fails."""
        result = OptimizationService.calculate_plan(
            debts=debt_infos,
            available_monthly=monthly_budget,
            strategy=strategy,
            extra_payment=extra_payment,
            start_date=start_date
        )
        
        # Add basic explanation
        result.ai_explanation = (
            f"Your {strategy.value} plan uses mathematical optimization to eliminate your debts "
            f"in {result.total_months} months with ${result.total_interest:,.2f} in total interest. "
            f"Stay consistent with your ${result.monthly_payment:,.2f} monthly payments."
        )
        
        return result


# Singleton instance
optimization_agent = OptimizationAgent()
