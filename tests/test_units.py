"""Unit tests for physical unit conversions and invariants."""


from leaf.core.units import (
    joules_to_watt_hours,
    power_and_time_to_joules,
    watt_hours_to_joules,
)


def test_joules_to_watt_hours_conversion():
    """Verify that 3600 Joules equals 1.0 Watt-hour."""
    assert joules_to_watt_hours(3600.0) == 1.0
    assert joules_to_watt_hours(0.0) == 0.0
    assert joules_to_watt_hours(1800.0) == 0.5


def test_watt_hours_to_joules_conversion():
    """Verify roundtrip conversion between Watt-hours and Joules."""
    assert watt_hours_to_joules(1.0) == 3600.0
    assert watt_hours_to_joules(0.25) == 900.0


def test_power_and_time_to_joules():
    """Verify E (Joules) = P (Watts) * t (seconds)."""
    # 50 Watts over 2 seconds = 100 Joules
    assert power_and_time_to_joules(50.0, 2.0) == 100.0
    # 15.5 Watts over 0.5 seconds = 7.75 Joules
    assert power_and_time_to_joules(15.5, 0.5) == 7.75
