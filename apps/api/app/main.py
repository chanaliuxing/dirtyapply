"""
Apply-Copilot FastAPI Backend
Job-Driven Resume Rewriter & Auto-Apply Agent

Implements Golden Rules:
- No hard-coded secrets
- Fail-fast configuration validation
- Safe logging practices
- Centralized configuration
"""

import structlog
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import traceback
import sys

# Import configuration FIRST - this validates environment
from app.core.config import get_settings, validate_environment
from app.core.database import init_db
from app.core.logging_config import setup_logging

# Configure structured logging early
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with fail-fast validation"""
    logger.info("🚀 Starting Apply-Copilot API Backend")
    
    try:
        # Step 1: Validate environment (fail-fast)
        validate_environment()
        settings = get_settings()
        
        # Step 2: Setup logging
        setup_logging(debug=settings.debug)
        
        # Step 3: Initialize database
        await init_db()
        
        # Step 4: Validate AI providers
        if settings.llm_provider != "none":
            logger.info(f"AI provider configured: {settings.llm_provider}")
        else:
            logger.info("Running in rule-based mode (no AI provider)")
        
        logger.info("✅ Application startup completed successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    finally:
        logger.info("🛑 Shutting down Apply-Copilot API Backend")

# Create FastAPI app with secure configuration
def create_app() -> FastAPI:
    """Create FastAPI application with security and monitoring"""
    
    settings = get_settings()
    
    app = FastAPI(
        title="Apply-Copilot API",
        description="Job-Driven Resume Rewriter & Auto-Apply Agent",
        version=settings.version,
        docs_url="/docs" if settings.debug else None,  # Disable docs in production
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Security Middleware
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", settings.api_host]
        )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = datetime.now()
        
        # Log request (safely mask sensitive headers)
        headers = dict(request.headers)
        if "authorization" in headers:
            headers["authorization"] = f"Bearer ***{headers['authorization'][-8:]}"
        if "x-auth-token" in headers:
            headers["x-auth-token"] = f"***{headers['x-auth-token'][-8:]}"
        
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url.remove_query()),
            client_ip=request.client.host if request.client else "unknown",
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                "Request completed",
                method=request.method,
                url=str(request.url.remove_query()),
                status_code=response.status_code,
                duration_seconds=duration,
            )
            
            return response
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(
                "Request failed",
                method=request.method,
                url=str(request.url.remove_query()),
                error=str(e),
                duration_seconds=duration,
                traceback=traceback.format_exc(),
            )
            
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
    
    return app

# Create the app instance
app = create_app()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    settings = get_settings()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.version,
        "app_name": settings.app_name,
        "environment": "development" if settings.debug else "production",
        "llm_provider": settings.llm_provider,
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Apply-Copilot API",
        "version": get_settings().version,
        "docs": "/docs" if get_settings().debug else "disabled",
    }

# LLM Test endpoint (debug only)
@app.post("/api/llm/test")
async def test_llm(request: dict):
    """
    Test LLM provider integration
    Only available in debug mode
    """
    settings = get_settings()
    
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Endpoint not available in production")
    
    from app.services.llm_provider import generate_llm_response
    
    try:
        messages = request.get("messages", [
            {"role": "user", "content": "Hello, please respond with information about which AI provider you are and test your functionality."}
        ])
        
        response = await generate_llm_response(
            messages, 
            max_tokens=request.get("max_tokens", 200)
        )
        
        return {
            "provider": settings.llm_provider,
            "response": response,
            "status": "success",
            "model_info": {
                "openai": "Uses OpenAI GPT models",
                "deepseek-nvidia": "Uses DeepSeek R1 via NVIDIA API",
                "anthropic": "Uses Anthropic Claude models",
                "none": "Rule-based responses (offline mode)"
            }.get(settings.llm_provider, "Unknown provider")
        }
        
    except Exception as e:
        logger.error(f"LLM test error: {e}")
        return {
            "provider": settings.llm_provider,
            "error": str(e),
            "status": "error",
            "fallback": "Rule-based provider will be used"
        }

# JTR endpoint (core functionality)
@app.post("/api/jtr")
async def generate_jtr(request: dict):
    """
    Generate Job-Tailored Resume with Reasoned Synthesis
    
    Input: JTR request schema
    Output: Tailored resume, match score, diff report, action plan
    """
    logger.info("JTR request received", provider=get_settings().llm_provider)
    
    # TODO: Implement full JTR engine - this is a demo endpoint
    from app.services.llm_provider import generate_llm_response
    
    try:
        # Demo: Use LLM to analyze the request
        messages = [
            {
                "role": "system", 
                "content": "You are an expert resume writer. Analyze job requirements and provide tailored resume suggestions with evidence-based reasoning."
            },
            {
                "role": "user", 
                "content": f"Analyze this job application request: {str(request)[:500]}..."
            }
        ]
        
        llm_response = await generate_llm_response(messages, max_tokens=500)
        
        return {
            "message": "JTR endpoint - demonstration mode",
            "request_id": f"jtr_{hash(str(request)) % 10000}",
            "match_score": 0.85,
            "status": "demo_complete",
            "llm_provider": get_settings().llm_provider,
            "analysis": llm_response,
            "note": "Full JTR implementation in progress - this demonstrates LLM integration"
        }
        
    except Exception as e:
        logger.error(f"JTR processing error: {e}")
        return {
            "message": "JTR endpoint - fallback mode",
            "request_id": "fallback",
            "match_score": 0.75,
            "status": "rule_based",
            "analysis": "Rule-based analysis: Resume tailoring would analyze job requirements against candidate profile.",
            "error": str(e)
        }

# Action Plan endpoint
@app.post("/api/plan")
async def generate_action_plan(request: dict):
    """
    Generate Action Plan for form filling
    
    Input: Field mapping and page context
    Output: Action plan with selectors, modes, dependencies
    """
    logger.info("Action plan request received")
    
    # TODO: Implement action planner
    return {
        "message": "Action plan endpoint - implementation in progress",
        "action_plan": [],
        "estimated_duration": "30s"
    }

# Submit guard endpoint
@app.post("/api/submit-guard")
async def submit_guard(request: dict):
    """
    Pre-submission validation and snapshot
    
    Input: Form data and context
    Output: Validation result and snapshot ID
    """
    logger.info("Submit guard request received")
    
    # TODO: Implement submit guard
    return {
        "message": "Submit guard endpoint - implementation in progress",
        "validation_passed": True,
        "snapshot_id": "placeholder"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"detail": f"Path {request.url.path} not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle 500 errors with safe logging"""
    logger.error(
        "Internal server error",
        url=str(request.url),
        error=str(exc),
        traceback=traceback.format_exc(),
    )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    # Safe logging of startup configuration
    logger.info(
        "Starting server",
        host=settings.api_host,
        port=settings.api_port,
        debug=settings.debug,
        workers=settings.api_workers,
    )
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=settings.api_workers if not settings.debug else 1,
        log_level="debug" if settings.debug else "info",
    )