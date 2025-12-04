"""
CRUD operations for database models.
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.models import (
    User, Analysis, AgentResponse, MarketData, FinancialData,
    Document, RAGFramework, AnalysisHistory, SystemMetrics,
    AssetType, RecommendationType
)

logger = logging.getLogger(__name__)


# User CRUD
def create_user(db: Session, email: str, full_name: str, hashed_password: str) -> User:
    """Create a new user."""
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


# Analysis CRUD
def create_analysis(
    db: Session,
    request_id: str,
    user_id: int,
    asset_type: AssetType,
    company_name: str,
    final_recommendation: RecommendationType,
    confidence: float,
    analysis_duration: float,
    ticker: Optional[str] = None,
    value_analysis: Optional[dict] = None,
    growth_analysis: Optional[dict] = None,
    risk_analysis: Optional[dict] = None,
    industry_analysis: Optional[dict] = None,
    forensics_analysis: Optional[dict] = None,
    debate_results: Optional[dict] = None,
    report_markdown: Optional[str] = None,
    report_type: Optional[str] = None
) -> Analysis:
    """Create a new analysis."""
    analysis = Analysis(
        request_id=request_id,
        user_id=user_id,
        asset_type=asset_type,
        ticker=ticker,
        company_name=company_name,
        final_recommendation=final_recommendation,
        confidence=confidence,
        value_analysis=value_analysis,
        growth_analysis=growth_analysis,
        risk_analysis=risk_analysis,
        industry_analysis=industry_analysis,
        forensics_analysis=forensics_analysis,
        debate_results=debate_results,
        report_markdown=report_markdown,
        report_type=report_type,
        analysis_duration=analysis_duration
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_analysis_by_id(db: Session, analysis_id: int) -> Optional[Analysis]:
    """Get analysis by ID."""
    return db.query(Analysis).filter(Analysis.id == analysis_id).first()


def get_analysis_by_request_id(db: Session, request_id: str) -> Optional[Analysis]:
    """Get analysis by request ID."""
    return db.query(Analysis).filter(Analysis.request_id == request_id).first()


def get_analyses_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Analysis]:
    """Get analyses by user."""
    return db.query(Analysis).filter(
        Analysis.user_id == user_id
    ).order_by(
        Analysis.created_at.desc()
    ).offset(skip).limit(limit).all()


def get_analyses_by_ticker(
    db: Session,
    ticker: str,
    skip: int = 0,
    limit: int = 100
) -> List[Analysis]:
    """Get analyses by ticker."""
    return db.query(Analysis).filter(
        Analysis.ticker == ticker
    ).order_by(
        Analysis.created_at.desc()
    ).offset(skip).limit(limit).all()


def get_recent_analyses(
    db: Session,
    days: int = 7,
    skip: int = 0,
    limit: int = 100
) -> List[Analysis]:
    """Get recent analyses."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    return db.query(Analysis).filter(
        Analysis.created_at >= cutoff_date
    ).order_by(
        Analysis.created_at.desc()
    ).offset(skip).limit(limit).all()


# Agent Response CRUD
def create_agent_response(
    db: Session,
    analysis_id: int,
    agent_role: str,
    agent_name: str,
    analysis_text: str,
    recommendation: RecommendationType,
    confidence: float,
    supporting_data: dict,
    frameworks_used: list,
    concerns: list,
    opportunities: list
) -> AgentResponse:
    """Create agent response."""
    response = AgentResponse(
        analysis_id=analysis_id,
        agent_role=agent_role,
        agent_name=agent_name,
        analysis_text=analysis_text,
        recommendation=recommendation,
        confidence=confidence,
        supporting_data=supporting_data,
        frameworks_used=frameworks_used,
        concerns=concerns,
        opportunities=opportunities
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    return response


def get_agent_responses_by_analysis(
    db: Session,
    analysis_id: int
) -> List[AgentResponse]:
    """Get all agent responses for an analysis."""
    return db.query(AgentResponse).filter(
        AgentResponse.analysis_id == analysis_id
    ).all()


# Market Data CRUD
def create_market_data(
    db: Session,
    ticker: str,
    date: datetime,
    close_price: float,
    source: str,
    open_price: Optional[float] = None,
    high_price: Optional[float] = None,
    low_price: Optional[float] = None,
    volume: Optional[int] = None
) -> MarketData:
    """Create market data entry."""
    data = MarketData(
        ticker=ticker,
        date=date,
        open_price=open_price,
        high_price=high_price,
        low_price=low_price,
        close_price=close_price,
        volume=volume,
        source=source
    )
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def get_market_data(
    db: Session,
    ticker: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[MarketData]:
    """Get market data for ticker."""
    query = db.query(MarketData).filter(MarketData.ticker == ticker)
    
    if start_date:
        query = query.filter(MarketData.date >= start_date)
    if end_date:
        query = query.filter(MarketData.date <= end_date)
    
    return query.order_by(MarketData.date.desc()).all()


# Financial Data CRUD
def create_financial_data(
    db: Session,
    ticker: str,
    company_name: str,
    fiscal_year: int,
    period_type: str,
    source: str,
    fiscal_quarter: Optional[int] = None,
    income_statement: Optional[dict] = None,
    balance_sheet: Optional[dict] = None,
    cash_flow: Optional[dict] = None,
    key_metrics: Optional[dict] = None
) -> FinancialData:
    """Create financial data entry."""
    data = FinancialData(
        ticker=ticker,
        company_name=company_name,
        fiscal_year=fiscal_year,
        fiscal_quarter=fiscal_quarter,
        period_type=period_type,
        income_statement=income_statement,
        balance_sheet=balance_sheet,
        cash_flow=cash_flow,
        key_metrics=key_metrics,
        source=source
    )
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def get_financial_data(
    db: Session,
    ticker: str,
    fiscal_year: Optional[int] = None
) -> List[FinancialData]:
    """Get financial data for ticker."""
    query = db.query(FinancialData).filter(FinancialData.ticker == ticker)
    
    if fiscal_year:
        query = query.filter(FinancialData.fiscal_year == fiscal_year)
    
    return query.order_by(FinancialData.fiscal_year.desc()).all()


# Document CRUD
def create_document(
    db: Session,
    filename: str,
    file_path: str,
    file_type: str,
    file_size: int,
    company_name: str,
    uploaded_by: int,
    extracted_text: Optional[str] = None,
    processed_data: Optional[dict] = None
) -> Document:
    """Create document entry."""
    doc = Document(
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        company_name=company_name,
        uploaded_by=uploaded_by,
        extracted_text=extracted_text,
        processed_data=processed_data
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_documents_by_company(
    db: Session,
    company_name: str
) -> List[Document]:
    """Get documents for company."""
    return db.query(Document).filter(
        Document.company_name == company_name
    ).order_by(Document.created_at.desc()).all()


# System Metrics CRUD
def create_system_metric(
    db: Session,
    metric_name: str,
    metric_value: float,
    metric_unit: Optional[str] = None,
    tags: Optional[dict] = None
) -> SystemMetrics:
    """Create system metric entry."""
    metric = SystemMetrics(
        metric_name=metric_name,
        metric_value=metric_value,
        metric_unit=metric_unit,
        tags=tags
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def get_system_metrics(
    db: Session,
    metric_name: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[SystemMetrics]:
    """Get system metrics."""
    query = db.query(SystemMetrics).filter(SystemMetrics.metric_name == metric_name)
    
    if start_time:
        query = query.filter(SystemMetrics.timestamp >= start_time)
    if end_time:
        query = query.filter(SystemMetrics.timestamp <= end_time)
    
    return query.order_by(SystemMetrics.timestamp.desc()).all()


# Statistics
def get_analysis_statistics(db: Session) -> dict:
    """Get analysis statistics."""
    total_analyses = db.query(Analysis).count()
    
    buy_count = db.query(Analysis).filter(
        Analysis.final_recommendation == RecommendationType.BUY
    ).count()
    
    hold_count = db.query(Analysis).filter(
        Analysis.final_recommendation == RecommendationType.HOLD
    ).count()
    
    sell_count = db.query(Analysis).filter(
        Analysis.final_recommendation == RecommendationType.SELL
    ).count()
    
    avg_confidence = db.query(Analysis).with_entities(
        db.func.avg(Analysis.confidence)
    ).scalar() or 0.0
    
    return {
        "total_analyses": total_analyses,
        "buy_count": buy_count,
        "hold_count": hold_count,
        "sell_count": sell_count,
        "avg_confidence": float(avg_confidence)
    }
