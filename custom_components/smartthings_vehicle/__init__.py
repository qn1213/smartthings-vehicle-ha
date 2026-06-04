from __future__ import annotations

from typing import Any

from .const import PLATFORMS


async def async_setup_entry(hass: Any, entry: Any) -> bool:
    from .coordinator import SmartThingsVehicleCoordinator

    coordinator = SmartThingsVehicleCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: Any, entry: Any) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
