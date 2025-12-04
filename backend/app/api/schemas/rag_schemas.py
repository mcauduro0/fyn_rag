"""
Pydantic schemas for RAG System API endpoints.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    """Request model for RAG queries."""
    
    query: str = Field(..., description="Query string to search in knowledge base", min_length=1)
    top_k: int = Field(default=5, description="Number of results to return", ge=1, le=20)
    category: Optional[str] = Field(default=None, description="Filter by framework category")
    chunk_type: Optional[str] = Field(default=None, description="Filter by chunk type")
    min_score: Optional[float] = Field(default=None, description="Minimum relevance score", ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How to evaluate a company's competitive advantage?",
                "top_k": 5,
                "category": "Value Investing",
                "min_score": 0.5
            }
        }


class FrameworkChunkResponse(BaseModel):
    """Response model for a single framework chunk."""
    
    chunk_id: str
    framework_name: str
    framework_category: str
    chunk_type: str
    content: str
    score: float
    metadata: Dict[str, Any]


class RAGQueryResponse(BaseModel):
    """Response model for RAG queries."""
    
    success: bool
    query: str
    results: List[FrameworkChunkResponse]
    count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "query": "How to evaluate a company's competitive advantage?",
                "results": [
                    {
                        "chunk_id": "Moat_Analysis_overview",
                        "framework_name": "Moat Analysis",
                        "framework_category": "Value Investing",
                        "chunk_type": "overview",
                        "content": "Framework for identifying sustainable competitive advantages...",
                        "score": 0.87,
                        "metadata": {}
                    }
                ],
                "count": 1
            }
        }


class RAGStatsResponse(BaseModel):
    """Response model for RAG system statistics."""
    
    status: str
    total_chunks: Optional[int] = None
    total_frameworks: Optional[int] = None
    index_size: Optional[int] = None
    embedding_model: Optional[str] = None
    reranker_model: Optional[str] = None
    index_type: Optional[str] = None
