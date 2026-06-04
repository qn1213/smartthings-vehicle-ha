from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import build_entity_id
from .coordinator import SmartThingsVehicleCoordinator
from .hvac import HVAC_DEFOG_OPTIONS


@dataclass(frozen=True, kw_only=True)
class SmartThingsVehicleSelectDescription(SelectEntityDescription):
    pass


SELECTS: tuple[SmartThingsVehicleSelectDescription, ...] = (
    SmartThingsVehicleSelectDescription(
        key="hvac_defog",
        translation_key="hvac_defog",
        options=list(HVAC_DEFOG_OPTIONS),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SmartThingsVehicleCoordinator = entry.runtime_data
    async_add_entities(
        SmartThingsVehicleSelect(coordinator, description) for description in SELECTS
    )


class SmartThingsVehicleSelect(CoordinatorEntity[SmartThingsVehicleCoordinator], SelectEntity):
    entity_description: SmartThingsVehicleSelectDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartThingsVehicleCoordinator,
        description: SmartThingsVehicleSelectDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.client.device_id}_{description.key}"
        self.entity_id = build_entity_id("select", description.key)
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str:
        return self.coordinator.hvac_settings.defog

    async def async_select_option(self, option: str) -> None:
        self.coordinator.set_hvac_defog(option)
        self.async_write_ha_state()
