# RELAI plugin

RELAI helps you continuously evaluate and optimize an AI agent. This plugin
gives your coding agent skills for running RELAI workflows through the `relai`
command-line tool: turning the behavior you expect into agent tests and
benchmarks, simulating your agent against them, and proposing harness changes
that are checked against earlier tests before you merge them.

## Requirements

The plugin contains only skills and reference text, and runs no code of its
own. Every action goes through the RELAI CLI, which you install and sign in to
separately. The CLI runs on macOS 15+ on Apple silicon and on Linux (x86_64
and ARM64):

```sh
curl -fsSL https://api.relai.ai/install.sh | bash
relai auth login
```

RELAI also needs curl, Bash, Git, `uv`, and a running Docker daemon with
Compose. See the [installation guide](https://cli-docs.relai.ai/installation).

## What the plugin runs and sends

- Your coding agent runs `relai` commands in your project, under its own
  permission settings. Once per session, before following a skill, it runs
  `relai guide --revision` to check that the skill matches your installed CLI.
- RELAI runs your agent in local Docker containers, which builds and pulls
  container images. Agent tests, benchmarks, and EvalsWiki pages are files in
  your repository; simulation results stay in local files.
- `relai optimize` commits the changes it proposes, and commits any
  uncommitted code changes separately first. It pushes a branch and opens a
  pull request with `gh` only when you ask for one.
- RELAI's own model calls, such as its workflow agent, LLM judges, and
  simulated users, use your RELAI sign-in and send the project content each
  step needs to RELAI's service.
- The CLI sends product analytics, such as command, status, duration,
  version, and OS, tied to your RELAI account and organization. It also sends
  diagnostic traces unless you set `auto_report = false` under `[telemetry]`
  in `~/.relai/config.toml`. Neither includes credentials, prompts, model or
  tool content, or project file contents.

## Documentation

[cli-docs.relai.ai](https://cli-docs.relai.ai)

## License

Copyright 2026 RELAI Inc.

This plugin is licensed under the Apache License, Version 2.0; see `LICENSE`.
The license covers this plugin's files, not the RELAI CLI or RELAI's service,
and grants no rights to the RELAI name or trademarks.
