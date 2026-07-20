import pytest

from custom_components.smartthings_vehicle.vehicle import (
    SmartThingsApiError,
    VehicleCommandResult,
    VehicleCommandStatus,
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
    assert status.ev_battery_level is None
    assert status.supports_attribute("vehicleBattery", "batteryLevel") is False


def test_parse_2025_ioniq5_electric_vehicle_status():
    payload = {
        "components": {
            "main": {
                "vehicleRange": {
                    "estimatedRemainingRange": {"value": 386, "unit": "km"}
                },
                "vehicleBattery": {
                    "batteryLevel": {"value": 72, "unit": "%"},
                    "chargingState": {"value": "charging"},
                    "chargingPlug": {"value": "connected"},
                    "chargingRemainTime": {"value": 95, "unit": "mins"},
                    "chargingDetail": {"value": "fastCharging"},
                },
                "vehicleWarning": {
                    "auxiliaryBattery": {"value": "normal"},
                    "electricVehicleBattery": {"value": "normal"},
                },
            }
        }
    }

    status = parse_vehicle_status(payload)

    assert status.range_km == 386
    assert status.ev_battery_level == 72
    assert status.charging_state == "charging"
    assert status.charging_plug == "connected"
    assert status.charging_remaining_time == 95
    assert status.charging_detail == "fastCharging"
    assert status.auxiliary_battery_warning == "normal"
    assert status.electric_vehicle_battery_warning == "normal"
    assert "vehicleBattery" in status.available_capabilities
    assert status.supports_attribute("vehicleBattery", "batteryLevel") is True
    assert status.supports_attribute("vehicleBattery", "chargingRemainTime") is True
    assert status.supports_attribute("vehicleBattery", "chargingDetail") is True
    assert status.supports_attribute("vehicleFuelLevel", "fuelLevel") is False


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


def test_vehicle_command_status_tracks_pending_response_and_terminal_states():
    status = VehicleCommandStatus.idle().mark_pending(
        command="lock",
        target="lock_state=locked",
        started_at=100.0,
    )

    assert status.state == "pending"
    assert status.as_attributes() == {
        "last_command": "lock",
        "target": "lock_state=locked",
        "command_id": None,
        "started_at": 100.0,
        "completed_at": None,
        "last_error": None,
    }

    accepted = status.mark_accepted("cmd-1")
    assert accepted.state == "accepted"
    assert accepted.command_id == "cmd-1"
    assert accepted.completed_at is None

    converged = accepted.mark_converged(completed_at=104.0)
    assert converged.state == "converged"
    assert converged.completed_at == 104.0

    timed_out = accepted.mark_timeout("status did not converge", completed_at=124.0)
    assert timed_out.state == "timeout"
    assert timed_out.last_error == "status did not converge"

    failed = status.mark_failed("SmartThings HTTP 500", completed_at=101.0)
    assert failed.state == "failed"
    assert failed.last_error == "SmartThings HTTP 500"
