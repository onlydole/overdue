---
title: CI/CD and Automation
category: architecture
freshness:
  ttl_days: 365
  sources:
    - ".github/workflows/*.yml"
    - ".github/scripts/*.py"
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

Bash is allowed without restriction. This is a deliberate trade-off between tool-level command restrictions and workflow reliability:

- **Why not individual patterns:** Restricting Bash to individual command patterns (e.g., `Bash(git diff *)`) is fragile — Claude naturally uses arbitrary shell commands (`find`, `cat`, compound commands, env-prefixed commands) that don't match specific patterns. Each denied command wastes a turn, and with `--max-turns 15`, a few denials can cause the workflow to fail without completing its task. This failure mode occurred repeatedly in PRs #29, #33, and #38.
- **Residual risk:** Unrestricted Bash means Claude can execute any shell command on the runner, including network calls or reading environment variables. If PR metadata were crafted to manipulate Claude's behavior, this could be exploited.
- **Mitigations:** The workflow only runs for `OWNER`, `MEMBER`, or `COLLABORATOR` PRs (not external contributors). PR metadata is wrapped in XML tags with explicit instructions to treat it as untrusted data. The runner is ephemeral (disposable VM) with no access to production systems. All changes go through PR review before merging. The `ANTHROPIC_API_KEY` secret is the only sensitive value on the runner and is not exposed to tool output.

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

### Documentation Freshness (`freshness.yml`)

Scores every doc page on a 0--100 scale on every PR and gates the merge against an SLO.

**Trigger:** Runs on PRs touching `docs/`, `src/`, the freshness script, the allowlist, or this workflow file. Also runs on `push` to `main` to refresh the baseline artifact.

**How it works:**

1. Checks out the PR ref with full history (`fetch-depth: 0`)
2. Runs `.github/scripts/freshness.py` to score each page from three deterministic signals (git age delta, frontmatter TTL, symbol drift)
3. Adds a `git worktree` for the PR base ref and scores the baseline so the comment formatter can show per-page deltas
4. Pages in the 35--64 gray zone are routed to a conditional [Claude Code Action](https://github.com/anthropics/claude-code-action) step that classifies each as `STILL_ACCURATE`, `DRIFTED`, or `NEEDS_HUMAN_REVIEW`
5. `marocchino/sticky-pull-request-comment@v2` posts (or updates) a single PR comment with the median delta and per-page drops
6. The SLO gate fails the job when the median drops below 75 or any `critical: true` page drops below 60

**Tool permissions for the semantic check:** `Read`, `Glob`, `Grep` only -- the step reads source files and docs and does not write anything.

**Required repository configuration:**

| Setting | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` secret | Authenticates the gray-zone semantic check |
| `contents: read` permission | Reads the repo |
| `pull-requests: write` permission | Posts the sticky PR comment |

**Required status check setup:**

To make merges actually wait on the freshness gate, mark this workflow as a required status check on the protected branch.

1. Settings -> Branches -> Add rule (or edit the existing rule for `main`)
2. Enable **Require status checks to pass before merging**
3. Search for and select **freshness** (the job ID from this workflow)
4. Save

Authors will still see the comment with the median delta on every PR even without protection rules, but only the required-status-check setup blocks merges on a failing SLO.

**Local check:**

Run the pipeline against the working tree before pushing:

```bash
uv run python .github/scripts/freshness.py
jq '[.[] | .score] | (add / length)' freshness.json    # mean
jq '[.[] | select(.score < 75)]' freshness.json         # below-floor pages
```

The generated `freshness.json` is gitignored.

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
