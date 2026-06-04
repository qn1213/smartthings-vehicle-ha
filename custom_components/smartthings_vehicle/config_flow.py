from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_DEVICE_ID, CONF_TITLE, DOMAIN, SMARTTHINGS_DOMAIN
from .vehicle import SmartThingsApiError, SmartThingsVehicleClient, extract_access_token


async def _find_smartthings_token(hass: HomeAssistant) -> str:
    for entry in hass.config_entries.async_entries(SMARTTHINGS_DOMAIN):
        try:
            return extract_access_token(dict(entry.data))
        except SmartThingsApiError:
            continue
    raise SmartThingsApiError("missing_smartthings_token")


async def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    token = await _find_smartthings_token(hass)
    client = SmartThingsVehicleClient(async_get_clientsession(hass), token, data[CONF_DEVICE_ID])
    device = await client.async_get_device()
    label = device.get("label") or data.get(CONF_TITLE) or "스마트싱스 차량"
    return {"title": str(label)}


async def _vehicle_options(hass: HomeAssistant) -> dict[str, str]:
    token = await _find_smartthings_token(hass)
    client = SmartThingsVehicleClient(async_get_clientsession(hass), token, "")
    vehicles = await client.async_list_devices()
    options: dict[str, str] = {}
    for vehicle in vehicles:
        device_id = vehicle.get(CONF_DEVICE_ID)
        if not isinstance(device_id, str) or not device_id:
            continue
        label = vehicle.get("label") or device_id
        options[device_id] = f"{label} (…{device_id[-6:]})"
    return options


def _schema(vehicle_options: dict[str, str]) -> vol.Schema:
    device_field = vol.In(vehicle_options) if vehicle_options else str
    return vol.Schema(
        {
            vol.Required(CONF_DEVICE_ID): device_field,
            vol.Optional(CONF_TITLE, default="스마트싱스 차량"): str,
        }
    )


class SmartThingsVehicleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for SmartThings Vehicle."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()
            try:
                info = await _validate_input(self.hass, user_input)
            except SmartThingsApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_TITLE) or info["title"],
                    data={
                        CONF_DEVICE_ID: user_input[CONF_DEVICE_ID],
                        CONF_TITLE: user_input.get(CONF_TITLE) or info["title"],
                    },
                )

        vehicle_options: dict[str, str] = {}
        if user_input is None:
            try:
                vehicle_options = await _vehicle_options(self.hass)
            except SmartThingsApiError:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(vehicle_options),
            errors=errors,
        )
