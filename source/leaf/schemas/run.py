"""Data schemas representing model generation attempts, test executions, and overall runs."""

from dataclasses import dataclass, field

from leaf.schemas.enums import Language, PromptStrategy, Verdict
from leaf.schemas.measurement import Measurement
from leaf.typing import (
    AttemptID,
    ExperimentID,
    JsonDict,
    ModelSpecID,
    ProblemID,
    RunID,
    TimeSeconds,
)


@dataclass
class TestResult:
    __test__ = False  # Prevent pytest from treating this domain dataclass as a test suite
    """Outcome of running code against a single test case.

    Attributes:
        test_id: Identifier of the test case.
        verdict: Verdict (AC, WA, TLE, MLE, RE).
        execution_time_seconds: Elapsed execution duration.
        stdout_captured: Captured output (truncated if excessive).
        stderr_captured: Captured error stream.
        memory_used_mb: Peak resident memory used during this test.
    """

    test_id: str | None
    verdict: Verdict | str
    execution_time_seconds: TimeSeconds
    stdout_captured: str = ""
    stderr_captured: str = ""
    memory_used_mb: float | None = None

    def to_dict(self) -> JsonDict:
        """Convert test result to dictionary."""
        v_str = self.verdict.value if isinstance(self.verdict, Verdict) else str(self.verdict)
        return {
            "test_id": self.test_id,
            "verdict": v_str,
            "execution_time_seconds": self.execution_time_seconds,
            "stdout_captured": self.stdout_captured,
            "stderr_captured": self.stderr_captured,
            "memory_used_mb": self.memory_used_mb,
        }

    @classmethod
    def from_dict(cls, data: JsonDict) -> TestResult:
        """Instantiate test result from dictionary."""
        v_val = data.get("verdict", Verdict.UNKNOWN.value)
        v = Verdict(v_val) if v_val in Verdict._value2member_map_ else str(v_val)
        return cls(
            test_id=data.get("test_id"),
            verdict=v,
            execution_time_seconds=float(data["execution_time_seconds"]),
            stdout_captured=str(data.get("stdout_captured", "")),
            stderr_captured=str(data.get("stderr_captured", "")),
            memory_used_mb=float(data["memory_used_mb"]) if data.get("memory_used_mb") is not None else None,
        )


@dataclass
class Attempt:
    """A single iteration or step within an iterative prompting strategy.

    Attributes:
        attempt_id: Unique attempt identifier within the run.
        attempt_number: 1-based index of this iteration.
        prompt_text: Full prompt submitted to the model (protected from test leaks).
        prompt_hash: SHA-256 hash of the prompt for deduplication and caching.
        raw_response: Full unmodified text response returned by the LLM.
        extracted_code: Code snippet isolated from markdown fences or text.
        input_tokens: Number of prompt tokens billed/reported by API.
        output_tokens: Number of completion tokens billed/reported by API.
        reasoning_tokens: Number of internal reasoning/chain-of-thought tokens if exposed.
        latency_seconds: Duration between sending request and receiving full response.
        billed_cost_usd: Calculated financial cost in USD from dated pricing schedule.
        feedback_given: Error message or NL critique communicated back to model for next attempt.
        compilation_success: True if C++/Java compiled cleanly, False if failed, None if interpreted.
        compilation_error_message: Compiler error output if compilation failed.
        test_results: Execution outcomes against authorized tests.
        verdict: Overall verdict of this attempt.
        inference_measurement: Hardware energy/power measurement during local inference if applicable.
        compilation_measurement: Energy/time measurement for compilation.
        execution_measurement: Energy/time measurement for running test cases.
    """

    attempt_id: AttemptID
    attempt_number: int
    prompt_text: str
    prompt_hash: str
    raw_response: str
    extracted_code: str
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int | None = None
    latency_seconds: float = 0.0
    billed_cost_usd: float | None = None
    feedback_given: str | None = None
    compilation_success: bool | None = None
    compilation_error_message: str | None = None
    test_results: list[TestResult] = field(default_factory=list)
    verdict: Verdict | str = Verdict.UNKNOWN
    inference_measurement: Measurement | None = None
    compilation_measurement: Measurement | None = None
    execution_measurement: Measurement | None = None

    def to_dict(self) -> JsonDict:
        """Serialize attempt to dictionary."""
        v_str = self.verdict.value if isinstance(self.verdict, Verdict) else str(self.verdict)
        return {
            "attempt_id": self.attempt_id,
            "attempt_number": self.attempt_number,
            "prompt_text": self.prompt_text,
            "prompt_hash": self.prompt_hash,
            "raw_response": self.raw_response,
            "extracted_code": self.extracted_code,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "latency_seconds": self.latency_seconds,
            "billed_cost_usd": self.billed_cost_usd,
            "feedback_given": self.feedback_given,
            "compilation_success": self.compilation_success,
            "compilation_error_message": self.compilation_error_message,
            "test_results": [t.to_dict() for t in self.test_results],
            "verdict": v_str,
            "inference_measurement": self.inference_measurement.to_dict() if self.inference_measurement else None,
            "compilation_measurement": self.compilation_measurement.to_dict() if self.compilation_measurement else None,
            "execution_measurement": self.execution_measurement.to_dict() if self.execution_measurement else None,
        }

    @classmethod
    def from_dict(cls, data: JsonDict) -> Attempt:
        """Instantiate attempt from dictionary."""
        v_val = data.get("verdict", Verdict.UNKNOWN.value)
        v = Verdict(v_val) if v_val in Verdict._value2member_map_ else str(v_val)
        return cls(
            attempt_id=str(data["attempt_id"]),
            attempt_number=int(data["attempt_number"]),
            prompt_text=str(data["prompt_text"]),
            prompt_hash=str(data["prompt_hash"]),
            raw_response=str(data["raw_response"]),
            extracted_code=str(data["extracted_code"]),
            input_tokens=int(data.get("input_tokens", 0)),
            output_tokens=int(data.get("output_tokens", 0)),
            reasoning_tokens=int(data["reasoning_tokens"]) if data.get("reasoning_tokens") is not None else None,
            latency_seconds=float(data.get("latency_seconds", 0.0)),
            billed_cost_usd=float(data["billed_cost_usd"]) if data.get("billed_cost_usd") is not None else None,
            feedback_given=data.get("feedback_given"),
            compilation_success=data.get("compilation_success"),
            compilation_error_message=data.get("compilation_error_message"),
            test_results=[TestResult.from_dict(t) for t in data.get("test_results", [])],
            verdict=v,
            inference_measurement=Measurement.from_dict(data["inference_measurement"]) if data.get("inference_measurement") else None,
            compilation_measurement=Measurement.from_dict(data["compilation_measurement"]) if data.get("compilation_measurement") else None,
            execution_measurement=Measurement.from_dict(data["execution_measurement"]) if data.get("execution_measurement") else None,
        )


@dataclass
class Run:
    """A complete experimental trial associating Problem x Model x Language x Strategy.

    Attributes:
        run_id: Unique identifier for this run.
        experiment_id: Campaign identifier to which this run belongs.
        problem_id: ID of the problem being solved.
        model_id: ID of the model evaluated.
        language: Programming language used.
        strategy: Prompting strategy employed.
        repetition_index: Index of this run if repeated (1-based).
        started_at: ISO timestamp of run commencement.
        completed_at: ISO timestamp of run termination.
        attempts: Sequence of all generation iterations until success or budget exhaustion.
        is_solved: True if any attempt produced a completely accepted solution.
        total_attempts: Total number of attempts executed.
        cumulative_input_tokens: Total prompt tokens consumed across all attempts.
        cumulative_output_tokens: Total completion tokens consumed across all attempts.
        cumulative_cost_usd: Total financial cost across all attempts.
        stop_reason: Reason run halted ('solved', 'budget_exhausted', 'timeout', 'error').
        system_metadata: Operating system, CPU/GPU, and runtime versions recording provenance.
    """

    run_id: RunID
    experiment_id: ExperimentID
    problem_id: ProblemID
    model_id: ModelSpecID
    language: Language | str
    strategy: PromptStrategy | str
    repetition_index: int = 1
    started_at: str | None = None
    completed_at: str | None = None
    attempts: list[Attempt] = field(default_factory=list)
    is_solved: bool = False
    total_attempts: int = 0
    cumulative_input_tokens: int = 0
    cumulative_output_tokens: int = 0
    cumulative_cost_usd: float | None = None
    stop_reason: str = "pending"
    system_metadata: JsonDict = field(default_factory=dict)

    def to_dict(self) -> JsonDict:
        """Serialize run to dictionary."""
        lang_str = self.language.value if isinstance(self.language, Language) else str(self.language)
        strat_str = self.strategy.value if isinstance(self.strategy, PromptStrategy) else str(self.strategy)
        return {
            "schema_version": "1.0.0",
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "problem_id": self.problem_id,
            "model_id": self.model_id,
            "language": lang_str,
            "strategy": strat_str,
            "repetition_index": self.repetition_index,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "is_solved": self.is_solved,
            "total_attempts": self.total_attempts,
            "cumulative_input_tokens": self.cumulative_input_tokens,
            "cumulative_output_tokens": self.cumulative_output_tokens,
            "cumulative_cost_usd": self.cumulative_cost_usd,
            "stop_reason": self.stop_reason,
            "attempts": [a.to_dict() for a in self.attempts],
            "system_metadata": self.system_metadata,
        }

    @classmethod
    def from_dict(cls, data: JsonDict) -> Run:
        """Instantiate run from dictionary."""
        lang_val = data.get("language", Language.PYTHON.value)
        lang = Language(lang_val) if lang_val in Language._value2member_map_ else str(lang_val)
        strat_val = data.get("strategy", PromptStrategy.ZERO_SHOT.value)
        strat = PromptStrategy(strat_val) if strat_val in PromptStrategy._value2member_map_ else str(strat_val)

        return cls(
            run_id=str(data["run_id"]),
            experiment_id=str(data["experiment_id"]),
            problem_id=str(data["problem_id"]),
            model_id=str(data["model_id"]),
            language=lang,
            strategy=strat,
            repetition_index=int(data.get("repetition_index", 1)),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            attempts=[Attempt.from_dict(a) for a in data.get("attempts", [])],
            is_solved=bool(data.get("is_solved", False)),
            total_attempts=int(data.get("total_attempts", 0)),
            cumulative_input_tokens=int(data.get("cumulative_input_tokens", 0)),
            cumulative_output_tokens=int(data.get("cumulative_output_tokens", 0)),
            cumulative_cost_usd=float(data["cumulative_cost_usd"]) if data.get("cumulative_cost_usd") is not None else None,
            stop_reason=str(data.get("stop_reason", "pending")),
            system_metadata=dict(data.get("system_metadata", {})),
        )
