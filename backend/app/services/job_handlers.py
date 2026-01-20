"""
Job handlers for background processing of LLM operations.
"""

from typing import Any
from app.services.job_service import job_service, JobType
from app.services.plan_service import PlanService
from app.services.ocr_service import OCRService
from app.services.payment_service import PaymentService
from app.db.repositories.debt_repo import DebtRepository
from app.db.repositories.plan_repo import PlanRepository
from app.db.repositories.payment_repo import PaymentRepository
from app.agents.action_agent import action_agent
from app.models.plan import PlanRequest, PlanSimulationRequest, RepaymentStrategy
from app.models.payment import PaymentCreate
from datetime import date


async def handle_plan_generation(user_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Handle plan generation job.
    
    Args:
        user_id: User ID
        input_data: {
            "strategy": str,
            "extra_monthly_payment": float,
            "start_date": str,
            "custom_monthly_budget": float,
            "available_for_debt": float,
            "token": str
        }
    
    Returns:
        Generated plan as dict
    """
    request = PlanRequest(
        strategy=RepaymentStrategy(input_data.get("strategy", "avalanche")),
        extra_monthly_payment=input_data.get("extra_monthly_payment"),
        start_date=date.fromisoformat(input_data["start_date"]) if input_data.get("start_date") else date.today(),
        custom_monthly_budget=input_data.get("custom_monthly_budget")
    )
    
    available = input_data["available_for_debt"]
    token = input_data.get("token")
    
    plan = await PlanService.generate_plan(user_id, request, available, token)
    return plan.model_dump()


async def handle_plan_recalculation(user_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Handle plan recalculation job.
    
    Args:
        user_id: User ID
        input_data: {
            "plan_id": str,
            "strategy": str,
            "extra_monthly_payment": float,
            "available_for_debt": float
        }
    
    Returns:
        Recalculated plan as dict
    """
    plan_id = input_data["plan_id"]
    strategy = RepaymentStrategy(input_data["strategy"]) if input_data.get("strategy") else None
    extra_payment = input_data.get("extra_monthly_payment")
    available = input_data.get("available_for_debt")
    token = input_data.get("token")
    
    plan = await PlanService.recalculate_plan(
        user_id,
        plan_id,
        strategy,
        extra_payment,
        available,
        token
    )
    return plan.model_dump()


async def handle_plan_simulation(user_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Handle plan simulation job.
    
    Args:
        user_id: User ID
        input_data: {
            "strategy": str,
            "extra_monthly_payment": float,
            "income_change": float,
            "lump_sum_payment": float,
            "lump_sum_target_debt_id": str,
            "rate_reduction": dict,
            "available_for_debt": float
        }
    
    Returns:
        Simulation result as dict
    """
    request = PlanSimulationRequest(
        strategy=RepaymentStrategy(input_data.get("strategy", "avalanche")),
        extra_monthly_payment=input_data.get("extra_monthly_payment"),
        income_change=input_data.get("income_change"),
        lump_sum_payment=input_data.get("lump_sum_payment"),
        lump_sum_target_debt_id=input_data.get("lump_sum_target_debt_id"),
        rate_reduction=input_data.get("rate_reduction")
    )
    
    available = input_data["available_for_debt"]
    token = input_data.get("token")
    
    result = await PlanService.simulate_scenario(user_id, request, available, token)
    return result.model_dump()


async def handle_daily_actions(user_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Handle daily actions generation job.
    
    Args:
        user_id: User ID
        input_data: {
            "token": str
        }
    
    Returns:
        Daily actions as dict
    """
    token = input_data.get("token")
    
    # Get active plan
    active_plan = await PlanRepository.get_active_plan(user_id)
    
    # Get active debts
    debts_response = await DebtRepository.get_all_by_user(user_id)
    debts = debts_response.debts
    
    # Get payment stats
    payment_stats = await PaymentRepository.get_stats(user_id, token=token)
    
    # Get last payment
    recent_payments = await PaymentRepository.get_recent(user_id, days=30, limit=1, token=token)
    last_payment_date = recent_payments[0].payment_date if recent_payments else None
    
    # Generate actions
    actions = await action_agent.generate_daily_actions(
        plan=active_plan,
        debts=debts,
        current_streak=payment_stats.current_streak_days,
        last_payment_date=last_payment_date,
        payments_this_month=payment_stats.payments_this_month
    )
    
    return actions.model_dump()


async def handle_milestone_check(user_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Handle milestone check job.
    
    Args:
        user_id: User ID
        input_data: {
            "payment_data": dict,
            "token": str
        }
    
    Returns:
        Milestone check result as dict
    """
    payment_data = PaymentCreate(**input_data["payment_data"])
    token = input_data.get("token")
    
    payment, milestones = await PaymentService.log_payment(
        user_id=user_id,
        payment_data=payment_data,
        token=token
    )
    
    return {
        "payment": payment.model_dump(),
        "milestones": milestones.model_dump() if milestones else None
    }


async def handle_ocr_processing(user_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Handle OCR document processing job.
    
    Args:
        user_id: User ID
        input_data: {
            "file_content": bytes,
            "file_type": str,
            "upload_id": str
        }
    
    Returns:
        OCR result as dict
    """
    import base64
    
    # Decode base64 file content
    file_content = base64.b64decode(input_data["file_content"])
    file_type = input_data["file_type"]
    upload_id = input_data["upload_id"]
    
    result = await OCRService.process_document(
        file_content=file_content,
        file_type=file_type,
        upload_id=upload_id
    )
    
    return result.model_dump()


# Register all handlers
def register_all_handlers():
    """Register all job handlers with the job service."""
    job_service.register_handler(JobType.PLAN_GENERATION, handle_plan_generation)
    job_service.register_handler(JobType.PLAN_RECALCULATION, handle_plan_recalculation)
    job_service.register_handler(JobType.PLAN_SIMULATION, handle_plan_simulation)
    job_service.register_handler(JobType.DAILY_ACTIONS, handle_daily_actions)
    job_service.register_handler(JobType.MILESTONE_CHECK, handle_milestone_check)
    job_service.register_handler(JobType.OCR_PROCESSING, handle_ocr_processing)
