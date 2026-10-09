---
name: relai-overview
description: Use when deciding whether a request should be handled by direct implementation or by a RELAI workflow, or when the user asks what RELAI is for.
---

# RELAI Overview

RELAI helps teams improve agents by turning observed behavior and feedback into repeatable agent tests, running simulations, and optimizing against measured outcomes.

Use `references/proactive-decision-policy.md` as the decision ladder and its
examples.

## Core loop

1. Initialize the project with a simulator harness.
2. Capture behavior as agent tests, evaluators, or benchmarks.
3. Simulate current behavior against those repeatable cases.
4. Optimize the agent against the selected cases.

## Triage

Apply the decision ladder to the completed conversation and resulting change.
When the user supplies a folder of traces or context to curate into EvalsWiki,
route that explicit request to `relai-ingest`.
Explain any material RELAI action and unresolved grounding gap. The ladder
controls whether to take no action, checkpoint EvalsWiki, reuse coverage,
create grounded coverage, or run a targeted simulation.
