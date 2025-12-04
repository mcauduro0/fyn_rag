"""
Risk Management Agent - Focuses on downside protection and risk assessment.
Expertise: VaR, Stress Testing, Liquidity Risk, Concentration Risk.
"""

import logging
from typing import Dict, Any, List, Optional
import math

from app.core.agents.base_agent import BaseAgent, AgentRole, AgentResponse

logger = logging.getLogger(__name__)


class RiskManagementAgent(BaseAgent):
    """
    Risk Management Agent specializes in risk assessment and mitigation.
    
    Core Frameworks:
    - Value at Risk (VaR)
    - Stress Testing & Scenario Analysis
    - Liquidity Risk Assessment
    - Concentration Risk
    - Beta & Volatility Analysis
    - Downside Protection
    """
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(
            role=AgentRole.RISK_MANAGEMENT,
            name="Risk Management Analyst",
            description="Expert in risk assessment, VaR, and downside protection",
            llm_model=llm_model
        )
    
    async def analyze(
        self,
        task: str,
        context: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]] = None
    ) -> AgentResponse:
        """
        Perform risk management analysis.
        
        Args:
            task: Analysis task
            context: Company and market data
            rag_results: Relevant risk frameworks
            
        Returns:
            AgentResponse with risk analysis
        """
        logger.info(f"{self.name} analyzing: {task}")
        
        # Extract metrics
        metrics = self._extract_key_metrics(context)
        
        # Perform risk analyses
        volatility_analysis = self._analyze_volatility(metrics, context)
        liquidity_risk = self._assess_liquidity_risk(metrics)
        concentration_risk = self._assess_concentration_risk(context)
        stress_scenarios = self._run_stress_tests(metrics, context)
        
        # Generate analysis
        analysis = self._generate_analysis(
            volatility_analysis,
            liquidity_risk,
            concentration_risk,
            stress_scenarios,
            metrics,
            rag_results
        )
        
        # Determine recommendation
        recommendation = self._determine_recommendation(
            volatility_analysis,
            liquidity_risk,
            stress_scenarios
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(metrics, volatility_analysis)
        
        # Identify concerns and opportunities
        concerns = self._identify_concerns(
            volatility_analysis,
            liquidity_risk,
            concentration_risk,
            stress_scenarios
        )
        opportunities = self._identify_opportunities(volatility_analysis)
        
        response = AgentResponse(
            agent_role=self.role,
            analysis=analysis,
            recommendation=recommendation,
            confidence=confidence,
            supporting_data={
                "volatility": volatility_analysis,
                "liquidity_risk": liquidity_risk,
                "concentration_risk": concentration_risk,
                "stress_scenarios": stress_scenarios
            },
            frameworks_used=self.get_relevant_frameworks(),
            concerns=concerns,
            opportunities=opportunities
        )
        
        self.add_to_memory({
            "task": task,
            "recommendation": recommendation,
            "confidence": confidence
        })
        
        return response
    
    def _analyze_volatility(
        self,
        metrics: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze volatility and beta.
        
        Args:
            metrics: Financial metrics
            context: Market context
            
        Returns:
            Volatility analysis
        """
        beta = metrics.get("beta", 1.0)
        volatility = metrics.get("volatility", 0.25)  # 25% default
        sharpe_ratio = metrics.get("sharpe_ratio")
        
        # Calculate VaR (95% confidence, 1-day)
        # VaR = μ - (z * σ)
        expected_return = 0.10 / 252  # 10% annual / 252 trading days
        z_score = 1.65  # 95% confidence
        var_95 = expected_return - (z_score * volatility / math.sqrt(252))
        
        # Classify volatility
        if volatility < 0.15:
            vol_class = "low"
        elif volatility < 0.30:
            vol_class = "medium"
        else:
            vol_class = "high"
        
        # Classify beta
        if beta < 0.8:
            beta_class = "defensive"
        elif beta < 1.2:
            beta_class = "market"
        else:
            beta_class = "aggressive"
        
        logger.info(f"Volatility: {volatility:.2%} ({vol_class}), Beta: {beta:.2f} ({beta_class})")
        
        return {
            "volatility": volatility,
            "vol_class": vol_class,
            "beta": beta,
            "beta_class": beta_class,
            "var_95": var_95,
            "sharpe_ratio": sharpe_ratio
        }
    
    def _assess_liquidity_risk(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess liquidity risk.
        
        Args:
            metrics: Financial metrics
            
        Returns:
            Liquidity risk assessment
        """
        current_ratio = metrics.get("current_ratio")
        quick_ratio = metrics.get("quick_ratio")
        cash = metrics.get("cash", 0)
        debt = metrics.get("total_debt", 0)
        
        # Calculate cash-to-debt ratio
        cash_to_debt = (cash / debt) if debt > 0 else float('inf')
        
        # Assess liquidity health
        if current_ratio and current_ratio >= 2.0 and quick_ratio and quick_ratio >= 1.0:
            health = "strong"
        elif current_ratio and current_ratio >= 1.5:
            health = "adequate"
        elif current_ratio and current_ratio >= 1.0:
            health = "weak"
        else:
            health = "critical"
        
        return {
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "cash_to_debt": cash_to_debt,
            "health": health
        }
    
    def _assess_concentration_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess concentration risk.
        
        Args:
            context: Context information
            
        Returns:
            Concentration risk assessment
        """
        # Placeholder concentration analysis
        # In production, would analyze customer concentration, geographic concentration, etc.
        
        customer_concentration = context.get("top_10_customer_revenue_pct", 0)
        geographic_concentration = context.get("primary_market_revenue_pct", 0)
        
        # Assess concentration risk
        if customer_concentration > 50 or geographic_concentration > 70:
            risk_level = "high"
        elif customer_concentration > 30 or geographic_concentration > 50:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "customer_concentration": customer_concentration,
            "geographic_concentration": geographic_concentration,
            "risk_level": risk_level
        }
    
    def _run_stress_tests(
        self,
        metrics: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run stress test scenarios.
        
        Args:
            metrics: Financial metrics
            context: Market context
            
        Returns:
            Stress test results
        """
        current_price = metrics.get("current_price", 100)
        
        # Define stress scenarios
        scenarios = {
            "market_crash": {
                "description": "Market crash (-30%)",
                "price_impact": current_price * 0.70,
                "probability": "low"
            },
            "recession": {
                "description": "Economic recession (-20%)",
                "price_impact": current_price * 0.80,
                "probability": "medium"
            },
            "sector_downturn": {
                "description": "Sector-specific downturn (-15%)",
                "price_impact": current_price * 0.85,
                "probability": "medium"
            }
        }
        
        # Assess overall stress resilience
        beta = metrics.get("beta", 1.0)
        if beta < 0.8:
            resilience = "high"
        elif beta < 1.2:
            resilience = "medium"
        else:
            resilience = "low"
        
        return {
            "scenarios": scenarios,
            "resilience": resilience
        }
    
    def _generate_analysis(
        self,
        volatility_analysis: Dict[str, Any],
        liquidity_risk: Dict[str, Any],
        concentration_risk: Dict[str, Any],
        stress_scenarios: Dict[str, Any],
        metrics: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Generate comprehensive risk analysis text."""
        
        parts = ["RISK MANAGEMENT ANALYSIS\n"]
        
        # Volatility & Beta
        parts.append(f"Market Risk:")
        parts.append(f"  Volatility: {volatility_analysis['volatility']:.2%} ({volatility_analysis['vol_class'].upper()})")
        parts.append(f"  Beta: {volatility_analysis['beta']:.2f} ({volatility_analysis['beta_class'].upper()})")
        parts.append(f"  VaR (95%, 1-day): {volatility_analysis['var_95']:.2%}")
        
        if volatility_analysis.get('sharpe_ratio'):
            parts.append(f"  Sharpe Ratio: {volatility_analysis['sharpe_ratio']:.2f}")
        
        # Liquidity Risk
        parts.append(f"\nLiquidity Risk: {liquidity_risk['health'].upper()}")
        if liquidity_risk['current_ratio']:
            parts.append(f"  Current Ratio: {liquidity_risk['current_ratio']:.2f}")
        if liquidity_risk['quick_ratio']:
            parts.append(f"  Quick Ratio: {liquidity_risk['quick_ratio']:.2f}")
        
        # Concentration Risk
        parts.append(f"\nConcentration Risk: {concentration_risk['risk_level'].upper()}")
        if concentration_risk['customer_concentration'] > 0:
            parts.append(f"  Customer Concentration: {concentration_risk['customer_concentration']:.1f}%")
        
        # Stress Test Resilience
        parts.append(f"\nStress Test Resilience: {stress_scenarios['resilience'].upper()}")
        
        # Framework Context
        if rag_results:
            parts.append(f"\nApplied {len(rag_results)} risk management frameworks")
        
        return "\n".join(parts)
    
    def _determine_recommendation(
        self,
        volatility_analysis: Dict[str, Any],
        liquidity_risk: Dict[str, Any],
        stress_scenarios: Dict[str, Any]
    ) -> str:
        """Determine risk-adjusted recommendation."""
        
        # High risk = more conservative
        if (volatility_analysis['vol_class'] == 'high' or
            liquidity_risk['health'] in ['weak', 'critical'] or
            stress_scenarios['resilience'] == 'low'):
            return "SELL - High risk profile"
        
        # Medium risk
        if (volatility_analysis['vol_class'] == 'medium' and
            liquidity_risk['health'] == 'adequate'):
            return "HOLD - Moderate risk"
        
        # Low risk
        if (volatility_analysis['vol_class'] == 'low' and
            liquidity_risk['health'] == 'strong'):
            return "BUY - Favorable risk profile"
        
        return "HOLD - Risk assessment inconclusive"
    
    def _calculate_confidence(
        self,
        metrics: Dict[str, Any],
        volatility_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence score."""
        
        confidence = 0.5
        
        # Increase with data availability
        if "beta" in metrics:
            confidence += 0.15
        
        if "current_ratio" in metrics:
            confidence += 0.15
        
        if volatility_analysis.get('sharpe_ratio'):
            confidence += 0.10
        
        if "volatility" in metrics:
            confidence += 0.10
        
        return min(confidence, 1.0)
    
    def _identify_concerns(
        self,
        volatility_analysis: Dict[str, Any],
        liquidity_risk: Dict[str, Any],
        concentration_risk: Dict[str, Any],
        stress_scenarios: Dict[str, Any]
    ) -> List[str]:
        """Identify risk concerns."""
        concerns = []
        
        if volatility_analysis['vol_class'] == 'high':
            concerns.append("High volatility increases downside risk")
        
        if liquidity_risk['health'] in ['weak', 'critical']:
            concerns.append("Weak liquidity position threatens financial stability")
        
        if concentration_risk['risk_level'] == 'high':
            concerns.append("High concentration risk reduces diversification")
        
        if stress_scenarios['resilience'] == 'low':
            concerns.append("Low stress resilience in adverse scenarios")
        
        return concerns
    
    def _identify_opportunities(
        self,
        volatility_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify risk-related opportunities."""
        opportunities = []
        
        if volatility_analysis['beta_class'] == 'defensive':
            opportunities.append("Defensive characteristics provide downside protection")
        
        if volatility_analysis['vol_class'] == 'low':
            opportunities.append("Low volatility supports stable returns")
        
        return opportunities
    
    def get_relevant_frameworks(self) -> List[str]:
        """Get relevant framework categories."""
        return [
            "Value at Risk (VaR)",
            "Stress Testing",
            "Liquidity Analysis",
            "Beta Analysis",
            "Concentration Risk",
            "Downside Protection",
            "Risk-Adjusted Returns"
        ]
