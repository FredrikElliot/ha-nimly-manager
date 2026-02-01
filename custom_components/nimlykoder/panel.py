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
        # Get the path to the frontend
        frontend_path = Path(__file__).parent / "frontend" / "dist"

        # Register the panel
        await frontend.async_register_built_in_panel(
            hass,
            component_name=DOMAIN,
            sidebar_title=PANEL_TITLE,
            sidebar_icon=PANEL_ICON,
            frontend_url_path=PANEL_NAME,
            config={"_panel_custom": {"name": PANEL_NAME}},
            require_admin=False,
        )

        _LOGGER.info("Registered Nimlykoder panel")

    except Exception as err:
        _LOGGER.error("Failed to register panel: %s", err)


async def async_unregister_panel(hass: HomeAssistant) -> None:
    """Unregister the Nimlykoder panel."""
    try:
        await frontend.async_remove_panel(hass, PANEL_NAME)
        _LOGGER.info("Unregistered Nimlykoder panel")
    except Exception as err:
        _LOGGER.error("Failed to unregister panel: %s", err)
