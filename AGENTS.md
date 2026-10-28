# AGENTS.md — Permanent Project Instructions

## Mission

Gradually build a reproducible research tool that compares the energy cost of AI inference and generated-code execution across multiple local/cloud models, several prompting strategies, and three programming languages: Python, C++, and Java. The project must ingest annotated programming problems, query models, attempt to validate their solutions in an isolated environment, measure the costs that are available, analyze the results, and produce charts. It must compare older and newer datasets without claiming to demonstrate memorization based on problem age alone, and then provide an estimate of a human-only scenario.

**Before implementing anything, read `PROJECT_PLAN.md` at the project root.** It contains the detailed scientific specifications, minimum schemas, development phases, tests, and initial references. This file contains the rules that remain active at all times. If a specific request conflicts with the scientific or security invariants below, flag the conflict before proceeding.

## Working Rules

1. **Proceed in small increments.** First inspect the repository, code, tests, dependencies, and environment. Propose the smallest useful step, identifying the affected files and validation criteria. Do not attempt to program the entire system at once.
2. **Actually run tests.** Run the relevant tests, report the commands and their results, and never claim that a test passes unless it has been run. Default tests must work offline with synthetic data or mock models.
3. **Preserve existing work.** Understand files before replacing them. Document architectural decisions, schema changes, and limitations in `docs/` or an ADR.
4. **Reproducibility first.** Record model, dataset, prompt, compiler/runtime, environment, configuration, and measurement-tool versions. Cache reusable data using a stable key that includes the relevant parameters. Store raw data and recompute aggregates.
5. **No hidden calls or costs.** Cloud API calls, large downloads, and long experiments must be optional, configured with explicit budgets, and preceded by a `dry-run` when useful. Never put secrets in the repository, logs, or results.
6. **Modularity and lean dependencies.** Separate data collection, generation, model adapters, sandbox, measurement, evaluation, storage, and analysis. Justify new dependencies and pin versions when needed for reproduction. Make sure to build the tool as easy to maintain and refactor as possible, using pipelines and classes.
7. **Never conceal an unknown.** An unavailable measurement must be `null`/`unknown`, never zero. Preserve failures and missing data. Always distinguish instrumental measurements, tool estimates, provider-reported values, derived approximations, and proxies.
8. **At the end of each increment:** summarize what was done, which files were changed, which tests were actually run, the remaining limitations, and the recommended next step. Do not launch a large experiment without first specifying its costs and budgets. Write a clear commit message to incrementally update the project on github.

## Scientific Invariants

### Inference energy and execution energy are not the same thing

- **Local model:** measure the machine's energy consumption during inference as far as possible, and document the hardware, method, and limitations.
- **Cloud model:** collect available official metrics—input/output tokens and, if exposed, reasoning/cache tokens, latency, model version, billed cost, or request ID. APIs do not necessarily expose the server's electrical energy consumption. Until a documented provider measurement or a reliable estimation method is available, mark server energy as `unknown`. Never ask the model to invent the energy consumed by its request.
- Electricity consumed locally while waiting for a cloud API belongs to the **client**, not to the remote server's inference energy.
- Measure environment setup, compilation (especially for C++/Java), and program execution separately. The “total cost” must specify which components are measured, estimated, or unknown.
- CodeCarbon is a starting option, not ground truth: its accuracy depends on the hardware and tracking mode; `process` is a software-level attribution, and GPU measurement may be device-level. Test measurement resolution before measuring very short snippets. Calibrate idle consumption, repeat measurements, report the median and dispersion, and distinguish cold starts from steady-state runs. If the signal is too weak, report that rather than manufacturing precision.

### Datasets and potential contamination

- Prefer a structured, versioned dataset first, then add platform/API adapters. Possible sources include CodeContests (problems, tests, and human solutions; used for AlphaCode), LiveCodeBench (time-indexed problems), and the Codeforces API (public metadata depending on the endpoints). Verify licenses/terms, dates, and official limitations during implementation; respect rate limits and implement caching and retry-on-error. Do not assume that the public API provides the full source code of submissions.
- Store the problem publication date, submission date, program execution time, contest duration, and active human working time separately. These concepts are not interchangeable. Never invent a programming time that is not available.
- Store the source, identifier/URL, collection date, license, hash, transformations, raw data, and provenance of the reference solution. Explicitly define what “best solution” means: official reference, fastest accepted solution, highest-ranked accessible participant, etc.
- A problem's age indicates only a **possibility** of contamination. For each model, record its exact version, release date, and knowledge cutoff if known, together with the source and confidence level. Compare time periods defined in advance, treat uncertain cases separately, and control for difficulty, tags, length, and source as far as possible. Worse performance on recent problems does not prove that older problems were memorized.

### Prompting strategies

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

Log every call, code version, test, and feedback item. Evaluate the **cumulative cost required to obtain a correct solution**, as well as the cost per attempt and per submitted problem. Never send the reference solution or hidden tests to the model. Make strategies comparable through explicit budgets and document their differences.

### Untrusted execution: mandatory security

Generated code is untrusted. Never execute it directly in the orchestrator process. Use a sandbox (ideally a reproducible container) with an unprivileged user, limits on time/CPU/RAM/processes/output, networking disabled, a disposable temporary workspace, and no access to secrets, the home directory, the container engine socket, or sensitive host data. Do not install dependencies on the fly. On timeout, terminate the entire process group. Test infinite loops, crashes, OOM conditions, excessive output, forbidden file access, and network attempts. Never allow the agent to change the evaluator or reference tests.

On Windows, verify that isolation is actually active: do not assume the IDE's sandbox automatically protects a program launched by your tool.

## Expected Architecture

Use Python primarily for orchestration and analysis. Maintain clear boundaries between:

- `datasets/`: collection, caching, normalization, and time-based cohorts;
- `models/`: common adapter interface for local/cloud models;
- `prompts/` and `generation/`: versioned prompts, attempts, and budgets;
- `sandbox/`: extraction, compilation, and isolated execution for Python/C++/Java;
- `measurement/`: energy, latency, idle power, and measurement quality;
- `evaluation/`: tests, verdicts, and comparison against references;
- `storage/`: SQLite initially, plus JSONL/CSV export;
- `analysis/`: statistics and charts;
- `tests/`, `docs/`, CLI/configuration.

Every run must be reconstructable from an ID and the complete configuration: problem hash/source, dataset/version, model/version, prompt/strategy/version, language, parameters, budgets, repetitions, hardware/OS, container image, and tool versions. A common model interface must preserve raw text, extracted code, latency, token usage, and costs only when provided by the API or calculable from a dated price schedule. Provide for timeouts, network errors/429 responses, quotas, cancellation, resumption, and cost limits.

## Human Baseline: Exploratory Result

Estimate separately: (a) the computer's electrical energy (active power × duration, and optionally incremental power relative to idle), (b) metabolic energy using explicit assumptions, and (c) uncertainty in working time. Use an observed value only if a reliable source actually provides active human working time; otherwise, use several low/central/high scenarios. Resting metabolism must not be presented as additional energy expenditure caused by the problem. Do not combine electrical and metabolic energy into an opaque score or a chart without visually and methodologically distinguishing them.

## Development Order

Follow the phases detailed in `PROJECT_PLAN.md`:

0. repository inspection and plan;
1. skeleton/CI/tests/configuration;
2. schemas and a small synthetic dataset;
3. sandbox and Python/C++/Java evaluator;
4. calibration and energy measurement bench;
5. first dataset connector;
6. model adapters and telemetry;
7. iteration strategies;
8. end-to-end pilot;
9. time-based cohorts;
10. statistics and charts;
11. human baseline;
12. security, replication, and publication.

Do not start with a large scraper, a complex UI, or expensive experiments. First make the synthetic, offline workflow reliable and tested.

## Minimum Quality Criteria

- Unit tests for schemas, J↔Wh conversions, costs, budgets, and time filters.
- API contract tests (missing tokens, interrupted calls, model changes, 429 errors) and collection tests (cache, pagination, duplicates, invalid data).
- Sandbox tests (invalid compilation, wrong output, timeout, crash, excessive RAM/output, cleanup).
- Automatic checks that prompts and feedback do not contain the reference solution or private tests.
- Failures remain in the statistics; `unknown` never becomes zero; all charts show `n`, units, successes, and missing data.
- Evaluate cost per submitted problem **and** per solved problem; otherwise, fast failures can make an underperforming model appear artificially inexpensive.
- Complete offline tests; real API tests are optional and enabled only with keys and an explicit budget.

## Official References to Recheck During Implementation

Prices, versions, APIs, and limits change. Verify the official pages and record the date:

- Antigravity rules (`AGENTS.md`): https://antigravity.google/docs/rules/
- Codeforces API: https://codeforces.com/apiHelp/ and https://codeforces.com/apiHelp/methods?locale=en&mobile=true
- CodeContests: https://github.com/google-deepmind/code_contests
- LiveCodeBench: https://github.com/LiveCodeBench/LiveCodeBench
- CodeCarbon: https://docs.codecarbon.io/latest/how-to/configuration/ and https://docs.codecarbon.io/latest/tutorials/cli/
- OpenAI usage telemetry: https://help.openai.com/en/articles/10478918-reviewing-api-usage-and-costs
