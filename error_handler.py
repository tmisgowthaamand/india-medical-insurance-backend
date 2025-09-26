"""
Enhanced Error Handling for MediCare+ Backend
Provides detailed error logging and user-friendly error responses
"""

import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for the application"""
    
    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with detailed logging"""
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        logger.error(f"Request: {request.method} {request.url}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path)
            }
        )
    
    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors with detailed information"""
        logger.error(f"Validation Error: {exc.errors()}")
        logger.error(f"Request: {request.method} {request.url}")
        
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message": "Validation Error",
                "details": exc.errors(),
                "status_code": 422,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path)
            }
        )
    
    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions with full error details"""
        error_traceback = traceback.format_exc()
        logger.error(f"Unhandled Exception: {str(exc)}")
        logger.error(f"Request: {request.method} {request.url}")
        logger.error(f"Traceback: {error_traceback}")
        
        # Determine if this is a database error
        error_message = str(exc).lower()
        if any(keyword in error_message for keyword in ['pgrst', 'supabase', 'database', 'connection']):
            user_message = "Database connection error. Please check if the database is properly configured."
            error_type = "database_error"
        elif 'model' in error_message:
            user_message = "AI model error. The prediction model may not be properly loaded."
            error_type = "model_error"
        elif 'file' in error_message or 'path' in error_message:
            user_message = "File system error. Required files may be missing."
            error_type = "file_error"
        else:
            user_message = "Internal server error. Please try again later."
            error_type = "general_error"
        
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": user_message,
                "error_type": error_type,
                "status_code": 500,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path),
                "debug_info": {
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc)
                } if logger.level <= logging.DEBUG else None
            }
        )

def setup_error_handlers(app):
    """Setup all error handlers for the FastAPI app"""
    
    # Add exception handlers
    app.add_exception_handler(HTTPException, ErrorHandler.http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, ErrorHandler.http_exception_handler)
    app.add_exception_handler(RequestValidationError, ErrorHandler.validation_exception_handler)
    app.add_exception_handler(Exception, ErrorHandler.general_exception_handler)
    
    logger.info("Error handlers configured successfully")

def log_startup_info():
    """Log important startup information"""
    import os
    
    logger.info("🏥 MediCare+ Backend Starting Up")
    logger.info("=" * 40)
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Supabase URL: {os.getenv('SUPABASE_URL', 'Not configured')[:50]}...")
    logger.info(f"JWT Secret: {'Configured' if os.getenv('JWT_SECRET_KEY') else 'Not configured'}")
    logger.info("=" * 40)

def log_request_info(request: Request):
    """Log detailed request information for debugging"""
    logger.debug(f"Request: {request.method} {request.url}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Client: {request.client}")

# Middleware for request logging
async def request_logging_middleware(request: Request, call_next):
    """Middleware to log all requests"""
    start_time = datetime.now()
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # Log response
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"← {response.status_code} {request.method} {request.url.path} ({duration:.3f}s)")
        
        return response
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"← ERROR {request.method} {request.url.path} ({duration:.3f}s): {str(e)}")
        raise
