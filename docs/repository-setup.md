# Repository setup

Before enabling the first automated release:

1. Enable GitHub Actions and native pull-request auto-merge.
2. Add a `main` ruleset that requires pull requests, blocks force pushes and
   deletions, and requires the `plugin-overlay` job from `Validate plugin release`.
3. Add a tag ruleset protecting `v*` tags from updates and deletion.
4. Install the RELAI release GitHub App on this repository with repository
   contents and pull-request read/write access.
5. Enable secret scanning, push protection, and code scanning where available.
6. Keep the repository internal during pipeline testing. Change visibility to
   public only before testing unauthenticated installs or submitting marketplace
   and directory listings.

The source release job requests a token scoped only to this repository and only
the `contents:write` and `pull_requests:write` permissions. It requests native
auto-merge after opening a generated release PR; GitHub merges only after the
ruleset requirements pass.
