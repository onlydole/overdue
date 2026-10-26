---
title: CI/CD and Automation
category: architecture
freshness:
  ttl_days: 365
  sources:
    - ".github/workflows/*.yml"
    - ".github/scripts/*.py"
    - ".github/dependabot.yml"
    - ".github/freshness-allowlist.txt"
---

# CI/CD and Automation

Overdue uses GitHub Actions for continuous integration, automated documentation maintenance, and on-demand agent runs. This page describes the workflows, their triggers, and how to configure them.

## Workflows

### Tests, Lint and Types (`checks.yml`)

Runs Python tests, lint, types, and frontend asset checks as independent jobs. Every install uses the committed lockfiles.

**Trigger:** Every pull request, every push to `main`, and `workflow_dispatch`.

**Jobs:**

| Job ID | Command |
|---|---|
| `test` | `uv run --locked pytest` |
| `lint` | `uv run --locked ruff check src/ tests/ scripts/` then `uv run --locked ruff format --check src/ tests/ scripts/` |
| `types` | `uv run --locked mypy src/` |
| `runtime` | `uv run --locked pytest` on Python 3.14 |
| `frontend` | `npm ci --ignore-scripts`, `npm audit --audit-level=low`, JavaScript syntax checks, and reproducible asset builds |

The jobs run concurrently, so a type error does not hide a test failure.

**Why there is no `paths:` filter:** these are intended to be required status checks, and GitHub never reports a required check that was skipped by a path filter, leaving the PR blocked on a run that will never arrive. Running on every PR costs a couple of cached minutes and always reports.

**Python versions:** the `test` job covers Python 3.12, the minimum supported version. The `runtime` job covers Python 3.14, matching Docker. Both install development dependencies with `uv sync --locked --extra dev`. The test job also regenerates icons and checks that they match the committed SVGs.

The frontend job uses Node.js 24. It rebuilds CSS and the vendored HTMX and Alpine.js files, then rejects changes to the committed assets. Browser libraries are development dependencies because the app serves their generated files without a Node.js runtime. Tailwind scans the configured template and JavaScript paths, with automatic repository scanning disabled.

Both asset checks inspect Git status, including untracked files, after regeneration. They reject generated files missing from the branch as well as modified or deleted assets.

The npm audit gate deliberately fails on low, moderate, high, and critical advisories, including development and transitive dependencies. These tools execute during builds, so development dependencies remain in scope. This policy can block an unrelated PR when a new advisory appears; fix the dependency or review a policy change rather than silently raising the threshold. The explicit `--audit-level=low` flag records that choice.

Docker uses Python 3.14.9 and installs runtime dependencies from `uv.lock` with `uv sync --locked --no-dev`. Compose Watch rebuilds the image when the lockfile changes. The project stays editable so source syncing still works.

**Required repository configuration:** none. The jobs use no secrets and opt into `contents: read` only, so they run on fork PRs.

**Required status check setup:**

1. Settings -> Branches -> Add rule (or edit the existing rule for `main`)
2. Enable **Require status checks to pass before merging**
3. Search for and select **test**, **lint**, **types**, **runtime**, and **frontend**
4. Save

**Local equivalent:**

```bash
make check
npm ci --ignore-scripts
npm audit --audit-level=low
npm run js:build
npm run css:build
uv run --locked python scripts/build_icons.py
```

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

- **Why not individual patterns:** Restricting Bash to individual command patterns (e.g., `Bash(git diff *)`) is fragile — Claude naturally uses arbitrary shell commands (`find`, `cat`, compound commands, env-prefixed commands) that don't match specific patterns. Each denied command wastes a turn, and with a turn cap in place, a few denials can cause the workflow to fail without completing its task. This failure mode occurred repeatedly in PRs #29, #33, and #38.
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
| `--max-turns 100` | Caps Claude's iteration depth (25 proved too low: a 61-file merge in PR #130 needed 26 turns and failed; the 30-minute timeout remains the cost backstop) |

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
6. The SLO gate fails the job when the median drops below 75 or any `critical: true` page scores 60 or below

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

### Pullfrog Agent (`pullfrog.yml`)

Runs a [Pullfrog](https://github.com/pullfrog/pullfrog) coding agent against the repository on demand, so a maintainer can hand the agent a task from the Actions tab without opening a PR first.

**Trigger:** `workflow_dispatch` only. There is no automatic trigger -- the workflow never runs on a push, a PR, or a schedule.

**Inputs:**

| Input | Required | Purpose |
|---|---|---|
| `prompt` | yes | The task handed to the agent |
| `name` | no | Sets the run title via `run-name`; falls back to the workflow name |

**Model:** the agent is served over an OpenAI-compatible BYOK endpoint (`model: openai-compatible/byok`) pointed at Ollama Cloud (`https://ollama.com/v1`) running `glm-5.2`. Because the model is not Anthropic-hosted, this workflow needs no `ANTHROPIC_API_KEY` -- unlike `doc-update.yml` and `freshness.yml`. Pullfrog requires both `OPENAI_COMPATIBLE_CONTEXT` and `OPENAI_COMPATIBLE_MAX_OUTPUT` to be set explicitly; the values in the workflow are GLM 5.2's published limits.

**Safety guards:**

| Guard | Purpose |
|---|---|
| `workflow_dispatch` only | No untrusted input path -- a maintainer with write access has to start every run |
| `push: restricted` | Keeps the agent off `main`; it cannot push directly to the protected branch |
| 90-minute timeout | Prevents runaway workflow costs |
| SHA-pinned actions | Both `actions/checkout` and `pullfrog/pullfrog` are pinned to a commit SHA with the tag in a trailing comment, matching the convention in the other workflows |

**Required repository configuration:**

| Setting | Purpose |
|---|---|
| `OLLAMA_API_KEY` secret | Authenticates against the Ollama Cloud OpenAI-compatible endpoint |
| `id-token: write` permission | OIDC authentication for the Pullfrog action |
| `contents: read` permission | Reads the repo |

To point the workflow at a different provider or model, change the `OPENAI_COMPATIBLE_BASE_URL`, `OPENAI_COMPATIBLE_MODEL`, and the two limit values in the `Run agent` step's `env` block, and store the matching key in the secret referenced by `OPENAI_COMPATIBLE_API_KEY`.

## Documentation structure

The doc-update workflow scans all files under `docs/` and any `README.md` in the repository root. Documentation that references code behavior, configuration values, or game mechanics is most likely to need updates when those areas change.

| Directory | Content | Common update triggers |
|---|---|---|
| `docs/guides/` | User-facing guides (gameplay, installation, configuration, bots) | Game balance changes, new features, config changes |
| `docs/api/` | API reference (endpoints, auth, errors, rate limiting) | Endpoint changes, new routes, auth changes |
| `docs/architecture/` | System design (overview, database, pixel art, CI/CD) | Infrastructure changes, new workflows, architectural decisions |
| `docs/changelog/` | Release history | Any user-facing change |

## Troubleshooting

### Workflow fails with `error_max_turns` and `permission_denials_count > 0`

Claude tried to use a tool that isn't in the `allowedTools` list. The CI logs only show the denial count, not which commands were denied, making individual patterns hard to debug. The fix is to allow `Bash` without restriction (see tool permissions above). If you need to restrict Bash, use broad patterns like `Bash(git *)` rather than individual subcommands, and note that the `:*` suffix syntax is deprecated in favor of ` *` (space-star).

### Workflow fails with `error_max_turns` and `permission_denials_count: 0`

The doc check legitimately ran out of turns — this happens on very large merges, where reading every changed file plus the full `docs/` tree exceeds the cap (a 61-file merge failed this way at the old cap of 25). The cap is now 100; if a merge still exhausts it, raise `--max-turns` in `doc-update.yml` — the 30-minute job timeout is the real cost backstop — or split unusually large PRs.

### Workflow fails with a 502 or OIDC error

Transient GitHub API or authentication failure. Re-run the failed job from the Actions tab.

### Workflow creates unnecessary doc update PRs

Add the `skip-docs-check` label to PRs that don't need documentation review (e.g., dependency bumps, CI-only changes).
