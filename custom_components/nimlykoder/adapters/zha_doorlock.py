"""ZHA adapter for communicating with Nimly locks over the ZCL Door Lock cluster.

Uses direct zigpy cluster calls (set_pin_code / clear_pin_code) instead of the
deprecated zha.issue_zigbee_cluster_command service, which broke in HA 2024+.
"""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

# Nimly locks expose the DoorLock cluster on endpoint 11, not endpoint 1
# (see zigpy/zha-device-handlers#3095). We try it first, then fall back
# to scanning all endpoints in case a future firmware/device differs.
DEFAULT_ENDPOINT_ID = 11


class ZhaDoorLockAdapter:
    """Adapter for communicating with a lock via ZHA's Door Lock cluster."""

    def __init__(self, hass: HomeAssistant, entity_id: str) -> None:
        self.hass = hass
        self.entity_id = entity_id

    def _get_door_lock_cluster(self):
        """Return the zigpy DoorLock cluster for this entity, or None."""
        from zigpy.zcl.clusters.closures import DoorLock

        if "zha" not in self.hass.config.components:
            _LOGGER.error("[ZhaDoorLockAdapter] ZHA integration not loaded")
            return None

        try:
            from homeassistant.components.zha.helpers import get_zha_gateway_proxy

            gateway = get_zha_gateway_proxy(self.hass)
            entity_ref = gateway.get_entity_reference(self.entity_id)
            zigpy_device = entity_ref.entity_data.device_proxy.device.device
        except Exception as err:
            _LOGGER.error(
                "[ZhaDoorLockAdapter] Could not resolve ZHA device for '%s': %s",
                self.entity_id,
                err,
            )
            return None

        candidate_ids = [DEFAULT_ENDPOINT_ID] + [
            ep_id for ep_id in zigpy_device.endpoints if ep_id != 0
        ]
        for ep_id in candidate_ids:
            ep = zigpy_device.endpoints.get(ep_id)
            if ep and DoorLock.cluster_id in ep.in_clusters:
                return ep.in_clusters[DoorLock.cluster_id]

        _LOGGER.error(
            "[ZhaDoorLockAdapter] No DoorLock cluster found on '%s'", self.entity_id
        )
        return None

    async def add_code(self, slot: int, pin_code: str, user_type: str = "unrestricted") -> None:
        """Set a PIN code on the lock via the ZCL set_pin_code command."""
        from zigpy.zcl.clusters.closures import DoorLock

        cluster = self._get_door_lock_cluster()
        if cluster is None:
            raise HomeAssistantError(
                "ZHA DoorLock cluster not available — check that ZHA is running and the lock is paired."
            )
        try:
            await cluster.set_pin_code(
                slot,
                DoorLock.UserStatus.Enabled,
                DoorLock.UserType.Unrestricted,
                pin_code,
            )
        except Exception as err:
            raise HomeAssistantError(f"Failed to set PIN via ZHA: {err}") from err

    async def remove_code(self, slot: int) -> None:
        """Clear a PIN code from the lock via the ZCL clear_pin_code command."""
        cluster = self._get_door_lock_cluster()
        if cluster is None:
            raise HomeAssistantError(
                "ZHA DoorLock cluster not available — check that ZHA is running and the lock is paired."
            )
        try:
            await cluster.clear_pin_code(slot)
        except Exception as err:
            raise HomeAssistantError(f"Failed to clear PIN via ZHA: {err}") from err

    async def verify_connection(self) -> bool:
        """Return True if the DoorLock cluster is reachable via ZHA."""
        return self._get_door_lock_cluster() is not None
