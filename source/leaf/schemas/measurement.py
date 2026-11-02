"""Data schema representing hardware energy, power, and timing measurements."""

from dataclasses import dataclass

from leaf.schemas.enums import MeasurementProvenance
from leaf.typing import EnergyJoules, EnergyWattHours, JsonDict, PowerWatts, TimeSeconds


@dataclass
class Measurement:
    """A quantified energy, timing, or resource measurement record.

    Attributes:
        phase: Measured workflow phase ('inference', 'compilation', 'execution', 'idle').
        energy_joules: Consumed electrical energy in Joules (None if unknown).
        energy_watt_hours: Consumed electrical energy in Watt-hours (None if unknown).
        duration_seconds: Elapsed duration of the measured phase in seconds.
        provenance: Scientific classification of measurement quality (e.g. 'measured', 'unknown').
        average_power_watts: Average electrical power draw across the duration.
        peak_power_watts: Peak instantaneous electrical power draw if captured.
        cpu_time_user_seconds: Process CPU user-space execution time.
        cpu_time_system_seconds: Process CPU kernel/system execution time.
        peak_memory_mb: Peak resident set size (RSS) memory in megabytes.
        sensor_type: Name or identifier of the meter/sensor (e.g., 'NVML', 'psutil', 'RAPL').
        repetitions_count: Number of repeated executions used to compute median/dispersion.
        dispersion_relative: Dispersion metric (e.g. standard deviation / mean or IQR / median).
        uncertainty_notes: Notes explaining sensor limits, noise floor, or software attribution.
    """

    phase: str
    provenance: MeasurementProvenance | str
    duration_seconds: TimeSeconds
    energy_joules: EnergyJoules | None = None
    energy_watt_hours: EnergyWattHours | None = None
    average_power_watts: PowerWatts | None = None
    peak_power_watts: PowerWatts | None = None
    cpu_time_user_seconds: float | None = None
    cpu_time_system_seconds: float | None = None
    peak_memory_mb: float | None = None
    sensor_type: str = "unknown"
    repetitions_count: int = 1
    dispersion_relative: float | None = None
    uncertainty_notes: str | None = None

    def to_dict(self) -> JsonDict:
        """Serialize measurement to dictionary."""
        prov_str = (
            self.provenance.value
            if isinstance(self.provenance, MeasurementProvenance)
            else str(self.provenance)
        )
        return {
            "schema_version": "1.0.0",
            "phase": self.phase,
            "provenance": prov_str,
            "duration_seconds": self.duration_seconds,
            "energy_joules": self.energy_joules,
            "energy_watt_hours": self.energy_watt_hours,
            "average_power_watts": self.average_power_watts,
            "peak_power_watts": self.peak_power_watts,
            "cpu_time_user_seconds": self.cpu_time_user_seconds,
            "cpu_time_system_seconds": self.cpu_time_system_seconds,
            "peak_memory_mb": self.peak_memory_mb,
            "sensor_type": self.sensor_type,
            "repetitions_count": self.repetitions_count,
            "dispersion_relative": self.dispersion_relative,
            "uncertainty_notes": self.uncertainty_notes,
        }

    @classmethod
    def from_dict(cls, data: JsonDict) -> Measurement:
        """Instantiate measurement from dictionary."""
        prov_val = data.get("provenance", MeasurementProvenance.UNKNOWN.value)
        prov = (
            MeasurementProvenance(prov_val)
            if prov_val in MeasurementProvenance._value2member_map_
            else str(prov_val)
        )

        return cls(
            phase=str(data["phase"]),
            provenance=prov,
            duration_seconds=float(data["duration_seconds"]),
            energy_joules=float(data["energy_joules"]) if data.get("energy_joules") is not None else None,
            energy_watt_hours=float(data["energy_watt_hours"]) if data.get("energy_watt_hours") is not None else None,
            average_power_watts=float(data["average_power_watts"]) if data.get("average_power_watts") is not None else None,
            peak_power_watts=float(data["peak_power_watts"]) if data.get("peak_power_watts") is not None else None,
            cpu_time_user_seconds=float(data["cpu_time_user_seconds"]) if data.get("cpu_time_user_seconds") is not None else None,
            cpu_time_system_seconds=float(data["cpu_time_system_seconds"]) if data.get("cpu_time_system_seconds") is not None else None,
            peak_memory_mb=float(data["peak_memory_mb"]) if data.get("peak_memory_mb") is not None else None,
            sensor_type=str(data.get("sensor_type", "unknown")),
            repetitions_count=int(data.get("repetitions_count", 1)),
            dispersion_relative=float(data["dispersion_relative"]) if data.get("dispersion_relative") is not None else None,
            uncertainty_notes=data.get("uncertainty_notes"),
        )
