from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

HVAC_TEMPERATURE_MIN = 17
HVAC_TEMPERATURE_MAX = 27
HVAC_TEMPERATURE_STEP = 1
HVAC_IGNITION_DURATION_MIN = 1
HVAC_IGNITION_DURATION_MAX = 30
HVAC_IGNITION_DURATION_STEP = 1
HVAC_DEFOG_OPTIONS = ("off", "on")


@dataclass(frozen=True, slots=True)
class HvacSettings:
    """User-adjustable HVAC command settings exposed through Home Assistant UI."""

    temperature: float | int = 22
    unit: str = "C"
    ignition_duration: int = 10
    defog: str = "off"

    def __post_init__(self) -> None:
        self._validate_temperature(self.temperature)
        self._validate_ignition_duration(self.ignition_duration)
        self._validate_defog(self.defog)

    def with_temperature(self, temperature: float | int) -> HvacSettings:
        self._validate_temperature(temperature)
        return replace(self, temperature=temperature)

    def with_ignition_duration(self, ignition_duration: float | int) -> HvacSettings:
        duration = int(ignition_duration)
        self._validate_ignition_duration(duration)
        return replace(self, ignition_duration=duration)

    def with_defog(self, defog: str) -> HvacSettings:
        self._validate_defog(defog)
        return replace(self, defog=defog)

    def as_command_kwargs(self) -> dict[str, Any]:
        return {
            "temperature": self.temperature,
            "unit": self.unit,
            "ignition_duration": self.ignition_duration,
            "defog": self.defog,
        }

    @staticmethod
    def _validate_temperature(temperature: float | int) -> None:
        if not HVAC_TEMPERATURE_MIN <= temperature <= HVAC_TEMPERATURE_MAX:
            raise ValueError(
                f"HVAC temperature must be between "
                f"{HVAC_TEMPERATURE_MIN} and {HVAC_TEMPERATURE_MAX}"
            )

    @staticmethod
    def _validate_ignition_duration(ignition_duration: int) -> None:
        if not HVAC_IGNITION_DURATION_MIN <= ignition_duration <= HVAC_IGNITION_DURATION_MAX:
            raise ValueError(
                f"HVAC ignition duration must be between "
                f"{HVAC_IGNITION_DURATION_MIN} and {HVAC_IGNITION_DURATION_MAX}"
            )

    @staticmethod
    def _validate_defog(defog: str) -> None:
        if defog not in HVAC_DEFOG_OPTIONS:
            raise ValueError(f"HVAC defog must be one of {HVAC_DEFOG_OPTIONS!r}")
