"""
Business configuration for the signed-in business (tenant-scoped).

Served at /api/v1/admin/config because the client dashboard already calls that URL, but it is
not part of the platform admin API: business owners and their admins read and update their
own tenant's settings here, so it stays mounted when ADMIN_API_ENABLED is false.
"""

from fastapi import APIRouter, Depends

from routers.users import get_current_admin
from services.admin_service import get_admin_service, AdminService

router = APIRouter()


@router.get("/config")
async def get_business_config(
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Get business configuration (tenant settings)"""
    tenant_id = current_admin.get("tenant_id") or current_admin.get("business_id")
    config = await service.get_business_config(tenant_id)
    return config


@router.put("/config")
async def update_business_config(
    config: dict,
    current_admin: dict = Depends(get_current_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Update business configuration (tenant settings)"""
    tenant_id = current_admin.get("tenant_id") or current_admin.get("business_id")
    updated = await service.update_business_config(tenant_id, config)
    return updated
