import asyncio

from custom_components.smartthings_vehicle.vehicle import (
    VehicleStatus,
    async_wait_for_vehicle_status,
)


class FakeStatusSource:
    def __init__(self, statuses):
        self.statuses = list(statuses)
        self.calls = 0

    async def async_get_status(self):
        self.calls += 1
        if len(self.statuses) > 1:
            return self.statuses.pop(0)
        return self.statuses[0]


def test_status_wait_polls_until_target_status_converges():
    async def run():
        source = FakeStatusSource(
            [
                VehicleStatus(lock_state="locked"),
                VehicleStatus(lock_state="locked"),
                VehicleStatus(lock_state="unlocked"),
            ]
        )
        updates = []

        result = await async_wait_for_vehicle_status(
            source.async_get_status,
            lambda status: status.lock_state == "unlocked",
            updates.append,
            timeout_seconds=1,
            poll_seconds=0,
        )

        assert result.converged is True
        assert source.calls == 3
        assert updates[-1].lock_state == "unlocked"

    asyncio.run(run())


def test_status_wait_uses_latest_status_before_convergence():
    async def run():
        source = FakeStatusSource(
            [
                VehicleStatus(hvac_state="off"),
                VehicleStatus(hvac_state="on"),
            ]
        )
        updates = []

        result = await async_wait_for_vehicle_status(
            source.async_get_status,
            lambda status: status.hvac_state in {"on", "running", "started"},
            updates.append,
            timeout_seconds=1,
            poll_seconds=0,
        )

        assert result.converged is True
        assert [status.hvac_state for status in updates] == ["off", "on"]

    asyncio.run(run())


def test_status_wait_timeout_keeps_latest_status_without_raising():
    async def run():
        source = FakeStatusSource([VehicleStatus(lock_state="locked")])
        updates = []

        result = await async_wait_for_vehicle_status(
            source.async_get_status,
            lambda status: status.lock_state == "unlocked",
            updates.append,
            timeout_seconds=0,
            poll_seconds=0,
        )

        assert result.converged is False
        assert result.last_error is None
        assert updates[-1].lock_state == "locked"

    asyncio.run(run())
