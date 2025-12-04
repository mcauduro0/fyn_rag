"""
Base Agent class for the multi-agent investment committee system.
Provides common functionality for all specialized agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Enumeration of agent roles in the investment committee."""
    ORCHESTRATOR = "orchestrator"
    VALUE_INVESTING = "value_investing"
    GROWTH_VC = "growth_vc"
    RISK_MANAGEMENT = "risk_management"
    INDUSTRY_COMPETITIVE = "industry_competitive"
    FINANCIAL_FORENSICS = "financial_forensics"


class AgentResponse:
    """Standardized response from an agent."""
    
    def __init__(
        self,
        agent_role: AgentRole,
        analysis: str,
        recommendation: str,
        confidence: float,
        supporting_data: Dict[str, Any],
        frameworks_used: List[str],
        concerns: Optional[List[str]] = None,
        opportunities: Optional[List[str]] = None
    ):
        self.agent_role = agent_role
        self.analysis = analysis
        self.recommendation = recommendation
        self.confidence = confidence
        self.supporting_data = supporting_data
        self.frameworks_used = frameworks_used
        self.concerns = concerns or []
        self.opportunities = opportunities or []
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "agent_role": self.agent_role.value,
            "analysis": self.analysis,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "supporting_data": self.supporting_data,
            "frameworks_used": self.frameworks_used,
            "concerns": self.concerns,
            "opportunities": self.opportunities,
            "timestamp": self.timestamp.isoformat()
        }


class BaseAgent(ABC):
    """Abstract base class for all investment committee agents."""
    
    def __init__(
        self,
        role: AgentRole,
        name: str,
        description: str,
        llm_model: str = "gpt-4"
    ):
        """
        Initialize the agent.
        
        Args:
            role: Agent's role in the committee
            name: Human-readable name
            description: Description of agent's expertise
            llm_model: LLM model to use for reasoning
        """
        self.role = role
        self.name = name
        self.description = description
        self.llm_model = llm_model
        self.memory: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized {self.name} ({self.role.value})")
    
    @abstractmethod
    async def analyze(
        self,
        task: str,
        context: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]] = None
    ) -> AgentResponse:
        """
        Perform analysis based on the agent's expertise.
        
        Args:
            task: The analysis task
            context: Context information (company data, market data, etc.)
            rag_results: Relevant frameworks from RAG system
            
        Returns:
            AgentResponse with analysis and recommendation
        """
        pass
    
    @abstractmethod
    def get_relevant_frameworks(self) -> List[str]:
        """
        Get list of framework categories relevant to this agent.
        
        Returns:
            List of framework category names
        """
        pass
    
    def add_to_memory(self, interaction: Dict[str, Any]) -> None:
        """
        Add an interaction to agent's memory.
        
        Args:
            interaction: Dictionary containing interaction details
        """
        interaction["timestamp"] = datetime.utcnow().isoformat()
        self.memory.append(interaction)
        
        # Keep only last 100 interactions
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]
    
    def get_recent_memory(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent interactions from memory.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interactions
        """
        return self.memory[-limit:]
    
    def clear_memory(self) -> None:
        """Clear agent's memory."""
        self.memory = []
        logger.info(f"Cleared memory for {self.name}")
    
    async def _query_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        Query the LLM with given prompts.
        
        Args:
            system_prompt: System/role prompt
            user_prompt: User query
            temperature: Sampling temperature
            
        Returns:
            LLM response text
        """
        # This will be implemented with actual LLM integration
        # For now, return a placeholder
        logger.info(f"{self.name} querying LLM: {user_prompt[:100]}...")
        
        # TODO: Implement actual LLM call (OpenAI/Anthropic)
        return f"[LLM Response from {self.name}]"
    
    def _format_rag_context(
        self,
        rag_results: Optional[List[Dict[str, Any]]]
    ) -> str:
        """
        Format RAG results into context string.
        
        Args:
            rag_results: Results from RAG system
            
        Returns:
            Formatted context string
        """
        if not rag_results:
            return "No relevant frameworks found."
        
        context_parts = []
        for i, result in enumerate(rag_results, 1):
            framework_name = result.get("framework_name", "Unknown")
            content = result.get("content", "")
            score = result.get("score", 0.0)
            
            context_parts.append(
                f"\n--- Framework {i}: {framework_name} (Relevance: {score:.2f}) ---\n"
                f"{content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _extract_key_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key metrics from context.
        
        Args:
            context: Context dictionary
            
        Returns:
            Dictionary of key metrics
        """
        metrics = {}
        
        # Extract from different data sources
        if "market_data" in context:
            market = context["market_data"]
            metrics["current_price"] = market.get("price")
            metrics["market_cap"] = market.get("market_cap")
        
        if "fundamental_data" in context:
            fundamental = context["fundamental_data"]
            metrics["revenue"] = fundamental.get("revenue")
            metrics["earnings"] = fundamental.get("earnings")
            metrics["pe_ratio"] = fundamental.get("pe_ratio")
        
        return metrics
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(role={self.role.value}, name={self.name})"
