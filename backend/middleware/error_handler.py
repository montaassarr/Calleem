"""
Global Exception Handler Middleware
====================================
Catches all unhandled exceptions and logs them
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

from utils.error_logger import error_logger, ErrorCategory, ErrorLevel

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to catch and log all errors"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log performance
            duration_ms = (time.time() - start_time) * 1000
            
            # Extract user context if available
            user_id = None
            tenant_id = None
            if hasattr(request.state, "user"):
                user_id = request.state.user.get("id")
                tenant_id = request.state.user.get("tenant_id")
            
            await error_logger.log_performance(
                endpoint=f"{request.method} {request.url.path}",
                duration_ms=duration_ms,
                status_code=response.status_code,
                user_id=user_id,
                tenant_id=tenant_id
            )
            
            return response
            
        except HTTPException as e:
            # Log HTTP exceptions
            duration_ms = (time.time() - start_time) * 1000
            
            user_id = None
            tenant_id = None
            if hasattr(request.state, "user"):
                user_id = request.state.user.get("id")
                tenant_id = request.state.user.get("tenant_id")
            
            await error_logger.log_error(
                error=e,
                category=self._categorize_error(e),
                level=ErrorLevel.WARNING if e.status_code < 500 else ErrorLevel.ERROR,
                user_id=user_id,
                tenant_id=tenant_id,
                context={
                    "status_code": e.status_code,
                    "detail": e.detail
                },
                request_data={
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query),
                    "duration_ms": duration_ms
                }
            )
            
            raise e
            
        except Exception as e:
            # Log unhandled exceptions
            duration_ms = (time.time() - start_time) * 1000
            
            user_id = None
            tenant_id = None
            if hasattr(request.state, "user"):
                user_id = request.state.user.get("id")
                tenant_id = request.state.user.get("tenant_id")
            
            await error_logger.log_error(
                error=e,
                category=ErrorCategory.UNKNOWN,
                level=ErrorLevel.CRITICAL,
                user_id=user_id,
                tenant_id=tenant_id,
                context={
                    "error_type": type(e).__name__
                },
                request_data={
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query),
                    "duration_ms": duration_ms
                }
            )
            
            logger.critical(
                f"Unhandled exception in {request.method} {request.url.path}: {str(e)}",
                exc_info=True
            )
            
            # Return generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error. The error has been logged and will be investigated.",
                    "error_id": str(time.time())
                }
            )
    
    def _categorize_error(self, error: HTTPException) -> ErrorCategory:
        """Categorize error based on status code and message"""
        if error.status_code in [401, 403]:
            return ErrorCategory.AUTH
        elif error.status_code == 404:
            return ErrorCategory.API
        elif error.status_code == 400:
            return ErrorCategory.VALIDATION
        elif error.status_code >= 500:
            return ErrorCategory.UNKNOWN
        return ErrorCategory.API
