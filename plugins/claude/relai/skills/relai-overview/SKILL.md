---
name: relai-overview
description: Use when deciding whether a request should be handled by direct implementation or by a RELAI workflow, when a user's goal needs several RELAI commands in sequence, or when the user asks what RELAI is for.
metadata:
  relai-cli-version: "0.2.13"
  relai-skills-revision: "32570166274ff546"
---

> **RELAI version check.** This skill matches skills revision `32570166274ff546` (RELAI CLI 0.2.13). Once per session, before following it, run `relai guide --revision`:
>
> - Same `skills_revision`: follow this skill as written.
> - Different `skills_revision`: run `relai guide relai-overview --agent claude` and follow its output instead of this file; the user does not need to do anything. If the printed `cli_version` is older than 0.2.13, suggest `relai update` once so they also get this plugin's newer features.
> - `relai guide` is not a command: this RELAI CLI predates the check. Ask the user to run `relai update`, then continue.
> - `relai guide` fails any other way, for example on an unknown workflow: follow this skill as written and tell the user the error once.

# RELAI Overview

RELAI helps teams improve agents by turning observed behavior and feedback into repeatable agent tests, running simulations, and optimizing against measured outcomes.

Use `references/proactive-decision-policy.md` as the decision ladder and its
examples.

## Core loop

1. Initialize the project with a simulator harness.
2. Capture behavior as agent tests, evaluators, or benchmarks.
3. Simulate current behavior against those repeatable cases.
4. Optimize the agent against the selected cases.

Use `relai optimize --fast` for one to three exact samples and a targeted fix;
use `relai optimize --full` for a broader optimization loop. A fast run keeps
test and harness assets fixed while measuring the agent change.

For a direct fix, `relai regression select` can choose focused existing
checks without starting an optimizer run. Run the suggested simulations when
the changed agent behavior needs measurement.

## Combining workflows

Plan from the user's goal, not from a single command. Most goals take several
RELAI commands in order. Follow each command's own skill for its flags and
confirmations, and apply the decision ladder before adding a step.

Measure before you change agent behavior. A score taken only after the change
cannot show whether the change helped or broke something.

These are common orders, not fixed recipes. Adapt them to the goal.

- **Check a behavior change for regressions.** Before editing, run
  `relai regression select --change "<planned change>"` and simulate the
  selected cases for a baseline (`relai-regression`, `relai-simulate`). Make
  the change, rerun the same cases, and compare scores, feedback, and
  trajectories. If a case got worse, revise the change or use
  `relai optimize --fast` on one to three of those cases (`relai-optimize`).
  If nothing measures the changed behavior, record the intent in EvalsWiki and
  create grounded coverage first (`relai-agent-test`).
- **Fix a behavior a user reported.** Turn the run log and feedback into an
  agent test (`relai-agent-test`). `relai optimize --fast` on that test
  measures its own baseline and regression checks, so do not repeat them. For
  a fix by hand, simulate the test first, make the fix, rerun it, then check
  the rest of the agent for regressions as above.

## Triage

Apply the decision ladder to the completed conversation and resulting change.
When the user supplies a folder of traces or context to curate into EvalsWiki,
route that explicit request to `relai-ingest`.
Explain any material RELAI action and unresolved grounding gap. The ladder
controls whether to take no action, checkpoint EvalsWiki, reuse coverage,
create grounded coverage, or run a targeted simulation.
