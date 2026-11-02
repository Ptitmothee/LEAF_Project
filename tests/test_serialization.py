"""Unit tests for JSONL and CSV serialization and synthetic problem suite."""

from pathlib import Path

from leaf.datasets.synthetic import get_synthetic_problems
from leaf.schemas.enums import Language, PromptStrategy, Verdict
from leaf.schemas.run import Attempt, Run
from leaf.schemas.serialization import (
    export_runs_summary_csv,
    load_problems_jsonl,
    load_runs_jsonl,
    save_problems_jsonl,
    save_runs_jsonl,
)


def test_synthetic_problems_generator():
    """Verify that synthetic problem suite generates expected challenges."""
    problems = get_synthetic_problems()
    assert len(problems) >= 4

    p_ids = [p.problem_id for p in problems]
    assert "synth_001_two_sum" in p_ids
    assert "synth_003_infinite_loop" in p_ids
    assert "synth_004_memory_bomb" in p_ids

    p1 = next(p for p in problems if p.problem_id == "synth_001_two_sum")
    assert len(p1.reference_solutions) == 3
    langs = [r.language for r in p1.reference_solutions]
    assert Language.PYTHON in langs
    assert Language.CPP in langs
    assert Language.JAVA in langs


def test_problems_jsonl_roundtrip(tmp_path: Path):
    """Verify writing and reading problems via JSONL."""
    problems = get_synthetic_problems()
    jsonl_file = tmp_path / "problems.jsonl"

    save_problems_jsonl(problems, jsonl_file)
    assert jsonl_file.is_file()

    loaded = load_problems_jsonl(jsonl_file)
    assert len(loaded) == len(problems)
    assert loaded[0].problem_id == problems[0].problem_id
    assert len(loaded[0].tests) == len(problems[0].tests)


def test_runs_jsonl_and_csv_roundtrip(tmp_path: Path):
    """Verify writing and reading experimental runs via JSONL and tabular CSV."""
    run = Run(
        run_id="run_test_1",
        experiment_id="exp_01",
        problem_id="synth_001_two_sum",
        model_id="mock:model",
        language=Language.PYTHON,
        strategy=PromptStrategy.ZERO_SHOT,
        is_solved=True,
        total_attempts=1,
        attempts=[
            Attempt(
                attempt_id="att_1",
                attempt_number=1,
                prompt_text="Solve",
                prompt_hash="hash1",
                raw_response="code",
                extracted_code="code",
                verdict=Verdict.ACCEPTED,
            )
        ],
    )

    jsonl_file = tmp_path / "runs.jsonl"
    save_runs_jsonl([run], jsonl_file)
    loaded_runs = load_runs_jsonl(jsonl_file)
    assert len(loaded_runs) == 1
    assert loaded_runs[0].run_id == "run_test_1"

    csv_file = tmp_path / "summary.csv"
    export_runs_summary_csv([run], csv_file)
    assert csv_file.is_file()
    content = csv_file.read_text(encoding="utf-8")
    assert "run_test_1" in content
    assert "synth_001_two_sum" in content
    assert "AC" in content
