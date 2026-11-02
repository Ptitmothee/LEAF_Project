"""Serialization and persistence utilities for LEAF schema models.

Provides JSON, JSONL, and CSV export/import helpers with explicit schema versioning.
"""

import csv
import json
from pathlib import Path

from leaf.schemas.enums import Verdict
from leaf.schemas.problem import Problem
from leaf.schemas.run import Run
from leaf.typing import JsonDict, PathLike


def save_json(data: JsonDict, file_path: PathLike, indent: int = 2) -> Path:
    """Save a dictionary to a JSON file, creating parent directories if necessary."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    return path


def load_json(file_path: PathLike) -> JsonDict:
    """Load a JSON file into a dictionary."""
    path = Path(file_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_problems_jsonl(problems: list[Problem], file_path: PathLike) -> Path:
    """Append or write a sequence of Problem objects to a JSONL file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(p.to_dict(), ensure_ascii=False) + "\n" for p in problems)
    return path


def load_problems_jsonl(file_path: PathLike) -> list[Problem]:
    """Load Problem objects from a JSONL file."""
    path = Path(file_path)
    problems: list[Problem] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                problems.append(Problem.from_dict(json.loads(line_str)))
    return problems


def save_runs_jsonl(runs: list[Run], file_path: PathLike) -> Path:
    """Write experimental Run records to a JSONL file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r.to_dict(), ensure_ascii=False) + "\n" for r in runs)
    return path


def load_runs_jsonl(file_path: PathLike) -> list[Run]:
    """Load Run records from a JSONL file."""
    path = Path(file_path)
    runs: list[Run] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                runs.append(Run.from_dict(json.loads(line_str)))
    return runs


def export_runs_summary_csv(runs: list[Run], file_path: PathLike) -> Path:
    """Export flattened high-level tabular summary of runs to CSV for statistical analysis."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "run_id",
        "experiment_id",
        "problem_id",
        "model_id",
        "language",
        "strategy",
        "repetition_index",
        "is_solved",
        "total_attempts",
        "cumulative_input_tokens",
        "cumulative_output_tokens",
        "cumulative_cost_usd",
        "stop_reason",
        "last_verdict",
    ]

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in runs:
            last_verdict = (
                r.attempts[-1].verdict
                if r.attempts
                else Verdict.UNKNOWN.value
            )
            v_str = last_verdict.value if isinstance(last_verdict, Verdict) else str(last_verdict)
            writer.writerow({
                "run_id": r.run_id,
                "experiment_id": r.experiment_id,
                "problem_id": r.problem_id,
                "model_id": r.model_id,
                "language": r.language.value if hasattr(r.language, "value") else str(r.language),
                "strategy": r.strategy.value if hasattr(r.strategy, "value") else str(r.strategy),
                "repetition_index": r.repetition_index,
                "is_solved": r.is_solved,
                "total_attempts": r.total_attempts,
                "cumulative_input_tokens": r.cumulative_input_tokens,
                "cumulative_output_tokens": r.cumulative_output_tokens,
                "cumulative_cost_usd": r.cumulative_cost_usd,
                "stop_reason": r.stop_reason,
                "last_verdict": v_str,
            })
    return path
