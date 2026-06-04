from pathlib import Path

from custom_components.smartthings_vehicle.const import build_entity_id

ROOT = Path(__file__).resolve().parents[1]


def test_vehicle_entity_ids_are_generic_and_do_not_include_vehicle_name():
    assert build_entity_id("sensor", "range_km") == "sensor.smartthings_vehicle_range_km"
    assert build_entity_id("sensor", "lock_state") == "sensor.smartthings_vehicle_lock_state"
    assert build_entity_id("button", "lock_vehicle") == "button.smartthings_vehicle_lock_vehicle"

    for vehicle_name in ("쏘나타", "아이오닉", "ev6", "genesis"):
        assert vehicle_name not in build_entity_id("sensor", "range_km").lower()


def test_entities_set_generic_entity_id_before_home_assistant_registers_them():
    sensor_source = (ROOT / "custom_components/smartthings_vehicle/sensor.py").read_text(
        encoding="utf-8"
    )
    button_source = (ROOT / "custom_components/smartthings_vehicle/button.py").read_text(
        encoding="utf-8"
    )

    assert 'self.entity_id = build_entity_id("sensor", description.key)' in sensor_source
    assert 'self.entity_id = build_entity_id("button", description.key)' in button_source
    assert "_attr_entity_id" not in sensor_source
    assert "_attr_entity_id" not in button_source
