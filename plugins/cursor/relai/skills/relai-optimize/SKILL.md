---
name: relai-optimize
description: Use when RELAI should make or validate behavior-focused changes against existing agent tests or benchmarks.
metadata:
  relai-cli-version: "0.2.13"
  relai-skills-revision: "32570166274ff546"
---

> **RELAI version check.** This skill matches skills revision `32570166274ff546` (RELAI CLI 0.2.13). Once per session, before following it, run `relai guide --revision`:
>
> - Same `skills_revision`: follow this skill as written.
> - Different `skills_revision`: run `relai guide relai-optimize --agent cursor` and follow its output instead of this file; the user does not need to do anything. If the printed `cli_version` is older than 0.2.13, suggest `relai update` once so they also get this plugin's newer features.
> - `relai guide` is not a command: this RELAI CLI predates the check. Ask the user to run `relai update`, then continue.
> - `relai guide` fails any other way, for example on an unknown workflow: follow this skill as written and tell the user the error once.

# RELAI Optimization

Use `relai optimize --fast` for a narrow behavioral fix with one to three exact samples. Use `relai optimize --full` when the fix needs a broader optimization loop. For a deterministic direct code fix, edit directly, then use `relai regression select` and run the selected simulations.

If `command -v relai` finds nothing, use the `relai-cli` skill to install the CLI and sign in before continuing.

Good fits:

- Simulations expose failures across agent tests or benchmarks.
- The issue involves prompt behavior, tool selection, reasoning path, or multi-turn workflow behavior.
- The desired change should be evaluated repeatedly during an optimization loop.

Prefer direct implementation first when the root cause is a deterministic code bug or missing capability that can be fixed and verified with ordinary tests.

Before optimizing:

- Inspect current git state. If publishable code changes are present, tell the user that RELAI will include them in a separate before-optimization commit and in any resulting pull request. Local `.relai` state and private runtime inputs remain uncommitted.
- Run `relai optimize --fast|--full --agent-interaction`. If the user has not chosen a mode, omit both flags and present RELAI's mode question with your native question tool; the next invocation asks for approval, so do not ask for the same confirmation in chat first. Full mode approval shows the selected tests, scope, rollout budget, source state, delivery, and that early stopping is enabled by default. Use `--no-early-stop` if early stopping previously ended a run before the desired fix. Fast mode approval shows the exact focus, simulation budget, regression cap, source state, and delivery.
- Fast mode requires one to three exact samples via `--focus-tests`, `--focus-custom-tests`, or `--focus-benchmark-samples`. `--seed-tests` only warms up full mode's scheduler. Use `--simulation-budget` and `--max-regression-checks` only when the user wants to change fast defaults of 12 and 3. Optional `--regression-tests`, `--regression-tags`, `--regression-custom-tests`, `--regression-custom-tags`, `--regression-benchmarks`, and `--regression-benchmark-samples` narrow the regression candidate pool; unmatched filters fail before the run. Exact benchmark regression samples are included even outside the usual ten-row benchmark screen, whose remaining coverage limit is reported.
- Full mode's scope, rollout, scheduler, and early-stop flags do not apply to fast mode.
- Pass `--no-pr` unless the user asked for a pull request; opening a PR pushes to the remote.
- The scope comes only from flags over RELAI's default (structural changes allowed, current models fixed, no new paid tools, cost optimization disabled); a scope saved by an interactive run is not used. Pass only what the user asked for: `--allowed-changes prompt-and-config` for a prompt/config-only pass, `--allowed-models MODEL,...` when model switches are acceptable, `--allow-paid-tools`, `--cost-optimization conservative|balanced|aggressive`, and `--scope-instructions TEXT` for their preferences.
- Present the exit `3` approval request with your native question tool and resume with its `resume_argv` plus `--interaction-response`. When the user wants a different scope or budget, send `decline`, then re-run with the changed flags for a fresh request; never reuse an earlier response. In a session without the native question tool, the protocol's headless rule applies: the user's own words approve the run only when they match the request's mode, focus or selection, budget, and delivery; otherwise stop and show the request.
- Use the `relai-cli` skill and command reference before running `relai optimize`.
- For custom adapter tasks, read `references/custom-adapter-contract.md` and
  use `--custom-tests ADAPTER::ID` or `--custom-tags ADAPTER::TAG`. If
  `--skip-final-eval` was requested, explain that final before/after scores
  are absent; use `--result-json` for a selected structured result file.

Task, evaluator, and benchmark fixtures are not optimizer code-edit targets.

RELAI groups agent tests into optimization steps by tag. Each benchmark sample
is tagged `benchmark-<id>` and `benchmark-<id>-sample-<index>`, and an agent
test without tags uses `test-<id>`. A run that selects agent tests but
cannot form its first step fails with `optimizer.no_schedulable_environments`;
report that error, not "no improvement found".

RELAI copies the live checkout without changing its files, index, or `HEAD`. It
commits eligible pre-existing code first and accepted optimizer changes second.
An automatic PR requires that second commit; a baseline-only branch remains local.
After a committed delivery RELAI removes its worktree, so the branch can be
checked out. It keeps the worktree with `--no-commit` (the changes stay staged
there, with a patch) and when the summary has a `Worktree` item naming why: an
unfinished repair, completed repairs of the run's tests, benchmarks, or project
runtime (listed in the result's `delivery.completed_repairs`), uncommitted
publishable changes, a timeout, or a failed
removal. Then the branch is still checked out in that worktree. Resume a repair
there; otherwise the item gives the `git worktree remove` command to run before
switching to the branch.

Run the approved resume without blocking the conversation, as the `relai-cli` skill's long-running command guidance describes. Relay `relai.progress.v1` progress. Fast mode baselines focus samples, edits in an isolated worktree, verifies chosen focus samples, and selects regression checks. A completed simulation without a comparable evaluator or genuine verifier score is unverified. The second attempt rechecks a regression found on the first. An `inconclusive` result means at least one focus or selected regression lacks comparable before/after scores. On failure after worktree creation, read the `failed` result and retained worktree path before retrying. Report unverified samples or conflicts clearly and recommend full mode only when the result explains why. Full mode reports each optimization step. Cancelling a run stops immediately; a full run cancelled during regression selection keeps accepted changes on its local branch and opens no PR. A failed or paused runtime repair ends a full run `failed` (exit 1) after its accepted changes are delivered; the document names the repair session, when there is one, and the next step, which the user completes before a fresh run.

Fast mode keeps agent tests, benchmarks, and the simulator harness fixed during its simulations. If one fails at runtime, it reports the failure instead of updating the test or harness inside the optimizer. Repair the owning asset separately, then start a fresh fast run. Its result lists definition digests and saved simulation evidence under the run's `evidence/` directory; compare definitions before accepting before/after scores. A score improvement on the focus sample does not prove complete regression coverage: report the selector's coverage gaps.

Fast regression selection requires comparable scores and inspects current scoring definitions. Runtime-only checks and unresolved scoring are excluded with reasons in `regression_selection.excluded_candidates`; their commands are execution suggestions, not scored passes. An undeclared verifier can qualify when it writes a real verdict; managed exit-status fallback rewards never qualify. With zero eligible scored checks, report “focus verified; no independent regression coverage” and the normal local delivery result. Read `verification` separately from `delivery`; an eligible check with unexpected missing scores remains unverified. Authoring or adapting a scored regression test is a separate workflow.
An unverified fast result keeps the worktree for inspection and does not commit a fix; a verified fix with a conflict can still be committed locally without opening a PR.

When it completes, present the completion document's `summary.agent_response_markdown` as RELAI's report and read `result_path`. In fast mode it names a `relai.optimize_fast_result.v1` document: report the focus baseline/post scores, which samples are unverified, regression choices and coverage gaps, conflicts, simulation budget, recommendation, and branch/patch/PR. A verified but conflicted fix may be committed locally without an automatic PR; an unverified fix remains in its worktree without a commit. In full mode, `result_path` names `optimizer-result.json`; local artifacts beside it are under `.relai/.internal/runs/optimizer/<run-id>/`:

- `optimization-report.json` for RELAI's concise optimizer report.
- `pr-summary.json` for each accepted change (`accepted_turns`) with its title, diagnosis, and change summary.
- `pr-description.md` for the human-readable report body.
- `optimizer-result.json` for the full structured result, including the final before/after evaluation (`final_evaluation_summary`).

If every planning or editing attempt fails, RELAI exits `1` with a `failed`
document and a saved `result_path`; the result has `status: "explore_failures"`
and `failed_explore_attempts` counts these failures separately from simulation
failures. Read `optimizer-debug.json` for the failing stage and cause before
retrying. Do not describe this as a successful search that found no improvement
or increase the rollout budget to work around it. A run where no turn produced
a verdict also ends `failed`, with `status: "not_evaluable"`; report the unscored
causes from its notes instead of retrying with a larger budget. A valid
no-change decision remains a successful outcome, including a run where another
attempt failed. When full mode starts no evolution step, report
`timed_out_before_step` as a deadline, `budget_exhausted_before_step` as an
empty budget or insufficient first-anchor budget, and `terminated_before_step`
as an explicit stop. Keep `cancelled` for signal cancellation even before the
first step; a deadline or explicit stop after a batch starts is
`terminated_after_step`. The result's `delivery` names where accepted work
went and, when no PR was opened, `pr_skipped_reason`.

Then explain the run to the user from those files and the optimizer branch:

1. **What changed and why.** For each accepted change, give its title, the diagnosed failure (`diagnosis_summary`), and what was changed (`change_summary`). Read the accepted commit's diff on the optimizer branch and show the key edit, such as an old instruction next to its replacement; say which files changed and that nothing else did.
2. **Scores.** A table with one row per agent test or benchmark sample from `final_evaluation_summary.environment_summaries`: before, after, and delta, plus the aggregate and the failure count before and after. Include evaluator-level changes from `evaluator_changes` when present.
3. **How failures were resolved.** A Scenario / Before / After table describing agent behavior for each previously failing case, drawn from the diagnosis and `observed_pattern_summary`. Explain any remaining deduction.
4. **Status and where it lives.** Accepted versus rejected changes and why the run stopped (`status`), the optimizer branch name or PR URL, and links to the report files. State `risks_or_open_questions` and any cost caveat RELAI reports; do not claim cost savings RELAI did not measure.

Do not apply the optimizer branch's changes to the user's checkout unless they ask. Keep RELAI's optimizer report and RELAI's suggested next steps distinct from your own recommendation. Do not replace the optimizer report with a one-paragraph paraphrase.
