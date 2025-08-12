"""
Database configuration and initialization
Implements secure connection handling with config validation
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

# Database base class
Base = declarative_base()

# Global database engine
engine = None
AsyncSessionLocal = None

async def init_db() -> None:
    """Initialize database connection with configuration validation"""
    global engine, AsyncSessionLocal
    
    settings = get_settings()
    
    try:
        # Create async engine with secure configuration
        engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo and settings.debug,  # Only echo in debug mode
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections every hour
            pool_size=5,
            max_overflow=10,
        )
        
        # Create session factory
        AsyncSessionLocal = sessionmaker(
            engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        
        # Test connection
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        
        logger.info(
            "✅ Database connection established",
            database_type="postgresql" if "postgresql" in settings.database_url else "sqlite",
            pool_size=5,
        )
        
    except Exception as e:
        logger.error(
            "❌ Database connection failed",
            error=str(e),
            database_url_masked=f"{settings.database_url.split('@')[0]}@***"
        )
        raise

async def get_db_session() -> AsyncSession:
    """Get database session - dependency injection"""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables() -> None:
    """Create database tables - used by migrations"""
    if engine is None:
        raise RuntimeError("Database engine not initialized")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Database tables created/verified")

async def close_db() -> None:
    """Close database connection"""
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")