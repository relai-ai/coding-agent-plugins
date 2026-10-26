# RELAI CLI Command Guide

Use this guide when a user asks an agent to operate the `relai` CLI. Write the company name as RELAI and the command name as `relai`. Treat the installed command's help output as the final authority: run `relai --help`, then nested `--help`, before using an unfamiliar command or option.

Resolve CLI-managed paths from the project layout marker. Projects containing
`.relai/.internal/layout.json` use `.relai/.internal/`; legacy projects without
the marker use the corresponding path directly under `.relai/`.

## Guardrails

- Start in the user's repository root unless they specify another path.
- Each command section below names the actions that need the user's confirmation; other commands run without asking.
- Keep `.relai/config.toml`, `.relai/simulator.env`, `.relai/.internal/runs/`, generated caches, and secret values local. Never print or commit secret values.
- Respect RELAI read/write permissions in `~/.relai/config.toml` and `.relai/config.toml`. Do not add agent source, dependency metadata, simulator support, agent tests, evaluator references, benchmark CSVs, or required runtime files to `permissions.read.deny`.
- Public commands are documented below. Do not suggest hidden or debug-only commands.
- Agentic commands have one wall-clock timeout per invocation: `simulate` 3h, `optimize` 6h, `test discover` 4h, other `test` commands 90m, and `init`, `ingest`, `wiki`, `evaluator`, and `benchmark` 1h. `--timeout <duration|off>` (such as `2h`) or the `RELAI_TIMEOUT` environment variable changes it; the flag wins. A timed-out command saves resumable progress where the workflow supports resume and exits `124` in terminal mode.
- A resumable workflow's session records an explicit `--permissions` flag. A resume without the flag keeps the recorded one; a resume with it uses and records the new one. A session started without the flag follows the global profile.

## Project instructions for RELAI

RELAI's workflow agents (init, ingest, agent tests, benchmarks, evaluators, EvalsWiki updates, and simulator repair) and Agent Optimizer follow instructions the repository writes for RELAI. Agent Optimizer receives them after the run's own custom instructions, within its 48,000-character limit, and a cut names the file to read for the rest.

- Sources, ordered from the repository root to the working directory: the section under a heading named exactly `RELAI` (any level, until the next heading of the same or a higher level) in each `AGENTS.md`, then each whole `RELAI.md`. `CLAUDE.md` is never a source, and RELAI's managed policy block is ignored; a file whose managed-policy markers are malformed is omitted with the marker line to fix.
- Use them for how RELAI should operate in this repository: datasets to use or avoid, the evaluator or scoring contract, files RELAI must not change, how to confirm a failure, and commands to run. Target-agent behavior belongs in the EvalsWiki; coding-agent guidance stays outside the `RELAI` section.
- They cannot change RELAI permissions, budgets, tool contracts, or validation. Enforce rules that must always hold with `permissions.read.deny` or `permissions.write.deny` in `.relai/config.toml`.
- RELAI reads read-permitted regular files only, skips symlinks, and shares one 32 KiB budget across sources, marking any cut. A run names the sources it uses; a resumed run picks up edited instructions.
- When the user states such a rule, propose the `RELAI` section or `RELAI.md` and ask before editing either file.

```markdown
## RELAI

- Benchmark and optimize against `data/validation.csv`; never read `data/test.csv`.
- Score with the project's production evaluator, not a new LLM judge.
- Run the agent through `scripts/run_agent.sh`, not by importing its modules.
```

## Public command map

`relai auth`, `relai auth status`, `relai auth login`, `relai auth logout`, `relai setup`, `relai update`, `relai uninstall`, `relai init`, `relai simulate`, `relai regression select`, `relai optimize`, `relai ingest`, `relai memory`, `relai wiki`, `relai tag`, `relai benchmark`, `relai test`, `relai test discover`, `relai evaluator`, `relai plugins`, `relai policy`, `relai runs`, and `relai completions` are the visible release command surface. Use `relai --version` to print the installed binary identity.

### `relai policy`

Install or remove RELAI's shared proactive workflow policy in existing regular repository-root `AGENTS.md` and `CLAUDE.md` files. The policy tells coding agents when a change calls for RELAI work (an EvalsWiki note, reusing or adding agent tests or evaluators, or a focused simulation) and when ordinary implementation is enough. The command skips symlinks without following them, never creates instruction files, and never recurses into nested files. Both actions fail if no regular root instruction file exists. After `relai init` succeeds, the coding agent runs `relai policy install` without asking whenever an existing regular root instruction file exists, including one that already has the managed policy marker, because the marker stays the same while the policy text changes between releases. Install adds the block where it is missing, updates an outdated block in place, and reports files that already have the current version as up to date. The coding agent then tells the user in one line which files gained or updated that guidance and that `relai policy remove` undoes it, and says nothing when install reports everything up to date. `install` validates every existing target before changing any of them; an error names the file, and the line of a malformed or unmatched marker. Both actions refuse a block written by a newer RELAI CLI and ask to upgrade `relai`. `remove` only removes RELAI's complete managed block and names the files it changed.

```sh
relai policy install
relai policy remove
```

## Setup and diagnostics

### Install the CLI

These skills can be installed from a plugin marketplace without the CLI. When
`command -v relai` finds nothing, the user's request for a RELAI workflow
covers installing it: tell the user in one line that you are installing the
RELAI CLI, then on macOS or Linux run the standalone installer:

```sh
curl -fsSL https://api.relai.ai/install.sh | bash
```

If the installer fails, show its error and stop; do not retry with `sudo` or
another install method. On any other platform, do not guess an installer; send
the user to https://cli-docs.relai.ai/installation. The installer adds its
directory to the shell profile, which the current shell has not read, so run
`relai` by the full path the installer printed until a new shell starts.

Then run `relai setup --check` and follow "Host prerequisites" below for
anything missing, and sign in with `relai auth login`. It prints a verification
link and short code; show both to the user and give the command a shell timeout
that leaves them several minutes to finish in the browser. Use `relai auth
login` rather than `relai setup` here: setup without a terminal does not start
sign-in, and `relai setup --agent` would install a second copy of the RELAI
skills this host already has. Confirm the result with `relai auth status`.

### OAuth setup

Interactive `relai setup` uses OAuth device authorization. It reuses a usable
OAuth session and starts device authorization only when sign-in is needed.
To sign in again deliberately, use `relai setup --reauthenticate`. Device
authorization prints the dashboard device URL and short code,
then tries to open the complete verification link in
the system browser; if it cannot, open the printed link and enter the code
manually. It also makes a best-effort local clipboard copy of the short code
without storing it. It also works for SSH, containers, and browserless
environments: open the printed link from another machine when needed. Complete
workspace selection in the browser; this command displays the selected workspace after success. OAuth access and refresh tokens are stored as plaintext in the
user-only file `~/.relai/credentials.json` and are used for ordinary CLI API
requests. They never appear in `~/.relai/config.toml` or logs; keep the file
private and never commit it.

```sh
relai setup
```

### `relai auth`

`auth status` shows the active OAuth identity, organization, and server-selected
workspace. In API-key mode it reports that method without attempting identity
lookup. `auth login` runs the browser-opening device flow directly; run it
again to reauthenticate or select a different server-bound workspace. `auth
logout` revokes the OAuth refresh token with the
issuer, then removes the secure credential; a transient revocation failure
keeps the credential so the user can retry. With no stored credential it clears
the local sign-in offline; a same-server API key stays configured and becomes
active (logout notes this on stderr; stdout still says `Signed out.`). In
API-key mode it removes OAuth credentials an earlier sign-in left for that
server.

```sh
relai auth status
relai auth login
relai auth logout
```

### `relai setup`

Configure machine-level preferences and authenticate with OAuth. `--check` only
audits prerequisites and does not write configuration.

```sh
relai setup --check
relai setup
relai setup --reauthenticate
relai setup --theme dark
relai setup --theme dark --agent codex
relai setup --theme dark --agent cursor
relai setup --api-url https://api.example.com
```

`--theme` accepts `light` or `dark`, and `--api-url` selects the OAuth backend.
Configuration is stored under `~/.relai/`. Without a terminal, `--agent` opts
in to OAuth device sign-in (the link and code go to stderr, and setup waits
until the sign-in is approved or expires: run it as a background command, or
with a shell timeout longer than the sign-in's lifetime, and relay the link and
code while it waits), and a first setup
without `--theme` saves the default `light` theme. Without a key, `--agent`,
or a usable session, a non-interactive setup fails with `setup.auth_required`.

#### Host prerequisites

When host readiness is unknown or a command reports a missing prerequisite,
use `relai setup --check` to audit the required tools. If a required host tool
such as `uv`, Docker, or Docker Compose is missing, ask the user to install it
before continuing the dependent workflow. Explain what is missing and why it is
needed, and provide OS-appropriate installation steps from the audit or CLI
diagnostics. If Docker is installed but its daemon is unavailable, ask the user
to start Docker. Do not install host tools or change machine configuration
automatically; perform the setup only when the user asks you to.

Preserve any saved workflow session while prerequisites are unavailable. After
the user reports that setup is complete, verify the missing tool is available
and, for Docker, that `docker info` succeeds, then use the documented resume or
retry path. Do not repeatedly rerun a workflow against an unchanged prerequisite
failure. If RELAI supplies an `external_action` request, present it through the
host's native question UI and follow its supplied resume protocol; `completed`
attests to finished setup, and RELAI verifies it on resume.

Distinguish host prerequisites from task-image dependencies. A missing
interpreter or package inside a Harbor image belongs to that image and its
existing RELAI repair workflow; installing it on the host does not fix the image.

### `relai update`

Update the installed CLI. `--force` reinstalls the latest release even when it is already current.

```sh
relai update
relai update --force
```

### `relai uninstall`

Remove the `relai` binary, the detected shell's completion file (other shells' completion files are listed as kept), the installer's lines in every known shell profile, saved credentials, and the CLI's own files in `~/.relai` (installed plugins included), keeping optimizer worktrees and anything else it did not create. On Windows it also removes the install folder from the user PATH and the PowerShell completion lines. It never touches a project's `.relai/` directory. `--dry-run` previews without changing anything. It also removes the RELAI coding-agent host registrations; one it cannot remove keeps that host's plugin source and is reported with the file to fix. Declining the confirmation exits `130`; any failed step is reported and makes it exit non-zero after the other steps ran, so do not report the uninstall as complete then. Confirm with the user before running it: it edits their shell profile and removes saved credentials.

```sh
relai uninstall --dry-run
relai uninstall
```

### `relai completions`

Print a shell completion script to standard output. Redirect it only when the user requests installation.

```sh
relai completions bash
relai completions zsh
relai completions fish
relai completions powershell
```

## Project initialization

### `relai init`

Requires an installed Docker CLI and a running daemon. Fresh, restarted, and
resumed runs check the daemon before model work or changes to the saved init
session; install or start Docker and rerun the command shown on failure.
`--bare` skips the Docker check.

Initialize a git-tracked agent repository and scaffold simulator support; it refuses to run from the home directory. It may register discovered targets and write project-local RELAI files. Use `--resume` to continue a paused session (it fails at once when there is none) or `--restart` to discard it and start again; never combine them. In a multi-target project, `--agent-target` may be repeated to select targets; a name init did not discover is asked about again on resume. `--permissions` accepts `auto`, `accept_edits`, or `ask` for bounded init-agent actions. `--timeout <duration|off>` changes the 1h wall-clock limit; after a timeout with saved progress, continue with `relai init --resume`. If preparation times out before creating a checkpoint, rerun the original command. Registered targets live in the local `.relai/config.toml`; in a fresh clone whose `.relai/harbor` is committed, register them with `relai init --restart` (add `--no-wiki` to skip the EvalsWiki bootstrap), since plain `relai init` refuses an existing harness.

```sh
relai init
relai init --resume
relai init --agent-target support-agent --permissions ask
relai init --bare
```

Machine-level setup authentication is used by default. OAuth credentials are
stored in the user-only file `~/.relai/credentials.json`. Harbor task images and project adapters own runtime
dependencies; init never forwards OAuth credentials to project code.

If captured sources change while init's EvalsWiki bootstrap is paused,
`relai init --resume` restarts that bootstrap with fresh sources and reports it.
The paused bootstrap's progress and clarification answers are discarded; other
init progress is retained. Init's bootstrap captures only the RELAI artifacts
registered before init started authoring its harness, not the smoke task init
is writing.

`relai init` initializes the Harbor simulator runtime in `.relai/harbor/`.
Agent tests, global evaluators, and CSV benchmarks are Harbor packages there.
`--bare` creates project configuration without Harbor or a target agent for a
custom-only project. It checks the same setup authentication as regular init
before writing project state. Interactive runs offer setup when needed;
noninteractive runs require it beforehand. Hosted optimizer access is checked
when `relai optimize` starts. See `references/custom-adapter-contract.md` for
the full catalog and runner contract.

### Coding-agent interaction mode

Commands whose help lists `--agent-interaction` (including `init`, `ingest`, the `wiki` workflows, `test create`, `test update`, `test discover`, `test suggestion`, `evaluator create`, `evaluator update`, `benchmark register`, and `benchmark update`) emit the typed `relai.agent_interaction.v1` protocol when run with that flag, and report progress on stderr as `relai.progress.v1` JSON lines (`phase`, `activity`, `milestone`, `test_ready`, `env_needed`, `heartbeat`, then a final `paused` or `finished`). `simulate` also accepts the flag for progress (`test_started` and `test_finished` per run) and one `completed` or `failed` completion document naming its outcome; it never pauses for a response. `optimize` accepts it for one approval pause before any rollout, progress (`rollout_finished` per simulation and `step_finished` per optimization step), and one `completed`, `failed`, or `cancelled` completion document. The installed `relai-cli` skill carries the full protocol: exit codes, completion reports, native-question mapping, and `--interaction-response` resumes. Under `--agent-interaction`, discovery's proposal review becomes a clarification with choices `build`, `build_all`, and `skip`, where a free-form answer is revision feedback (once the candidate's proposal revisions are used up, it adds `retire`, which retires a risk no published agent test covers, and takes no free-form answer), and a timeout caught inside an agent loop arrives as an exit `3` limit pause with a `resume_argv`.

```sh
relai init --agent-interaction
relai init --resume --agent-interaction --interaction-response '{"schema_version":"relai.agent_interaction.v1","session_id":"SESSION","request_id":"REQUEST","answer":"ANSWER"}'
```

### `relai runs`

On macOS and Linux, every `--agent-interaction` invocation runs as a background run that outlives the shell call, and waits for it up to `--wait` (default `90s`; `0s` returns once it has started). A run that finishes in time reports exactly as a foreground run. A run still going prints a `running` document (`relai.agent_interaction.v1` with `status: "running"`, `run_id`, `log_offset`, `wait_argv`, `cancel_argv`, and the `latest_progress` event) and exits `75`. `relai runs wait <run-id> --log-offset <n>`, the document's `wait_argv`, waits again, relaying on stderr every progress event written since the previous relay (always use the newest `running` document's `wait_argv`), and once the run finishes prints its stdout document and exits with its exit status (`3` for a question); `--wait` has no maximum, so a long one such as `24h` returns only when the run pauses for a question or ends; `relai runs status <run-id>` reports without waiting, `relai runs logs <run-id>` prints the whole stderr log, `relai runs cancel <run-id>` interrupts the run as Ctrl-C would and waits like `wait` (repeating it only waits; `--force` stops the run at once, skipping cleanup), and `relai runs list` lists the project's runs. Run them from the project directory. If a run's supervisor is killed, its command stops at its last checkpoint and the run is `lost` (exit `1`); resume a resumable workflow as usual.

```sh
relai runs wait <run-id>
relai runs cancel <run-id>
relai runs list
```

When asked to wait for completion, keep collecting the run's result until it
ends or requests user action. A `running` document or host background-task ID
is not a completion report. In a headless coding-agent session, collect any
background wait's output before ending the session; it cannot notify the user
after the session exits. Follow the installed skill's host-specific waiting
guidance.

New run records, logs, and temporary stdout files are owner-only (`0600`);
historical file permissions are unchanged. New records redact values passed
with `--interaction-response ANSWER` or `--interaction-response=ANSWER`.
`relai runs list` redacts both forms in historical records too, without
rewriting those files.

## Simulation and optimization

### `relai simulate`

Measure selected agent tests, tags, benchmarks, custom adapter tasks, or one explicit Harbor task. At least one selector is required; selectors may be repeated or comma-separated. Use `--max-simulations` after selection/deduplication, `--shuffle` and optional `--shuffle-seed` for execution order, and `--result-json` for the suite result contract. Every completed run also saves its result under the CLI-managed `runs/results/` directory. Simulation results stay local. Run the selected simulation and its automatic repairs without asking for confirmation. Pass `--agent-interaction` for `relai.progress.v1` progress on stderr (`test_started`, then `test_finished` with `status` and evaluator `scores`, for each run; the next run's `test_started` can arrive before a run's `test_finished`, and `test_finished` events stay in test order) and one stdout completion document; simulation never pauses for questions, so it takes no `--interaction-response`. For Harbor runs, that document names `outcome_path`, the stable `relai.agent_simulation_outcome.v1` receipt for completed, partial, and terminal failures, which the CLI writes to a fresh path in its runs directory.

```sh
relai simulate --tests example
relai simulate --tests example --agent-interaction
relai simulate --tests env-a,env-b --result-json .relai/.internal/runs/results.json
relai simulate --tags regression --agent-interaction --outcome-intent verify-policy
relai simulate --tags regression --shuffle --shuffle-seed 7
relai simulate --benchmarks support-suite --max-simulations 5
relai simulate --benchmark-samples 'support-suite#row-0-abcdef123456'
relai simulate --harbor-task path/to/task --timeout 45m
relai simulate --custom-tests 'example::request/create' --result-json .relai/runs/custom-suite.json
relai simulate --custom-tags 'example::request-workflow'
```

`--harbor-task PATH` runs one unregistered task and cannot be combined with
selectors or `--retry-from-outcome`. `--env-file` and `--env`
work with every selector.
Custom selectors use `ADAPTER::ID` or `ADAPTER::TAG`, including an exact
`ADAPTER::*` wildcard. They may be mixed with explicit Harbor selectors.
Custom runs use `--result-json` and saved per-run results. Outcome receipts,
`--retry-from-outcome`, and `--harbor-task` are Harbor-only. Read
`references/custom-adapter-contract.md` before creating an adapter.

The terminal summary groups completed runs by agent test and lists
each evaluator score and evaluator error. It is human-readable only; use the
result JSON or the `--agent-interaction` document and outcome receipt when
another program needs to consume a simulation.

Users add required runtime variables to the local `.relai/simulator.env` file; RELAI loads it automatically for simulation and optimization, and the values persist across local runs. Use the shell environment for temporary runs or CI. Use repeated `--env-file PATH` for an alternate file or `--env KEY=VALUE` for an invocation-specific override. `relai init` seeds that file with empty placeholders for the declared names, so the user only fills in values. Tell the user which variable names are missing; do not create, open, or edit the file for them, and do not put secret values in chat or command history.
When an agent consumes a Harbor result, read the stdout document's `outcome_path` and summarize that outcome instead of parsing terminal prose; once the simulation starts, the document exists on exit 1 too, with status `failed`. For custom results, read the document's summary or the suite JSON. The outcome distinguishes valid low scores from evaluator errors, unscored runs (no evaluator scored them; `next_actions` includes `review_unscored_runs`), simulator/runtime and environment/configuration failures, model-access stops (category `model_access`, next action `restore_model_access`: the model proxy refused a host judge for sign-in, budget, or usage-cap reasons), and publication failures, carries each score's evaluator `feedback` when the evaluator gave one, and lists each run's local artifacts, including its ATIF trajectory and saved per-run result. Each evaluator error carries a structured `repair_decision`, and `--retry-from-outcome <initial> --agent-interaction` reruns the recorded selection once after an evaluator repair; the `relai-simulate` skill describes when to use them. `--outcome-change` and `--outcome-intent` accept caller-supplied attribution.

### `relai regression select`

Select a small set of existing regression checks after a direct fix without
running them. `--base` defaults to `HEAD`; `--change` adds the intended change
when Git alone is incomplete. `--agent-target` excludes explicitly different
targets while keeping unscoped tests eligible. The selector may inspect
permitted project source and EvalsWiki through read-only tools. `--max-targets`
defaults to 3, and `--result-json` saves the versioned result.
`--agent-interaction` prints a completion document with `result_path` naming
the saved versioned result for coding agents. An empty
selection is valid when `empty_reason` explains it. Each selected item has
an exact `simulate_argv`, including `--benchmark-samples` for one benchmark
row. Read `coverage_gaps` and `evalswiki_status` before interpreting the result.

```sh
relai regression select --change 'Fix retry handling' --result-json .relai/runs/regression-selection.json
relai regression select --base main --agent-target support-agent --agent-interaction
```

### `relai optimize`

Choose `--fast` for a targeted fix against one to three exact focus samples or `--full` for the broader optimization loop. If neither is supplied, a terminal asks for a mode; `--agent-interaction` returns a mode-choice request. Headless runs require an explicit flag. In a multi-target repository, `--agent-target` is required. Both modes use an isolated optimizer worktree.

From a coding agent, run it with `--agent-interaction`. Each request exits `3`; present it with the native question tool and resume with `resume_argv` plus `--interaction-response`. Fast mode asks for approval of focus, simulation budget, regression cap, source state, and delivery. Full mode asks for approval of scope, rollout budget, and delivery. The full scope is the default (structural changes allowed, current models fixed, no new paid tools, cost optimization disabled) with requested scope flags applied. A response never applies to a changed command.

```sh
relai optimize --fast --focus-tests example --no-pr --agent-interaction
relai optimize --fast --focus-custom-tests example::task --simulation-budget 9
relai optimize --fast --focus-benchmark-samples support-suite#row-0-abcdef123456
relai optimize --full --tests example --no-pr --allowed-changes prompt-and-config --agent-interaction
relai optimize --full --tags regression --env-file .relai/simulator.env --total-rollouts 50
relai optimize --full --benchmarks support-suite --agent-target support-agent --batch-size 2
relai optimize --full --tests example --no-early-stop --no-pr
```

Fast mode requires one to three exact samples across `--focus-tests`, `--focus-custom-tests`, and `--focus-benchmark-samples`. Its default 12-simulation budget includes initial focus baselines, post-edit reruns, and selected regression before/after checks. `--max-regression-checks` defaults to 3. `--regression-tests`, `--regression-tags`, `--regression-custom-tests`, `--regression-custom-tags`, `--regression-benchmarks`, and `--regression-benchmark-samples` optionally restrict the candidate pool; unmatched filters fail before approval. Exact benchmark regression samples are included even outside the usual ten-row benchmark screen. Fast results use `relai.optimize_fast_result.v1`; inspect baseline/post scores, unverified samples, regression selections and evidence, conflicts, and delivery. A completed simulation without an evaluator score remains unverified. An `inconclusive` result commits no fix; a verified but conflicted improvement may still be committed locally without an automatic PR. A failure after worktree creation writes a `failed` result with the available evidence and delivery state. Fast mode defaults to a `60m` timeout.

Fast simulations do not automatically repair registered tests, benchmarks, or the simulator harness. An unverified focus baseline stops the run for separate repair; another unverified result keeps the worktree without committing the fix. Each simulation saves a suite result and, when available, a trajectory under the fast run's `evidence/` directory, retained after worktree cleanup. The result records each sample's definition digest and evidence paths; a changed definition makes before/after scores unverified. Completion reports show focus scores, regression status, coverage gaps, and delivery.

The rest of this section describes full mode. Custom selectors suppress the default Harbor pool; explicit Harbor selectors
may be mixed in. `--skip-final-eval` uses the full rollout budget for
optimization and omits final before/after scores. Its minimum rollout count
is `2 * batch-size`. `--result-json` writes the structured optimizer result.

`--seed-tests` provides warm-start agent tests. `--total-rollouts` and `--batch-size` control the full run. Early stopping is enabled by default; `--no-early-stop` disables it when it stops before the desired fix, while `--early-stop` remains accepted. `--total-rollouts` has no fixed maximum and must be at least `6 * batch-size` by default or `2 * batch-size` with `--skip-final-eval`; RELAI asks to confirm more than 50 total rollouts interactively, warns about them non-interactively, and names them in the `--agent-interaction` approval. `--no-pr` keeps accepted changes on the local optimizer branch; otherwise a configured GitHub CLI may push and open a PR. Pass `--no-pr` unless the user asked for a pull request. `--pr-base` must already exist on `origin`. `--no-commit` (or `[optimize] commit = false` in `.relai/config.toml`) creates no Git commits, so repository commit hooks never run: accepted changes stay staged in the optimizer worktree and RELAI's changes alone are written to `.relai/runs/optimizer/{run-id}/changes.patch`, which the summary shows how to `git apply`; it implies `--no-pr`. Use it when the repository's hooks or signing setup reject RELAI's commits; the commit error names both options.

A confirmed target-agent crash or timeout is a failed verdict with score `0`, so optimization may repair it. Evaluator, simulator harness, setup, and other failures without a trustworthy agent verdict remain unscored and are excluded from score comparisons. A host prerequisite failure, such as an unavailable Docker daemon, stops optimization with its cause and keeps accepted changes.
For a custom adapter, a validated non-null `failure` result without evaluator errors is a failed verdict. A custom grader error remains unscored even when another grader returned a partial score. An unsuccessful runner command remains unscored because its exit alone does not identify the failing component. Missing executables, malformed results, and missing runtime requirements stop optimization for correction instead.

RELAI copies the live checkout without changing its files, index, or `HEAD`. It commits publishable pre-existing code changes as a before-optimization baseline, then commits accepted optimizer changes separately. Warn the user that an automatic PR includes both commits. `.relai` state, explicit runtime env inputs, credentials, dependency-setup outputs, generated reports, and Git-ignored private files remain uncommitted. No accepted publishable optimizer diff means no automatic PR, though a baseline branch may remain locally. With `--no-commit` or `[optimize] commit = false`, RELAI creates neither commit and opens no PR; the patch holds only its accepted changes.

An unfinished update session for a selected test blocks startup. If a Harbor runtime or test repair pauses, is cancelled, or fails during a rollout, the optimizer stops and reports the cause, session path when present, and recovery command. Preserve accepted changes, but treat final validation as incomplete; resume a remaining session in the reported worktree or fix the cause, then start a fresh optimization run from the repaired project.

If every planning or editing attempt fails, the command exits `1` after saving
the result and diagnostics. The result has `status: "explore_failures"` and
`failed_explore_attempts`; `optimizer-debug.json` names the failing stages and
causes. A run where no attempted turn produced a verdict has
`status: "not_evaluable"` and also exits `1` after saving its result; its notes
name each unscored cause. Under `--agent-interaction`, the `failed` document
carries the saved `result_path`. Inspect those diagnostics before retrying. A
valid no-change decision remains a successful outcome, including when another
attempt failed. The result's `delivery` records where accepted work went
(`state`, branch, PR URL or `pr_skipped_reason`, patch, kept worktree and
reason). A full result that starts no evolution step uses
`timed_out_before_step` for a deadline, `budget_exhausted_before_step` for an
empty rollout budget or one too small for first-anchor validation, and
`terminated_before_step` for an explicit stop. Signal cancellation remains
`cancelled` before or after a step. A deadline or explicit stop after a batch
starts uses `terminated_after_step`. With `--agent-target`, the default pool,
wildcards, and tags keep only
that target's tests and untargeted ones; naming another target's test is an
error.

### `relai ingest`

Ingest a folder of traces or context into EvalsWiki. The folder may be outside
the repository; RELAI treats it as read-only, analyzes it agentically, persists
selected raw excerpts under `.relai/evals-wiki/attachments/traces/<ingestion-id>/`, and updates
requirements, risk hypotheses, or open questions. Use `--note` to disambiguate
the target trace set. Wiki patches apply automatically by default and cannot
delete pages; pass `--review` to pause before applying each Wiki patch (an
interactive terminal prompts instead). An approval applies a patch only while
its pages are unchanged. Risk updates and extracted attachments can be written
before that approval. Analysis scripts run on the host and need approval under
`accept_edits` and `ask`. A paused, failed, or interrupted ingestion resumes
with `--resume`, which keeps the session's `--permissions` profile; declining a
pause discards the session; `--restart` discards the unfinished ingestion
session, not durable writes already made. A timeout saves the session for resume; a resumed invocation starts a new
deadline, so repeat any `--timeout` override.

```sh
relai ingest ./traces --note failed-refund-handoff-runs
relai ingest ~/Downloads/support-traces --review
relai ingest --resume --agent-interaction
relai ingest ./traces --timeout 2h
```

## Project knowledge

### `relai wiki update`

When a conversation yields durable project knowledge (a user decision, correction, constraint, preference, or useful hypothesis), send the bounded evidence envelope to RELAI. Do not search or edit the Wiki yourself: RELAI retrieves, deduplicates, validates, and updates it. It returns structured `updated` or `no_change`; only semantic conflicts should need the coding agent's native question UI. Pass evidence through stdin, never a command argument.

```sh
relai wiki update --agent-interaction --evidence-json -
```

For example, pipe this JSON envelope to that command:

```json
{"schema_version":"relai.wiki_evidence.v1","evidence_id":"<stable-uuid>","source":{"kind":"coding_agent","agent":"<coding-agent>","messages":[{"role":"user","content":"Prefer deterministic repository search."}],"changed_paths":["src/example.rs"]}}
```

Use `--review` when each proposed Wiki patch should pause for approval; otherwise focused, validated patches apply directly. Writes recheck captured preimages and replace files atomically, but a stopped multi-file update can leave a visible partial result for later validation and repair. An unfinished update is resumable with `relai wiki update --resume`; `relai wiki update --discard` removes it instead (also one this CLI cannot read or resume, and the queued evidence it was reconciling), exits `0`, and prints a one-line confirmation, but refuses a bootstrap's or another workflow's Wiki step and names that workflow's own commands. Wiki updates do not reconcile artifacts automatically: each agent test, evaluator, or benchmark workflow re-reads and validates current grounding before its own write. Do not invoke it for ordinary transient implementation chatter.

A fresh `relai wiki update --agent-interaction` reads its piped evidence even when
`--wait 0s` returns before the run finishes. A resumed update uses saved evidence
and needs no stdin.

Agent test suggestion decisions queue their Wiki evidence locally. A fresh
`relai wiki update` first reconciles queued evidence, oldest first, and writes
only your evidence's result document; if a queued update pauses, the pause is
the command's (resume it with `relai wiki update --resume`), and your evidence
is queued behind it for the next fresh update. Declining a queued update's
question or approval discards that queued evidence and the reconciliation
continues. Cancelling the command (Ctrl-C or `relai runs cancel`) stops the
update without losing it: `relai wiki update --resume` continues it (a `--review`
patch that was being applied is proposed again for approval), and any queued
evidence, yours too, stays queued for the update after it.

### `relai wiki reconcile`

Use this command after a normative EvalsWiki requirement changes to review
every affected grounded artifact in one run. `still_valid` refreshes the
captured grounding only after source, Wiki, and requirement preimage checks;
other decisions use the artifact's existing staged update flow. Ambiguity,
coverage reduction, and retirement pause for a native user decision. Declining
leaves that artifact unchanged and moves to the next one (a retirement is never
automatic, so either answer to it declines), and the run lists what was
declined when it finishes. An artifact grounded on a missing or invalid
requirement page stops the run before it starts, naming the artifact and
requirement. An unfinished update of a queued artifact that reconciliation did
not start is never adopted; finish or discard it first. `--restart` discards
the unfinished reconciliation queue (also one this CLI cannot read or resume)
and starts a new run that discovers the affected artifacts again; an artifact
update the discarded run started keeps its own session and commands. While an
earlier reconciliation run is still running, even inside an artifact update it
started, every `relai wiki reconcile` invocation, `--restart` included, is
refused until that run ends.

```sh
relai wiki reconcile --agent-interaction
relai wiki reconcile --resume --agent-interaction
relai wiki reconcile --restart --agent-interaction
```

### `relai wiki bootstrap`

Build or merge the local EvalsWiki from the current working tree, Git history, registered local RELAI artifacts (the agent test, evaluator, and benchmark packages under `.relai/harbor/`), local run/evaluation logs, and associated Codex or Claude Code sessions. Bootstrap writes concise orientation plus canonical requirement pages; project and artifact pages are CLI-owned. RELAI inventories and reads each source through bounded, read-only, capability-specific tools; session output contains only user/assistant conversational messages and never hidden prompts, reasoning, tool output, or terminal output. Bootstrap uses the same direct, preimage-checked Wiki patches as updates; `--agent-interaction --review` approves each patch, and `--resume` continues an unfinished session, including one stopped by Ctrl-C or `relai runs cancel`. `--discard` removes only the resumable session and captured source state, exits `0`, and prints a one-line confirmation; it does not roll back accepted Wiki writes. It refuses the bootstrap `relai init` runs as its Wiki step (continue it with `relai init --resume` or start again with `relai init --restart`) and any other Wiki update, naming that update's own commands; a session file it cannot read at all is left for `relai wiki update --discard`.

```sh
relai wiki bootstrap
relai wiki bootstrap --agent-interaction --review
relai wiki bootstrap --resume --review --agent-interaction
relai wiki bootstrap --discard
```

### `relai wiki backlinks`

Inspect the registered agent test, evaluator, and benchmark artifacts
grounded in a stable EvalsWiki knowledge ID; a removed (retired) artifact is
not listed. Human output shows artifact kind,
ID, and the artifact record's path from the project root. Use `--json` when
another tool needs the deterministic array of `[id, path]` entries, where the
path is the canonical record path relative to the managed `.relai` directory;
it disambiguates artifact kinds with the same ID.

```sh
relai wiki backlinks <knowledge-id> --json
```

### `relai wiki resolve`

Resolve a first-class EvalsWiki open question from an explicit user answer.
The answer is treated as user intent and reconciled through RELAI's bounded
Wiki update workflow, which may remove the resolved open-question page after
creating or updating the durable requirement. The patch applies directly; pass
`--review` to pause for approval first. A resolution is a Wiki update session:
its pauses name `relai wiki update --resume`, which continues it (as does
`relai wiki resolve open-question --resume`). `--restart` discards only an
unfinished standalone Wiki update (with the queued evidence it was
reconciling), after the question and answer are validated; a paused bootstrap or another workflow's Wiki step is refused with
its own command. Legacy bullets in `hypotheses/requirements.md` are listed but
cannot be resolved this way.

```sh
relai wiki resolve open-question <id> --answer <answer>
relai wiki resolve open-question --resume
```

### `relai wiki list`

Inspect curated EvalsWiki knowledge from the terminal. Requirements are listed
from canonical requirement pages, risks are listed from typed hypothesis
records with priority metadata, and open questions are listed from the
requirement-hypotheses page. Use `--json` for deterministic machine-readable
output. `relai wiki list risks --create-test --risk <id>` starts a
targeted discovery run from a selected hypothesis; `relai wiki list
requirements --create-test --id <id>` creates an agent test from a
requirement, and `relai wiki list open-questions --resolve --id <id> --answer
...` resolves an open question.

```sh
relai wiki list requirements
relai wiki list requirements --create-test --id <id>
relai wiki list risks --lifecycle proposed
relai wiki list risks --json
relai wiki list risks --create-test --risk <id>
relai wiki list open-questions
relai wiki list open-questions --resolve --id <id> --answer <answer>
```

#### Presenting risks

When a workflow adds or updates risk hypotheses (such as `relai init` or
`relai ingest`), read `relai wiki list risks --json` and present its `results`
as a Markdown table in their order (highest priority first). When `total`
exceeds the rows returned, page with `--offset`/`--limit` or state "showing N of
`total`". When the workflow's report names specific risks, show only those rows.

| Risk | What could fail | Triggered by | Impact | Confidence | Triggerability |
| --- | --- | --- | --- | --- | --- |
| `<id>` | `observable_failure` | `trigger` | `impact` | `confidence` | `triggerability` |

Shorten each text cell to one sentence. Add a `Status` column from `lifecycle`
only when the rows differ. After the table, offer
`relai test discover --risk <id>` for the top risk.

### `relai memory`

Manage Markdown memory for the whole agent or an existing tag, component, or evaluator. `read`, `path`, `write`, and `append` each take one scope: `agent`, `tag <NAME>`, `component <NAME>`, or `evaluator <ID>`. `read`, `path`, and `list` are read-only. `write` replaces content and `append` adds content; each accepts exactly one of `--text`, `--file`, or `--stdin`.

Custom tag memory uses `tag ADAPTER::TAG` with `read`, `path`, `write`, or
`append`. `relai memory list` omits custom adapter tags; inspect the catalog
for their names. Like `relai tag list`, it leaves out an agent test or
benchmark whose manifest does not load, lists the rest, and exits nonzero
naming each damaged package.

```sh
relai memory list
relai memory read agent
relai memory path tag regression
relai memory write component planner --text guidance-note
relai memory append evaluator support-policy --file note.md
```

Confirm with the user before `write`, which replaces existing memory; `append`
and the read-only actions need no confirmation.

### `relai tag list`

List known agent test tags. `--verbose` includes agent test file locations. Tag mutation commands are intentionally not public. A benchmark whose samples cannot be counted shows `unavailable` beside its tags and the command exits nonzero with that benchmark's error. An agent test or benchmark whose `task.toml` or `benchmark.toml` does not load is left out and named, and the command exits nonzero; `relai benchmark list` does the same, and selecting by tag, wildcard, or the default pool in `relai simulate` or `relai optimize` fails naming each damaged package while explicit selections still run. Warnings name invalid manifest tags and tags that differ only by case. An agent-test or benchmark proposal cannot introduce two new tags that differ only by case. Updates can retain existing tags, and artifacts can reuse exact registered spellings with legacy case conflicts.

```sh
relai tag list
relai tag list --verbose
```

## Agent tests, evaluators, and benchmarks

### `relai test create`

Create one agent test from either `--prompt` or a paired `--log-file` and `--feedback`. It generates a local Harbor package and validates it with one full simulation; the completion report names that run's `Validation trajectory`. When the reported plan's EvalsWiki citations need a Wiki reconciliation, the CLI agent cites the reconciled Wiki in a fresh plan, and a package that then differs only in its README keeps that simulation instead of running another. Use `--resume` for a paused create workflow, or `--restart` with a new source; do not combine the source options with `--resume`. Use `--timeout <duration|off>` to change the 90m wall-clock limit for one invocation.

Before the CLI agent's first step, RELAI makes the reads every new agent test starts from: the project overview, the agent target's source file, the project adapter in `.relai/harbor/adapter/`, and the EvalsWiki requirement the test comes from (or the requirement list). A `relai test discover` build does the same with the requirements its accepted proposal cites. A read the permission profile would ask about is left to the agent, so these reads never prompt on their own; a resumed run keeps what it read.

```sh
relai test create --prompt test-refund-escalation
relai test create --log-file run.log --feedback missing-escalation-policy
relai test create --prompt test-retries --name retry-policy --agent-target support-agent
relai test create --resume --timeout 2h
relai test create --prompt test-retries --timeout 45m
```

### `relai test update`

Update one existing agent test from a prompt. RELAI first classifies the request using its grounding and current EvalsWiki. It updates the same agent test only when the request is a correction or related extension; an unrelated request is not silently turned into a new agent test. ID, target identity, and tags stay immutable. If intent changes, Wiki reconciliation completes before the staged update is promoted; a staged package that then differs only in its README keeps its passing validation run. As with create, the completion report names the `Validation trajectory`. `--timeout <duration|off>` changes the 90m wall-clock limit for one invocation.

```sh
relai test update refund-routing --prompt handle-documented-escalation-exception
relai test update refund-routing --restart --prompt handle-documented-escalation-exception
relai test update refund-routing --resume
```

### `relai test suggestion`

Generate, list, review, accept, reject, or clear agent test suggestions. `generate` records suggestions against the current branch and commit, so it needs at least one commit and stops before any model work without one; ask the user to commit, then rerun it, or continue a saved run with `relai test suggestion generate --resume`. `accept` runs the `relai test create` workflow for one suggestion; an accepted suggestion whose creation session was discarded is listed again as abandoned. Accept and reject decisions queue their EvalsWiki evidence before the Wiki update; when another Wiki update is unfinished or the Wiki is busy, the decision still succeeds with a warning that it is queued, and the next `relai wiki update` or suggestion decision reconciles it. `clear-memory` clears the selected target's history and discards only that target's unfinished `generate` session.

```sh
relai test suggestion generate --count 5
relai test suggestion list
relai test suggestion review
relai test suggestion accept suggestion-1
relai test suggestion reject suggestion-1 --reason not-relevant
relai test suggestion clear-memory --yes
```

### `relai test discover`

Generate Harbor agent test candidates from EvalsWiki risk hypotheses and current code, then simulate and review them before promoting failure-revealing or useful coverage tests. The completion report lists each created test's simulation trajectory. Run `relai wiki bootstrap` first when the repository does not yet have a bootstrapped EvalsWiki. By default, interactive runs pause after proposal/critique so a human can review the proposed agent test before expensive build/run work; pass `--no-review` only when the user explicitly asks to skip review. With `--agent-interaction`, that review pauses for the coding agent's native question tool instead of being skipped. Use `--risk <id>` to test one curated hypothesis directly. `--timeout <duration|off>` changes the 4h wall-clock limit for one invocation. A paused discovery never resumes implicitly: use `--resume` to continue the saved session or `--restart` to discard it and start over.

`--risk` and `--count` are mutually exclusive. With `--risk <id>`, omit
`--count`, including `--count 1`: the risk selector already targets one
hypothesis. Use `--count <N>` only when searching eligible risks without
`--risk`.

```sh
relai test discover
relai test discover --count 3 --timeout 2h
relai test discover --risk <id> --agent-interaction
relai test discover --count 3 --agent-interaction
relai test discover --resume
relai test discover --restart
```

### `relai evaluator`

Create, update, or remove global evaluators. An evaluator scores only its agent
target's agent tests and benchmarks, plus those without a target, and any
benchmark that names it in `evaluator_refs` whatever its target; its
`evaluator.toml` records the target as `agent_target`. `update` is a copy-on-write,
agentic workflow for a manually edited evaluator: it preserves the evaluator ID
and agent target, and its type unless a code evaluator's criteria now need an LLM
judge; validates a staged revision; refreshes verified EvalsWiki
grounding; then replaces the source. It supports `--agent-interaction`,
`--resume`, and `--restart`. Create writes a local Harbor package. After create or update, summarize the
evaluator from its EvalsWiki page, `.relai/evals-wiki/tests/evaluators/<id>.md`. Its completion summary reports how many current agent tests and benchmark samples it applies to (`Applies to`); report a zero count to the user, since the evaluator does not run until a matching agent test or benchmark exists.
Confirm with the user before `remove`; it deletes the evaluator. `remove` refuses
an evaluator that a benchmark names in `evaluator_refs` until that benchmark
stops naming it; a benchmark that had evaluators must keep one, so when it is
the only evaluator, update the benchmark to replace it rather than remove it.
A rerun finishes an interrupted removal.

```sh
relai evaluator create --prompt judge-policy-accuracy --name support-policy
relai evaluator create --prompt judge-policy-accuracy --agent-target support-agent
relai evaluator update --id support-policy --prompt add-citation-coverage
relai evaluator update --resume --agent-interaction
relai evaluator remove --id support-policy
```

### `relai benchmark`

Register, update, list, or remove CSV-backed benchmarks. Registration and updates are local agentic workflows with EvalsWiki grounding; inspect the CSV and working tree first. `--evaluator-ref` may be repeated; each must be a file inside the repository, and the benchmark's scoring must apply the evaluation it defines. Static candidate validation materializes one representative sample and uses the runtime evaluator resolver, so publication rejects invalid or missing `evaluator_refs`, scope-incompatible referenced evaluators, and referenced IDs that collide with inline evaluators. Existing registered packages remain readable so an update can repair a broken reference, but the replacement must pass current validation. Registration validation also runs the first and last CSV rows and requires an evaluator score from each; an update of a benchmark that had evaluators must keep them scoring the same way (it may replace evaluators, never remove them all), while a benchmark registered without evaluators stays exempt. The completion summary reports the sample count. An update whose request needs a different dataset pauses for a replacement CSV path; answer it with the user's project-relative CSV path. Confirm with the user before `remove`; it deletes the benchmark.

```sh
relai benchmark register --csv data.csv --name support-suite
relai benchmark register --csv data.csv --evaluator-ref evaluator.md --prompt judge-support-quality --agent-target support-agent
relai benchmark register --resume --timeout 2h
relai benchmark list
relai benchmark update --id support-suite --prompt extend-suite-policy
relai benchmark update --id support-suite --csv data-v2.csv --prompt replace-dataset
relai benchmark remove --id support-suite
```

## Coding-agent plugins

### `relai plugins install`

Replace the complete bundled Codex and Claude Code plugin sources under `~/.relai/plugins/`, then configure the selected hosts. Cursor uses `~/.cursor/plugins/local/relai`; GitHub Copilot uses one directory per skill under `~/.copilot/skills/`. `--agent` accepts `all` (the default), `codex`, `claude`, `cursor`, or `copilot`. Neither host executable nor an authenticated session is required. `relai update` also refreshes previously configured plugins. Each host is installed independently; when one fails, the others still are, and the command names each failed host and exits non-zero. Start a new Codex or Cursor session (or restart the app) before verifying RELAI skills. In Claude Code, run `/reload-plugins`, then verify RELAI skills. Use an interactive GitHub Copilot session; cloud-agent and other headless sessions are unsupported.

```sh
relai plugins install
relai plugins install --agent codex
relai plugins install --agent claude
relai plugins install --agent cursor
relai plugins install --agent copilot
```

New Harbor tasks include a `README.md` file guide (an agent test's README is the
same human summary recorded in EvalsWiki), an editable
`environment/scenario.json`, evaluators declared in `task.toml` (code in the
verifier `tests/evaluate.py`, LLM judges as `tests/evaluator.toml` with a
rubric), and generated packaging under `generated/`. Preserve authored task
behavior when editing a task by hand, and route environment repairs through
`relai init`. When a task's `spec.install_secrets` names private-registry
credentials, the user sets their values in `.relai/simulator.env` or the
environment.
