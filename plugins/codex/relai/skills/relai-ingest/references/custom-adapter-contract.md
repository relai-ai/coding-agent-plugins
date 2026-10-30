# Custom adapter contract

Use this reference when a user wants to create or run a project-owned custom
adapter. Confirm the project has `.relai/config.toml`; `relai init --bare`
creates minimal state without Harbor. An existing Harbor project may add an
adapter without changing its runtime. Do not require `.relai/harbor/` for a
custom-only simulation.
Bare init requires the same setup authentication as regular init before writing
project state. Run `relai setup` first for noninteractive use; hosted optimizer
access is checked separately when `relai optimize` starts.

## Catalog

Create `.relai/custom-adaptor/<name>/catalog.json`. `<name>` contains only
lowercase ASCII letters, digits, `-`, and `_`. The version is
`relai.custom_adapter.v1`. `runner` is a nonempty command argument array;
`prepare` is an optional argument array, run once per selected adapter before
its tasks. Both commands run from the project checkout and receive the
configured runtime environment. The runner receives appended
`--task-id <ID> --output <PATH>` arguments and must write its JSON result to
that path. Other directories under `.relai/custom-adaptor/`, such as shared
runner code without a `catalog.json` or a directory with an invalid name, are
not adapters: commands that scan every adapter skip them with a warning, and
skip names starting with `.` silently.
The commands are not run through a shell and need no Python runtime unless the
adapter uses Python. For Python, select the project's environment explicitly;
bare `python3` selects the first host interpreter on `PATH`. For example:

```json
{
  "prepare": ["uv", "sync", "--locked"],
  "runner": ["uv", "run", "--locked", "python", ".relai/custom-adaptor/example/run.py"]
}
```

Track the lockfile and dependency metadata. Optimization runs `prepare` in its
worktree, which does not inherit an ignored virtual environment or build
artifact from the source checkout. A compiled runner can use `prepare` to build
a binary and `runner` to invoke it, for example:

```json
{
  "prepare": ["cargo", "build", "--release", "--bin", "adapter-runner"],
  "runner": ["./target/release/adapter-runner"]
}
```

The host needs the chosen environment manager or toolchain. Use the platform's
executable path and satisfy the same `--task-id`/`--output` and JSON contract
for every language.

```json
{
  "schema_version": "relai.custom_adapter.v1",
  "prepare": ["uv", "sync", "--locked"],
  "runner": ["uv", "run", "--locked", "python", ".relai/custom-adaptor/example/run.py"],
  "tasks": [{
    "id": "request/create",
    "tags": ["request.create", "request-workflow", "smoke"],
    "description": "Create the requested item",
    "input_summary": "The target agent handles a request.",
    "evaluators": [
      {"id": "correctness", "description": "Checks the result"},
      {"id": "quality", "description": "Rates the response", "min_score": 0, "max_score": 5}
    ]
  }, {
    "id": "request/update",
    "tags": ["request.update", "request-workflow"],
    "description": "Update an existing item",
    "evaluators": [
      {"id": "correctness", "description": "Checks the requested update"}
    ]
  }]
}
```

Task IDs are unique and may have `/` groups; reject absolute paths, empty or
`.`/`..` segments, `::`, comma, backslash, a lone `*`, and control characters.
Give each task requirement- or risk-based RELAI tags. Missing or empty tags
remain readable for legacy/custom catalogs; the optimizer assigns a unique
scheduling and memory tag derived from the qualified task identity. Optional task fields are
`description`, `input_summary`, `agent_target`, and `metadata`. Evaluator IDs
must be unique and descriptions nonempty. Both finite range bounds must appear
together with `min_score < max_score`; omission means 0–1. An omitted
`evaluators` list keeps the legacy single `custom-grade` evaluator, whose
description may come from `evaluator_description`.

Recommend one meaningful, task-specific tag per task or sample, plus shared
tags for related tasks. In the example, `request.create` and `request.update`
select individual behaviors, while `request-workflow` selects both and can
carry shared tag memory. Use `--custom-tests ADAPTER::ID` for direct selection
by task ID. Keep tag names stable across catalog revisions so selectors and
memory keep their meaning. Do not reuse a task-specific tag for an unrelated
task; use a broad tag such as `smoke` only for the tasks intended to run
together. This is guidance, not a uniqueness rule enforced by RELAI.

## Runner result

The runner writes `relai.custom_run.v1` JSON with the requested `task_id`,
`trace.steps` array, optional `final_output`, and scores or failure details:

```json
{
  "schema_version": "relai.custom_run.v1",
  "task_id": "request/create",
  "trace": {"steps": [{"step_id": 1, "source": "agent", "message": "Done"}]},
  "final_output": "Done",
  "evaluations": [
    {"evaluator_id": "correctness", "score": 1, "feedback": "Passed"},
    {"evaluator_id": "quality", "score": 4, "min_score": 0, "max_score": 5, "feedback": "Clear"}
  ]
}
```

Each score must be finite and within its catalog range. If the result names a
range, it must equal the catalog range; RELAI supplies omitted result bounds
from the catalog. A completed error-free run supplies exactly one score per
declared evaluator. RELAI normalizes scores to 0–1 and averages them for
optimization. For grader or execution failure, include a non-null `failure`
object; for a run that did not fail, omit it or use `null` or `false`. Any
other value, such as a message string or `true`, also reports a failure.
`evaluation_errors` may carry diagnostic IDs outside the catalog but require
`failure`; partial scored evaluations remain evidence and the run stays
unscored during optimization. A validated execution failure without evaluator
errors scores zero in full optimization; fast optimization rejects it as
non-comparable evidence and leaves the sample unverified. A nonzero runner exit
is recorded as a task failure but remains unscored because it does not establish
which component failed.
Missing runtime requirements still stop
optimization for correction.

Classify failures by the evidence the runner has. A non-null `failure` without
evaluator errors says the target execution failed. Full optimization scores
that verdict zero; fast optimization treats it as non-comparable evidence and
leaves the sample unverified. Add `evaluation_errors` when grading failed; that
keeps the run unscored even when it contains partial scored evaluations. Exit
nonzero when the runner cannot establish which component failed; that also
remains unscored. Invalid JSON, a missing executable, and a missing runtime
requirement stop the workflow for correction rather than becoming agent
verdicts.

Target failure:

```json
{"schema_version":"relai.custom_run.v1","task_id":"request/create","trace":{"steps":[{"step_id":1,"source":"agent","message":"Request failed"}]},"failure":{"message":"The target agent could not complete the request"}}
```

Grader failure:

```json
{"schema_version":"relai.custom_run.v1","task_id":"request/create","trace":{"steps":[{"step_id":1,"source":"agent","message":"Done"}]},"failure":{"message":"A grader failed"},"evaluations":[{"evaluator_id":"correctness","score":1,"feedback":"Passed"}],"evaluation_errors":[{"evaluator_id":"quality","message":"The grading service was unavailable"}]}
```

## Selection and outputs

Validate a fresh execution with
`relai custom-adapter validate run --custom-tests 'example::request/create'`,
or select tasks with `--custom-tags`. This runs `prepare` and the selected
runner commands, so the target and its tools retain their normal costs and
external side effects. Use a narrow selector and a safe target environment;
pass runtime values with `--env-file` or `--env`. RELAI applies the same catalog,
result, scoring, failure, and trajectory checks used by simulation and then, by
default, asks a model to review relevant adapter source and the freshly redacted
trajectory for evidence-quality concerns. Model findings are advisory. If model
access is unavailable, report the AI review as incomplete while retaining the
deterministic findings. `--offline` intentionally skips AI review.

Inspect an existing simulation result or suite without executing tasks with
`relai custom-adapter validate results PATH`. Saved results do not bind their
catalog or source revision, so RELAI checks them against the current checkout
and warns that provenance is unverified. An embedded structured trajectory must
use `ATIF-v1.7` and contain a `steps` array; reject malformed embedded evidence
as a hard validation error. Before sending valid saved evidence to the model,
RELAI reapplies the current checkout's runtime redaction, including
secret-shaped fields and values known through the current runtime environment.
It cannot guarantee removal of a historical secret that the current runtime
configuration no longer identifies. Ask the user to review saved evidence when
its earlier environment may have contained other sensitive values.

A compatible legacy result may omit embedded structured trajectory evidence.
Continue its deterministic score checks and source review, but report that
trajectory-quality review is unavailable and the AI review is incomplete. Use
`validate run` to produce fresh evidence under the current configuration.
`results PATH --offline` runs only deterministic checks.

Use `--custom-tests 'example::request/create'`,
`--custom-tags 'example::request.create'` for one task,
`--custom-tags 'example::request-workflow'` for related tasks,
or an exact, quoted `example::*` wildcard with `relai simulate` or
`relai optimize`. Explicit Harbor selectors may be mixed; custom selectors
prevent the optimizer's default Harbor pool. RELAI converts `trace.steps` into
Agent Trajectory Interchange Format (ATIF) evidence and saves each completed
simulation result locally. With
`--result-json`, a suite keeps completed results and later task failures.
Runner-reported failures count under `failures`, with the validated result in
that entry's optional `result` field so partial scores and trace paths remain
available as evidence. If custom preparation fails after Harbor selection,
the combined report retains completed Harbor runs and records selected custom
tasks as failures.
Custom selectors write no outcome receipt and do not support
`--retry-from-outcome` or `--harbor-task`.

## Runtime requirements and evidence

`relai init --bare` does not require `.relai/runtime-manifest.json`. When that
file exists, its `relai.runtime_manifest.v1` requirements are project-wide;
`relai.runtime_manifest.v2` adds the required Harbor-only `outputs` list.
RELAI checks either version's required nonempty environment values and required
file paths before custom `prepare` and runner commands, including optimizer
runs. A custom runner reports its own result. Mixed
Harbor/custom projects must satisfy the same manifest for both workflows;
provide every declared requirement when running either one. The manifest lists
names, reasons, and `sensitive` flags, never values. Runtime values come from
the process environment, `.relai/simulator.env`, `--env-file`, then `--env` in
that order.

If a custom command fails, RELAI redacts local env file and `--env` values,
plus manifest-sensitive process values, from its stderr before showing or
saving the failure. Truncated stderr is omitted; the exit status remains.

RELAI keeps the adapter JSON and ATIF trajectory raw in the local run
directory. Returned trajectory evidence is redacted using sensitive manifest
variables and values from local env files or `--env`; custom `trace.steps`
needs no additional fields for this. Do not put credentials in other runner
result fields such as `final_output` or evaluator feedback.

Custom tag memory uses qualified tags such as `example::request.create` for
focused guidance and `example::request-workflow` for guidance shared by both
tasks. Pass them to `relai memory read`, `path`, `write`, or `append` after
`tag`. `relai memory list` omits custom tags;
inspect the catalog.
The public guide at `/cli/custom-adapters` has the full setup and environment
instructions.
