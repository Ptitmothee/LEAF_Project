"""Custom exceptions hierarchy for the LEAF project."""


class LeafError(Exception):
    """Base exception for all errors originating within LEAF."""


class ConfigError(LeafError):
    """Raised when configuration parsing or validation fails."""


class ExecutionError(LeafError):
    """Raised when process execution, sandboxing, or compiler invocation fails."""


class MeasurementError(LeafError):
    """Raised when energy/telemetry sampling encounters an unrecoverable failure."""


class DatasetError(LeafError):
    """Raised when problem ingestion, schema validation, or cohort filtering fails."""


class ModelError(LeafError):
    """Raised when an inference model adapter encounters an API or runtime failure."""
