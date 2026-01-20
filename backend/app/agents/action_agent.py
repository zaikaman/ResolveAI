"""
Action Agent for generating daily recommended actions.

Generates personalized daily actions based on the user's repayment plan,
payment schedule, and current progress.
"""

from datetime import date, datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

from app.agents.base_agent import BaseAgent
from app.core.openai_client import openai_client
from app.models.plan import PlanResponse, MonthlyBreakdown
from app.models.debt import DebtResponse


class ActionType(str, Enum):
    """Types of recommended actions."""
    PAYMENT = "payment"
    REVIEW = "review"
    REST = "rest"
    MILESTONE = "milestone"
    NUDGE = "nudge"


class ActionPriority(int, Enum):
    """Priority levels for actions."""
    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    OPTIONAL = 5


class DailyAction(BaseModel):
    """A single recommended action."""
    action_type: ActionType
    priority: ActionPriority
    title: str
    description: str
    suggested_amount: Optional[float] = None
    debt_id: Optional[str] = None
    debt_name: Optional[str] = None
    due_date: Optional[date] = None
    is_overdue: bool = False
    motivational_message: Optional[str] = None


class DailyActionsResponse(BaseModel):
    """Response containing daily actions."""
    actions: List[DailyAction]
    date: date
    summary: str
    progress_message: Optional[str] = None
    streak_message: Optional[str] = None


class ActionAgent(BaseAgent):
    """
    Agent for generating personalized daily actions.
    
    Analyzes the user's repayment plan, debts, and payment history
    to recommend prioritized daily actions.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="ActionAgent",
            description="Generates daily recommended actions for debt repayment"
        )
    
    async def generate_daily_actions(
        self,
        plan: Optional[PlanResponse],
        debts: List[DebtResponse],
        current_streak: int = 0,
        last_payment_date: Optional[date] = None,
        payments_this_month: int = 0
    ) -> DailyActionsResponse:
        """
        Generate daily actions based on user's plan and debts.
        
        Args:
            plan: Active repayment plan (optional)
            debts: List of active debts
            current_streak: Current payment streak
            last_payment_date: Date of last payment
            payments_this_month: Number of payments made this month
        
        Returns:
            DailyActionsResponse with prioritized actions
        """
        return await self.trace_execution(
            self._generate_actions,
            plan=plan,
            debts=debts,
            current_streak=current_streak,
            last_payment_date=last_payment_date,
            payments_this_month=payments_this_month
        )
    
    async def _generate_actions(
        self,
        plan: Optional[PlanResponse],
        debts: List[DebtResponse],
        current_streak: int,
        last_payment_date: Optional[date],
        payments_this_month: int
    ) -> DailyActionsResponse:
        """Internal method to generate actions using AI."""
        today = date.today()
        
        # Build context for AI
        context = self._build_context(plan, debts, current_streak, last_payment_date, payments_this_month, today)
        
        # Call OpenAI to generate intelligent actions
        prompt = self._build_prompt(context)
        
        try:
            response = await openai_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert financial coach specializing in debt repayment. 
Your role is to generate personalized, actionable daily recommendations for users working to become debt-free.
Focus on:
1. Payment reminders based on due dates and plan
2. Motivational encouragement
3. Progress reviews
4. Practical, specific actions
Be empathetic, encouraging, and realistic."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )
            
            # Parse AI response and create structured actions
            actions = self._parse_ai_response(response, debts, plan, today)
            
        except Exception as e:
            print(f"AI generation failed, using fallback: {e}")
            # Fallback to rule-based logic if AI fails
            actions = self._generate_fallback_actions(plan, debts, today)
        
        # Generate summary and messages
        summary = self._generate_summary(actions, plan, today)
        
        # Streak message
        streak_message = None
        if current_streak > 0:
            streak_message = f"🔥 {current_streak} day streak! Keep it going!"
            if current_streak >= 7:
                streak_message = f"🔥 Amazing! {current_streak} day streak! You're unstoppable!"
            elif current_streak >= 30:
                streak_message = f"🏆 Incredible! {current_streak} day streak! You're a debt-crushing machine!"
        
        # Progress message
        progress_message = None
        if plan:
            progress_pct = ((plan.total_months - plan.months_remaining) / max(plan.total_months, 1)) * 100
            if progress_pct > 0:
                progress_message = f"You're {progress_pct:.0f}% of the way to debt freedom!"
        
        return DailyActionsResponse(
            actions=actions[:5],  # Limit to top 5 actions
            date=today,
            summary=summary,
            progress_message=progress_message,
            streak_message=streak_message
        )
    
    def _build_context(
        self,
        plan: Optional[PlanResponse],
        debts: List[DebtResponse],
        current_streak: int,
        last_payment_date: Optional[date],
        payments_this_month: int,
        today: date
    ) -> dict:
        """Build context dictionary for AI."""
        context = {
            "today": today.isoformat(),
            "current_streak": current_streak,
            "last_payment_date": last_payment_date.isoformat() if last_payment_date else None,
            "payments_this_month": payments_this_month,
            "has_plan": plan is not None,
            "debts": []
        }
        
        if plan:
            context["plan"] = {
                "strategy": plan.strategy,
                "monthly_payment": plan.monthly_payment,
                "months_remaining": plan.months_remaining,
                "debt_free_date": plan.debt_free_date.isoformat()
            }
        
        for debt in debts:
            context["debts"].append({
                "id": str(debt.id),
                "name": debt.creditor_name,
                "balance": debt.balance,
                "apr": debt.apr,
                "minimum_payment": debt.minimum_payment,
                "due_date": debt.due_date,
                "is_paid_off": debt.is_paid_off
            })
        
        return context
    
    def _build_prompt(self, context: dict) -> str:
        """Build AI prompt from context."""
        prompt = f"""Today is {context['today']}.

User's Debt Situation:
"""
        if not context['debts']:
            prompt += "- No debts added yet\n"
        else:
            prompt += f"- Total debts: {len(context['debts'])}\n"
            for debt in context['debts']:
                prompt += f"  * {debt['name']}: ${debt['balance']:,.2f} balance, ${debt['minimum_payment']:.2f} minimum, {debt['apr']:.1f}% APR"
                if debt['due_date']:
                    prompt += f", due day {debt['due_date']}"
                prompt += "\n"
        
        if context['has_plan']:
            plan = context['plan']
            prompt += f"\nActive Plan: {plan['strategy']} strategy, ${plan['monthly_payment']:.2f}/month, {plan['months_remaining']} months until freedom\n"
        else:
            prompt += "\nNo active repayment plan\n"
        
        prompt += f"\nPayment Activity:\n"
        prompt += f"- Current streak: {context['current_streak']} days\n"
        prompt += f"- Payments this month: {context['payments_this_month']}\n"
        if context['last_payment_date']:
            prompt += f"- Last payment: {context['last_payment_date']}\n"
        
        prompt += """\n
Generate 3-5 prioritized daily actions in JSON format. Each action should have:
- action_type: "payment", "review", "rest", "milestone", or "nudge"
- priority: 1 (urgent) to 5 (optional)
- title: Short action title
- description: Detailed description (1-2 sentences)
- suggested_amount: (optional) dollar amount for payments
- debt_id: (optional) ID of related debt
- debt_name: (optional) name of related debt
- is_overdue: (optional) boolean if payment is overdue
- motivational_message: Encouraging message

Return ONLY valid JSON array of actions, no other text.
Example: [{"action_type": "payment", "priority": 1, "title": "Pay Credit Card", "description": "Make your monthly payment", "suggested_amount": 150.00, "debt_id": "...", "debt_name": "Chase Card", "motivational_message": "You got this! 💪"}]
"""
        return prompt
    
    def _parse_ai_response(
        self,
        response: str,
        debts: List[DebtResponse],
        plan: Optional[PlanResponse],
        today: date
    ) -> List[DailyAction]:
        """Parse AI response into structured actions."""
        import json
        
        actions = []
        
        try:
            # Try to extract JSON from response
            response = response.strip()
            if response.startswith("```"):
                # Remove markdown code blocks
                lines = response.split("\n")
                response = "\n".join(line for line in lines if not line.startswith("```"))
            
            ai_actions = json.loads(response)
            
            for action_data in ai_actions:
                # Map debt_id to actual debt if present
                debt_id = action_data.get("debt_id")
                due_date = None
                
                if debt_id:
                    debt = next((d for d in debts if str(d.id) == debt_id), None)
                    if debt and debt.due_date:
                        # Calculate due date for this month
                        due_date = today.replace(day=min(debt.due_date, 28))
                
                action = DailyAction(
                    action_type=ActionType(action_data.get("action_type", "review")),
                    priority=ActionPriority(action_data.get("priority", 3)),
                    title=action_data["title"],
                    description=action_data["description"],
                    suggested_amount=action_data.get("suggested_amount"),
                    debt_id=debt_id,
                    debt_name=action_data.get("debt_name"),
                    due_date=due_date,
                    is_overdue=action_data.get("is_overdue", False),
                    motivational_message=action_data.get("motivational_message")
                )
                actions.append(action)
            
            # Sort by priority
            actions.sort(key=lambda a: a.priority.value)
            
        except Exception as e:
            print(f"Failed to parse AI response: {e}")
            # Return empty list, fallback will handle
            return []
        
        return actions
    
    def _generate_fallback_actions(
        self,
        plan: Optional[PlanResponse],
        debts: List[DebtResponse],
        today: date
    ) -> List[DailyAction]:
        """Generate fallback actions using rule-based logic."""
        actions: List[DailyAction] = []
    def _generate_fallback_actions(
        self,
        plan: Optional[PlanResponse],
        debts: List[DebtResponse],
        today: date
    ) -> List[DailyAction]:
        """Generate fallback actions using rule-based logic."""
        actions: List[DailyAction] = []
        
        # If no plan, suggest creating one
        if not plan:
            if debts:
                actions.append(DailyAction(
                    action_type=ActionType.REVIEW,
                    priority=ActionPriority.URGENT,
                    title="Create Your Repayment Plan",
                    description="You have debts but no active plan. Create a personalized repayment strategy.",
                    motivational_message="Every journey begins with a single step! 🎯"
                ))
            else:
                actions.append(DailyAction(
                    action_type=ActionType.REVIEW,
                    priority=ActionPriority.HIGH,
                    title="Add Your Debts",
                    description="Start by adding your debts to get started.",
                    motivational_message="Knowledge is power! 💪"
                ))
            return actions
        
        # Check for due payments
        for debt in debts:
            if debt.is_paid_off:
                continue
                
            if debt.due_date:
                due_date = today.replace(day=min(debt.due_date, 28))
                days_until_due = (due_date - today).days
                
                if -3 <= days_until_due <= 3:  # Within 3 days of due date
                    priority = ActionPriority.URGENT if days_until_due <= 0 else ActionPriority.HIGH
                    actions.append(DailyAction(
                        action_type=ActionType.PAYMENT,
                        priority=priority,
                        title=f"Pay {debt.creditor_name}",
                        description=f"Make payment of ${debt.minimum_payment:.2f}",
                        suggested_amount=debt.minimum_payment,
                        debt_id=str(debt.id),
                        debt_name=debt.creditor_name,
                        due_date=due_date,
                        is_overdue=days_until_due < 0,
                        motivational_message="Every payment brings you closer! 🌟"
                    ))
        
        # If no urgent actions, add review
        if not actions:
            actions.append(DailyAction(
                action_type=ActionType.REVIEW,
                priority=ActionPriority.MEDIUM,
                title="Review Your Progress",
                description="Check your debt freedom progress!",
                motivational_message="You're doing great! 🎉"
            ))
        
        return actions[:5]
    
    def _get_current_month_payments(
        self,
        plan: PlanResponse,
        today: date
    ) -> List[dict]:
        """Extract payments scheduled for the current month from plan."""
        current_month = today.month
        current_year = today.year
        
        payments = []
        for month_breakdown in plan.monthly_schedule:
            breakdown_date = datetime.fromisoformat(month_breakdown.date).date() if isinstance(month_breakdown.date, str) else month_breakdown.date
            
            if breakdown_date.month == current_month and breakdown_date.year == current_year:
                for payment in month_breakdown.payments:
                    payments.append({
                        "debt_id": payment.debt_id,
                        "debt_name": payment.debt_name,
                        "payment_amount": payment.payment_amount,
                        "remaining_balance": payment.remaining_balance,
                        "is_payoff_month": payment.is_payoff_month
                    })
                break
        
        return payments
    
    def _get_payment_motivation(self, remaining_balance: float) -> str:
        """Generate motivational message based on remaining balance."""
        if remaining_balance < 100:
            return "Almost there! Just a little more and this debt is history! 🎉"
        elif remaining_balance < 500:
            return "You can see the finish line! Keep pushing! 💪"
        elif remaining_balance < 1000:
            return "Great progress! Every payment brings you closer to freedom! 🌟"
        else:
            return "You've got this! Stay focused on your goal! 🎯"
    
    def _generate_summary(
        self,
        actions: List[DailyAction],
        plan: PlanResponse,
        today: date
    ) -> str:
        """Generate a summary message for the day."""
        payment_actions = [a for a in actions if a.action_type == ActionType.PAYMENT]
        
        if not payment_actions:
            return "No payments scheduled today. Take a moment to review your progress!"
        
        total_to_pay = sum(a.suggested_amount or 0 for a in payment_actions)
        num_payments = len(payment_actions)
        
        if num_payments == 1:
            return f"You have 1 payment of ${total_to_pay:.2f} to make today."
        else:
            return f"You have {num_payments} payments totaling ${total_to_pay:.2f} today."


# Singleton instance
action_agent = ActionAgent()
