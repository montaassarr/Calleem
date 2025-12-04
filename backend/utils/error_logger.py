"""
Custom Error Logging and Monitoring System
==========================================
Captures all errors, performance metrics, and user actions
Stores in MongoDB for analysis and alerting
"""

from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import traceback
import logging

logger = logging.getLogger(__name__)


class ErrorLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    AUTH = "authentication"
    DATABASE = "database"
    API = "api"
    VOICE_AGENT = "voice_agent"
    AGENT = "agent"
    USER = "user"
    PAYMENT = "payment"
    PERFORMANCE = "performance"
    NETWORK = "network"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


class ErrorLogger:
    """Centralized error logging and monitoring"""
    
    def __init__(self, db=None):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    async def log_error(
        self,
        error: Exception,
        category: ErrorCategory,
        level: ErrorLevel = ErrorLevel.ERROR,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        request_data: Optional[Dict[str, Any]] = None
    ):
        """Log error to database and console"""
        
        error_doc = {
            "timestamp": datetime.utcnow(),
            "level": level,
            "category": category,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "context": context or {},
            "request_data": self._sanitize_request_data(request_data or {}),
            "environment": "production",
            "resolved": False
        }
        
        # Log to console
        self.logger.error(
            f"[{category}] {error_doc['error_type']}: {error_doc['error_message']} | User: {user_id} | Tenant: {tenant_id}",
            exc_info=True
        )
        
        # Save to database
        if self.db is not None:
            try:
                await self.db.error_logs.insert_one(error_doc)
            except Exception as db_error:
                self.logger.critical(f"Failed to save error to database: {db_error}")
        
        return error_doc
    
    async def log_action(
        self,
        action: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        success: bool = True
    ):
        """Log user action for debugging"""
        
        action_doc = {
            "timestamp": datetime.utcnow(),
            "action": action,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "data": self._sanitize_request_data(data or {}),
            "success": success
        }
        
        if self.db is not None:
            try:
                await self.db.action_logs.insert_one(action_doc)
            except Exception as e:
                self.logger.error(f"Failed to log action: {e}")
        
        return action_doc
    
    async def log_performance(
        self,
        endpoint: str,
        duration_ms: float,
        status_code: int,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ):
        """Log API performance metrics"""
        
        perf_doc = {
            "timestamp": datetime.utcnow(),
            "endpoint": endpoint,
            "duration_ms": duration_ms,
            "status_code": status_code,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "is_slow": duration_ms > 2000
        }
        
        if self.db is not None:
            try:
                await self.db.performance_logs.insert_one(perf_doc)
            except Exception as e:
                self.logger.error(f"Failed to log performance: {e}")
        
        if duration_ms > 2000:
            self.logger.warning(f"Slow endpoint: {endpoint} took {duration_ms}ms")
        
        return perf_doc

    async def log_client_error(
        self,
        message: str,
        level: ErrorLevel,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        stack_trace: Optional[str] = None,
        component: Optional[str] = None,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log frontend/client-side errors"""
        doc = {
            "timestamp": datetime.utcnow(),
            "level": level,
            "message": message,
            "stack_trace": stack_trace,
            "component": component,
            "url": url,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "metadata": self._sanitize_request_data(metadata or {})
        }
        
        self.logger.error(
            f"[frontend] {message} | Component: {component} | User: {user_id}"
        )
        
        if self.db is not None:
            try:
                await self.db.frontend_error_logs.insert_one(doc)
            except Exception as e:
                self.logger.error(f"Failed to log client error: {e}")
        
        return doc
    
    async def log_client_performance(
        self,
        metric: str,
        duration_ms: float,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log frontend performance metrics"""
        doc = {
            "timestamp": datetime.utcnow(),
            "metric": metric,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "metadata": self._sanitize_request_data(metadata or {}),
            "is_slow": duration_ms > 2000
        }
        
        if duration_ms > 2000:
            self.logger.warning(f"Frontend metric {metric} is slow: {duration_ms}ms")
        
        if self.db is not None:
            try:
                await self.db.frontend_performance_logs.insert_one(doc)
            except Exception as e:
                self.logger.error(f"Failed to log client performance: {e}")
        
        return doc
    
    def _sanitize_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from logs"""
        sensitive_keys = [
            'password', 'token', 'secret', 'api_key', 'access_token',
            'refresh_token', 'credit_card', 'cvv', 'ssn', 'hashed_password'
        ]
        
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_request_data(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    async def get_error_stats(self, tenant_id: Optional[str] = None, hours: int = 24):
        """Get error statistics for monitoring"""
        from datetime import timedelta
        
        if self.db is None:
            return {}
        
        since = datetime.utcnow() - timedelta(hours=hours)
        query = {"timestamp": {"$gte": since}}
        
        if tenant_id:
            query["tenant_id"] = tenant_id
        
        try:
            total_errors = await self.db.error_logs.count_documents(query)
            
            # Group by category
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$category",
                    "count": {"$sum": 1}
                }}
            ]
            category_stats = await self.db.error_logs.aggregate(pipeline).to_list(None)
            
            # Recent critical errors
            critical_errors = await self.db.error_logs.find(
                {**query, "level": ErrorLevel.CRITICAL}
            ).limit(10).to_list(10)
            
            return {
                "total_errors": total_errors,
                "by_category": {item["_id"]: item["count"] for item in category_stats},
                "critical_errors": critical_errors
            }
        except Exception as e:
            self.logger.error(f"Failed to get error stats: {e}")
            return {}


# Global error logger instance
error_logger = ErrorLogger()


def set_error_logger_db(db):
    """Set database for error logger"""
    error_logger.db = db
