from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ATTR_TEMPERATURE,
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import build_entity_id
from .coordinator import SmartThingsVehicleCoordinator
from .hvac import HVAC_TEMPERATURE_MAX, HVAC_TEMPERATURE_MIN, HVAC_TEMPERATURE_STEP


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SmartThingsVehicleCoordinator = entry.runtime_data
    async_add_entities([SmartThingsVehicleClimate(coordinator)])


class SmartThingsVehicleClimate(
    CoordinatorEntity[SmartThingsVehicleCoordinator], ClimateEntity
):
    """Climate entity for Google Assistant friendly vehicle HVAC control."""

    _attr_has_entity_name = True
    _attr_translation_key = "hvac_climate"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_precision = PRECISION_WHOLE
    _attr_target_temperature_step = HVAC_TEMPERATURE_STEP
    _attr_min_temp = HVAC_TEMPERATURE_MIN
    _attr_max_temp = HVAC_TEMPERATURE_MAX
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT_COOL]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    entity_description = ClimateEntityDescription(
        key="hvac_climate",
        translation_key="hvac_climate",
    )

    def __init__(self, coordinator: SmartThingsVehicleCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.client.device_id}_hvac_climate"
        self.entity_id = build_entity_id("climate", "hvac")
        self._attr_device_info = coordinator.device_info

    @property
    def current_temperature(self) -> float | int | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.cabin_temperature

    @property
    def target_temperature(self) -> float | int:
        return self.coordinator.hvac_settings.temperature

    @property
    def hvac_mode(self) -> HVACMode:
        if self.coordinator.is_hvac_on:
            return HVACMode.HEAT_COOL
        return HVACMode.OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            self.coordinator.set_hvac_temperature(temperature)
        if (hvac_mode := kwargs.get("hvac_mode")) is not None:
            await self.async_set_hvac_mode(hvac_mode)
        else:
            self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_turn_hvac_off()
        else:
            await self.coordinator.async_turn_hvac_on()
        self.async_write_ha_state()

    async def async_turn_on(self) -> None:
        await self.coordinator.async_turn_hvac_on()
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        await self.coordinator.async_turn_hvac_off()
        self.async_write_ha_state()
