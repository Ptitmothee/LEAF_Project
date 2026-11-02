"""Physical unit conversion utilities and invariants for energy and power."""

from leaf.typing import EnergyJoules, EnergyWattHours, PowerWatts, TimeSeconds


def joules_to_watt_hours(joules: EnergyJoules) -> EnergyWattHours:
    """Convert energy from Joules (J) to Watt-hours (Wh).

    1 Watt-hour = 3600 Joules.

    Args:
        joules: Energy in Joules.

    Returns:
        Energy in Watt-hours.
    """
    return joules / 3600.0


def watt_hours_to_joules(wh: EnergyWattHours) -> EnergyJoules:
    """Convert energy from Watt-hours (Wh) to Joules (J).

    1 Watt-hour = 3600 Joules.

    Args:
        wh: Energy in Watt-hours.

    Returns:
        Energy in Joules.
    """
    return wh * 3600.0


def power_and_time_to_joules(power_watts: PowerWatts, duration_seconds: TimeSeconds) -> EnergyJoules:
    """Compute energy in Joules from average power in Watts and duration in seconds.

    E (Joules) = P (Watts) * t (seconds).

    Args:
        power_watts: Average electrical power draw in Watts.
        duration_seconds: Elapsed duration in seconds.

    Returns:
        Energy consumed in Joules.
    """
    return power_watts * duration_seconds

