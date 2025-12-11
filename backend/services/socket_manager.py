from typing import Dict, List, Any
from fastapi import WebSocket
import logging
import asyncio

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections, grouped by tenant_id.
    """
    def __init__(self):
        # tenant_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: str):
        """Accept connection and store it."""
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = []
        self.active_connections[tenant_id].append(websocket)
        logger.info(f"WebSocket connected for tenant {tenant_id}. Total connections: {len(self.active_connections[tenant_id])}")

    def disconnect(self, websocket: WebSocket, tenant_id: str):
        """Remove connection."""
        if tenant_id in self.active_connections:
            if websocket in self.active_connections[tenant_id]:
                self.active_connections[tenant_id].remove(websocket)
                if not self.active_connections[tenant_id]:
                    del self.active_connections[tenant_id]
                logger.info(f"WebSocket disconnected for tenant {tenant_id}")

    async def broadcast_to_tenant(self, tenant_id: str, message: dict):
        """Send JSON message to all connected clients for a tenant."""
        if tenant_id in self.active_connections:
            to_remove = []
            for connection in self.active_connections[tenant_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send to websocket: {e}")
                    to_remove.append(connection)
            
            # Clean up dead connections
            for dead in to_remove:
                self.disconnect(dead, tenant_id)

socket_manager = ConnectionManager()
