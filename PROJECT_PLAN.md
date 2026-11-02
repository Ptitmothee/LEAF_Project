import pypandoc

english = r"""# PROJECT_PLAN.md — Detailed Specifications and Roadmap

This document complements the permanent instructions in `AGENTS.md`. Read it before implementing a feature and use its phases as a gradual roadmap.

## 1. Mission and Role of the Agent

Gradually build a reproducible research tool that investigates the energy cost of AI-assisted programming, distinguishing:
* The energy cost of generating code using AI models (across local and cloud models and several prompting strategies).
* The energy cost of compiling and executing the generated code across three programming languages: Python, C++, and Java.
* The functional performance and correctness of the generated solutions.

**Primary research objective:** determine the energy cost of executing AI-generated programs as accurately as possible, while minimizing measurement bias introduced by the execution environment and measurement infrastructure. Infrastructure overhead, virtualization, and measurement uncertainty must be characterized rather than silently included in the results.

You are the project's software engineer. Use this file as the enduring specification. Before coding, inspect the repository, summarize its state, and propose a limited step. Then work in testable increments. Do not build the entire system all at once. Preserve functions that have already been validated, document decisions, and report measurement limitations rather than hiding them.

**Scientific priority:** isolate the energy attributable to program execution. A precise-looking curve does not make an indirect measurement accurate. Measure what can be measured, label estimates and unknowns, and avoid conclusions that go beyond the data.

## 2. Questions the Project Must Answer

The scientific and mathematical formulation of the questions is expected to evolve as testing progresses, particularly when evaluating which formula best represents a given behavior. The tool must therefore be flexible enough to adapt the questions being investigated and the modeling formulas relatively easily.

1. How often does each model solve problems correctly?
2. What is the generation cost required to obtain a correct solution, including all attempts and corrections?
3. How much energy and time are required to compile and execute the correct solution?
4. How do results vary by language (Python/C++/Java), model, prompting strategy, and problem difficulty?
5. Do performance results differ between older problems, which may have appeared in training data, and problems published after the model's release date or declared knowledge cutoff?
6. How do these costs compare with a **high-uncertainty estimate** of human work without AI?

### Preliminary Methodological Question
* **MRQ — Measurement reliability:** How do execution environments and isolation mechanisms (native execution vs. Docker vs. virtual machines, OS distributions, background services) affect the accuracy, stability, and reproducibility of program energy measurements? *(This question validates the experimental protocol and may independently yield a methodological contribution, but is not the sole objective of LEAF).*

Metadata availability varies by source. Where legal and accessible, seek the problem statement, publication date, tests, one or more accepted human solutions, programming language, verdicts, and submission metadata, as well as human working time if it genuinely exists. Never invent a programming duration: a submission timestamp, contest duration, and program execution time are **not** the active time a person spent solving the problem.

## 3. Scientific Invariants to Respect

### 3.1 Separate Security Validation from Energy Measurement

The benchmark maintains two distinct execution workflows:

* **Workflow A — Security validation (`sandbox/`):**
  * Purpose: verify that potentially hazardous AI-generated code cannot compromise the benchmark infrastructure.
  * Execute generated code in hardened, disposable Docker containers and/or virtual machines.
  * Disable network access and access to sensitive host files.
  * Apply CPU, memory, process, and execution-time limits.
  * Test malicious and faulty programs (infinite loops, excessive RAM, unauthorized file/network access).
  * Validate cleanup and recovery.
  * *Security validation runs are not used to produce main energy measurements.*

* **Workflow B — Energy measurement (`runner/`):**
  * Purpose: estimate the energy attributable to the generated program while minimizing external overhead.
  * Use a controlled native execution environment whenever possible (or minimal, stable OS installation).
  * Avoid Docker and virtualization in the primary measurement configuration to prevent measurement bias.
  * Keep compilation, program execution, and environment setup separate.
  * Measure idle consumption, background baseline, repeat measurements, and report uncertainty.

The security-tested execution workflow and the energy-measurement workflow must remain logically separate.

### 3.2 Keep Energy Categories Separate

Record distinct categories; never reduce them to a single figure whose meaning is ambiguous:

- **Local inference:** energy used by the machine's CPU/GPU/RAM during generation, together with the method, duration, hardware, and uncertainty.
- **Cloud inference:** APIs often expose token counts, latency, and/or billed cost, but not the server's actual electricity consumption. Retrieve the official metrics that are available. Server energy remains `unknown` unless the provider publishes verifiable data or a documented estimation method is available. Never ask the model to guess the energy used by its own request.
- **Client energy during a cloud call:** optional measurement of the local computer while waiting/networking; this is NOT the inference energy of remote servers.
- **Compilation:** measure C++/Java compilation separately and, where relevant, environment preparation.
- **Execution:** measure program launch and execution energy separately from compilation. Also record elapsed time, CPU, memory, status, and number of tests.
- **Complete workflow:** it may be possible to sum the categories that were actually measured, alongside reported subtotals and clearly identified estimates. Do not present a partial sum as the complete cost.
- **Human reference:** report the computer's electrical energy separately from estimated metabolic energy. Specify whether metabolic power includes resting metabolism or measures only the additional expenditure. Do not combine them without explanation.

Each energy value must carry a provenance label: `measured` (instrumental measurement), `tool_estimate` (estimate from a tool such as CodeCarbon), `provider_reported`, `derived_estimate`, `proxy`, or `unknown`. Store the unit, method, tool version, range/error if known, and measurement conditions. If data is unavailable, use `null`/`unknown`, never zero.

### 3.3 Be Careful with Energy Measurement and Execution Environments

Energy measurements for short programs are noisy and may fall below the meters' resolution. Plan for calibration, repetitions, a stabilization period, idle measurements, and controlled repetition of the workload where necessary. Report the median, dispersion, and number of repetitions. Distinguish cold starts (JVM, model loading, GPU initialization) from warm operation. Repeating a workload in a loop can change caching and behavior; document the protocol.

CodeCarbon can be used as an initial implementation, but it provides estimates whose accuracy depends on the platform and hardware. Its `process` mode is a software-based attribution, and GPU energy may be reported at device level; therefore, do not claim that this value is a perfect per-program measurement. Provide an extensible interface for hardware/OS energy counters where available.

However, before selecting the primary measurement environment, evaluate the influence of:
* Native Windows, Linux, and macOS execution where hardware is available.
* Different Linux distributions (lightweight vs. complete).
* Native execution versus Docker versus virtualized execution.
* Background services and idle power consumption.

A Linux distribution or environment must not be assumed more efficient without experimental verification. Provide an extensible interface for hardware/OS energy counters where available.

### 3.4 Be Careful When Investigating the Models' “Memory Effect”

A problem's age is an **indicator of potential contamination**, not proof that the model saw it during training or memorized it. For each model, store the release date, exact version, and declared knowledge-cutoff date if available, together with the source and confidence level. Compare cohorts defined before the experiment: problems before the known cutoff, problems published after the model's release, and, optionally, an intermediate/uncertain period. Preserve the actual dates and make it possible to rerun the filters.

At a minimum, measure accuracy, compilation rate, test-passing rate, and success per problem. A performance drop on recent problems may reflect differences in difficulty, styles, languages, or test quality; match or stratify cohorts by difficulty, tags, statement length, and source where possible. Do not conclude that memorization occurred without additional evidence and an analysis of limitations.

### 3.5 Fair Comparison of Strategies

The benchmark must support the following prompting strategies, ordered by their expected solution accuracy, from lowest to highest. This is a working hypothesis, not a guaranteed ranking: actual performance may vary by model, problem, language, and resource budget.

1. **`zero_shot`** — Directly generates a solution from the problem statement in a single model call, without explicit intermediate reasoning, examples, or refinement. Serves as the baseline.

2. **`chain_of_thought`** — Instructs the model to analyze the problem, identify an algorithm, consider edge cases, and then produce the final solution. Measures the impact of explicit reasoning-oriented instructions.

3. **`chain_of_draft`** — Uses two distinct generation stages: the model first produces a concise draft describing its approach, then generates the final implementation using that draft. Measures the impact of separating planning from implementation.

4. **`self_refinement_NL`** — Iteratively improves an initial solution using natural-language self-critique and revision, without execution feedback. Measures the benefits of explicit review and refinement.

5. **`self_refinement_Exec`** — Iteratively improves a solution using feedback from compilation, execution, and evaluation against an authorized test set. Measures the benefits of execution-guided debugging and correction.

6. **`self_refinement_Exec_NL`** — Combines execution-guided refinement with explicit natural-language critique: the model analyzes execution feedback, identifies likely causes of failure, and produces a revised solution. Measures whether explicit critique improves upon execution feedback alone.

7. **`agent`** — Uses a controlled, iterative tool-calling workflow in which the model can plan, inspect authorized tool outputs, compile or execute candidate solutions, and adapt its approach until success or a predefined budget limit. The available tools, interaction policy, and resource budgets must be specified precisely.

**Experimental requirements:**
- Treat this ordering as a hypothesis to investigate, not an assumed result. In particular, `agent` may outperform or underperform the refinement strategies depending on its configuration.
- Define each strategy as a reproducible experimental configuration with explicit rules for generation, feedback, iteration, and termination.
- Enforce separate inference and execution budgets, and record all model calls, generated tokens, iterations, compilations, and executions.
- Keep the final evaluator and hidden tests inaccessible to the model.
- Report success rate alongside resource consumption, including cost per attempted problem and cost per successfully solved problem.
- Where strategies overlap, document their precise configurations and use controlled ablation experiments to isolate the contribution of each component.

Evaluate the **total cost per correct solution**, not just the cost of a single response. Record every call, code version, feedback item received, test run, and cumulative cost. Also compare cost per attempt and cost per problem, so that strategies using more iterations are not artificially favored. The prompt must never contain hidden tests or the reference solution.

## 4. Data Sources: Strategy and Constraints

Create interchangeable adapters rather than a single scraper. Start with an already structured data source to obtain a reproducible prototype, then expand. Sources to investigate:

- **CodeContests (Google DeepMind):** problems, tests, and correct/incorrect human solutions in several languages. The repository indicates that the dataset was used for AlphaCode, making it particularly useful for illustrating a corpus that a model may have encountered, but not for concluding that every model has seen it.
- **LiveCodeBench:** problems collected over time from multiple platforms, with versions that can be filtered by period; useful for structuring temporal evaluation and reducing contamination risks.
- **Codeforces API:** problem, contest, ranking, and public-submission metadata, depending on the permitted methods. Respect the API's stated limit (no more than one request every two seconds), cache results, and do not assume the public API provides source code for every submission.
- Any other source (AtCoder, etc.) must be evaluated according to its terms of use, licenses, technical limits, and redistribution options.

Document the source, original URL/identifier, collection date, license/terms, transformations applied, and checksum of the raw file. Do not bypass authentication, rate limits, or access restrictions; do not collect or publish unnecessary personal data. If source code or human working time cannot lawfully be obtained or is inaccessible, retain the available metadata and explain the limitation.

Distinguish between:
- problem creation/publication date;
- date and time of the human submission, if known;
- official solution execution time;
- time spent by the participant on the problem, if actually provided;
- participant rank/score/acceptance;
- dataset capture/import date.

Do not call a solution the “best solution” without a criterion. Configure the criterion: official/reference solution, fastest accepted solution in a given environment, or a solution submitted by the highest-ranked participant accessible. Preserve the criterion and provenance. Human reference performance is comparable to AI execution only if the environment, compiler, constraints, and tests are sufficiently aligned.

## 5. Target Architecture

Build an application primarily in Python for orchestration, adapters, analysis, and charts. Measurement and execution must remain decoupled from model calls.

Suggested logical modules:

- `datasets/`: source connectors, normalization, temporal filters, schema validation;
- `models/`: common interface and adapters for cloud APIs and local models;
- `prompts/`: versioned templates and strategies;
- `generation/`: orchestration, iteration budgets, version history;
- `sandbox/`: isolated execution in hardened containers/VMs for security validation;
- `runner/`: controlled native execution for energy experiments;
- `measurement/`: energy meters, timing, idle power, measurement quality, and calibration;
- `evaluation/`: tests, verdicts, compilation/correctness checks, comparison with reference;
- `storage/`: configuration, SQLite initially, JSONL/CSV export;
- `analysis/`: statistical aggregation and charts;
- `cli/`: launch ingestion, validation, pilots, and complete experiments;
- `tests/` and `docs/`.

Prefer a common `ModelAdapter` interface that returns generated text, exact model identifier/version, latency, input/output/reasoning/cache tokens if exposed, billed cost if calculable, request ID, status, and sanitized raw metadata. An adapter must not invent missing fields.

An experimental run must be reconstructible from its configuration: `experiment_id`, tool commit/version, date, hardware/OS, container images and compiler/runtime versions, dataset/version, problem, model/version, language, prompt/strategy/version, sampling parameters, seed if possible, budgets, repetitions, and measurement methods.

## 6. Minimum Data Schema

Define and document typed, validated, versioned schemas. At a minimum:

**Problem**: `problem_id`, `source`, `source_id`, `source_url`, `title`, `statement`, `input_spec`, `output_spec`, `constraints`, `tags`, `difficulty` (and method/source), `published_at`, `contest_at`, `dataset_captured_at`, `temporal_cohort`, `license`, `tests_available`, `test_provenance`, `reference_solutions[]`, `human_time_value`, `human_time_semantics`, `human_time_source`, `metadata_raw`.

**ReferenceSolution**: code source, language, known acceptance status, author/rank if publishable and useful, official memory/CPU time if known, timestamp, and selection criterion. Do not treat a platform's displayed runtime as comparable without local recalibration.

**ModelSpec**: provider, display name, API identifier or local path, version/snapshot, cloud/local mode, release date, declared knowledge date, sources for these dates, parameters, limits, and ability to provide tokens/cost/energy measurements.

**Run/Attempt**: `run_id`, `experiment_id`, `problem_id`, `model_spec_id`, strategy, language, attempt number, parent/previous attempt, prompt hash + version, timestamps, raw response text, extracted code, parsing errors, token/cost/latency telemetry, code versions, feedback visible to the model, compilation/test results, stop reasons, and remaining budgets.

**Measurement**: measured phase, energy in joules or Wh, method and quality label, time, average power if available, CPU/GPU/RAM, temperature/system state if accessible, reference idle level, repetitions, dispersion, tool version, limitations/errors.

Store raw data append-only as far as possible. Aggregates can be recalculated. Use schema migrations, stable keys, and a cache whose key includes the exact model, prompt, parameters, and problem hash. API keys/secrets must never appear in results or logs.

## 7. Mandatory Security and Isolation: Two Distinct Workflows

Generated code is untrusted, even if the model is reputable. Run it only in a dedicated sandbox or controlled runner, never directly in the orchestrator process. To avoid virtualization overhead biasing primary energy measurements, the benchmark strictly separates security validation from energy measurement:

* **Workflow A — Security validation (`sandbox/`):**
  * Pinned, hardened, disposable containers (or VMs) for Python, C++, and Java; record versions.
  * Non-privileged user, read-only root filesystem where possible, disposable temporary directory, no mounts of the home directory, API keys, Docker sockets, or sensitive host files.
  * Network disabled while compiling/executing snippets; no on-the-fly dependency installation.
  * CPU, RAM, process, file-size, stdout/stderr, compilation-duration, and per-test duration limits.
  * Handle segmentation faults, infinite loops, deadlocks, OOM, timeouts, and excessive output; kill the entire process group when a timeout expires.
  * A failing test or compilation failure must not interrupt other experiments.
  * Never allow an agent to modify the evaluator, reference tests, or orchestration code during a run.
  * *Security validation runs verify program safety and are not used to produce main energy measurements.*

* **Workflow B — Energy measurement (`runner/`):**
  * Execute candidate programs in a controlled native environment (or minimal OS installation) to eliminate Docker and hypervisor measurement bias.
  * Record compilation, runtime setup, and program execution separately.
  * Apply resource limits and process group termination to prevent runaway processes.

On Windows, validate the isolation capabilities actually enabled in the environment; do not assume that an IDE's sandbox mode automatically protects a program launched by the benchmark.

## 8. Human Cost Measurement: An Explicit Model, Not False Precision

Implement several configurable scenarios rather than a single human result:

1. **Documented human time:** use only active time actually provided by a reliable source. Otherwise, mark it missing.
2. **Estimated human time:** if necessary, use difficulty groups or an independent human pilot study; publish the method and range, not a pseudo-exact measurement.
3. **Computer electricity:** `average power in watts × duration in seconds`, with a scenario for total active power and, separately, incremental power relative to idle (`P_active - P_idle`) if measured.
4. **Human metabolism:** a separate scenario with a range of metabolic power and duration. Explain whether the estimate includes resting metabolism. Total metabolic power must not be described as additional expenditure caused entirely by the problem.
5. **Uncertainty:** generate low/central/high scenarios from configured assumptions. Perform sensitivity analysis; if human duration is unknown, show an illustrative range and do not rank models based on this figure alone.

Do not combine measured electrical energy and estimated metabolic energy in the same chart without explicit colors/legends and annotations. Human comparisons are exploratory and must be presented as such in the report.

## 9. Mandatory Roadmap: Proceed in Stages

Do not move to the next stage until the exit criteria for the current stage are satisfied, unless an explicitly documented decision says otherwise. Each stage must produce a small change, tests, documentation, and a summary of what remains.

### Phase 0 — Repository reconnaissance and planning
- Inspect the existing project, environment, and dependencies.
- Review available measurement tools, OS, virtualization capabilities, and hardware energy counters.
- Establish the initial experimental protocol.
- Deliver an inventory and detailed implementation plan.
- **Exit criterion:** architecture and initial methodology defined.

### Phase 1 — Project skeleton
- Finalize the Python environment, dependency management, and module structure.
- Configure logging (with secret sanitization), CLI, unit tests, and default configuration without secrets.
- Establish documentation and version control conventions (ADRs).
- **Exit criterion:** clean installation and basic tests pass on the target machine.

### Phase 2 — Data schemas and synthetic dataset
- Implement versioned schemas for problems, models, attempts, runs, and measurements.
- Create 3–5 synthetic problems with small tests (solved, failed, timeout, memory limit).
- Add validators, JSONL/CSV exports, and round-trip tests.
- **Exit criterion:** a complete offline workflow can be tested without external APIs or datasets.

### Phase 3 — Measurement environment investigation
*(Moved ahead of the execution runner because the measurement environment directly influences runner design).*
- Identify available hardware energy counters and software measurement tools; evaluate resolution and limitations.
- Compare idle power, background activity, and known workloads.
- Investigate native execution on available operating systems (Windows, Linux, macOS).
- Compare selected native, Docker, and virtualized configurations to quantify virtualization overhead and measurement bias.
- Evaluate lightweight versus complete Linux installations.
- Select a primary execution configuration.
- **Exit criterion:** documented measurement environment and protocol, with known limitations and justification for the selected configuration. *(Potential independent output: methodological paper on the influence of execution environments and isolation mechanisms on software energy measurements).*

### Phase 4 — Security sandbox validation
- Configure Docker and/or disposable virtual machines for hardened execution.
- Implement security configurations: unprivileged user, read-only filesystem where possible, network disabled, CPU/RAM/process/output limits.
- Test malicious and faulty programs (infinite loops, memory bombs, unauthorized file access, network attempts).
- Verify cleanup and recovery after termination.
- **Exit criterion:** security configuration passes all isolation tests. *(Note: energy measurements from this phase are not used in the main benchmark).*

### Phase 5 — Native execution runner
- Implement execution runners for Python, C++, and Java with pinned compiler/runtime versions.
- Separate extraction, compilation, execution, evaluation, and cleanup.
- Apply execution limits, Unicode/line-ending handling, and robust process termination.
- Ensure the runner can execute within the selected primary measurement environment.
- **Exit criterion:** successful, failed, timed-out, and crashed programs are handled correctly across all three languages.

### Phase 6 — Energy measurement implementation
- Implement a measurement interface independent of the execution runner.
- Integrate available hardware (e.g. NVML, RAPL where accessible) and software measurement methods.
- Measure idle consumption, empty commands, and known workloads; evaluate startup energy vs. warm-operation.
- Implement repetitions, calibration, baseline subtraction, and uncertainty reporting.
- Detect measurements below the available resolution (`below_resolution`).
- **Exit criterion:** documented and validated measurement procedure on the selected hardware.

### Phase 7 — Dataset integration
- Select an initial structured dataset (e.g. CodeContests or LiveCodeBench selection).
- Implement connector with local caching, rate limits, retries, source attribution, licenses, and collection dates.
- Validate problem statements, tests, languages, duplicates, reference solutions, and input/output consistency.
- Explicitly record missing fields, building a metadata coverage report.
- **Exit criterion:** a small versioned batch can be imported, validated, and replayed offline.

### Phase 8 — Model adapters and inference accounting
- Define the common `ModelAdapter` interface: deterministic mock mode, then local model, then cloud providers.
- Collect telemetry from API responses: tokens (input/output/reasoning/cache), latency, model version, billed cost, request ID.
- Keep server energy for cloud models marked `unknown` unless verifiable data exists; measure client local energy separately.
- Handle timeouts, quotas, 429 rate limits, retries, cancellation, maximum cost budgets, and cost-free dry-runs.
- **Exit criterion:** the same experiment can use mock, local, and cloud models without changing the orchestrator.

### Phase 9 — Prompting strategies and generation workflow
- Implement and version the seven strategies in Section 3.5 (`zero_shot` to `agent`).
- Set request, token, cost, time, and correction budgets for each strategy.
- For every call, record exact prompt (or hash), output, extracted code, tokens, costs, and feedback visible to the model.
- Keep hidden tests and reference solutions inaccessible to the model.
- **Exit criterion:** every generation experiment is reconstructible and has an explicit outcome.

### Phase 10 — Integrated pilot
- Combine dataset, generation, execution, evaluation, and measurement with unique run IDs.
- Run a small selection of problems (5–10) with mock/local models, verifying the complete workflow.
- Ensure security validation and energy measurement remain strictly separate.
- Test resumption of interrupted experiments and cost controls.
- **Exit criterion:** an end-to-end experiment can be completed, traced, and reproduced without silent loss or budget overruns.

### Phase 11 — Main benchmark
- Expand the problem dataset; evaluate multiple models, languages, and prompting strategies with sufficient repetitions.
- Collect generation, compilation, and execution costs separately.
- Analyze correctness, energy, latency, and performance trade-offs.
- Compare cost per submitted problem AND per correctly solved problem.
- **Exit criterion:** sufficient experimental data to address RQ1 and RQ2.

### Phase 12 — Human reference and overall analysis
- Establish documented or estimated human programming-time scenarios with uncertainty ranges.
- Keep electrical and metabolic energy strictly separate.
- Perform sensitivity analysis; combine generation and execution costs where data permits.
- Address RQ3 and identify the limits of the comparison.
- **Exit criterion:** main research questions addressed with traceable measurements and explicit uncertainty.

### Phase 13 — Replication and publication
- Add recovery tests, sandbox security audits, schema migrations validation.
- Replay a pinned experiment; confirm results fall within expected tolerances.
- Generate experiment manifest, dataset versions, checksums, dependencies, raw data, and final report.
- Document biases, impossible measurements, corpus coverage, tested models, financial costs, and reproduction conditions.
- **Exit criterion:** experimental protocol and results are sufficiently documented for independent reproduction.

## 10. Software Quality and Tests Not to Forget

- Unit tests for schemas, unit conversions (J ↔ Wh, W × s), costs, budgets, and temporal cohorts.
- Contract tests for each provider, including missing token fields, interrupted responses, renamed models, and API errors.
- Connector reliability tests: duplicates, pagination, cache, HTTP 429, invalid data, schema changes, and retries.
- Runner tests: failed compilation, wrong output, empty output, timeout, OOM, crash, Unicode, large stdout, cleanup after termination.
- Contamination tests: the prompt contains neither private tests nor the reference solution; the agent cannot modify the evaluator.
- Aggregation tests: failed runs remain counted, `unknown` values never become zero, and every chart exposes `n`.
- Full offline smoke test using the synthetic dataset; optional API integration tests enabled only when keys and a budget are configured.
- Statistical stability tests: repeat energy measurements several times, check variance/time, and detect an overloaded machine.

## 11. Antigravity Working Rules

1. **One stage at a time.** For a broad request, propose the smallest next increment that makes a capability usable. Do not jump directly to a complete application.
2. **Read before modifying.** Inspect files, tests, configuration, and relevant history. Do not overwrite existing work without understanding its role.
3. **Plan, then code.** State the files to change, intended behavior, risks, and exit test. For small changes, the plan can be brief.
4. **Actually test.** Run the relevant tests and provide commands and results. Never claim success if tests were not run.
5. **Update documentation.** Record every structural decision or measurement limitation in `docs/` or an ADR.
6. **Avoid unnecessary dependencies.** Justify dependencies and pin versions required for reproducibility.
7. **Do not hide uncertainty.** Preserve `unknown`, `null`, errors, and missing data. Never turn an unavailable measurement into zero.
8. **No costly calls without configuration.** Default tests must be offline/mock-based. Cloud calls and large downloads require visible configuration and budgets.
9. **Separate orchestration from untrusted execution.** The orchestrator must never launch model-generated code directly.
10. **At the end of each phase,** summarize what was done, files modified, tests run/results, known limitations, and the suggested next phase. Do not launch a long real experiment without first presenting the planned budget.

## 12. Project Success Criteria

LEAF should ultimately provide:

1. A reproducible benchmark for AI-assisted code generation and execution.
2. A measurement protocol designed to isolate program execution energy.
3. A separately validated security mechanism for executing untrusted generated code.
4. Comparisons across models, prompting strategies, and programming languages.
5. A transparent accounting of generation, compilation, and execution costs.
6. Statistical results with documented uncertainty and limitations.
7. An experimental dataset and analysis pipeline that can be independently reproduced.

The comparison of operating systems and execution environments is primarily a methodological contribution supporting the reliability of the main benchmark, rather than its central scientific result.

## 13. Initial Technical References to Verify During Implementation

APIs, licenses, limits, and prices may change: revalidate official documentation at the start of each connector implementation and record the verification date.

- Antigravity — project rules `AGENTS.md` / `GEMINI.md`: https://antigravity.google/docs/rules/
- Codeforces API and limits: https://codeforces.com/apiHelp/ and https://codeforces.com/apiHelp/methods?locale=en&mobile=true
- CodeContests (problems, tests, and human solutions): https://github.com/google-deepmind/code_contests
- LiveCodeBench (temporal problems and dataset versions): https://github.com/LiveCodeBench/LiveCodeBench
- CodeCarbon — configuration and interpretation of measurements: https://docs.codecarbon.io/latest/how-to/configuration/
- CodeCarbon — CLI command tracking: https://docs.codecarbon.io/latest/tutorials/cli/
- OpenAI — token usage fields by API: https://help.openai.com/en/articles/10478918-reviewing-api-usage-and-costs
"""

out = "/mnt/data/PROJECT_PLAN_EN.md"
pypandoc.convert_text(english, "md", format="md", outputfile=out, extra_args=["--standalone"])
print(f"Created {out}")
