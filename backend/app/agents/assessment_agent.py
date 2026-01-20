"""
Assessment Agent - Analyzes user's financial situation from uploaded documents and manual entries.

Uses GPT-5-Nano vision for OCR on Vietnamese bank statements, categorizes debts,
identifies spending leaks, and provides comprehensive financial diagnosis.
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from app.agents.base_agent import BaseAgent
from app.core.openai_client import openai_client
from app.models.debt import DebtResponse


class DebtCategory(str, Enum):
    """Debt categorization."""
    HIGH_INTEREST_CREDIT = "high_interest_credit"  # >15% APR
    MODERATE_CREDIT = "moderate_credit"  # 10-15% APR
    LOW_INTEREST_LOAN = "low_interest_loan"  # <10% APR
    MEDICAL = "medical"
    STUDENT = "student"
    MORTGAGE = "mortgage"
    OTHER = "other"


class SpendingLeak(BaseModel):
    """Identified spending leak."""
    category: str
    monthly_amount: float
    description: str
    saving_potential: float
    suggestions: List[str]


class RiskFactor(BaseModel):
    """Identified financial risk."""
    risk_type: str
    severity: str  # low, medium, high, critical
    description: str
    impact: str
    recommendation: str


class FinancialAssessment(BaseModel):
    """Complete financial assessment result."""
    total_debt: float
    total_monthly_payment: float
    total_interest_burden: float  # Annual interest cost
    debt_to_income_ratio: Optional[float] = None
    categorized_debts: Dict[str, List[str]]  # category -> debt IDs
    spending_leaks: List[SpendingLeak]
    risk_factors: List[RiskFactor]
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    available_for_debt: Optional[float] = None
    assessment_summary: str
    recommendations: List[str]
    confidence_score: float = Field(ge=0, le=1)  # AI confidence in assessment


class AssessmentAgent(BaseAgent):
    """
    Agent for comprehensive financial assessment.
    
    Analyzes debts, income, expenses, and spending patterns to provide
    accurate financial diagnosis. Uses GPT-5-Nano vision for OCR.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="AssessmentAgent",
            description="Analyzes financial situation and provides comprehensive diagnosis"
        )
    
    async def assess_financial_situation(
        self,
        debts: List[DebtResponse],
        monthly_income: Optional[float] = None,
        monthly_expenses: Optional[float] = None,
        ocr_data: Optional[Dict[str, Any]] = None
    ) -> FinancialAssessment:
        """
        Assess user's complete financial situation.
        
        Args:
            debts: List of user's debts
            monthly_income: Reported monthly income
            monthly_expenses: Reported monthly expenses
            ocr_data: Optional OCR-extracted data from bank statements
        
        Returns:
            FinancialAssessment with diagnosis and recommendations
        """
        return await self.trace_execution(
            self._assess_situation,
            debts=debts,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            ocr_data=ocr_data
        )
    
    async def perform_ocr_analysis(
        self,
        image_url: str,
        document_type: str = "bank_statement"
    ) -> Dict[str, Any]:
        """
        Use GPT-5-Nano vision to extract data from Vietnamese bank documents.
        
        Args:
            image_url: URL to the uploaded image
            document_type: Type of document (bank_statement, credit_card, loan_statement)
        
        Returns:
            Extracted structured data
        """
        return await self.trace_execution(
            self._perform_ocr,
            image_url=image_url,
            document_type=document_type
        )
    
    async def _perform_ocr(
        self,
        image_url: str,
        document_type: str
    ) -> Dict[str, Any]:
        """Internal OCR processing with GPT-5-Nano vision."""
        
        prompt = f"""Analyze this Vietnamese {document_type} and extract ALL relevant financial information.

Extract in JSON format:
- creditor_name: Bank/creditor name
- account_number: Account or card number (last 4 digits if masked)
- balance: Current balance/outstanding amount
- credit_limit: Credit limit (if applicable)
- apr: Annual percentage rate (if shown)
- minimum_payment: Minimum payment due
- due_date: Payment due date
- transactions: Recent transactions (date, description, amount)
- income_deposits: Any salary/income deposits identified
- recurring_charges: Subscriptions or recurring payments spotted

Return ONLY valid JSON, be precise with Vietnamese text and numbers.
"""
        
        try:
            response = await openai_client.vision_completion(
                image_url=image_url,
                prompt=prompt
            )
            
            import json
            # Parse response
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(line for line in lines if not line.startswith("```"))
            
            return json.loads(response)
        
        except Exception as e:
            print(f"OCR analysis failed: {e}")
            return {"error": str(e), "raw_response": response if 'response' in locals() else None}
    
    async def _assess_situation(
        self,
        debts: List[DebtResponse],
        monthly_income: Optional[float],
        monthly_expenses: Optional[float],
        ocr_data: Optional[Dict[str, Any]]
    ) -> FinancialAssessment:
        """Internal assessment logic using AI."""
        
        # Build context
        context = self._build_assessment_context(debts, monthly_income, monthly_expenses, ocr_data)
        
        # Use AI to analyze
        prompt = self._build_assessment_prompt(context)
        
        try:
            response = await openai_client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert financial analyst specializing in debt assessment for Vietnamese users.
Your role is to:
1. Categorize debts by priority (high-interest vs low-interest)
2. Identify spending leaks and wasteful expenses
3. Spot financial risks (minimum payment traps, high DTI ratio, etc.)
4. Calculate debt burden and available cash flow
5. Provide actionable, empathetic recommendations

Be precise with numbers, culturally aware (Vietnamese context), and honest about risks."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )
            
            # Parse AI assessment
            assessment = self._parse_assessment_response(response, debts, monthly_income, monthly_expenses)
            
        except Exception as e:
            print(f"AI assessment failed: {e}")
            # Fallback to rule-based
            assessment = self._generate_fallback_assessment(debts, monthly_income, monthly_expenses)
        
        return assessment
    
    def _build_assessment_context(
        self,
        debts: List[DebtResponse],
        monthly_income: Optional[float],
        monthly_expenses: Optional[float],
        ocr_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build context for AI analysis."""
        
        debt_details = []
        for debt in debts:
            debt_details.append({
                "id": str(debt.id),
                "creditor": debt.creditor_name,
                "type": debt.debt_type,
                "balance": debt.balance,
                "apr": debt.apr,
                "minimum_payment": debt.minimum_payment,
                "due_date": debt.due_date
            })
        
        return {
            "debts": debt_details,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "ocr_data": ocr_data,
            "total_debts": len(debts),
            "active_debts": len([d for d in debts if not d.is_paid_off])
        }
    
    def _build_assessment_prompt(self, context: Dict[str, Any]) -> str:
        """Build assessment prompt."""
        
        prompt = "Analyze this financial situation:\n\n"
        
        # Debts
        prompt += f"Debts ({context['total_debts']} total):\n"
        for debt in context['debts']:
            prompt += f"- {debt['creditor']} ({debt['type']}): ${debt['balance']:,.2f} @ {debt['apr']:.1f}% APR, "
            prompt += f"${debt['minimum_payment']:.2f} minimum\n"
        
        # Income/Expenses
        if context['monthly_income']:
            prompt += f"\nMonthly Income: ${context['monthly_income']:,.2f}\n"
        if context['monthly_expenses']:
            prompt += f"Monthly Expenses: ${context['monthly_expenses']:,.2f}\n"
        
        # OCR data
        if context.get('ocr_data'):
            prompt += f"\nExtracted Bank Data: {context['ocr_data']}\n"
        
        prompt += """
Provide comprehensive assessment in JSON format:
{
  "categorized_debts": {"high_interest_credit": ["debt_id1"], "low_interest_loan": ["debt_id2"]},
  "spending_leaks": [
    {
      "category": "food_delivery",
      "monthly_amount": 150.00,
      "description": "Frequent GrabFood orders",
      "saving_potential": 100.00,
      "suggestions": ["Cook at home 3x/week", "Use meal prep"]
    }
  ],
  "risk_factors": [
    {
      "risk_type": "minimum_payment_trap",
      "severity": "high",
      "description": "Only paying minimums on high-APR card",
      "impact": "Will take 15 years to pay off, $10k extra interest",
      "recommendation": "Increase payment by $100/month"
    }
  ],
  "total_interest_burden": 2400.00,
  "debt_to_income_ratio": 0.45,
  "available_for_debt": 500.00,
  "assessment_summary": "You have $15k in debt, primarily high-interest credit cards...",
  "recommendations": [
    "Prioritize Capital One card (18% APR) with avalanche method",
    "Cut food delivery expenses by 50% to free up $75/month",
    "Consider balance transfer to lower APR if credit score allows"
  ],
  "confidence_score": 0.85
}

Return ONLY valid JSON.
"""
        return prompt
    
    def _parse_assessment_response(
        self,
        response: str,
        debts: List[DebtResponse],
        monthly_income: Optional[float],
        monthly_expenses: Optional[float]
    ) -> FinancialAssessment:
        """Parse AI response into FinancialAssessment."""
        import json
        
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(line for line in lines if not line.startswith("```"))
        
        data = json.loads(response)
        
        # Calculate totals
        total_debt = sum(d.balance for d in debts if not d.is_paid_off)
        total_monthly = sum(d.minimum_payment for d in debts if not d.is_paid_off)
        
        # Parse spending leaks
        leaks = [SpendingLeak(**leak) for leak in data.get("spending_leaks", [])]
        
        # Parse risks
        risks = [RiskFactor(**risk) for risk in data.get("risk_factors", [])]
        
        return FinancialAssessment(
            total_debt=total_debt,
            total_monthly_payment=total_monthly,
            total_interest_burden=data.get("total_interest_burden", 0),
            debt_to_income_ratio=data.get("debt_to_income_ratio"),
            categorized_debts=data.get("categorized_debts", {}),
            spending_leaks=leaks,
            risk_factors=risks,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            available_for_debt=data.get("available_for_debt"),
            assessment_summary=data.get("assessment_summary", ""),
            recommendations=data.get("recommendations", []),
            confidence_score=data.get("confidence_score", 0.5)
        )
    
    def _generate_fallback_assessment(
        self,
        debts: List[DebtResponse],
        monthly_income: Optional[float],
        monthly_expenses: Optional[float]
    ) -> FinancialAssessment:
        """Fallback rule-based assessment."""
        
        active_debts = [d for d in debts if not d.is_paid_off]
        
        total_debt = sum(d.balance for d in active_debts)
        total_monthly = sum(d.minimum_payment for d in active_debts)
        total_interest = sum(d.balance * (d.apr / 100) for d in active_debts)
        
        # Categorize by APR
        categorized = {
            "high_interest_credit": [str(d.id) for d in active_debts if d.apr >= 15],
            "moderate_credit": [str(d.id) for d in active_debts if 10 <= d.apr < 15],
            "low_interest_loan": [str(d.id) for d in active_debts if d.apr < 10]
        }
        
        # Check risks
        risks = []
        if any(d.apr >= 18 for d in active_debts):
            risks.append(RiskFactor(
                risk_type="high_interest_debt",
                severity="high",
                description="You have debt with 18%+ APR",
                impact="Paying significantly more in interest over time",
                recommendation="Prioritize paying off highest APR debts first"
            ))
        
        dti = None
        available = None
        if monthly_income and monthly_income > 0:
            dti = total_monthly / monthly_income
            if dti > 0.43:
                risks.append(RiskFactor(
                    risk_type="high_dti_ratio",
                    severity="critical",
                    description=f"Debt-to-income ratio is {dti:.1%}",
                    impact="May struggle to meet minimum payments",
                    recommendation="Urgently need to increase income or reduce debt"
                ))
            
            if monthly_expenses:
                available = monthly_income - monthly_expenses - total_monthly
        
        return FinancialAssessment(
            total_debt=total_debt,
            total_monthly_payment=total_monthly,
            total_interest_burden=total_interest,
            debt_to_income_ratio=dti,
            categorized_debts=categorized,
            spending_leaks=[],
            risk_factors=risks,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            available_for_debt=available,
            assessment_summary=f"You have ${total_debt:,.2f} in total debt across {len(active_debts)} accounts.",
            recommendations=[
                "Focus on high-interest debts first",
                "Track spending to find areas to cut",
                "Consider debt consolidation if available"
            ],
            confidence_score=0.6
        )


# Singleton instance
assessment_agent = AssessmentAgent()
