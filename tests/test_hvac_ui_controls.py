from pathlib import Path

import pytest

from custom_components.smartthings_vehicle.const import PLATFORMS, build_entity_id
from custom_components.smartthings_vehicle.hvac import HvacSettings

ROOT = Path(__file__).resolve().parents[1]


def test_hvac_settings_default_and_command_payload_kwargs_are_user_adjustable():
    settings = HvacSettings()

    assert settings.temperature == 22
    assert settings.ignition_duration == 10
    assert settings.defog == "off"
    assert settings.as_command_kwargs() == {
        "temperature": 22,
        "unit": "C",
        "ignition_duration": 10,
        "defog": "off",
    }

    adjusted = settings.with_temperature(24).with_ignition_duration(20).with_defog("on")

    assert adjusted.as_command_kwargs() == {
        "temperature": 24,
        "unit": "C",
        "ignition_duration": 20,
        "defog": "on",
    }


@pytest.mark.parametrize(
    ("change", "value"),
    [
        ("with_temperature", 16),
        ("with_temperature", 28),
        ("with_ignition_duration", 0),
        ("with_ignition_duration", 31),
        ("with_defog", "invalid"),
    ],
)
def test_hvac_settings_reject_unsupported_ui_values(change, value):
    with pytest.raises(ValueError):
        getattr(HvacSettings(), change)(value)


def test_home_assistant_platforms_include_hvac_number_and_select_entities():
    assert PLATFORMS == ["sensor", "button", "number", "select"]

    assert build_entity_id("number", "hvac_temperature") == (
        "number.smartthings_vehicle_hvac_temperature"
    )
    assert build_entity_id("number", "hvac_ignition_duration") == (
        "number.smartthings_vehicle_hvac_ignition_duration"
    )
    assert build_entity_id("select", "hvac_defog") == "select.smartthings_vehicle_hvac_defog"

    number_source = (ROOT / "custom_components/smartthings_vehicle/number.py").read_text(
        encoding="utf-8"
    )
    select_source = (ROOT / "custom_components/smartthings_vehicle/select.py").read_text(
        encoding="utf-8"
    )
    coordinator_source = (
        ROOT / "custom_components/smartthings_vehicle/coordinator.py"
    ).read_text(encoding="utf-8")

    assert "NumberEntity" in number_source
    assert "hvac_temperature" in number_source
    assert "hvac_ignition_duration" in number_source
    assert "SelectEntity" in select_source
    assert "hvac_defog" in select_source
    assert "self.hvac_settings.as_command_kwargs()" in coordinator_source
