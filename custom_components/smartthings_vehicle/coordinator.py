from __future__ import annotations

import logging
from dataclasses import replace
from datetime import timedelta
from typing import Any, Protocol

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
    async_wait_for_vehicle_status,
    extract_access_token,
)

_LOGGER = logging.getLogger(__name__)
_COMMAND_CONVERGENCE_TIMEOUT_SECONDS = 24
_COMMAND_CONVERGENCE_POLL_SECONDS = 2
_ON_STATES = {"on", "running", "started"}
_OFF_STATES = {"off", "stopped"}


class _StatusPredicate(Protocol):
    def __call__(self, status: VehicleStatus) -> bool: ...


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
        self._assume_status(lock_state="locked")
        await self._async_wait_for_status(
            lambda status: status.lock_state == "locked",
            "lock_state=locked",
            publish_intermediate_statuses=False,
        )

    async def async_unlock_vehicle(self) -> None:
        await self.client.async_unlock()
        self._assume_status(lock_state="unlocked")
        await self._async_wait_for_status(
            lambda status: status.lock_state == "unlocked",
            "lock_state=unlocked",
            publish_intermediate_statuses=False,
        )

    async def async_start_engine(self) -> None:
        await self.client.async_start_engine()
        await self.async_request_refresh()

    async def async_stop_engine(self) -> None:
        await self.client.async_stop_engine()
        await self.async_request_refresh()

    async def async_turn_hvac_on(self) -> None:
        await self.client.async_turn_hvac_on(**self.hvac_settings.as_command_kwargs())
        self._assume_status(hvac_state="on")
        await self._async_wait_for_status(
            lambda status: status.hvac_state in _ON_STATES,
            "hvac_state=on",
            publish_intermediate_statuses=False,
        )

    async def async_turn_hvac_off(self) -> None:
        await self.client.async_turn_hvac_off()
        self._assume_status(hvac_state="off")
        await self._async_wait_for_status(
            lambda status: status.hvac_state in _OFF_STATES,
            "hvac_state=off",
            publish_intermediate_statuses=False,
        )

    @property
    def is_hvac_on(self) -> bool:
        if self.data is None:
            return False
        return self.data.hvac_state in _ON_STATES

    async def async_set_hvac_defog_on(self) -> None:
        self.set_hvac_defog("on")

    async def async_set_hvac_defog_off(self) -> None:
        self.set_hvac_defog("off")

    async def _async_wait_for_status(
        self,
        predicate: _StatusPredicate,
        target_description: str,
        *,
        timeout_seconds: int = _COMMAND_CONVERGENCE_TIMEOUT_SECONDS,
        poll_seconds: int = _COMMAND_CONVERGENCE_POLL_SECONDS,
        publish_intermediate_statuses: bool = True,
    ) -> None:
        """Poll SmartThings status until an accepted vehicle command settles."""

        def update_status(status: VehicleStatus) -> None:
            if publish_intermediate_statuses or predicate(status):
                self.async_set_updated_data(status)

        result = await async_wait_for_vehicle_status(
            self.client.async_get_status,
            predicate,
            update_status,
            timeout_seconds=timeout_seconds,
            poll_seconds=poll_seconds,
        )
        if result.converged:
            return

        _LOGGER.warning(
            "SmartThings vehicle command was accepted but status did not converge to %s "
            "within %ss%s",
            target_description,
            timeout_seconds,
            f"; last status error: {result.last_error}" if result.last_error else "",
        )

    def _assume_status(self, **updates: str) -> None:
        """Immediately publish a command target state, then reconcile by polling."""

        self.async_set_updated_data(replace(self.data or VehicleStatus(), **updates))

    def set_hvac_temperature(self, temperature: float | int) -> None:
        self.hvac_settings = self.hvac_settings.with_temperature(temperature)
        self.async_update_listeners()

    def set_hvac_ignition_duration(self, ignition_duration: float | int) -> None:
        self.hvac_settings = self.hvac_settings.with_ignition_duration(ignition_duration)
        self.async_update_listeners()

    def set_hvac_defog(self, defog: str) -> None:
        self.hvac_settings = self.hvac_settings.with_defog(defog)
        self.async_update_listeners()

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
