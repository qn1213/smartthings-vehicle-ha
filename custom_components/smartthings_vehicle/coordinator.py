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
from .hvac import HvacSettings
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
        self.hvac_settings = HvacSettings()
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

    async def async_ping_vehicle(self) -> None:
        await self.client.async_ping()
        await self.async_request_refresh()

    async def async_lock_vehicle(self) -> None:
        await self.client.async_lock()
        await self.async_request_refresh()

    async def async_unlock_vehicle(self) -> None:
        await self.client.async_unlock()
        await self.async_request_refresh()

    async def async_start_engine(self) -> None:
        await self.client.async_start_engine()
        await self.async_request_refresh()

    async def async_stop_engine(self) -> None:
        await self.client.async_stop_engine()
        await self.async_request_refresh()

    async def async_turn_hvac_on(self) -> None:
        await self.client.async_turn_hvac_on(**self.hvac_settings.as_command_kwargs())
        await self.async_request_refresh()

    async def async_turn_hvac_off(self) -> None:
        await self.client.async_turn_hvac_off()
        await self.async_request_refresh()

    def set_hvac_temperature(self, temperature: float | int) -> None:
        self.hvac_settings = self.hvac_settings.with_temperature(temperature)

    def set_hvac_ignition_duration(self, ignition_duration: float | int) -> None:
        self.hvac_settings = self.hvac_settings.with_ignition_duration(ignition_duration)

    def set_hvac_defog(self, defog: str) -> None:
        self.hvac_settings = self.hvac_settings.with_defog(defog)

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
