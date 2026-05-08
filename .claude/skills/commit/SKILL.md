---
name: commit
description: Draft a Conventional Commits message from the currently staged diff. Reads the staged changes and recent commit log, then proposes a type(scope) subject and bullet body. Does not commit — only proposes the message for review.
disable-model-invocation: true
allowed-tools: Bash, Read
---

Read the staged diff and propose a commit message in Conventional Commits format.

## Inputs

- Stage status: !`git status --short`
- Staged diff (names only): !`git diff --cached --name-status`
- Staged diff (truncated): !`git diff --cached --stat`
- Full staged diff: !`git diff --cached`
- Recent log style: !`git log --oneline -10`

## Task

If `git diff --cached` is empty, stop and report that nothing is staged.

Otherwise, draft a single commit message in this format:

```
<type>(<scope>): <subject>

<optional body — bullet points, wrapped at 72 chars>

<optional footer — BREAKING CHANGE / Closes #N>
```

### Rules

- **type** — one of: `feat` (new behavior), `fix` (bug fix), `refactor` (no behavior change), `docs`, `test`, `chore`, `build`, `ci`, `perf`, `style`. Pick the dominant change; do not invent types.
- **scope** — the area touched, derived from paths (e.g., `agents`, `ci`, `skills`, `tests`, `docs`). Omit `()` if the change is repo-wide. Single scope only — if the diff spans many areas, drop the scope.
- **subject** — imperative mood ("add", not "added"/"adds"), no trailing period, ≤ 72 chars total including type/scope.
- **body** — only if the change is non-trivial. One bullet per logical change. Wrap at 72 chars. Explain *why*, not *what* the diff already shows.
- **breaking change** — if any public API, CLI flag, env var, or import path changes incompatibly, add a `BREAKING CHANGE:` footer explaining the migration.

### Output

Print exactly one fenced code block containing the proposed message. After the block, in 1–2 lines, note any judgment calls (chosen type, scope choice, anything ambiguous) so the user can override before committing. Do not run `git commit`.
