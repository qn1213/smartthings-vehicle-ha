from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import build_entity_id
from .coordinator import SmartThingsVehicleCoordinator


@dataclass(frozen=True, kw_only=True)
class SmartThingsVehicleButtonDescription(ButtonEntityDescription):
    press_fn: Callable[[SmartThingsVehicleCoordinator], Awaitable[None]]


BUTTONS = (
    SmartThingsVehicleButtonDescription(
        key="refresh",
        translation_key="refresh",
        press_fn=lambda coordinator: coordinator.async_refresh_vehicle(),
    ),
    SmartThingsVehicleButtonDescription(
        key="lock_vehicle",
        translation_key="lock_vehicle",
        press_fn=lambda coordinator: coordinator.async_lock_vehicle(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SmartThingsVehicleCoordinator = entry.runtime_data
    async_add_entities(
        SmartThingsVehicleButton(coordinator, description) for description in BUTTONS
    )


class SmartThingsVehicleButton(CoordinatorEntity[SmartThingsVehicleCoordinator], ButtonEntity):
    entity_description: SmartThingsVehicleButtonDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartThingsVehicleCoordinator,
        description: SmartThingsVehicleButtonDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.client.device_id}_{description.key}"
        self.entity_id = build_entity_id("button", description.key)
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        await self.entity_description.press_fn(self.coordinator)
