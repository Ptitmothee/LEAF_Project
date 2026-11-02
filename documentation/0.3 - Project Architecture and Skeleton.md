# 0.3 - Project Architecture and Skeleton (Phase 1)

This document describes the structure, CLI capabilities, configuration schema, and reproduction steps for the LEAF skeleton established in Phase 1.

---

## 1. Package Architecture

The code is organized under `source/leaf/` as a modular Python package:

```text
source/leaf/
├── __init__.py          # Package metadata (version 0.1.0)
├── __main__.py          # Entry point for `python -m leaf`
├── cli/                 # Command-line interface
│   ├── __init__.py
│   └── main.py          # Argparse implementation (info, validate-config)
└── core/                # Shared infrastructure
    ├── __init__.py
    ├── config.py        # Typed dataclasses & YAML parser/validator
    ├── exceptions.py    # Custom domain exceptions (LeafError, ConfigError, etc.)
    └── logging.py       # Structured logging with regex secret masking
```

A root-level launcher [`run_leaf.py`](file:///c:/Programs/LEAF_Project/run_leaf.py) provides a direct entrypoint that ensures `source/` is automatically on `sys.path`.

---

## 2. Configuration Management

All benchmark parameters are defined in YAML format (see [`config/default_config.yaml`](file:///c:/Programs/LEAF_Project/config/default_config.yaml)).

### Key Sections:
* **`experiment`**: Experiment name, repetition counts, random seed, and execution flags (`dry_run`, `allow_cloud_calls`).
* **`paths`**: Configurable relative paths for input datasets (`data`), output metrics (`results`), and temporary compilation artifacts (`artifacts`).
* **`budgets`**: Enforced thresholds for attempts per problem, max tokens per attempt, compilation timeouts (default 30s), execution timeouts (default 10s), and cost ceilings.
* **`sandbox`**: Mode (`process` or `container`), memory limit (MB), CPU time limit (s), output byte limit, and network access toggle (default `false`).
* **`measurement`**: Sampling interval (ms), idle calibration duration (s), and flags to enable CPU/GPU power tracking.
* **`supported_languages`**: Target programming languages (`python`, `cpp`, `java`).

Validation is enforced by `leaf.core.config.validate_config_dict`, catching missing keys, invalid types, or negative numeric bounds.

---

## 3. Secret Sanitization

In accordance with project rules, no secrets or private keys must ever leak to logs or console outputs.

[`leaf.core.logging.SecretSanitizingFormatter`](file:///c:/Programs/LEAF_Project/source/leaf/core/logging.py) automatically intercepts and masks:
* Bearer tokens (`Bearer ***REDACTED***`)
* OpenAI API keys (`sk-***REDACTED***`)
* Google Cloud / Gemini API keys (`AIza***REDACTED***`)
* Generic key/secret assignments (`api_key='***REDACTED***'`, `secret='***REDACTED***'`)

---

## 4. How to Reproduce & Verify

All commands use the `uv` toolchain and require no external network access:

### 1. Verify Environment Synchronization
```bash
uv sync --locked --offline
```
*Expected result:* 22 packages verified from `uv.lock`.

### 2. Inspect Environment and Toolchains
```bash
uv run python run_leaf.py info
```
*Expected result:* Outputs OS, Python runtime, detected C++ (g++) and Java (javac) versions, container engines, and GPU telemetry.

### 3. Validate Configuration File
```bash
uv run python run_leaf.py validate-config config/default_config.yaml
```
*Expected result:* `SUCCESS: Configuration 'config/default_config.yaml' is valid.`

### 4. Run Automated Unit Tests
```bash
uv run pytest
```
*Expected result:* All 14 tests pass (`tests/test_cli.py`, `tests/test_config.py`, `tests/test_logging.py`).

### 5. Run Linter
```bash
uv run ruff check .
```
*Expected result:* `All checks passed!`.

