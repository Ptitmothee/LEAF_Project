# 0.4 - Data Schemas and Synthetic Dataset (Phase 2)

This document describes the data models, physical unit conversions, serialization routines, and synthetic problems established in Phase 2 of the LEAF benchmark.

---

## 1. Schema Architecture & Domain Invariants

In accordance with Section 6 of `PROJECT_PLAN.md` and the scientific invariants of `AGENTS.md`:

```text
source/leaf/
├── typing.py              # Centralized domain and physical type aliases
├── core/
│   └── units.py           # Explicit Joule, Watt, and Watt-hour conversions
├── schemas/
│   ├── __init__.py        # Clean schema exports
│   ├── enums.py           # Language, Verdict, PromptStrategy, MeasurementProvenance
│   ├── problem.py         # Problem, TestCase, ReferenceSolution
│   ├── model.py           # ModelSpec
│   ├── measurement.py     # Measurement (physical quantities and provenance)
│   ├── run.py             # Run, Attempt, TestResult
│   └── serialization.py   # JSON, JSONL, and tabular CSV helpers
└── datasets/
    ├── __init__.py
    └── synthetic.py       # Deterministic offline synthetic problems
```

### Key Scientific Invariants Implemented:
1. **Never Conceal an Unknown:** If an energy value is unavailable (e.g. remote cloud API inference energy), it is stored as `null` / `None` with provenance `MeasurementProvenance.UNKNOWN`. It is never manufactured or set to zero.
2. **Provenance Labels:** Every measurement record carries an explicit provenance tag (`measured`, `tool_estimate`, `provider_reported`, `derived_estimate`, `proxy`, `unknown`).
3. **Prompt Leak Protection:** The `Problem` class provides separate `public_tests()` and `hidden_tests()` methods to guarantee private test cases and reference solutions are not leaked into prompting contexts.

---

## 2. Synthetic Benchmark Dataset

[`leaf.datasets.synthetic.get_synthetic_problems()`](file:///c:/Programs/LEAF_Project/source/leaf/datasets/synthetic.py) provides 4 deterministic test problems covering all execution branches without requiring internet access or third-party datasets:

| Problem ID | Category | Validated Capability |
| :--- | :--- | :--- |
| `synth_001_two_sum` | Math / Basics | Standard solved execution across Python, C++, and Java reference solutions. |
| `synth_002_reverse_string` | Strings | Text parsing and string manipulation. |
| `synth_003_infinite_loop` | Trap / Algorithmic | Infinite loop / Time Limit Exceeded (TLE) runner validation. |
| `synth_004_memory_bomb` | Trap / Stress | Memory Limit Exceeded (MLE) / excessive buffer allocation detection. |

---

## 3. Serialization & Data Exchange

[`leaf.schemas.serialization`](file:///c:/Programs/LEAF_Project/source/leaf/schemas/serialization.py) provides versioned (`schema_version: "1.0.0"`) I/O:
* **`save_problems_jsonl` / `load_problems_jsonl`**: Stream problems in newline-delimited JSON.
* **`save_runs_jsonl` / `load_runs_jsonl`**: Stream experimental run records.
* **`export_runs_summary_csv`**: Flattens run metadata, token counts, and verdicts into a tabular CSV suitable for Pandas and statistical analysis.

---

## 4. Verification & Testing

Run all unit tests:
```powershell
uv run pytest
```
*Expected result:* 26 passed tests (`test_schemas.py`, `test_serialization.py`, `test_units.py`, etc.).

Build documentation:
```powershell
uv run mkdocs build --strict
```
*Expected result:* Strict build completes with 0 warnings.

