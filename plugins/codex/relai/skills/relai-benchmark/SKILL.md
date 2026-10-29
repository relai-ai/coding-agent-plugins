---
name: relai-benchmark
description: Use when the user has a CSV benchmark, with optional evaluator references or prompt guidance, that should become a RELAI benchmark.
metadata:
  relai-cli-version: "0.2.15"
  relai-skills-revision: "17c39e03dcd25819"
---

> **RELAI version check.** This skill matches skills revision `17c39e03dcd25819` (RELAI CLI 0.2.15). Once per session, before following it, run `relai guide --revision`:
>
> - Same `skills_revision`: follow this skill as written.
> - Different `skills_revision`: run `relai guide relai-benchmark --agent codex` and follow its output instead of this file; the user does not need to do anything. If the printed `cli_version` is older than 0.2.15, suggest `relai update` once so they also get this plugin's newer features.
> - `relai guide` is not a command: this RELAI CLI predates the check. Ask the user to run `relai update`, then continue.
> - `relai guide` fails any other way, for example on an unknown workflow: follow this skill as written and tell the user the error once.

# RELAI Benchmarks

Use a RELAI benchmark when the user has CSV-backed benchmark data to register for repeatable evaluation.

If `command -v relai` finds nothing, use the `relai-cli` skill, which asks the user to install the CLI and then signs in, before continuing.

Good fits:

- A CSV or dataset represents repeated inputs, personas, tasks, or regression cases.
- The CSV benchmark should be reused across simulation and optimization runs.
- Optional evaluator references or prompt guidance should help score benchmark samples.

Prefer an agent test instead when the issue is one concrete observed failure or one specific behavior to preserve.

Before registering a benchmark:

- Check that CSV headers are nonempty and unique and that no data rows lack
  values; registration refuses these inputs to preserve every column value
  and avoid empty samples. Repair an existing dataset with
  `relai benchmark update --id {id} --csv {path} --prompt "Use the corrected column names."`.
- Pass an evaluator the user wants applied with `--evaluator-ref`; it must be a
  file inside the repository, so copy an external evaluator in first.
- Registration and update candidates materialize a representative sample and
  resolve evaluators through the same path as simulation and optimization.
  Treat an invalid or missing `evaluator_refs` ID, a scope mismatch, or a
  collision with an inline evaluator as a publication failure. An existing
  registered package remains readable so `benchmark update` can repair it;
  only the replacement must pass the current check.
- In a multi-target repository, identify the intended registered target before registering the benchmark.
- Do not search, dump, or edit the Wiki yourself; the benchmark workflow reads its own grounding.
- Use `relai benchmark register --help` through the `relai-cli` skill before constructing the command.
- Benchmark tags in `benchmark.toml` must include a requirement- or risk-based tag and select the benchmark with `--tags`. The manifest’s `[sample_tags]` table stores tags by zero-based row index, including `benchmark-<id>` and `benchmark-<id>-sample-<index>` for every row. Row-specific tags can group related cases. Optimizer scheduling and memory use both shared and row-specific tags, independently of task-template tags.
- Confirm with the user before `relai benchmark remove`; it deletes the benchmark.

After `relai benchmark register` or `relai benchmark update` completes, read the benchmark's EvalsWiki page (`.relai/evals-wiki/tests/benchmarks/<id>.md`) and summarize it: its ID and what it measures (Description) in one sentence, its coverage (Coverage and sample mapping) and sample count (Dataset), and one "passes when" line from Evaluation criteria. For an update, say what changed.
