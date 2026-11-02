# ADR-0001: Architecture, Technology Stack, and Orchestration Language

* **Status:** Accepted
* **Date:** 2026-11-02
* **Authors:** Antigravity & User
* **Technical Context:** LEAF Project (Phase 1 — Project Skeleton)

---

## 1. Context and Problem Statement

The goal of the LEAF project is to build a reproducible research tool that benchmarks and compares the energy cost of AI inference and generated code execution across multiple models, prompting strategies, and three programming languages: Python, C++, and Java.

The benchmark requires:
1. Orchestrating LLM calls across multiple prompting strategies with feedback loops.
2. Managing untrusted code extraction, compilation, and execution across Python, C++, and Java.
3. Reading energy telemetry (GPU power via NVML, CPU process metrics via OS system calls, idle baselines).
4. Ensuring strict reproducibility, schema validation, data export, statistical aggregation, and chart generation.

We evaluated whether C++ or Java would provide measurable benefits over Python for reading hardware energy, isolating processes, or executing the benchmark, and determined how to structure the project for long-term maintainability.

---

## 2. Decision Drivers

* **Scientific accuracy & measurement resolution:** Hardware energy meters (NVML, Intel/AMD RAPL) update on millisecond timescales (1 ms to 100 ms). Low-level language speed does not increase the underlying register update frequency.
* **Security & Isolation boundary:** Process isolation and resource quotas are enforced by the operating system kernel (Win32 Job Objects, Linux cgroups/namespaces) or container engines, not the orchestrator language.
* **Ecosystem for research & ML:** LLM APIs, statistical analysis (`pandas`), plotting (`matplotlib`), and schema validation are native to Python.
* **Lean dependencies & full offline reproducibility:** All project operations must be lockfile-controlled (`uv.lock`), runnable offline, and traceable.

---

## 3. Considered Options

1. **Pure C++:** High performance and native Win32/POSIX access, but extreme friction for LLM APIs, JSON processing, data wrangling, and charting.
2. **Pure Java:** Strong typing, but poor low-level OS access (requires JNI for Job Objects/MSRs), JVM background threads (JIT, GC) contaminate energy readings, and limited data science ecosystem.
3. **Python Orchestrator with Native OS/Helper Bridges (Chosen):** Python orchestrates the pipeline, schemas, APIs, and analysis. Native OS APIs (Job Objects, NVML) are accessed via standard library bindings (`ctypes`, `win32job`, `psutil`). If specialized high-frequency helpers are ever needed on Windows (e.g. custom kernel MSR drivers), small C++ utilities can be invoked seamlessly.

---

## 4. Decision

We choose **Python 3.14+ managed by Astral `uv`** as the core orchestration and benchmarking platform:

1. **Source Layout:** Modular package under `source/leaf/` containing:
   * `leaf.core`: Logging (with secret sanitization), configuration models, and custom exceptions.
   * `leaf.cli`: CLI entrypoint (`run_leaf.py` launcher).
   * `leaf.schemas`: Versioned data models (Phase 2).
   * `leaf.sandbox`: Isolated runners for Python, C++, and Java (Phase 3).
   * `leaf.measurement`: Hardware power samplers and provenance accounting (Phase 4).
   * `leaf.datasets`: Connectors and cohort filters (Phase 5 & 9).
   * `leaf.models`: Model adapters with telemetry collection (Phase 6).
   * `leaf.prompts` & `leaf.generation`: 7 prompting strategies with budgets (Phase 7).
   * `leaf.evaluation`, `leaf.storage`, `leaf.analysis`: Verification, SQLite storage, and plots.
2. **Configuration:** YAML format in `config/default_config.yaml`, validated strictly via `leaf.core.config`.
3. **Security Invariant:** Zero secrets in repositories, logs, or results. Log outputs pass through `SecretSanitizingFormatter`.
4. **Environment Control:** `pyproject.toml` and `uv.lock` are tracked; tests and commands are run via `uv run`.

---

## 5. Consequences

### Positive
* Fast, flexible experimental iteration without sacrificing telemetry accuracy.
* Complete offline reproducibility and strict dependency isolation.
* Clear modular boundaries making code easy to refactor, test, and maintain.
* Automated prevention of secret leakage in logs.

### Limitations / Mitigations
* On Windows, native container runtimes (Docker/Podman) are currently absent. Initial sandbox testing will utilize Windows Job Object / process limits (`psutil`), with container execution enabled once external container engines are available.
* CPU hardware RAPL counters are not exposed to non-admin user-space on Windows. Telemetry will record process CPU time/memory and label unavailable direct electrical measurements as `unknown` or `tool_estimate`, never manufacturing false precision.

