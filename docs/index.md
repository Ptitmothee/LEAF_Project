# LEAF Benchmark Framework

**Low Energy AI Framework (LEAF)** is a reproducible research platform designed to measure and compare the energy cost of AI code generation and execution across multiple models, prompting strategies, and programming languages (Python, C++, and Java).

---

## Key Capabilities

* **Decoupled Execution Workflows:**
    * **Workflow A (Security Validation):** Hardened, disposable containers/VMs to test for memory leaks, infinite loops, and unauthorized system access.
    * **Workflow B (Native Energy Measurement):** Controlled native execution minimizing hypervisor and container overhead.
* **Granular Energy Accounting:** Separate tracking of inference energy, compilation, and execution costs with explicit provenance labels.
* **Seven Prompting Strategies:** From `zero_shot` baseline to multi-turn execution-guided refinement and tool-using agents.
* **Automated Secret Sanitization:** Built-in protection preventing API keys and tokens from appearing in console logs or artifacts.

---

## Quickstart

### 1. Install & Synchronize
```bash
uv sync --locked
```

### 2. Inspect Environment & Hardware Meters
```bash
uv run python run_leaf.py info
```

### 3. Validate Benchmark Configuration
```bash
uv run python run_leaf.py validate-config config/default_config.yaml
```

### 4. Build Documentation Locally
```bash
uv run mkdocs serve
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser to explore the live interactive documentation.

