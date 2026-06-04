from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.lock import LockEntity, LockEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import build_entity_id
from .coordinator import SmartThingsVehicleCoordinator


@dataclass(frozen=True, kw_only=True)
class SmartThingsVehicleLockDescription(LockEntityDescription):
    """Describes a SmartThings vehicle lock entity."""


LOCKS: tuple[SmartThingsVehicleLockDescription, ...] = (
    SmartThingsVehicleLockDescription(
        key="door_lock",
        translation_key="door_lock",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SmartThingsVehicleCoordinator = entry.runtime_data
    async_add_entities(
        SmartThingsVehicleLock(coordinator, description) for description in LOCKS
    )


class SmartThingsVehicleLock(CoordinatorEntity[SmartThingsVehicleCoordinator], LockEntity):
    entity_description: SmartThingsVehicleLockDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartThingsVehicleCoordinator,
        description: SmartThingsVehicleLockDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.client.device_id}_{description.key}"
        self.entity_id = build_entity_id("lock", description.key)
        self._attr_device_info = coordinator.device_info

    @property
    def is_locked(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        lock_state = self.coordinator.data.lock_state
        if lock_state == "locked":
            return True
        if lock_state == "unlocked":
            return False
        return None

    async def async_lock(self, **kwargs: Any) -> None:
        await self.coordinator.async_lock_vehicle()

    async def async_unlock(self, **kwargs: Any) -> None:
        await self.coordinator.async_unlock_vehicle()
