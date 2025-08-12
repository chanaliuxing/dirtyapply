"""
Centralized configuration module implementing Golden Rules:
- No hard-coded secrets
- Fail-fast validation
- Safe logging
- Single config source
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import Optional, Literal
import os
import secrets
import structlog

logger = structlog.get_logger(__name__)

def mask_secret(secret: str, show_chars: int = 8) -> str:
    """Safely mask secrets for logging - never log full values"""
    if not secret or len(secret) <= show_chars:
        return "***"
    return f"{secret[:show_chars]}***"

class Settings(BaseSettings):
    """
    Application settings with fail-fast validation.
    All secrets must come from environment variables.
    """
    
    # Application
    app_name: str = Field("Apply-Copilot", env="APP_NAME")
    version: str = Field("1.0.0", env="VERSION")
    debug: bool = Field(False, env="DEBUG")
    
    # API Configuration
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    api_workers: int = Field(1, env="API_WORKERS")
    
    # Database (required)
    database_url: str = Field(..., env="DATABASE_URL")
    database_echo: bool = Field(False, env="DATABASE_ECHO")
    
    # Redis (optional - fallback to memory)
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    
    # MinIO/S3 Storage (optional - fallback to local disk)
    minio_endpoint: Optional[str] = Field(None, env="MINIO_ENDPOINT")
    minio_access_key: Optional[str] = Field(None, env="MINIO_ACCESS_KEY")
    minio_secret_key: Optional[str] = Field(None, env="MINIO_SECRET_KEY")
    minio_bucket_name: str = Field("apply-copilot", env="MINIO_BUCKET_NAME")
    minio_secure: bool = Field(False, env="MINIO_SECURE")
    
    # LLM Provider Configuration (optional - defaults to rule-based)
    llm_provider: Literal["none", "openai", "deepseek", "deepseek-nvidia", "anthropic"] = Field("none", env="LLM_PROVIDER")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    deepseek_api_key: Optional[str] = Field(None, env="DEEPSEEK_API_KEY")
    deepseek_nvidia_api_key: Optional[str] = Field(None, env="DEEPSEEK_NVIDIA_API_KEY")
    
    # Security (required for production)
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    companion_token: str = Field(..., env="COMPANION_TOKEN")
    
    # Companion Service
    companion_host: str = Field("127.0.0.1", env="COMPANION_HOST")
    companion_port: int = Field(8765, env="COMPANION_PORT")
    
    # Feature Flags
    enable_mock_ats: bool = Field(True, env="ENABLE_MOCK_ATS")
    enable_debug_logging: bool = Field(False, env="ENABLE_DEBUG_LOGGING")
    max_applications_per_day: int = Field(25, env="MAX_APPLICATIONS_PER_DAY")
    
    # Development Only (NEVER use in production)
    disable_auth: bool = Field(False, env="DISABLE_AUTH")
    
    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "chrome-extension://*"],
        env="CORS_ORIGINS"
    )
    
    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v):
        if v and not v.startswith('sk-'):
            raise ValueError("Invalid OpenAI API key format - must start with 'sk-'")
        return v
    
    @field_validator("anthropic_api_key")
    @classmethod
    def validate_anthropic_key(cls, v):
        if v and not (v.startswith('sk-ant-') or v.startswith('ant-')):
            raise ValueError("Invalid Anthropic API key format")
        return v
    
    @field_validator("deepseek_nvidia_api_key")
    @classmethod
    def validate_deepseek_nvidia_key(cls, v):
        if v and not v.startswith('nvapi-'):
            raise ValueError("Invalid DeepSeek NVIDIA API key format - must start with 'nvapi-'")
        return v
    
    @field_validator("companion_token")
    @classmethod
    def validate_companion_token(cls, v):
        if len(v) < 32:
            raise ValueError("COMPANION_TOKEN must be at least 32 characters for security")
        return v
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v):
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://', 'sqlite:///')):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL or SQLite URL")
        return v
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
    
    def validate_llm_dependencies(self) -> None:
        """Validate that required API keys are present for selected LLM provider"""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        elif self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
        elif self.llm_provider == "deepseek" and not self.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is required when LLM_PROVIDER=deepseek")
        elif self.llm_provider == "deepseek-nvidia" and not self.deepseek_nvidia_api_key:
            raise ValueError("DEEPSEEK_NVIDIA_API_KEY is required when LLM_PROVIDER=deepseek-nvidia")
    
    def validate_production_security(self) -> None:
        """Additional validation for production environment"""
        if not self.debug:  # Production mode
            if self.disable_auth:
                raise ValueError("DISABLE_AUTH=true is not allowed in production")
            if self.secret_key == "dev-secret-key":
                raise ValueError("Default SECRET_KEY not allowed in production")
    
    def log_startup_config(self) -> None:
        """Log configuration at startup with masked secrets"""
        logger.info(
            "Configuration loaded",
            app_name=self.app_name,
            version=self.version,
            debug=self.debug,
            api_host=self.api_host,
            api_port=self.api_port,
            database_url=mask_secret(self.database_url, 20),
            redis_url=mask_secret(self.redis_url or "none", 15),
            llm_provider=self.llm_provider,
            openai_api_key=mask_secret(self.openai_api_key or "none"),
            anthropic_api_key=mask_secret(self.anthropic_api_key or "none"),
            deepseek_api_key=mask_secret(self.deepseek_api_key or "none"),
            deepseek_nvidia_api_key=mask_secret(self.deepseek_nvidia_api_key or "none"),
            companion_token=mask_secret(self.companion_token),
            minio_configured=bool(self.minio_endpoint),
            max_applications_per_day=self.max_applications_per_day,
            disable_auth=self.disable_auth,
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False

# Global settings instance
settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get settings instance with fail-fast validation"""
    global settings
    if settings is None:
        try:
            settings = Settings()
            
            # Run all validation checks
            settings.validate_llm_dependencies()
            settings.validate_production_security()
            
            # Log configuration safely
            settings.log_startup_config()
            
            logger.info("✅ Configuration validation successful")
            
        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            raise SystemExit(f"Configuration error: {e}")
    
    return settings

def validate_environment() -> None:
    """Validate environment at startup - called by main.py"""
    try:
        get_settings()
        logger.info("✅ Environment validation passed")
    except Exception as e:
        logger.error(f"❌ Environment validation failed: {e}")
        raise SystemExit(f"Environment validation error: {e}")