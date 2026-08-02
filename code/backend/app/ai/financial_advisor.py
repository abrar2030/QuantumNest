import warnings
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from app.core.time_utils import utc_now

warnings.filterwarnings("ignore")
import logging
import os

from app.ai.advanced_lstm_model import AdvancedLSTMModel
from app.ai.portfolio_optimization import AdvancedPortfolioOptimizer
from app.services.market_data_service import MarketDataService
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class InvestmentGoal(str, Enum):
    RETIREMENT = "retirement"
    EDUCATION = "education"
    HOME_PURCHASE = "home_purchase"
    WEALTH_BUILDING = "wealth_building"
    INCOME_GENERATION = "income_generation"
    EMERGENCY_FUND = "emergency_fund"
    TAX_OPTIMIZATION = "tax_optimization"


class RiskTolerance(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"


class InvestmentHorizon(str, Enum):
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


@dataclass
class UserProfile:
    """User financial profile"""

    user_id: str
    age: int
    income: float
    net_worth: float
    investment_experience: str
    risk_tolerance: RiskTolerance
    investment_goals: List[InvestmentGoal]
    investment_horizon: InvestmentHorizon
    current_portfolio: Dict[str, float]
    monthly_investment_capacity: float
    tax_bracket: float
    dependents: int
    debt_obligations: float
    emergency_fund_months: int
    preferences: Dict[str, Any]


@dataclass
class FinancialAdvice:
    """Financial advice recommendation"""

    user_id: str
    advice_type: str
    title: str
    description: str
    recommended_actions: List[str]
    expected_outcomes: Dict[str, Any]
    risk_assessment: str
    confidence_score: float
    supporting_data: Dict[str, Any]
    implementation_steps: List[str]
    monitoring_metrics: List[str]
    timestamp: datetime


@dataclass
class PortfolioRecommendation:
    """Portfolio allocation recommendation"""

    user_id: str
    recommended_allocation: Dict[str, float]
    asset_recommendations: List[Dict[str, Any]]
    rebalancing_strategy: str
    expected_return: float
    expected_volatility: float
    rationale: str
    implementation_cost: float
    tax_implications: Dict[str, Any]


class AIFinancialAdvisor:
    """AI-powered financial advisor with personalized recommendations"""

    def __init__(self, config: Optional[Dict] = None) -> None:
        """Initialize AI financial advisor"""
        self.config = {
            "openai_model": "gpt-4",
            "max_tokens": 2000,
            "temperature": 0.7,
            "min_portfolio_size": 1000,
            "max_recommendations": 10,
            "confidence_threshold": 0.6,
            "allocation_models": [
                "target_date",
                "risk_parity",
                "factor_based",
                "goal_based",
            ],
            "lookback_period": 252,
            "benchmark_symbols": ["SPY", "AGG", "VTI", "VXUS"],
            "risk_factors": [
                "age",
                "income_stability",
                "debt_ratio",
                "investment_experience",
            ],
            "retirement_replacement_ratio": 0.8,
            "education_inflation_rate": 0.05,
            "home_down_payment_ratio": 0.2,
            "tax_loss_harvesting": True,
            "asset_location_optimization": True,
            "behavioral_biases": [
                "loss_aversion",
                "overconfidence",
                "herding",
                "anchoring",
            ],
        }
        if config:
            self.config.update(config)
        self.market_data = MarketDataService()
        self.portfolio_optimizer = AdvancedPortfolioOptimizer()
        self.lstm_model = AdvancedLSTMModel()
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE")
        )
        self.user_profiles = {}
        self.recommendation_history = {}
        self.asset_database = {}
        self.market_insights = {}

    async def create_user_profile(self, user_data: Dict[str, Any]) -> UserProfile:
        """Create comprehensive user financial profile"""
        try:
            profile = UserProfile(
                user_id=user_data["user_id"],
                age=user_data.get("age", 30),
                income=user_data.get("income", 50000),
                net_worth=user_data.get("net_worth", 0),
                investment_experience=user_data.get(
                    "investment_experience", "beginner"
                ),
                risk_tolerance=RiskTolerance(
                    user_data.get("risk_tolerance", "moderate")
                ),
                investment_goals=[
                    InvestmentGoal(goal)
                    for goal in user_data.get("investment_goals", ["wealth_building"])
                ],
                investment_horizon=InvestmentHorizon(
                    user_data.get("investment_horizon", "long_term")
                ),
                current_portfolio=user_data.get("current_portfolio", {}),
                monthly_investment_capacity=user_data.get(
                    "monthly_investment_capacity", 500
                ),
                tax_bracket=user_data.get("tax_bracket", 0.22),
                dependents=user_data.get("dependents", 0),
                debt_obligations=user_data.get("debt_obligations", 0),
                emergency_fund_months=user_data.get("emergency_fund_months", 3),
                preferences=user_data.get("preferences", {}),
            )
            self.user_profiles[profile.user_id] = profile
            logger.info(f"Created user profile for {profile.user_id}")
            return profile
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}", exc_info=True)
            raise

    async def generate_comprehensive_advice(
        self, user_id: str
    ) -> List[FinancialAdvice]:
        """Generate comprehensive financial advice for user"""
        try:
            if user_id not in self.user_profiles:
                raise ValueError(f"User profile not found for {user_id}")
            profile = self.user_profiles[user_id]
            advice_list = []
            emergency_advice = await self._assess_emergency_fund(profile)
            if emergency_advice:
                advice_list.append(emergency_advice)
            debt_advice = await self._assess_debt_management(profile)
            if debt_advice:
                advice_list.append(debt_advice)
            investment_advice = await self._generate_investment_advice(profile)
            if investment_advice:
                advice_list.append(investment_advice)
            tax_advice = await self._generate_tax_advice(profile)
            if tax_advice:
                advice_list.append(tax_advice)
            for goal in profile.investment_goals:
                goal_advice = await self._generate_goal_specific_advice(profile, goal)
                if goal_advice:
                    advice_list.append(goal_advice)
            risk_advice = await self._assess_risk_management(profile)
            if risk_advice:
                advice_list.append(risk_advice)
            if user_id not in self.recommendation_history:
                self.recommendation_history[user_id] = []
            self.recommendation_history[user_id].extend(advice_list)
            logger.info(
                f"Generated {len(advice_list)} recommendations for user {user_id}"
            )
            return advice_list
        except Exception as e:
            logger.error(
                f"Error generating comprehensive advice: {str(e)}", exc_info=True
            )
            return []

    async def generate_portfolio_recommendation(
        self, user_id: str
    ) -> PortfolioRecommendation:
        """Generate personalized portfolio recommendation"""
        try:
            if user_id not in self.user_profiles:
                raise ValueError(f"User profile not found for {user_id}")
            profile = self.user_profiles[user_id]
            allocation_strategy = self._determine_allocation_strategy(profile)
            recommended_allocation = await self._calculate_target_allocation(
                profile, allocation_strategy
            )
            asset_recommendations = await self._recommend_specific_assets(
                profile, recommended_allocation
            )
            expected_return, expected_volatility = (
                await self._calculate_portfolio_metrics(
                    recommended_allocation, asset_recommendations
                )
            )
            rationale = await self._generate_allocation_rationale(
                profile, recommended_allocation
            )
            implementation_cost = self._calculate_implementation_cost(
                profile.current_portfolio, recommended_allocation
            )
            tax_implications = self._assess_tax_implications(
                profile, recommended_allocation
            )
            recommendation = PortfolioRecommendation(
                user_id=user_id,
                recommended_allocation=recommended_allocation,
                asset_recommendations=asset_recommendations,
                rebalancing_strategy=self._determine_rebalancing_strategy(profile),
                expected_return=expected_return,
                expected_volatility=expected_volatility,
                rationale=rationale,
                implementation_cost=implementation_cost,
                tax_implications=tax_implications,
            )
            logger.info(f"Generated portfolio recommendation for user {user_id}")
            return recommendation
        except Exception as e:
            logger.error(
                f"Error generating portfolio recommendation: {str(e)}", exc_info=True
            )
            raise

    async def provide_market_insights(self, user_id: str) -> Dict[str, Any]:
        """Provide personalized market insights"""
        try:
            if user_id not in self.user_profiles:
                raise ValueError(f"User profile not found for {user_id}")
            profile = self.user_profiles[user_id]
            market_data = await self._get_relevant_market_data(profile)
            market_outlook = await self._generate_market_outlook(market_data)
            sector_analysis = await self._analyze_sectors(profile)
            economic_impact = await self._assess_economic_indicators(profile)
            ai_insights = await self._generate_ai_market_insights(profile, market_data)
            insights = {
                "user_id": user_id,
                "market_outlook": market_outlook,
                "sector_analysis": sector_analysis,
                "economic_impact": economic_impact,
                "ai_insights": ai_insights,
                "personalized_opportunities": await self._identify_opportunities(
                    profile, market_data
                ),
                "risk_alerts": await self._identify_risks(profile, market_data),
                "timestamp": utc_now().isoformat(),
            }
            return insights
        except Exception as e:
            logger.error(f"Error providing market insights: {str(e)}", exc_info=True)
            return {"error": str(e)}

    async def _assess_emergency_fund(
        self, profile: UserProfile
    ) -> Optional[FinancialAdvice]:
        """Assess emergency fund adequacy"""
        try:
            monthly_expenses = profile.income * 0.7
            recommended_months = 6 if profile.investment_experience == "beginner" else 3
            current_emergency_fund = profile.emergency_fund_months * monthly_expenses
            recommended_emergency_fund = recommended_months * monthly_expenses
            if current_emergency_fund < recommended_emergency_fund:
                shortfall = recommended_emergency_fund - current_emergency_fund
                return FinancialAdvice(
                    user_id=profile.user_id,
                    advice_type="emergency_fund",
                    title="Emergency Fund Assessment",
                    description=f"Your emergency fund should cover {recommended_months} months of expenses (${recommended_emergency_fund:,.2f}). You currently have ${current_emergency_fund:,.2f}.",
                    recommended_actions=[
                        f"Build emergency fund by ${shortfall:,.2f}",
                        "Consider high-yield savings account",
                        "Automate monthly contributions",
                        "Prioritize emergency fund before investing",
                    ],
                    expected_outcomes={
                        "financial_security": "Improved",
                        "stress_reduction": "Significant",
                        "investment_readiness": "Enhanced",
                    },
                    risk_assessment="Low risk, high importance",
                    confidence_score=0.9,
                    supporting_data={
                        "current_fund": current_emergency_fund,
                        "recommended_fund": recommended_emergency_fund,
                        "shortfall": shortfall,
                    },
                    implementation_steps=[
                        "Open high-yield savings account",
                        "Set up automatic transfer",
                        "Review and adjust monthly budget",
                        "Track progress monthly",
                    ],
                    monitoring_metrics=["Emergency fund balance", "Months of coverage"],
                    timestamp=utc_now(),
                )
            return None
        except Exception as e:
            logger.error(f"Error assessing emergency fund: {str(e)}")
            return None

    async def _assess_debt_management(
        self, profile: UserProfile
    ) -> Optional[FinancialAdvice]:
        """Assess debt management strategy"""
        try:
            debt_to_income_ratio = profile.debt_obligations / profile.income
            if debt_to_income_ratio > 0.4:
                return FinancialAdvice(
                    user_id=profile.user_id,
                    advice_type="debt_management",
                    title="Debt Management Priority",
                    description=f"Your debt-to-income ratio is {debt_to_income_ratio:.1%}, which is above the recommended 40% threshold.",
                    recommended_actions=[
                        "Focus on high-interest debt first",
                        "Consider debt consolidation",
                        "Create aggressive payoff plan",
                        "Limit new debt accumulation",
                    ],
                    expected_outcomes={
                        "monthly_cash_flow": "Improved",
                        "credit_score": "Enhanced",
                        "investment_capacity": "Increased",
                    },
                    risk_assessment="High priority for financial health",
                    confidence_score=0.85,
                    supporting_data={
                        "debt_to_income_ratio": debt_to_income_ratio,
                        "total_debt": profile.debt_obligations,
                        "annual_income": profile.income,
                    },
                    implementation_steps=[
                        "List all debts with interest rates",
                        "Choose debt payoff strategy",
                        "Negotiate with creditors if needed",
                        "Track progress monthly",
                    ],
                    monitoring_metrics=[
                        "Debt balance",
                        "Debt-to-income ratio",
                        "Credit score",
                    ],
                    timestamp=utc_now(),
                )
            return None
        except Exception as e:
            logger.error(f"Error assessing debt management: {str(e)}")
            return None

    async def _generate_investment_advice(
        self, profile: UserProfile
    ) -> Optional[FinancialAdvice]:
        """Generate investment advice"""
        try:
            investment_readiness = self._calculate_investment_readiness(profile)
            if investment_readiness < 0.6:
                return FinancialAdvice(
                    user_id=profile.user_id,
                    advice_type="investment_readiness",
                    title="Investment Readiness Assessment",
                    description="Focus on building financial foundation before aggressive investing.",
                    recommended_actions=[
                        "Build emergency fund first",
                        "Pay down high-interest debt",
                        "Start with conservative investments",
                        "Increase financial education",
                    ],
                    expected_outcomes={
                        "financial_stability": "Improved",
                        "investment_success": "Higher probability",
                    },
                    risk_assessment="Foundation building phase",
                    confidence_score=0.8,
                    supporting_data={
                        "investment_readiness_score": investment_readiness
                    },
                    implementation_steps=[
                        "Complete emergency fund",
                        "Address debt obligations",
                        "Start with index funds",
                        "Gradually increase allocation",
                    ],
                    monitoring_metrics=[
                        "Emergency fund",
                        "Debt levels",
                        "Investment balance",
                    ],
                    timestamp=utc_now(),
                )
            strategy = await self._determine_investment_strategy(profile)
            return FinancialAdvice(
                user_id=profile.user_id,
                advice_type="investment_strategy",
                title=f"{strategy['name']} Investment Strategy",
                description=strategy["description"],
                recommended_actions=strategy["actions"],
                expected_outcomes=strategy["outcomes"],
                risk_assessment=strategy["risk_assessment"],
                confidence_score=0.75,
                supporting_data=strategy["supporting_data"],
                implementation_steps=strategy["implementation_steps"],
                monitoring_metrics=strategy["monitoring_metrics"],
                timestamp=utc_now(),
            )
        except Exception as e:
            logger.error(f"Error generating investment advice: {str(e)}")
            return None

    async def _generate_tax_advice(
        self, profile: UserProfile
    ) -> Optional[FinancialAdvice]:
        """Generate tax optimization advice"""
        try:
            tax_strategies = []
            if profile.income > 50000:
                max_401k = 22500
                recommended_contribution = min(profile.income * 0.15, max_401k)
                tax_strategies.append(
                    f"Maximize 401(k) contribution: ${recommended_contribution:,.0f}"
                )
            if profile.income < 138000:
                tax_strategies.append("Consider Roth IRA contribution: $6,500")
            if profile.current_portfolio:
                tax_strategies.append("Implement tax-loss harvesting strategy")
            if tax_strategies:
                return FinancialAdvice(
                    user_id=profile.user_id,
                    advice_type="tax_optimization",
                    title="Tax Optimization Strategies",
                    description="Optimize your tax situation through strategic planning.",
                    recommended_actions=tax_strategies,
                    expected_outcomes={
                        "tax_savings": f"${profile.income * profile.tax_bracket * 0.1:,.0f} annually",
                        "retirement_savings": "Accelerated",
                    },
                    risk_assessment="Low risk, high benefit",
                    confidence_score=0.8,
                    supporting_data={
                        "current_tax_bracket": profile.tax_bracket,
                        "estimated_savings": profile.income * profile.tax_bracket * 0.1,
                    },
                    implementation_steps=[
                        "Review employer 401(k) plan",
                        "Open appropriate IRA account",
                        "Set up automatic contributions",
                        "Consult tax professional",
                    ],
                    monitoring_metrics=[
                        "Tax savings",
                        "Retirement contributions",
                        "Effective tax rate",
                    ],
                    timestamp=utc_now(),
                )
            return None
        except Exception as e:
            logger.error(f"Error generating tax advice: {str(e)}")
            return None

    async def _generate_goal_specific_advice(
        self, profile: UserProfile, goal: InvestmentGoal
    ) -> Optional[FinancialAdvice]:
        """Generate advice for specific investment goals"""
        try:
            if goal == InvestmentGoal.RETIREMENT:
                return await self._generate_retirement_advice(profile)
            elif goal == InvestmentGoal.EDUCATION:
                return await self._generate_education_advice(profile)
            elif goal == InvestmentGoal.HOME_PURCHASE:
                return await self._generate_home_purchase_advice(profile)
            else:
                return await self._generate_general_goal_advice(profile, goal)
        except Exception as e:
            logger.error(f"Error generating goal-specific advice: {str(e)}")
            return None

    async def _generate_retirement_advice(
        self, profile: UserProfile
    ) -> FinancialAdvice:
        """Generate retirement planning advice"""
        retirement_age = 65
        years_to_retirement = retirement_age - profile.age
        annual_need = profile.income * self.config["retirement_replacement_ratio"]
        total_need = annual_need * 25
        if years_to_retirement > 0:
            monthly_savings_needed = self._calculate_monthly_savings(
                total_need, years_to_retirement, 0.07
            )
        else:
            monthly_savings_needed = 0
        return FinancialAdvice(
            user_id=profile.user_id,
            advice_type="retirement_planning",
            title="Retirement Planning Strategy",
            description=f"You need approximately ${total_need:,.0f} for retirement in {years_to_retirement} years.",
            recommended_actions=[
                f"Save ${monthly_savings_needed:,.0f} monthly for retirement",
                "Maximize employer 401(k) match",
                "Consider Roth IRA for tax diversification",
                "Review and adjust annually",
            ],
            expected_outcomes={
                "retirement_readiness": "On track",
                "financial_independence": f"Age {retirement_age}",
            },
            risk_assessment="Long-term planning essential",
            confidence_score=0.8,
            supporting_data={
                "retirement_need": total_need,
                "years_to_retirement": years_to_retirement,
                "monthly_savings_needed": monthly_savings_needed,
            },
            implementation_steps=[
                "Increase 401(k) contribution",
                "Open IRA account",
                "Automate retirement savings",
                "Review investment allocation",
            ],
            monitoring_metrics=[
                "Retirement balance",
                "Savings rate",
                "Investment returns",
            ],
            timestamp=utc_now(),
        )

    def _determine_allocation_strategy(self, profile: UserProfile) -> str:
        """Determine appropriate asset allocation strategy"""
        if profile.age < 30 and profile.risk_tolerance in [
            RiskTolerance.AGGRESSIVE,
            RiskTolerance.VERY_AGGRESSIVE,
        ]:
            return "aggressive_growth"
        elif profile.age < 50 and profile.risk_tolerance == RiskTolerance.MODERATE:
            return "balanced_growth"
        elif profile.age >= 50 or profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            return "conservative_income"
        else:
            return "target_date"

    async def _calculate_target_allocation(
        self, profile: UserProfile, strategy: str
    ) -> Dict[str, float]:
        """Calculate target asset allocation"""
        if strategy == "aggressive_growth":
            return {"stocks": 0.8, "international_stocks": 0.15, "bonds": 0.05}
        elif strategy == "balanced_growth":
            return {
                "stocks": 0.6,
                "international_stocks": 0.2,
                "bonds": 0.15,
                "reits": 0.05,
            }
        elif strategy == "conservative_income":
            return {
                "stocks": 0.3,
                "bonds": 0.5,
                "international_stocks": 0.1,
                "cash": 0.1,
            }
        else:
            stock_allocation = max(0.2, 1.0 - (profile.age - 20) / 100)
            bond_allocation = 1.0 - stock_allocation
            return {
                "stocks": stock_allocation * 0.7,
                "international_stocks": stock_allocation * 0.3,
                "bonds": bond_allocation,
            }

    async def _recommend_specific_assets(
        self, profile: UserProfile, allocation: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Recommend specific assets for allocation"""
        recommendations = []
        asset_mapping = {
            "stocks": [
                {
                    "symbol": "VTI",
                    "name": "Total Stock Market ETF",
                    "expense_ratio": 0.03,
                },
                {"symbol": "VOO", "name": "S&P 500 ETF", "expense_ratio": 0.03},
            ],
            "international_stocks": [
                {
                    "symbol": "VXUS",
                    "name": "Total International Stock ETF",
                    "expense_ratio": 0.08,
                },
                {
                    "symbol": "VTIAX",
                    "name": "Total International Stock Index",
                    "expense_ratio": 0.11,
                },
            ],
            "bonds": [
                {
                    "symbol": "BND",
                    "name": "Total Bond Market ETF",
                    "expense_ratio": 0.03,
                },
                {
                    "symbol": "AGG",
                    "name": "Core Aggregate Bond ETF",
                    "expense_ratio": 0.03,
                },
            ],
            "reits": [
                {"symbol": "VNQ", "name": "Real Estate ETF", "expense_ratio": 0.12}
            ],
            "cash": [
                {"symbol": "VMFXX", "name": "Money Market Fund", "expense_ratio": 0.11}
            ],
        }
        for asset_class, weight in allocation.items():
            if weight > 0 and asset_class in asset_mapping:
                asset = asset_mapping[asset_class][0].copy()
                asset["allocation"] = weight
                asset["asset_class"] = asset_class
                recommendations.append(asset)
        return recommendations

    async def _generate_allocation_rationale(
        self, profile: UserProfile, allocation: Dict[str, float]
    ) -> str:
        """Generate AI-powered rationale for allocation"""
        try:
            prompt = f"\n            Generate a clear, professional rationale for the following investment allocation for a {profile.age}-year-old investor:\n\n            Investor Profile:\n            - Age: {profile.age}\n            - Risk Tolerance: {profile.risk_tolerance.value}\n            - Investment Horizon: {profile.investment_horizon.value}\n            - Investment Experience: {profile.investment_experience}\n            - Goals: {[goal.value for goal in profile.investment_goals]}\n\n            Recommended Allocation:\n            {allocation}\n\n            Explain why this allocation is appropriate for this investor in 2-3 paragraphs.\n            "
            response = self.openai_client.chat.completions.create(
                model=self.config["openai_model"],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional financial advisor providing clear, educational explanations for investment recommendations.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating allocation rationale: {str(e)}")
            return "This allocation is designed to balance growth potential with risk management based on your profile."

    def _calculate_investment_readiness(self, profile: UserProfile) -> float:
        """Calculate investment readiness score"""
        score = 0.0
        if profile.emergency_fund_months >= 3:
            score += 0.3
        elif profile.emergency_fund_months >= 1:
            score += 0.15
        debt_ratio = profile.debt_obligations / profile.income
        if debt_ratio < 0.2:
            score += 0.3
        elif debt_ratio < 0.4:
            score += 0.15
        score += 0.2
        if profile.monthly_investment_capacity > profile.income * 0.1:
            score += 0.2
        elif profile.monthly_investment_capacity > 0:
            score += 0.1
        return min(score, 1.0)

    async def _determine_investment_strategy(
        self, profile: UserProfile
    ) -> Dict[str, Any]:
        """Determine investment strategy based on profile"""
        if profile.risk_tolerance == RiskTolerance.AGGRESSIVE:
            return {
                "name": "Growth-Focused",
                "description": "Emphasis on long-term capital appreciation through equity investments.",
                "actions": [
                    "Allocate 80-90% to stock investments",
                    "Focus on low-cost index funds",
                    "Consider international diversification",
                    "Minimize bond allocation",
                ],
                "outcomes": {
                    "expected_return": "8-10% annually",
                    "volatility": "High",
                    "time_horizon": "Long-term",
                },
                "risk_assessment": "High volatility, high growth potential",
                "supporting_data": {
                    "risk_tolerance": profile.risk_tolerance.value,
                    "age": profile.age,
                    "investment_horizon": profile.investment_horizon.value,
                },
                "implementation_steps": [
                    "Open brokerage account",
                    "Set up automatic investing",
                    "Choose broad market index funds",
                    "Review quarterly",
                ],
                "monitoring_metrics": [
                    "Portfolio value",
                    "Asset allocation",
                    "Rebalancing needs",
                ],
            }
        else:
            return {
                "name": "Balanced",
                "description": "Balanced approach between growth and stability.",
                "actions": [
                    "Maintain 60/40 stock/bond allocation",
                    "Use diversified index funds",
                    "Include international exposure",
                    "Rebalance annually",
                ],
                "outcomes": {
                    "expected_return": "6-8% annually",
                    "volatility": "Moderate",
                    "time_horizon": "Medium to long-term",
                },
                "risk_assessment": "Moderate risk, steady growth",
                "supporting_data": {
                    "risk_tolerance": profile.risk_tolerance.value,
                    "age": profile.age,
                },
                "implementation_steps": [
                    "Open investment account",
                    "Choose target-date fund or build portfolio",
                    "Automate contributions",
                    "Monitor and rebalance",
                ],
                "monitoring_metrics": [
                    "Portfolio balance",
                    "Risk level",
                    "Performance vs benchmark",
                ],
            }

    def _calculate_monthly_savings(
        self, future_value: float, years: int, annual_return: float
    ) -> float:
        """Calculate required monthly savings for future value"""
        if years <= 0:
            return future_value
        monthly_rate = annual_return / 12
        months = years * 12
        if monthly_rate == 0:
            return future_value / months
        return future_value * monthly_rate / ((1 + monthly_rate) ** months - 1)

    async def _calculate_portfolio_metrics(
        self, allocation: Dict[str, float], assets: List[Dict[str, Any]]
    ) -> Tuple[float, float]:
        """Calculate expected portfolio return and volatility"""
        try:
            expected_returns = {
                "stocks": 0.1,
                "international_stocks": 0.08,
                "bonds": 0.04,
                "reits": 0.09,
                "cash": 0.02,
            }
            volatilities = {
                "stocks": 0.16,
                "international_stocks": 0.18,
                "bonds": 0.04,
                "reits": 0.2,
                "cash": 0.01,
            }
            portfolio_return = sum(
                (
                    allocation.get(asset_class, 0)
                    * expected_returns.get(asset_class, 0.06)
                    for asset_class in allocation.keys()
                )
            )
            portfolio_volatility = (
                sum(
                    (
                        allocation.get(asset_class, 0)
                        * volatilities.get(asset_class, 0.1)
                        for asset_class in allocation.keys()
                    )
                )
                * 0.8
            )
            return (portfolio_return, portfolio_volatility)
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {str(e)}")
            return (0.07, 0.12)

    def _calculate_implementation_cost(
        self, current_portfolio: Dict[str, float], target_allocation: Dict[str, float]
    ) -> float:
        """Calculate cost of implementing new allocation"""
        total_changes = sum(
            (
                abs(target_allocation.get(asset, 0) - current_portfolio.get(asset, 0))
                for asset in set(
                    list(current_portfolio.keys()) + list(target_allocation.keys())
                )
            )
        )
        return total_changes * 0.001

    def _assess_tax_implications(
        self, profile: UserProfile, allocation: Dict[str, float]
    ) -> Dict[str, Any]:
        """Assess tax implications of allocation"""
        return {
            "tax_efficiency": (
                "High"
                if "bonds" in allocation and allocation["bonds"] < 0.3
                else "Medium"
            ),
            "recommended_accounts": {
                "taxable": ["stocks", "international_stocks"],
                "tax_deferred": ["bonds"],
                "tax_free": ["reits"],
            },
            "estimated_tax_drag": allocation.get("bonds", 0) * 0.02,
        }

    def _determine_rebalancing_strategy(self, profile: UserProfile) -> str:
        """Determine appropriate rebalancing strategy"""
        if profile.investment_experience == "beginner":
            return "Annual rebalancing with 5% threshold"
        elif profile.monthly_investment_capacity > 1000:
            return "Quarterly rebalancing with new contributions"
        else:
            return "Semi-annual rebalancing or 10% threshold"

    async def _get_relevant_market_data(self, profile: UserProfile) -> Dict[str, Any]:
        """Get market data relevant to user's profile"""
        try:
            market_data = {}
            for symbol in self.config["benchmark_symbols"]:
                prices = await self.market_data.get_historical_prices(symbol, days=30)
                if prices:
                    market_data[symbol] = prices
            sector_performance = await self.market_data.get_sector_performance()
            market_data["sectors"] = sector_performance
            economic_indicators = await self.market_data.get_economic_indicators()
            market_data["economic_indicators"] = economic_indicators
            return market_data
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            return {}

    async def _generate_market_outlook(self, market_data: Dict[str, Any]) -> str:
        """Generate market outlook using AI"""
        try:
            prompt = f"\n            Based on the following market data, provide a brief market outlook (2-3 sentences):\n\n            Recent Performance:\n            - Economic Indicators: {market_data.get('economic_indicators', {})}\n            - Sector Performance: {market_data.get('sectors', [])}\n\n            Focus on key trends and implications for long-term investors.\n            "
            response = self.openai_client.chat.completions.create(
                model=self.config["openai_model"],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial analyst providing concise market insights.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating market outlook: {str(e)}")
            return "Market conditions remain dynamic. Maintain a long-term perspective and stay diversified."

    async def _analyze_sectors(self, profile: UserProfile) -> Dict[str, Any]:
        """Analyze sector opportunities and risks"""
        try:
            sector_data = await self.market_data.get_sector_performance()
            if sector_data:
                top_performers = sorted(
                    sector_data, key=lambda x: x.get("change_percent", 0), reverse=True
                )[:3]
                underperformers = sorted(
                    sector_data, key=lambda x: x.get("change_percent", 0)
                )[:3]
                return {
                    "top_performers": top_performers,
                    "underperformers": underperformers,
                    "recommendation": "Consider rebalancing if sector concentration is high",
                }
            return {"message": "Sector data not available"}
        except Exception as e:
            logger.error(f"Error analyzing sectors: {str(e)}")
            return {"error": str(e)}

    async def _assess_economic_indicators(self, profile: UserProfile) -> Dict[str, Any]:
        """Assess impact of economic indicators"""
        try:
            await self.market_data.get_economic_indicators()
            assessment = {
                "inflation_impact": "Monitor bond allocation if inflation rises",
                "interest_rate_impact": "Rising rates may benefit value stocks",
                "volatility_impact": "High VIX suggests increased market uncertainty",
            }
            return assessment
        except Exception as e:
            logger.error(f"Error assessing economic indicators: {str(e)}")
            return {}

    async def _generate_ai_market_insights(
        self, profile: UserProfile, market_data: Dict[str, Any]
    ) -> str:
        """Generate personalized AI insights"""
        try:
            prompt = f"\n            Provide personalized market insights for an investor with the following profile:\n            - Age: {profile.age}\n            - Risk Tolerance: {profile.risk_tolerance.value}\n            - Investment Goals: {[goal.value for goal in profile.investment_goals]}\n            - Investment Horizon: {profile.investment_horizon.value}\n\n            Based on current market conditions, what should this investor focus on? (2-3 sentences)\n            "
            response = self.openai_client.chat.completions.create(
                model=self.config["openai_model"],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial advisor providing personalized insights.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.6,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return "Stay focused on your long-term goals and maintain a diversified portfolio."

    async def _identify_opportunities(
        self, profile: UserProfile, market_data: Dict[str, Any]
    ) -> List[str]:
        """Identify investment opportunities"""
        opportunities = []
        if profile.age < 40 and profile.risk_tolerance in [
            RiskTolerance.MODERATE,
            RiskTolerance.AGGRESSIVE,
        ]:
            opportunities.append("Consider increasing international equity allocation")
        if profile.investment_horizon == InvestmentHorizon.LONG_TERM:
            opportunities.append("Dollar-cost averaging into growth sectors")
        return opportunities

    async def _identify_risks(
        self, profile: UserProfile, market_data: Dict[str, Any]
    ) -> List[str]:
        """Identify potential risks"""
        risks = []
        if profile.current_portfolio:
            concentration_risk = (
                max(profile.current_portfolio.values())
                if profile.current_portfolio.values()
                else 0
            )
            if concentration_risk > 0.3:
                risks.append(
                    "High concentration in single asset - consider diversification"
                )
        if profile.emergency_fund_months < 3:
            risks.append(
                "Insufficient emergency fund may force early investment liquidation"
            )
        return risks

    async def _assess_risk_management(
        self, profile: UserProfile
    ) -> Optional[FinancialAdvice]:
        """Assess risk management needs"""
        try:
            risk_factors = []
            if profile.dependents > 0 and profile.income > 30000:
                risk_factors.append("Consider life insurance coverage")
            if profile.income > 50000:
                risk_factors.append("Evaluate disability insurance needs")
            if profile.net_worth > 100000:
                risk_factors.append("Review liability insurance coverage")
            if risk_factors:
                return FinancialAdvice(
                    user_id=profile.user_id,
                    advice_type="risk_management",
                    title="Risk Management Assessment",
                    description="Protect your financial plan with appropriate insurance coverage.",
                    recommended_actions=risk_factors,
                    expected_outcomes={
                        "financial_protection": "Enhanced",
                        "peace_of_mind": "Improved",
                    },
                    risk_assessment="Essential for financial security",
                    confidence_score=0.7,
                    supporting_data={
                        "dependents": profile.dependents,
                        "income": profile.income,
                        "net_worth": profile.net_worth,
                    },
                    implementation_steps=[
                        "Review current insurance coverage",
                        "Get quotes from multiple providers",
                        "Consider term life insurance",
                        "Evaluate employer benefits",
                    ],
                    monitoring_metrics=[
                        "Coverage amounts",
                        "Premium costs",
                        "Policy terms",
                    ],
                    timestamp=utc_now(),
                )
            return None
        except Exception as e:
            logger.error(f"Error assessing risk management: {str(e)}")
            return None

    async def _generate_education_advice(self, profile: UserProfile) -> FinancialAdvice:
        """Generate education funding advice"""
        years_to_education = 18 - min(
            [child_age for child_age in [10, 15]] if profile.dependents > 0 else [18]
        )
        education_cost = 100000
        monthly_savings = self._calculate_monthly_savings(
            education_cost, years_to_education, 0.06
        )
        return FinancialAdvice(
            user_id=profile.user_id,
            advice_type="education_planning",
            title="Education Funding Strategy",
            description=f"Plan for education costs of approximately ${education_cost:,.0f}.",
            recommended_actions=[
                f"Save ${monthly_savings:,.0f} monthly in 529 plan",
                "Take advantage of state tax deductions",
                "Consider age-based investment options",
                "Review and adjust annually",
            ],
            expected_outcomes={
                "education_funding": "On track",
                "tax_benefits": "Maximized",
            },
            risk_assessment="Education inflation risk",
            confidence_score=0.75,
            supporting_data={
                "education_cost": education_cost,
                "years_to_education": years_to_education,
                "monthly_savings": monthly_savings,
            },
            implementation_steps=[
                "Open 529 education savings plan",
                "Set up automatic contributions",
                "Choose appropriate investment option",
                "Monitor progress annually",
            ],
            monitoring_metrics=[
                "529 balance",
                "Investment performance",
                "Education cost inflation",
            ],
            timestamp=utc_now(),
        )

    async def _generate_home_purchase_advice(
        self, profile: UserProfile
    ) -> FinancialAdvice:
        """Generate home purchase advice"""
        home_price = profile.income * 3
        down_payment = home_price * self.config["home_down_payment_ratio"]
        return FinancialAdvice(
            user_id=profile.user_id,
            advice_type="home_purchase",
            title="Home Purchase Planning",
            description=f"Plan for home purchase with estimated price of ${home_price:,.0f}.",
            recommended_actions=[
                f"Save ${down_payment:,.0f} for down payment",
                "Maintain good credit score",
                "Keep housing costs under 28% of income",
                "Get pre-approved for mortgage",
            ],
            expected_outcomes={
                "homeownership": "Achievable",
                "financial_stability": "Maintained",
            },
            risk_assessment="Market timing and affordability risk",
            confidence_score=0.7,
            supporting_data={
                "estimated_home_price": home_price,
                "down_payment_needed": down_payment,
                "income_multiple": 3,
            },
            implementation_steps=[
                "Open high-yield savings for down payment",
                "Monitor credit score",
                "Research neighborhoods",
                "Connect with mortgage lender",
            ],
            monitoring_metrics=["Down payment savings", "Credit score", "Home prices"],
            timestamp=utc_now(),
        )

    async def _generate_general_goal_advice(
        self, profile: UserProfile, goal: InvestmentGoal
    ) -> FinancialAdvice:
        """Generate advice for general investment goals"""
        return FinancialAdvice(
            user_id=profile.user_id,
            advice_type=f"{goal.value}_planning",
            title=f"{goal.value.replace('_', ' ').title()} Strategy",
            description=f"Develop a strategy for your {goal.value.replace('_', ' ')} goal.",
            recommended_actions=[
                "Define specific target amount and timeline",
                "Choose appropriate investment vehicles",
                "Monitor progress regularly",
                "Adjust strategy as needed",
            ],
            expected_outcomes={
                "goal_achievement": "Improved probability",
                "financial_discipline": "Enhanced",
            },
            risk_assessment="Goal-specific risk assessment needed",
            confidence_score=0.6,
            supporting_data={"goal": goal.value},
            implementation_steps=[
                "Quantify goal requirements",
                "Create dedicated savings plan",
                "Choose suitable investments",
                "Track progress monthly",
            ],
            monitoring_metrics=[
                "Progress toward goal",
                "Investment performance",
                "Timeline adherence",
            ],
            timestamp=utc_now(),
        )
