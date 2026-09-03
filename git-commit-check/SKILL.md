---
name: git-commit-check
description: "Check a drafted git commit message (and the staged diff behind it) against this project's conventional-commit rules — format `type(scope): subject`, the 8 allowed types, English-only subject, one type per commit, and never pushing to main/master without explicit confirmation — before the commit is made, and draft a compliant message when asked to. Use this whenever about to run `git commit` in this repo, when asked to review/validate a commit message, or when the user says \"kiểm tra commit\", \"commit đúng chuẩn chưa\", \"check quy tắc commit\", \"viết commit message giúp tui\"."
---

# Git commit rule check

## What this is for

This repo (and any other project that adopts the same convention) requires every
commit to follow a strict format so `git log` stays readable across contributors
and tools. This skill is the portable, agent-agnostic version of that rule — the
same rule usually only lives in a Claude-Code-specific `CLAUDE.md`, which other
agents (Codex, OpenCode, the Claude Agent SDK) never read. Load this skill instead
of re-deriving the convention from memory.

## The rules

Format, exactly:
```
type(scope): subject
```

| Type | Meaning | Example |
|---|---|---|
| `feat` | New feature | `feat(employee): Add annual leave management` |
| `fix` | Bug fix | `fix(payroll): Fix tax calculation error` |
| `docs` | Documentation | `docs(api): Update API docs` |
| `style` | Formatting only, no logic change | `style(models): Fix indentation` |
| `refactor` | Restructuring without behavior change | `refactor(auth): Extract authentication logic` |
| `test` | Adding/adjusting tests | `test(employee): Add unit tests` |
| `chore` | Everything else (deps, tooling, cleanup) | `chore(deps): Update dependencies` |
| `ci` | CI/CD config | `ci(github): Configure workflows` |

- `scope` = the module/folder most affected by the change (e.g. `employee`,
  `payroll`, `auth`, `api`, or the actual package/folder name in this repo).
- `subject` = short, direct, capitalized first letter, **no trailing period**.
- **`subject` must always be written in English** — never Vietnamese, and never
  unaccented Vietnamese as a fallback (e.g. `Them tinh nang` is not acceptable
  just because a tool can't type diacritics). This is what keeps `git log`
  readable for every contributor regardless of locale.

## Workflow

1. **Look at what actually changed** — `git status` / `git diff` / `git diff --staged`
   before writing anything. Don't guess the type/scope from the request alone;
   read the real diff.
2. **Classify the change(s).** If the diff spans more than one type (e.g. a
   feature plus an unrelated formatting cleanup, or a fix plus a doc update),
   **split into separate commits, one per type** — stage and commit each subset
   separately rather than writing one mixed-type commit. This is a hard rule,
   not a suggestion.
3. **Pick the scope** from the most-affected module/folder — if a change touches
   several folders, pick the one that best names *what* changed, not every
   folder it happened to touch.
4. **Draft the subject in English**, short and direct, present-tense imperative
   ("Add", "Fix", "Update" — not "Added"/"Fixes"), capitalized first letter, no
   trailing period.
5. **Validate the final message against the format before committing**:
   - Matches `type(scope): subject` exactly (lowercase type, scope in
     parentheses, colon-space before subject)
   - `type` is one of the 8 in the table above — reject anything else
     (`feature`, `bugfix`, `update`, etc. are not valid types)
   - `subject` is English-only
   - No trailing period on `subject`
   - If any check fails, **fix the message before committing** — don't commit
     first and explain the deviation after.
6. **Never push to `main`/`master` without explicit confirmation.** Default to
   creating a feature branch and opening a Pull Request. Only push directly to
   `main`/`master` if the user has explicitly asked for that in this exact
   request — a prior approval for a different push does not carry over.

## Judgment calls

If asked to just "commit this" without a message, draft one following the rules
above from the actual diff, and show it before running `git commit` rather than
committing silently. If the user's own suggested message breaks a rule (wrong
type, Vietnamese subject, mixes multiple change types), say exactly which rule
it breaks and propose the corrected version(s) — including splitting into
multiple commits when that's what the rule requires — rather than committing
it as given.
