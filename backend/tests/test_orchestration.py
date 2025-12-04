"""
Tests for orchestration and debate simulation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.core.orchestrator.orchestrator_agent import OrchestratorAgent
from app.core.reasoning.debate_simulator import DebateSimulator
from app.core.reasoning.agent_memory import AgentMemory, MemoryEntry, MemoryType
from app.core.agents.base_agent import AgentRole, AgentResponse


@pytest.fixture
def sample_agent_responses():
    """Sample responses from agents for testing."""
    return {
        AgentRole.VALUE_INVESTING: AgentResponse(
            agent_role=AgentRole.VALUE_INVESTING,
            analysis="Strong value proposition with 30% margin of safety",
            recommendation="BUY",
            confidence=0.85,
            supporting_data={"intrinsic_value": 200, "current_price": 140},
            frameworks_used=["DCF", "Margin of Safety"],
            concerns=["High valuation multiples"],
            opportunities=["Undervalued relative to peers"]
        ),
        AgentRole.GROWTH_VC: AgentResponse(
            agent_role=AgentRole.GROWTH_VC,
            analysis="Excellent growth metrics with Rule of 40 score of 45",
            recommendation="BUY",
            confidence=0.90,
            supporting_data={"rule_of_40": 45, "ltv_cac_ratio": 4.5},
            frameworks_used=["Rule of 40", "Unit Economics"],
            concerns=["High burn rate"],
            opportunities=["Large TAM", "Strong unit economics"]
        ),
        AgentRole.RISK_MANAGEMENT: AgentResponse(
            agent_role=AgentRole.RISK_MANAGEMENT,
            analysis="Moderate risk with acceptable volatility",
            recommendation="HOLD",
            confidence=0.70,
            supporting_data={"var_95": -15.5, "beta": 1.2},
            frameworks_used=["VaR", "Beta Analysis"],
            concerns=["High beta", "Liquidity concerns"],
            opportunities=["Diversification benefits"]
        ),
        AgentRole.INDUSTRY_COMPETITIVE: AgentResponse(
            agent_role=AgentRole.INDUSTRY_COMPETITIVE,
            analysis="Strong competitive position in attractive industry",
            recommendation="BUY",
            confidence=0.80,
            supporting_data={"industry_attractiveness": "high", "position": "leader"},
            frameworks_used=["Porter's Five Forces", "SWOT"],
            concerns=["Increasing competition"],
            opportunities=["Market leadership", "High barriers to entry"]
        ),
        AgentRole.FINANCIAL_FORENSICS: AgentResponse(
            agent_role=AgentRole.FINANCIAL_FORENSICS,
            analysis="Clean financials with no red flags detected",
            recommendation="BUY",
            confidence=0.95,
            supporting_data={"m_score": -1.5, "z_score": 3.5},
            frameworks_used=["M-Score", "Z-Score"],
            concerns=[],
            opportunities=["High quality earnings", "Strong cash flow"]
        )
    }


class TestOrchestratorAgent:
    """Tests for Orchestrator Agent."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create Orchestrator instance."""
        return OrchestratorAgent()
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator is properly initialized."""
        assert orchestrator.name == "Orchestrator"
        assert isinstance(orchestrator.available_agents, list)
        assert len(orchestrator.available_agents) == 5
    
    def test_task_decomposition(self, orchestrator):
        """Test task decomposition."""
        task = "Analyze AAPL for investment"
        subtasks = orchestrator.decompose_task(task)
        
        assert isinstance(subtasks, list)
        assert len(subtasks) > 0
        assert all(isinstance(st, dict) for st in subtasks)
    
    @pytest.mark.asyncio
    async def test_orchestrate_analysis(self, orchestrator):
        """Test orchestrate analysis coordinates agents."""
        task = "Analyze AAPL"
        context = {"ticker": "AAPL", "current_price": 180}
        
        with patch.object(orchestrator, '_run_agent_analysis', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = AgentResponse(
                agent_role=AgentRole.VALUE_INVESTING,
                analysis="Test analysis",
                recommendation="BUY",
                confidence=0.8,
                supporting_data={},
                frameworks_used=[],
                concerns=[],
                opportunities=[]
            )
            
            results = await orchestrator.orchestrate_analysis(task, context, [])
            
            assert isinstance(results, dict)
            assert len(results) > 0


class TestDebateSimulator:
    """Tests for Debate Simulator."""
    
    @pytest.fixture
    def simulator(self):
        """Create Debate Simulator instance."""
        return DebateSimulator(max_rounds=3)
    
    def test_simulator_initialization(self, simulator):
        """Test simulator is properly initialized."""
        assert simulator.max_rounds == 3
        assert hasattr(simulator, 'debate_history')
    
    @pytest.mark.asyncio
    async def test_run_debate(self, simulator, sample_agent_responses):
        """Test debate simulation runs successfully."""
        context = {"ticker": "AAPL"}
        
        results = await simulator.run_debate(sample_agent_responses, context)
        
        assert isinstance(results, dict)
        assert "consensus_reached" in results
        assert "final_recommendation" in results
        assert "confidence" in results
        assert "debate_rounds" in results
        assert "synthesis" in results
    
    @pytest.mark.asyncio
    async def test_consensus_with_agreement(self, simulator):
        """Test consensus is reached when agents agree."""
        # All agents agree on BUY
        responses = {
            AgentRole.VALUE_INVESTING: AgentResponse(
                agent_role=AgentRole.VALUE_INVESTING,
                analysis="Buy recommendation",
                recommendation="BUY",
                confidence=0.9,
                supporting_data={},
                frameworks_used=[],
                concerns=[],
                opportunities=[]
            ),
            AgentRole.GROWTH_VC: AgentResponse(
                agent_role=AgentRole.GROWTH_VC,
                analysis="Buy recommendation",
                recommendation="BUY",
                confidence=0.85,
                supporting_data={},
                frameworks_used=[],
                concerns=[],
                opportunities=[]
            )
        }
        
        results = await simulator.run_debate(responses, {})
        
        assert results["consensus_reached"] is True
        assert results["final_recommendation"] == "BUY"
        assert results["confidence"] > 0.8
    
    @pytest.mark.asyncio
    async def test_consensus_with_disagreement(self, simulator, sample_agent_responses):
        """Test debate handles disagreement."""
        # Mix of recommendations
        results = await simulator.run_debate(sample_agent_responses, {})
        
        assert "final_recommendation" in results
        assert results["final_recommendation"] in ["BUY", "HOLD", "SELL"]
        assert len(results["debate_rounds"]) > 0
    
    def test_calculate_weighted_vote(self, simulator, sample_agent_responses):
        """Test weighted voting calculation."""
        vote_result = simulator._calculate_weighted_vote(sample_agent_responses)
        
        assert "recommendation" in vote_result
        assert "confidence" in vote_result
        assert "vote_distribution" in vote_result
        assert vote_result["recommendation"] in ["BUY", "HOLD", "SELL"]
    
    def test_identify_conflicts(self, simulator, sample_agent_responses):
        """Test conflict identification."""
        conflicts = simulator._identify_conflicts(sample_agent_responses)
        
        assert isinstance(conflicts, list)
        # Should identify Risk Management's HOLD vs others' BUY
        assert len(conflicts) > 0
    
    def test_synthesize_insights(self, simulator, sample_agent_responses):
        """Test insight synthesis."""
        synthesis = simulator._synthesize_insights(sample_agent_responses)
        
        assert isinstance(synthesis, dict)
        assert "common_opportunities" in synthesis
        assert "common_concerns" in synthesis
        assert "key_insights" in synthesis


class TestAgentMemory:
    """Tests for Agent Memory System."""
    
    @pytest.fixture
    def memory(self):
        """Create Agent Memory instance."""
        return AgentMemory(agent_id="test_agent")
    
    def test_memory_initialization(self, memory):
        """Test memory is properly initialized."""
        assert memory.agent_id == "test_agent"
        assert len(memory.short_term) == 0
        assert len(memory.long_term) == 0
    
    def test_add_short_term_memory(self, memory):
        """Test adding short-term memory."""
        memory.add_memory(
            content="Test interaction",
            memory_type=MemoryType.SHORT_TERM,
            importance=0.5
        )
        
        assert len(memory.short_term) == 1
        assert memory.short_term[0].content == "Test interaction"
    
    def test_add_long_term_memory(self, memory):
        """Test adding long-term memory."""
        memory.add_memory(
            content="Important learning",
            memory_type=MemoryType.LONG_TERM,
            importance=0.9,
            metadata={"category": "valuation"}
        )
        
        assert len(memory.long_term) == 1
        entry = memory.long_term[0]
        assert entry.content == "Important learning"
        assert entry.importance == 0.9
        assert entry.metadata["category"] == "valuation"
    
    def test_short_term_capacity_limit(self, memory):
        """Test short-term memory respects capacity limit."""
        # Add more than capacity
        for i in range(60):
            memory.add_memory(
                content=f"Memory {i}",
                memory_type=MemoryType.SHORT_TERM
            )
        
        # Should not exceed capacity (50)
        assert len(memory.short_term) <= 50
    
    def test_retrieve_memories(self, memory):
        """Test memory retrieval."""
        # Add some memories
        memory.add_memory("Analysis of AAPL", MemoryType.SHORT_TERM)
        memory.add_memory("DCF valuation method", MemoryType.LONG_TERM, importance=0.8)
        memory.add_memory("Risk assessment", MemoryType.SHORT_TERM)
        
        # Retrieve all
        all_memories = memory.retrieve_memories()
        assert len(all_memories) == 3
        
        # Retrieve by type
        short_term = memory.retrieve_memories(memory_type=MemoryType.SHORT_TERM)
        assert len(short_term) == 2
        
        long_term = memory.retrieve_memories(memory_type=MemoryType.LONG_TERM)
        assert len(long_term) == 1
    
    def test_search_memories(self, memory):
        """Test memory search."""
        memory.add_memory("AAPL valuation analysis", MemoryType.SHORT_TERM)
        memory.add_memory("GOOGL growth metrics", MemoryType.SHORT_TERM)
        memory.add_memory("AAPL risk assessment", MemoryType.LONG_TERM)
        
        # Search for AAPL
        results = memory.search_memories("AAPL")
        assert len(results) == 2
        assert all("AAPL" in r.content for r in results)
    
    def test_consolidate_memories(self, memory):
        """Test memory consolidation."""
        # Add many short-term memories
        for i in range(10):
            memory.add_memory(
                f"Important insight {i}",
                MemoryType.SHORT_TERM,
                importance=0.8
            )
        
        initial_long_term = len(memory.long_term)
        
        # Consolidate
        consolidated = memory.consolidate_memories(threshold=0.7)
        
        # Some should be promoted to long-term
        assert len(memory.long_term) > initial_long_term
        assert consolidated > 0
    
    def test_memory_relevance_scoring(self, memory):
        """Test relevance scoring."""
        import time
        
        # Add old memory
        old_entry = MemoryEntry(
            content="Old memory",
            memory_type=MemoryType.LONG_TERM,
            importance=0.5
        )
        old_entry.timestamp = datetime(2020, 1, 1)
        old_entry.access_count = 1
        memory.long_term.append(old_entry)
        
        # Add recent memory
        recent_entry = MemoryEntry(
            content="Recent memory",
            memory_type=MemoryType.LONG_TERM,
            importance=0.5
        )
        recent_entry.access_count = 5
        memory.long_term.append(recent_entry)
        
        # Recent memory should have higher relevance
        old_relevance = memory._calculate_relevance(old_entry)
        recent_relevance = memory._calculate_relevance(recent_entry)
        
        assert recent_relevance > old_relevance
    
    def test_cleanup_expired_memories(self, memory):
        """Test cleanup of expired memories."""
        # Add expired memory
        expired_entry = MemoryEntry(
            content="Expired",
            memory_type=MemoryType.SHORT_TERM
        )
        expired_entry.timestamp = datetime(2020, 1, 1)
        memory.short_term.append(expired_entry)
        
        # Add fresh memory
        memory.add_memory("Fresh", MemoryType.SHORT_TERM)
        
        # Cleanup
        removed = memory.cleanup_expired(max_age_days=30)
        
        assert removed > 0
        assert len(memory.short_term) == 1
        assert memory.short_term[0].content == "Fresh"
    
    def test_export_import_memories(self, memory):
        """Test memory export and import."""
        # Add memories
        memory.add_memory("Test memory 1", MemoryType.SHORT_TERM)
        memory.add_memory("Test memory 2", MemoryType.LONG_TERM, importance=0.9)
        
        # Export
        exported = memory.export_memories()
        
        assert isinstance(exported, dict)
        assert "agent_id" in exported
        assert "short_term" in exported
        assert "long_term" in exported
        
        # Create new memory and import
        new_memory = AgentMemory(agent_id="test_agent_2")
        new_memory.import_memories(exported)
        
        assert len(new_memory.short_term) == len(memory.short_term)
        assert len(new_memory.long_term) == len(memory.long_term)


@pytest.mark.asyncio
async def test_full_orchestration_flow(sample_agent_responses):
    """Integration test: full orchestration flow."""
    orchestrator = OrchestratorAgent()
    simulator = DebateSimulator()
    
    # Simulate orchestration
    task = "Analyze AAPL for investment"
    context = {"ticker": "AAPL", "current_price": 180}
    
    # Run debate
    debate_results = await simulator.run_debate(sample_agent_responses, context)
    
    # Validate results
    assert debate_results["final_recommendation"] in ["BUY", "HOLD", "SELL"]
    assert 0 <= debate_results["confidence"] <= 1
    assert len(debate_results["debate_rounds"]) > 0
    
    # Check synthesis
    synthesis = debate_results["synthesis"]
    assert "common_opportunities" in synthesis
    assert "common_concerns" in synthesis


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
