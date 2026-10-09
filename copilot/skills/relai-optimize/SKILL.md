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
- When the user asked for optimization, run it without further confirmation; a rollout count or batch size they gave is approved. When you decide on your own that optimization is warranted, confirm once with the user first, stating the selectors, total rollouts, and whether the result stays local.
- Pass `--no-pr` unless the user asked for a pull request; opening a PR pushes to the remote.
- Optimization runs without a terminal from a coding agent, so it needs an optimizer scope already saved by an interactive `relai optimize` run. When the CLI says to run `relai optimize` interactively (no saved scope, or an invalid one), relay that instruction to the user.
- Use the `relai-cli` skill and command reference before running `relai optimize`.
- For custom adapter tasks, read `references/custom-adapter-contract.md` and
  use `--custom-tests ADAPTER::ID` or `--custom-tags ADAPTER::TAG`. If
  `--skip-final-eval` was requested, explain that final before/after scores
  are absent; use `--result-json` for a selected structured result file.

Task, evaluator, and benchmark fixtures are not optimizer code-edit targets.

RELAI copies the live checkout without changing its files, index, or `HEAD`. It
commits eligible pre-existing code first and accepted optimizer changes second.
An automatic PR requires that second commit; a baseline-only branch remains local.

`relai optimize` is terminal-only. After it completes, preserve RELAI's final terminal report. Its local artifacts are under `.relai/.internal/runs/optimizer/<run-id>/` (in the CLI-managed runs directory):

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
