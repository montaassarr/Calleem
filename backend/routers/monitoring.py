"""Monitoring & Diagnostics API"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from utils.error_logger import error_logger, ErrorLevel

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


class FrontendErrorPayload(BaseModel):
    message: str = Field(..., min_length=1)
    level: ErrorLevel = ErrorLevel.ERROR
    stack: Optional[str] = None
    component: Optional[str] = None
    url: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FrontendActionPayload(BaseModel):
    action: str = Field(..., min_length=1)
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True


class FrontendPerformancePayload(BaseModel):
    metric: str = Field(..., min_length=1)
    duration_ms: float = Field(gt=0)
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.post("/frontend-error", status_code=201)
async def log_frontend_error(payload: FrontendErrorPayload):
    await error_logger.log_client_error(
        message=payload.message,
        level=payload.level,
        user_id=payload.user_id,
        tenant_id=payload.tenant_id,
        stack_trace=payload.stack,
        component=payload.component,
        url=payload.url,
        metadata=payload.metadata,
    )
    return {"status": "recorded"}


@router.post("/frontend-action", status_code=201)
async def log_frontend_action(payload: FrontendActionPayload):
    await error_logger.log_action(
        action=payload.action,
        user_id=payload.user_id,
        tenant_id=payload.tenant_id,
        data=payload.data,
        success=payload.success
    )
    return {"status": "recorded"}


@router.post("/frontend-performance", status_code=201)
async def log_frontend_performance(payload: FrontendPerformancePayload):
    await error_logger.log_client_performance(
        metric=payload.metric,
        duration_ms=payload.duration_ms,
        user_id=payload.user_id,
        tenant_id=payload.tenant_id,
        metadata=payload.metadata
    )
    return {"status": "recorded"}
