"""
Agent Memory System - Manages context, history, and learning for agents.
Provides short-term and long-term memory capabilities.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
import json

logger = logging.getLogger(__name__)


class MemoryEntry:
    """Represents a single memory entry."""
    
    def __init__(
        self,
        entry_id: str,
        entry_type: str,
        content: Dict[str, Any],
        importance: float = 0.5,
        tags: Optional[List[str]] = None
    ):
        self.entry_id = entry_id
        self.entry_type = entry_type  # analysis, decision, feedback, learning
        self.content = content
        self.importance = importance  # 0-1 scale
        self.tags = tags or []
        self.timestamp = datetime.utcnow()
        self.access_count = 0
        self.last_accessed = self.timestamp
    
    def access(self) -> None:
        """Record an access to this memory."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
    
    def calculate_relevance(self, current_time: datetime) -> float:
        """
        Calculate relevance score based on recency, importance, and access frequency.
        
        Args:
            current_time: Current timestamp
            
        Returns:
            Relevance score (0-1)
        """
        # Recency factor (exponential decay)
        age_hours = (current_time - self.timestamp).total_seconds() / 3600
        recency = 0.5 ** (age_hours / 168)  # Half-life of 1 week
        
        # Frequency factor
        frequency = min(self.access_count / 10, 1.0)  # Cap at 10 accesses
        
        # Weighted combination
        relevance = (0.4 * recency) + (0.4 * self.importance) + (0.2 * frequency)
        
        return relevance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entry_id": self.entry_id,
            "entry_type": self.entry_type,
            "content": self.content,
            "importance": self.importance,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat()
        }


class AgentMemory:
    """
    Agent Memory System manages context and learning for individual agents.
    
    Features:
    - Short-term memory (recent interactions)
    - Long-term memory (important learnings)
    - Context retrieval with relevance scoring
    - Memory consolidation and pruning
    """
    
    def __init__(
        self,
        agent_id: str,
        short_term_capacity: int = 50,
        long_term_capacity: int = 500
    ):
        """
        Initialize agent memory.
        
        Args:
            agent_id: Unique agent identifier
            short_term_capacity: Max entries in short-term memory
            long_term_capacity: Max entries in long-term memory
        """
        self.agent_id = agent_id
        self.short_term_capacity = short_term_capacity
        self.long_term_capacity = long_term_capacity
        
        # Short-term memory (FIFO queue)
        self.short_term_memory: deque = deque(maxlen=short_term_capacity)
        
        # Long-term memory (dict by entry_id)
        self.long_term_memory: Dict[str, MemoryEntry] = {}
        
        # Entry counter for unique IDs
        self.entry_counter = 0
        
        logger.info(f"Initialized memory for agent {agent_id}")
    
    def add_memory(
        self,
        entry_type: str,
        content: Dict[str, Any],
        importance: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Add a new memory entry.
        
        Args:
            entry_type: Type of memory (analysis, decision, feedback, learning)
            content: Memory content
            importance: Importance score (0-1)
            tags: Optional tags for categorization
            
        Returns:
            Entry ID
        """
        self.entry_counter += 1
        entry_id = f"{self.agent_id}_mem_{self.entry_counter}"
        
        entry = MemoryEntry(
            entry_id=entry_id,
            entry_type=entry_type,
            content=content,
            importance=importance,
            tags=tags
        )
        
        # Add to short-term memory
        self.short_term_memory.append(entry)
        
        # If important enough, add to long-term memory
        if importance >= 0.7:
            self._add_to_long_term(entry)
        
        logger.debug(f"Added memory {entry_id} (type={entry_type}, importance={importance})")
        
        return entry_id
    
    def _add_to_long_term(self, entry: MemoryEntry) -> None:
        """Add entry to long-term memory."""
        self.long_term_memory[entry.entry_id] = entry
        
        # Prune if over capacity
        if len(self.long_term_memory) > self.long_term_capacity:
            self._prune_long_term_memory()
    
    def _prune_long_term_memory(self) -> None:
        """Prune long-term memory to capacity."""
        current_time = datetime.utcnow()
        
        # Calculate relevance for all entries
        entries_with_relevance = [
            (entry_id, entry.calculate_relevance(current_time))
            for entry_id, entry in self.long_term_memory.items()
        ]
        
        # Sort by relevance (descending)
        entries_with_relevance.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top entries
        keep_ids = set(e[0] for e in entries_with_relevance[:self.long_term_capacity])
        
        # Remove low-relevance entries
        removed = 0
        for entry_id in list(self.long_term_memory.keys()):
            if entry_id not in keep_ids:
                del self.long_term_memory[entry_id]
                removed += 1
        
        logger.info(f"Pruned {removed} entries from long-term memory")
    
    def retrieve_context(
        self,
        query_tags: Optional[List[str]] = None,
        entry_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """
        Retrieve relevant context from memory.
        
        Args:
            query_tags: Filter by tags
            entry_types: Filter by entry types
            limit: Maximum number of entries to return
            
        Returns:
            List of relevant memory entries
        """
        current_time = datetime.utcnow()
        candidates = []
        
        # Collect candidates from both memories
        for entry in self.short_term_memory:
            if self._matches_filters(entry, query_tags, entry_types):
                candidates.append(entry)
        
        for entry in self.long_term_memory.values():
            if self._matches_filters(entry, query_tags, entry_types):
                candidates.append(entry)
        
        # Remove duplicates (prefer long-term version)
        seen_ids = set()
        unique_candidates = []
        for entry in candidates:
            if entry.entry_id not in seen_ids:
                unique_candidates.append(entry)
                seen_ids.add(entry.entry_id)
        
        # Sort by relevance
        unique_candidates.sort(
            key=lambda e: e.calculate_relevance(current_time),
            reverse=True
        )
        
        # Mark as accessed
        for entry in unique_candidates[:limit]:
            entry.access()
        
        logger.debug(f"Retrieved {len(unique_candidates[:limit])} context entries")
        
        return unique_candidates[:limit]
    
    def _matches_filters(
        self,
        entry: MemoryEntry,
        query_tags: Optional[List[str]],
        entry_types: Optional[List[str]]
    ) -> bool:
        """Check if entry matches filters."""
        # Check entry type
        if entry_types and entry.entry_type not in entry_types:
            return False
        
        # Check tags
        if query_tags:
            if not any(tag in entry.tags for tag in query_tags):
                return False
        
        return True
    
    def get_recent_analyses(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent analysis entries."""
        entries = self.retrieve_context(
            entry_types=["analysis"],
            limit=limit
        )
        return [e.to_dict() for e in entries]
    
    def get_recent_decisions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent decision entries."""
        entries = self.retrieve_context(
            entry_types=["decision"],
            limit=limit
        )
        return [e.to_dict() for e in entries]
    
    def consolidate_memories(self) -> Dict[str, Any]:
        """
        Consolidate short-term memories into long-term.
        Called periodically to move important memories.
        
        Returns:
            Consolidation statistics
        """
        promoted = 0
        
        for entry in self.short_term_memory:
            # Promote if accessed frequently or important
            if entry.access_count >= 3 or entry.importance >= 0.6:
                if entry.entry_id not in self.long_term_memory:
                    self._add_to_long_term(entry)
                    promoted += 1
        
        logger.info(f"Consolidated memories: {promoted} promoted to long-term")
        
        return {
            "promoted": promoted,
            "short_term_size": len(self.short_term_memory),
            "long_term_size": len(self.long_term_memory)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        current_time = datetime.utcnow()
        
        # Count by type
        type_counts = {}
        for entry in list(self.short_term_memory) + list(self.long_term_memory.values()):
            type_counts[entry.entry_type] = type_counts.get(entry.entry_type, 0) + 1
        
        # Average relevance
        all_entries = list(self.short_term_memory) + list(self.long_term_memory.values())
        avg_relevance = sum(e.calculate_relevance(current_time) for e in all_entries) / len(all_entries) if all_entries else 0
        
        return {
            "agent_id": self.agent_id,
            "short_term_size": len(self.short_term_memory),
            "long_term_size": len(self.long_term_memory),
            "total_entries": self.entry_counter,
            "type_distribution": type_counts,
            "average_relevance": avg_relevance
        }
    
    def clear(self) -> None:
        """Clear all memories."""
        self.short_term_memory.clear()
        self.long_term_memory.clear()
        logger.info(f"Cleared all memories for agent {self.agent_id}")
    
    def export_to_json(self) -> str:
        """Export memories to JSON string."""
        data = {
            "agent_id": self.agent_id,
            "short_term_memory": [e.to_dict() for e in self.short_term_memory],
            "long_term_memory": [e.to_dict() for e in self.long_term_memory.values()],
            "statistics": self.get_statistics()
        }
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_str: str) -> None:
        """Import memories from JSON string."""
        data = json.loads(json_str)
        
        # Clear existing
        self.clear()
        
        # Import short-term
        for entry_dict in data.get("short_term_memory", []):
            entry = self._dict_to_entry(entry_dict)
            self.short_term_memory.append(entry)
        
        # Import long-term
        for entry_dict in data.get("long_term_memory", []):
            entry = self._dict_to_entry(entry_dict)
            self.long_term_memory[entry.entry_id] = entry
        
        logger.info(f"Imported memories for agent {self.agent_id}")
    
    def _dict_to_entry(self, entry_dict: Dict[str, Any]) -> MemoryEntry:
        """Convert dictionary to MemoryEntry."""
        entry = MemoryEntry(
            entry_id=entry_dict["entry_id"],
            entry_type=entry_dict["entry_type"],
            content=entry_dict["content"],
            importance=entry_dict["importance"],
            tags=entry_dict["tags"]
        )
        entry.timestamp = datetime.fromisoformat(entry_dict["timestamp"])
        entry.access_count = entry_dict["access_count"]
        entry.last_accessed = datetime.fromisoformat(entry_dict["last_accessed"])
        return entry


class MemoryManager:
    """Manages memories for multiple agents."""
    
    def __init__(self):
        self.agent_memories: Dict[str, AgentMemory] = {}
        logger.info("Initialized Memory Manager")
    
    def get_agent_memory(self, agent_id: str) -> AgentMemory:
        """Get or create memory for an agent."""
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = AgentMemory(agent_id)
        return self.agent_memories[agent_id]
    
    def consolidate_all(self) -> Dict[str, Any]:
        """Consolidate memories for all agents."""
        results = {}
        for agent_id, memory in self.agent_memories.items():
            results[agent_id] = memory.consolidate_memories()
        return results
    
    def get_all_statistics(self) -> Dict[str, Any]:
        """Get statistics for all agents."""
        return {
            agent_id: memory.get_statistics()
            for agent_id, memory in self.agent_memories.items()
        }


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


if __name__ == "__main__":
    # Test memory system
    memory = AgentMemory("test_agent")
    
    # Add some memories
    memory.add_memory(
        entry_type="analysis",
        content={"ticker": "AAPL", "recommendation": "BUY"},
        importance=0.8,
        tags=["tech", "value"]
    )
    
    memory.add_memory(
        entry_type="decision",
        content={"action": "bought", "shares": 100},
        importance=0.9,
        tags=["tech"]
    )
    
    # Retrieve context
    context = memory.retrieve_context(query_tags=["tech"], limit=5)
    print(f"Retrieved {len(context)} entries")
    
    # Statistics
    stats = memory.get_statistics()
    print(f"Statistics: {stats}")
