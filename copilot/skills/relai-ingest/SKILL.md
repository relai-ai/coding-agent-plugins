---
name: relai-ingest
description: Use when the user wants RELAI to ingest a folder of agent traces, transcripts, logs, or other context into EvalsWiki.
---

# RELAI folder ingestion

Use `relai ingest` for a folder of source evidence the user wants curated into
EvalsWiki. For a bounded decision or correction from the current coding-agent
conversation, use `relai wiki update` instead. For one run log paired with
feedback to create an agent test, use `relai test create`.

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
Present the structured completion report, including changed knowledge and
remaining questions; show added or updated risks as the table in the command
reference's "Presenting risks" section. For `action_required`, use the host's native question
tool and the exact supplied resume command and interaction response.
