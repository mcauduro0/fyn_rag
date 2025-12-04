"""
RAG System API Endpoints.
Provides access to the knowledge base query system.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from typing import List

from app.api.schemas.rag_schemas import (
    RAGQueryRequest,
    RAGQueryResponse,
    RAGStatsResponse,
    FrameworkChunkResponse
)
from app.core.rag.rag_system import get_rag_system

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG System"])


@router.post("/query", response_model=RAGQueryResponse)
async def query_knowledge_base(request: RAGQueryRequest):
    """
    Query the investment knowledge base.
    
    Uses two-stage retrieval (FAISS + CrossEncoder reranking) to find
    the most relevant investment frameworks for your query.
    """
    try:
        rag = get_rag_system()
        
        # Initialize RAG system if not already initialized
        if not rag._initialized:
            logger.info("Initializing RAG system...")
            rag.initialize(auto_build=True)
        
        # Perform query
        results = rag.query(
            query=request.query,
            top_k=request.top_k,
            category=request.category,
            chunk_type=request.chunk_type,
            min_score=request.min_score
        )
        
        # Convert results to response format
        response_results = [
            FrameworkChunkResponse(
                chunk_id=r.chunk_id,
                framework_name=r.framework_name,
                framework_category=r.framework_category,
                chunk_type=r.chunk_type,
                content=r.content,
                score=r.score,
                metadata=r.metadata
            )
            for r in results
        ]
        
        return RAGQueryResponse(
            success=True,
            query=request.query,
            results=response_results,
            count=len(response_results)
        )
        
    except Exception as e:
        logger.error(f"Error querying RAG system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query knowledge base: {str(e)}"
        )


@router.get("/stats", response_model=RAGStatsResponse)
async def get_rag_stats():
    """
    Get statistics about the RAG system.
    
    Returns information about the knowledge base size, models used, and system status.
    """
    try:
        rag = get_rag_system()
        stats = rag.get_stats()
        
        return RAGStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting RAG stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get RAG statistics: {str(e)}"
        )


@router.get("/framework/{framework_name}")
async def get_framework(framework_name: str):
    """
    Get all chunks for a specific framework by name.
    
    Returns all semantic chunks (overview, metrics, application, evaluation, crossref)
    for the specified investment framework.
    """
    try:
        rag = get_rag_system()
        
        # Initialize RAG system if not already initialized
        if not rag._initialized:
            logger.info("Initializing RAG system...")
            rag.initialize(auto_build=True)
        
        # Get framework chunks
        results = rag.get_framework(framework_name)
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Framework not found: {framework_name}"
            )
        
        # Convert results to response format
        response_results = [
            FrameworkChunkResponse(
                chunk_id=r.chunk_id,
                framework_name=r.framework_name,
                framework_category=r.framework_category,
                chunk_type=r.chunk_type,
                content=r.content,
                score=r.score,
                metadata=r.metadata
            )
            for r in results
        ]
        
        return {
            "success": True,
            "framework_name": framework_name,
            "chunks": response_results,
            "count": len(response_results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting framework: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get framework: {str(e)}"
        )


@router.post("/rebuild-index")
async def rebuild_index():
    """
    Rebuild the FAISS index from the knowledge base.
    
    ⚠️ This operation can take several minutes and will temporarily
    make the RAG system unavailable.
    """
    try:
        rag = get_rag_system()
        
        logger.info("Starting index rebuild...")
        rag.build_index(force_rebuild=True)
        
        # Reinitialize after rebuild
        rag._initialized = False
        rag.initialize()
        
        return {
            "success": True,
            "message": "Index rebuilt successfully"
        }
        
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rebuild index: {str(e)}"
        )
