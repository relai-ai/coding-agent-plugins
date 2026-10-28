---
name: relai-ingest
description: Use when the user wants RELAI to ingest a folder of agent traces, transcripts, logs, or other context into EvalsWiki.
metadata:
  relai-cli-version: "0.2.14"
  relai-skills-revision: "17c39e03dcd25819"
---

> **RELAI version check.** This skill matches skills revision `17c39e03dcd25819` (RELAI CLI 0.2.14). Once per session, before following it, run `relai guide --revision`:
>
> - Same `skills_revision`: follow this skill as written.
> - Different `skills_revision`: run `relai guide relai-ingest --agent codex` and follow its output instead of this file; the user does not need to do anything. If the printed `cli_version` is older than 0.2.14, suggest `relai update` once so they also get this plugin's newer features.
> - `relai guide` is not a command: this RELAI CLI predates the check. Ask the user to run `relai update`, then continue.
> - `relai guide` fails any other way, for example on an unknown workflow: follow this skill as written and tell the user the error once.

# RELAI folder ingestion

Use `relai ingest` for a folder of source evidence the user wants curated into
EvalsWiki. For a bounded decision or correction from the current coding-agent
conversation, use `relai wiki update` instead. For one run log paired with
feedback to create an agent test, use `relai test create`.

If `command -v relai` finds nothing, use the `relai-cli` skill, which asks
the user to install the CLI and then signs in, before continuing.

Read `references/relai-cli-commands.md` and inspect `relai ingest --help` for
the installed CLI. From the project root, confirm `.relai/config.toml` and
`.relai/evals-wiki/` exist; use `relai wiki bootstrap` if the Wiki is missing.
Inspect the source folder and run `relai ingest <folder> --agent-interaction`,
adding `--note` only when it helps disambiguate the trace set or goal. The
source folder is read only. Selected excerpts are stored under
`.relai/evals-wiki/attachments/traces/<ingestion-id>/`.

An explicit `--restart` discards the unfinished session but does not roll back
durable Wiki or attachment writes.

With `--review`, RELAI pauses before applying Wiki patches. Risk hypothesis
updates and selected attachments can still be written before patch approval.
Under `accept_edits` or `ask`, each analysis-script run also pauses for
approval; the resume keeps the session's permissions profile.
Present the structured completion report, including changed knowledge and
remaining questions; show added or updated risks as the table in the command
reference's "Presenting risks" section. For `action_required`, use the host's native question
tool and the exact supplied resume command and interaction response.
