"""Panel registration for Nimlykoder integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PANEL_NAME, PANEL_TITLE, PANEL_ICON

_LOGGER = logging.getLogger(__name__)


async def async_register_panel(hass: HomeAssistant) -> None:
    """Register the Nimlykoder panel."""
    try:
        # Register URL for serving the panel
        frontend_path = Path(__file__).parent / "frontend" / "dist"
        
        # Register the custom panel with iframe
        hass.http.register_static_path(
            f"/api/{DOMAIN}",
            str(frontend_path),
            cache_headers=False,
        )

        # Register panel in sidebar
        hass.components.frontend.async_register_built_in_panel(
            component_name="iframe",
            sidebar_title=PANEL_TITLE,
            sidebar_icon=PANEL_ICON,
            frontend_url_path=PANEL_NAME,
            config={"url": f"/api/{DOMAIN}/index.html"},
            require_admin=False,
        )

        _LOGGER.info("Registered Nimlykoder panel")

    except Exception as err:
        _LOGGER.error("Failed to register panel: %s", err)


async def async_unregister_panel(hass: HomeAssistant) -> None:
    """Unregister the Nimlykoder panel."""
    try:
        hass.components.frontend.async_remove_panel(PANEL_NAME)
        _LOGGER.info("Unregistered Nimlykoder panel")
    except Exception as err:
        _LOGGER.error("Failed to unregister panel: %s", err)
