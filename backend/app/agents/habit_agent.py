"""
Habit Agent for milestone detection, celebrations, and habit reinforcement.

Monitors user progress, detects milestones, and generates celebrations
and motivational messages.
"""

from datetime import date, datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

from app.agents.base_agent import BaseAgent
from app.core.openai_client import openai_client
from app.models.payment import PaymentStats


class MilestoneType(str, Enum):
    """Types of milestones."""
    DEBT_PAID_OFF = "debt_paid_off"
    PERCENTAGE_MILESTONE = "percentage_milestone"
    CONSISTENCY_STREAK = "consistency_streak"
    NEGOTIATION_SUCCESS = "negotiation_success"
    SAVINGS_MILESTONE = "savings_milestone"
    FIRST_PAYMENT = "first_payment"
    MONTHLY_GOAL = "monthly_goal"


class BadgeType(str, Enum):
    """Types of achievement badges."""
    FIRST_VICTORY = "first_victory"
    DEBT_DESTROYER = "debt_destroyer"
    STREAK_STARTER = "streak_starter"
    WEEK_WARRIOR = "week_warrior"
    MONTH_MASTER = "month_master"
    QUARTER_CHAMPION = "quarter_champion"
    HALFWAY_HERO = "halfway_hero"
    ALMOST_THERE = "almost_there"
    DEBT_FREE = "debt_free"
    NEGOTIATOR = "negotiator"
    SAVER = "saver"


class Milestone(BaseModel):
    """A detected milestone achievement."""
    milestone_type: MilestoneType
    title: str
    description: str
    badge_name: Optional[BadgeType] = None
    achievement_value: Optional[float] = None
    related_debt_id: Optional[str] = None
    related_debt_name: Optional[str] = None
    celebration_message: str
    interest_saved: Optional[float] = None
    achieved_at: datetime = Field(default_factory=datetime.utcnow)


class MilestoneCheckResult(BaseModel):
    """Result of checking for milestones."""
    milestones: List[Milestone]
    has_new_milestones: bool
    celebration_priority: int = 0  # 0 = none, 1 = minor, 2 = major, 3 = epic


class StreakInfo(BaseModel):
    """Information about user's streak."""
    current_streak: int
    longest_streak: int
    is_at_risk: bool  # True if no payment in last 2 days
    days_until_next_milestone: int  # Days until next streak badge
    next_streak_badge: Optional[BadgeType] = None
    message: str


class HabitNudge(BaseModel):
    """A habit reinforcement nudge."""
    title: str
    message: str
    action_suggestion: Optional[str] = None
    urgency: int = 1  # 1-5, 5 being most urgent


class HabitAgent(BaseAgent):
    """
    Agent for detecting milestones and reinforcing positive habits.
    
    Monitors progress and generates celebrations, badges, and nudges
    to keep users motivated on their debt freedom journey.
    """
    
    STREAK_MILESTONES = {
        7: (BadgeType.WEEK_WARRIOR, "Week Warrior"),
        30: (BadgeType.MONTH_MASTER, "Month Master"),
        90: (BadgeType.QUARTER_CHAMPION, "Quarter Champion"),
    }
    
    PERCENTAGE_MILESTONES = [25, 50, 75, 90]
    
    def __init__(self):
        super().__init__(
            agent_name="HabitAgent",
            description="Detects milestones and generates celebrations for habit reinforcement"
        )
    
    async def check_milestones(
        self,
        user_id: str,
        total_debt_original: float,
        total_debt_current: float,
        total_paid: float,
        total_interest_saved: float,
        debts_paid_off: int,
        payment_stats: PaymentStats,
        recently_paid_debt_id: Optional[str] = None,
        recently_paid_debt_name: Optional[str] = None,
        existing_badges: Optional[List[str]] = None
    ) -> MilestoneCheckResult:
        """
        Check for any new milestones achieved.
        
        Args:
            user_id: User UUID
            total_debt_original: Original total debt amount
            total_debt_current: Current total debt amount
            total_paid: Total amount paid so far
            total_interest_saved: Total interest saved
            debts_paid_off: Number of debts fully paid off
            payment_stats: User's payment statistics
            recently_paid_debt_id: ID of debt just paid (if any)
            recently_paid_debt_name: Name of debt just paid (if any)
            existing_badges: List of badge names user already has
        
        Returns:
            MilestoneCheckResult with any new milestones
        """
        return await self.trace_execution(
            self._check_milestones,
            user_id=user_id,
            total_debt_original=total_debt_original,
            total_debt_current=total_debt_current,
            total_paid=total_paid,
            total_interest_saved=total_interest_saved,
            debts_paid_off=debts_paid_off,
            payment_stats=payment_stats,
            recently_paid_debt_id=recently_paid_debt_id,
            recently_paid_debt_name=recently_paid_debt_name,
            existing_badges=existing_badges or []
        )
    
    async def _check_milestones(
        self,
        user_id: str,
        total_debt_original: float,
        total_debt_current: float,
        total_paid: float,
        total_interest_saved: float,
        debts_paid_off: int,
        payment_stats: PaymentStats,
        recently_paid_debt_id: Optional[str],
        recently_paid_debt_name: Optional[str],
        existing_badges: List[str]
    ) -> MilestoneCheckResult:
        """Internal method to check milestones using AI."""
        milestones: List[Milestone] = []
        celebration_priority = 0
        
        # Build context for AI
        context = {
            "total_debt_original": total_debt_original,
            "total_debt_current": total_debt_current,
            "total_paid": total_paid,
            "total_interest_saved": total_interest_saved,
            "debts_paid_off": debts_paid_off,
            "total_payments": payment_stats.total_payments,
            "current_streak": payment_stats.current_streak_days,
            "longest_streak": payment_stats.longest_streak_days,
            "recently_paid_debt": recently_paid_debt_name,
            "existing_badges": existing_badges
        }
        
        # Detect numeric milestones first
        detected_milestones = self._detect_milestone_triggers(context)
        
        if detected_milestones:
            # Use AI to generate personalized celebrations
            try:
                ai_celebrations = await self._generate_ai_celebrations(context, detected_milestones)
                milestones = ai_celebrations
                celebration_priority = self._calculate_priority(detected_milestones)
            except Exception as e:
                print(f"AI celebration generation failed: {e}")
                # Fallback to rule-based celebrations
                milestones = self._generate_fallback_celebrations(context, detected_milestones)
                celebration_priority = self._calculate_priority(detected_milestones)
        
        return MilestoneCheckResult(
            milestones=milestones,
            has_new_milestones=len(milestones) > 0,
            celebration_priority=celebration_priority
        )
    
    def _detect_milestone_triggers(self, context: dict) -> List[dict]:
        """Detect which milestones have been achieved."""
        milestones = []
        
        # First payment
        if context["total_payments"] == 1 and BadgeType.FIRST_VICTORY.value not in context["existing_badges"]:
            milestones.append({
                "type": MilestoneType.FIRST_PAYMENT,
                "value": context["total_paid"],
                "badge": BadgeType.FIRST_VICTORY
            })
        
        # Debt paid off
        if context["recently_paid_debt"]:
            milestones.append({
                "type": MilestoneType.DEBT_PAID_OFF,
                "debt_name": context["recently_paid_debt"],
                "badge": BadgeType.DEBT_DESTROYER if BadgeType.DEBT_DESTROYER.value not in context["existing_badges"] else None
            })
        
        # Percentage milestones
        if context["total_debt_original"] > 0:
            progress_pct = ((context["total_debt_original"] - context["total_debt_current"]) / context["total_debt_original"]) * 100
            
            for pct in self.PERCENTAGE_MILESTONES:
                badge_key = f"pct_{pct}"
                if progress_pct >= pct and badge_key not in context["existing_badges"]:
                    badge = None
                    if pct == 50:
                        badge = BadgeType.HALFWAY_HERO
                    elif pct == 90:
                        badge = BadgeType.ALMOST_THERE
                    
                    milestones.append({
                        "type": MilestoneType.PERCENTAGE_MILESTONE,
                        "value": pct,
                        "badge": badge
                    })
        
        # Streak milestones
        for streak_days, (badge, badge_name) in self.STREAK_MILESTONES.items():
            streak_key = f"streak_{streak_days}"
            if context["current_streak"] >= streak_days and streak_key not in context["existing_badges"]:
                milestones.append({
                    "type": MilestoneType.CONSISTENCY_STREAK,
                    "value": streak_days,
                    "badge": badge if badge.value not in context["existing_badges"] else None
                })
        
        # Interest savings milestones
        for savings in [100, 500, 1000, 5000, 10000]:
            savings_key = f"saved_{savings}"
            if context["total_interest_saved"] >= savings and savings_key not in context["existing_badges"]:
                milestones.append({
                    "type": MilestoneType.SAVINGS_MILESTONE,
                    "value": savings,
                    "actual_saved": context["total_interest_saved"],
                    "badge": BadgeType.SAVER if savings >= 1000 and BadgeType.SAVER.value not in context["existing_badges"] else None
                })
        
        return milestones
    
    async def _generate_ai_celebrations(self, context: dict, milestones: List[dict]) -> List[Milestone]:
        """Use AI to generate personalized celebration messages."""
        prompt = f"""Generate personalized celebration messages for debt repayment milestones.

User Context:
- Total debt paid: ${context['total_paid']:,.2f}
- Total interest saved: ${context['total_interest_saved']:,.2f}
- Debts paid off: {context['debts_paid_off']}
- Current payment streak: {context['current_streak']} days
- Total payments: {context['total_payments']}

Achieved Milestones:
"""
        for m in milestones:
            prompt += f"- {m['type']}: "
            if m['type'] == MilestoneType.DEBT_PAID_OFF:
                prompt += f"Paid off {m['debt_name']}\n"
            elif m['type'] == MilestoneType.PERCENTAGE_MILESTONE:
                prompt += f"Reached {m['value']}% debt freedom\n"
            elif m['type'] == MilestoneType.CONSISTENCY_STREAK:
                prompt += f"{m['value']} day streak\n"
            elif m['type'] == MilestoneType.SAVINGS_MILESTONE:
                prompt += f"Saved ${m['value']:,.0f} in interest\n"
            elif m['type'] == MilestoneType.FIRST_PAYMENT:
                prompt += f"First payment made!\n"
        
        prompt += """
Generate celebration messages in JSON format. For each milestone, provide:
- title: Exciting, encouraging title (5-8 words)
- description: Brief explanation (1-2 sentences)
- celebration_message: Enthusiastic personalized message with emojis (2-3 sentences)

Be authentic, encouraging, and celebrate their progress genuinely!

Return ONLY valid JSON array, no other text.
Example: [{"title": "First Victory!", "description": "You made your first payment!", "celebration_message": "🎉 Amazing start! You've taken..."}]
"""
        
        response = await openai_client.chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": """You are an enthusiastic financial coach celebrating user achievements. 
Your role is to create genuine, personalized celebrations that make people feel proud and motivated.
Use emojis, be specific to their achievement, and make it feel special!"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        
        # Parse AI response
        import json
        
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(line for line in lines if not line.startswith("```"))
        
        ai_messages = json.loads(response)
        
        # Build milestone objects
        result = []
        for i, milestone_trigger in enumerate(milestones):
            if i < len(ai_messages):
                ai_msg = ai_messages[i]
                milestone = Milestone(
                    milestone_type=milestone_trigger["type"],
                    title=ai_msg["title"],
                    description=ai_msg["description"],
                    badge_name=milestone_trigger.get("badge"),
                    achievement_value=milestone_trigger.get("value"),
                    related_debt_name=milestone_trigger.get("debt_name"),
                    celebration_message=ai_msg["celebration_message"],
                    interest_saved=milestone_trigger.get("actual_saved")
                )
                result.append(milestone)
        
        return result
    
    def _generate_fallback_celebrations(self, context: dict, milestones: List[dict]) -> List[Milestone]:
        """Generate fallback celebrations using templates."""
        result = []
        
        for milestone_trigger in milestones:
            if milestone_trigger["type"] == MilestoneType.FIRST_PAYMENT:
                result.append(Milestone(
                    milestone_type=MilestoneType.FIRST_PAYMENT,
                    title="First Step to Freedom!",
                    description="You've made your first payment!",
                    badge_name=milestone_trigger.get("badge"),
                    achievement_value=milestone_trigger.get("value"),
                    celebration_message="🎉 Congratulations! You've taken the most important step!"
                ))
            
            elif milestone_trigger["type"] == MilestoneType.DEBT_PAID_OFF:
                debt_name = milestone_trigger.get("debt_name", "debt")
                result.append(Milestone(
                    milestone_type=MilestoneType.DEBT_PAID_OFF,
                    title=f"Debt Demolished: {debt_name}!",
                    description=f"You've completely paid off {debt_name}!",
                    badge_name=milestone_trigger.get("badge"),
                    related_debt_name=debt_name,
                    celebration_message=f"🏆 AMAZING! {debt_name} is history! You're unstoppable!"
                ))
            
            elif milestone_trigger["type"] == MilestoneType.PERCENTAGE_MILESTONE:
                pct = milestone_trigger["value"]
                result.append(Milestone(
                    milestone_type=MilestoneType.PERCENTAGE_MILESTONE,
                    title=f"{pct}% Debt Free!",
                    description=f"You've paid off {pct}% of your debt!",
                    badge_name=milestone_trigger.get("badge"),
                    achievement_value=pct,
                    celebration_message=self._get_percentage_celebration(pct)
                ))
            
            elif milestone_trigger["type"] == MilestoneType.CONSISTENCY_STREAK:
                days = milestone_trigger["value"]
                result.append(Milestone(
                    milestone_type=MilestoneType.CONSISTENCY_STREAK,
                    title=f"{days}-Day Streak!",
                    description=f"You've maintained a {days}-day payment streak!",
                    badge_name=milestone_trigger.get("badge"),
                    achievement_value=days,
                    celebration_message=f"🔥 {days} days of consistency! Unstoppable momentum!"
                ))
            
            elif milestone_trigger["type"] == MilestoneType.SAVINGS_MILESTONE:
                amount = milestone_trigger["value"]
                result.append(Milestone(
                    milestone_type=MilestoneType.SAVINGS_MILESTONE,
                    title=f"${amount:,.0f} Interest Saved!",
                    description=f"You've saved ${amount:,.0f} in interest!",
                    badge_name=milestone_trigger.get("badge"),
                    achievement_value=amount,
                    interest_saved=milestone_trigger.get("actual_saved"),
                    celebration_message=f"💰 ${amount:,.0f} saved! That's YOUR money staying in YOUR pocket!"
                ))
        
        return result
    
    def _calculate_priority(self, milestones: List[dict]) -> int:
        """Calculate celebration priority (0-3)."""
        if not milestones:
            return 0
        
        max_priority = 0
        for m in milestones:
            if m["type"] == MilestoneType.DEBT_PAID_OFF:
                max_priority = max(max_priority, 3)
            elif m["type"] == MilestoneType.PERCENTAGE_MILESTONE and m.get("value", 0) >= 75:
                max_priority = max(max_priority, 3)
            elif m["type"] == MilestoneType.PERCENTAGE_MILESTONE:
                max_priority = max(max_priority, 2)
            elif m["type"] == MilestoneType.CONSISTENCY_STREAK:
                max_priority = max(max_priority, 2)
            else:
                max_priority = max(max_priority, 1)
        
        return max_priority
    
    async def get_streak_info(
        self,
        payment_stats: PaymentStats,
        last_payment_date: Optional[date]
    ) -> StreakInfo:
        """
        Get information about user's current streak.
        
        Args:
            payment_stats: User's payment statistics
            last_payment_date: Date of last payment
        
        Returns:
            StreakInfo with streak details
        """
        current_streak = payment_stats.current_streak_days
        longest_streak = payment_stats.longest_streak_days
        
        # Check if streak is at risk
        today = date.today()
        is_at_risk = False
        if last_payment_date:
            days_since_payment = (today - last_payment_date).days
            is_at_risk = days_since_payment >= 2
        
        # Find next streak milestone
        next_milestone_days = None
        next_badge = None
        for streak_days, (badge, _) in sorted(self.STREAK_MILESTONES.items()):
            if streak_days > current_streak:
                next_milestone_days = streak_days
                next_badge = badge
                break
        
        days_until_next = (next_milestone_days - current_streak) if next_milestone_days else 0
        
        # Generate message
        if is_at_risk:
            message = "⚠️ Your streak is at risk! Make a payment today to keep it going!"
        elif current_streak == 0:
            message = "Start a streak today! Consistency is the key to success."
        elif current_streak < 7:
            message = f"🔥 {current_streak} day streak! Keep going to unlock Week Warrior badge!"
        elif next_milestone_days:
            message = f"🔥 {current_streak} day streak! Only {days_until_next} more days to {next_badge.value if next_badge else 'next milestone'}!"
        else:
            message = f"🏆 {current_streak} day streak! You're a consistency champion!"
        
        return StreakInfo(
            current_streak=current_streak,
            longest_streak=longest_streak,
            is_at_risk=is_at_risk,
            days_until_next_milestone=days_until_next,
            next_streak_badge=next_badge,
            message=message
        )
    
    async def generate_nudge(
        self,
        days_since_last_payment: int,
        current_streak: int,
        has_overdue_payments: bool,
        progress_percentage: float
    ) -> Optional[HabitNudge]:
        """
        Generate a habit reinforcement nudge if needed.
        
        Args:
            days_since_last_payment: Days since last payment
            current_streak: Current streak count
            has_overdue_payments: Whether there are overdue payments
            progress_percentage: Overall progress percentage
        
        Returns:
            HabitNudge if one should be shown, None otherwise
        """
        # Overdue payments - highest priority
        if has_overdue_payments:
            return HabitNudge(
                title="Payment Due",
                message="You have overdue payments. Getting back on track today will help you avoid extra interest!",
                action_suggestion="Make a payment now",
                urgency=5
            )
        
        # Streak at risk
        if current_streak > 0 and days_since_last_payment >= 2:
            return HabitNudge(
                title="Protect Your Streak!",
                message=f"Your {current_streak}-day streak is at risk! Make any payment to keep it alive.",
                action_suggestion="Log a payment",
                urgency=4
            )
        
        # No activity for a while
        if days_since_last_payment >= 7:
            return HabitNudge(
                title="We Miss You!",
                message="It's been a week since your last payment. Every payment, no matter how small, brings you closer to freedom!",
                action_suggestion="Check your progress",
                urgency=3
            )
        
        # Encouragement at milestones
        if progress_percentage >= 45 and progress_percentage < 50:
            return HabitNudge(
                title="Almost Halfway!",
                message=f"You're at {progress_percentage:.0f}%! Just a bit more to reach the halfway point!",
                action_suggestion="View your plan",
                urgency=1
            )
        
        return None
    
    def _get_percentage_celebration(self, percentage: int) -> str:
        """Get celebration message for percentage milestone."""
        messages = {
            25: "🌟 A quarter of the way there! You're building amazing momentum!",
            50: "🎊 HALFWAY THERE! You've conquered half your debt! The finish line is in sight!",
            75: "🚀 75% debt-free! You're in the home stretch now! Victory is near!",
            90: "⭐ 90% DONE! You're SO close to total freedom! The end is in sight!"
        }
        return messages.get(percentage, f"🎉 {percentage}% complete! Keep crushing it!")


# Singleton instance
habit_agent = HabitAgent()
