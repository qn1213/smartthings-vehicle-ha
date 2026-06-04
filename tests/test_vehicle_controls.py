import asyncio

import pytest

from custom_components.smartthings_vehicle.vehicle import SmartThingsVehicleClient


class FakeResponse:
    status = 200

    async def json(self):
        return {"results": [{"status": "ACCEPTED", "id": "cmd-1"}]}

    async def text(self):
        return ""


class FakeRequestContext:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeSession:
    def __init__(self):
        self.requests = []

    def request(self, method, url, **kwargs):
        self.requests.append((method, url, kwargs))
        return FakeRequestContext(FakeResponse())


def _posted_command(method_name, *args, **kwargs):
    async def run():
        session = FakeSession()
        client = SmartThingsVehicleClient(session, "token", "device-1")
        result = await getattr(client, method_name)(*args, **kwargs)

        assert result.accepted is True
        assert len(session.requests) == 1
        method, url, request_kwargs = session.requests[0]
        assert method == "POST"
        assert url.endswith("/devices/device-1/commands")
        return request_kwargs["json"]["commands"][0]

    return asyncio.run(run())


@pytest.mark.parametrize(
    ("method_name", "capability", "command"),
    [
        ("async_refresh", "refresh", "refresh"),
        ("async_ping", "healthCheck", "ping"),
        ("async_lock", "vehicleDoorState", "lock"),
        ("async_unlock", "vehicleDoorState", "unlock"),
        ("async_start_engine", "vehicleEngine", "startEngine"),
        ("async_stop_engine", "vehicleEngine", "stopEngine"),
        ("async_turn_hvac_off", "vehicleHvacRemoteSwitch", "off"),
    ],
)
def test_vehicle_control_methods_send_expected_smartthings_commands(
    method_name, capability, command
):
    posted = _posted_command(method_name)

    assert posted == {
        "component": "main",
        "capability": capability,
        "command": command,
        "arguments": [],
    }


def test_turn_hvac_on_sends_temperature_duration_and_defog_arguments():
    posted = _posted_command(
        "async_turn_hvac_on",
        temperature=23,
        unit="C",
        ignition_duration=15,
        defog="off",
    )

    assert posted == {
        "component": "main",
        "capability": "vehicleHvacRemoteSwitch",
        "command": "on",
        "arguments": [
            {
                "temperature": {"value": 23, "unit": "C"},
                "ignitionDuration": 15,
                "defog": "off",
            }
        ],
    }
