"""Access control helpers for Nimlykoder."""
from __future__ import annotations

from functools import wraps
from typing import Any, Awaitable, Callable

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_ALLOWED_USERS, DOMAIN


def is_user_allowed(hass: HomeAssistant, user: Any) -> bool:
    """Return whether a user is an administrator or allowed to manage codes."""
    if user.is_admin:
        return True

    data = hass.data.get(DOMAIN)
    entry = data.get("entry") if data else None
    return bool(entry and user.id in entry.options.get(CONF_ALLOWED_USERS, []))


def require_websocket_access(
    handler: Callable[..., Awaitable[None]],
) -> Callable[..., Awaitable[None]]:
    """Restrict a websocket command to admins and configured users."""

    @wraps(handler)
    async def wrapped(
        hass: HomeAssistant, connection: Any, msg: dict[str, Any]
    ) -> None:
        if not is_user_allowed(hass, connection.user):
            connection.send_error(
                msg["id"], "unauthorized", "You are not allowed to use Nimlykoder"
            )
            return
        await handler(hass, connection, msg)

    return wrapped


def require_service_access(
    hass: HomeAssistant, handler: Callable[..., Awaitable[Any]]
) -> Callable[..., Awaitable[Any]]:
    """Restrict user-initiated services to admins and configured users."""

    @wraps(handler)
    async def wrapped(call: Any) -> Any:
        if call.context.user_id is not None:
            user = await hass.auth.async_get_user(call.context.user_id)
            if user is None or not is_user_allowed(hass, user):
                raise HomeAssistantError("You are not allowed to use Nimlykoder")
        return await handler(call)

    return wrapped
