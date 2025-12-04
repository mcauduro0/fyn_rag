"""
Orchestrator Agent - Coordinates the multi-agent investment committee.
Decomposes tasks, delegates to specialized agents, and synthesizes responses.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.agents.base_agent import BaseAgent, AgentRole, AgentResponse

logger = logging.getLogger(__name__)


class Task:
    """Represents a decomposed subtask."""
    
    def __init__(
        self,
        task_id: str,
        description: str,
        assigned_agent: AgentRole,
        priority: int = 1,
        dependencies: Optional[List[str]] = None
    ):
        self.task_id = task_id
        self.description = description
        self.assigned_agent = assigned_agent
        self.priority = priority
        self.dependencies = dependencies or []
        self.status = "pending"  # pending, in_progress, completed, failed
        self.result: Optional[AgentResponse] = None
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "assigned_agent": self.assigned_agent.value,
            "priority": self.priority,
            "dependencies": self.dependencies,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent coordinates the investment committee.
    
    Responsibilities:
    1. Decompose complex investment analysis into subtasks
    2. Delegate subtasks to specialized agents
    3. Manage task dependencies and execution order
    4. Synthesize agent responses into final recommendation
    5. Facilitate debate and consensus building
    """
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(
            role=AgentRole.ORCHESTRATOR,
            name="Investment Committee Orchestrator",
            description="Coordinates multi-agent investment analysis and synthesis",
            llm_model=llm_model
        )
        self.tasks: List[Task] = []
        self.agent_responses: Dict[AgentRole, AgentResponse] = {}
    
    async def analyze(
        self,
        task: str,
        context: Dict[str, Any],
        rag_results: Optional[List[Dict[str, Any]]] = None
    ) -> AgentResponse:
        """
        Orchestrate the complete investment analysis.
        
        Args:
            task: High-level investment analysis task
            context: All available context (company, market, documents)
            rag_results: Relevant frameworks from RAG
            
        Returns:
            Synthesized AgentResponse with final recommendation
        """
        logger.info(f"Orchestrator starting analysis: {task}")
        
        # Step 1: Decompose task into subtasks
        subtasks = await self._decompose_task(task, context)
        
        # Step 2: Determine execution order
        execution_plan = self._create_execution_plan(subtasks)
        
        # Step 3: Execute tasks (will be delegated to specialized agents)
        # This is a placeholder - actual execution happens via agent manager
        
        # Step 4: Synthesize results
        synthesis = await self._synthesize_results(task, context)
        
        return synthesis
    
    async def _decompose_task(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> List[Task]:
        """
        Decompose high-level task into specialized subtasks.
        
        Args:
            task: High-level investment analysis task
            context: Context information
            
        Returns:
            List of decomposed tasks
        """
        logger.info("Decomposing task into subtasks...")
        
        # Analyze task type and context to determine required analyses
        asset_type = context.get("asset_type", "listed")  # listed or illiquid
        
        subtasks = []
        
        # Always include value analysis
        subtasks.append(Task(
            task_id="value_analysis",
            description=f"Perform value investing analysis: {task}",
            assigned_agent=AgentRole.VALUE_INVESTING,
            priority=1
        ))
        
        # Growth analysis for growth/tech companies
        if self._requires_growth_analysis(context):
            subtasks.append(Task(
                task_id="growth_analysis",
                description=f"Perform growth and VC analysis: {task}",
                assigned_agent=AgentRole.GROWTH_VC,
                priority=1
            ))
        
        # Risk analysis (always required)
        subtasks.append(Task(
            task_id="risk_analysis",
            description=f"Perform risk management analysis: {task}",
            assigned_agent=AgentRole.RISK_MANAGEMENT,
            priority=2,
            dependencies=["value_analysis"]
        ))
        
        # Industry analysis
        subtasks.append(Task(
            task_id="industry_analysis",
            description=f"Perform industry and competitive analysis: {task}",
            assigned_agent=AgentRole.INDUSTRY_COMPETITIVE,
            priority=1
        ))
        
        # Financial forensics for detailed due diligence
        if self._requires_forensics(context):
            subtasks.append(Task(
                task_id="forensics_analysis",
                description=f"Perform financial forensics analysis: {task}",
                assigned_agent=AgentRole.FINANCIAL_FORENSICS,
                priority=2,
                dependencies=["value_analysis"]
            ))
        
        self.tasks = subtasks
        logger.info(f"Decomposed into {len(subtasks)} subtasks")
        
        return subtasks
    
    def _create_execution_plan(self, subtasks: List[Task]) -> List[List[Task]]:
        """
        Create execution plan respecting dependencies.
        
        Args:
            subtasks: List of tasks to execute
            
        Returns:
            List of task batches (tasks in same batch can run in parallel)
        """
        # Group tasks by priority and dependencies
        batches: List[List[Task]] = []
        
        # Priority 1 tasks with no dependencies (can run in parallel)
        batch_1 = [t for t in subtasks if t.priority == 1 and not t.dependencies]
        if batch_1:
            batches.append(batch_1)
        
        # Priority 2 tasks (depend on batch 1)
        batch_2 = [t for t in subtasks if t.priority == 2]
        if batch_2:
            batches.append(batch_2)
        
        logger.info(f"Created execution plan with {len(batches)} batches")
        return batches
    
    async def _synthesize_results(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """
        Synthesize all agent responses into final recommendation.
        
        Args:
            task: Original task
            context: Context information
            
        Returns:
            Synthesized AgentResponse
        """
        logger.info("Synthesizing agent responses...")
        
        # Collect all agent responses
        responses = list(self.agent_responses.values())
        
        if not responses:
            # No responses yet (placeholder for testing)
            return AgentResponse(
                agent_role=AgentRole.ORCHESTRATOR,
                analysis="Analysis in progress. Awaiting specialized agent responses.",
                recommendation="HOLD - Pending detailed analysis",
                confidence=0.5,
                supporting_data={"status": "in_progress"},
                frameworks_used=[]
            )
        
        # Aggregate recommendations
        recommendations = [r.recommendation for r in responses]
        avg_confidence = sum(r.confidence for r in responses) / len(responses)
        
        # Collect all frameworks used
        all_frameworks = []
        for r in responses:
            all_frameworks.extend(r.frameworks_used)
        
        # Collect concerns and opportunities
        all_concerns = []
        all_opportunities = []
        for r in responses:
            all_concerns.extend(r.concerns)
            all_opportunities.extend(r.opportunities)
        
        # Generate synthesis (placeholder - will use LLM)
        synthesis_text = self._generate_synthesis_text(responses)
        final_recommendation = self._determine_final_recommendation(recommendations)
        
        return AgentResponse(
            agent_role=AgentRole.ORCHESTRATOR,
            analysis=synthesis_text,
            recommendation=final_recommendation,
            confidence=avg_confidence,
            supporting_data={
                "agent_count": len(responses),
                "individual_recommendations": recommendations,
                "task": task
            },
            frameworks_used=list(set(all_frameworks)),
            concerns=list(set(all_concerns)),
            opportunities=list(set(all_opportunities))
        )
    
    def _generate_synthesis_text(self, responses: List[AgentResponse]) -> str:
        """Generate synthesis text from agent responses."""
        parts = ["Investment Committee Synthesis:\n"]
        
        for response in responses:
            parts.append(f"\n{response.agent_role.value.upper()}:")
            parts.append(f"  {response.analysis[:200]}...")
            parts.append(f"  Recommendation: {response.recommendation}")
            parts.append(f"  Confidence: {response.confidence:.2%}")
        
        return "\n".join(parts)
    
    def _determine_final_recommendation(self, recommendations: List[str]) -> str:
        """Determine final recommendation from individual recommendations."""
        # Simple majority voting (will be enhanced with debate simulator)
        buy_count = sum(1 for r in recommendations if "BUY" in r.upper())
        sell_count = sum(1 for r in recommendations if "SELL" in r.upper())
        hold_count = sum(1 for r in recommendations if "HOLD" in r.upper())
        
        if buy_count > sell_count and buy_count > hold_count:
            return "BUY"
        elif sell_count > buy_count and sell_count > hold_count:
            return "SELL"
        else:
            return "HOLD"
    
    def _requires_growth_analysis(self, context: Dict[str, Any]) -> bool:
        """Determine if growth analysis is needed."""
        # Check if company is in growth/tech sector
        sector = context.get("sector", "").lower()
        growth_sectors = ["technology", "software", "biotech", "saas"]
        return any(s in sector for s in growth_sectors)
    
    def _requires_forensics(self, context: Dict[str, Any]) -> bool:
        """Determine if forensics analysis is needed."""
        # Always require for detailed due diligence
        return context.get("analysis_depth", "standard") == "deep"
    
    def get_relevant_frameworks(self) -> List[str]:
        """Orchestrator uses all framework categories."""
        return [
            "Value Investing",
            "Growth & VC",
            "Risk Management",
            "Industry Analysis",
            "Financial Forensics"
        ]
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get status of all tasks."""
        return {
            "total_tasks": len(self.tasks),
            "completed": len([t for t in self.tasks if t.status == "completed"]),
            "in_progress": len([t for t in self.tasks if t.status == "in_progress"]),
            "pending": len([t for t in self.tasks if t.status == "pending"]),
            "tasks": [t.to_dict() for t in self.tasks]
        }
    
    def register_agent_response(
        self,
        agent_role: AgentRole,
        response: AgentResponse
    ) -> None:
        """
        Register a response from a specialized agent.
        
        Args:
            agent_role: Role of the agent
            response: Agent's response
        """
        self.agent_responses[agent_role] = response
        
        # Update corresponding task status
        for task in self.tasks:
            if task.assigned_agent == agent_role:
                task.status = "completed"
                task.result = response
                task.completed_at = datetime.utcnow()
        
        logger.info(f"Registered response from {agent_role.value}")


if __name__ == "__main__":
    # Test orchestrator
    import asyncio
    
    async def test():
        orchestrator = OrchestratorAgent()
        
        task = "Analyze Apple Inc. (AAPL) for potential investment"
        context = {
            "ticker": "AAPL",
            "sector": "Technology",
            "asset_type": "listed",
            "analysis_depth": "deep"
        }
        
        response = await orchestrator.analyze(task, context)
        print(f"\nOrchestrator Response:")
        print(f"Recommendation: {response.recommendation}")
        print(f"Confidence: {response.confidence:.2%}")
        
        print(f"\nTask Status:")
        status = orchestrator.get_task_status()
        print(f"Total tasks: {status['total_tasks']}")
        for task_dict in status['tasks']:
            print(f"  - {task_dict['description']} ({task_dict['assigned_agent']})")
    
    asyncio.run(test())
