"""
CallFlow AI - Multi-Tenant Voice Agent Worker

This worker connects to LiveKit Cloud and handles voice agent sessions
for multiple tenants. Each tenant gets their own isolated agent with
custom configuration (LLM, voice, system prompt, API keys).

Usage:
    Development: python main.py dev
    Production:  python main.py start

Environment Variables:
    LIVEKIT_URL          - LiveKit server URL
    LIVEKIT_API_KEY      - LiveKit API key
    LIVEKIT_API_SECRET   - LiveKit API secret
    BACKEND_URL          - Backend API URL for tenant configs
"""

import logging
from tenant_agent import server
from livekit.agents import cli

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("callflow-worker")


if __name__ == "__main__":
    logger.info("Starting CallFlow AI Multi-Tenant Agent Worker")
    
    # Run the agent server with LiveKit CLI
    cli.run_app(server)
