"""
Financial Forensics Agent - Focuses on financial statement quality and red flags.
Expertise: Beneish M-Score, Altman Z-Score, Quality of Earnings, Accounting Red Flags.
"""

import logging
from typing import Dict, Any, List, Optional
import math

from app.core.agents.base_agent import BaseAgent, AgentRole, AgentResponse

logger = logging.getLogger(__name__)


class FinancialForensicsAgent(BaseAgent):
    """
    Financial Forensics Agent specializes in financial statement analysis and fraud detection.
    
    Core Frameworks:
    - Beneish M-Score (Earnings Manipulation)
    - Altman Z-Score (Bankruptcy Risk)
    - Quality of Earnings
    - Cash Flow Analysis
    - Accounting Red Flags
    - Revenue Recognition Quality
    """
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(
            role=AgentRole.FINANCIAL_FORENSICS,
            name="Financial Forensics Analyst",
            description="Expert in financial statement quality, M-Score, Z-Score, and red flags",
            llm_model=llm_model
        )
    
    async def analyze(
        self,
        task: str,
        context: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]] = None
    ) -> AgentResponse:
        """
        Perform financial forensics analysis.
        
        Args:
            task: Analysis task
            context: Financial statement data
            rag_results: Relevant forensics frameworks
            
        Returns:
            AgentResponse with forensics analysis
        """
        logger.info(f"{self.name} analyzing: {task}")
        
        # Extract metrics
        metrics = self._extract_key_metrics(context)
        
        # Perform forensics analyses
        beneish_score = self._calculate_beneish_m_score(metrics, context)
        altman_score = self._calculate_altman_z_score(metrics)
        quality_of_earnings = self._assess_quality_of_earnings(metrics)
        red_flags = self._identify_red_flags(metrics, context)
        
        # Generate analysis
        analysis = self._generate_analysis(
            beneish_score,
            altman_score,
            quality_of_earnings,
            red_flags,
            metrics,
            rag_results
        )
        
        # Determine recommendation
        recommendation = self._determine_recommendation(
            beneish_score,
            altman_score,
            quality_of_earnings,
            red_flags
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(metrics, beneish_score, altman_score)
        
        # Identify concerns and opportunities
        concerns = self._identify_concerns(beneish_score, altman_score, red_flags)
        opportunities = self._identify_opportunities(quality_of_earnings)
        
        response = AgentResponse(
            agent_role=self.role,
            analysis=analysis,
            recommendation=recommendation,
            confidence=confidence,
            supporting_data={
                "beneish_m_score": beneish_score,
                "altman_z_score": altman_score,
                "quality_of_earnings": quality_of_earnings,
                "red_flags": red_flags
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
    
    def _calculate_beneish_m_score(
        self,
        metrics: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate Beneish M-Score for earnings manipulation detection.
        M-Score > -2.22 suggests possible manipulation.
        
        Args:
            metrics: Financial metrics
            context: Additional context
            
        Returns:
            M-Score analysis
        """
        # Simplified M-Score calculation (requires historical data)
        # Full formula has 8 variables: DSRI, GMI, AQI, SGI, DEPI, SGAI, LVGI, TATA
        
        # Placeholder calculation
        dsri = metrics.get("dsri", 1.0)  # Days Sales in Receivables Index
        gmi = metrics.get("gmi", 1.0)    # Gross Margin Index
        aqi = metrics.get("aqi", 1.0)    # Asset Quality Index
        sgi = metrics.get("sgi", 1.0)    # Sales Growth Index
        
        # Simplified M-Score
        m_score = -4.84 + (0.92 * dsri) + (0.58 * gmi) + (0.40 * aqi) + (0.89 * sgi)
        
        # Interpret score
        if m_score > -2.22:
            risk = "high"
            interpretation = "Possible earnings manipulation"
        elif m_score > -2.50:
            risk = "medium"
            interpretation = "Some manipulation indicators"
        else:
            risk = "low"
            interpretation = "Low manipulation risk"
        
        logger.info(f"Beneish M-Score: {m_score:.2f} ({risk} risk)")
        
        return {
            "score": m_score,
            "risk": risk,
            "interpretation": interpretation,
            "threshold": -2.22
        }
    
    def _calculate_altman_z_score(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Altman Z-Score for bankruptcy risk.
        Z > 2.99: Safe zone
        1.81 < Z < 2.99: Gray zone
        Z < 1.81: Distress zone
        
        Args:
            metrics: Financial metrics
            
        Returns:
            Z-Score analysis
        """
        # Z-Score formula for public companies:
        # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
        # X1 = Working Capital / Total Assets
        # X2 = Retained Earnings / Total Assets
        # X3 = EBIT / Total Assets
        # X4 = Market Value of Equity / Total Liabilities
        # X5 = Sales / Total Assets
        
        total_assets = metrics.get("total_assets", 1)
        working_capital = metrics.get("working_capital", 0)
        retained_earnings = metrics.get("retained_earnings", 0)
        ebit = metrics.get("ebit", 0)
        market_cap = metrics.get("market_cap", 0)
        total_liabilities = metrics.get("total_liabilities", 1)
        revenue = metrics.get("revenue", 0)
        
        x1 = working_capital / total_assets
        x2 = retained_earnings / total_assets
        x3 = ebit / total_assets
        x4 = market_cap / total_liabilities if total_liabilities > 0 else 0
        x5 = revenue / total_assets
        
        z_score = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (1.0 * x5)
        
        # Interpret score
        if z_score > 2.99:
            zone = "safe"
            risk = "low"
        elif z_score > 1.81:
            zone = "gray"
            risk = "medium"
        else:
            zone = "distress"
            risk = "high"
        
        logger.info(f"Altman Z-Score: {z_score:.2f} ({zone} zone)")
        
        return {
            "score": z_score,
            "zone": zone,
            "risk": risk
        }
    
    def _assess_quality_of_earnings(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess quality of earnings.
        
        Args:
            metrics: Financial metrics
            
        Returns:
            Quality of earnings assessment
        """
        net_income = metrics.get("net_income", 0)
        operating_cash_flow = metrics.get("operating_cash_flow", 0)
        
        # Cash flow to earnings ratio
        if net_income > 0:
            cf_to_earnings = operating_cash_flow / net_income
        else:
            cf_to_earnings = 0
        
        # Accruals ratio
        accruals = net_income - operating_cash_flow
        total_assets = metrics.get("total_assets", 1)
        accruals_ratio = accruals / total_assets
        
        # Assess quality
        if cf_to_earnings > 1.0 and abs(accruals_ratio) < 0.05:
            quality = "high"
        elif cf_to_earnings > 0.8:
            quality = "medium"
        else:
            quality = "low"
        
        return {
            "quality": quality,
            "cf_to_earnings_ratio": cf_to_earnings,
            "accruals_ratio": accruals_ratio
        }
    
    def _identify_red_flags(
        self,
        metrics: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Identify accounting red flags.
        
        Args:
            metrics: Financial metrics
            context: Additional context
            
        Returns:
            List of red flags
        """
        red_flags = []
        
        # Revenue recognition issues
        revenue_growth = metrics.get("revenue_growth_rate", 0)
        receivables_growth = metrics.get("receivables_growth_rate", 0)
        
        if receivables_growth > revenue_growth * 1.5:
            red_flags.append({
                "type": "revenue_recognition",
                "severity": "high",
                "description": "Receivables growing much faster than revenue"
            })
        
        # Cash flow issues
        net_income = metrics.get("net_income", 0)
        operating_cash_flow = metrics.get("operating_cash_flow", 0)
        
        if net_income > 0 and operating_cash_flow < net_income * 0.5:
            red_flags.append({
                "type": "cash_flow",
                "severity": "high",
                "description": "Operating cash flow significantly below net income"
            })
        
        # Inventory issues
        inventory_growth = metrics.get("inventory_growth_rate", 0)
        if inventory_growth > revenue_growth * 2:
            red_flags.append({
                "type": "inventory",
                "severity": "medium",
                "description": "Inventory growing faster than revenue"
            })
        
        # Debt issues
        debt_to_equity = metrics.get("debt_to_equity", 0)
        if debt_to_equity > 3.0:
            red_flags.append({
                "type": "leverage",
                "severity": "high",
                "description": "Excessive leverage"
            })
        
        # Auditor changes
        if context.get("auditor_changed_recently"):
            red_flags.append({
                "type": "auditor",
                "severity": "medium",
                "description": "Recent auditor change"
            })
        
        return red_flags
    
    def _generate_analysis(
        self,
        beneish_score: Dict[str, Any],
        altman_score: Dict[str, Any],
        quality_of_earnings: Dict[str, Any],
        red_flags: List[Dict[str, str]],
        metrics: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Generate comprehensive forensics analysis text."""
        
        parts = ["FINANCIAL FORENSICS ANALYSIS\n"]
        
        # Beneish M-Score
        parts.append(f"Earnings Manipulation Risk (Beneish M-Score):")
        parts.append(f"  Score: {beneish_score['score']:.2f}")
        parts.append(f"  Risk Level: {beneish_score['risk'].upper()}")
        parts.append(f"  {beneish_score['interpretation']}")
        
        # Altman Z-Score
        parts.append(f"\nBankruptcy Risk (Altman Z-Score):")
        parts.append(f"  Score: {altman_score['score']:.2f}")
        parts.append(f"  Zone: {altman_score['zone'].upper()}")
        parts.append(f"  Risk Level: {altman_score['risk'].upper()}")
        
        # Quality of Earnings
        parts.append(f"\nQuality of Earnings: {quality_of_earnings['quality'].upper()}")
        parts.append(f"  CF/Earnings Ratio: {quality_of_earnings['cf_to_earnings_ratio']:.2f}")
        parts.append(f"  Accruals Ratio: {quality_of_earnings['accruals_ratio']:.2%}")
        
        # Red Flags
        if red_flags:
            parts.append(f"\nRed Flags Identified: {len(red_flags)}")
            for flag in red_flags[:3]:  # Show top 3
                parts.append(f"  ⚠ [{flag['severity'].upper()}] {flag['description']}")
        else:
            parts.append("\n✓ No significant red flags identified")
        
        # Framework Context
        if rag_results:
            parts.append(f"\nApplied {len(rag_results)} forensics frameworks")
        
        return "\n".join(parts)
    
    def _determine_recommendation(
        self,
        beneish_score: Dict[str, Any],
        altman_score: Dict[str, Any],
        quality_of_earnings: Dict[str, Any],
        red_flags: List[Dict[str, str]]
    ) -> str:
        """Determine forensics-based recommendation."""
        
        # Sell: high manipulation risk or distress
        if (beneish_score['risk'] == 'high' or
            altman_score['zone'] == 'distress' or
            len([f for f in red_flags if f['severity'] == 'high']) >= 2):
            return "SELL - Significant forensics concerns"
        
        # Hold: medium risk
        if (beneish_score['risk'] == 'medium' or
            altman_score['zone'] == 'gray' or
            quality_of_earnings['quality'] == 'low'):
            return "HOLD - Forensics require monitoring"
        
        # Buy: clean financials
        if (beneish_score['risk'] == 'low' and
            altman_score['zone'] == 'safe' and
            quality_of_earnings['quality'] == 'high' and
            len(red_flags) == 0):
            return "BUY - Clean financial statements"
        
        return "HOLD - Mixed forensics signals"
    
    def _calculate_confidence(
        self,
        metrics: Dict[str, Any],
        beneish_score: Dict[str, Any],
        altman_score: Dict[str, Any]
    ) -> float:
        """Calculate confidence score."""
        
        confidence = 0.5
        
        # Increase with data availability
        if beneish_score['score'] is not None:
            confidence += 0.20
        
        if altman_score['score'] is not None:
            confidence += 0.20
        
        if "operating_cash_flow" in metrics:
            confidence += 0.10
        
        return min(confidence, 1.0)
    
    def _identify_concerns(
        self,
        beneish_score: Dict[str, Any],
        altman_score: Dict[str, Any],
        red_flags: List[Dict[str, str]]
    ) -> List[str]:
        """Identify forensics concerns."""
        concerns = []
        
        if beneish_score['risk'] in ['high', 'medium']:
            concerns.append(f"Beneish M-Score indicates {beneish_score['risk']} manipulation risk")
        
        if altman_score['zone'] in ['distress', 'gray']:
            concerns.append(f"Altman Z-Score in {altman_score['zone']} zone")
        
        # Add high severity red flags
        for flag in red_flags:
            if flag['severity'] == 'high':
                concerns.append(flag['description'])
        
        return concerns
    
    def _identify_opportunities(
        self,
        quality_of_earnings: Dict[str, Any]
    ) -> List[str]:
        """Identify forensics-based opportunities."""
        opportunities = []
        
        if quality_of_earnings['quality'] == 'high':
            opportunities.append("High quality earnings provide confidence in reported results")
        
        if quality_of_earnings['cf_to_earnings_ratio'] > 1.2:
            opportunities.append("Strong cash flow generation exceeds reported earnings")
        
        return opportunities
    
    def get_relevant_frameworks(self) -> List[str]:
        """Get relevant framework categories."""
        return [
            "Beneish M-Score",
            "Altman Z-Score",
            "Quality of Earnings",
            "Cash Flow Analysis",
            "Accounting Red Flags",
            "Revenue Recognition Quality"
        ]
