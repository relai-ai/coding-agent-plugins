# RELAI plugin for Claude Code, Codex, Cursor, and GitHub Copilot

Continuously evaluate and optimize your AI agent: build Harbor-format evals from
your code, requirements, and traces, then get harness improvements as pull requests.

Ask your coding agent in plain language. RELAI turns the behavior you expect
into repeatable agent tests, runs your agent against them in isolated
containers, and proposes changes that are checked against every earlier test
before you merge them.

## Install

### Claude Code

```text
/plugin marketplace add relai-ai/coding-agent-plugins
/plugin install relai@relai-claude
```

### Codex

```sh
codex plugin marketplace add relai-ai/coding-agent-plugins
codex plugin add relai@relai-codex
```

Start a new Codex session to load the skills.

### Cursor and GitHub Copilot

Install through the RELAI CLI with `relai setup --agent cursor` or
`relai setup --agent copilot` (see below). Cursor Teams and Enterprise admins
can also import this repository as a team marketplace under
**Dashboard → Plugins & MCPs → Add Marketplace → Import from Repo**.

### The RELAI CLI

The plugin runs the RELAI CLI on macOS 15+ (Apple silicon) or Linux (x86_64
and ARM64). If you installed the plugin from a marketplace, install the CLI
and sign in:

```sh
curl -fsSL https://api.relai.ai/install.sh | bash
relai auth login
```

Do not also run `relai setup --agent` afterwards: it installs a second copy of
the plugin's skills.

To start from the CLI instead, let setup install the plugin that matches your
CLI version:

```sh
curl -fsSL https://api.relai.ai/install.sh | bash
relai setup --agent <claude|codex|cursor|copilot>
```

RELAI also needs Git, `uv`, and a running Docker daemon with Compose. See the
[installation guide](https://cli-docs.relai.ai/installation?utm_source=github&utm_medium=plugin_readme&utm_campaign=plugin_discovery).

## Try it

Open your agent's repository in your coding agent and ask:

> Use RELAI to check whether this agent project is ready. Keep the check
> read-only and explain any blockers.

Then initialize it:

> Use RELAI to initialize this agent project. Keep provider keys out of chat
> and Git.

## What you get

- **Evals in your repository.** Agent tests and benchmarks use the open-source
  Harbor format and are versioned next to your code.
- **EvalsWiki.** Your agent's requirements, risks, coverage, and open questions
  live as Markdown files in `.relai/evals-wiki/`.
- **Simulation.** RELAI runs your agent against each scenario in an isolated
  Harbor environment and scores the result with code evaluators and LLM judges.
- **Harness optimization.** RELAI changes prompts, context, tools, workflows,
  memory, and agent logic for your quality and cost objective, then opens a
  pull request or leaves the change on a local branch.
- **Your existing tracing.** Ingest traces exported from Arize, Braintrust,
  LangSmith, Langfuse, Helicone, or your own logs to keep evals current.

## Results

- **Terminal-Bench 2.0:** pass rate rose from 62.5% to 79.2% after the first
  optimization round.
  [Read the article](https://relai.ai/blog/continual-learning-evaluation-on-terminal-bench-2-0?utm_source=github&utm_medium=plugin_readme&utm_campaign=plugin_discovery)
- **AutomationBench:** 3 to 10 pass-rate points gained and 22–44% lower cost per
  successful task across three frontier models.
  [Read the article](https://relai.ai/blog/improving-the-cost-quality-frontier-for-ai-agents?utm_source=github&utm_medium=plugin_readme&utm_campaign=plugin_discovery)

## FAQ

**Do I need traces or an existing eval suite to start?**
No. RELAI starts from your code, requirements, and existing tests. Traces add
evidence as they arrive.

**Does RELAI replace my observability platform?**
No. Keep Arize, Braintrust, LangSmith, Langfuse, or your own stack for
monitoring. RELAI uses their traces to keep evals current.

**How does RELAI avoid regressions?**
Earlier evals stay in the loop. Every candidate change is checked against all
accumulated coverage, so a new fix can't quietly break what already worked.

**Where do evals and changes live?**
In your repository: EvalsWiki, agent tests, and harness changes. RELAI hosts
run history, metrics, and evidence.

**Which agents does it work with?**
RELAI is framework-agnostic. It works best with a Git-tracked Python,
TypeScript, JavaScript, or Go project that has a runnable local entry point.
See [compatibility](https://cli-docs.relai.ai/compatibility?utm_source=github&utm_medium=plugin_readme&utm_campaign=plugin_discovery).

## Learn more

- [Documentation](https://cli-docs.relai.ai?utm_source=github&utm_medium=plugin_readme&utm_campaign=plugin_discovery)
- [relai.ai](https://relai.ai/?utm_source=github&utm_medium=plugin_readme&utm_campaign=plugin_discovery)
- [Start free](https://platform.relai.ai/auth/register?source=plugin_readme&utm_source=github&utm_medium=plugin_readme&utm_campaign=plugin_discovery)

## Repository layout

| Host | Package | Catalog |
| --- | --- | --- |
| Claude Code | `plugins/claude/relai/` | `.claude-plugin/marketplace.json` |
| Codex | `plugins/codex/relai/` | `.agents/plugins/marketplace.json` |
| Cursor | `plugins/cursor/relai/` | `.cursor-plugin/marketplace.json` |
| GitHub Copilot | `copilot/skills/` | Published with `gh skill publish` |

The OpenAI submission archive is `artifacts/relai-openai-vX.Y.Z.zip`. These
files are generated by the RELAI CLI release; see
[CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes.
