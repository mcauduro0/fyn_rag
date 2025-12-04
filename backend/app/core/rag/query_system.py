"""
Query System Module for RAG.
Implements two-stage retrieval: FAISS similarity search + CrossEncoder reranking.
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder

logger = logging.getLogger(__name__)


class RetrievalResult:
    """Represents a single retrieval result."""
    
    def __init__(
        self,
        chunk_id: str,
        framework_name: str,
        framework_category: str,
        chunk_type: str,
        content: str,
        score: float,
        metadata: Dict[str, Any]
    ):
        self.chunk_id = chunk_id
        self.framework_name = framework_name
        self.framework_category = framework_category
        self.chunk_type = chunk_type
        self.content = content
        self.score = score
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "framework_name": self.framework_name,
            "framework_category": self.framework_category,
            "chunk_type": self.chunk_type,
            "content": self.content,
            "score": float(self.score),
            "metadata": self.metadata
        }


class QuerySystem:
    """Handles querying the RAG system with two-stage retrieval."""
    
    def __init__(
        self,
        index_path: str,
        metadata_path: str,
        embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2",
        reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        """
        Initialize the query system.
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to metadata JSON file
            embedding_model_name: Name of embedding model
            reranker_model_name: Name of cross-encoder reranker model
        """
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.embedding_model_name = embedding_model_name
        self.reranker_model_name = reranker_model_name
        
        self.index: Optional[faiss.Index] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.reranker: Optional[CrossEncoder] = None
        self.chunks: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        
    def initialize(self) -> None:
        """Initialize all components of the query system."""
        logger.info("Initializing Query System...")
        
        # Load FAISS index
        logger.info(f"Loading FAISS index from {self.index_path}")
        if not self.index_path.exists():
            raise FileNotFoundError(f"Index file not found at {self.index_path}")
        self.index = faiss.read_index(str(self.index_path))
        logger.info(f"Index loaded. Total vectors: {self.index.ntotal}")
        
        # Load metadata
        logger.info(f"Loading metadata from {self.metadata_path}")
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found at {self.metadata_path}")
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        self.chunks = self.metadata.get('chunks', [])
        logger.info(f"Metadata loaded. Total chunks: {len(self.chunks)}")
        
        # Load embedding model
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Load reranker model
        logger.info(f"Loading reranker model: {self.reranker_model_name}")
        self.reranker = CrossEncoder(self.reranker_model_name)
        
        logger.info("Query System initialized successfully!")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 20,
        rerank_top_k: int = 5,
        min_score: Optional[float] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks using two-stage retrieval.
        
        Stage 1: FAISS similarity search (fast, approximate)
        Stage 2: CrossEncoder reranking (slow, accurate)
        
        Args:
            query: Query string
            top_k: Number of candidates to retrieve in stage 1
            rerank_top_k: Number of results to return after reranking
            min_score: Minimum score threshold (optional)
            
        Returns:
            List of RetrievalResult objects
        """
        if not self.index or not self.embedding_model or not self.reranker:
            raise RuntimeError("Query system not initialized. Call initialize() first.")
        
        # Stage 1: FAISS similarity search
        logger.info(f"Stage 1: Retrieving top {top_k} candidates with FAISS")
        candidates = self._faiss_search(query, top_k)
        
        # Stage 2: CrossEncoder reranking
        logger.info(f"Stage 2: Reranking with CrossEncoder")
        reranked_results = self._rerank(query, candidates, rerank_top_k)
        
        # Apply minimum score filter if specified
        if min_score is not None:
            reranked_results = [r for r in reranked_results if r.score >= min_score]
            logger.info(f"Filtered to {len(reranked_results)} results with score >= {min_score}")
        
        return reranked_results
    
    def _faiss_search(self, query: str, top_k: int) -> List[Tuple[int, float]]:
        """
        Perform FAISS similarity search.
        
        Args:
            query: Query string
            top_k: Number of results to retrieve
            
        Returns:
            List of (chunk_index, distance) tuples
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Convert to list of tuples
        candidates = [
            (int(idx), float(dist))
            for idx, dist in zip(indices[0], distances[0])
            if idx != -1  # Filter out invalid indices
        ]
        
        return candidates
    
    def _rerank(
        self,
        query: str,
        candidates: List[Tuple[int, float]],
        top_k: int
    ) -> List[RetrievalResult]:
        """
        Rerank candidates using CrossEncoder.
        
        Args:
            query: Query string
            candidates: List of (chunk_index, distance) tuples from FAISS
            top_k: Number of top results to return
            
        Returns:
            List of RetrievalResult objects, sorted by reranking score
        """
        # Prepare query-document pairs for reranking
        pairs = []
        chunk_indices = []
        
        for idx, _ in candidates:
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                pairs.append([query, chunk['content']])
                chunk_indices.append(idx)
        
        # Get reranking scores
        rerank_scores = self.reranker.predict(pairs)
        
        # Create RetrievalResult objects
        results = []
        for idx, score in zip(chunk_indices, rerank_scores):
            chunk = self.chunks[idx]
            result = RetrievalResult(
                chunk_id=chunk['chunk_id'],
                framework_name=chunk['framework_name'],
                framework_category=chunk['framework_category'],
                chunk_type=chunk['chunk_type'],
                content=chunk['content'],
                score=float(score),
                metadata=chunk.get('metadata', {})
            )
            results.append(result)
        
        # Sort by reranking score (descending)
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Return top_k results
        return results[:top_k]
    
    def retrieve_by_category(
        self,
        query: str,
        category: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Retrieve chunks filtered by framework category.
        
        Args:
            query: Query string
            category: Framework category to filter by
            top_k: Number of results to return
            
        Returns:
            List of RetrievalResult objects from the specified category
        """
        # Retrieve more candidates to account for filtering
        all_results = self.retrieve(query, top_k=top_k * 4, rerank_top_k=top_k * 2)
        
        # Filter by category
        filtered_results = [
            r for r in all_results
            if r.framework_category.lower() == category.lower()
        ]
        
        return filtered_results[:top_k]
    
    def retrieve_by_chunk_type(
        self,
        query: str,
        chunk_type: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Retrieve chunks filtered by chunk type.
        
        Args:
            query: Query string
            chunk_type: Chunk type to filter by (overview, metrics, application, etc.)
            top_k: Number of results to return
            
        Returns:
            List of RetrievalResult objects of the specified type
        """
        # Retrieve more candidates to account for filtering
        all_results = self.retrieve(query, top_k=top_k * 4, rerank_top_k=top_k * 2)
        
        # Filter by chunk type
        filtered_results = [
            r for r in all_results
            if r.chunk_type.lower() == chunk_type.lower()
        ]
        
        return filtered_results[:top_k]
    
    def get_framework_by_name(self, framework_name: str) -> List[RetrievalResult]:
        """
        Retrieve all chunks for a specific framework.
        
        Args:
            framework_name: Name of the framework
            
        Returns:
            List of all chunks for the framework
        """
        results = []
        
        for chunk in self.chunks:
            if chunk['framework_name'].lower() == framework_name.lower():
                result = RetrievalResult(
                    chunk_id=chunk['chunk_id'],
                    framework_name=chunk['framework_name'],
                    framework_category=chunk['framework_category'],
                    chunk_type=chunk['chunk_type'],
                    content=chunk['content'],
                    score=1.0,  # Perfect match
                    metadata=chunk.get('metadata', {})
                )
                results.append(result)
        
        return results


if __name__ == "__main__":
    # Test the query system
    logging.basicConfig(level=logging.INFO)
    
    index_path = "/app/data/faiss_index/faiss.index"
    metadata_path = "/app/data/faiss_index/metadata.json"
    
    query_system = QuerySystem(index_path, metadata_path)
    query_system.initialize()
    
    # Test query
    test_query = "How to value a technology company with high growth potential?"
    results = query_system.retrieve(test_query, top_k=20, rerank_top_k=5)
    
    print(f"\nQuery: {test_query}")
    print(f"\nTop {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.framework_name} ({result.chunk_type})")
        print(f"   Score: {result.score:.4f}")
        print(f"   Content preview: {result.content[:200]}...")
