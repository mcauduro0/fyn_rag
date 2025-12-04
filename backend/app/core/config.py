"""
Central configuration module for the Fyn RAG application.
Loads environment variables and provides application-wide settings.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")
    
    # Backend
    BACKEND_HOST: str = Field(default="0.0.0.0")
    BACKEND_PORT: int = Field(default=8000)
    CORS_ORIGINS: str = Field(default="http://localhost:3000")
    
    # Database
    DATABASE_URL: str = Field(...)
    
    # OpenAI
    OPENAI_API_KEY: str = Field(...)
    
    # Anthropic
    ANTHROPIC_API_KEY: str = Field(...)
    
    # Data Sources - Market Data
    POLYGON_API_KEY: str = Field(default="")
    FMP_API_KEY: str = Field(default="")
    
    # Data Sources - Economic Data
    TRADING_ECONOMICS_API_KEY: str = Field(default="")
    FRED_API_KEY: str = Field(default="")
    
    # Data Sources - Social Media
    REDDIT_CLIENT_ID: str = Field(default="")
    REDDIT_CLIENT_SECRET: str = Field(default="")
    REDDIT_USER_AGENT: str = Field(default="FynRAG/1.0")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
