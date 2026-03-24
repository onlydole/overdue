---
name: doc-it
description: >
  Generate, update, and audit project documentation from source code. Scans the
  repo for missing docs, stale references, and gaps in existing files. Produces
  new pages, patches existing ones, and recommends docs the project should have.
allowed-tools: [Read, Grep, Glob, Bash, Write]
argument-hint: "<path> to target a file or directory, or 'all' for a full audit"
user-invocable: true
---

# Generate and Maintain Project Documentation

## When to Use

Run this skill when:
- A new contributor asks "where are the docs?"
- Endpoints, CLI commands, or config options have changed since the last doc update
- You want to find out what documentation is missing, stale, or incomplete
- You're preparing a release and need the CHANGELOG or README refreshed

Invoke with `/doc-it all` for a full repo audit, or target a specific
area: `/doc-it src/api/volumes.py`, `/doc-it README.md`,
`/doc-it docs/guides/`.

## Workflow

### Step 1: Discover what exists

Scan the repo root and common locations for documentation files.

- Root files: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `TOOLS.md`,
  `CLAUDE.md`, `AGENTS.md`, `CLAUDE.local.md`, `LICENSE`
- Doc directories: `docs/`, `documentation/`, `doc/`, `wiki/`
- Inline docs: docstrings, JSDoc, rustdoc, godoc annotations in source files
- Config manifests: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`,
  `Makefile`, `Dockerfile`, `docker-compose.yml`

**Resolve symlinks before doing anything else.** Many repos symlink AI
instruction files to a single canonical source. Common patterns:

- `CLAUDE.md` -> `AGENTS.md` (or the reverse)
- `.cursorrules` -> `AGENTS.md`
- `CODEX.md` -> `AGENTS.md`

Run `ls -la` on every root-level markdown file to detect symlinks. When a
symlink is found, record which file is the real file (the symlink target)
and which are aliases. For the rest of the workflow:

- Only read and edit the **canonical (real) file**, never the symlink
- If the user targets a symlink by name (e.g., `/doc-it CLAUDE.md`
  and CLAUDE.md is a symlink to AGENTS.md), resolve it and edit AGENTS.md
- Report the symlink relationship in the summary so the user knows which
  file was edited and why

If both `CLAUDE.md` and `AGENTS.md` exist as separate (non-symlinked) files,
treat them as independent files but flag content divergence between them in
the audit step.

Build an inventory: file path (noting symlinks), last modified date,
approximate line count, and a one-line summary of what each file covers.

### Step 2: Audit existing documentation

For every documentation file found in Step 1 (using canonical paths only,
never symlink aliases):

1. **Check for stale references.** Flag any mention of files, directories,
   commands, environment variables, or config keys that no longer exist in
   the codebase.
2. **Check for missing coverage.** Compare what the doc describes against
   what the code contains. If the code has endpoints, CLI commands, config
   options, models, or public APIs that the doc doesn't mention, list them.
3. **Check internal consistency.** If the project has both CLAUDE.md and
   AGENTS.md as separate files, flag divergence between them. If README.md
   describes a setup process that conflicts with CONTRIBUTING.md, flag that
   too.

Report findings as a list: file, issue type (stale, missing, inconsistent),
specific detail, and suggested fix.

### Step 3: Update existing docs

If $ARGUMENTS targets a specific file (e.g., `README.md`, `CHANGELOG.md`,
`docs/api/volumes.md`), update that file directly:

- Preserve the existing structure, voice, and formatting
- Add missing sections where the code has outgrown the docs
- Remove or flag references to deleted code
- Update examples, commands, and config values to match current state
- Leave a brief inline comment (`<!-- updated by /doc-it -->`)
  at each changed section so reviewers can find the edits

If $ARGUMENTS is 'all', apply updates to every file that has audit findings
from Step 2.

### Step 4: Generate missing documentation

Based on the audit, generate new files the project should have but doesn't.
Detect which files to create from the repo contents:

**README.md** (if missing or stub): Project name, one-paragraph description,
install/setup commands (from manifest files), usage example, link to docs
directory if it exists.

**CONTRIBUTING.md** (if missing): Dev environment setup, branch and PR
conventions (inferred from git history and any PR templates), test commands,
commit message format, code review expectations.

**CHANGELOG.md** (if missing): Scaffold from git tags and release history.
Group entries by version with dates.

**TOOLS.md** (if missing): Language version, package manager, dev server
command, build command, lint/format commands, any MCP or tooling config.

**CLAUDE.md or AGENTS.md** (if missing): Project overview, directory layout,
key conventions, build/test/lint commands, and existing docs to reference
for style.

**API documentation** (if the project has route handlers or RPC definitions):
Scan for HTTP handlers, gRPC services, GraphQL resolvers, or CLI command
definitions. For each public interface, generate a doc page with:
- Name and signature
- "When to Use" section explaining the use case, not restating the signature
- Request/input details with types
- Response/output examples (success and common errors)
- Runnable code example
- Caveats: auth requirements, rate limits, side effects

Write API docs to the project's existing docs directory structure. If none
exists, create `docs/api/`.

### Step 5: Recommend additional docs

After generating and updating, look for gaps that aren't covered by the
standard files above. Recommend (but don't generate without confirmation)
docs the project would benefit from:

- Architecture overview (if the project has multiple services or layers)
- Deployment guide (if Dockerfile, CI config, or infra files exist)
- Troubleshooting page (if error handling code is substantial)
- Migration guide (if the schema or API has versioned breaking changes)
- Security policy (if auth, encryption, or secrets management code exists)

Present recommendations as a bulleted list with one sentence explaining
why each one would help.

### Step 6: Summary report

Print a structured summary:

- **Updated:** files that were modified, with a one-line description of
  each change
- **Created:** new files that were generated
- **Recommended:** additional docs the project should consider
- **Gaps:** information the skill couldn't determine from source alone
  (e.g., deployment targets, team conventions not visible in code)

## Quality Rules

- Never invent request/response fields, config keys, CLI flags, or
  environment variables that don't exist in the source code
- Every code example must be syntactically valid and runnable
- Flag gaps rather than filling them with assumptions
- Match the voice, formatting, and heading style of existing docs in
  the project. If the project has no docs yet, use plain markdown with
  ATX headings
- Include only status codes, error messages, and return values that the
  code produces. Do not guess
- If unsure about a parameter's purpose, write
  "See source at [file:line]" rather than guessing
- When updating an existing file, make the smallest edit that fixes the
  gap. Do not rewrite sections that are already correct
- Preserve manual edits. If a section has been hand-written and is still
  accurate, leave it alone
