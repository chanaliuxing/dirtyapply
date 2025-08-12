"""
Cloud Backend for Indeed.ca Automation System
AI Orchestrator, JTR (Job-Tailored Resume), and Policy Engine
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import structlog
from typing import Dict, List, Optional
import os
from datetime import datetime

# Import our modules
from app.core.config import settings
from app.core.database import engine, create_tables
from app.ai.orchestrator import AIOrchestrator
from app.services.resume_tailoring import ResumeTailoringService
from app.services.job_matching import JobMatchingService
from app.services.qa_generation import QAGenerationService
from app.api.routes import auth, jobs, resumes, applications, analytics
from app.core.monitoring import setup_monitoring

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Indeed Automation Cloud Backend")
    
    # Create database tables
    await create_tables()
    
    # Initialize AI services
    app.state.ai_orchestrator = AIOrchestrator()
    app.state.resume_service = ResumeTailoringService()
    app.state.job_matcher = JobMatchingService()
    app.state.qa_generator = QAGenerationService()
    
    # Setup monitoring
    setup_monitoring(app)
    
    logger.info("Cloud backend startup completed")
    yield
    
    logger.info("Shutting down cloud backend")

# Create FastAPI app
app = FastAPI(
    title="Indeed.ca Automation Cloud Backend",
    description="AI-powered job application automation with resume tailoring and intelligent matching",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["Resumes"])
app.include_router(applications.router, prefix="/api/v1/applications", tags=["Applications"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    """Root endpoint with system info"""
    return {
        "service": "Indeed.ca Automation Cloud Backend",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "AI-powered resume tailoring",
            "Job matching and skill analysis", 
            "Automated Q&A generation",
            "Evidence-based reasoning synthesis",
            "ATS optimization",
            "Application tracking"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connectivity
        from app.core.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        
        # Check AI services
        ai_status = "healthy" if hasattr(app.state, 'ai_orchestrator') else "not_initialized"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "connected",
                "ai_orchestrator": ai_status,
                "resume_tailoring": "ready",
                "job_matching": "ready"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Core API endpoints

@app.post("/api/v1/jtr")
async def job_tailored_resume(
    request: Dict,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Job-Tailored Resume (JTR) Generation
    Creates ATS-optimized resume based on job requirements
    """
    try:
        logger.info("JTR request received", job_id=request.get('job_id'))
        
        # Extract job data and user profile
        job_data = request['job']
        user_profile = request['user_profile']
        evidence_vault = request.get('evidence_vault', [])
        
        # Generate tailored resume
        resume_service = app.state.resume_service
        result = await resume_service.create_tailored_resume(
            job_data=job_data,
            user_profile=user_profile,
            evidence_vault=evidence_vault
        )
        
        # Log for analytics
        background_tasks.add_task(
            log_jtr_request,
            user_id=user_profile.get('user_id'),
            job_id=job_data.get('job_id'),
            result=result
        )
        
        return result
        
    except Exception as e:
        logger.error("JTR generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Resume tailoring failed: {str(e)}")

@app.post("/api/v1/job-analysis")
async def analyze_job(
    request: Dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analyze job posting for skills, requirements, and match score
    """
    try:
        job_data = request['job']
        user_profile = request.get('user_profile', {})
        
        # Job matching analysis
        job_matcher = app.state.job_matcher
        analysis = await job_matcher.analyze_job_match(
            job_data=job_data,
            user_profile=user_profile
        )
        
        return analysis
        
    except Exception as e:
        logger.error("Job analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Job analysis failed: {str(e)}")

@app.post("/api/v1/qa-generation")
async def generate_qa(
    request: Dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Generate application questions and answers based on job and profile
    """
    try:
        job_data = request['job']
        user_profile = request['user_profile']
        questions = request.get('questions', [])
        
        # Generate Q&A
        qa_generator = app.state.qa_generator
        qa_bundle = await qa_generator.generate_answers(
            job_data=job_data,
            user_profile=user_profile,
            questions=questions
        )
        
        return {"qa_bundle": qa_bundle}
        
    except Exception as e:
        logger.error("Q&A generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Q&A generation failed: {str(e)}")

@app.post("/api/v1/ats-check")
async def ats_check(
    request: Dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Check resume for ATS compatibility
    """
    try:
        resume_content = request['resume_content']
        
        # ATS compatibility check
        resume_service = app.state.resume_service
        ats_result = await resume_service.check_ats_compatibility(resume_content)
        
        return ats_result
        
    except Exception as e:
        logger.error("ATS check failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"ATS check failed: {str(e)}")

# Background tasks
async def log_jtr_request(user_id: str, job_id: str, result: Dict):
    """Log JTR request for analytics"""
    try:
        from app.models.analytics import JTRRequest
        from app.core.database import get_db
        
        db = next(get_db())
        
        log_entry = JTRRequest(
            user_id=user_id,
            job_id=job_id,
            match_score=result.get('match_score', 0),
            rs_bullet_count=len([b for b in result.get('bullets', []) if b.get('rs', False)]),
            created_at=datetime.utcnow()
        )
        
        db.add(log_entry)
        db.commit()
        
        logger.info("JTR request logged", user_id=user_id, job_id=job_id)
        
    except Exception as e:
        logger.error("Failed to log JTR request", error=str(e))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None  # Use structlog instead
    )