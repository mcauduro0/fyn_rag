"""
RAG System Integration Module.
Provides a unified interface for the complete RAG pipeline.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.core.rag.data_preparation import DataPreparation
from app.core.rag.embedding_indexer import EmbeddingIndexer, build_index
from app.core.rag.query_system import QuerySystem, RetrievalResult

logger = logging.getLogger(__name__)


class RAGSystem:
    """
    Unified RAG System interface.
    Handles initialization, indexing, and querying of investment frameworks.
    """
    
    def __init__(
        self,
        kb_path: str,
        index_dir: str,
        embedding_model: str = "sentence-transformers/all-mpnet-base-v2",
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        index_type: str = "flatl2"
    ):
        """
        Initialize RAG System.
        
        Args:
            kb_path: Path to investment_kb_enriched.json
            index_dir: Directory to store FAISS index and metadata
            embedding_model: Sentence-transformers model name
            reranker_model: Cross-encoder reranker model name
            index_type: Type of FAISS index
        """
        self.kb_path = Path(kb_path)
        self.index_dir = Path(index_dir)
        self.embedding_model = embedding_model
        self.reranker_model = reranker_model
        self.index_type = index_type
        
        # Paths for index artifacts
        self.chunks_path = self.index_dir / "framework_chunks.json"
        self.index_path = self.index_dir / "faiss.index"
        self.metadata_path = self.index_dir / "metadata.json"
        
        self.query_system: Optional[QuerySystem] = None
        self._initialized = False
    
    def build_index(self, force_rebuild: bool = False) -> None:
        """
        Build or rebuild the FAISS index from knowledge base.
        
        Args:
            force_rebuild: If True, rebuild even if index exists
        """
        # Check if index already exists
        if not force_rebuild and self.index_path.exists():
            logger.info("Index already exists. Use force_rebuild=True to rebuild.")
            return
        
        logger.info("Building RAG index...")
        
        # Step 1: Prepare data (chunking)
        logger.info("Step 1: Preparing data and creating chunks...")
        prep = DataPreparation(str(self.kb_path))
        prep.load_knowledge_base()
        chunks = prep.create_semantic_chunks()
        
        # Create index directory if it doesn't exist
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Save chunks
        prep.save_chunks(str(self.chunks_path))
        
        # Step 2: Generate embeddings and create index
        logger.info("Step 2: Generating embeddings and creating FAISS index...")
        build_index(
            chunks_path=str(self.chunks_path),
            index_output_path=str(self.index_path),
            metadata_output_path=str(self.metadata_path),
            model_name=self.embedding_model,
            index_type=self.index_type
        )
        
        logger.info("Index building complete!")
    
    def initialize(self, auto_build: bool = True) -> None:
        """
        Initialize the RAG system for querying.
        
        Args:
            auto_build: If True, automatically build index if it doesn't exist
        """
        if self._initialized:
            logger.info("RAG System already initialized")
            return
        
        # Check if index exists
        if not self.index_path.exists():
            if auto_build:
                logger.info("Index not found. Building index...")
                self.build_index()
            else:
                raise FileNotFoundError(
                    f"Index not found at {self.index_path}. "
                    "Call build_index() first or set auto_build=True."
                )
        
        # Initialize query system
        logger.info("Initializing query system...")
        self.query_system = QuerySystem(
            index_path=str(self.index_path),
            metadata_path=str(self.metadata_path),
            embedding_model_name=self.embedding_model,
            reranker_model_name=self.reranker_model
        )
        self.query_system.initialize()
        
        self._initialized = True
        logger.info("RAG System initialized successfully!")
    
    def query(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        chunk_type: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> List[RetrievalResult]:
        """
        Query the RAG system for relevant frameworks.
        
        Args:
            query: Query string
            top_k: Number of results to return
            category: Optional category filter
            chunk_type: Optional chunk type filter
            min_score: Optional minimum score threshold
            
        Returns:
            List of RetrievalResult objects
        """
        if not self._initialized:
            raise RuntimeError("RAG System not initialized. Call initialize() first.")
        
        # Apply filters if specified
        if category:
            return self.query_system.retrieve_by_category(query, category, top_k)
        elif chunk_type:
            return self.query_system.retrieve_by_chunk_type(query, chunk_type, top_k)
        else:
            return self.query_system.retrieve(
                query,
                top_k=top_k * 4,  # Retrieve more candidates
                rerank_top_k=top_k,
                min_score=min_score
            )
    
    def get_framework(self, framework_name: str) -> List[RetrievalResult]:
        """
        Get all chunks for a specific framework by name.
        
        Args:
            framework_name: Name of the framework
            
        Returns:
            List of all chunks for the framework
        """
        if not self._initialized:
            raise RuntimeError("RAG System not initialized. Call initialize() first.")
        
        return self.query_system.get_framework_by_name(framework_name)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.
        
        Returns:
            Dictionary with system statistics
        """
        if not self._initialized:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "total_chunks": len(self.query_system.chunks),
            "total_frameworks": len(set(c['framework_name'] for c in self.query_system.chunks)),
            "index_size": self.query_system.index.ntotal if self.query_system.index else 0,
            "embedding_model": self.embedding_model,
            "reranker_model": self.reranker_model,
            "index_type": self.index_type
        }


# Global RAG system instance
_rag_system: Optional[RAGSystem] = None


def get_rag_system() -> RAGSystem:
    """
    Get or create the global RAG system instance.
    
    Returns:
        RAGSystem instance
    """
    global _rag_system
    
    if _rag_system is None:
        # Default paths (can be overridden via environment variables)
        kb_path = "/app/app/core/rag/investment_kb_enriched.json"
        index_dir = "/app/data/faiss_index"
        
        _rag_system = RAGSystem(
            kb_path=kb_path,
            index_dir=index_dir
        )
    
    return _rag_system


if __name__ == "__main__":
    # Test the RAG system
    logging.basicConfig(level=logging.INFO)
    
    rag = get_rag_system()
    
    # Build index (only if needed)
    rag.build_index(force_rebuild=False)
    
    # Initialize for querying
    rag.initialize()
    
    # Get stats
    stats = rag.get_stats()
    print(f"\nRAG System Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test query
    test_query = "How to evaluate a company's competitive advantage?"
    print(f"\nTest Query: {test_query}")
    
    results = rag.query(test_query, top_k=3)
    print(f"\nTop {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.framework_name} ({result.chunk_type})")
        print(f"   Category: {result.framework_category}")
        print(f"   Score: {result.score:.4f}")
        print(f"   Content: {result.content[:150]}...")
