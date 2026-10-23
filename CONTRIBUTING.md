# Contributing

This repository is the generated public distribution surface for RELAI
coding-agent plugins and skills. Plugin packages in this repository are
generated. Make source or content changes in `relai-ai/relai-cli`; its release
pipeline opens the publication pull request here.

Do not edit generated packages directly. Release pull requests contain an exact
source commit, content inventory, and digest in `provenance.json`; changes merge
only after the repository validation workflow passes.

Every merged release is tagged as `vX.Y.Z`. The post-merge workflow publishes
the Copilot skills and attaches the OpenAI archive to the corresponding GitHub
Release.

Changes to repository-owned automation under `.github/`, `scripts/`, or root
documentation can be proposed directly in this repository. They must not modify
generated paths in the same pull request.
