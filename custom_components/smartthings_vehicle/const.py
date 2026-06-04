from __future__ import annotations

DOMAIN = "smartthings_vehicle"
SMARTTHINGS_DOMAIN = "smartthings"
CONF_DEVICE_ID = "device_id"
CONF_TITLE = "title"
DEFAULT_SCAN_INTERVAL_SECONDS = 300
PLATFORMS = ["sensor", "button"]


def build_entity_id(platform: str, key: str) -> str:
    """Build a generic Home Assistant entity ID for a vehicle entity.

    Keep object IDs independent from the user-visible vehicle name so the same
    integration can support multiple Hyundai/Kia/Genesis vehicles consistently.
    Home Assistant will append a numeric suffix when another vehicle exposes the
    same generic entity ID.
    """

    return f"{platform}.{DOMAIN}_{key}"
