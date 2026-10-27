---
name: relai-wiki
description: Capture durable project decisions, corrections, constraints, preferences, and useful hypotheses from coding-agent conversations into the RELAI EvalsWiki.
metadata:
  relai-cli-version: "0.2.13"
  relai-skills-revision: "32570166274ff546"
---

> **RELAI version check.** This skill matches skills revision `32570166274ff546` (RELAI CLI 0.2.13). Once per session, before following it, run `relai guide --revision`:
>
> - Same `skills_revision`: follow this skill as written.
> - Different `skills_revision`: run `relai guide relai-wiki --agent claude` and follow its output instead of this file; the user does not need to do anything. If the printed `cli_version` is older than 0.2.13, suggest `relai update` once so they also get this plugin's newer features.
> - `relai guide` is not a command: this RELAI CLI predates the check. Ask the user to run `relai update`, then continue.
> - `relai guide` fails any other way, for example on an unknown workflow: follow this skill as written and tell the user the error once.

# RELAI Wiki updates

Apply `references/proactive-decision-policy.md` before invoking this workflow.
Use this workflow for the Wiki-only checkpoint or as the required durable
knowledge predecessor to grounded coverage and updates driven by newly
confirmed durable intent; do not use it for the no-action rung.

When a user states a durable decision, correction, constraint, preference, or a useful hypothesis emerges from completed work, invoke `relai wiki update --agent-interaction --evidence-json -` proactively, but only in an initialized RELAI project: confirm the project-local `.relai/config.toml` exists. A missing `.relai/evals-wiki` is fine: the updater bootstraps it lazily. Do not search or edit `.relai/evals-wiki` yourself: RELAI owns retrieval, conflict detection, and mutation.

Generate one opaque UUID for each logical checkpoint and keep it if the command is retried. Pass only the relevant bounded message excerpt as the versioned JSON envelope on stdin; `evidence_id` is required and RELAI rejects reusing it with changed content. Use the typed coding-agent source payload below. Inspect the structured outcome: `updated` means RELAI changed the local Wiki; `no_change` means the evidence was already represented or transient. If the update pauses, resolve its single resumable session through the supplied resume command before starting another update.

```json
{"schema_version":"relai.wiki_evidence.v1","evidence_id":"<stable-uuid>","source":{"kind":"coding_agent","agent":"<coding-agent>","messages":[{"role":"user","content":"Relevant durable decision excerpt."}],"changed_paths":["src/example.rs"]}}
```

In the default automatic mode, `action_required` represents a semantic conflict or ambiguity. An explicit `--review` invocation may instead request approval for a proposed action. Present either through the host's native question tool and resume with RELAI's supplied argv and interaction response. Artifact workflows independently re-read and validate current grounding before they write or publish.

Use `relai wiki list requirements`, `relai wiki list risks`, and `relai wiki list open-questions`
for read-only inspection. Requirements are grounded enough for eval design; open
questions are unresolved ambiguities. Risk hypotheses are falsifiable ideas for
agent test discovery, and can be sent directly to
`relai test discover --risk <ID>` or selected with
`relai wiki list risks --create-test`. A requirement can be turned into a
agent test with `relai wiki list requirements --create-test` or
`relai test create --requirement <ID>`. When the user answers an
open question, resolve it with `relai wiki resolve open-question <ID> --answer
<ANSWER>`; the resulting Wiki patch applies directly unless `--review` is passed.

Cancelled, failed, incomplete, and explicitly unresolved updates are not applied.

When a requirement change leaves an artifact grounding stale, invoke `relai wiki
reconcile --agent-interaction`. RELAI reviews the persisted assertions against
the changed requirement for every affected artifact, refreshes only a semantic
`still_valid` result through guarded preimage checks, and hands required edits
to the artifact's staged update workflow. Resume a pause with `relai wiki
reconcile --resume --agent-interaction`; coverage reduction and retirement stay
with the user for an explicit decision.

Do not invoke the workflow for temporary plans, routine progress, raw transcripts, or secrets.
