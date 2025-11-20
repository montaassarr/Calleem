"""Compatibility shim for legacy imports.

The unified Vapi orchestration layer now lives inside
``backend/voice_agent/vapi_agent.py``.  This module simply re-exports the
singleton so other modules that still import from ``services.*`` continue to
work without modification.
"""

from voice_agent.vapi_agent import voice_agent_service as voice_agent

__all__ = ["voice_agent"]

