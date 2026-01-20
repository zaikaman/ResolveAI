"""
Negotiation Agent - Specializes in creditor interactions and debt negotiation strategies.

Crafts professional scripts for Vietnamese banks, prepares negotiation tactics,
and can integrate with Vapi.ai for voice call simulations.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import date

from app.agents.base_agent import BaseAgent
from app.core.openai_client import openai_client
from app.models.debt import DebtResponse


class NegotiationTactic(str, Enum):
    """Negotiation approach types."""
    HARDSHIP_APPEAL = "hardship_appeal"
    RATE_REDUCTION = "rate_reduction"
    SETTLEMENT_OFFER = "settlement_offer"
    PAYMENT_PLAN = "payment_plan"
    BALANCE_TRANSFER = "balance_transfer"
    WAIVE_FEES = "waive_fees"


class NegotiationScript(BaseModel):
    """Negotiation script for creditor communication."""
    tactic: NegotiationTactic
    creditor_name: str
    script_type: str  # email, phone_call, letter
    opening: str
    main_points: List[str]
    key_phrases: List[str]
    closing: str
    dos: List[str]
    donts: List[str]
    expected_outcomes: List[str]
    fallback_options: List[str]
    full_script: str


class NegotiationPlan(BaseModel):
    """Complete negotiation plan for a debt."""
    debt_id: str
    creditor_name: str
    current_terms: Dict[str, Any]
    target_terms: Dict[str, Any]
    recommended_tactics: List[NegotiationTactic]
    scripts: List[NegotiationScript]
    timeline: str
    success_probability: float
    preparation_checklist: List[str]
    vietnamese_regulations: List[str]
    risk_assessment: str


class VapiCallFlow(BaseModel):
    """Vapi.ai voice call flow configuration."""
    call_purpose: str
    conversation_stages: List[Dict[str, Any]]
    objection_handling: Dict[str, str]
    success_criteria: List[str]
    sample_dialogues: List[Dict[str, str]]


class NegotiationAgent(BaseAgent):
    """
    Agent for creditor negotiation strategies.
    
    Generates professional scripts, prepares negotiation tactics,
    and provides confidence-building support for creditor interactions.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="NegotiationAgent",
            description="Specializes in creditor negotiation and debt settlement strategies"
        )
    
    async def create_negotiation_plan(
        self,
        debt: DebtResponse,
        user_situation: Dict[str, Any],
        negotiation_goal: str = "reduce_apr"
    ) -> NegotiationPlan:
        """
        Create comprehensive negotiation plan for a specific debt.
        
        Args:
            debt: The debt to negotiate
            user_situation: User's financial context (income, hardship, payment history)
            negotiation_goal: What to negotiate (reduce_apr, waive_fees, payment_plan, settlement)
        
        Returns:
            Complete negotiation plan with scripts and tactics
        """
        return await self.trace_execution(
            self._create_plan,
            debt=debt,
            user_situation=user_situation,
            negotiation_goal=negotiation_goal
        )
    
    async def generate_script(
        self,
        debt: DebtResponse,
        tactic: NegotiationTactic,
        script_type: str,
        user_context: Dict[str, Any]
    ) -> NegotiationScript:
        """
        Generate specific negotiation script.
        
        Args:
            debt: Target debt
            tactic: Negotiation tactic to use
            script_type: email, phone_call, or letter
            user_context: User's situation details
        
        Returns:
            Detailed script with dos/donts
        """
        return await self.trace_execution(
            self._generate_script,
            debt=debt,
            tactic=tactic,
            script_type=script_type,
            user_context=user_context
        )
    
    async def create_vapi_flow(
        self,
        negotiation_plan: NegotiationPlan,
        practice_mode: bool = True
    ) -> VapiCallFlow:
        """
        Create Vapi.ai voice call flow for negotiation practice.
        
        Args:
            negotiation_plan: The negotiation plan
            practice_mode: If True, creates sandbox/practice flow
        
        Returns:
            Vapi call flow configuration
        """
        return await self.trace_execution(
            self._create_vapi_flow,
            negotiation_plan=negotiation_plan,
            practice_mode=practice_mode
        )
    
    async def _create_plan(
        self,
        debt: DebtResponse,
        user_situation: Dict[str, Any],
        negotiation_goal: str
    ) -> NegotiationPlan:
        """Internal plan creation using AI."""
        
        prompt = f"""Create a comprehensive negotiation plan for debt negotiation in Vietnam.

Debt Details:
- Creditor: {debt.creditor_name}
- Type: {debt.debt_type}
- Balance: ${debt.balance:,.2f}
- APR: {debt.apr}%
- Minimum Payment: ${debt.minimum_payment:.2f}

User Situation:
{self._format_situation(user_situation)}

Negotiation Goal: {negotiation_goal}

Create detailed plan in JSON format:
{{
  "current_terms": {{"apr": {debt.apr}, "balance": {debt.balance}, "minimum_payment": {debt.minimum_payment}}},
  "target_terms": {{"apr": 12.0, "waived_fees": 50.0}},
  "recommended_tactics": ["rate_reduction", "hardship_appeal"],
  "timeline": "2-4 weeks, 3 contact attempts",
  "success_probability": 0.65,
  "preparation_checklist": [
    "Gather 6 months payment history",
    "Document hardship (if applicable)",
    "Research competitor rates",
    "Know your minimum acceptable offer"
  ],
  "vietnamese_regulations": [
    "State Bank of Vietnam Circular 39/2016 on debt restructuring",
    "Consumer protection laws apply to unfair collection practices"
  ],
  "risk_assessment": "Moderate success chance. Bank may initially refuse but counter-offer likely."
}}

Be specific to Vietnamese banking practices. Return ONLY valid JSON.
"""
        
        try:
            response = await openai_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert debt negotiation consultant specializing in Vietnamese banking.
You understand Vietnamese regulations, bank policies, cultural norms, and effective negotiation tactics.
Your role is to create professional, realistic negotiation plans that work in Vietnam's banking context."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )
            
            import json
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(line for line in lines if not line.startswith("```"))
            
            data = json.loads(response)
            
            # Generate scripts for each tactic
            scripts = []
            for tactic in data.get("recommended_tactics", []):
                script = await self._generate_script(
                    debt=debt,
                    tactic=NegotiationTactic(tactic),
                    script_type="phone_call",
                    user_context=user_situation
                )
                scripts.append(script)
            
            return NegotiationPlan(
                debt_id=str(debt.id),
                creditor_name=debt.creditor_name,
                current_terms=data["current_terms"],
                target_terms=data["target_terms"],
                recommended_tactics=[NegotiationTactic(t) for t in data["recommended_tactics"]],
                scripts=scripts,
                timeline=data["timeline"],
                success_probability=data["success_probability"],
                preparation_checklist=data["preparation_checklist"],
                vietnamese_regulations=data.get("vietnamese_regulations", []),
                risk_assessment=data["risk_assessment"]
            )
        
        except Exception as e:
            print(f"Negotiation plan creation failed: {e}")
            return self._generate_fallback_plan(debt, user_situation, negotiation_goal)
    
    async def _generate_script(
        self,
        debt: DebtResponse,
        tactic: NegotiationTactic,
        script_type: str,
        user_context: Dict[str, Any]
    ) -> NegotiationScript:
        """Generate negotiation script using AI."""
        
        prompt = f"""Create a professional negotiation script for Vietnamese banking context.

Creditor: {debt.creditor_name}
Debt: ${debt.balance:,.2f} @ {debt.apr}% APR
Tactic: {tactic.value}
Format: {script_type}
User Context: {self._format_situation(user_context)}

Generate in JSON format:
{{
  "opening": "Professional greeting and introduction",
  "main_points": [
    "I've been a customer for X years and maintained good payment history",
    "Due to [specific hardship], I'm requesting [specific ask]",
    "I've researched comparable rates and found X%"
  ],
  "key_phrases": [
    "I value our relationship and want to find a solution",
    "Is there a supervisor who can review my account?",
    "I'm committed to paying but need adjusted terms"
  ],
  "closing": "Thank you for considering my request. When can I expect a response?",
  "dos": [
    "Be polite and professional",
    "Have account details ready",
    "Take notes during call",
    "Ask for confirmation in writing"
  ],
  "donts": [
    "Don't threaten to default",
    "Don't get emotional or aggressive",
    "Don't accept first offer immediately",
    "Don't share more info than needed"
  ],
  "expected_outcomes": [
    "Immediate approval (15% chance)",
    "Request for documentation (50% chance)",
    "Denial but counter-offer (30% chance)",
    "Flat denial (5% chance)"
  ],
  "fallback_options": [
    "Ask to speak with supervisor",
    "Request written denial for records",
    "Ask about hardship programs",
    "Propose specific alternative terms"
  ],
  "full_script": "Complete word-for-word script in Vietnamese and English"
}}

Make it culturally appropriate for Vietnam, professional, and effective. Return ONLY JSON.
"""
        
        try:
            response = await openai_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional negotiation coach specializing in Vietnamese debt negotiation.
Create scripts that are assertive but respectful, culturally appropriate, and effective with Vietnamese banks."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )
            
            import json
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(line for line in lines if not line.startswith("```"))
            
            data = json.loads(response)
            
            return NegotiationScript(
                tactic=tactic,
                creditor_name=debt.creditor_name,
                script_type=script_type,
                opening=data["opening"],
                main_points=data["main_points"],
                key_phrases=data["key_phrases"],
                closing=data["closing"],
                dos=data["dos"],
                donts=data["donts"],
                expected_outcomes=data["expected_outcomes"],
                fallback_options=data["fallback_options"],
                full_script=data["full_script"]
            )
        
        except Exception as e:
            print(f"Script generation failed: {e}")
            return self._generate_fallback_script(debt, tactic, script_type)
    
    async def _create_vapi_flow(
        self,
        negotiation_plan: NegotiationPlan,
        practice_mode: bool
    ) -> VapiCallFlow:
        """Create Vapi.ai call flow."""
        
        prompt = f"""Create a Vapi.ai voice call flow for negotiation practice.

Negotiation Plan:
- Creditor: {negotiation_plan.creditor_name}
- Goal: {negotiation_plan.target_terms}
- Tactics: {[t.value for t in negotiation_plan.recommended_tactics]}

Mode: {"Practice/Sandbox" if practice_mode else "Live"}

Generate Vapi conversation flow in JSON:
{{
  "call_purpose": "Practice negotiating APR reduction with {negotiation_plan.creditor_name}",
  "conversation_stages": [
    {{
      "stage": "greeting",
      "bot_message": "Thank you for calling {negotiation_plan.creditor_name}. How can I help?",
      "expected_user_response": "User introduces themselves and states purpose",
      "coaching_tip": "Speak clearly, be confident"
    }},
    {{
      "stage": "verification",
      "bot_message": "I'll need to verify your account. Last 4 of SSN?",
      "expected_user_response": "Provides verification",
      "coaching_tip": "Have account info ready"
    }}
  ],
  "objection_handling": {{
    "We can't change your rate": "Response: I understand policies, but given my payment history and current situation, is there a hardship program or supervisor who could review?",
    "You need to fill out a form": "Response: I'm happy to do that. Can you email it now while we're on the call? What's the typical timeline for review?"
  }},
  "success_criteria": [
    "Got approval or counter-offer",
    "Got case number or timeline",
    "Maintained professional tone throughout"
  ],
  "sample_dialogues": [
    {{"user": "I'd like to discuss my APR", "bot": "I can help with that. Let me pull up your account."}},
    {{"user": "I've been a good customer for 3 years", "bot": "I see that. Your payment history is good. What specifically are you requesting?"}}
  ]
}}

Return ONLY valid JSON for Vapi integration.
"""
        
        try:
            response = await openai_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Vapi.ai conversation designer creating realistic bank negotiation practice flows."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )
            
            import json
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(line for line in lines if not line.startswith("```"))
            
            data = json.loads(response)
            
            return VapiCallFlow(**data)
        
        except Exception as e:
            print(f"Vapi flow creation failed: {e}")
            return VapiCallFlow(
                call_purpose="Negotiation practice",
                conversation_stages=[],
                objection_handling={},
                success_criteria=[],
                sample_dialogues=[]
            )
    
    def _format_situation(self, situation: Dict[str, Any]) -> str:
        """Format user situation for prompts."""
        parts = []
        if situation.get("income"):
            parts.append(f"Monthly Income: ${situation['income']:,.2f}")
        if situation.get("hardship"):
            parts.append(f"Hardship: {situation['hardship']}")
        if situation.get("payment_history"):
            parts.append(f"Payment History: {situation['payment_history']}")
        return "\n".join(parts) if parts else "No additional context"
    
    def _generate_fallback_plan(
        self,
        debt: DebtResponse,
        user_situation: Dict[str, Any],
        negotiation_goal: str
    ) -> NegotiationPlan:
        """Fallback negotiation plan."""
        return NegotiationPlan(
            debt_id=str(debt.id),
            creditor_name=debt.creditor_name,
            current_terms={"apr": debt.apr, "balance": debt.balance},
            target_terms={"apr": max(debt.apr - 3, 8)},
            recommended_tactics=[NegotiationTactic.RATE_REDUCTION],
            scripts=[],
            timeline="2-4 weeks",
            success_probability=0.5,
            preparation_checklist=[
                "Review payment history",
                "Research competitor rates",
                "Prepare hardship documentation"
            ],
            vietnamese_regulations=[],
            risk_assessment="Moderate success chance with proper preparation"
        )
    
    def _generate_fallback_script(
        self,
        debt: DebtResponse,
        tactic: NegotiationTactic,
        script_type: str
    ) -> NegotiationScript:
        """Fallback script template."""
        return NegotiationScript(
            tactic=tactic,
            creditor_name=debt.creditor_name,
            script_type=script_type,
            opening=f"Hello, I'm calling about my account ending in {debt.account_number_last4 or 'XXXX'}.",
            main_points=[
                "I've been a loyal customer",
                f"I'm requesting a review of my {debt.apr}% APR",
                "I'm committed to paying but need better terms"
            ],
            key_phrases=[
                "Is there a supervisor available?",
                "Can you review my account for hardship programs?",
                "What documentation do you need?"
            ],
            closing="Thank you for your time. When can I expect an answer?",
            dos=["Be polite", "Take notes", "Get name/ID of rep"],
            donts=["Don't threaten", "Don't get emotional"],
            expected_outcomes=["Request for documentation", "Transfer to supervisor"],
            fallback_options=["Ask for callback", "Request written response"],
            full_script="[Professional script template]"
        )


# Singleton instance
negotiation_agent = NegotiationAgent()
