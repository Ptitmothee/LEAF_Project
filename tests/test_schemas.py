"""Unit tests for Problem, ModelSpec, Measurement, and Run schemas."""

from leaf.schemas.enums import (
    Language,
    MeasurementProvenance,
    PromptStrategy,
    TemporalCohort,
    Verdict,
)
from leaf.schemas.measurement import Measurement
from leaf.schemas.model import ModelSpec
from leaf.schemas.problem import Problem, ReferenceSolution, TestCase
from leaf.schemas.run import Attempt, Run


def test_test_case_roundtrip():
    """Verify serialization roundtrip for TestCase."""
    tc = TestCase(input_data="1 2\n", expected_output="3\n", is_hidden=False, test_id="t1")
    d = tc.to_dict()
    tc2 = TestCase.from_dict(d)
    assert tc2.input_data == tc.input_data
    assert tc2.expected_output == tc.expected_output
    assert tc2.is_hidden == tc.is_hidden
    assert tc2.test_id == tc.test_id


def test_reference_solution_roundtrip():
    """Verify serialization roundtrip for ReferenceSolution."""
    ref = ReferenceSolution(
        code="print('hello')",
        language=Language.PYTHON,
        selection_criterion="official_reference",
        execution_time_seconds=0.05,
    )
    d = ref.to_dict()
    ref2 = ReferenceSolution.from_dict(d)
    assert ref2.code == ref.code
    assert ref2.language == Language.PYTHON
    assert ref2.execution_time_seconds == 0.05


def test_problem_roundtrip_and_filtering():
    """Verify serialization roundtrip and public/hidden test separation for Problem."""
    p = Problem(
        problem_id="p_001",
        source="synthetic",
        source_id="001",
        title="Test Problem",
        statement="Problem statement",
        temporal_cohort=TemporalCohort.HISTORICAL,
        tests=[
            TestCase(input_data="in1", expected_output="out1", is_hidden=False),
            TestCase(input_data="in2", expected_output="out2", is_hidden=True),
        ],
    )
    assert len(p.public_tests()) == 1
    assert len(p.hidden_tests()) == 1
    assert p.public_tests()[0].input_data == "in1"
    assert p.hidden_tests()[0].input_data == "in2"

    d = p.to_dict()
    p2 = Problem.from_dict(d)
    assert p2.problem_id == p.problem_id
    assert p2.temporal_cohort == TemporalCohort.HISTORICAL
    assert len(p2.tests) == 2


def test_model_spec_roundtrip():
    """Verify serialization roundtrip for ModelSpec."""
    spec = ModelSpec(
        model_id="mock:test-model",
        provider="mock",
        display_name="Mock Test Model",
        api_model_name="mock-1",
        is_local=True,
        pricing_input_per_million=0.15,
        pricing_output_per_million=0.60,
    )
    d = spec.to_dict()
    spec2 = ModelSpec.from_dict(d)
    assert spec2.model_id == spec.model_id
    assert spec2.is_local is True
    assert spec2.pricing_input_per_million == 0.15


def test_measurement_roundtrip_with_unknowns():
    """Verify that unmeasured values remain null/None and provenance is respected."""
    m = Measurement(
        phase="inference",
        provenance=MeasurementProvenance.UNKNOWN,
        duration_seconds=1.25,
        energy_joules=None,
        energy_watt_hours=None,
    )
    d = m.to_dict()
    assert d["energy_joules"] is None
    assert d["provenance"] == "unknown"

    m2 = Measurement.from_dict(d)
    assert m2.energy_joules is None
    assert m2.provenance == MeasurementProvenance.UNKNOWN
    assert m2.duration_seconds == 1.25


def test_run_and_attempt_roundtrip():
    """Verify serialization roundtrip for Run and Attempt records."""
    meas = Measurement(
        phase="execution",
        provenance=MeasurementProvenance.MEASURED,
        duration_seconds=0.42,
        energy_joules=8.4,
        energy_watt_hours=8.4 / 3600.0,
    )
    attempt = Attempt(
        attempt_id="att_1",
        attempt_number=1,
        prompt_text="Solve two sum",
        prompt_hash="abc123hash",
        raw_response="```python\nprint(5)\n```",
        extracted_code="print(5)\n",
        input_tokens=50,
        output_tokens=15,
        verdict=Verdict.ACCEPTED,
        execution_measurement=meas,
    )
    run = Run(
        run_id="run_001",
        experiment_id="exp_pilot",
        problem_id="p_001",
        model_id="mock:test",
        language=Language.PYTHON,
        strategy=PromptStrategy.ZERO_SHOT,
        attempts=[attempt],
        is_solved=True,
        total_attempts=1,
        cumulative_input_tokens=50,
        cumulative_output_tokens=15,
        stop_reason="solved",
    )

    d = run.to_dict()
    run2 = Run.from_dict(d)
    assert run2.run_id == "run_001"
    assert run2.is_solved is True
    assert run2.language == Language.PYTHON
    assert run2.strategy == PromptStrategy.ZERO_SHOT
    assert len(run2.attempts) == 1
    assert run2.attempts[0].verdict == Verdict.ACCEPTED
    assert run2.attempts[0].execution_measurement is not None
    assert run2.attempts[0].execution_measurement.energy_joules == 8.4
