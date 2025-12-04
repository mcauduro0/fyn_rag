"""
Database models for Fyn RAG system.
Stores analyses, users, and historical data.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class AssetType(str, enum.Enum):
    """Type of asset analyzed."""
    LISTED = "listed"
    ILLIQUID = "illiquid"


class RecommendationType(str, enum.Enum):
    """Investment recommendation."""
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="user")
    
    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.full_name}')>"


class Analysis(Base):
    """Analysis model - stores complete investment analyses."""
    
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(36), unique=True, index=True, nullable=False)
    
    # User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="analyses")
    
    # Asset information
    asset_type = Column(SQLEnum(AssetType), nullable=False)
    ticker = Column(String(20), index=True, nullable=True)
    company_name = Column(String(255), index=True, nullable=False)
    
    # Analysis results
    final_recommendation = Column(SQLEnum(RecommendationType), nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Agent analyses (JSON)
    value_analysis = Column(JSON, nullable=True)
    growth_analysis = Column(JSON, nullable=True)
    risk_analysis = Column(JSON, nullable=True)
    industry_analysis = Column(JSON, nullable=True)
    forensics_analysis = Column(JSON, nullable=True)
    
    # Debate results (JSON)
    debate_results = Column(JSON, nullable=True)
    
    # Report
    report_markdown = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=True)
    
    # Metadata
    analysis_duration = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    agent_responses = relationship("AgentResponse", back_populates="analysis")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, ticker='{self.ticker}', recommendation='{self.final_recommendation}')>"


class AgentResponse(Base):
    """Agent response model - stores individual agent analyses."""
    
    __tablename__ = "agent_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Analysis reference
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    analysis = relationship("Analysis", back_populates="agent_responses")
    
    # Agent information
    agent_role = Column(String(50), nullable=False)
    agent_name = Column(String(100), nullable=False)
    
    # Response data
    analysis_text = Column(Text, nullable=False)
    recommendation = Column(SQLEnum(RecommendationType), nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Supporting data (JSON)
    supporting_data = Column(JSON, nullable=False)
    frameworks_used = Column(JSON, nullable=False)
    concerns = Column(JSON, nullable=False)
    opportunities = Column(JSON, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AgentResponse(agent='{self.agent_role}', recommendation='{self.recommendation}')>"


class MarketData(Base):
    """Market data model - stores historical market data."""
    
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Asset information
    ticker = Column(String(20), index=True, nullable=False)
    
    # Price data
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    
    # Metadata
    date = Column(DateTime, index=True, nullable=False)
    source = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MarketData(ticker='{self.ticker}', date='{self.date}', close={self.close_price})>"


class FinancialData(Base):
    """Financial data model - stores company financials."""
    
    __tablename__ = "financial_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Company information
    ticker = Column(String(20), index=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    
    # Financial metrics (JSON for flexibility)
    income_statement = Column(JSON, nullable=True)
    balance_sheet = Column(JSON, nullable=True)
    cash_flow = Column(JSON, nullable=True)
    key_metrics = Column(JSON, nullable=True)
    
    # Period information
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer, nullable=True)
    period_type = Column(String(20), nullable=False)  # annual, quarterly
    
    # Metadata
    source = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FinancialData(ticker='{self.ticker}', year={self.fiscal_year})>"


class Document(Base):
    """Document model - stores uploaded documents for illiquid assets."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Document information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Associated company
    company_name = Column(String(255), index=True, nullable=False)
    
    # Processed data (JSON)
    extracted_text = Column(Text, nullable=True)
    processed_data = Column(JSON, nullable=True)
    
    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Document(filename='{self.filename}', company='{self.company_name}')>"


class RAGFramework(Base):
    """RAG Framework model - stores investment frameworks."""
    
    __tablename__ = "rag_frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Framework information
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Framework content
    methodology = Column(Text, nullable=True)
    key_metrics = Column(JSON, nullable=True)
    interpretation_guide = Column(Text, nullable=True)
    
    # Examples and references
    examples = Column(JSON, nullable=True)
    references = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RAGFramework(name='{self.name}', category='{self.category}')>"


class AnalysisHistory(Base):
    """Analysis history model - tracks analysis performance over time."""
    
    __tablename__ = "analysis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to original analysis
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    
    # Actual outcome (for backtesting)
    actual_outcome = Column(String(50), nullable=True)
    outcome_date = Column(DateTime, nullable=True)
    
    # Performance metrics
    accuracy_score = Column(Float, nullable=True)
    return_achieved = Column(Float, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AnalysisHistory(analysis_id={self.analysis_id}, outcome='{self.actual_outcome}')>"


class SystemMetrics(Base):
    """System metrics model - stores performance metrics."""
    
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metric information
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)
    
    # Tags (JSON for flexibility)
    tags = Column(JSON, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<SystemMetrics(name='{self.metric_name}', value={self.metric_value})>"
