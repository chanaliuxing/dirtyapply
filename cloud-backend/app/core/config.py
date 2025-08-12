"""
Configuration settings for the cloud backend
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/indeed_automation"
    )
    
    # Redis for caching and Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # AI/LLM Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4")
    
    # Object Storage (MinIO/S3)
    STORAGE_ENDPOINT: str = os.getenv("STORAGE_ENDPOINT", "localhost:9000")
    STORAGE_ACCESS_KEY: str = os.getenv("STORAGE_ACCESS_KEY", "minioadmin")
    STORAGE_SECRET_KEY: str = os.getenv("STORAGE_SECRET_KEY", "minioadmin")
    STORAGE_BUCKET: str = os.getenv("STORAGE_BUCKET", "indeed-automation")
    STORAGE_SECURE: bool = os.getenv("STORAGE_SECURE", "false").lower() == "true"
    
    # Chrome Extension Settings
    ALLOWED_ORIGINS: List[str] = [
        "chrome-extension://*",
        "http://localhost:3000",
        "https://ca.indeed.com",
        "https://indeed.ca"
    ]
    
    # JTR (Job-Tailored Resume) Settings
    MAX_RS_BULLETS_PER_RESUME: int = 15
    RS_CONFIDENCE_THRESHOLD: float = 0.7
    ATS_SCORE_THRESHOLD: int = 85
    
    # Job Matching Settings
    SKILL_MATCH_THRESHOLD: float = 0.6
    EXPERIENCE_MATCH_WEIGHT: float = 0.4
    EDUCATION_MATCH_WEIGHT: float = 0.2
    SKILLS_MATCH_WEIGHT: float = 0.4
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    DAILY_APPLICATION_LIMIT: int = 50
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "8080"))
    
    # Safety Settings - Critical for ethical operation
    AUTO_SUBMIT_ENABLED: bool = False  # Always false for safety
    ENABLE_AUTO_SUBMIT: bool = False  # Always false for safety
    REQUIRE_CONFIRMATION: bool = True  # Always require human confirmation
    REQUIRE_HUMAN_APPROVAL: bool = True
    MAX_APPLICATIONS_PER_DAY: int = 25
    WHITELIST_DOMAINS: List[str] = ["ca.indeed.com", "indeed.ca"]
    
    # Evidence Vault Settings
    MAX_EVIDENCE_ITEMS: int = 1000
    EVIDENCE_RETENTION_DAYS: int = 365
    
    # Document Generation
    RESUME_TEMPLATES_PATH: str = "templates/resumes"
    COVER_LETTER_TEMPLATES_PATH: str = "templates/cover_letters"
    OUTPUT_FORMATS: List[str] = ["pdf", "docx"]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/backend.log")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Validation and warnings
if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
    print("WARNING: No AI API keys configured. AI features will be limited.")

if settings.SECRET_KEY == "your-secret-key-change-in-production":
    print("WARNING: Using default secret key. Change this in production!")

if settings.ENABLE_AUTO_SUBMIT:
    print("ERROR: Auto-submit is enabled! This should NEVER be true in production.")
    settings.ENABLE_AUTO_SUBMIT = False  # Force disable