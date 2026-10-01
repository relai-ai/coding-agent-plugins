# RELAI coding-agent plugins

This repository is the generated public distribution surface for RELAI coding-agent
plugins and skills. The source files are maintained in the private `relai-cli`
repository and copied here by its release pipeline.

Do not edit generated packages directly. Release pull requests contain an exact
source commit, content inventory, and digest in `provenance.json`; changes merge
only after the repository validation workflow passes.

## Published packages

- Codex plugin: `plugins/codex/relai/`
- Claude Code plugin and marketplace: `plugins/claude/relai/` and
  `.claude-plugin/marketplace.json`
- Cursor plugin and marketplace: `plugins/cursor/relai/` and
  `.cursor-plugin/marketplace.json`
- GitHub Copilot skills: `copilot/skills/`
- OpenAI submission archive: `artifacts/relai-openai-vX.Y.Z.zip`

Every merged release is tagged as `vX.Y.Z`. The post-merge workflow publishes
the Copilot skills and attaches the OpenAI archive to the corresponding GitHub
Release.
