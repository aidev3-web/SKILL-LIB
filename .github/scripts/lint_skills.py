#!/usr/bin/env python3
"""Validate SKILL.md frontmatter against the rules in PACKAGING.md.

Rules checked (see PACKAGING.md sections 3 and 8):
- frontmatter parses as YAML and contains only `name` + `description`
- `name` is lowercase letters/digits/hyphens, <=64 chars
- `name` matches the skill's folder name
- `description` is non-empty
"""
import re
import subprocess
import sys

import yaml

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def changed_skill_files(base_sha, head_sha):
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACM", f"{base_sha}...{head_sha}"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return [p for p in out if p == "SKILL.md" or p.endswith("/SKILL.md")]


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, "SKILL.md must start with a YAML frontmatter block (---)"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "SKILL.md frontmatter block is not closed with a second ---"
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        return None, f"frontmatter is not valid YAML: {e}"
    if not isinstance(data, dict):
        return None, "frontmatter must be a YAML mapping"
    return data, None


def lint_file(path):
    errors = []
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    fm, err = parse_frontmatter(text)
    if err:
        errors.append(err)
        return errors

    folder_name = path.rsplit("/", 2)[-2] if "/" in path else None

    extra_keys = sorted(k for k in fm.keys() if k not in ("name", "description"))
    if extra_keys:
        errors.append(
            f"frontmatter has extra key(s) not allowed by PACKAGING.md: {', '.join(extra_keys)} "
            "(move agent-specific config to an agents/ folder instead)"
        )

    name = fm.get("name")
    if not name:
        errors.append("frontmatter is missing required key `name`")
    else:
        if len(name) > 64:
            errors.append(f"`name` is {len(name)} chars, must be <= 64")
        if not NAME_RE.match(name):
            errors.append(f"`name` \"{name}\" must be lowercase letters/digits/hyphens only")
        if folder_name and name != folder_name:
            errors.append(f"`name` \"{name}\" does not match folder name \"{folder_name}\"")

    description = fm.get("description")
    if not description or not str(description).strip():
        errors.append("frontmatter is missing required key `description`")

    return errors


def main():
    if len(sys.argv) == 3:
        files = changed_skill_files(sys.argv[1], sys.argv[2])
    else:
        out = subprocess.run(
            ["git", "ls-files", "*SKILL.md"], capture_output=True, text=True, check=True
        ).stdout.splitlines()
        files = out

    if not files:
        print("No SKILL.md files to lint.")
        return 0

    had_errors = False
    for path in files:
        errors = lint_file(path)
        if errors:
            had_errors = True
            for e in errors:
                print(f"::error file={path}::{e}")
        else:
            print(f"OK: {path}")

    return 1 if had_errors else 0


if __name__ == "__main__":
    sys.exit(main())
