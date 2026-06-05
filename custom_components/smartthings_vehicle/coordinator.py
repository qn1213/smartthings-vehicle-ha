from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import replace
from datetime import timedelta
from time import time
from typing import Any, Protocol, TypeVar

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_call_later
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
    SmartThingsTokenInfo,
    SmartThingsUnauthorizedError,
    SmartThingsVehicleClient,
    VehicleStatus,
    async_wait_for_vehicle_status,
    extract_token_info,
)

_LOGGER = logging.getLogger(__name__)
_COMMAND_CONVERGENCE_TIMEOUT_SECONDS = 24
_COMMAND_CONVERGENCE_POLL_SECONDS = 2
_TOKEN_REFRESH_MARGIN_SECONDS = 600
_ON_STATES = {"on", "running", "started"}
_OFF_STATES = {"off", "stopped"}
_T = TypeVar("_T")


class _StatusPredicate(Protocol):
    def __call__(self, status: VehicleStatus) -> bool: ...


class SmartThingsVehicleCoordinator(DataUpdateCoordinator[VehicleStatus]):
    """Coordinates SmartThings vehicle status polling."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.config_entry = entry
        self.hvac_settings = HvacSettings()
        token_info = self._find_smartthings_token_info(hass)
        self.client = SmartThingsVehicleClient(
            async_get_clientsession(hass),
            token_info.access_token,
            entry.data[CONF_DEVICE_ID],
        )
        self._token_expires_at = token_info.expires_at
        self._remove_token_refresh_timer: Callable[[], None] | None = None
        super().__init__(
            hass,
            _LOGGER,
            name=entry.data.get(CONF_TITLE) or "스마트싱스 차량",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS),
        )
        self._schedule_token_refresh()

    async def _async_update_data(self) -> VehicleStatus:
        return await self._async_get_status_with_fresh_token()

    async def async_refresh_vehicle(self) -> None:
        await self._async_call_with_fresh_token(self.client.async_refresh)
        await self.async_request_refresh()

    async def async_ping_vehicle(self) -> None:
        await self._async_call_with_fresh_token(self.client.async_ping)
        await self.async_request_refresh()

    async def async_lock_vehicle(self) -> None:
        await self._async_call_with_fresh_token(self.client.async_lock)
        self._assume_status(lock_state="locked")
        await self._async_wait_for_status(
            lambda status: status.lock_state == "locked",
            "lock_state=locked",
            publish_intermediate_statuses=False,
        )

    async def async_unlock_vehicle(self) -> None:
        await self._async_call_with_fresh_token(self.client.async_unlock)
        self._assume_status(lock_state="unlocked")
        await self._async_wait_for_status(
            lambda status: status.lock_state == "unlocked",
            "lock_state=unlocked",
            publish_intermediate_statuses=False,
        )

    async def async_start_engine(self) -> None:
        await self._async_call_with_fresh_token(self.client.async_start_engine)
        await self.async_request_refresh()

    async def async_stop_engine(self) -> None:
        await self._async_call_with_fresh_token(self.client.async_stop_engine)
        await self.async_request_refresh()

    async def async_turn_hvac_on(self) -> None:
        await self._async_call_with_fresh_token(
            self.client.async_turn_hvac_on,
            **self.hvac_settings.as_command_kwargs(),
        )
        self._assume_status(hvac_state="on")
        await self._async_wait_for_status(
            lambda status: status.hvac_state in _ON_STATES,
            "hvac_state=on",
            publish_intermediate_statuses=False,
        )

    async def async_turn_hvac_off(self) -> None:
        await self._async_call_with_fresh_token(self.client.async_turn_hvac_off)
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

    async def _async_get_status_with_fresh_token(self) -> VehicleStatus:
        return await self._async_call_with_fresh_token(self.client.async_get_status)

    async def _async_call_with_fresh_token(
        self,
        callback: Callable[..., Awaitable[_T]],
        *args: Any,
        **kwargs: Any,
    ) -> _T:
        await self._async_ensure_fresh_token()
        try:
            return await callback(*args, **kwargs)
        except SmartThingsUnauthorizedError:
            _LOGGER.info(
                "SmartThings vehicle access token was rejected; refreshing official "
                "SmartThings entry and retrying once"
            )
            await self._async_ensure_fresh_token(force_reload=True)
            return await callback(*args, **kwargs)

    async def _async_ensure_fresh_token(self, *, force_reload: bool = False) -> None:
        token_info = self._find_smartthings_token_info(self.hass)
        should_reload = force_reload or self._token_expires_soon(token_info)

        if should_reload:
            await self._async_reload_smartthings_entries()
            token_info = self._find_smartthings_token_info(self.hass)

        self._apply_token_info(token_info)

    async def _async_reload_smartthings_entries(self) -> None:
        entries = list(self.hass.config_entries.async_entries(SMARTTHINGS_DOMAIN))
        if not entries:
            raise SmartThingsApiError(
                "No Home Assistant SmartThings config entry found for OAuth refresh."
            )

        for entry in entries:
            _LOGGER.debug(
                "Reloading SmartThings config entry %s before token expiry",
                entry.entry_id,
            )
            await self.hass.config_entries.async_reload(entry.entry_id)

    def _apply_token_info(self, token_info: SmartThingsTokenInfo) -> None:
        self.client.set_access_token(token_info.access_token)
        self._token_expires_at = token_info.expires_at
        self._schedule_token_refresh()

    def _token_expires_soon(self, token_info: SmartThingsTokenInfo) -> bool:
        if token_info.expires_at is None:
            return False
        return token_info.expires_at - time() <= _TOKEN_REFRESH_MARGIN_SECONDS

    def _schedule_token_refresh(self) -> None:
        if self._remove_token_refresh_timer is not None:
            self._remove_token_refresh_timer()
            self._remove_token_refresh_timer = None

        if self._token_expires_at is None:
            return

        delay = max(self._token_expires_at - time() - _TOKEN_REFRESH_MARGIN_SECONDS, 0)
        self._remove_token_refresh_timer = async_call_later(
            self.hass,
            delay,
            self._handle_scheduled_token_refresh,
        )

    def _handle_scheduled_token_refresh(self, _: Any) -> None:
        self._remove_token_refresh_timer = None
        self.hass.async_create_task(self._async_scheduled_token_refresh())

    async def _async_scheduled_token_refresh(self) -> None:
        try:
            await self._async_ensure_fresh_token(force_reload=True)
        except Exception:  # noqa: BLE001 - keep polling fallback alive after scheduled refresh errors
            _LOGGER.exception("Scheduled SmartThings vehicle token refresh failed")

    def async_shutdown(self) -> None:
        if self._remove_token_refresh_timer is not None:
            self._remove_token_refresh_timer()
            self._remove_token_refresh_timer = None

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
            self._async_get_status_with_fresh_token,
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
    def _find_smartthings_token_info(hass: HomeAssistant) -> SmartThingsTokenInfo:
        for entry in hass.config_entries.async_entries(SMARTTHINGS_DOMAIN):
            try:
                return extract_token_info(dict(entry.data))
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
