"""
Apply-Copilot Companion Service
Local automation service with secure configuration

Implements Golden Rules:
- No hard-coded tokens
- Fail-fast validation  
- Safe logging
- Local-only security (127.0.0.1)
"""

import structlog
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, BaseSettings, Field, validator
from contextlib import asynccontextmanager
from typing import Optional, Tuple
import pyautogui
import pytesseract
import cv2
import numpy as np
from PIL import Image
import mss
import os
import sys
from datetime import datetime
import traceback

# Configure PyAutoGUI safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(colors=True)
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

def mask_token(token: str) -> str:
    """Safely mask tokens for logging"""
    if not token or len(token) <= 8:
        return "***"
    return f"{token[:8]}***"

class CompanionSettings(BaseSettings):
    """
    Companion service configuration with security validation
    NEVER stores hard-coded secrets
    """
    
    # Service Configuration (local-only for security)
    host: str = Field("127.0.0.1", env="COMPANION_HOST")
    port: int = Field(8765, env="COMPANION_PORT")
    
    # Security (required)
    auth_token: str = Field(..., env="COMPANION_TOKEN")
    
    # Feature Configuration
    enable_ocr: bool = Field(True, env="ENABLE_OCR")
    enable_screenshots: bool = Field(True, env="ENABLE_SCREENSHOTS")
    coordinate_tolerance: int = Field(3, env="COORDINATE_TOLERANCE")
    
    # Safety Limits
    max_click_distance: int = Field(50, env="MAX_CLICK_DISTANCE")
    action_timeout_ms: int = Field(5000, env="ACTION_TIMEOUT_MS")
    
    # Debug
    debug: bool = Field(False, env="DEBUG")
    
    @validator("host")
    def validate_host(cls, v):
        # CRITICAL SECURITY: Only allow localhost for companion service
        if v not in ["127.0.0.1", "localhost"]:
            raise ValueError("Companion service MUST run on localhost only (127.0.0.1)")
        return v
    
    @validator("auth_token")
    def validate_auth_token(cls, v):
        if len(v) < 32:
            raise ValueError("COMPANION_TOKEN must be at least 32 characters for security")
        return v
    
    def log_startup_config(self):
        """Log configuration safely"""
        logger.info(
            "Companion service configuration",
            host=self.host,
            port=self.port,
            auth_token=mask_token(self.auth_token),
            enable_ocr=self.enable_ocr,
            enable_screenshots=self.enable_screenshots,
            coordinate_tolerance=self.coordinate_tolerance,
            debug=self.debug,
        )
    
    class Config:
        env_file = ".env"

# Global settings instance
settings: Optional[CompanionSettings] = None

def get_settings() -> CompanionSettings:
    """Get settings with fail-fast validation"""
    global settings
    if settings is None:
        try:
            settings = CompanionSettings()
            settings.log_startup_config()
            logger.info("✅ Companion configuration validation successful")
        except Exception as e:
            logger.error(f"❌ Companion configuration validation failed: {e}")
            raise SystemExit(f"Configuration error: {e}")
    return settings

# Request/Response Models
class ClickRequest(BaseModel):
    x: int
    y: int
    rect: Optional[dict] = None
    screen_offset: Optional[dict] = None
    device_pixel_ratio: float = 1.0

class TypeRequest(BaseModel):
    text: str
    x: Optional[int] = None
    y: Optional[int] = None
    rect: Optional[dict] = None
    screen_offset: Optional[dict] = None
    device_pixel_ratio: float = 1.0

class OCRClickRequest(BaseModel):
    text_pattern: str
    confirm: bool = True
    region: Optional[dict] = None

class ActionResponse(BaseModel):
    success: bool
    message: str
    timestamp: str
    duration_ms: Optional[int] = None
    coordinates: Optional[Tuple[int, int]] = None

# Authentication
async def verify_token(x_auth_token: str = Header(None)):
    """Verify authentication token"""
    settings = get_settings()
    
    if not x_auth_token:
        logger.warning("Authentication failed: missing token")
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    if x_auth_token != settings.auth_token:
        logger.warning(
            "Authentication failed: invalid token", 
            provided_token=mask_token(x_auth_token)
        )
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with validation"""
    logger.info("🚀 Starting Apply-Copilot Companion Service")
    
    try:
        # Validate settings
        settings = get_settings()
        
        # Check system requirements
        try:
            screen_size = pyautogui.size()
            logger.info(f"Screen size detected: {screen_size}")
        except Exception as e:
            logger.error(f"Failed to detect screen: {e}")
            raise
        
        # Check OCR if enabled
        if settings.enable_ocr:
            try:
                # Test OCR installation
                pytesseract.get_tesseract_version()
                logger.info("✅ OCR (Tesseract) available")
            except Exception as e:
                logger.warning(f"OCR not available: {e}")
        
        logger.info("✅ Companion service startup completed")
        yield
        
    except Exception as e:
        logger.error(f"❌ Companion service startup failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    finally:
        logger.info("🛑 Shutting down Companion Service")

# Create FastAPI app
def create_app() -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="Apply-Copilot Companion Service",
        description="Local automation service for browser interactions",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if get_settings().debug else None,
    )
    
    # CORS for local development only
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:*", "chrome-extension://*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    return app

app = create_app()

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "companion",
        "screen_size": pyautogui.size(),
        "ocr_enabled": get_settings().enable_ocr,
    }

# Focus window
@app.post("/focus", dependencies=[Depends(verify_token)])
async def focus_window() -> ActionResponse:
    """Ensure browser window is focused"""
    start_time = datetime.now()
    
    try:
        # Bring window to front (platform-specific)
        if os.name == 'nt':  # Windows
            pyautogui.keyDown('alt')
            pyautogui.press('tab')
            pyautogui.keyUp('alt')
        else:  # macOS/Linux
            pyautogui.keyDown('cmd')
            pyautogui.press('tab')
            pyautogui.keyUp('cmd')
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.info("Window focus action completed", duration_ms=duration)
        
        return ActionResponse(
            success=True,
            message="Window focused",
            timestamp=datetime.now().isoformat(),
            duration_ms=int(duration)
        )
        
    except Exception as e:
        logger.error(f"Focus window failed: {e}")
        return ActionResponse(
            success=False,
            message=f"Focus failed: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

# Click endpoint
@app.post("/click", dependencies=[Depends(verify_token)])
async def click_element(request: ClickRequest) -> ActionResponse:
    """Click at specified coordinates"""
    start_time = datetime.now()
    
    try:
        # Calculate actual screen coordinates
        x, y = request.x, request.y
        
        # Apply device pixel ratio and screen offset if provided
        if request.rect and request.screen_offset:
            # Convert CSS coordinates to screen coordinates
            x = request.rect.get('x', 0) + request.screen_offset.get('x', 0)
            y = request.rect.get('y', 0) + request.screen_offset.get('y', 0)
            x = int(x * request.device_pixel_ratio)
            y = int(y * request.device_pixel_ratio)
        
        # Safety check - ensure coordinates are within screen bounds
        screen_width, screen_height = pyautogui.size()
        if not (0 <= x <= screen_width and 0 <= y <= screen_height):
            raise ValueError(f"Coordinates ({x}, {y}) outside screen bounds")
        
        # Perform click
        pyautogui.click(x, y)
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.info(
            "Click action completed",
            coordinates=(x, y),
            duration_ms=duration
        )
        
        return ActionResponse(
            success=True,
            message="Click successful",
            timestamp=datetime.now().isoformat(),
            duration_ms=int(duration),
            coordinates=(x, y)
        )
        
    except Exception as e:
        logger.error(f"Click action failed: {e}")
        return ActionResponse(
            success=False,
            message=f"Click failed: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

# Type endpoint  
@app.post("/type", dependencies=[Depends(verify_token)])
async def type_text(request: TypeRequest) -> ActionResponse:
    """Type text at current cursor or specified location"""
    start_time = datetime.now()
    
    try:
        # Click at location if coordinates provided
        if request.x is not None and request.y is not None:
            x, y = request.x, request.y
            
            # Apply coordinate conversion if needed
            if request.rect and request.screen_offset:
                x = request.rect.get('x', 0) + request.screen_offset.get('x', 0)
                y = request.rect.get('y', 0) + request.screen_offset.get('y', 0)
                x = int(x * request.device_pixel_ratio)
                y = int(y * request.device_pixel_ratio)
            
            pyautogui.click(x, y)
        
        # Type the text
        pyautogui.typewrite(request.text)
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.info(
            "Type action completed",
            text_length=len(request.text),
            duration_ms=duration
        )
        
        return ActionResponse(
            success=True,
            message=f"Typed {len(request.text)} characters",
            timestamp=datetime.now().isoformat(),
            duration_ms=int(duration)
        )
        
    except Exception as e:
        logger.error(f"Type action failed: {e}")
        return ActionResponse(
            success=False,
            message=f"Type failed: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

# Screenshot endpoint
@app.post("/screenshot", dependencies=[Depends(verify_token)])
async def take_screenshot():
    """Take screenshot and return base64 encoded image"""
    settings = get_settings()
    
    if not settings.enable_screenshots:
        raise HTTPException(status_code=403, detail="Screenshots disabled")
    
    try:
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1])  # Primary monitor
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
        logger.info("Screenshot captured", size=screenshot.size)
        
        # Return base64 encoded image (in real implementation)
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "size": screenshot.size,
            "message": "Screenshot captured (base64 encoding not implemented in demo)"
        }
        
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        raise HTTPException(status_code=500, detail=f"Screenshot failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    logger.info(
        "Starting Companion Service",
        host=settings.host,
        port=settings.port,
        debug=settings.debug
    )
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )