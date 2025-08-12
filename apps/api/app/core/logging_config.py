"""
Logging configuration with security compliance
- Never log full secrets
- Structured logging for monitoring
- Safe masking of sensitive data
"""

import structlog
import logging
import sys
from typing import Any, Dict

def mask_sensitive_data(event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive data in log events"""
    
    # List of sensitive keys to mask
    sensitive_keys = {
        "password", "token", "key", "secret", "authorization", 
        "api_key", "openai_api_key", "anthropic_api_key", "deepseek_api_key",
        "companion_token", "secret_key", "database_url", "redis_url"
    }
    
    def mask_value(key: str, value: Any) -> Any:
        if isinstance(key, str) and any(sensitive in key.lower() for sensitive in sensitive_keys):
            if isinstance(value, str) and len(value) > 8:
                return f"{value[:8]}***"
            return "***"
        return value
    
    # Recursively mask sensitive data
    def mask_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        return {
            k: mask_dict(v) if isinstance(v, dict) else mask_value(k, v)
            for k, v in d.items()
        }
    
    return mask_dict(event_dict)

def setup_logging(debug: bool = False) -> None:
    """Setup structured logging with security compliance"""
    
    # Configure log level
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Configure structlog processors
    processors = [
        # Filter by log level
        structlog.stdlib.filter_by_level,
        
        # Add logger name
        structlog.stdlib.add_logger_name,
        
        # Add log level
        structlog.stdlib.add_log_level,
        
        # Add timestamp
        structlog.processors.TimeStamper(fmt="ISO"),
        
        # Mask sensitive data (CRITICAL FOR SECURITY)
        mask_sensitive_data,
        
        # Add caller info in debug mode
        structlog.processors.CallsiteParameterAdder(
            parameters=[structlog.processors.CallsiteParameter.FILENAME,
                       structlog.processors.CallsiteParameter.FUNC_NAME,
                       structlog.processors.CallsiteParameter.LINENO]
        ) if debug else lambda logger, method_name, event_dict: event_dict,
        
        # Handle positional arguments
        structlog.stdlib.PositionalArgumentsFormatter(),
        
        # Add stack info on exceptions
        structlog.processors.StackInfoRenderer(),
        
        # Format exceptions
        structlog.processors.format_exc_info,
        
        # JSON renderer for production, colorized for development
        structlog.dev.ConsoleRenderer(colors=True) if debug else structlog.processors.JSONRenderer()
    ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format="%(message)s",
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.error").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING if not debug else log_level)
    
    # Silence noisy loggers in production
    if not debug:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("anthropic").setLevel(logging.WARNING)

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance"""
    return structlog.get_logger(name)