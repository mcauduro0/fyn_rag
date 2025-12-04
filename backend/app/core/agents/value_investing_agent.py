"""
Value Investing Agent - Focuses on intrinsic value and margin of safety.
Expertise: DCF, Graham's principles, Buffett's moat analysis.
"""

import logging
from typing import Dict, Any, List, Optional

from app.core.agents.base_agent import BaseAgent, AgentRole, AgentResponse

logger = logging.getLogger(__name__)


class ValueInvestingAgent(BaseAgent):
    """
    Value Investing Agent specializes in fundamental value analysis.
    
    Core Frameworks:
    - Discounted Cash Flow (DCF)
    - Benjamin Graham's Value Principles
    - Warren Buffett's Moat Analysis
    - P/E, P/B, P/S Ratios
    - Free Cash Flow Analysis
    - Margin of Safety
    """
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(
            role=AgentRole.VALUE_INVESTING,
            name="Value Investing Analyst",
            description="Expert in intrinsic value, DCF, and margin of safety analysis",
            llm_model=llm_model
        )
    
    async def analyze(
        self,
        task: str,
        context: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]] = None
    ) -> AgentResponse:
        """
        Perform value investing analysis.
        
        Args:
            task: Analysis task
            context: Company and market data
            rag_results: Relevant value investing frameworks
            
        Returns:
            AgentResponse with value analysis
        """
        logger.info(f"{self.name} analyzing: {task}")
        
        # Extract key metrics
        metrics = self._extract_key_metrics(context)
        
        # Perform value analysis
        intrinsic_value = self._calculate_intrinsic_value(metrics, context)
        margin_of_safety = self._calculate_margin_of_safety(intrinsic_value, metrics)
        moat_analysis = self._analyze_moat(context, rag_results)
        
        # Generate analysis text
        analysis = self._generate_analysis(
            intrinsic_value,
            margin_of_safety,
            moat_analysis,
            metrics,
            rag_results
        )
        
        # Determine recommendation
        recommendation = self._determine_recommendation(
            margin_of_safety,
            moat_analysis
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            margin_of_safety,
            moat_analysis,
            metrics
        )
        
        # Identify concerns and opportunities
        concerns = self._identify_concerns(metrics, moat_analysis)
        opportunities = self._identify_opportunities(margin_of_safety, moat_analysis)
        
        response = AgentResponse(
            agent_role=self.role,
            analysis=analysis,
            recommendation=recommendation,
            confidence=confidence,
            supporting_data={
                "intrinsic_value": intrinsic_value,
                "margin_of_safety": margin_of_safety,
                "moat_strength": moat_analysis.get("strength", "unknown"),
                "key_metrics": metrics
            },
            frameworks_used=self.get_relevant_frameworks(),
            concerns=concerns,
            opportunities=opportunities
        )
        
        # Add to memory
        self.add_to_memory({
            "task": task,
            "recommendation": recommendation,
            "confidence": confidence
        })
        
        return response
    
    def _calculate_intrinsic_value(
        self,
        metrics: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[float]:
        """
        Calculate intrinsic value using DCF or other methods.
        
        Args:
            metrics: Key financial metrics
            context: Additional context
            
        Returns:
            Estimated intrinsic value per share
        """
        # Simplified DCF calculation
        fcf = metrics.get("free_cash_flow")
        shares = metrics.get("shares_outstanding")
        growth_rate = metrics.get("growth_rate", 0.05)
        discount_rate = 0.10  # 10% WACC assumption
        
        if not fcf or not shares:
            return None
        
        # 10-year DCF projection (simplified)
        terminal_value = fcf * (1 + growth_rate) / (discount_rate - growth_rate)
        present_value = terminal_value / ((1 + discount_rate) ** 10)
        
        intrinsic_value_per_share = present_value / shares
        
        logger.info(f"Calculated intrinsic value: ${intrinsic_value_per_share:.2f}")
        return intrinsic_value_per_share
    
    def _calculate_margin_of_safety(
        self,
        intrinsic_value: Optional[float],
        metrics: Dict[str, Any]
    ) -> Optional[float]:
        """
        Calculate margin of safety.
        
        Args:
            intrinsic_value: Calculated intrinsic value
            metrics: Current market metrics
            
        Returns:
            Margin of safety as percentage
        """
        current_price = metrics.get("current_price")
        
        if not intrinsic_value or not current_price:
            return None
        
        margin = (intrinsic_value - current_price) / intrinsic_value
        logger.info(f"Margin of safety: {margin:.2%}")
        return margin
    
    def _analyze_moat(
        self,
        context: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Analyze competitive moat strength.
        
        Args:
            context: Company context
            rag_results: RAG results about moat analysis
            
        Returns:
            Moat analysis results
        """
        # Placeholder moat analysis
        # In production, this would use LLM + RAG frameworks
        
        moat_factors = {
            "brand_strength": "medium",
            "switching_costs": "high",
            "network_effects": "low",
            "cost_advantages": "medium",
            "regulatory_barriers": "low"
        }
        
        # Determine overall moat strength
        high_count = sum(1 for v in moat_factors.values() if v == "high")
        
        if high_count >= 3:
            strength = "wide"
        elif high_count >= 1:
            strength = "narrow"
        else:
            strength = "none"
        
        return {
            "strength": strength,
            "factors": moat_factors,
            "sustainability": "medium"
        }
    
    def _generate_analysis(
        self,
        intrinsic_value: Optional[float],
        margin_of_safety: Optional[float],
        moat_analysis: Dict[str, Any],
        metrics: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Generate comprehensive value analysis text."""
        
        parts = ["VALUE INVESTING ANALYSIS\n"]
        
        # Intrinsic Value
        if intrinsic_value:
            current_price = metrics.get("current_price", 0)
            parts.append(f"Intrinsic Value: ${intrinsic_value:.2f} vs Current Price: ${current_price:.2f}")
            
            if margin_of_safety:
                parts.append(f"Margin of Safety: {margin_of_safety:.2%}")
                if margin_of_safety > 0.25:
                    parts.append("✓ Significant margin of safety provides downside protection")
                elif margin_of_safety > 0:
                    parts.append("⚠ Modest margin of safety")
                else:
                    parts.append("✗ Trading above intrinsic value")
        
        # Moat Analysis
        parts.append(f"\nCompetitive Moat: {moat_analysis['strength'].upper()}")
        parts.append(f"Sustainability: {moat_analysis['sustainability']}")
        
        # Valuation Metrics
        parts.append("\nValuation Metrics:")
        if "pe_ratio" in metrics:
            parts.append(f"  P/E Ratio: {metrics['pe_ratio']:.2f}")
        if "pb_ratio" in metrics:
            parts.append(f"  P/B Ratio: {metrics['pb_ratio']:.2f}")
        
        # Framework Context
        if rag_results:
            parts.append(f"\nApplied {len(rag_results)} value investing frameworks")
        
        return "\n".join(parts)
    
    def _determine_recommendation(
        self,
        margin_of_safety: Optional[float],
        moat_analysis: Dict[str, Any]
    ) -> str:
        """Determine buy/sell/hold recommendation."""
        
        if not margin_of_safety:
            return "HOLD - Insufficient data for valuation"
        
        moat_strength = moat_analysis.get("strength", "none")
        
        # Strong buy: high margin + wide moat
        if margin_of_safety > 0.30 and moat_strength == "wide":
            return "STRONG BUY"
        
        # Buy: good margin + any moat
        if margin_of_safety > 0.20:
            return "BUY"
        
        # Hold: modest margin
        if margin_of_safety > 0:
            return "HOLD"
        
        # Sell: overvalued
        if margin_of_safety < -0.20:
            return "SELL"
        
        return "HOLD"
    
    def _calculate_confidence(
        self,
        margin_of_safety: Optional[float],
        moat_analysis: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> float:
        """Calculate confidence score (0-1)."""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence with data availability
        if margin_of_safety is not None:
            confidence += 0.2
        
        if moat_analysis.get("strength") in ["wide", "narrow"]:
            confidence += 0.15
        
        if "pe_ratio" in metrics and "pb_ratio" in metrics:
            confidence += 0.15
        
        return min(confidence, 1.0)
    
    def _identify_concerns(
        self,
        metrics: Dict[str, Any],
        moat_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify investment concerns."""
        concerns = []
        
        if moat_analysis.get("strength") == "none":
            concerns.append("Weak competitive moat - vulnerable to competition")
        
        if metrics.get("pe_ratio", 0) > 40:
            concerns.append("High P/E ratio suggests expensive valuation")
        
        if metrics.get("debt_to_equity", 0) > 2.0:
            concerns.append("High leverage increases financial risk")
        
        return concerns
    
    def _identify_opportunities(
        self,
        margin_of_safety: Optional[float],
        moat_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify investment opportunities."""
        opportunities = []
        
        if margin_of_safety and margin_of_safety > 0.25:
            opportunities.append("Significant undervaluation provides upside potential")
        
        if moat_analysis.get("strength") == "wide":
            opportunities.append("Wide moat supports long-term value creation")
        
        return opportunities
    
    def get_relevant_frameworks(self) -> List[str]:
        """Get relevant framework categories."""
        return [
            "DCF Valuation",
            "Graham Value Principles",
            "Buffett Moat Analysis",
            "Free Cash Flow Analysis",
            "Margin of Safety",
            "Value Investing Metrics"
        ]
