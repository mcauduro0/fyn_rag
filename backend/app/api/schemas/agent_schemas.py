"""
Pydantic schemas for agent-related API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum


class AssetType(str, Enum):
    """Type of asset to analyze."""
    LISTED = "listed"  # Public stocks with ticker
    ILLIQUID = "illiquid"  # Private companies, documents


class AnalysisRequest(BaseModel):
    """Request for complete investment analysis."""
    
    asset_type: AssetType = Field(..., description="Type of asset")
    
    # For listed assets
    ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    
    # For illiquid assets
    company_name: Optional[str] = Field(None, description="Company name")
    documents: Optional[List[str]] = Field(None, description="Document paths or URLs")
    
    # Optional context
    additional_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context for analysis"
    )
    
    # Analysis options
    include_debate: bool = Field(True, description="Include debate simulation")
    generate_report: bool = Field(True, description="Generate investment report")
    report_type: str = Field("one_pager", description="Report type (one_pager, comprehensive, presentation)")
    
    class Config:
        schema_extra = {
            "example": {
                "asset_type": "listed",
                "ticker": "AAPL",
                "additional_context": {"target_price": 200},
                "include_debate": True,
                "generate_report": True,
                "report_type": "one_pager"
            }
        }


class AgentAnalysisResponse(BaseModel):
    """Response from a single agent."""
    
    agent_role: str = Field(..., description="Agent role")
    analysis: str = Field(..., description="Analysis text")
    recommendation: str = Field(..., description="Investment recommendation")
    confidence: float = Field(..., description="Confidence score (0-1)")
    supporting_data: Dict[str, Any] = Field(..., description="Supporting data")
    frameworks_used: List[str] = Field(..., description="Frameworks applied")
    concerns: List[str] = Field(..., description="Investment concerns")
    opportunities: List[str] = Field(..., description="Investment opportunities")


class DebateResult(BaseModel):
    """Result of debate simulation."""
    
    consensus_reached: bool = Field(..., description="Whether consensus was reached")
    final_recommendation: str = Field(..., description="Final recommendation")
    confidence: float = Field(..., description="Consensus confidence")
    debate_rounds: List[Dict[str, Any]] = Field(..., description="Debate rounds")
    synthesis: Dict[str, Any] = Field(..., description="Synthesis of debate")


class AnalysisResponse(BaseModel):
    """Complete analysis response."""
    
    request_id: str = Field(..., description="Unique request ID")
    asset_type: AssetType = Field(..., description="Asset type")
    ticker: Optional[str] = Field(None, description="Ticker symbol")
    company_name: Optional[str] = Field(None, description="Company name")
    
    # Agent analyses
    agent_analyses: Dict[str, AgentAnalysisResponse] = Field(
        ...,
        description="Analyses from each agent"
    )
    
    # Debate results
    debate_result: Optional[DebateResult] = Field(
        None,
        description="Debate simulation results"
    )
    
    # Final outputs
    final_recommendation: str = Field(..., description="Final recommendation")
    confidence: float = Field(..., description="Overall confidence")
    
    # Report
    report_markdown: Optional[str] = Field(None, description="Generated report in Markdown")
    
    # Metadata
    analysis_duration: float = Field(..., description="Analysis duration in seconds")
    timestamp: str = Field(..., description="Analysis timestamp")


class ReportGenerationRequest(BaseModel):
    """Request for report generation."""
    
    company_name: str = Field(..., description="Company name")
    ticker: Optional[str] = Field(None, description="Stock ticker")
    analysis_data: Dict[str, Any] = Field(..., description="Analysis data from agents")
    recommendation: str = Field(..., description="Final recommendation")
    confidence: float = Field(..., description="Confidence score")
    report_type: str = Field("one_pager", description="Report type")
    
    class Config:
        schema_extra = {
            "example": {
                "company_name": "Apple Inc.",
                "ticker": "AAPL",
                "analysis_data": {},
                "recommendation": "BUY",
                "confidence": 0.8,
                "report_type": "one_pager"
            }
        }


class ReportResponse(BaseModel):
    """Response with generated report."""
    
    report_type: str = Field(..., description="Report type")
    report_markdown: str = Field(..., description="Report in Markdown format")
    company_name: str = Field(..., description="Company name")
    ticker: Optional[str] = Field(None, description="Ticker symbol")
    generated_at: str = Field(..., description="Generation timestamp")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Health status")
    uptime_seconds: float = Field(..., description="System uptime")
    error_rate_percent: float = Field(..., description="Error rate percentage")
    avg_latency_seconds: float = Field(..., description="Average latency")
    total_requests: float = Field(..., description="Total requests processed")


class PerformanceMetrics(BaseModel):
    """Performance metrics response."""
    
    health: HealthCheckResponse = Field(..., description="Health status")
    api_metrics: Dict[str, Any] = Field(..., description="API metrics")
    agent_metrics: Dict[str, Any] = Field(..., description="Agent metrics")
    cache_metrics: Dict[str, Any] = Field(..., description="Cache metrics")
    rag_metrics: Dict[str, Any] = Field(..., description="RAG metrics")
    system_metrics: Dict[str, Any] = Field(..., description="System metrics")


class CacheStatistics(BaseModel):
    """Cache statistics response."""
    
    embedding: Dict[str, Any] = Field(..., description="Embedding cache stats")
    api: Dict[str, Any] = Field(..., description="API cache stats")
    analysis: Dict[str, Any] = Field(..., description="Analysis cache stats")
    rag: Dict[str, Any] = Field(..., description="RAG cache stats")


class RateLimitInfo(BaseModel):
    """Rate limit information."""
    
    active_users: int = Field(..., description="Number of active users")
    active_endpoints: int = Field(..., description="Number of active endpoints")
    external_apis: Dict[str, Any] = Field(..., description="External API quota info")
