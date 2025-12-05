"""
Data Preparation Module for RAG System.
Handles semantic chunking of investment frameworks into retrievable units.
"""

import json
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class FrameworkChunk:
    """Represents a semantic chunk of an investment framework."""
    
    def __init__(
        self,
        chunk_id: str,
        framework_name: str,
        framework_category: str,
        chunk_type: str,
        content: str,
        metadata: Dict[str, Any]
    ):
        self.chunk_id = chunk_id
        self.framework_name = framework_name
        self.framework_category = framework_category
        self.chunk_type = chunk_type
        self.content = content
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary format."""
        return {
            "chunk_id": self.chunk_id,
            "framework_name": self.framework_name,
            "framework_category": self.framework_category,
            "chunk_type": self.chunk_type,
            "content": self.content,
            "metadata": self.metadata
        }


class DataPreparation:
    """Handles the preparation and chunking of investment frameworks."""
    
    def __init__(self, kb_path: str):
        """
        Initialize data preparation with knowledge base path.
        
        Args:
            kb_path: Path to the investment_kb_enriched.json file
        """
        self.kb_path = Path(kb_path)
        self.frameworks = []
        self.chunks = []
        
    def load_knowledge_base(self) -> None:
        """Load the investment knowledge base from JSON file."""
        logger.info(f"Loading knowledge base from {self.kb_path}")
        
        if not self.kb_path.exists():
            raise FileNotFoundError(f"Knowledge base not found at {self.kb_path}")
        
        with open(self.kb_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle both list (legacy) and dict (enriched) formats
            if isinstance(data, list):
                self.frameworks = data
            else:
                self.frameworks = data.get("frameworks", [])
        
        logger.info(f"Loaded {len(self.frameworks)} frameworks")
    
    def create_semantic_chunks(self) -> List[FrameworkChunk]:
        """
        Create semantic chunks from frameworks.
        Each framework is divided into 5 main chunks:
        1. Overview & Core Concept
        2. Key Metrics & Formulas
        3. Application & Use Cases
        4. Strengths & Limitations
        5. Cross-References & Related Frameworks
        """
        logger.info("Creating semantic chunks from frameworks...")
        self.chunks = []
        
        for idx, framework in enumerate(self.frameworks):
            framework_name = framework.get("name", f"Framework_{idx}")
            category = framework.get("category", "Unknown")
            
            # Chunk 1: Overview & Core Concept
            overview_content = self._build_overview_chunk(framework)
            if overview_content:
                chunk = FrameworkChunk(
                    chunk_id=f"{framework_name}_overview",
                    framework_name=framework_name,
                    framework_category=category,
                    chunk_type="overview",
                    content=overview_content,
                    metadata={
                        "framework_id": idx,
                        "category": category,
                        "description": framework.get("description", "")
                    }
                )
                self.chunks.append(chunk)
            
            # Chunk 2: Key Metrics & Formulas
            metrics_content = self._build_metrics_chunk(framework)
            if metrics_content:
                chunk = FrameworkChunk(
                    chunk_id=f"{framework_name}_metrics",
                    framework_name=framework_name,
                    framework_category=category,
                    chunk_type="metrics",
                    content=metrics_content,
                    metadata={
                        "framework_id": idx,
                        "category": category,
                        "has_formulas": bool(framework.get("formulas"))
                    }
                )
                self.chunks.append(chunk)
            
            # Chunk 3: Application & Use Cases
            application_content = self._build_application_chunk(framework)
            if application_content:
                chunk = FrameworkChunk(
                    chunk_id=f"{framework_name}_application",
                    framework_name=framework_name,
                    framework_category=category,
                    chunk_type="application",
                    content=application_content,
                    metadata={
                        "framework_id": idx,
                        "category": category,
                        "has_case_studies": bool(framework.get("case_studies"))
                    }
                )
                self.chunks.append(chunk)
            
            # Chunk 4: Strengths & Limitations
            evaluation_content = self._build_evaluation_chunk(framework)
            if evaluation_content:
                chunk = FrameworkChunk(
                    chunk_id=f"{framework_name}_evaluation",
                    framework_name=framework_name,
                    framework_category=category,
                    chunk_type="evaluation",
                    content=evaluation_content,
                    metadata={
                        "framework_id": idx,
                        "category": category
                    }
                )
                self.chunks.append(chunk)
            
            # Chunk 5: Cross-References
            crossref_content = self._build_crossref_chunk(framework)
            if crossref_content:
                chunk = FrameworkChunk(
                    chunk_id=f"{framework_name}_crossref",
                    framework_name=framework_name,
                    framework_category=category,
                    chunk_type="crossref",
                    content=crossref_content,
                    metadata={
                        "framework_id": idx,
                        "category": category,
                        "related_frameworks": framework.get("related_frameworks", [])
                    }
                )
                self.chunks.append(chunk)
        
        logger.info(f"Created {len(self.chunks)} semantic chunks from {len(self.frameworks)} frameworks")
        return self.chunks
    
    def _build_overview_chunk(self, framework: Dict[str, Any]) -> str:
        """Build overview chunk content."""
        parts = []
        
        if name := framework.get("name"):
            parts.append(f"Framework: {name}")
        
        if category := framework.get("category"):
            parts.append(f"Category: {category}")
        
        if description := framework.get("description"):
            parts.append(f"Description: {description}")
        
        if core_concept := framework.get("core_concept"):
            parts.append(f"Core Concept: {core_concept}")
        
        if origin := framework.get("origin"):
            parts.append(f"Origin: {origin}")
        
        return "\n\n".join(parts)
    
    def _build_metrics_chunk(self, framework: Dict[str, Any]) -> str:
        """Build metrics and formulas chunk content."""
        parts = []
        
        if key_metrics := framework.get("key_metrics"):
            parts.append("Key Metrics:")
            if isinstance(key_metrics, list):
                parts.append("\n".join(f"- {metric}" for metric in key_metrics))
            else:
                parts.append(str(key_metrics))
        
        if formulas := framework.get("formulas"):
            parts.append("\nFormulas:")
            if isinstance(formulas, list):
                for formula in formulas:
                    if isinstance(formula, dict):
                        parts.append(f"- {formula.get('name', 'Formula')}: {formula.get('formula', '')}")
                        if explanation := formula.get('explanation'):
                            parts.append(f"  Explanation: {explanation}")
                    else:
                        parts.append(f"- {formula}")
            else:
                parts.append(str(formulas))
        
        return "\n".join(parts)
    
    def _build_application_chunk(self, framework: Dict[str, Any]) -> str:
        """Build application and use cases chunk content."""
        parts = []
        
        if application := framework.get("application"):
            parts.append(f"Application: {application}")
        
        if use_cases := framework.get("use_cases"):
            parts.append("\nUse Cases:")
            if isinstance(use_cases, list):
                parts.append("\n".join(f"- {case}" for case in use_cases))
            else:
                parts.append(str(use_cases))
        
        if case_studies := framework.get("case_studies"):
            parts.append("\nCase Studies:")
            if isinstance(case_studies, list):
                for study in case_studies:
                    if isinstance(study, dict):
                        parts.append(f"- {study.get('company', 'Company')}: {study.get('description', '')}")
                    else:
                        parts.append(f"- {study}")
            else:
                parts.append(str(case_studies))
        
        return "\n".join(parts)
    
    def _build_evaluation_chunk(self, framework: Dict[str, Any]) -> str:
        """Build evaluation chunk with strengths and limitations."""
        parts = []
        
        if strengths := framework.get("strengths"):
            parts.append("Strengths:")
            if isinstance(strengths, list):
                parts.append("\n".join(f"- {strength}" for strength in strengths))
            else:
                parts.append(str(strengths))
        
        if limitations := framework.get("limitations"):
            parts.append("\nLimitations:")
            if isinstance(limitations, list):
                parts.append("\n".join(f"- {limitation}" for limitation in limitations))
            else:
                parts.append(str(limitations))
        
        if best_for := framework.get("best_for"):
            parts.append(f"\nBest For: {best_for}")
        
        return "\n".join(parts)
    
    def _build_crossref_chunk(self, framework: Dict[str, Any]) -> str:
        """Build cross-reference chunk content."""
        parts = []
        
        if related_frameworks := framework.get("related_frameworks"):
            parts.append("Related Frameworks:")
            if isinstance(related_frameworks, list):
                parts.append("\n".join(f"- {ref}" for ref in related_frameworks))
            else:
                parts.append(str(related_frameworks))
        
        if citations := framework.get("citations"):
            parts.append("\nCitations:")
            if isinstance(citations, list):
                for citation in citations:
                    if isinstance(citation, dict):
                        parts.append(f"- {citation.get('author', 'Unknown')}: {citation.get('title', 'Untitled')}")
                    else:
                        parts.append(f"- {citation}")
            else:
                parts.append(str(citations))
        
        return "\n".join(parts)
    
    def save_chunks(self, output_path: str) -> None:
        """Save chunks to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        chunks_data = [chunk.to_dict() for chunk in self.chunks]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(chunks_data)} chunks to {output_file}")
    
    def get_chunks(self) -> List[FrameworkChunk]:
        """Get the list of created chunks."""
        return self.chunks


if __name__ == "__main__":
    # Test the data preparation module
    logging.basicConfig(level=logging.INFO)
    
    kb_path = "/app/app/core/rag/investment_kb_enriched.json"
    output_path = "/app/data/faiss_index/framework_chunks.json"
    
    prep = DataPreparation(kb_path)
    prep.load_knowledge_base()
    chunks = prep.create_semantic_chunks()
    prep.save_chunks(output_path)
    
    print(f"Successfully created {len(chunks)} chunks")
