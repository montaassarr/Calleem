"""Legacy Vapi service placeholder kept for backward compatibility."""

from typing import Any


class VapiRemovedError(RuntimeError):
    """Raised when deprecated Vapi helpers are accidentally invoked."""

    def __init__(self, feature: str) -> None:
        super().__init__(
            "Vapi integration has been permanently removed as part of the LiveKit migration. "
            f"Feature '{feature}' is no longer available."
        )


def _raise(feature: str) -> None:
    raise VapiRemovedError(feature)


async def create_vapi_assistant(*_: Any, **__: Any) -> str:  # pragma: no cover - deprecated
    _raise("create_vapi_assistant")


async def update_vapi_assistant(*_: Any, **__: Any) -> None:  # pragma: no cover - deprecated
    _raise("update_vapi_assistant")


async def delete_vapi_assistant(*_: Any, **__: Any) -> None:  # pragma: no cover - deprecated
    _raise("delete_vapi_assistant")
