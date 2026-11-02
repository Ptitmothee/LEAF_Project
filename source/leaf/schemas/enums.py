"""Enumerations for benchmark states, verdicts, and scientific classifications."""

from enum import Enum


class Language(str, Enum):
    """Supported target programming languages for generation and execution."""

    PYTHON = "python"
    CPP = "cpp"
    JAVA = "java"


class PromptStrategy(str, Enum):
    """The 7 evaluated prompting strategies ordered by expected complexity/refinement."""

    ZERO_SHOT = "zero_shot"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    CHAIN_OF_DRAFT = "chain_of_draft"
    SELF_REFINEMENT_NL = "self_refinement_NL"
    SELF_REFINEMENT_EXEC = "self_refinement_Exec"
    SELF_REFINEMENT_EXEC_NL = "self_refinement_Exec_NL"
    AGENT = "agent"


class MeasurementProvenance(str, Enum):
    """Provenance and scientific quality label for energy and resource measurements.

    In accordance with Section 3.1 of PROJECT_PLAN.md:
    Never conceal an unknown, and clearly distinguish direct measurements from software estimates.
    """

    MEASURED = "measured"                  # Direct hardware/instrumental measurement
    TOOL_ESTIMATE = "tool_estimate"        # Model/software attribution (e.g. CodeCarbon, TDP proxy)
    PROVIDER_REPORTED = "provider_reported"# Official reported metrics from API provider
    DERIVED_ESTIMATE = "derived_estimate"  # Calculated from other measured metrics (e.g. P * t)
    PROXY = "proxy"                        # Hardware proxy (e.g. GPU device power as snippet proxy)
    UNKNOWN = "unknown"                    # Unmeasured / inaccessible (e.g. remote cloud server energy)


class Verdict(str, Enum):
    """Functional evaluation verdict for candidate code executions."""

    ACCEPTED = "AC"                        # Passed all required tests
    WRONG_ANSWER = "WA"                    # Produced output differing from expected
    TIME_LIMIT_EXCEEDED = "TLE"            # Exceeded execution wall-clock / CPU limit
    MEMORY_LIMIT_EXCEEDED = "MLE"          # Exceeded allocated resident memory quota
    RUNTIME_ERROR = "RE"                   # Crashed with non-zero exit code or exception
    COMPILATION_ERROR = "CE"              # C++ or Java compiler failure
    SECURITY_VIOLATION = "SV"              # Sandbox restriction triggered (network/forbidden access)
    UNKNOWN = "UNKNOWN"                    # Unevaluated or interrupted


class TemporalCohort(str, Enum):
    """Temporal classification for problem statements relative to model training cutoff."""

    HISTORICAL = "historical"              # Published well before model release / cutoff
    RECENT = "recent"                      # Published strictly after declared knowledge cutoff
    UNCERTAIN = "uncertain"                # Ambiguous cutoff date or intermediate timeline

