"""
Local Companion Script for Indeed.ca Automation
Handles PyAutoGUI operations, OCR, and file uploads as fallback methods
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import pyautogui
import pytesseract
from PIL import Image, ImageGrab
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('companion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configure PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

app = FastAPI(title="Indeed Automation Local Companion", version="1.0.0")

# CORS middleware for Chrome extension communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)


class ClickCoordinates(BaseModel):
    x: int
    y: int
    button: str = "left"
    clicks: int = 1


class TypeText(BaseModel):
    text: str
    interval: float = 0.05


class FileUpload(BaseModel):
    file_path: str
    input_selector: str


class ScreenshotRequest(BaseModel):
    region: Optional[Dict[str, int]] = None
    filename: Optional[str] = None


class OCRRequest(BaseModel):
    region: Optional[Dict[str, int]] = None
    search_text: str


class IndeedCompanion:
    def __init__(self):
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
        
    def get_active_window_coords(self) -> Tuple[int, int, int, int]:
        """Get coordinates of the active browser window"""
        try:
            # Take a screenshot to get screen dimensions
            screenshot = ImageGrab.grab()
            screen_width, screen_height = screenshot.size
            return 0, 0, screen_width, screen_height
        except Exception as e:
            logger.error(f"Error getting window coordinates: {e}")
            return 0, 0, 1920, 1080  # Default fallback
    
    def take_screenshot(self, region: Optional[Dict] = None, filename: Optional[str] = None) -> str:
        """Take screenshot of specified region or full screen"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not filename:
                filename = f"screenshot_{timestamp}.png"
            
            filepath = self.screenshots_dir / filename
            
            if region:
                bbox = (region['left'], region['top'], 
                       region['left'] + region['width'], 
                       region['top'] + region['height'])
                screenshot = ImageGrab.grab(bbox=bbox)
            else:
                screenshot = ImageGrab.grab()
            
            screenshot.save(filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def click_coordinates(self, x: int, y: int, button: str = "left", clicks: int = 1):
        """Click at specific coordinates with error handling"""
        try:
            # Ensure coordinates are within screen bounds
            screen_width, screen_height = pyautogui.size()
            x = max(0, min(x, screen_width - 1))
            y = max(0, min(y, screen_height - 1))
            
            # Move to position first
            pyautogui.moveTo(x, y, duration=0.2)
            time.sleep(0.1)
            
            # Take screenshot before click for debugging
            self.take_screenshot(filename=f"before_click_{x}_{y}.png")
            
            # Perform click
            if button == "right":
                pyautogui.rightClick(x, y, clicks=clicks)
            else:
                pyautogui.click(x, y, clicks=clicks, button=button)
            
            logger.info(f"Clicked at ({x}, {y}) with {button} button, {clicks} clicks")
            time.sleep(0.2)
            
            # Take screenshot after click
            self.take_screenshot(filename=f"after_click_{x}_{y}.png")
            
        except Exception as e:
            logger.error(f"Error clicking coordinates ({x}, {y}): {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def type_text(self, text: str, interval: float = 0.05):
        """Type text with natural intervals"""
        try:
            # Clear any existing text first (Ctrl+A, Delete)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('delete')
            time.sleep(0.1)
            
            # Type the text
            pyautogui.write(text, interval=interval)
            logger.info(f"Typed text: {text[:50]}...")
            time.sleep(0.2)
            
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def find_text_with_ocr(self, search_text: str, region: Optional[Dict] = None) -> Optional[Tuple[int, int]]:
        """Find text on screen using OCR and return click coordinates"""
        try:
            # Take screenshot
            if region:
                bbox = (region['left'], region['top'], 
                       region['left'] + region['width'], 
                       region['top'] + region['height'])
                screenshot = ImageGrab.grab(bbox=bbox)
                offset_x, offset_y = region['left'], region['top']
            else:
                screenshot = ImageGrab.grab()
                offset_x, offset_y = 0, 0
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Use Tesseract to get text and bounding boxes
            ocr_data = pytesseract.image_to_data(opencv_image, output_type=pytesseract.Output.DICT)
            
            # Search for the text
            for i, text in enumerate(ocr_data['text']):
                if search_text.lower() in text.lower() and int(ocr_data['conf'][i]) > 30:
                    # Calculate center coordinates
                    x = offset_x + ocr_data['left'][i] + ocr_data['width'][i] // 2
                    y = offset_y + ocr_data['top'][i] + ocr_data['height'][i] // 2
                    
                    logger.info(f"Found text '{search_text}' at ({x}, {y})")
                    return x, y
            
            logger.warning(f"Text '{search_text}' not found with OCR")
            return None
            
        except Exception as e:
            logger.error(f"Error with OCR text search: {e}")
            return None
    
    def upload_file(self, file_path: str) -> bool:
        """Handle file upload using system file dialog"""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=400, detail=f"File not found: {file_path}")
            
            # Wait a moment for file dialog to appear
            time.sleep(1)
            
            # Type the file path directly
            pyautogui.write(file_path)
            time.sleep(0.5)
            
            # Press Enter to confirm
            pyautogui.press('enter')
            time.sleep(1)
            
            logger.info(f"File uploaded: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def scroll_to_element(self, direction: str = "down", clicks: int = 3):
        """Scroll to bring elements into view"""
        try:
            if direction == "down":
                pyautogui.scroll(-clicks)
            else:
                pyautogui.scroll(clicks)
            
            time.sleep(0.5)
            logger.info(f"Scrolled {direction} {clicks} clicks")
            
        except Exception as e:
            logger.error(f"Error scrolling: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def focus_browser_window(self):
        """Attempt to focus the browser window"""
        try:
            # Click on browser window (assuming it's the active window)
            screen_width, screen_height = pyautogui.size()
            center_x, center_y = screen_width // 2, screen_height // 2
            
            pyautogui.click(center_x, center_y)
            time.sleep(0.5)
            
            logger.info("Focused browser window")
            
        except Exception as e:
            logger.error(f"Error focusing window: {e}")


# Initialize companion
companion = IndeedCompanion()


# API Endpoints
@app.post("/click")
async def click_endpoint(coords: ClickCoordinates):
    """Click at specified coordinates"""
    companion.click_coordinates(coords.x, coords.y, coords.button, coords.clicks)
    return {"status": "success", "message": f"Clicked at ({coords.x}, {coords.y})"}


@app.post("/type")
async def type_endpoint(request: TypeText):
    """Type text at current cursor position"""
    companion.type_text(request.text, request.interval)
    return {"status": "success", "message": "Text typed successfully"}


@app.post("/upload")
async def upload_endpoint(request: FileUpload):
    """Handle file upload"""
    success = companion.upload_file(request.file_path)
    if success:
        return {"status": "success", "message": "File uploaded successfully"}
    else:
        raise HTTPException(status_code=500, detail="File upload failed")


@app.post("/screenshot")
async def screenshot_endpoint(request: ScreenshotRequest):
    """Take screenshot"""
    filepath = companion.take_screenshot(request.region, request.filename)
    return {"status": "success", "filepath": filepath}


@app.post("/ocr_find")
async def ocr_find_endpoint(request: OCRRequest):
    """Find text using OCR"""
    coords = companion.find_text_with_ocr(request.search_text, request.region)
    if coords:
        return {"status": "success", "coordinates": {"x": coords[0], "y": coords[1]}}
    else:
        return {"status": "not_found", "message": f"Text '{request.search_text}' not found"}


@app.post("/scroll")
async def scroll_endpoint(direction: str = "down", clicks: int = 3):
    """Scroll page"""
    companion.scroll_to_element(direction, clicks)
    return {"status": "success", "message": f"Scrolled {direction}"}


@app.post("/focus")
async def focus_endpoint():
    """Focus browser window"""
    companion.focus_browser_window()
    return {"status": "success", "message": "Browser window focused"}


@app.get("/health")
async def health_check(response: Response):
    """Health check endpoint with explicit CORS headers"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return {"status": "healthy", "service": "Indeed Automation Local Companion"}

@app.options("/health")
@app.options("/click")
@app.options("/type")
@app.options("/upload")
@app.options("/screenshot")
@app.options("/ocr_find")
@app.options("/scroll")
@app.options("/focus")
async def handle_options():
    """Handle OPTIONS preflight requests for all endpoints"""
    return {"message": "OK"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Indeed Automation Local Companion",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    logger.info("Starting Indeed Automation Local Companion...")
    logger.info("Endpoints available:")
    logger.info("  POST /click - Click at coordinates")
    logger.info("  POST /type - Type text")
    logger.info("  POST /upload - Upload file")
    logger.info("  POST /screenshot - Take screenshot")
    logger.info("  POST /ocr_find - Find text with OCR")
    logger.info("  POST /scroll - Scroll page")
    logger.info("  POST /focus - Focus browser window")
    logger.info("  GET /health - Health check")
    
    # Test PyAutoGUI and OCR setup
    try:
        screen_size = pyautogui.size()
        logger.info(f"Screen size detected: {screen_size}")
        
        # Test OCR (optional - just log if tesseract is available)
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
        except Exception:
            logger.warning("Tesseract OCR not available - OCR features will be limited")
            
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
    
    # Try different ports if 8001 is in use
    import socket
    
    def find_free_port(start_port=8001):
        # Prefer 8001 for extension compatibility
        preferred_ports = [8001, 8002, 8003, 8080]
        
        for port in preferred_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        
        # Try other ports if preferred ones are taken
        for port in range(8010, 8030):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        
        return 8001  # fallback
    
    port = find_free_port()
    logger.info(f"Starting server on port {port}")
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=port, 
        log_level="info"
    )