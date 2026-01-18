# Agent Contracts: ResolveAI Multi-Agent System

**Feature**: ResolveAI Debt Freedom Coach  
**Created**: 2026-01-18  
**Framework**: Custom agent orchestration (LangChain patterns)  
**LLM**: GPT-5-Nano (OpenAI API)  
**Tracing**: Opik (Comet)

## Overview

ResolveAI uses a multi-agent system with specialized agents for different aspects of debt coaching. Each agent has a specific responsibility, defined inputs/outputs, and is wrapped with Opik tracing for observability. The orchestrator coordinates agents using a ReAct-style pattern (Reason → Act → Observe).

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                             │
│  (ReAct Loop: Thought → Action → Observation → Repeat)     │
└────────┬────────┬────────┬────────┬────────┬───────────────┘
         │        │        │        │        │
    ┌────▼───┐ ┌─▼─────┐ ┌▼──────┐ ┌▼─────┐ ┌▼──────────┐
    │Assess  │ │Optimize│ │Action │ │Habit │ │Negotiation│
    │Agent   │ │Agent   │ │Agent  │ │Agent │ │Agent      │
    └────────┘ └────────┘ └───────┘ └──────┘ └───────────┘
         │        │          │         │         │
         └────────┴──────────┴─────────┴─────────┘
                           │
                      ┌────▼────┐
                      │  OPIK   │
                      │ Tracing │
                      └─────────┘
```

## Base Agent Interface

**BaseAgent Class** (all agents inherit):

```python
# app/agents/base_agent.py
from typing import Any, Dict
from opik import trace
import logging

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
    
    @trace(name="agent_execute")
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent's main logic. Override in subclasses.
        
        Args:
            input_data: Agent-specific input dictionary
            
        Returns:
            Agent-specific output dictionary
            
        Raises:
            AgentError: If execution fails
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input before execution"""
        raise NotImplementedError("Subclasses must implement validate_input()")
    
    def _log_trace(self, stage: str, data: Any) -> None:
        """Log to Opik with structured metadata"""
        opik.log(
            agent=self.name,
            stage=stage,
            data=data,
            timestamp=datetime.utcnow()
        )
```

---

## 1. Assessment Agent

**Responsibility**: Analyze user's debt situation, detect unsustainable scenarios, calculate available payment capacity, recommend repayment strategy.

**Input Contract**:
```python
class AssessmentInput(BaseModel):
    debts: List[Debt]  # List of user's debts (decrypted)
    monthly_income: Decimal
    monthly_expenses: Decimal
    user_preferences: Optional[Dict[str, Any]] = None
```

**Output Contract**:
```python
class AssessmentOutput(BaseModel):
    is_sustainable: bool  # Can user realistically pay off debts?
    unsustainable_reason: Optional[str] = None  # If False, why?
    available_income: Decimal  # Income - expenses - minimum payments
    total_minimum_payments: Decimal
    recommended_strategy: Literal["avalanche", "snowball"]
    strategy_rationale: str
    warnings: List[str] = []  # e.g., "Income fluctuates, consider buffer"
    confidence_score: float  # 0.0-1.0 (Opik quality metric)
```

**Logic**:
1. Calculate total minimum payments across all debts
2. Check if `monthly_income - monthly_expenses >= total_minimum_payments`
   - If NO → `is_sustainable = False`, provide guidance (hardship programs, credit counseling)
   - If YES → Calculate `available_income = income - expenses - minimums`
3. Recommend strategy:
   - **Avalanche** if user is analytical/focused on math (maximize interest savings)
   - **Snowball** if user needs quick wins (psychological boost from small payoffs)
4. Detect warnings:
   - Income < 2x minimum payments → "Very tight budget, consider income increase"
   - Irregular income → "Set aside 1-month buffer for variable income"
   - High-interest debt >25% → "Prioritize negotiation to reduce rates"

**Opik Tracing**:
- Input: Debts count, total balance, income, expenses
- Output: Sustainability verdict, recommended strategy, confidence
- Metrics: `assessment_confidence`, `unsustainable_rate` (% of users flagged)
- LLM-as-Judge: Validate strategy recommendation makes sense given user profile

**Example**:
```python
# app/agents/assessment_agent.py
class AssessmentAgent(BaseAgent):
    @trace(name="assess_debt_situation")
    async def execute(self, input_data: AssessmentInput) -> AssessmentOutput:
        # 1. Calculate minimums
        total_minimums = sum(debt.minimum_payment for debt in input_data.debts)
        
        # 2. Check sustainability
        available = input_data.monthly_income - input_data.monthly_expenses
        is_sustainable = available >= total_minimums
        
        if not is_sustainable:
            return AssessmentOutput(
                is_sustainable=False,
                unsustainable_reason=f"Income insufficient. Need ${total_minimums - available:.2f} more per month.",
                ...
            )
        
        # 3. Recommend strategy (call GPT-5-Nano for personalization)
        strategy = await self._recommend_strategy(input_data.debts, input_data.user_preferences)
        
        # 4. Opik log
        opik.log_metric("assessment_confidence", 0.95)
        
        return AssessmentOutput(
            is_sustainable=True,
            available_income=available - total_minimums,
            recommended_strategy=strategy,
            ...
        )
```

---

## 2. Optimization Agent

**Responsibility**: Calculate optimal debt repayment schedule using mathematical optimization (PuLP), minimize total interest or maximize psychological wins.

**Input Contract**:
```python
class OptimizationInput(BaseModel):
    debts: List[Debt]
    available_monthly_payment: Decimal  # From AssessmentAgent
    strategy: Literal["avalanche", "snowball"]
    constraints: Optional[Dict[str, Any]] = None  # e.g., target_months, extra_payment
```

**Output Contract**:
```python
class OptimizationOutput(BaseModel):
    payment_schedule: List[MonthlyPayment]  # Month-by-month allocation
    target_debt_free_date: date
    total_interest_paid: Decimal
    total_months: int
    debt_payoff_order: List[str]  # List of debt IDs in payoff order
    optimization_metadata: Dict[str, Any]  # PuLP solver stats, algorithm details
    comparison: Dict[str, StrategyComparison]  # Avalanche vs Snowball comparison
```

**MonthlyPayment Schema**:
```python
class MonthlyPayment(BaseModel):
    month: int
    date: date
    payments: List[DebtPayment]  # Per-debt allocations
    total_paid: Decimal
    remaining_total_debt: Decimal
    
class DebtPayment(BaseModel):
    debt_id: str
    creditor_name: str
    amount: Decimal
    is_minimum: bool  # True if only paying minimum
    new_balance: Decimal
```

**Logic**:
1. Set up PuLP linear programming problem:
   - **Objective (Avalanche)**: Minimize total interest paid
   - **Objective (Snowball)**: Maximize number of debts paid off early (secondary: minimize interest)
   - **Constraints**: 
     - Pay at least minimum on each debt each month
     - Total monthly payment ≤ available_monthly_payment
     - Balance >= 0 (cannot overpay)
2. Solve optimization problem
3. Generate month-by-month schedule
4. Calculate comparison (both strategies) for user education

**Opik Tracing**:
- Input: Debts count, available payment, strategy
- Output: Total interest saved, months to freedom, solver time
- Metrics: `optimization_time_ms`, `interest_saved_vs_minimum`, `strategy_difference_months` (avalanche vs snowball)
- Custom Dashboard: "Optimization Performance" (avg solver time, interest savings distribution)

**Example**:
```python
# app/agents/optimization_agent.py
from pulp import LpProblem, LpMinimize, LpVariable, lpSum

class OptimizationAgent(BaseAgent):
    @trace(name="optimize_repayment_plan")
    async def execute(self, input_data: OptimizationInput) -> OptimizationOutput:
        start_time = time.time()
        
        # 1. Setup PuLP problem
        problem = LpProblem("DebtRepayment", LpMinimize)
        
        # 2. Variables: payments[debt_id][month]
        payments = {
            debt.id: {
                month: LpVariable(f"pay_{debt.id}_{month}", lowBound=debt.minimum_payment)
                for month in range(1, 61)  # Max 5 years
            }
            for debt in input_data.debts
        }
        
        # 3. Objective: Minimize total interest
        problem += lpSum([...interest calculations...])
        
        # 4. Constraints
        for month in range(1, 61):
            problem += lpSum([payments[d.id][month] for d in debts]) <= available_payment
        
        # 5. Solve
        problem.solve()
        
        # 6. Extract solution
        schedule = self._build_schedule(payments, input_data.debts)
        
        # 7. Opik metrics
        elapsed = (time.time() - start_time) * 1000
        opik.log_metric("optimization_time_ms", elapsed)
        opik.log_metric("interest_saved", ...)
        
        return OptimizationOutput(payment_schedule=schedule, ...)
```

---

## 3. Action Agent

**Responsibility**: Generate daily/weekly actionable recommendations, personalize language, create reminders.

**Input Contract**:
```python
class ActionInput(BaseModel):
    plan: RepaymentPlan  # From OptimizationAgent
    current_date: date
    user_profile: UserProfile  # Name, preferences, language
    recent_activity: Optional[List[Payment]] = None  # Last 7 days
```

**Output Contract**:
```python
class ActionOutput(BaseModel):
    daily_actions: List[Action]  # Next 7 days
    weekly_summary: str  # "This week: Pay $600 total, focus on VCB card"
    motivational_message: str  # Personalized encouragement
    upcoming_milestones: List[Milestone]  # Within next 30 days
```

**Action Schema**:
```python
class Action(BaseModel):
    action_date: date
    action_type: Literal["payment", "review", "rest", "milestone", "nudge"]
    description: str  # Vietnamese or English based on user preference
    priority: int  # 1-5 (1 = highest)
    related_debt_id: Optional[str] = None
    suggested_amount: Optional[Decimal] = None
```

**Logic**:
1. Extract upcoming payments from plan schedule for next 7 days
2. For each day:
   - If payment due → "Pay $X to [Creditor]"
   - If no payment → "Rest day - you're on track!" or "Review your progress"
   - If milestone approaching → "3 days until you're 25% debt-free!"
3. Personalize language using GPT-5-Nano:
   - Empathetic tone for Vietnamese users ("Bạn đang làm rất tốt!")
   - Adjust formality based on user age/profile
4. Generate motivational message:
   - Reference recent progress ("You've paid $500 this week!")
   - Highlight future wins ("2 more months until first debt paid off")

**Opik Tracing**:
- Input: Plan ID, current date, user language
- Output: Actions count, personalization quality score
- LLM-as-Judge: Evaluate if motivational message is empathetic and culturally appropriate
- Metrics: `action_engagement_rate` (% of actions user completes)

**Example**:
```python
# app/agents/action_agent.py
class ActionAgent(BaseAgent):
    @trace(name="generate_actions")
    async def execute(self, input_data: ActionInput) -> ActionOutput:
        actions = []
        
        # 1. Next 7 days from plan
        for day in range(7):
            target_date = input_data.current_date + timedelta(days=day)
            payments_today = self._extract_payments_for_date(input_data.plan, target_date)
            
            if payments_today:
                for payment in payments_today:
                    actions.append(Action(
                        action_date=target_date,
                        action_type="payment",
                        description=f"Pay ${payment.amount:.2f} to {payment.creditor}",
                        priority=1,
                        related_debt_id=payment.debt_id,
                        suggested_amount=payment.amount
                    ))
            else:
                actions.append(Action(
                    action_date=target_date,
                    action_type="rest",
                    description="Rest day - you're on track!",
                    priority=3
                ))
        
        # 2. Personalize with GPT-5-Nano
        motivational_msg = await self._generate_motivation(input_data.user_profile, input_data.recent_activity)
        
        # 3. Opik log
        opik.log_llm_call(
            prompt=f"Generate motivational message for {user_profile.full_name}",
            response=motivational_msg,
            model="gpt-5-nano"
        )
        
        return ActionOutput(daily_actions=actions, motivational_message=motivational_msg, ...)
```

---

## 4. Habit Agent

**Responsibility**: Detect milestones, trigger celebrations, suggest nudges to reinforce positive behaviors.

**Input Contract**:
```python
class HabitInput(BaseModel):
    user_id: str
    recent_payment: Optional[Payment] = None  # Just logged payment
    current_debts: List[Debt]
    payment_history: List[Payment]  # Last 90 days
    plan: RepaymentPlan
```

**Output Contract**:
```python
class HabitOutput(BaseModel):
    milestone_triggered: Optional[Milestone] = None
    celebration_content: Optional[CelebrationContent] = None
    nudges: List[Nudge] = []
    habit_score: float  # 0.0-1.0 (consistency metric)
```

**Milestone Schema**:
```python
class Milestone(BaseModel):
    milestone_type: Literal["debt_paid_off", "percentage_milestone", "consistency_streak", "negotiation_success", "savings_milestone"]
    title: str
    description: str
    badge_name: Optional[str] = None
    achievement_value: Decimal  # Amount or percentage
```

**CelebrationContent Schema**:
```python
class CelebrationContent(BaseModel):
    animation_type: Literal["confetti", "fireworks", "badge_unlock"]
    headline: str  # "First Victory!"
    message: str  # "You eliminated $4,500 in debt..."
    share_text: Optional[str] = None  # Social sharing template
```

**Logic**:
1. **Milestone Detection**:
   - Debt paid off: Check if any debt's balance = 0
   - Percentage milestones: Calculate total debt progress (25%, 50%, 75%)
   - Consistency streaks: Check for 3/6/12 consecutive months with payments
   - Negotiation success: Detected via `/negotiation/script` outcome update
2. **Celebration Trigger**: If milestone detected, generate personalized celebration
3. **Nudge Generation**:
   - If no activity in 5 days → "Don't lose momentum!"
   - If payment missed → "It's okay, get back on track today"
   - If exceeding plan → "You're ahead of schedule! Keep it up!"
4. **Habit Score**: Calculate consistency (% of scheduled payments made on time)

**Opik Tracing**:
- Input: Payment count, milestone candidates
- Output: Milestone detected (yes/no), celebration quality
- LLM-as-Judge: Evaluate if celebration message is encouraging and culturally appropriate
- Metrics: `milestone_trigger_rate`, `habit_score_avg`, `nudge_effectiveness` (user engagement after nudge)

**Example**:
```python
# app/agents/habit_agent.py
class HabitAgent(BaseAgent):
    @trace(name="check_milestones_and_habits")
    async def execute(self, input_data: HabitInput) -> HabitOutput:
        milestone = None
        celebration = None
        
        # 1. Check for debt payoff
        if input_data.recent_payment:
            paid_off_debt = next(
                (d for d in input_data.current_debts if d.current_balance == 0),
                None
            )
            if paid_off_debt:
                milestone = Milestone(
                    milestone_type="debt_paid_off",
                    title="First Victory!",
                    description=f"You eliminated ${paid_off_debt.original_balance:.2f} in debt!",
                    badge_name="First Victory"
                )
                celebration = await self._generate_celebration(milestone, input_data.user_id)
        
        # 2. Check percentage milestones
        total_paid = sum(p.amount for p in input_data.payment_history)
        total_original = input_data.plan.total_debt_amount
        percentage = (total_paid / total_original) * 100
        
        if percentage >= 25 and not self._milestone_exists(input_data.user_id, "25_percent"):
            milestone = Milestone(
                milestone_type="percentage_milestone",
                title="25% Debt-Free!",
                description="You've eliminated a quarter of your debt!",
                achievement_value=Decimal("25.0")
            )
        
        # 3. Generate nudges (if needed)
        nudges = await self._generate_nudges(input_data)
        
        # 4. Opik log
        if milestone:
            opik.log_event("milestone_triggered", {"type": milestone.milestone_type})
        
        return HabitOutput(
            milestone_triggered=milestone,
            celebration_content=celebration,
            nudges=nudges,
            habit_score=self._calculate_habit_score(input_data.payment_history)
        )
```

---

## 5. Negotiation Agent

**Responsibility**: Generate personalized creditor negotiation scripts, set up Vapi voice simulation.

**Input Contract**:
```python
class NegotiationInput(BaseModel):
    debt: Debt
    user_profile: UserProfile
    payment_history_score: float  # 0.0-1.0 (from debt.payment_history_score)
    account_age_years: float
    competitive_rates: Optional[List[float]] = None  # Research from market
```

**Output Contract**:
```python
class NegotiationOutput(BaseModel):
    script_text: str
    talking_points: List[TalkingPoint]
    success_probability: float  # 0.0-1.0 (estimated)
    optimal_timing: str
    vapi_session_config: Optional[VapiConfig] = None
    confidence_score: float  # Opik quality metric
```

**TalkingPoint Schema**:
```python
class TalkingPoint(BaseModel):
    key: str  # "loyalty", "payment_history", "competitive_offer"
    text: str  # Full sentence for user to say
    weight: float  # Importance (for script emphasis)
```

**Logic**:
1. Analyze user's position:
   - Account age: >3 years = strong loyalty point
   - Payment history: >80% = strong reliability point
   - Competitive rates: Research current market (GPT-5-Nano web search or manual input)
2. Generate script using GPT-5-Nano:
   - Prompt: "Generate negotiation script for Vietnamese user with [account_age] years, [payment_score]% on-time payments, current APR [current_rate]%, competitive offers at [competitive_rate]%"
   - Output: Personalized script in Vietnamese or English
3. Calculate success probability:
   - Formula: `0.5 * (payment_score) + 0.3 * (account_age / 10) + 0.2 * (rate_difference / current_rate)`
   - Higher score if user has strong leverage
4. Set up Vapi session:
   - Configure AI creditor persona (objections, counter-offers)
   - Provide feedback after practice (tone, confidence, script adherence)

**Opik Tracing**:
- Input: Debt details, user leverage factors
- Output: Script text, success probability
- LLM-as-Judge: Evaluate script for professionalism, persuasiveness, cultural appropriateness
- Metrics: `negotiation_success_rate` (% of users who report success), `script_quality_score` (LLM-as-judge rating)

**Example**:
```python
# app/agents/negotiation_agent.py
class NegotiationAgent(BaseAgent):
    @trace(name="generate_negotiation_script")
    async def execute(self, input_data: NegotiationInput) -> NegotiationOutput:
        # 1. Build leverage points
        leverage = []
        if input_data.account_age_years > 3:
            leverage.append(f"Loyal customer for {input_data.account_age_years:.1f} years")
        if input_data.payment_history_score > 0.8:
            leverage.append(f"{input_data.payment_history_score * 100:.0f}% on-time payment history")
        
        # 2. Generate script with GPT-5-Nano
        prompt = self._build_prompt(input_data, leverage)
        script = await self.openai_client.generate(prompt, model="gpt-5-nano")
        
        # 3. Calculate success probability
        success_prob = self._estimate_success(input_data)
        
        # 4. Setup Vapi session
        vapi_config = await self.vapi_client.create_session(
            scenario="creditor_negotiation",
            user_script=script,
            creditor_profile="financial_institution"
        )
        
        # 5. Opik LLM-as-judge
        quality = await opik.judge_output(
            prompt=prompt,
            response=script,
            criteria=["professionalism", "persuasiveness", "cultural_appropriateness"]
        )
        
        return NegotiationOutput(
            script_text=script,
            success_probability=success_prob,
            vapi_session_config=vapi_config,
            confidence_score=quality.overall_score
        )
```

---

## Orchestrator (ReAct Pattern)

**Responsibility**: Coordinate agents, handle errors, retry failed agents, maintain conversation state.

**ReAct Loop**:
```
1. THOUGHT: What should I do next? (Assessment needed? Re-optimization? Action generation?)
2. ACTION: Execute specific agent (e.g., AssessmentAgent.execute())
3. OBSERVATION: Check agent output, validate results
4. REPEAT: If not complete, loop (e.g., if assessment says unsustainable, don't optimize)
```

**Example**:
```python
# app/agents/orchestrator.py
class Orchestrator:
    @trace(name="orchestrate_plan_generation")
    async def generate_plan(self, user_id: str) -> RepaymentPlan:
        # 1. THOUGHT: Need to assess first
        assessment_input = await self._prepare_assessment_input(user_id)
        
        # 2. ACTION: Run AssessmentAgent
        assessment = await self.assessment_agent.execute(assessment_input)
        
        # 3. OBSERVATION: Check if sustainable
        if not assessment.is_sustainable:
            raise UnsustainableDebtError(assessment.unsustainable_reason)
        
        # 4. THOUGHT: Assessment passed, now optimize
        optimization_input = OptimizationInput(
            debts=assessment_input.debts,
            available_monthly_payment=assessment.available_income,
            strategy=assessment.recommended_strategy
        )
        
        # 5. ACTION: Run OptimizationAgent
        optimization = await self.optimization_agent.execute(optimization_input)
        
        # 6. THOUGHT: Generate actions for first week
        action_input = ActionInput(
            plan=optimization,
            current_date=date.today(),
            user_profile=await self._get_user_profile(user_id)
        )
        
        # 7. ACTION: Run ActionAgent
        actions = await self.action_agent.execute(action_input)
        
        # 8. Save plan to DB
        plan = await self._save_plan(user_id, optimization, actions)
        
        return plan
```

---

## Opik Integration Details

**Tracing Setup**:
```python
# app/core/opik_tracing.py
import opik

opik.configure(
    api_key=os.getenv("OPIK_API_KEY"),
    project_name="resolveai-agents"
)

def trace_agent(func):
    """Decorator to automatically trace agent execution"""
    @wraps(func)
    @opik.trace()
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        # Auto-log token usage, latency, etc.
        return result
    return wrapper
```

**LLM-as-Judge** (quality validation):
```python
# app/core/opik_tracing.py
async def judge_agent_output(
    agent_name: str,
    input_data: Dict,
    output_data: Dict,
    criteria: List[str]
) -> JudgeScore:
    """
    Use GPT-5-Nano as judge to evaluate agent output quality.
    
    Args:
        agent_name: Which agent produced this output
        input_data: Agent input
        output_data: Agent output
        criteria: ["accuracy", "hallucination_check", "cultural_appropriateness", ...]
        
    Returns:
        JudgeScore with per-criterion scores and overall rating
    """
    judge_prompt = f"""
    You are evaluating the output of the {agent_name} agent.
    
    INPUT: {json.dumps(input_data)}
    OUTPUT: {json.dumps(output_data)}
    
    Evaluate the output on these criteria: {', '.join(criteria)}
    
    For each criterion, provide:
    1. Score (0-10)
    2. Reasoning
    
    Focus on:
    - Accuracy: Is the information correct? (especially financial calculations)
    - Hallucination: Did the agent invent information not present in input?
    - Cultural Appropriateness: Is language/tone appropriate for Vietnamese users?
    - Actionability: Can the user act on this output?
    """
    
    judge_response = await openai_client.generate(judge_prompt, model="gpt-5-nano")
    scores = parse_judge_response(judge_response)
    
    # Log to Opik
    opik.log_evaluation(
        agent=agent_name,
        scores=scores,
        criteria=criteria
    )
    
    return scores
```

**Custom Dashboards**:
- **Agent Performance**: Latency, success rate, error rate per agent
- **Financial Accuracy**: LLM-as-judge scores for interest calculations, plan quality
- **User Engagement**: Action completion rate, milestone celebration clicks
- **Cost Tracking**: Token usage, API costs per user session

---

## Error Handling & Recovery

**Agent Errors**:
```python
class AgentError(Exception):
    """Base exception for agent errors"""
    pass

class AssessmentError(AgentError):
    """Assessment agent failed"""
    pass

class OptimizationError(AgentError):
    """Optimization agent failed (e.g., PuLP solver timeout)"""
    pass

class ExternalServiceError(AgentError):
    """External service (OpenAI, Vapi) failed"""
    pass
```

**Retry Logic**:
```python
# app/agents/orchestrator.py
async def execute_agent_with_retry(
    agent: BaseAgent,
    input_data: Any,
    max_retries: int = 3
) -> Any:
    for attempt in range(max_retries):
        try:
            result = await agent.execute(input_data)
            return result
        except ExternalServiceError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except AgentError as e:
            # Don't retry agent logic errors
            raise
```

**Graceful Degradation**:
- If GPT-5-Nano fails → Fall back to template-based responses
- If Vapi fails → Skip voice simulation, provide script only
- If optimization times out → Use simple greedy algorithm (less optimal but fast)

---

## Summary

**5 Specialized Agents**:
1. **AssessmentAgent**: Debt situation analysis, sustainability check
2. **OptimizationAgent**: Mathematical optimization (PuLP), repayment schedule
3. **ActionAgent**: Daily recommendations, personalized messaging
4. **HabitAgent**: Milestone detection, celebration triggers, nudges
5. **NegotiationAgent**: Creditor negotiation scripts, Vapi voice simulation

**Orchestrator**: ReAct-style coordination, error handling, retry logic

**Opik Integration**: Full tracing, LLM-as-judge quality validation, custom dashboards for hackathon demo

**Performance**: Each agent <1s latency (GPT-5-Nano fast inference), full plan generation <3s (spec PERF-001)

**Reliability**: Retry logic, graceful degradation, comprehensive error handling aligned with constitution code quality standards
