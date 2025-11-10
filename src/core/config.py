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

    # Agent Evaluator Settings
    agent_min_success_rate: float = Field(default=0.4, env="AGENT_MIN_SUCCESS_RATE")
    agent_max_idle_minutes: int = Field(default=60, env="AGENT_MAX_IDLE_MINUTES")
    agent_evaluation_interval: int = Field(default=3, env="AGENT_EVALUATION_INTERVAL")

    # Razorpay Configuration (Payment Gateway)
    razorpay_enabled: bool = Field(default=False, env="RAZORPAY_ENABLED")
    razorpay_key_id: str = Field(default="", env="RAZORPAY_KEY_ID")
    razorpay_key_secret: str = Field(default="", env="RAZORPAY_KEY_SECRET")
    razorpay_account_number: str = Field(default="", env="RAZORPAY_ACCOUNT_NUMBER")
    razorpay_callback_url: str = Field(default="http://localhost:8000/api/payment/callback", env="RAZORPAY_CALLBACK_URL")

    # DigitalOcean Configuration (Cloud Deployment)
    digitalocean_enabled: bool = Field(default=False, env="DIGITALOCEAN_ENABLED")
    digitalocean_api_token: str = Field(default="", env="DIGITALOCEAN_API_TOKEN")
    digitalocean_ssh_key_id: Optional[str] = Field(default=None, env="DIGITALOCEAN_SSH_KEY_ID")
    digitalocean_default_region: str = Field(default="blr1", env="DIGITALOCEAN_DEFAULT_REGION")

    # Real Business Mode
    real_business_mode: bool = Field(default=False, env="REAL_BUSINESS_MODE")
    use_real_payments: bool = Field(default=False, env="USE_REAL_PAYMENTS")
    use_real_deployment: bool = Field(default=False, env="USE_REAL_DEPLOYMENT")

    # Security
    api_key: str = Field(default="dev-key", env="API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
