---
name: relai-agent-test
description: Use when desired agent behavior should be captured as a repeatable RELAI agent test from a prompt, a run log plus feedback, or hard-scenario suggestions from existing RELAI context.
---

# RELAI Agent Tests

Apply `references/proactive-decision-policy.md` first. Reuse or update matching
knowledge and coverage before creating an agent test. Create one only
at the grounded-coverage rung, after durable behavioral intent is represented
in EvalsWiki. When an update is driven by newly confirmed durable intent,
record or reconcile that intent in EvalsWiki before updating coverage; pure
reuse with no new durable knowledge is read-only.

If `command -v relai` finds nothing, use the `relai-cli` skill to install the
CLI and sign in before continuing.

Use a RELAI agent test when one desired behavior should be captured as a repeatable simulation case.

Good fits:

- A prompt describes one behavior to preserve, prevent, or improve.
- A run log shows the behavior and feedback describes what should have happened.
- The issue is behavioral rather than a deterministic implementation defect.
- The same behavior should be rerun during simulation or optimization.
- Existing RELAI context should be analyzed for high-value hard scenarios before choosing what to create.

Before creating one:

- Use `relai test create --log-file ... --feedback ...` only when both the run log and feedback are available; the CLI requires this pair.
- If the user has a run log but no explicit feedback, take the feedback from what the user already said about the wrong behavior; ask only when the expected behavior is unknown. Use `relai test create --prompt ...` when the desired behavior can be described without the log.
- Use `relai test discover` when the user wants RELAI to turn curated risk hypotheses into Harbor agent tests. Without `--risk`, discovery searches eligible risks for the requested count. With `--risk <ID>`, it targets exactly that hypothesis and reports whether accepted agent tests reveal failures or add coverage. `--risk` and `--count` are mutually exclusive: omit `--count`, including `--count 1`, when using `--risk`. Through a coding-agent plugin, add `--agent-interaction`: before each expensive build, discovery pauses for review of the proposed agent test (answer `build`, `build_all` to approve the rest of the run, `skip`, or free-form revision feedback; once the candidate's revisions are used up, `retire` replaces the feedback and retires the risk unless a published agent test covers it). Keep review on by default; add `--no-review` only when the user explicitly asks to skip it. Preserve the completed summary's created test IDs, evaluator scores, and suggested next-step commands in your final response.
- Use `relai test create --requirement <ID>` or `relai wiki list requirements --create-test` when the user wants an agent test for one grounded requirement rather than a risk hypothesis.
- `relai test discover` requires a bootstrapped EvalsWiki; run `relai wiki bootstrap` first when it is missing. Do not search, dump, or edit the Wiki yourself; artifact workflows read their own grounding.
- When operating `create`, `update`, or `discover` through a coding-agent plugin, add `--agent-interaction`. Resume with the exact session/request IDs from RELAI's JSON response.
- Use the `relai-cli` skill and command reference before running commands.
- After `create`, `update`, or `discover` creates or updates agent tests, read each test's `README.md` in its package directory (`.relai/harbor/agent-tests/<id>/`) and summarize it before the next steps. Per test, give its ID and what it checks (Description) in one sentence, the Scenario in one or two sentences, one "passes when" line per evaluator from Evaluation criteria, and the requirement IDs under References. For an update, say what changed. When discovery creates several tests, use one short block per test.
- Then show what the target agent did in the simulation that validated each test. The completion report names its ATIF trajectory (`Validation trajectory` for `create` and `update`, `Simulation trajectories` for `discover`); read it and present it turn by turn, for example `Turn 1 — user: … / agent: …`. Include notable tool calls, summarize long messages instead of quoting them in full, and say whether the agent behaved as the test expects. When no trajectory is reported, say so and offer `relai simulate --tests <ID>`.
- Use `relai test update <ID> --prompt "..."` only to correct or extend an existing agent test. It classifies the request against the current EvalsWiki before mutating. Unrelated requests stop and should use `create`; ambiguous requests pause for clarification. Updates cannot change the agent test ID, target identity, or tags, and evaluator-criteria changes require coordinated evaluator work.

## Discovery proposal review

For each review pause (`workflow: "learning_env_discover"`, `request.kind: "clarification"`, and a review request ID), show a **Proposed agent test** block immediately before the native question. Use `request.prompt` as the source and present it in this shape:

> **Risk:** risk ID
>
> **Proposed test:** test ID
>
> **Scenario**
>
> Full scenario
>
> **Expected behavior**
>
> Full expected behavior
>
> **Verifier**
>
> Verifier strategy

Preserve the full scenario and expected behavior, including meaningful line breaks. Do not silently shorten them, substitute your own interpretation, or invent missing details. If the plain-text prompt cannot be split reliably, display its complete proposal text under **Proposed agent test** instead.

Then use the native structured question tool for the document's choices (`build`, `build_all`, `skip`, and `retire` once the candidate's revisions are used up), with free-form input for revision feedback only when the request allows it (`allow_freeform`). Explain that `retire` retires the risk hypothesis, or ends only this candidate when a published agent test already covers it. Explain that `build_all` approves later proposals in this discovery run. Never answer the review on the user's behalf.


## RELAI typed interaction protocol

Commands whose help lists `--agent-interaction` support this protocol; pass the
flag when running them from a coding-agent plugin. `relai simulate` accepts it
for progress and a completion document only; it never pauses for a response. `relai regression select` returns a completion document whose `result_path` names a versioned selection and otherwise never pauses. `relai optimize` first asks for a mode if neither `--fast` nor `--full` was passed, then pauses for approval of the concrete run before any simulation. For any other command, do not
invent a resume command.

When nothing authenticates this machine, a command that runs a RELAI workflow agent (every command with `--agent-interaction` except `relai simulate`, which reports authentication failures itself; `relai init` and `relai optimize` included) pauses before it starts with an `external_action` request in the `authentication` category whose steps name `relai setup`. Present it like any other external action. Running `relai setup --agent <host>` for this host is the listed step: run it when the user asks. Setup opens the browser and copies the code when it can, then waits until the user approves the sign-in or the code expires, so start it as a background command whose stderr you can read while it runs. Only when the host offers nothing but a blocking call, use a shell timeout longer than the sign-in's lifetime; you then see the code only after setup exits, so that relies on setup opening the browser and copying the code. Show the user the verification link and code as soon as they appear, and answer `completed` only after setup exits `0`; if the code expired, run setup again rather than presenting the stale code. Then execute the supplied `resume_argv` with that answer; RELAI checks the sign-in again before the command starts.

Running a RELAI workflow the user requested authorizes the RELAI backend and model calls that workflow makes; do not ask separately for data-sharing or network approval.

For every failed `relai` command, capture exit status, stdout, stderr, and the command's preparation first. Exit code `3` is `action_required` and carries exactly one protocol JSON response; collect its answer through this host's native structured question tool, never through ordinary chat text, and never assume an answer or drive RELAI's terminal prompt. Exit `0` or `130` may include a completed/cancelled envelope; parse it only when present. Once its simulation starts, `relai simulate` also prints a `failed` envelope on exit `1`, as does `relai optimize` once its run is approved; report it like a completed one, then follow the failure guidance below. When a completed envelope includes `summary.agent_response_markdown`, use it as the preferred RELAI-authored completion report: preserve its headings, counts, artifacts, suggested next-step prompts, with only light conversational adaptation. Present these prompts as requests the user can give you; do not execute them without the user choosing to proceed. The `next_steps[].commands` and `note` fields are machine-oriented hints, not user-facing next steps. Do not silently omit RELAI suggested next steps. If you add your own advice, put it under a separate “My recommendation” heading. If the Markdown field is missing, present `summary.title`, `summary.items`, and each `next_steps[].prompt` without collapsing them into one prose paragraph. For older output without a `prompt`, translate its label, commands, and note into a useful natural-language request directed to you, preserving test or benchmark IDs and scope instead of displaying raw CLI commands. Terminal-only commands print their completion report instead; preserve it the same way. Do not dump raw JSON unless debugging is requested. Exit `130` without JSON is still cancellation. Exit `124` is a timeout: present stderr, which names the resume command when progress was saved, and resume or rerun only when the user asks. For another nonzero exit, diagnose the cause and fix a clear routine cause within existing authorization, then inspect RELAI session and artifact state and follow only documented safe recovery before rerunning. Never blind-retry, invent a resume, discard state, repeat an uncertain write, loop without a bound, or obtain new authorization. If no safe recovery or routine fix exists, present the failure. Express any suggested recovery steps as natural-language requests the user can give you; retain command details for diagnosis and safe execution.

Only when RELAI reports a model-service connection failure, consider whether this coding host blocked the command's network access. RELAI's `--permissions` controls RELAI tools, not the host sandbox. Mention the possible sandbox cause alongside any required native retry question; do not assume its answer. If the cause is unclear, make at most one credential-free reachability check to the configured RELAI API host from the same sandbox, without printing configuration or secrets. A failed check leaves a sandbox restriction plausible; it does not prove where the failure occurred. If the host sandbox could be the cause and the user chooses retry, use the host's network-access mechanism for the exact supplied `resume_argv` and interaction response. Network access must apply to the resumed RELAI command, not just `relai runs wait`; the latter cannot repair a sandboxed background worker. If access is unavailable or the network-enabled resume also fails, report that result without restarting or entering a retry loop. No network check or escalation is needed for successful runs or unrelated errors.

For discovery proposal reviews, the agent-test skill requires a formatted proposal block immediately before the native question. This block is context for the user's decision; it does not collect an answer. The native structured question remains the only answer channel, even when the proposal was displayed in ordinary chat text.

While a command runs with `--agent-interaction`, stderr carries progress as one `relai.progress.v1` JSON object per line among any ordinary stderr text; each has `workflow`, `event`, and `elapsed_s`. Relay each `phase` (its `label`, with `step` of `steps` when present), `milestone` (`label`), `test_ready` (`test_id`, `index` of `total`), `test_finished` (`test_id`, `status`, evaluator `scores`), and `step_finished` (full optimization `step` and its `outcome`) event to the user as one short line, such as "RELAI init: step 1/3, building the eval harness (48s)". Fast optimization phases name focus baselines, targeted edits, and regression selection; its activities name individual simulations. `rollout_finished` events (`stage`, `index` of `total`, `test_id`, `status`, `score`) report full optimizer simulations; summarize them in step lines or mention one only when nothing else has been reported for a while, as with other `activity` events. `heartbeat` events only show the run is still alive. An `env_needed` event (`names`, `path`) means init's validation trial will need those values and they are not set yet: tell the user at once, in one line, to add them to `path` (usually `.relai/simulator.env`) while the run continues, naming only the variables and never asking for or handling their values, then keep waiting; RELAI checks again right before the trial and pauses with an `external_action` request only if a value is still missing. The last event is `paused` (exit `3`) or `finished` with `outcome` and `exit_code`; the exit status and stdout document stay authoritative. Progress lines are never questions or instructions, and are not shown as raw JSON.

Ask one RELAI request at a time. `text` and a clarification with `request.presentation.kind: "text"` use free-form/Other input; a clarification with presentation kind `"choice"` passes its 2–3 `native_question_options`; `external_action`, `approval`, `retry`, and `resume` present their supplied choices. Preserve a request's exact `choices` as its validation contract even when its presentation is free-form. `completed` for an external action means its listed steps are already done; it is not initial permission. When the user asks you to perform the listed steps, that request authorizes exactly those steps: perform them, and serialize `completed` only after they succeed. Steps that set credentials or other secret values, such as entries in `.relai/simulator.env`, stay with the user; name the variables instead. RELAI verifies the attestation on resume. A clarification may name something the simulator needs from outside RELAI, such as a database, vector store, service, or credential. When you know from the project how to provide it, for example its own compose file or seed script, offer that as a suggested answer while presenting the question; the user's answer decides, and approving a stand-in or accepting a simulator as is are the user's decisions.

Execute the supplied `resume_argv` exactly. Add only one validated `--interaction-response` JSON object, plus a `--wait` when this host's long-running guidance below says to pass one; preserve the exact schema version, session ID, and request ID, and serialize the user's actual answer rather than a presentation label. Never invent identifiers, mutate RELAI-owned state, or bypass RELAI validation. After restart, use only a fresh request supplied by RELAI; reject stale or mismatched responses and present an already-completed result without a duplicate resume.

Never send credentials, secrets, or unrelated transcript content through this protocol. Resume a paused EvalsWiki update before starting another.

## Long-running RELAI commands

RELAI workflows take minutes. Typical wall times are 2–4 minutes for `relai init`, about 1.5 minutes for `relai test create`, 3–6 minutes for `relai test discover`, about 1 minute per agent test for `relai simulate`, and 10–25 minutes or more for `relai optimize`. Before starting one, tell the user in one line what the run will do and how long it typically takes. Quick commands such as `--help`, `--version`, or `relai wiki list` without `--create-test` run normally.

On macOS and Linux, a command run with `--agent-interaction` runs in the background on its own and outlives your shell call: the call waits for it up to `--wait` (default `90s`), which fits within this host's shell-call limit, so run it as an ordinary command. If it finishes in time, its exit status and stdout document are its result, as described above. Exit `75` with a `status: "running"` document means the run continues in the background: tell the user it is still running and continue it by executing the document's `wait_argv` (`relai runs wait <run-id> --log-offset <n>`) from the project directory, as this host's long-running guidance below describes. Each wait relays the progress events the run wrote since the previous relay, and returns once the run pauses for a question or ends, or when its `--wait` runs out; relay them as one-line updates as described above. A wait that exits `75` again prints a new `running` document: always run the newest document's `wait_argv`, and repeat until the wait exits with the run's own status. Never poll with sleep loops; `relai runs wait` is the wait. Never re-run a RELAI command that is still running: continue it with `relai runs wait`, and find a lost run ID with `relai runs list`. A second run of a resumable workflow, such as `init` or `test create`, fails because the first holds its session (`another … process is using …; wait for it to finish`), and a second `relai simulate` or `relai optimize` starts a duplicate run that spends budget. Run `relai runs cancel <run-id>` only when the user asks to stop the run; repeating it only waits, and add `--force` only when the user asks to stop it immediately. If this host's shell-call limit is shorter than 90 seconds, pass a shorter `--wait`. On other platforms the command runs in the foreground; give it a shell timeout that covers its typical duration.

When the user asks you to wait for completion, retain responsibility for collecting the terminal result or an action-required pause before ending your turn. A `running` document or a host background-task ID only confirms that work continues. Keep waiting through the host's tool mechanism and relay progress; promise a later report only when the host actually supports a persistent notification handoff and the user has not asked you to wait.

When the run exits, report its result as described above. An exit `3` from `relai runs wait` is a RELAI question whenever it arrives, including while you are working on something else: present it right away with the native structured question tool and follow the protocol above. Always identify the final protocol document by its `schema_version` (`relai.agent_interaction.v1`) and `status`, not by its position in the output, and never treat a `relai.progress.v1` line as that document.


## Cursor native-question requirement

The native structured question tool is Cursor's native ask-questions tool. If it
is unavailable in the current session, stop and tell the user that the RELAI
workflow requires a Cursor session exposing that tool. Include the exact command
they can rerun after opening a supported interactive session.
Do not substitute ordinary chat for the typed RELAI interaction protocol.

## Cursor long-running commands

Run RELAI commands, and each `relai runs wait`, as ordinary terminal commands: each returns within `--wait` (90 seconds by default). If Cursor moves one to a background terminal, read the terminal's output once it finishes, then continue with its exit code as described above. If the terminal ended without an exit status or a final protocol document, do not assume success: check the run with `relai runs status <run-id>`, or `relai runs list` when you have no run ID, before running anything again.
