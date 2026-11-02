# LEAF_Project (Low Energy AI Framework)

AI-generated code energy and efficiency benchmark: measuring and comparing the energy cost of AI inference and generated-code execution across models, prompting strategies, and programming languages (Python, C++, and Java).

---

## Quickstart

### Prerequisites
* [uv](https://docs.astral.sh/uv/) (v0.13.6+)
* Python 3.14.10 (managed automatically via `uv`)

### 1. Synchronize Virtual Environment
```bash
uv sync --locked
```

### 2. Inspect Environment & Available Toolchains
```bash
uv run python run_leaf.py info
```

### 3. Validate Benchmark Configuration
```bash
uv run python run_leaf.py validate-config config/default_config.yaml
```

### 4. Run Test Suite
```bash
uv run pytest
```

### 5. Lint & Style Check
```bash
uv run ruff check .
```

---

## Project Structure

```text
├── .python-version        # Pinned Python version (3.14.10)
├── AGENTS.md              # Permanent project rules and scientific invariants
├── PROJECT_PLAN.md        # Detailed 12-phase project specification and roadmap
├── config/                # Benchmark YAML configuration files
├── data/                  # Input datasets, problem statements, and reference tests
├── documentation/         # Setup guides, phase docs, and Architecture Decision Records (ADRs)
├── results/               # Experimental telemetry, JSONL exports, and charts
├── artifacts/             # Intermediate compiled executables and scratch files
├── run_leaf.py            # CLI entrypoint launcher
├── source/
│   └── leaf/              # Core LEAF benchmark package
│       ├── cli/           # Command-line interface subcommands
│       ├── core/          # Configuration, structured logging, and exceptions
│       ├── datasets/      # Ingestion and temporal cohort filtering (Phases 5 & 9)
│       ├── models/        # Model adapters and inference accounting (Phase 6)
│       ├── prompts/       # Prompt templates and 7 iterative strategies (Phase 7)
│       ├── sandbox/       # Isolated compilers and runners for Python, C++, Java (Phase 3)
│       ├── measurement/   # Energy meters and telemetry calibration (Phase 4)
│       ├── evaluation/    # Verdict evaluation against test suites
│       └── analysis/      # Statistical aggregation and figure generation (Phase 10)
└── tests/                 # Automated pytest suite
```

For detailed specifications and architectural decisions, see [`documentation/ADR-0001-architecture-and-technology-stack.md`](documentation/ADR-0001-architecture-and-technology-stack.md) and [`PROJECT_PLAN.md`](PROJECT_PLAN.md).
