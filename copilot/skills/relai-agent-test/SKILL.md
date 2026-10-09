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
- Use `relai test discover` when the user wants RELAI to turn curated risk hypotheses into Harbor agent tests. Without `--risk`, discovery searches eligible risks for the requested count. With `--risk <ID>`, it targets exactly that hypothesis and reports whether accepted agent tests reveal failures or add coverage. `--risk` and `--count` are mutually exclusive: omit `--count`, including `--count 1`, when using `--risk`. Through a coding-agent plugin, add `--agent-interaction`: before each expensive build, discovery pauses for review of the proposed agent test (answer `build`, `build_all` to approve the rest of the run, `skip`, or free-form revision feedback). Keep review on by default; add `--no-review` only when the user explicitly asks to skip it. Preserve the completed summary's created test IDs, evaluator scores, and suggested next-step commands in your final response.
- Use `relai test create --requirement <ID>` or `relai wiki list requirements --create-test` when the user wants an agent test for one grounded requirement rather than a risk hypothesis.
- `relai test discover` requires a bootstrapped EvalsWiki; run `relai wiki bootstrap` first when it is missing. Do not search, dump, or edit the Wiki yourself; artifact workflows read their own grounding.
- When operating `create` or `discover` through a coding-agent plugin, add `--agent-interaction`. Resume with the exact session/request IDs from RELAI's JSON response.
- Use the `relai-cli` skill and command reference before running commands.
- After `create`, `update`, or `discover` creates or updates agent tests, read each test's `README.md` in its package directory (`.relai/harbor/agent-tests/<id>/`) and summarize it before the next steps. Per test, give its ID and what it checks (Description) in one sentence, the Scenario in one or two sentences, one "passes when" line per evaluator from Evaluation criteria, and the requirement IDs under References. For an update, say what changed. When discovery creates several tests, use one short block per test.
- Then show what the target agent did in the simulation that validated each test. The completion report names its ATIF trajectory (`Validation trajectory` for `create` and `update`, `Simulation trajectories` for `discover`); read it and present it turn by turn, for example `Turn 1 — user: … / agent: …`. Include notable tool calls, summarize long messages instead of quoting them in full, and say whether the agent behaved as the test expects. When no trajectory is reported, say so and offer `relai simulate --tests <ID>`.
- Use `relai test update <ID> --prompt "..."` only to correct or extend an existing agent test. It classifies the request against the current EvalsWiki before mutating. Unrelated requests stop and should use `create`; ambiguous requests pause for clarification. Updates cannot change the agent test ID or target identity, and evaluator-criteria changes require coordinated evaluator work.


## RELAI typed interaction protocol

Commands whose help lists `--agent-interaction` support this protocol; pass the
flag when running them from a coding-agent plugin. For any other command, do not
invent a resume command.

Running a RELAI workflow the user requested authorizes the RELAI backend and model calls that workflow makes; do not ask separately for data-sharing or network approval.

For every failed `relai` command, capture exit status, stdout, stderr, and the command's preparation first. Exit code `3` is `action_required` and carries exactly one protocol JSON response; present it through this host's native structured question tool, never as ordinary chat text, and never assume an answer or drive RELAI's terminal prompt. Exit `0` or `130` may include a completed/cancelled envelope; parse it only when present. When a completed envelope includes `summary.agent_response_markdown`, use it as the preferred RELAI-authored completion report: preserve its headings, counts, artifacts, suggested next steps, and commands, with only light conversational adaptation. Do not silently omit RELAI suggested next steps. If you add your own advice, put it under a separate “My recommendation” heading. If the Markdown field is missing, present `summary.title`, `summary.items`, and `next_steps` without collapsing them into one prose paragraph. Terminal-only commands print their completion report instead; preserve it the same way. Do not dump raw JSON unless debugging is requested. Exit `130` without JSON is still cancellation. Exit `124` is a timeout: present stderr, which names the resume command when progress was saved, and resume or rerun only when the user asks. For another nonzero exit, diagnose the cause and fix a clear routine cause within existing authorization, then inspect RELAI session and artifact state and follow only documented safe recovery before rerunning. Never blind-retry, invent a resume, discard state, repeat an uncertain write, loop without a bound, or obtain new authorization. If no safe recovery or routine fix exists, present the failure.

Ask one RELAI request at a time. `text` and a clarification with `request.presentation.kind: "text"` use free-form/Other input; a clarification with presentation kind `"choice"` passes its 2–3 `native_question_options`; `external_action`, `approval`, `retry`, and `resume` present their supplied choices. Preserve a request's exact `choices` as its validation contract even when its presentation is free-form. `completed` for an external action means its listed steps are already done; it is not initial permission. When the user asks you to perform the listed steps, that request authorizes exactly those steps: perform them, and serialize `completed` only after they succeed. Steps that set credentials or other secret values, such as entries in `.relai/simulator.env`, stay with the user; name the variables instead. RELAI verifies the attestation on resume.

Execute the supplied `resume_argv` exactly. Add only one validated `--interaction-response` JSON object; preserve the exact schema version, session ID, and request ID, and serialize the user's actual answer rather than a presentation label. Never invent identifiers, mutate RELAI-owned state, or bypass RELAI validation. After restart, use only a fresh request supplied by RELAI; reject stale or mismatched responses and present an already-completed result without a duplicate resume.

Never send credentials, secrets, or unrelated transcript content through this protocol. Resume a paused EvalsWiki update before starting another.


## GitHub Copilot native-question requirement

The native structured question tool is GitHub Copilot's `ask_user`. Use this
only in an interactive GitHub Copilot session where `ask_user` is available.
Cloud-agent and other headless sessions are unsupported because no user can
answer the request. Stop with that actionable explanation when the tool is
unavailable; do not claim live-workflow parity and do not substitute ordinary
chat for the typed RELAI interaction protocol.
