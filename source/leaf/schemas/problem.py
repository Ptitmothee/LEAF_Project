"""Data schemas for programming problems, test cases, and reference solutions."""

from dataclasses import asdict, dataclass, field

from leaf.schemas.enums import Language, TemporalCohort
from leaf.typing import JsonDict, ProblemID


@dataclass
class TestCase:
    __test__ = False  # Prevent pytest from treating this domain dataclass as a test suite
    """A single input/output test case for problem evaluation.

    Attributes:
        input_data: String data supplied via standard input (stdin).
        expected_output: Expected exact standard output string (stdout).
        is_hidden: Whether this test is private/hidden from model prompt contexts.
        test_id: Optional identifier or index for this test case.
    """

    input_data: str
    expected_output: str
    is_hidden: bool = False
    test_id: str | None = None

    def to_dict(self) -> JsonDict:
        """Convert test case to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: JsonDict) -> TestCase:
        """Instantiate test case from dictionary."""
        return cls(
            input_data=str(data["input_data"]),
            expected_output=str(data["expected_output"]),
            is_hidden=bool(data.get("is_hidden", False)),
            test_id=data.get("test_id"),
        )


@dataclass
class ReferenceSolution:
    """Accepted reference or human solution for functional baseline comparison.

    Attributes:
        code: Complete source code string.
        language: Programming language of the solution.
        selection_criterion: Criterion used (e.g. 'official_reference', 'fastest_accepted').
        author: Optional author identifier if public.
        submission_time: Submission timestamp if available.
        execution_time_seconds: Official execution runtime on platform if recorded.
    """

    code: str
    language: Language | str
    selection_criterion: str = "official_reference"
    author: str | None = None
    submission_time: str | None = None
    execution_time_seconds: float | None = None

    def to_dict(self) -> JsonDict:
        """Convert reference solution to dictionary."""
        return {
            "code": self.code,
            "language": self.language.value if isinstance(self.language, Language) else str(self.language),
            "selection_criterion": self.selection_criterion,
            "author": self.author,
            "submission_time": self.submission_time,
            "execution_time_seconds": self.execution_time_seconds,
        }

    @classmethod
    def from_dict(cls, data: JsonDict) -> ReferenceSolution:
        """Instantiate reference solution from dictionary."""
        return cls(
            code=str(data["code"]),
            language=Language(data["language"]) if data.get("language") in Language._value2member_map_ else str(data["language"]),
            selection_criterion=str(data.get("selection_criterion", "official_reference")),
            author=data.get("author"),
            submission_time=data.get("submission_time"),
            execution_time_seconds=float(data["execution_time_seconds"]) if data.get("execution_time_seconds") is not None else None,
        )


@dataclass
class Problem:
    """Standardized programming problem schema matching Section 6 of PROJECT_PLAN.md.

    Attributes:
        problem_id: Unique benchmark identifier (e.g., 'codecontests_1234', 'synth_001').
        source: Origin platform or dataset ('codecontests', 'livecodebench', 'synthetic').
        source_id: Original identifier in the parent dataset.
        title: Title of the problem.
        statement: Full problem description and task prompt.
        input_spec: Description of standard input format.
        output_spec: Description of expected standard output format.
        constraints: Textual or mathematical constraints (e.g. 1 <= N <= 10^5).
        tags: Problem domain tags (e.g., ['math', 'dp', 'sorting']).
        difficulty: Categorical or numeric difficulty rating (e.g., 'easy', '1200').
        published_at: Date/time when problem was first published/held.
        temporal_cohort: Categorization relative to model cutoff.
        tests: List of authorized public and hidden test cases.
        reference_solutions: List of known reference solutions.
        license: Dataset license or terms of use.
        metadata_raw: Preserved raw source dictionary for complete provenance.
    """

    problem_id: ProblemID
    source: str
    source_id: str
    title: str
    statement: str
    input_spec: str = ""
    output_spec: str = ""
    constraints: str = ""
    tags: list[str] = field(default_factory=list)
    difficulty: str = "medium"
    published_at: str | None = None
    contest_at: str | None = None
    dataset_captured_at: str | None = None
    temporal_cohort: TemporalCohort | str = TemporalCohort.HISTORICAL
    license: str = "Unknown"
    source_url: str | None = None
    tests: list[TestCase] = field(default_factory=list)
    reference_solutions: list[ReferenceSolution] = field(default_factory=list)
    human_time_value: float | None = None
    human_time_semantics: str | None = None
    human_time_source: str | None = None
    metadata_raw: JsonDict = field(default_factory=dict)

    def public_tests(self) -> list[TestCase]:
        """Return only non-hidden test cases visible to prompting contexts."""
        return [t for t in self.tests if not t.is_hidden]

    def hidden_tests(self) -> list[TestCase]:
        """Return private evaluation tests inaccessible to the model."""
        return [t for t in self.tests if t.is_hidden]

    def to_dict(self) -> JsonDict:
        """Serialize problem to JSON-compatible dictionary."""
        return {
            "schema_version": "1.0.0",
            "problem_id": self.problem_id,
            "source": self.source,
            "source_id": self.source_id,
            "source_url": self.source_url,
            "title": self.title,
            "statement": self.statement,
            "input_spec": self.input_spec,
            "output_spec": self.output_spec,
            "constraints": self.constraints,
            "tags": list(self.tags),
            "difficulty": self.difficulty,
            "published_at": self.published_at,
            "contest_at": self.contest_at,
            "dataset_captured_at": self.dataset_captured_at,
            "temporal_cohort": self.temporal_cohort.value if isinstance(self.temporal_cohort, TemporalCohort) else str(self.temporal_cohort),
            "license": self.license,
            "tests": [t.to_dict() for t in self.tests],
            "reference_solutions": [r.to_dict() for r in self.reference_solutions],
            "human_time_value": self.human_time_value,
            "human_time_semantics": self.human_time_semantics,
            "human_time_source": self.human_time_source,
            "metadata_raw": self.metadata_raw,
        }

    @classmethod
    def from_dict(cls, data: JsonDict) -> Problem:
        """Deserialize problem from dictionary with schema validation."""
        cohort_val = data.get("temporal_cohort", TemporalCohort.HISTORICAL.value)
        cohort = TemporalCohort(cohort_val) if cohort_val in TemporalCohort._value2member_map_ else str(cohort_val)

        return cls(
            problem_id=str(data["problem_id"]),
            source=str(data["source"]),
            source_id=str(data["source_id"]),
            source_url=data.get("source_url"),
            title=str(data["title"]),
            statement=str(data["statement"]),
            input_spec=str(data.get("input_spec", "")),
            output_spec=str(data.get("output_spec", "")),
            constraints=str(data.get("constraints", "")),
            tags=list(data.get("tags", [])),
            difficulty=str(data.get("difficulty", "medium")),
            published_at=data.get("published_at"),
            contest_at=data.get("contest_at"),
            dataset_captured_at=data.get("dataset_captured_at"),
            temporal_cohort=cohort,
            license=str(data.get("license", "Unknown")),
            tests=[TestCase.from_dict(t) for t in data.get("tests", [])],
            reference_solutions=[ReferenceSolution.from_dict(r) for r in data.get("reference_solutions", [])],
            human_time_value=float(data["human_time_value"]) if data.get("human_time_value") is not None else None,
            human_time_semantics=data.get("human_time_semantics"),
            human_time_source=data.get("human_time_source"),
            metadata_raw=dict(data.get("metadata_raw", {})),
        )
