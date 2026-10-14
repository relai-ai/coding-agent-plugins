---
name: relai-benchmark
description: Use when the user has a CSV benchmark, with optional evaluator references or prompt guidance, that should become a RELAI benchmark.
---

# RELAI Benchmarks

Use a RELAI benchmark when the user has CSV-backed benchmark data to register for repeatable evaluation.

Good fits:

- A CSV or dataset represents repeated inputs, personas, tasks, or regression cases.
- The CSV benchmark should be reused across simulation and optimization runs.
- Optional evaluator references or prompt guidance should help score benchmark samples.

Prefer an agent test instead when the issue is one concrete observed failure or one specific behavior to preserve.

Before registering a benchmark:

- Check that the CSV shape is intentional and has no data rows without values;
  registration refuses them because each data row becomes one sample.
- Pass an evaluator the user wants applied with `--evaluator-ref`; it must be a
  file inside the repository, so copy an external evaluator in first.
- In a multi-target repository, identify the intended registered target before registering the benchmark.
- Do not search, dump, or edit the Wiki yourself; the benchmark workflow reads its own grounding.
- Use `relai benchmark register --help` through the `relai-cli` skill before constructing the command.
- Confirm with the user before `relai benchmark remove`; it deletes the benchmark.

After `relai benchmark register` or `relai benchmark update` completes, read the benchmark's EvalsWiki page (`.relai/evals-wiki/tests/benchmarks/<id>.md`) and summarize it: its ID and what it measures (Description) in one sentence, its coverage (Coverage and sample mapping) and sample count (Dataset), and one "passes when" line from Evaluation criteria. For an update, say what changed.
