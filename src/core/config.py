"""Configuration management for the AI Entrepreneur Agent System."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Ollama Configuration
    ollama_host: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    ollama_model: str = Field(default="gpt-oss:latest", env="OLLAMA_MODEL")

    # Application Settings
    app_name: str = Field(default="AI Entrepreneur Agent System", env="APP_NAME")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug: bool = Field(default=False, env="DEBUG")

    # Database
    database_url: str = Field(default="sqlite:///./entrepreneur_agent.db", env="DATABASE_URL")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Web Dashboard
    dashboard_host: str = Field(default="0.0.0.0", env="DASHBOARD_HOST")
    dashboard_port: int = Field(default=8000, env="DASHBOARD_PORT")

    # Agent Configuration
    max_concurrent_agents: int = Field(default=10, env="MAX_CONCURRENT_AGENTS")
    agent_timeout_seconds: int = Field(default=300, env="AGENT_TIMEOUT_SECONDS")
    max_iterations_per_task: int = Field(default=50, env="MAX_ITERATIONS_PER_TASK")

    # Business Parameters
    initial_capital: float = Field(default=1000.0, env="INITIAL_CAPITAL")
    risk_tolerance: float = Field(default=0.7, env="RISK_TOLERANCE")
    min_profit_margin: float = Field(default=0.15, env="MIN_PROFIT_MARGIN")
    opportunity_scan_interval_minutes: int = Field(default=30, env="OPPORTUNITY_SCAN_INTERVAL_MINUTES")

    # Security
    api_key: str = Field(default="dev-key", env="API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
