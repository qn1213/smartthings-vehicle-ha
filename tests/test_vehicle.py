import pytest

from custom_components.smartthings_vehicle.vehicle import (
    SmartThingsApiError,
    VehicleCommandResult,
    VehicleStatus,
    extract_access_token,
    parse_command_result,
    parse_vehicle_status,
)


def test_extract_access_token_supports_home_assistant_smartthings_oauth_shapes():
    assert extract_access_token({"access_token": "direct-token"}) == "direct-token"
    assert extract_access_token({"token": {"access_token": "nested-token"}}) == "nested-token"
    assert extract_access_token({"auth": {"accessToken": "camel-token"}}) == "camel-token"


def test_extract_access_token_rejects_missing_token():
    with pytest.raises(SmartThingsApiError):
        extract_access_token({"not_token": "nope"})


def test_parse_vehicle_status_maps_smartthings_status_payload():
    payload = {
        "components": {
            "main": {
                "vehicleRange": {"estimatedRemainingRange": {"value": 412, "unit": "km"}},
                "vehicleOdometer": {"odometerReading": {"value": 12345.6, "unit": "km"}},
                "vehicleEngine": {"engineState": {"value": "off"}},
                "vehicleHvac": {
                    "hvacState": {"value": "off"},
                    "temperature": {"value": 22, "unit": "C"},
                },
                "vehicleDoorState": {
                    "lockState": {"value": "locked"},
                    "frontLeftDoor": {"value": "locked"},
                    "frontRightDoor": {"value": "locked"},
                    "rearLeftDoor": {"value": "locked"},
                    "rearRightDoor": {"value": "locked"},
                },
                "vehicleWindowState": {
                    "frontLeftWindow": {"value": "closed"},
                    "frontRightWindow": {"value": "closed"},
                    "rearLeftWindow": {"value": "closed"},
                    "rearRightWindow": {"value": "closed"},
                },
                "vehicleWarning": {
                    "fuel": {"value": "normal"},
                    "smartKeyBattery": {"value": "normal"},
                },
                "healthCheck": {"DeviceWatch-DeviceStatus": {"value": "online"}},
            }
        }
    }

    status = parse_vehicle_status(payload)

    assert status == VehicleStatus(
        range_km=412,
        odometer_km=12345.6,
        engine_state="off",
        hvac_state="off",
        cabin_temperature=22,
        cabin_temperature_unit="C",
        lock_state="locked",
        front_left_door="locked",
        front_right_door="locked",
        rear_left_door="locked",
        rear_right_door="locked",
        front_left_window="closed",
        front_right_window="closed",
        rear_left_window="closed",
        rear_right_window="closed",
        fuel_warning="normal",
        smart_key_battery="normal",
        health="online",
    )


def test_parse_vehicle_status_tolerates_missing_capabilities():
    status = parse_vehicle_status({"components": {"main": {}}})

    assert status.lock_state is None
    assert status.engine_state is None
    assert status.range_km is None


def test_parse_command_result_requires_accepted_status():
    payload = {"results": [{"id": "abc", "status": "ACCEPTED"}]}

    assert parse_command_result(payload) == VehicleCommandResult(
        accepted=True,
        command_id="abc",
        raw=payload,
    )


def test_parse_command_result_rejects_failed_status():
    with pytest.raises(SmartThingsApiError):
        parse_command_result({"results": [{"id": "abc", "status": "FAILED"}]})
