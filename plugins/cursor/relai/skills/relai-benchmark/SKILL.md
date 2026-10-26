---
name: relai-benchmark
description: Use when the user has a CSV benchmark, with optional evaluator references or prompt guidance, that should become a RELAI benchmark.
---

# RELAI Benchmarks

Use a RELAI benchmark when the user has CSV-backed benchmark data to register for repeatable evaluation.

If `command -v relai` finds nothing, use the `relai-cli` skill to install the CLI and sign in before continuing.

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
- Benchmark tags (in `benchmark.toml`) select the benchmark with `--tags`. When optimizing, each sample is grouped only by `benchmark-<id>` and `benchmark-<id>-sample-<index>`.
- Confirm with the user before `relai benchmark remove`; it deletes the benchmark.

After `relai benchmark register` or `relai benchmark update` completes, read the benchmark's EvalsWiki page (`.relai/evals-wiki/tests/benchmarks/<id>.md`) and summarize it: its ID and what it measures (Description) in one sentence, its coverage (Coverage and sample mapping) and sample count (Dataset), and one "passes when" line from Evaluation criteria. For an update, say what changed.
