"""
Growth & VC Agent - Focuses on growth metrics and venture capital frameworks.
Expertise: Rule of 40, TAM/SAM/SOM, Unit Economics, Growth Rates.
"""

import logging
from typing import Dict, Any, List, Optional

from app.core.agents.base_agent import BaseAgent, AgentRole, AgentResponse

logger = logging.getLogger(__name__)


class GrowthVCAgent(BaseAgent):
    """
    Growth & VC Agent specializes in growth company analysis.
    
    Core Frameworks:
    - Rule of 40 (SaaS)
    - TAM/SAM/SOM Analysis
    - Unit Economics (CAC, LTV)
    - Growth Rates & Cohort Analysis
    - Burn Rate & Runway
    - Network Effects
    """
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(
            role=AgentRole.GROWTH_VC,
            name="Growth & VC Analyst",
            description="Expert in growth metrics, unit economics, and VC frameworks",
            llm_model=llm_model
        )
    
    async def analyze(
        self,
        task: str,
        context: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]] = None
    ) -> AgentResponse:
        """
        Perform growth and VC analysis.
        
        Args:
            task: Analysis task
            context: Company and market data
            rag_results: Relevant growth frameworks
            
        Returns:
            AgentResponse with growth analysis
        """
        logger.info(f"{self.name} analyzing: {task}")
        
        # Extract metrics
        metrics = self._extract_key_metrics(context)
        
        # Perform growth analyses
        rule_of_40 = self._calculate_rule_of_40(metrics)
        tam_analysis = self._analyze_tam(context)
        unit_economics = self._analyze_unit_economics(metrics)
        growth_trajectory = self._analyze_growth_trajectory(metrics, context)
        
        # Generate analysis
        analysis = self._generate_analysis(
            rule_of_40,
            tam_analysis,
            unit_economics,
            growth_trajectory,
            metrics,
            rag_results
        )
        
        # Determine recommendation
        recommendation = self._determine_recommendation(
            rule_of_40,
            unit_economics,
            growth_trajectory
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(metrics, growth_trajectory)
        
        # Identify concerns and opportunities
        concerns = self._identify_concerns(rule_of_40, unit_economics, metrics)
        opportunities = self._identify_opportunities(tam_analysis, growth_trajectory)
        
        response = AgentResponse(
            agent_role=self.role,
            analysis=analysis,
            recommendation=recommendation,
            confidence=confidence,
            supporting_data={
                "rule_of_40": rule_of_40,
                "tam_analysis": tam_analysis,
                "unit_economics": unit_economics,
                "growth_rate": growth_trajectory.get("current_growth")
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
    
    def _calculate_rule_of_40(self, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Calculate Rule of 40 for SaaS companies.
        Rule of 40: Growth Rate + Profit Margin should be >= 40%
        
        Args:
            metrics: Financial metrics
            
        Returns:
            Rule of 40 analysis
        """
        growth_rate = metrics.get("revenue_growth_rate")
        profit_margin = metrics.get("ebitda_margin") or metrics.get("operating_margin")
        
        if growth_rate is None or profit_margin is None:
            return None
        
        rule_of_40_score = growth_rate + profit_margin
        
        # Determine health
        if rule_of_40_score >= 40:
            health = "excellent"
        elif rule_of_40_score >= 30:
            health = "good"
        elif rule_of_40_score >= 20:
            health = "fair"
        else:
            health = "poor"
        
        logger.info(f"Rule of 40: {rule_of_40_score:.1f}% ({health})")
        
        return {
            "score": rule_of_40_score,
            "growth_rate": growth_rate,
            "profit_margin": profit_margin,
            "health": health
        }
    
    def _analyze_tam(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Total Addressable Market.
        
        Args:
            context: Market context
            
        Returns:
            TAM analysis
        """
        # Placeholder TAM analysis
        # In production, would use market research data
        
        tam = context.get("tam", 100_000_000_000)  # $100B default
        sam = context.get("sam", tam * 0.3)  # 30% of TAM
        som = context.get("som", sam * 0.1)  # 10% of SAM
        
        current_revenue = context.get("revenue", 0)
        market_penetration = (current_revenue / som * 100) if som > 0 else 0
        
        return {
            "tam": tam,
            "sam": sam,
            "som": som,
            "current_revenue": current_revenue,
            "market_penetration": market_penetration,
            "runway_potential": "high" if market_penetration < 20 else "medium"
        }
    
    def _analyze_unit_economics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze unit economics (CAC, LTV, LTV/CAC ratio).
        
        Args:
            metrics: Financial metrics
            
        Returns:
            Unit economics analysis
        """
        cac = metrics.get("cac")  # Customer Acquisition Cost
        ltv = metrics.get("ltv")  # Lifetime Value
        
        if not cac or not ltv:
            return {
                "ltv_cac_ratio": None,
                "health": "unknown",
                "payback_period": None
            }
        
        ltv_cac_ratio = ltv / cac
        
        # Determine health
        if ltv_cac_ratio >= 3.0:
            health = "excellent"
        elif ltv_cac_ratio >= 2.0:
            health = "good"
        elif ltv_cac_ratio >= 1.0:
            health = "fair"
        else:
            health = "poor"
        
        # Estimate payback period (months)
        monthly_revenue_per_customer = metrics.get("arpu", 0)
        payback_period = (cac / monthly_revenue_per_customer) if monthly_revenue_per_customer > 0 else None
        
        return {
            "cac": cac,
            "ltv": ltv,
            "ltv_cac_ratio": ltv_cac_ratio,
            "health": health,
            "payback_period": payback_period
        }
    
    def _analyze_growth_trajectory(
        self,
        metrics: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze growth trajectory and sustainability.
        
        Args:
            metrics: Financial metrics
            context: Additional context
            
        Returns:
            Growth trajectory analysis
        """
        current_growth = metrics.get("revenue_growth_rate", 0)
        historical_growth = context.get("historical_growth_rates", [])
        
        # Determine trend
        if len(historical_growth) >= 3:
            recent_avg = sum(historical_growth[-3:]) / 3
            if current_growth > recent_avg * 1.1:
                trend = "accelerating"
            elif current_growth < recent_avg * 0.9:
                trend = "decelerating"
            else:
                trend = "stable"
        else:
            trend = "unknown"
        
        # Assess sustainability
        if current_growth > 100:
            sustainability = "high_risk"  # Very high growth hard to sustain
        elif current_growth > 50:
            sustainability = "medium"
        elif current_growth > 20:
            sustainability = "sustainable"
        else:
            sustainability = "mature"
        
        return {
            "current_growth": current_growth,
            "trend": trend,
            "sustainability": sustainability,
            "historical_growth": historical_growth
        }
    
    def _generate_analysis(
        self,
        rule_of_40: Optional[Dict[str, Any]],
        tam_analysis: Dict[str, Any],
        unit_economics: Dict[str, Any],
        growth_trajectory: Dict[str, Any],
        metrics: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Generate comprehensive growth analysis text."""
        
        parts = ["GROWTH & VC ANALYSIS\n"]
        
        # Rule of 40
        if rule_of_40:
            parts.append(f"Rule of 40 Score: {rule_of_40['score']:.1f}% ({rule_of_40['health'].upper()})")
            parts.append(f"  Growth Rate: {rule_of_40['growth_rate']:.1f}%")
            parts.append(f"  Profit Margin: {rule_of_40['profit_margin']:.1f}%")
            
            if rule_of_40['health'] in ['excellent', 'good']:
                parts.append("  ✓ Strong SaaS metrics")
            else:
                parts.append("  ⚠ Below Rule of 40 threshold")
        
        # TAM Analysis
        parts.append(f"\nMarket Opportunity:")
        parts.append(f"  TAM: ${tam_analysis['tam']/1e9:.1f}B")
        parts.append(f"  Market Penetration: {tam_analysis['market_penetration']:.2f}%")
        parts.append(f"  Runway Potential: {tam_analysis['runway_potential'].upper()}")
        
        # Unit Economics
        if unit_economics['ltv_cac_ratio']:
            parts.append(f"\nUnit Economics:")
            parts.append(f"  LTV/CAC Ratio: {unit_economics['ltv_cac_ratio']:.2f}x ({unit_economics['health'].upper()})")
            if unit_economics['payback_period']:
                parts.append(f"  CAC Payback: {unit_economics['payback_period']:.1f} months")
        
        # Growth Trajectory
        parts.append(f"\nGrowth Trajectory:")
        parts.append(f"  Current Growth: {growth_trajectory['current_growth']:.1f}%")
        parts.append(f"  Trend: {growth_trajectory['trend'].upper()}")
        parts.append(f"  Sustainability: {growth_trajectory['sustainability'].upper()}")
        
        # Framework Context
        if rag_results:
            parts.append(f"\nApplied {len(rag_results)} growth frameworks")
        
        return "\n".join(parts)
    
    def _determine_recommendation(
        self,
        rule_of_40: Optional[Dict[str, Any]],
        unit_economics: Dict[str, Any],
        growth_trajectory: Dict[str, Any]
    ) -> str:
        """Determine investment recommendation."""
        
        # Strong buy: excellent metrics across the board
        if (rule_of_40 and rule_of_40['health'] == 'excellent' and
            unit_economics['health'] in ['excellent', 'good'] and
            growth_trajectory['current_growth'] > 30):
            return "STRONG BUY"
        
        # Buy: good growth with solid unit economics
        if (growth_trajectory['current_growth'] > 20 and
            unit_economics.get('ltv_cac_ratio', 0) >= 2.0):
            return "BUY"
        
        # Hold: moderate growth
        if growth_trajectory['current_growth'] > 10:
            return "HOLD"
        
        # Sell: poor metrics
        if (growth_trajectory['current_growth'] < 5 or
            unit_economics.get('ltv_cac_ratio', 0) < 1.0):
            return "SELL"
        
        return "HOLD"
    
    def _calculate_confidence(
        self,
        metrics: Dict[str, Any],
        growth_trajectory: Dict[str, Any]
    ) -> float:
        """Calculate confidence score."""
        
        confidence = 0.5
        
        # Increase with data availability
        if "revenue_growth_rate" in metrics:
            confidence += 0.15
        
        if "cac" in metrics and "ltv" in metrics:
            confidence += 0.15
        
        if growth_trajectory['trend'] != "unknown":
            confidence += 0.10
        
        if len(growth_trajectory.get('historical_growth', [])) >= 3:
            confidence += 0.10
        
        return min(confidence, 1.0)
    
    def _identify_concerns(
        self,
        rule_of_40: Optional[Dict[str, Any]],
        unit_economics: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Identify growth concerns."""
        concerns = []
        
        if rule_of_40 and rule_of_40['health'] == 'poor':
            concerns.append("Rule of 40 score below 20% indicates weak SaaS metrics")
        
        if unit_economics.get('ltv_cac_ratio', 0) < 1.5:
            concerns.append("Low LTV/CAC ratio suggests inefficient customer acquisition")
        
        if metrics.get("burn_rate", 0) > metrics.get("cash", 0) / 12:
            concerns.append("High burn rate relative to cash reserves")
        
        return concerns
    
    def _identify_opportunities(
        self,
        tam_analysis: Dict[str, Any],
        growth_trajectory: Dict[str, Any]
    ) -> List[str]:
        """Identify growth opportunities."""
        opportunities = []
        
        if tam_analysis['market_penetration'] < 10:
            opportunities.append("Low market penetration provides significant expansion potential")
        
        if growth_trajectory['trend'] == "accelerating":
            opportunities.append("Accelerating growth indicates strong product-market fit")
        
        if tam_analysis['runway_potential'] == "high":
            opportunities.append("Large addressable market supports long-term growth")
        
        return opportunities
    
    def get_relevant_frameworks(self) -> List[str]:
        """Get relevant framework categories."""
        return [
            "Rule of 40",
            "TAM/SAM/SOM Analysis",
            "Unit Economics",
            "CAC/LTV Analysis",
            "Growth Metrics",
            "Network Effects",
            "Cohort Analysis"
        ]
