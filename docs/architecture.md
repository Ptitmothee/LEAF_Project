# Project Architecture & Modularity

The LEAF framework is organized into decoupled Python packages under `source/leaf/`:

```text
source/leaf/
├── __init__.py          # Version metadata
├── cli/                 # Command-line interface subcommands (info, validate-config)
├── core/                # Configuration models, logging, and custom exceptions
├── datasets/            # Ingestion connectors, temporal cohorts, and caching
├── models/              # Common ModelAdapter interface for local & cloud LLMs
├── prompts/             # Versioned prompt templates for the 7 strategies
├── generation/          # Orchestration loop, budgets, and attempt history
├── sandbox/             # Hardened container/VM runner for security validation
├── runner/              # Controlled native runner for energy measurement experiments
├── measurement/         # Telemetry samplers (NVML, psutil, baseline calibration)
├── evaluation/          # Correctness tests and verdict computation
├── storage/             # SQLite results repository and JSONL/CSV export
└── analysis/            # Statistical analysis and figures generator
```

---

## Architectural Principles

1. **Decoupled Security & Energy:** Security tests run in disposable containers (`sandbox/`) without generating main energy data. Energy runs execute on bare metal (`runner/`) to avoid measurement bias.
2. **Never Conceal an Unknown:** Unmeasured cloud inference energy is explicitly marked `unknown`, never zero.
3. **Traceability:** Every experiment run is indexed by an immutable configuration hash, tool versions, and raw telemetry data.

