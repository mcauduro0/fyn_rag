"""
Industry & Competitive Agent - Focuses on industry dynamics and competitive positioning.
Expertise: Porter's 5 Forces, SWOT, Competitive Landscape, Industry Trends.
"""

import logging
from typing import Dict, Any, List, Optional

from app.core.agents.base_agent import BaseAgent, AgentRole, AgentResponse

logger = logging.getLogger(__name__)


class IndustryCompetitiveAgent(BaseAgent):
    """
    Industry & Competitive Agent specializes in industry and competitive analysis.
    
    Core Frameworks:
    - Porter's Five Forces
    - SWOT Analysis
    - Competitive Positioning
    - Industry Life Cycle
    - Market Share Analysis
    - Barriers to Entry
    """
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(
            role=AgentRole.INDUSTRY_COMPETITIVE,
            name="Industry & Competitive Analyst",
            description="Expert in Porter's 5 Forces, SWOT, and competitive dynamics",
            llm_model=llm_model
        )
    
    async def analyze(
        self,
        task: str,
        context: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]] = None
    ) -> AgentResponse:
        """
        Perform industry and competitive analysis.
        
        Args:
            task: Analysis task
            context: Company and industry data
            rag_results: Relevant industry frameworks
            
        Returns:
            AgentResponse with industry analysis
        """
        logger.info(f"{self.name} analyzing: {task}")
        
        # Extract metrics
        metrics = self._extract_key_metrics(context)
        
        # Perform analyses
        porters_five = self._analyze_porters_five_forces(context)
        swot = self._perform_swot_analysis(context, metrics)
        competitive_position = self._analyze_competitive_position(context, metrics)
        industry_lifecycle = self._assess_industry_lifecycle(context)
        
        # Generate analysis
        analysis = self._generate_analysis(
            porters_five,
            swot,
            competitive_position,
            industry_lifecycle,
            metrics,
            rag_results
        )
        
        # Determine recommendation
        recommendation = self._determine_recommendation(
            porters_five,
            competitive_position,
            industry_lifecycle
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(context, metrics)
        
        # Identify concerns and opportunities
        concerns = self._identify_concerns(porters_five, swot, competitive_position)
        opportunities = self._identify_opportunities(swot, industry_lifecycle)
        
        response = AgentResponse(
            agent_role=self.role,
            analysis=analysis,
            recommendation=recommendation,
            confidence=confidence,
            supporting_data={
                "porters_five_forces": porters_five,
                "swot": swot,
                "competitive_position": competitive_position,
                "industry_lifecycle": industry_lifecycle
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
    
    def _analyze_porters_five_forces(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Porter's Five Forces.
        
        Args:
            context: Industry context
            
        Returns:
            Five Forces analysis
        """
        # Placeholder analysis - in production would use LLM + industry data
        
        forces = {
            "threat_of_new_entrants": {
                "level": "medium",
                "factors": ["Moderate capital requirements", "Established brand loyalty"]
            },
            "bargaining_power_of_suppliers": {
                "level": "low",
                "factors": ["Multiple supplier options", "Low switching costs"]
            },
            "bargaining_power_of_buyers": {
                "level": "medium",
                "factors": ["Price sensitivity", "Multiple alternatives"]
            },
            "threat_of_substitutes": {
                "level": "medium",
                "factors": ["Alternative solutions exist", "Technology disruption risk"]
            },
            "competitive_rivalry": {
                "level": "high",
                "factors": ["Numerous competitors", "Price competition"]
            }
        }
        
        # Calculate overall industry attractiveness
        high_count = sum(1 for f in forces.values() if f["level"] == "high")
        low_count = sum(1 for f in forces.values() if f["level"] == "low")
        
        if low_count >= 3:
            attractiveness = "high"
        elif high_count >= 3:
            attractiveness = "low"
        else:
            attractiveness = "medium"
        
        return {
            "forces": forces,
            "overall_attractiveness": attractiveness
        }
    
    def _perform_swot_analysis(
        self,
        context: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform SWOT analysis.
        
        Args:
            context: Company context
            metrics: Financial metrics
            
        Returns:
            SWOT analysis
        """
        # Placeholder SWOT - in production would use LLM + comprehensive data
        
        market_share = context.get("market_share", 0)
        brand_strength = context.get("brand_strength", "medium")
        
        swot = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }
        
        # Strengths
        if market_share > 20:
            swot["strengths"].append("Leading market position")
        if brand_strength == "high":
            swot["strengths"].append("Strong brand recognition")
        if metrics.get("operating_margin", 0) > 0.20:
            swot["strengths"].append("High operating margins")
        
        # Weaknesses
        if market_share < 5:
            swot["weaknesses"].append("Limited market share")
        if metrics.get("debt_to_equity", 0) > 2.0:
            swot["weaknesses"].append("High leverage")
        
        # Opportunities
        tam = context.get("tam", 0)
        if tam > 10_000_000_000:  # $10B+
            swot["opportunities"].append("Large addressable market")
        
        # Threats
        swot["threats"].append("Competitive pressure")
        swot["threats"].append("Technology disruption risk")
        
        return swot
    
    def _analyze_competitive_position(
        self,
        context: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze competitive positioning.
        
        Args:
            context: Company context
            metrics: Financial metrics
            
        Returns:
            Competitive position analysis
        """
        market_share = context.get("market_share", 0)
        market_share_trend = context.get("market_share_trend", "stable")
        
        # Determine position
        if market_share > 30:
            position = "leader"
        elif market_share > 15:
            position = "challenger"
        elif market_share > 5:
            position = "follower"
        else:
            position = "niche"
        
        # Assess competitive advantages
        advantages = []
        if context.get("brand_strength") == "high":
            advantages.append("Strong brand")
        if metrics.get("operating_margin", 0) > 0.25:
            advantages.append("Cost advantage")
        if context.get("innovation_score", 0) > 7:
            advantages.append("Innovation leadership")
        
        return {
            "position": position,
            "market_share": market_share,
            "trend": market_share_trend,
            "competitive_advantages": advantages
        }
    
    def _assess_industry_lifecycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess industry lifecycle stage.
        
        Args:
            context: Industry context
            
        Returns:
            Lifecycle assessment
        """
        industry_growth = context.get("industry_growth_rate", 0)
        
        # Determine lifecycle stage
        if industry_growth > 20:
            stage = "growth"
            characteristics = ["High growth", "New entrants", "Innovation focus"]
        elif industry_growth > 5:
            stage = "mature"
            characteristics = ["Stable growth", "Consolidation", "Efficiency focus"]
        elif industry_growth > 0:
            stage = "mature_late"
            characteristics = ["Slow growth", "Market saturation", "Cost competition"]
        else:
            stage = "decline"
            characteristics = ["Negative growth", "Exit of players", "Disruption"]
        
        return {
            "stage": stage,
            "growth_rate": industry_growth,
            "characteristics": characteristics
        }
    
    def _generate_analysis(
        self,
        porters_five: Dict[str, Any],
        swot: Dict[str, Any],
        competitive_position: Dict[str, Any],
        industry_lifecycle: Dict[str, Any],
        metrics: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Generate comprehensive industry analysis text."""
        
        parts = ["INDUSTRY & COMPETITIVE ANALYSIS\n"]
        
        # Industry Attractiveness
        parts.append(f"Industry Attractiveness: {porters_five['overall_attractiveness'].upper()}")
        parts.append(f"  Competitive Rivalry: {porters_five['forces']['competitive_rivalry']['level'].upper()}")
        parts.append(f"  Threat of New Entrants: {porters_five['forces']['threat_of_new_entrants']['level'].upper()}")
        parts.append(f"  Threat of Substitutes: {porters_five['forces']['threat_of_substitutes']['level'].upper()}")
        
        # Competitive Position
        parts.append(f"\nCompetitive Position: {competitive_position['position'].upper()}")
        parts.append(f"  Market Share: {competitive_position['market_share']:.1f}%")
        parts.append(f"  Trend: {competitive_position['trend'].upper()}")
        
        if competitive_position['competitive_advantages']:
            parts.append(f"  Advantages: {', '.join(competitive_position['competitive_advantages'])}")
        
        # Industry Lifecycle
        parts.append(f"\nIndustry Lifecycle: {industry_lifecycle['stage'].upper()}")
        parts.append(f"  Industry Growth: {industry_lifecycle['growth_rate']:.1f}%")
        
        # SWOT Summary
        parts.append(f"\nSWOT Summary:")
        parts.append(f"  Strengths: {len(swot['strengths'])}")
        parts.append(f"  Weaknesses: {len(swot['weaknesses'])}")
        parts.append(f"  Opportunities: {len(swot['opportunities'])}")
        parts.append(f"  Threats: {len(swot['threats'])}")
        
        # Framework Context
        if rag_results:
            parts.append(f"\nApplied {len(rag_results)} industry analysis frameworks")
        
        return "\n".join(parts)
    
    def _determine_recommendation(
        self,
        porters_five: Dict[str, Any],
        competitive_position: Dict[str, Any],
        industry_lifecycle: Dict[str, Any]
    ) -> str:
        """Determine industry-based recommendation."""
        
        # Strong buy: attractive industry + strong position + growth stage
        if (porters_five['overall_attractiveness'] == 'high' and
            competitive_position['position'] in ['leader', 'challenger'] and
            industry_lifecycle['stage'] == 'growth'):
            return "STRONG BUY"
        
        # Buy: good industry + decent position
        if (porters_five['overall_attractiveness'] in ['high', 'medium'] and
            competitive_position['position'] in ['leader', 'challenger']):
            return "BUY"
        
        # Hold: mixed signals
        if competitive_position['position'] in ['follower', 'niche']:
            return "HOLD"
        
        # Sell: unattractive industry or declining
        if (porters_five['overall_attractiveness'] == 'low' or
            industry_lifecycle['stage'] == 'decline'):
            return "SELL"
        
        return "HOLD"
    
    def _calculate_confidence(
        self,
        context: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> float:
        """Calculate confidence score."""
        
        confidence = 0.5
        
        # Increase with data availability
        if "market_share" in context:
            confidence += 0.15
        
        if "industry_growth_rate" in context:
            confidence += 0.15
        
        if "brand_strength" in context:
            confidence += 0.10
        
        if "operating_margin" in metrics:
            confidence += 0.10
        
        return min(confidence, 1.0)
    
    def _identify_concerns(
        self,
        porters_five: Dict[str, Any],
        swot: Dict[str, Any],
        competitive_position: Dict[str, Any]
    ) -> List[str]:
        """Identify industry concerns."""
        concerns = []
        
        if porters_five['overall_attractiveness'] == 'low':
            concerns.append("Unattractive industry structure limits profitability")
        
        if porters_five['forces']['competitive_rivalry']['level'] == 'high':
            concerns.append("Intense competitive rivalry pressures margins")
        
        if competitive_position['position'] in ['follower', 'niche']:
            concerns.append("Weak competitive position limits pricing power")
        
        if len(swot['threats']) > len(swot['opportunities']):
            concerns.append("Threats outweigh opportunities in SWOT analysis")
        
        return concerns
    
    def _identify_opportunities(
        self,
        swot: Dict[str, Any],
        industry_lifecycle: Dict[str, Any]
    ) -> List[str]:
        """Identify industry opportunities."""
        opportunities = []
        
        if industry_lifecycle['stage'] == 'growth':
            opportunities.append("Growing industry provides expansion tailwinds")
        
        # Add SWOT opportunities
        opportunities.extend(swot['opportunities'][:3])  # Top 3
        
        return opportunities
    
    def get_relevant_frameworks(self) -> List[str]:
        """Get relevant framework categories."""
        return [
            "Porter's Five Forces",
            "SWOT Analysis",
            "Competitive Positioning",
            "Industry Life Cycle",
            "Market Share Analysis",
            "Barriers to Entry"
        ]
