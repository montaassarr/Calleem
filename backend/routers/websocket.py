from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException, status
from services.socket_manager import socket_manager
from jose import JWTError, jwt
from utils.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])

async def get_tenant_from_token(token: str) -> str:
    """Validate JWT token and return tenant_id"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        tenant_id = payload.get("tenant_id")
        if tenant_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return str(tenant_id)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

@router.websocket("/ws/{tenant_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    tenant_id: str,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time frontend updates.
    Requires a valid JWT token in query param.
    """
    try:
        # Validate token matches requested tenant
        token_tenant = await get_tenant_from_token(token)
        
        # Simple security check: enforce token tenant matches path tenant
        # (Unless super admin, but let's keep it strict for now)
        if token_tenant != tenant_id:
             logger.warning(f"WebSocket auth failed: Token tenant {token_tenant} != Path tenant {tenant_id}")
             await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
             return

        await socket_manager.connect(websocket, tenant_id)
        
        try:
            while True:
                # Keep connection open. We mostly push data, but we can listen for pings.
                data = await websocket.receive_text()
                # Optional: Handle client messages (e.g. heartbeat)
                if data == "ping":
                    await websocket.send_text("pong")
                    
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, tenant_id)
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        # Try to close if not already closed
        try:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        except:
            pass
