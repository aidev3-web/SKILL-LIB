---
name: git-branch-name
description: Draft a git branch name from a description of the work, following this project's `type/scope-subject` convention — lowercase, hyphen-separated, English only, no diacritics. Use whenever about to create a branch (`git checkout -b`, `git switch -c`), when asked to name a branch, or when the user says "đặt tên nhánh", "tạo nhánh cho", "branch name cho việc này", "name this branch".
---

# Naming a git branch

Turn a description of the work into one branch name. The description usually
arrives in Vietnamese; the branch name is always in English.

## The format

```
type/scope-subject
```

The `type` values are the same eight this project uses for commits, so a
branch and the commits on it agree with each other:

| Type       | Use it for                     | Example branch                    |
|------------|--------------------------------|-----------------------------------|
| `feat`     | New feature                    | `feat/auth-add-oauth-login`       |
| `fix`      | Bug fix                        | `fix/payroll-month-13-calculation`|
| `docs`     | Documentation                  | `docs/readme-update-setup-steps`  |
| `style`    | Formatting only                | `style/models-fix-indentation`    |
| `refactor` | Restructuring, behavior unchanged | `refactor/auth-extract-logic`  |
| `test`     | Adding or fixing tests         | `test/employee-add-unit-tests`    |
| `chore`    | Everything else                | `chore/deps-bump-express`         |
| `ci`       | CI/CD pipelines                | `ci/github-add-release-workflow`  |

## Rules

1. **Lowercase throughout.** `feat/auth-add-login`, never `Feat/Auth-Add-Login`.
2. **Hyphens between words**, not underscores, spaces, or camelCase.
3. **English only** — and never unaccented Vietnamese as a substitute. If the
   description is "thêm đăng nhập bằng Google", the branch is
   `feat/auth-add-google-login`, not `feat/auth-them-dang-nhap`.
4. **Subject is 2–5 words.** Long enough to identify the work in a branch
   list, short enough to type. Drop filler words (`the`, `a`, `some`).
5. **One slash only** — the one after `type`. Hyphens carry the rest.
6. **No issue numbers unless the user gives one.** If they do, it goes at the
   end: `fix/payroll-tax-rounding-142`.

## Picking the scope

Use the module or folder most affected, the same way a commit scope is
chosen — `auth`, `payroll`, `api`, `employee`. If the change genuinely spans
the whole project with no single owner (a dependency bump, a repo-wide
formatting pass), drop the scope and use `type/subject`:
`chore/bump-node-to-22`.

## Judgment calls

- **If the description covers more than one type of change**, say so and
  suggest splitting it into separate branches — the same rule the commit
  convention uses. Don't silently pick whichever type seems dominant.
- **If the work is too vague to name** ("sửa linh tinh", "fix stuff"), ask
  what specifically changes rather than inventing a plausible-sounding
  subject. A branch name nobody can decode is worse than a question.
- **Don't create the branch.** Propose the name and let the user run
  `git checkout -b` themselves, unless they explicitly ask you to create it.
