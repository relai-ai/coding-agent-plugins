---
name: relai-cli
description: Use when the user asks to operate any public RELAI CLI workflow, including setup, init, ingest, agent tests, benchmarks, evaluators, simulation, optimization, memory, tags, plugin marketplaces, shared proactive policy, updates, or shell completions.
---

# RELAI CLI

Use the RELAI CLI command reference in `references/relai-cli-commands.md` before running `relai` commands. It covers every visible release command; do not suggest hidden or debug-only commands. RELAI turns feedback into agent tests, runs agent simulations, evaluates outcomes, and optimizes agents against repeatable scenarios.

If the user asks for a RELAI workflow, inspect the repository state, use `relai --help` or nested help to confirm available commands/options, then choose the narrowest supported command. Treat help output as the source of truth for the installed CLI version.

Resolve CLI-managed paths from the project layout marker. When
`.relai/.internal/layout.json` exists, use `.relai/.internal/`; otherwise the
project is legacy and the same paths live directly under `.relai/`.

## Authentication: OAuth

Use OAuth device authorization for setup. Do not ask the user for a RELAI API
key as a prerequisite to `relai setup` or `relai init`.

Run `relai setup --agent <codex|claude|cursor|copilot>` and select the host running this skill; for a user-selected backend, also use `--api-url <requested-endpoint>`. This explicit selection works without invoking or authenticating the coding-agent executable. Setup reuses a usable RELAI OAuth session and starts browser sign-in only when one is needed. Use `--reauthenticate` only when a fresh RELAI OAuth sign-in is needed. Restart or reload the selected host after installation, then verify the RELAI skills are available.

Core rules:

- Run from the user's repo root unless they specify another path.
- Follow the command reference's host-prerequisite guidance before dependent workflows. Ask the user to install missing required host tools or start required services; keep task-image dependency repair in the owning RELAI workflow.
- To check whether the current repo is initialized for RELAI, confirm `.relai/config.toml` and `.relai/harbor/` exist; when the requested workflow requires initialization and they are missing, run `relai init`. Use `relai --version` only to confirm the installed binary identity.
- Use `relai <command> --help` or `relai <command> <subcommand> --help` before constructing commands you have not already confirmed.
- Each workflow's skill or command-reference section names the actions that need the user's confirmation; everything else runs without asking.
- Never invent unsupported `relai` flags or hidden commands.
- After a successful `relai init`, inspect only existing regular, non-symlink root `AGENTS.md` and `CLAUDE.md` files for the current managed RELAI policy marker. Ignore symlinks when deciding whether to install. If no regular target exists, explain that the policy cannot be installed because RELAI never creates instruction files or follows symlinks. If every regular target has the marker, no installation is needed. If any regular target lacks it, run `relai policy install` automatically without asking for confirmation. Do not edit instruction files to install or change the policy.
- RELAI's workflow agents follow project instructions for RELAI: the `## RELAI` section of each `AGENTS.md` and every `RELAI.md`, from the repository root down to the working directory. `CLAUDE.md` is never read as RELAI instructions. When the user says how RELAI itself should work in this repository, such as which dataset or evaluator to use, which files RELAI must not change, or how to confirm a failure, propose adding it there rather than to the EvalsWiki or `relai memory`, and ask before editing. Keep target-agent behavior in the EvalsWiki. Put rules that must always hold, such as never reading a held-out split, in `.relai/config.toml` read or write permissions; instructions guide RELAI's workflow agents but cannot loosen permissions or budgets. See "Project instructions for RELAI" in the command reference.
- Keep secrets, `.relai/config.toml`, `.relai/simulator.env`, `.relai/.internal/runs/`, and generated caches out of summaries unless the user explicitly asks.
- Follow the RELAI typed interaction protocol below for exit codes, completion reports, and failures. An `action_required` response **must** use this host's native structured question tool, and resumes add only `--interaction-response`, preserving the exact session and request IDs. Some workflows, including `relai optimize`, are terminal-only and do not support `--agent-interaction`; preserve their terminal completion report.
- After `relai evaluator create` or `relai evaluator update` completes, read the evaluator's EvalsWiki page (`.relai/evals-wiki/tests/evaluators/<id>.md`) and summarize it: its ID and what it judges (Description) in one sentence, where it applies (Scope and applicability), its type, and one "passes when" line from Evaluation criteria. For an update, say what changed.
- `init` may ask for multiple discovered logical targets. Collect the exact target names as comma- or newline-separated free-form text; an empty answer registers none. Do not silently select only the first target.
- After successful `relai init`, present its risk hypotheses as the table in the command reference's "Presenting risks" section. Users can inspect curated EvalsWiki material with `relai wiki list requirements`, `relai wiki list risks`, and `relai wiki list open-questions`. To generate tests, use `relai wiki list risks --create-test`, `relai test discover --risk <ID>`, `relai wiki list requirements --create-test`, or `relai test create --requirement <ID>`. To resolve an open question, use `relai wiki resolve open-question <ID> --answer <ANSWER>` or `relai wiki list open-questions --resolve`.
- Never collect API keys, passwords, tokens, or other secrets through chat or `--interaction-response`. When values are missing, tell the user which variable names to set and where: `.relai/simulator.env`, which RELAI loads automatically, or the shell environment for temporary runs or CI. Do not create, open, or edit that file for them.


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
