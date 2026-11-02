"""Configuration loading, typing, and validation for LEAF.

This module provides strongly typed dataclass structures representing LEAF benchmark
configurations, alongside parser and validation utilities for YAML configuration files.

Typical usage:
    ```python
    from leaf.core.config import load_config

    config = load_config("config/default_config.yaml")
    print(config.experiment.name)
    ```
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from leaf.core.exceptions import ConfigError


@dataclass
class ExperimentConfig:
    """Experiment metadata, modes, and reproducibility parameters.

    Attributes:
        name: Unique identifier for the experimental campaign.
        description: Human-readable summary of the experiment's intent.
        repetitions: Number of times each execution measurement is repeated
            to compute dispersion and median metrics (minimum 1, recommended >= 3).
        seed: Random seed used to ensure deterministic sampling across runs.
        dry_run: When True, validates orchestration workflows without running
            heavy workloads or calling chargeable APIs.
        allow_cloud_calls: Explicit safety gate required to permit external API calls.
    """

    name: str = "default_experiment"
    description: str = "Default LEAF benchmark configuration"
    repetitions: int = 1
    seed: int | None = 42
    dry_run: bool = False
    allow_cloud_calls: bool = False


@dataclass
class PathsConfig:
    """Configured filesystem storage directories for benchmark artifacts.

    Attributes:
        data_dir: Root directory for input datasets, problem statements, and reference tests.
        results_dir: Output directory for experimental telemetry, logs, and exported charts.
        artifacts_dir: Scratch space for intermediate compilation files and binaries.
    """

    data_dir: Path = Path("data")
    results_dir: Path = Path("results")
    artifacts_dir: Path = Path("artifacts")


@dataclass
class BudgetsConfig:
    """Resource, iteration, and monetary budgets enforced during generation and execution.

    Attributes:
        max_attempts_per_problem: Maximum generation and correction attempts per strategy.
        max_tokens_per_attempt: Output token generation ceiling per model call.
        timeout_compilation_seconds: Maximum wall-clock time permitted for compiling C++/Java.
        timeout_execution_seconds: Maximum wall-clock execution time per test before TLE.
        max_cost_usd_per_run: Maximum allowed financial expenditure ceiling across the run.
    """

    max_attempts_per_problem: int = 3
    max_tokens_per_attempt: int = 2048
    timeout_compilation_seconds: float = 30.0
    timeout_execution_seconds: float = 10.0
    max_cost_usd_per_run: float = 0.0


@dataclass
class SandboxConfig:
    """Containment modes and resource limits for executing untrusted code.

    Attributes:
        mode: Isolation mechanism ('process' for local isolation, 'container' for Docker/VM).
        memory_limit_mb: Maximum resident memory allowed for the executed process (>= 32 MB).
        cpu_limit_seconds: Maximum CPU execution time permitted.
        allow_network: Whether network access is permitted during execution (default False).
        max_output_bytes: Buffer limit for stdout/stderr to prevent memory exhaustion (default 64 KB).
    """

    mode: str = "process"  # "process" or "container"
    memory_limit_mb: int = 512
    cpu_limit_seconds: float = 5.0
    allow_network: bool = False
    max_output_bytes: int = 65536


@dataclass
class MeasurementConfig:
    """Telemetry sampling, calibration, and power monitoring settings.

    Attributes:
        sampling_interval_ms: Interval between consecutive power/resource samples in milliseconds.
        idle_calibration_seconds: Duration used to establish baseline idle power before runs.
        record_cpu: Whether to sample host process CPU user/system times and memory.
        record_gpu: Whether to query GPU telemetry (e.g., NVML power draw) when available.
    """

    sampling_interval_ms: int = 50
    idle_calibration_seconds: float = 2.0
    record_cpu: bool = True
    record_gpu: bool = True


@dataclass
class LeafConfig:
    """Root configuration container combining all benchmark configuration sections.

    Attributes:
        experiment: Metadata, modes, and reproducibility configuration.
        paths: Directory storage paths.
        budgets: Resource, iteration, and monetary budgets.
        sandbox: Execution containment settings.
        measurement: Telemetry and power meter sampling settings.
        supported_languages: List of programming languages enabled for evaluation.
    """

    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    budgets: BudgetsConfig = field(default_factory=BudgetsConfig)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    measurement: MeasurementConfig = field(default_factory=MeasurementConfig)
    supported_languages: list[str] = field(
        default_factory=lambda: ["python", "cpp", "java"]
    )


def validate_config_dict(data: dict[str, Any]) -> list[str]:
    """Validate a loaded configuration dictionary against required bounds and types.

    Args:
        data: Raw dictionary typically parsed from a YAML configuration file.

    Returns:
        List of human-readable error descriptions. An empty list denotes a valid dictionary.
    """
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["Configuration root must be a YAML dictionary/mapping."]

    exp = data.get("experiment", {})
    if not isinstance(exp, dict):
        errors.append("Section 'experiment' must be a dictionary.")
    else:
        reps = exp.get("repetitions", 1)
        if not isinstance(reps, int) or reps < 1:
            errors.append("'experiment.repetitions' must be a positive integer.")

    budgets = data.get("budgets", {})
    if not isinstance(budgets, dict):
        errors.append("Section 'budgets' must be a dictionary.")
    else:
        for time_key in ("timeout_compilation_seconds", "timeout_execution_seconds"):
            val = budgets.get(time_key, 10.0)
            if not isinstance(val, (int, float)) or val <= 0:
                errors.append(f"'budgets.{time_key}' must be a positive number.")

    sandbox = data.get("sandbox", {})
    if not isinstance(sandbox, dict):
        errors.append("Section 'sandbox' must be a dictionary.")
    else:
        mode = sandbox.get("mode", "process")
        if mode not in ("process", "container"):
            errors.append(f"'sandbox.mode' must be 'process' or 'container', got '{mode}'.")
        mem = sandbox.get("memory_limit_mb", 512)
        if not isinstance(mem, int) or mem < 32:
            errors.append("'sandbox.memory_limit_mb' must be an integer >= 32.")

    measurement = data.get("measurement", {})
    if not isinstance(measurement, dict):
        errors.append("Section 'measurement' must be a dictionary.")
    else:
        interval = measurement.get("sampling_interval_ms", 50)
        if not isinstance(interval, int) or interval < 5:
            errors.append("'measurement.sampling_interval_ms' must be an integer >= 5.")

    languages = data.get("supported_languages", ["python", "cpp", "java"])
    if not isinstance(languages, list) or not languages:
        errors.append("'supported_languages' must be a non-empty list of languages.")

    return errors


def load_config(path: str | Path) -> LeafConfig:
    """Load, validate, and construct a LeafConfig instance from a YAML file.

    Args:
        path: Filesystem path to the YAML configuration file.

    Returns:
        Fully populated and validated LeafConfig instance.

    Raises:
        ConfigError: If the file does not exist, contains invalid YAML syntax,
            or fails schema validation checks.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f) or {}
    except (yaml.YAMLError, OSError) as e:
        raise ConfigError(f"Failed to parse YAML configuration '{config_path}': {e}") from e

    errors = validate_config_dict(raw_data)
    if errors:
        raise ConfigError(
            f"Configuration validation failed for '{config_path}':\n- "
            + "\n- ".join(errors)
        )

    exp_data = raw_data.get("experiment", {})
    paths_data = raw_data.get("paths", {})
    budgets_data = raw_data.get("budgets", {})
    sandbox_data = raw_data.get("sandbox", {})
    measurement_data = raw_data.get("measurement", {})

    return LeafConfig(
        experiment=ExperimentConfig(
            name=exp_data.get("name", "default_experiment"),
            description=exp_data.get("description", "Default LEAF benchmark configuration"),
            repetitions=exp_data.get("repetitions", 1),
            seed=exp_data.get("seed", 42),
            dry_run=exp_data.get("dry_run", False),
            allow_cloud_calls=exp_data.get("allow_cloud_calls", False),
        ),
        paths=PathsConfig(
            data_dir=Path(paths_data.get("data_dir", "data")),
            results_dir=Path(paths_data.get("results_dir", "results")),
            artifacts_dir=Path(paths_data.get("artifacts_dir", "artifacts")),
        ),
        budgets=BudgetsConfig(
            max_attempts_per_problem=budgets_data.get("max_attempts_per_problem", 3),
            max_tokens_per_attempt=budgets_data.get("max_tokens_per_attempt", 2048),
            timeout_compilation_seconds=float(budgets_data.get("timeout_compilation_seconds", 30.0)),
            timeout_execution_seconds=float(budgets_data.get("timeout_execution_seconds", 10.0)),
            max_cost_usd_per_run=float(budgets_data.get("max_cost_usd_per_run", 0.0)),
        ),
        sandbox=SandboxConfig(
            mode=sandbox_data.get("mode", "process"),
            memory_limit_mb=int(sandbox_data.get("memory_limit_mb", 512)),
            cpu_limit_seconds=float(sandbox_data.get("cpu_limit_seconds", 5.0)),
            allow_network=bool(sandbox_data.get("allow_network", False)),
            max_output_bytes=int(sandbox_data.get("max_output_bytes", 65536)),
        ),
        measurement=MeasurementConfig(
            sampling_interval_ms=int(measurement_data.get("sampling_interval_ms", 50)),
            idle_calibration_seconds=float(measurement_data.get("idle_calibration_seconds", 2.0)),
            record_cpu=bool(measurement_data.get("record_cpu", True)),
            record_gpu=bool(measurement_data.get("record_gpu", True)),
        ),
        supported_languages=raw_data.get(
            "supported_languages", ["python", "cpp", "java"]
        ),
    )


def validate_config_file(path: str | Path) -> tuple[bool, list[str]]:
    """Validate a YAML configuration file stored on disk without raising an exception.

    Args:
        path: Filesystem path to the YAML file to validate.

    Returns:
        A tuple `(is_valid, error_list)`. `is_valid` is True if and only if
        `error_list` is empty.
    """
    config_path = Path(path)
    if not config_path.is_file():
        return False, [f"File not found: {config_path}"]

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except (yaml.YAMLError, OSError) as e:
        return False, [f"YAML syntax error: {e}"]

    errors = validate_config_dict(data)
    return len(errors) == 0, errors
