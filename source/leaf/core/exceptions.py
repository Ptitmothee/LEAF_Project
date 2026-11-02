"""Custom exceptions hierarchy for the LEAF project.

Defines a clean, domain-specific exception tree rooted in `LeafError`. This allows
callers to either catch all LEAF-originated errors or handle specific failure domains
(such as execution failures vs. telemetry sampling errors) programmatically.
"""


class LeafError(Exception):
    """Base exception for all errors originating within LEAF."""


class ConfigError(LeafError):
    """Raised when configuration parsing, typing, or constraint validation fails."""


class ExecutionError(LeafError):
    """Raised when process execution, sandboxing, or compiler invocation fails.

    Attributes:
        exit_code: Process exit code if available.
        stdout: Standard output text captured prior to failure.
        stderr: Standard error text captured prior to failure.
        timeout: True if the process was terminated due to timeout.
    """

    def __init__(
        self,
        message: str,
        exit_code: int | None = None,
        stdout: str = "",
        stderr: str = "",
        timeout: bool = False,
    ) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.timeout = timeout


class MeasurementError(LeafError):
    """Raised when energy or telemetry sampling encounters an unrecoverable failure.

    Attributes:
        sensor_name: Identifier of the sensor or meter that failed (e.g., 'NVML', 'RAPL').
        recoverable: Whether the failure was transient.
    """

    def __init__(
        self,
        message: str,
        sensor_name: str = "unknown",
        recoverable: bool = False,
    ) -> None:
        super().__init__(message)
        self.sensor_name = sensor_name
        self.recoverable = recoverable


class DatasetError(LeafError):
    """Raised when problem ingestion, schema validation, or cohort filtering fails."""


class ModelError(LeafError):
    """Raised when an inference model adapter encounters an API or runtime failure."""
