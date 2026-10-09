---
name: relai-simulate
description: Use when measuring current agent behavior against RELAI agent tests, tags, or benchmarks.
---

# RELAI Simulation

Apply `references/proactive-decision-policy.md` and `references/relai-cli-commands.md` first. Simulation is the
targeted-measurement rung: run relevant grounded coverage when behavioral
validation is needed, not as a default for ordinary implementation work.

Use RELAI simulation when the goal is to measure current behavior against repeatable cases.

Good fits:

- The user wants to verify whether an agent currently passes known agent tests.
- A benchmark or tag should be run before deciding what to fix.
- A recent change needs behavioral validation beyond unit tests.
- Optimization should be preceded by a baseline measurement.

Before simulating, confirm the selected agent tests, tags, or benchmarks exist.
If required runtime env vars are missing, tell the user their names and that
they belong in `.relai/simulator.env` (loaded automatically; `relai init`
seeds their empty placeholders) or the shell environment; do not create, open,
or edit that file for them.

## Behavioral validation after coding work

After behavior-changing coding work and its deterministic tests, decide whether
the targeted-measurement rung applies. Do this before dispatching a simulation;
do not treat simulation as a default post-codecheck.

1. Inspect the completed change, its deterministic test coverage, current
   EvalsWiki grounding, and existing agent tests, evaluators, and
   benchmarks. Keep EvalsWiki reconciliation separate from simulation execution:
   reconcile it only when the decision ladder requires a durable-knowledge
   checkpoint, and do not use a simulation to perform that reconciliation.
2. If matching grounded coverage exists, reuse it. Prefer coverage newly
   updated by the change when it directly measures the changed behavior;
   otherwise select the smallest existing relevant agent test or
   benchmark sample. Do not create duplicate coverage or add unrelated cases
   just to run a simulation.
3. Select deterministically: name the exact agent test ID, tag, or benchmark
   ID and the resolved run count. Prefer `--tests <BEHAVIORAL_TEST_ID>` for
   one identified case; use a narrowly named `--tags <TAG>` or
   `--benchmarks <BENCHMARK_ID>` only when it is the grounded selector. Apply
   `--max-simulations <COUNT>` after resolution and deduplication when it
   bounds a multi-case selector. Do not use a broad tag, shuffle, a full suite,
   or a duplicate run merely because it is convenient.
4. If no applicable grounded coverage exists, or selectors/grounding cannot be
   determined safely, explicitly report the no-run or defer decision and why.
   State whether the next appropriate action is no RELAI action, a separate
   EvalsWiki checkpoint, or grounded-coverage work. Do not
   silently substitute unrelated or full-suite coverage.

## Running

Run the selected simulation without asking for confirmation. `relai simulate`
repairs malformed selected artifacts and simulator runtime failures
automatically within its own bounded retries; do not reimplement either repair
yourself.

For custom adapters, read `references/custom-adapter-contract.md`, pass
`--custom-tests` or `--custom-tags` with `--result-json`, and inspect the suite
JSON plus saved per-run results. Custom runs do not support outcome receipts or
the Harbor evaluator repair retry flow below.

For Harbor runs, pass `--outcome-json <runs>/simulation-outcome.json --outcome-invocation-id <opaque-id>`,
where `<runs>` is the project's CLI-managed runs directory (plus bounded
`--outcome-change` or `--outcome-intent` when useful). After the command exits,
read and summarize the versioned `relai.agent_simulation_outcome.v1` artifact,
including terminal failures and partial suites. Do not scrape or parse terminal
prose: it is human-facing and not the integration contract.

## Results

For each completed run, show what happened before its scores: read the run's
ATIF trajectory (the `trajectory.json` in that run's `local_artifact_paths`)
and present it turn by turn, for example `Turn 1 — user: … / agent: …`. Include
notable tool calls, and summarize long messages instead of quoting them in full.

When presenting results, distinguish these outcomes:

- A valid low score is behavioral evidence, not a simulator failure or a reason
  to retry/repair automatically.
- Evaluator errors are result-payload warnings. Report them separately; they
  are out of scope for runtime repair. Inspect the
  structured per-error `repair_decision`, never its message. Only one `repairable` grounded local global evaluator is eligible for automatic repair.
  Repair only a completed outcome with no blocking execution failures, one
  repairable evaluator source across all errors, and a positive
  `retry_constraints.remaining_retry_budget`.
  Preserve the initial artifacts and repair without a separate confirmation using
  `relai evaluator update --id <evaluator-id> --prompt <bounded failure context>
  --agent-interaction`; do not mutate evaluator files directly. Then run at
  most one `relai simulate --retry-from-outcome <initial-outcome>` with
  distinct `--outcome-json`, `--outcome-invocation-id`, and `--result-json`
  values. It
  reuses exactly the initial selector/control/environment-reference contract
  and refuses drift. Report both outcomes. A
  cancelled update or any non-repairable, stale, unavailable, inline,
  configuration, credential, or infrastructure attribution is terminal and
  non-mutating. Never broaden the retry to a suite or loop.
- A simulator subprocess, environment, or infrastructure failure is not a
  behavioral score. Report the final automatic runtime-repair outcome supplied
  by `relai simulate` (repaired and retried, repair failed, or retry exhausted)
  without reimplementing repair yourself. Runtime repair never fixes host
  problems such as Docker being unavailable; those follow the command
  reference's host-prerequisite guidance.
