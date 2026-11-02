"""Centralized typing definitions and aliases for the LEAF benchmark.

Follows the typing conventions inspired by clean scientific Python packages,
separating Python standard types, external types, and domain-specific aliases.
"""

from pathlib import Path
from typing import Any

# --- Standard Aliases ---
type PathLike = str | Path
type JsonDict = dict[str, Any]

# --- Domain Aliases ---
type ProblemID = str
type ModelSpecID = str
type RunID = str
type AttemptID = str
type ExperimentID = str

# --- Physical Measurement Quantities ---
type EnergyJoules = float
type EnergyWattHours = float
type PowerWatts = float
type TimeSeconds = float
type MemoryMegabytes = float
