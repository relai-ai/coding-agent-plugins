---
name: relai-optimize
description: Use when RELAI should make or validate behavior-focused changes against existing agent tests or benchmarks.
---

# RELAI Optimization

Use `relai optimize` when changes are behavioral, non-deterministic, or hard to codify accurately as direct code changes. Also use it after other changes of any kind when the user wants to check for performance regressions against existing RELAI cases.

Good fits:

- Simulations expose failures across agent tests or benchmarks.
- The issue involves prompt behavior, tool selection, reasoning path, or multi-turn workflow behavior.
- The desired change should be evaluated repeatedly during an optimization loop.
- Direct code changes have been made and the user wants regression protection against existing RELAI cases.

Prefer direct implementation first when the root cause is a deterministic code bug or missing capability that can be fixed and verified with ordinary tests.

Before optimizing:

- Inspect current git state. If publishable code changes are present, tell the user that RELAI will include them in a separate before-optimization commit and in any resulting pull request. Local `.relai` state and private runtime inputs remain uncommitted.
- Run `relai optimize --agent-interaction`. RELAI asks the user to approve the selected tests, scope, rollout budget, start commit, and any uncommitted changes it will commit before any rollout, so do not ask for the same confirmation in chat first. Pass a rollout count or batch size the user gave; otherwise RELAI's default budget appears in the approval.
- Pass `--no-pr` unless the user asked for a pull request; opening a PR pushes to the remote.
- The scope comes only from flags over RELAI's default (structural changes allowed, current models fixed, no new paid tools, cost optimization disabled); a scope saved by an interactive run is not used. Pass only what the user asked for: `--allowed-changes prompt-and-config` for a prompt/config-only pass, `--allowed-models MODEL,...` when model switches are acceptable, `--allow-paid-tools`, `--cost-optimization conservative|balanced|aggressive`, and `--scope-instructions TEXT` for their preferences.
- Present the exit `3` approval request with your native question tool and resume with its `resume_argv` plus `--interaction-response`. When the user wants a different scope or budget, send `decline`, then re-run with the changed flags for a fresh request; never reuse an earlier response.
- Use the `relai-cli` skill and command reference before running `relai optimize`.
- For custom adapter tasks, read `references/custom-adapter-contract.md` and
  use `--custom-tests ADAPTER::ID` or `--custom-tags ADAPTER::TAG`. If
  `--skip-final-eval` was requested, explain that final before/after scores
  are absent; use `--result-json` for a selected structured result file.

Task, evaluator, and benchmark fixtures are not optimizer code-edit targets.

RELAI copies the live checkout without changing its files, index, or `HEAD`. It
commits eligible pre-existing code first and accepted optimizer changes second.
An automatic PR requires that second commit; a baseline-only branch remains local.
After a committed delivery RELAI removes its worktree, so the branch can be
checked out. It keeps the worktree with `--no-commit` (the changes stay staged
there, with a patch) and when the summary has a `Worktree` item naming why: an
unfinished repair, uncommitted publishable changes, a timeout, or a failed
removal. Then the branch is still checked out in that worktree. Resume a repair
there; otherwise the item gives the `git worktree remove` command to run before
switching to the branch.

Run the approved resume without blocking the conversation, as the `relai-cli` skill's long-running command guidance describes. While it runs, relay its `relai.progress.v1` progress: each phase and each optimization step's outcome (`step_finished`). A run takes minutes to hours; RELAI cannot be asked to stop early after the current step from a coding agent, and cancelling it stops immediately.

When it completes, present the completion document's `summary.agent_response_markdown` as RELAI's report. `result_path` names `optimizer-result.json`; the local artifacts beside it are under `.relai/.internal/runs/optimizer/<run-id>/` (in the CLI-managed runs directory):

- `optimization-report.json` for RELAI's concise optimizer report.
- `pr-summary.json` for each accepted change (`accepted_turns`) with its title, diagnosis, and change summary.
- `pr-description.md` for the human-readable report body.
- `optimizer-result.json` for the full structured result, including the final before/after evaluation (`final_evaluation_summary`).

Then explain the run to the user from those files and the optimizer branch:

1. **What changed and why.** For each accepted change, give its title, the diagnosed failure (`diagnosis_summary`), and what was changed (`change_summary`). Read the accepted commit's diff on the optimizer branch and show the key edit, such as an old instruction next to its replacement; say which files changed and that nothing else did.
2. **Scores.** A table with one row per agent test or benchmark sample from `final_evaluation_summary.environment_summaries`: before, after, and delta, plus the aggregate and the failure count before and after. Include evaluator-level changes from `evaluator_changes` when present.
3. **How failures were resolved.** A Scenario / Before / After table describing agent behavior for each previously failing case, drawn from the diagnosis and `observed_pattern_summary`. Explain any remaining deduction.
4. **Status and where it lives.** Accepted versus rejected changes and why the run stopped (`status`), the optimizer branch name or PR URL, and links to the report files. State `risks_or_open_questions` and any cost caveat RELAI reports; do not claim cost savings RELAI did not measure.

Do not apply the optimizer branch's changes to the user's checkout unless they ask. Keep RELAI's optimizer report and RELAI's suggested next steps distinct from your own recommendation. Do not replace the optimizer report with a one-paragraph paraphrase.
