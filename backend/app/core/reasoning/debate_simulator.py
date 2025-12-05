"""
Debate Simulator - Facilitates structured debate between agents to reach consensus.
Implements multi-round debate with conflict resolution and consensus building.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from app.core.agents.base_agent import AgentResponse, AgentRole
from app.core.llm.llm_client import LLMClient

logger = logging.getLogger(__name__)


class DebatePhase(str, Enum):
    """Phases of the debate process."""
    INITIAL_POSITIONS = "initial_positions"
    CHALLENGE = "challenge"
    REBUTTAL = "rebuttal"
    SYNTHESIS = "synthesis"
    CONSENSUS = "consensus"


class DebateRound:
    """Represents a single round of debate."""
    
    def __init__(self, round_number: int, phase: DebatePhase):
        self.round_number = round_number
        self.phase = phase
        self.statements: List[Dict[str, Any]] = []
        self.timestamp = datetime.utcnow()
    
    def add_statement(
        self,
        agent_role: AgentRole,
        statement: str,
        targets: Optional[List[AgentRole]] = None
    ) -> None:
        """Add a statement to this round."""
        self.statements.append({
            "agent_role": agent_role,
            "statement": statement,
            "targets": targets or [],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert round to dictionary."""
        return {
            "round_number": self.round_number,
            "phase": self.phase.value,
            "statements": self.statements,
            "timestamp": self.timestamp.isoformat()
        }


class DebateSimulator:
    """
    Debate Simulator facilitates structured debate between investment committee agents.
    
    Process:
    1. Initial Positions: Each agent presents their analysis and recommendation
    2. Challenge: Agents challenge conflicting positions with evidence
    3. Rebuttal: Agents respond to challenges and defend their positions
    4. Synthesis: Identify common ground and areas of disagreement
    5. Consensus: Build final recommendation through weighted voting
    """
    
    def __init__(self, max_rounds: int = 3, llm_model: str = "gpt-4"):
        """
        Initialize debate simulator.
        
        Args:
            max_rounds: Maximum number of debate rounds
            llm_model: LLM model to use for debate generation
        """
        self.max_rounds = max_rounds
        self.llm_model = llm_model
        self.llm_client = LLMClient(provider="openai")
        self.rounds: List[DebateRound] = []
        self.agent_responses: Dict[AgentRole, AgentResponse] = {}
        self.consensus_reached = False
        self.final_recommendation: Optional[str] = None
        
        logger.info(f"Initialized Debate Simulator (max_rounds={max_rounds})")
    
    async def run_debate(
        self,
        agent_responses: Dict[AgentRole, AgentResponse],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run the complete debate process.
        
        Args:
            agent_responses: Responses from all specialized agents
            context: Analysis context
            
        Returns:
            Debate results with final consensus
        """
        logger.info(f"Starting debate with {len(agent_responses)} agents")
        
        self.agent_responses = agent_responses
        
        # Phase 1: Initial Positions
        await self._phase_initial_positions()
        
        # Phase 2-3: Challenge and Rebuttal (multiple rounds if needed)
        for round_num in range(1, self.max_rounds + 1):
            if self._check_consensus():
                logger.info(f"Consensus reached in round {round_num}")
                break
            
            await self._phase_challenge(round_num)
            await self._phase_rebuttal(round_num)
        
        # Phase 4: Synthesis
        synthesis = await self._phase_synthesis()
        
        # Phase 5: Consensus
        consensus = await self._phase_consensus(synthesis)
        
        return {
            "consensus_reached": self.consensus_reached,
            "final_recommendation": self.final_recommendation,
            "confidence": consensus.get("confidence"),
            "synthesis": synthesis,
            "debate_rounds": [r.to_dict() for r in self.rounds],
            "participating_agents": [r.value for r in self.agent_responses.keys()]
        }
    
    async def _phase_initial_positions(self) -> None:
        """Phase 1: Collect initial positions from all agents."""
        round_obj = DebateRound(0, DebatePhase.INITIAL_POSITIONS)
        
        for agent_role, response in self.agent_responses.items():
            statement = f"{agent_role.value.upper()}: {response.recommendation} " \
                       f"(Confidence: {response.confidence:.0%})\n" \
                       f"Key points: {response.analysis[:200]}..."
            
            round_obj.add_statement(agent_role, statement)
        
        self.rounds.append(round_obj)
        logger.info("Phase 1: Initial positions collected")
    
    async def _phase_challenge(self, round_num: int) -> None:
        """Phase 2: Agents challenge conflicting positions."""
        round_obj = DebateRound(round_num, DebatePhase.CHALLENGE)
        
        # Identify conflicts
        conflicts = self._identify_conflicts()
        
        for conflict in conflicts:
            challenger = conflict["agent1"]
            target = conflict["agent2"]
            
            # Generate challenge statement
            challenge = await self._generate_challenge(
                challenger,
                target,
                conflict["disagreement"]
            )
            
            round_obj.add_statement(challenger, challenge, targets=[target])
        
        if conflicts:
            self.rounds.append(round_obj)
            logger.info(f"Phase 2 (Round {round_num}): {len(conflicts)} challenges issued")
    
    async def _phase_rebuttal(self, round_num: int) -> None:
        """Phase 3: Agents respond to challenges."""
        round_obj = DebateRound(round_num, DebatePhase.REBUTTAL)
        
        # Get challenges from previous round
        if len(self.rounds) > 0:
            last_round = self.rounds[-1]
            if last_round.phase == DebatePhase.CHALLENGE:
                for statement in last_round.statements:
                    for target in statement.get("targets", []):
                        # Generate rebuttal
                        rebuttal = await self._generate_rebuttal(
                            target,
                            statement["agent_role"],
                            statement["statement"]
                        )
                        
                        round_obj.add_statement(target, rebuttal)
        
        if round_obj.statements:
            self.rounds.append(round_obj)
            logger.info(f"Phase 3 (Round {round_num}): {len(round_obj.statements)} rebuttals issued")
    
    async def _phase_synthesis(self) -> Dict[str, Any]:
        """Phase 4: Synthesize debate into key findings."""
        logger.info("Phase 4: Synthesizing debate")
        
        # Collect all recommendations
        recommendations = {}
        for agent_role, response in self.agent_responses.items():
            rec = response.recommendation.split()[0]  # Get BUY/SELL/HOLD
            if rec not in recommendations:
                recommendations[rec] = []
            recommendations[rec].append({
                "agent": agent_role.value,
                "confidence": response.confidence
            })
        
        # Collect concerns and opportunities
        all_concerns = []
        all_opportunities = []
        for response in self.agent_responses.values():
            all_concerns.extend(response.concerns)
            all_opportunities.extend(response.opportunities)
        
        # Find common ground
        common_concerns = self._find_common_items(all_concerns)
        common_opportunities = self._find_common_items(all_opportunities)
        
        return {
            "recommendation_distribution": recommendations,
            "common_concerns": common_concerns,
            "common_opportunities": common_opportunities,
            "total_concerns": len(set(all_concerns)),
            "total_opportunities": len(set(all_opportunities))
        }
    
    async def _phase_consensus(self, synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 5: Build consensus and final recommendation."""
        logger.info("Phase 5: Building consensus")
        
        # Weighted voting based on confidence
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        total_weight = 0
        
        for agent_role, response in self.agent_responses.items():
            rec = response.recommendation.split()[0]
            weight = response.confidence
            
            if rec in votes:
                votes[rec] += weight
                total_weight += weight
        
        # Normalize votes
        if total_weight > 0:
            for rec in votes:
                votes[rec] /= total_weight
        
        # Determine final recommendation
        final_rec = max(votes, key=votes.get)
        confidence = votes[final_rec]
        
        # Check if consensus is strong enough
        if confidence >= 0.6:
            self.consensus_reached = True
            self.final_recommendation = final_rec
        else:
            self.consensus_reached = False
            self.final_recommendation = "HOLD - No strong consensus"
        
        logger.info(f"Consensus: {self.final_recommendation} (confidence: {confidence:.0%})")
        
        return {
            "final_recommendation": self.final_recommendation,
            "confidence": confidence,
            "vote_distribution": votes,
            "consensus_reached": self.consensus_reached
        }
    
    def _identify_conflicts(self) -> List[Dict[str, Any]]:
        """Identify conflicting positions between agents."""
        conflicts = []
        
        agents = list(self.agent_responses.items())
        
        for i, (role1, resp1) in enumerate(agents):
            for role2, resp2 in agents[i+1:]:
                # Check if recommendations conflict
                rec1 = resp1.recommendation.split()[0]
                rec2 = resp2.recommendation.split()[0]
                
                if self._are_conflicting(rec1, rec2):
                    conflicts.append({
                        "agent1": role1,
                        "agent2": role2,
                        "disagreement": f"{rec1} vs {rec2}"
                    })
        
        return conflicts
    
    def _are_conflicting(self, rec1: str, rec2: str) -> bool:
        """Check if two recommendations conflict."""
        if rec1 == rec2:
            return False
        
        # BUY vs SELL is a conflict
        if (rec1 == "BUY" and rec2 == "SELL") or (rec1 == "SELL" and rec2 == "BUY"):
            return True
        
        # STRONG BUY vs SELL is a conflict
        if ("BUY" in rec1 and "SELL" in rec2) or ("SELL" in rec1 and "BUY" in rec2):
            return True
        
        return False
    
    async def _generate_challenge(
        self,
        challenger: AgentRole,
        target: AgentRole,
        disagreement: str
    ) -> str:
        """Generate a challenge statement using LLM."""
        challenger_resp = self.agent_responses[challenger]
        target_resp = self.agent_responses[target]
        
        prompt = f"""
        You are the {challenger.value} in an investment committee debate.
        You disagree with the {target.value} regarding {disagreement}.
        
        Your Analysis:
        {challenger_resp.analysis[:500]}
        
        Your Recommendation: {challenger_resp.recommendation}
        Your Key Concerns: {', '.join(challenger_resp.concerns[:3])}
        
        Target's Analysis:
        {target_resp.analysis[:500]}
        Target's Recommendation: {target_resp.recommendation}
        
        Generate a professional, data-driven challenge to the {target.value}'s position.
        Focus on specific metrics, risks, or growth factors that they might have overlooked.
        Keep it concise (under 100 words) and direct.
        """
        
        try:
            return await self.llm_client.generate(prompt, model=self.llm_model)
        except Exception as e:
            logger.error(f"Failed to generate challenge: {e}")
            # Fallback to template
            key_point = challenger_resp.concerns[0] if challenger_resp.concerns else "fundamental analysis"
            return f"{challenger.value.upper()} challenges {target.value.upper()}'s position ({disagreement}). Key concern: {key_point}."
    
    async def _generate_rebuttal(
        self,
        defender: AgentRole,
        challenger: AgentRole,
        challenge: str
    ) -> str:
        """Generate a rebuttal statement using LLM."""
        defender_resp = self.agent_responses[defender]
        
        prompt = f"""
        You are the {defender.value} in an investment committee debate.
        You have been challenged by the {challenger.value}.
        
        Challenge: "{challenge}"
        
        Your Original Analysis:
        {defender_resp.analysis[:500]}
        
        Your Recommendation: {defender_resp.recommendation}
        Your Key Opportunities: {', '.join(defender_resp.opportunities[:3])}
        
        Generate a professional, evidence-based rebuttal.
        Defend your position using your data and frameworks. Acknowledge valid points but explain why your thesis holds.
        Keep it concise (under 100 words).
        """
        
        try:
            return await self.llm_client.generate(prompt, model=self.llm_model)
        except Exception as e:
            logger.error(f"Failed to generate rebuttal: {e}")
            # Fallback to template
            key_point = defender_resp.opportunities[0] if defender_resp.opportunities else "analysis framework"
            return f"{defender.value.upper()} responds: While acknowledging concerns, {key_point} supports our position."
    
    def _check_consensus(self) -> bool:
        """Check if consensus has been reached."""
        recommendations = [r.recommendation.split()[0] 
                          for r in self.agent_responses.values()]
        
        # Count each recommendation
        from collections import Counter
        counts = Counter(recommendations)
        
        # Consensus if >60% agree
        most_common = counts.most_common(1)[0]
        consensus_pct = most_common[1] / len(recommendations)
        
        return consensus_pct >= 0.6
    
    def _find_common_items(self, items: List[str]) -> List[str]:
        """Find items mentioned by multiple agents."""
        from collections import Counter
        counts = Counter(items)
        
        # Return items mentioned by at least 2 agents
        common = [item for item, count in counts.items() if count >= 2]
        return common[:5]  # Top 5
    
    def get_debate_summary(self) -> str:
        """Get a human-readable summary of the debate."""
        parts = ["DEBATE SUMMARY\n"]
        
        parts.append(f"Participants: {len(self.agent_responses)} agents")
        parts.append(f"Rounds: {len(self.rounds)}")
        parts.append(f"Consensus Reached: {'Yes' if self.consensus_reached else 'No'}")
        parts.append(f"Final Recommendation: {self.final_recommendation}\n")
        
        # Summary of each round
        for round_obj in self.rounds:
            parts.append(f"\nRound {round_obj.round_number} ({round_obj.phase.value}):")
            parts.append(f"  Statements: {len(round_obj.statements)}")
        
        return "\n".join(parts)


if __name__ == "__main__":
    # Test debate simulator
    import asyncio
    from app.core.agents.base_agent import AgentResponse, AgentRole
from app.core.llm.llm_client import LLMClient
    
    async def test():
        # Create mock agent responses
        responses = {
            AgentRole.VALUE_INVESTING: AgentResponse(
                agent_role=AgentRole.VALUE_INVESTING,
                analysis="Strong value metrics",
                recommendation="BUY",
                confidence=0.8,
                supporting_data={"pe_ratio": 15},
                frameworks_used=["DCF"],
                concerns=["Market volatility"],
                opportunities=["Undervalued"]
            ),
            AgentRole.RISK_MANAGEMENT: AgentResponse(
                agent_role=AgentRole.RISK_MANAGEMENT,
                analysis="High risk profile",
                recommendation="SELL",
                confidence=0.7,
                supporting_data={"volatility": 0.35},
                frameworks_used=["VaR"],
                concerns=["High volatility"],
                opportunities=[]
            ),
            AgentRole.GROWTH_VC: AgentResponse(
                agent_role=AgentRole.GROWTH_VC,
                analysis="Strong growth",
                recommendation="BUY",
                confidence=0.75,
                supporting_data={"growth_rate": 30},
                frameworks_used=["Rule of 40"],
                concerns=[],
                opportunities=["Market expansion"]
            )
        }
        
        simulator = DebateSimulator(max_rounds=2)
        results = await simulator.run_debate(responses, {})
        
        print(simulator.get_debate_summary())
        print(f"\nFinal: {results['final_recommendation']}")
        print(f"Confidence: {results['confidence']:.0%}")
    
    asyncio.run(test())
