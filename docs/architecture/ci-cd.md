---
title: CI/CD and Automation
category: architecture
---

# CI/CD and Automation

Overdue uses GitHub Actions for continuous integration and automated documentation maintenance. This page describes the workflows, their triggers, and how to configure them.

## Workflows

### Auto-Update Documentation (`doc-update.yml`)

Automatically detects when merged PRs introduce documentation drift and proposes updates via follow-up PRs.

**Trigger:** Runs when a PR is merged to `main`.

**How it works:**

1. Checks out the repository with full history (`fetch-depth: 0`)
2. Computes the list of files changed between the PR's base and merge commits
3. Passes the changed files and PR metadata to [Claude Code Action](https://github.com/anthropics/claude-code-action)
4. Claude reads the changed files and all documentation in `docs/`
5. If documentation updates are needed, Claude creates a new branch (`docs/update-from-pr-{number}`), commits changes, and opens a follow-up PR
6. If no updates are needed, Claude explains why and the workflow exits cleanly

**Tool permissions:** The Claude Code Action step runs with a restricted set of allowed tools:

| Category | Tools |
|---|---|
| File operations | `Read`, `Edit`, `Write`, `Glob`, `Grep` |
| Shell commands | `Bash` (unrestricted) |

Bash is allowed without restriction because the workflow runs on an ephemeral GitHub Actions runner with no access to production systems. All changes go through PR review before merging. The security boundary is the GitHub Actions permissions (`contents: write`, `pull-requests: write`), not Bash tool restrictions.

Restricting Bash to individual command patterns (e.g., `Bash(git diff *)`) is fragile — Claude naturally uses arbitrary shell commands (`find`, `cat`, compound commands, env-prefixed commands) that won't match specific patterns. Each denied command wastes a turn, and with `--max-turns 15`, a few denials can cause the workflow to fail without completing its task.

**Safety guards:**

| Guard | Purpose |
|---|---|
| `skip-docs-check` label | Opt out of doc checks on a per-PR basis |
| Bot author exclusion | Prevents infinite loops from `github-actions[bot]` and `claude[bot]` |
| Author association check | Only runs for `OWNER`, `MEMBER`, or `COLLABORATOR` PRs |
| Concurrency group | Cancels in-progress runs for the same PR |
| 30-minute timeout | Prevents runaway workflow costs |
| `--max-turns 15` | Caps Claude's iteration depth |

**Required repository configuration:**

| Setting | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` secret | Authenticates with the Anthropic API |
| Claude GitHub App | Provides the GitHub integration for Claude Code Action |
| `id-token: write` permission | Required for OIDC authentication with Anthropic's API |
| `contents: write` permission | Allows creating branches and committing changes |
| `pull-requests: write` permission | Allows opening follow-up PRs |

## Documentation structure

The doc-update workflow scans all files under `docs/` and any `README.md` in the repository root. Documentation that references code behavior, configuration values, or game mechanics is most likely to need updates when those areas change.

| Directory | Content | Common update triggers |
|---|---|---|
| `docs/guides/` | User-facing guides (gameplay, installation, configuration, bots) | Game balance changes, new features, config changes |
| `docs/api/` | API reference (endpoints, auth, errors, rate limiting) | Endpoint changes, new routes, auth changes |
| `docs/architecture/` | System design (overview, CI/CD) | Infrastructure changes, new workflows, architectural decisions |
| `docs/changelog/` | Release history | Any user-facing change |

## Troubleshooting

### Workflow fails with `error_max_turns` and `permission_denials_count > 0`

Claude tried to use a tool that isn't in the `allowedTools` list. The CI logs only show the denial count, not which commands were denied, making individual patterns hard to debug. The fix is to allow `Bash` without restriction (see tool permissions above). If you need to restrict Bash, use broad patterns like `Bash(git *)` rather than individual subcommands, and note that the `:*` suffix syntax is deprecated in favor of ` *` (space-star).

### Workflow fails with a 502 or OIDC error

Transient GitHub API or authentication failure. Re-run the failed job from the Actions tab.

### Workflow creates unnecessary doc update PRs

Add the `skip-docs-check` label to PRs that don't need documentation review (e.g., dependency bumps, CI-only changes).
