---
name: relai-regression
description: Use when a planned or completed direct code change needs focused regression checks from existing agent tests, custom-adapter tasks, or benchmark samples without an optimizer run.
metadata:
  relai-cli-version: "0.2.14"
  relai-skills-revision: "17c39e03dcd25819"
---

> **RELAI version check.** This skill matches skills revision `17c39e03dcd25819` (RELAI CLI 0.2.14). Once per session, before following it, run `relai guide --revision`:
>
> - Same `skills_revision`: follow this skill as written.
> - Different `skills_revision`: run `relai guide relai-regression --agent copilot` and follow its output instead of this file; the user does not need to do anything. If the printed `cli_version` is older than 0.2.14, suggest `relai update` once so they also get this plugin's newer features.
> - `relai guide` is not a command: this RELAI CLI predates the check. Ask the user to run `relai update`, then continue.
> - `relai guide` fails any other way, for example on an unknown workflow: follow this skill as written and tell the user the error once.

# RELAI Regression Selection

If `command -v relai` finds nothing, use the `relai-cli` skill, which asks
the user to install the CLI and then signs in, before continuing.

For a straightforward direct fix, finish the change and its deterministic
checks, then run `relai regression select --agent-interaction` when existing
agent behavior could regress. Add `--change` when the intent is not clear from
the Git diff, and `--agent-target` in a multi-target project. Use `--base` to
compare against the intended baseline. The command only selects cases; it
does not run a simulation or edit files.
The selector can inspect permitted current source and EvalsWiki pages. A test
without an explicit agent target remains eligible when `--agent-target` is set;
review its rationale for relevance to that target.

For a planned agent-behavior change, select and simulate cases before editing
so the rerun after the change has a baseline; `relai-overview` shows the full
order.

Read the versioned selection result at the completion document's `result_path`.
Each item has a type, exact reference,
rationale, and `simulate_argv`; use that command to run the relevant case.
For changes made after a measured baseline, compare before and after scores,
feedback, and trajectories. Otherwise run selected cases after the fix and
describe the limits of that evidence. A low score or execution failure needs
investigation; a high score on one case does not prove global safety.

An empty `selections` list is a legitimate decision when `empty_reason`
explains it. Report `coverage_gaps` and `evalswiki_status`; missing EvalsWiki
does not invalidate the selection, but it reduces historical context. If no
existing case measures an important behavior, propose grounded coverage
instead of running unrelated tests. Use `relai optimize --fast` for a targeted
behavioral fix against one to three exact samples, or `relai optimize --full`
for a broader loop with repeated before/after evaluation.

Consult `references/relai-cli-commands.md` for flags and the installed CLI's
`relai regression select --help` for version-specific availability.
