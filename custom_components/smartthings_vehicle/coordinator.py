from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_DEVICE_ID,
    CONF_TITLE,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DOMAIN,
    SMARTTHINGS_DOMAIN,
)
from .vehicle import (
    SmartThingsApiError,
    SmartThingsVehicleClient,
    VehicleStatus,
    extract_access_token,
)

_LOGGER = logging.getLogger(__name__)


class SmartThingsVehicleCoordinator(DataUpdateCoordinator[VehicleStatus]):
    """Coordinates SmartThings vehicle status polling."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.config_entry = entry
        token = self._find_smartthings_token(hass)
        self.client = SmartThingsVehicleClient(
            async_get_clientsession(hass),
            token,
            entry.data[CONF_DEVICE_ID],
        )
        super().__init__(
            hass,
            _LOGGER,
            name=entry.data.get(CONF_TITLE) or "스마트싱스 차량",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS),
        )

    async def _async_update_data(self) -> VehicleStatus:
        return await self.client.async_get_status()

    async def async_refresh_vehicle(self) -> None:
        await self.client.async_refresh()
        await self.async_request_refresh()

    async def async_lock_vehicle(self) -> None:
        await self.client.async_lock()
        await self.async_request_refresh()

    @staticmethod
    def _find_smartthings_token(hass: HomeAssistant) -> str:
        for entry in hass.config_entries.async_entries(SMARTTHINGS_DOMAIN):
            try:
                return extract_access_token(dict(entry.data))
            except SmartThingsApiError:
                continue
        raise SmartThingsApiError(
            "No usable Home Assistant SmartThings OAuth token found. "
            "Set up the official SmartThings integration first."
        )

    @property
    def device_info(self) -> dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self.client.device_id)},
            "name": self.config_entry.data.get(CONF_TITLE) or "스마트싱스 차량",
            "manufacturer": "Hyundai Motor Group / SmartThings",
            "model": "한국 SmartThings 차량",
        }
