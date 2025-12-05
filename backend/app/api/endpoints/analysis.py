"""
Analysis API endpoints - Main endpoint for multi-agent investment analysis.
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import time
from datetime import datetime
import uuid

from app.core.config import settings
from app.api.schemas.agent_schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AgentAnalysisResponse,
    DebateResult,
    ReportGenerationRequest,
    ReportResponse,
    AssetType
)
from app.core.orchestrator.orchestrator_agent import OrchestratorAgent
from app.core.agents.value_investing_agent import ValueInvestingAgent
from app.core.agents.growth_vc_agent import GrowthVCAgent
from app.core.agents.risk_management_agent import RiskManagementAgent
from app.core.agents.industry_competitive_agent import IndustryCompetitiveAgent
from app.core.agents.financial_forensics_agent import FinancialForensicsAgent
from app.core.reasoning.debate_simulator import DebateSimulator
from app.core.reports.report_generator import ReportGenerator, ReportType
from app.core.rag.rag_system import RAGSystem, get_rag_system
from app.data.fetchers.polygon_fetcher import PolygonFetcher
from app.data.fetchers.fmp_fetcher import FMPFetcher
from app.data.processors.document_processor import DocumentProcessor
from app.core.utils.monitoring import get_performance_monitor
from app.core.utils.rate_limiter import get_rate_limiter
from app.core.utils.caching import cached_async

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/complete", response_model=AnalysisResponse)
async def run_complete_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
) -> AnalysisResponse:
    """
    Run complete multi-agent investment analysis.
    
    This endpoint orchestrates the entire investment committee process:
    1. Data gathering (market data or document processing)
    2. RAG system query for relevant frameworks
    3. Multi-agent analysis (5 specialized agents)
    4. Debate simulation for consensus
    5. Report generation
    
    Args:
        request: Analysis request with asset details
        background_tasks: FastAPI background tasks
        
    Returns:
        Complete analysis with agent insights, debate results, and report
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    logger.info(f"Starting analysis {request_id} for {request.ticker or request.company_name}")
    
    # Check rate limit
    rate_limiter = get_rate_limiter()
    if not rate_limiter.check_endpoint_limit("analysis.complete"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    try:
        # Step 1: Gather data
        context = await _gather_data(request)
        
        # Step 2: Query RAG system for relevant frameworks
        rag_system = get_rag_system()
        await rag_system.initialize()
        
        query = f"investment analysis frameworks for {request.ticker or request.company_name}"
        rag_results = await rag_system.query(query, top_k=20)
        
        # Step 3: Run multi-agent analysis
        agent_responses = await _run_agent_analyses(context, rag_results)
        
        # Step 4: Debate simulation (if requested)
        debate_result = None
        if request.include_debate:
            debate_result = await _run_debate_simulation(agent_responses, context)
            final_recommendation = debate_result["final_recommendation"]
            final_confidence = debate_result["confidence"]
        else:
            # Simple majority vote
            final_recommendation, final_confidence = _simple_consensus(agent_responses)
        
        # Step 5: Generate report (if requested)
        report_markdown = None
        if request.generate_report:
            report_markdown = await _generate_report(
                request,
                agent_responses,
                final_recommendation,
                final_confidence
            )
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Track metrics
        monitor = get_performance_monitor()
        monitor.track_api_request("/analysis/complete", "POST", 200, duration)
        
        # Prepare response
        response = AnalysisResponse(
            request_id=request_id,
            asset_type=request.asset_type,
            ticker=request.ticker,
            company_name=request.company_name,
            agent_analyses={
                role.value: AgentAnalysisResponse(
                    agent_role=resp.agent_role.value,
                    analysis=resp.analysis,
                    recommendation=resp.recommendation,
                    confidence=resp.confidence,
                    supporting_data=resp.supporting_data,
                    frameworks_used=resp.frameworks_used,
                    concerns=resp.concerns,
                    opportunities=resp.opportunities
                )
                for role, resp in agent_responses.items()
            },
            debate_result=DebateResult(**debate_result) if debate_result else None,
            final_recommendation=final_recommendation,
            confidence=final_confidence,
            report_markdown=report_markdown,
            analysis_duration=duration,
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Completed analysis {request_id} in {duration:.2f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        
        # Track error
        monitor = get_performance_monitor()
        monitor.track_api_request("/analysis/complete", "POST", 500, time.time() - start_time)
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


async def _gather_data(request: AnalysisRequest) -> Dict[str, Any]:
    """Gather data based on asset type."""
    context = {}
    
    if request.asset_type == AssetType.LISTED:
        # Gather market data
        if not request.ticker:
            raise HTTPException(status_code=400, detail="Ticker required for listed assets")
        
        logger.info(f"Gathering market data for {request.ticker}")
        
        # Polygon data
        polygon = PolygonFetcher(api_key=settings.POLYGON_API_KEY)
        try:
            quote = polygon.fetch_quote(request.ticker)
            context["current_price"] = quote.get("price")
            context["volume"] = quote.get("volume")
        except Exception as e:
            logger.warning(f"Failed to fetch Polygon data: {e}")
        
        # FMP data
        fmp = FMPFetcher(api_key=settings.FMP_API_KEY)
        try:
            profile = fmp.fetch_company_profile(request.ticker)
            context.update(profile)
            
            financials = fmp.fetch_comprehensive_data(request.ticker)
            context["financials"] = financials
        except Exception as e:
            logger.warning(f"Failed to fetch FMP data: {e}")
        
        context["ticker"] = request.ticker
        context["company_name"] = context.get("companyName", request.ticker)
        
    elif request.asset_type == AssetType.ILLIQUID:
        # Process documents
        if not request.company_name:
            raise HTTPException(status_code=400, detail="Company name required for illiquid assets")
        
        logger.info(f"Processing documents for {request.company_name}")
        
        if request.documents:
            processor = DocumentProcessor()
            processed_docs = []
            
            for doc_path in request.documents:
                try:
                    doc_data = processor.process(doc_path)
                    processed_docs.append(doc_data)
                except Exception as e:
                    logger.warning(f"Failed to process document {doc_path}: {e}")
            
            context["processed_documents"] = processed_docs
        
        context["company_name"] = request.company_name
    
    # Add additional context
    context.update(request.additional_context)
    
    return context


async def _run_agent_analyses(
    context: Dict[str, Any],
    rag_results: list
) -> Dict[str, Any]:
    """Run analyses from all specialized agents."""
    logger.info("Running multi-agent analyses")
    
    # Initialize agents
    agents = {
        "value": ValueInvestingAgent(),
        "growth": GrowthVCAgent(),
        "risk": RiskManagementAgent(),
        "industry": IndustryCompetitiveAgent(),
        "forensics": FinancialForensicsAgent()
    }
    
    # Run analyses in parallel (simulated)
    responses = {}
    task = f"Analyze investment opportunity for {context.get('company_name', context.get('ticker'))}"
    
    for name, agent in agents.items():
        try:
            start_time = time.time()
            response = await agent.analyze(task, context, rag_results)
            duration = time.time() - start_time
            
            responses[response.agent_role] = response
            
            # Track metrics
            monitor = get_performance_monitor()
            monitor.track_agent_execution(name, duration, True)
            
        except Exception as e:
            logger.error(f"Agent {name} failed: {e}")
            monitor = get_performance_monitor()
            monitor.track_agent_execution(name, 0, False)
    
    return responses


async def _run_debate_simulation(
    agent_responses: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Run debate simulation to reach consensus."""
    logger.info("Running debate simulation")
    
    simulator = DebateSimulator(max_rounds=3)
    debate_results = await simulator.run_debate(agent_responses, context)
    
    return debate_results


def _simple_consensus(agent_responses: Dict[str, Any]) -> tuple[str, float]:
    """Simple consensus without debate."""
    from collections import Counter
    
    recommendations = [r.recommendation.split()[0] for r in agent_responses.values()]
    confidences = [r.confidence for r in agent_responses.values()]
    
    # Most common recommendation
    rec_counts = Counter(recommendations)
    final_rec = rec_counts.most_common(1)[0][0]
    
    # Average confidence
    final_confidence = sum(confidences) / len(confidences)
    
    return final_rec, final_confidence


async def _generate_report(
    request: AnalysisRequest,
    agent_responses: Dict[str, Any],
    recommendation: str,
    confidence: float
) -> str:
    """Generate investment report."""
    logger.info(f"Generating {request.report_type} report")
    
    generator = ReportGenerator()
    
    # Prepare analysis data
    analysis_data = {
        f"{role.value}_analysis": {
            "recommendation": resp.recommendation,
            "confidence": resp.confidence,
            "supporting_data": resp.supporting_data,
            "concerns": resp.concerns,
            "opportunities": resp.opportunities
        }
        for role, resp in agent_responses.items()
    }
    
    # Generate report based on type
    if request.report_type == "one_pager":
        report = generator.generate_one_pager(
            company_name=request.company_name or request.ticker,
            ticker=request.ticker,
            analysis_data=analysis_data,
            recommendation=recommendation,
            confidence=confidence
        )
    elif request.report_type == "comprehensive":
        report = generator.generate_comprehensive_thesis(
            company_name=request.company_name or request.ticker,
            ticker=request.ticker,
            analysis_data=analysis_data,
            recommendation=recommendation,
            confidence=confidence
        )
    elif request.report_type == "presentation":
        report = generator.generate_presentation_outline(
            company_name=request.company_name or request.ticker,
            ticker=request.ticker,
            analysis_data=analysis_data,
            recommendation=recommendation,
            confidence=confidence
        )
    else:
        raise ValueError(f"Unknown report type: {request.report_type}")
    
    return report.to_markdown()


@router.post("/report", response_model=ReportResponse)
async def generate_report(request: ReportGenerationRequest) -> ReportResponse:
    """
    Generate investment report from analysis data.
    
    Args:
        request: Report generation request
        
    Returns:
        Generated report in Markdown format
    """
    logger.info(f"Generating report for {request.company_name}")
    
    try:
        generator = ReportGenerator()
        
        # Map report type
        report_type_map = {
            "one_pager": ReportType.ONE_PAGER,
            "comprehensive": ReportType.COMPREHENSIVE_THESIS,
            "presentation": ReportType.PRESENTATION
        }
        
        # Generate report
        if request.report_type == "one_pager":
            report = generator.generate_one_pager(
                company_name=request.company_name,
                ticker=request.ticker,
                analysis_data=request.analysis_data,
                recommendation=request.recommendation,
                confidence=request.confidence
            )
        elif request.report_type == "comprehensive":
            report = generator.generate_comprehensive_thesis(
                company_name=request.company_name,
                ticker=request.ticker,
                analysis_data=request.analysis_data,
                recommendation=request.recommendation,
                confidence=request.confidence
            )
        else:
            report = generator.generate_presentation_outline(
                company_name=request.company_name,
                ticker=request.ticker,
                analysis_data=request.analysis_data,
                recommendation=request.recommendation,
                confidence=request.confidence
            )
        
        return ReportResponse(
            report_type=request.report_type,
            report_markdown=report.to_markdown(),
            company_name=request.company_name,
            ticker=request.ticker,
            generated_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
