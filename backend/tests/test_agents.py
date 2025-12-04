"""
Comprehensive tests for specialized agents.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.core.agents.base_agent import BaseAgent, AgentRole, AgentResponse
from app.core.agents.value_investing_agent import ValueInvestingAgent
from app.core.agents.growth_vc_agent import GrowthVCAgent
from app.core.agents.risk_management_agent import RiskManagementAgent
from app.core.agents.industry_competitive_agent import IndustryCompetitiveAgent
from app.core.agents.financial_forensics_agent import FinancialForensicsAgent


@pytest.fixture
def sample_context():
    """Sample context for testing."""
    return {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "current_price": 180.0,
        "market_cap": 2800000000000,
        "revenue": 394000000000,
        "net_income": 97000000000,
        "free_cash_flow": 99000000000,
        "total_debt": 120000000000,
        "cash": 50000000000,
        "shares_outstanding": 15500000000,
        "beta": 1.2,
        "pe_ratio": 28.5,
        "pb_ratio": 45.0,
        "industry": "Technology",
        "sector": "Consumer Electronics"
    }


@pytest.fixture
def sample_rag_results():
    """Sample RAG results for testing."""
    return [
        {
            "framework": "Discounted Cash Flow",
            "description": "DCF valuation methodology",
            "category": "valuation",
            "score": 0.95
        },
        {
            "framework": "Porter's Five Forces",
            "description": "Industry analysis framework",
            "category": "competitive",
            "score": 0.88
        }
    ]


class TestBaseAgent:
    """Tests for BaseAgent."""
    
    def test_base_agent_initialization(self):
        """Test base agent can be initialized."""
        agent = BaseAgent(
            role=AgentRole.VALUE_INVESTING,
            name="Test Agent"
        )
        
        assert agent.role == AgentRole.VALUE_INVESTING
        assert agent.name == "Test Agent"
        assert agent.frameworks == []
    
    @pytest.mark.asyncio
    async def test_base_agent_analyze_not_implemented(self, sample_context, sample_rag_results):
        """Test base agent analyze raises NotImplementedError."""
        agent = BaseAgent(
            role=AgentRole.VALUE_INVESTING,
            name="Test Agent"
        )
        
        with pytest.raises(NotImplementedError):
            await agent.analyze("Test task", sample_context, sample_rag_results)


class TestValueInvestingAgent:
    """Tests for Value Investing Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create Value Investing Agent instance."""
        return ValueInvestingAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.role == AgentRole.VALUE_INVESTING
        assert agent.name == "Value Investing Analyst"
        assert len(agent.frameworks) > 0
        assert "Discounted Cash Flow" in agent.frameworks
    
    @pytest.mark.asyncio
    async def test_analyze_returns_response(self, agent, sample_context, sample_rag_results):
        """Test analyze returns proper AgentResponse."""
        response = await agent.analyze(
            "Analyze AAPL for value investment",
            sample_context,
            sample_rag_results
        )
        
        assert isinstance(response, AgentResponse)
        assert response.agent_role == AgentRole.VALUE_INVESTING
        assert response.recommendation in ["BUY", "HOLD", "SELL"]
        assert 0 <= response.confidence <= 1
        assert len(response.frameworks_used) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_intrinsic_value(self, agent, sample_context):
        """Test intrinsic value calculation."""
        response = await agent.analyze(
            "Calculate intrinsic value",
            sample_context,
            []
        )
        
        assert "intrinsic_value" in response.supporting_data
        assert response.supporting_data["intrinsic_value"] > 0
    
    @pytest.mark.asyncio
    async def test_margin_of_safety_calculation(self, agent, sample_context):
        """Test margin of safety is calculated."""
        response = await agent.analyze(
            "Analyze value",
            sample_context,
            []
        )
        
        assert "margin_of_safety" in response.supporting_data
        margin = response.supporting_data["margin_of_safety"]
        assert isinstance(margin, (int, float))


class TestGrowthVCAgent:
    """Tests for Growth & VC Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create Growth & VC Agent instance."""
        return GrowthVCAgent()
    
    @pytest.fixture
    def growth_context(self, sample_context):
        """Context for growth company."""
        context = sample_context.copy()
        context.update({
            "revenue_growth": 0.25,
            "cac": 1000,
            "ltv": 5000,
            "burn_rate": 5000000,
            "cash": 50000000,
            "tam": 100000000000,
            "sam": 20000000000,
            "som": 2000000000
        })
        return context
    
    def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.role == AgentRole.GROWTH_VC
        assert "Rule of 40" in agent.frameworks
    
    @pytest.mark.asyncio
    async def test_rule_of_40_calculation(self, agent, growth_context):
        """Test Rule of 40 calculation."""
        response = await agent.analyze(
            "Analyze growth metrics",
            growth_context,
            []
        )
        
        assert "rule_of_40" in response.supporting_data
        rule_of_40 = response.supporting_data["rule_of_40"]
        assert isinstance(rule_of_40, (int, float))
    
    @pytest.mark.asyncio
    async def test_ltv_cac_ratio(self, agent, growth_context):
        """Test LTV/CAC ratio calculation."""
        response = await agent.analyze(
            "Analyze unit economics",
            growth_context,
            []
        )
        
        assert "ltv_cac_ratio" in response.supporting_data
        ratio = response.supporting_data["ltv_cac_ratio"]
        assert ratio == 5.0  # 5000 / 1000


class TestRiskManagementAgent:
    """Tests for Risk Management Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create Risk Management Agent instance."""
        return RiskManagementAgent()
    
    @pytest.fixture
    def risk_context(self, sample_context):
        """Context with risk data."""
        context = sample_context.copy()
        context.update({
            "volatility": 0.25,
            "beta": 1.2,
            "current_ratio": 1.5,
            "quick_ratio": 1.2,
            "debt_to_equity": 1.8
        })
        return context
    
    def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.role == AgentRole.RISK_MANAGEMENT
        assert "Value at Risk" in agent.frameworks
    
    @pytest.mark.asyncio
    async def test_var_calculation(self, agent, risk_context):
        """Test VaR calculation."""
        response = await agent.analyze(
            "Calculate risk metrics",
            risk_context,
            []
        )
        
        assert "var_95" in response.supporting_data
        var = response.supporting_data["var_95"]
        assert isinstance(var, (int, float))
        assert var < 0  # VaR should be negative
    
    @pytest.mark.asyncio
    async def test_identifies_high_risk(self, agent, risk_context):
        """Test agent identifies high risk scenarios."""
        high_risk_context = risk_context.copy()
        high_risk_context["debt_to_equity"] = 5.0
        high_risk_context["current_ratio"] = 0.5
        
        response = await agent.analyze(
            "Assess risk",
            high_risk_context,
            []
        )
        
        assert len(response.concerns) > 0
        assert response.confidence < 0.7  # Lower confidence for high risk


class TestIndustryCompetitiveAgent:
    """Tests for Industry & Competitive Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create Industry & Competitive Agent instance."""
        return IndustryCompetitiveAgent()
    
    @pytest.fixture
    def industry_context(self, sample_context):
        """Context with industry data."""
        context = sample_context.copy()
        context.update({
            "market_share": 0.15,
            "industry_growth": 0.08,
            "competitive_position": "leader",
            "barriers_to_entry": "high",
            "supplier_power": "low",
            "buyer_power": "medium"
        })
        return context
    
    def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.role == AgentRole.INDUSTRY_COMPETITIVE
        assert "Porter's Five Forces" in agent.frameworks
    
    @pytest.mark.asyncio
    async def test_porters_five_forces(self, agent, industry_context):
        """Test Porter's Five Forces analysis."""
        response = await agent.analyze(
            "Analyze competitive position",
            industry_context,
            []
        )
        
        assert "industry_attractiveness" in response.supporting_data
        assert "competitive_position" in response.supporting_data
    
    @pytest.mark.asyncio
    async def test_identifies_market_leader(self, agent, industry_context):
        """Test agent identifies market leaders."""
        response = await agent.analyze(
            "Analyze position",
            industry_context,
            []
        )
        
        position = response.supporting_data.get("competitive_position")
        assert position in ["leader", "challenger", "follower", "niche"]


class TestFinancialForensicsAgent:
    """Tests for Financial Forensics Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create Financial Forensics Agent instance."""
        return FinancialForensicsAgent()
    
    @pytest.fixture
    def forensics_context(self, sample_context):
        """Context with forensics data."""
        context = sample_context.copy()
        context.update({
            "days_sales_outstanding": 45,
            "asset_quality_index": 1.1,
            "sales_growth_index": 1.2,
            "depreciation_index": 1.0,
            "sgai": 0.95,
            "total_accruals": 5000000000,
            "operating_cash_flow": 100000000000,
            "working_capital": 20000000000,
            "current_assets": 150000000000,
            "current_liabilities": 130000000000
        })
        return context
    
    def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.role == AgentRole.FINANCIAL_FORENSICS
        assert "Beneish M-Score" in agent.frameworks
    
    @pytest.mark.asyncio
    async def test_m_score_calculation(self, agent, forensics_context):
        """Test M-Score calculation."""
        response = await agent.analyze(
            "Check for manipulation",
            forensics_context,
            []
        )
        
        assert "m_score" in response.supporting_data
        m_score = response.supporting_data["m_score"]
        assert isinstance(m_score, (int, float))
    
    @pytest.mark.asyncio
    async def test_z_score_calculation(self, agent, forensics_context):
        """Test Z-Score calculation."""
        response = await agent.analyze(
            "Assess bankruptcy risk",
            forensics_context,
            []
        )
        
        assert "z_score" in response.supporting_data
        z_score = response.supporting_data["z_score"]
        assert isinstance(z_score, (int, float))
    
    @pytest.mark.asyncio
    async def test_detects_red_flags(self, agent, forensics_context):
        """Test agent detects accounting red flags."""
        suspicious_context = forensics_context.copy()
        suspicious_context["days_sales_outstanding"] = 120  # Very high DSO
        suspicious_context["total_accruals"] = 50000000000  # High accruals
        
        response = await agent.analyze(
            "Investigate financials",
            suspicious_context,
            []
        )
        
        assert len(response.concerns) > 0


@pytest.mark.asyncio
async def test_all_agents_return_valid_responses(sample_context, sample_rag_results):
    """Integration test: all agents return valid responses."""
    agents = [
        ValueInvestingAgent(),
        GrowthVCAgent(),
        RiskManagementAgent(),
        IndustryCompetitiveAgent(),
        FinancialForensicsAgent()
    ]
    
    for agent in agents:
        response = await agent.analyze(
            f"Analyze {sample_context['ticker']}",
            sample_context,
            sample_rag_results
        )
        
        # Validate response structure
        assert isinstance(response, AgentResponse)
        assert response.agent_role in AgentRole
        assert response.analysis
        assert response.recommendation in ["BUY", "HOLD", "SELL"]
        assert 0 <= response.confidence <= 1
        assert isinstance(response.supporting_data, dict)
        assert isinstance(response.frameworks_used, list)
        assert isinstance(response.concerns, list)
        assert isinstance(response.opportunities, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
