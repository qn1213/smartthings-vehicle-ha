from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import build_entity_id
from .coordinator import SmartThingsVehicleCoordinator
from .vehicle import VehicleStatus


@dataclass(frozen=True, kw_only=True)
class SmartThingsVehicleSensorDescription(SensorEntityDescription):
    value_fn: Callable[[VehicleStatus], Any]


SENSORS: tuple[SmartThingsVehicleSensorDescription, ...] = (
    SmartThingsVehicleSensorDescription(
        key="range_km",
        translation_key="range_km",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda status: status.range_km,
    ),
    SmartThingsVehicleSensorDescription(
        key="odometer_km",
        translation_key="odometer_km",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda status: status.odometer_km,
    ),
    SmartThingsVehicleSensorDescription(
        key="engine_state",
        translation_key="engine_state",
        value_fn=lambda status: status.engine_state,
    ),
    SmartThingsVehicleSensorDescription(
        key="hvac_state",
        translation_key="hvac_state",
        value_fn=lambda status: status.hvac_state,
    ),
    SmartThingsVehicleSensorDescription(
        key="cabin_temperature",
        translation_key="cabin_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda status: status.cabin_temperature,
    ),
    SmartThingsVehicleSensorDescription(
        key="lock_state",
        translation_key="lock_state",
        value_fn=lambda status: status.lock_state,
    ),
    SmartThingsVehicleSensorDescription(
        key="front_left_door",
        translation_key="front_left_door",
        value_fn=lambda status: status.front_left_door,
    ),
    SmartThingsVehicleSensorDescription(
        key="front_right_door",
        translation_key="front_right_door",
        value_fn=lambda status: status.front_right_door,
    ),
    SmartThingsVehicleSensorDescription(
        key="rear_left_door",
        translation_key="rear_left_door",
        value_fn=lambda status: status.rear_left_door,
    ),
    SmartThingsVehicleSensorDescription(
        key="rear_right_door",
        translation_key="rear_right_door",
        value_fn=lambda status: status.rear_right_door,
    ),
    SmartThingsVehicleSensorDescription(
        key="front_left_window",
        translation_key="front_left_window",
        value_fn=lambda status: status.front_left_window,
    ),
    SmartThingsVehicleSensorDescription(
        key="front_right_window",
        translation_key="front_right_window",
        value_fn=lambda status: status.front_right_window,
    ),
    SmartThingsVehicleSensorDescription(
        key="rear_left_window",
        translation_key="rear_left_window",
        value_fn=lambda status: status.rear_left_window,
    ),
    SmartThingsVehicleSensorDescription(
        key="rear_right_window",
        translation_key="rear_right_window",
        value_fn=lambda status: status.rear_right_window,
    ),
    SmartThingsVehicleSensorDescription(
        key="fuel_warning",
        translation_key="fuel_warning",
        value_fn=lambda status: status.fuel_warning,
    ),
    SmartThingsVehicleSensorDescription(
        key="smart_key_battery",
        translation_key="smart_key_battery",
        value_fn=lambda status: status.smart_key_battery,
    ),
    SmartThingsVehicleSensorDescription(
        key="health",
        translation_key="health",
        value_fn=lambda status: status.health,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SmartThingsVehicleCoordinator = entry.runtime_data
    async_add_entities(
        SmartThingsVehicleSensor(coordinator, description) for description in SENSORS
    )


class SmartThingsVehicleSensor(CoordinatorEntity[SmartThingsVehicleCoordinator], SensorEntity):
    entity_description: SmartThingsVehicleSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartThingsVehicleCoordinator,
        description: SmartThingsVehicleSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.client.device_id}_{description.key}"
        self.entity_id = build_entity_id("sensor", description.key)
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
