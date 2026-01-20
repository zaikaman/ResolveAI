"""
Optimization Agent - AI-powered debt repayment plan optimization.

Uses GPT to analyze user's financial situation and recommend the best strategy,
then executes mathematical optimization for precise payment schedules.
"""

from typing import List, Optional, Dict, Any
from datetime import date
import json

from app.agents.base_agent import BaseAgent
from app.services.optimization_service import OptimizationService, OptimizationResult, DebtInfo
from app.models.debt import DebtResponse
from app.models.plan import RepaymentStrategy
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
    
    def __init__(self):
        super().__init__(
            agent_name="OptimizationAgent",
            description="AI-powered debt repayment plan creator with mathematical optimization"
        )
    
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
        """Internal optimization logic with AI analysis."""
        
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
        
        # Call optimization service
        result = OptimizationService.calculate_plan(
            debts=debt_infos,
            available_monthly=monthly_budget,
            strategy=repayment_strategy,
            extra_payment=extra_payment,
            start_date=start_date
        )
        
        # Add strategy name and AI reasoning to result
        result.strategy = strategy.lower()
        
        # Generate AI explanation of the plan
        ai_explanation = await self._generate_plan_explanation(
            debts=debts,
            result=result,
            strategy=strategy,
            user_context=user_context
        )
        result.ai_explanation = ai_explanation
        
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
                ],
            )
            
            recommendation = self._parse_strategy_response(response)
            return recommendation
        
        except Exception as e:
            self.logger.error(f"AI strategy recommendation failed: {e}")
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
- Personal financial goals and psychological preferences"""
        
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
            self.logger.error(f"Failed to parse strategy response: {e}")
            return {"strategy": "avalanche", "reasoning": "Default strategy"}
    
    async def _generate_plan_explanation(
        self,
        debts: List[DebtResponse],
        result: OptimizationResult,
        strategy: str,
        user_context: Dict[str, Any]
    ) -> str:
        """Generate AI explanation of the repayment plan."""
        
        prompt = f"""Explain this debt repayment plan in a motivating, clear way:

**Strategy:** {strategy.upper()}
**Timeline:** {result.total_months} months to debt freedom
**Total Interest:** ${result.total_interest:,.2f}
**Monthly Payment:** ${result.monthly_payment:,.2f}
**Total Paid:** ${result.total_paid:,.2f}

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


# Singleton instance
optimization_agent = OptimizationAgent()
