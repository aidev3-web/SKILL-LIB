#!/usr/bin/env python3
"""
Stitch a Phase 1 group's raw <section> fragments into a real, previewable copy of
proposal-template.html — mechanically, without needing to hold the whole ~250KB
template in an agent's own context.

Why this exists: each Phase 1 group agent (A/B/C/D) reads assets/section-shell.md
(~5KB) instead of the full template, and returns raw <section id="..."> fragments,
not a full-page copy. checkpoint-manager's own rule still requires every intermediate
file to be a real, openable-in-a-browser HTML page (never a bare fragment on its
own) — this script is that mechanical bridge: it takes the template, replaces each
matching section's placeholder body with the agent's real fragment, and writes the
result as a full previewable page. This is a find-and-replace, not a task requiring
an agent's reasoning — running it as a script instead of an Agent call is the whole
point (it was the one piece of the "read section-shell.md instead of the full
template" plan that still needed the full template's bytes somewhere).

Usage:
    python stitch_group.py <template.html> <fragments.html> <out.html>

<fragments.html> is the group agent's raw output: one or more concatenated
`<section id="...">...</section>` blocks, in any order, for any subset of the
template's sections (only the sections that group actually owns).

Exit codes:
    0 = stitched successfully (every fragment's id was found and replaced)
    1 = at least one fragment's section id doesn't exist in the template (typo, or a
        section this group doesn't actually own — this is a real bug to fix, not a
        warning to ignore)
    2 = usage error
"""
import re
import sys
from pathlib import Path


def extract_fragments(fragments_html):
    """Return {section_id: full_fragment_html} for every top-level <section id="...">
    block in the given HTML. A naive regex can't correctly find a section's matching
    closing tag if sections nest (they don't, in this template) or contain nested
    <section>-like text in a citation excerpt — this uses a depth counter instead of
    a lazy regex match, so it can't be fooled by that."""
    fragments = {}
    pos = 0
    open_re = re.compile(r'<section\s+id="([a-z0-9-]+)"[^>]*>')
    while True:
        m = open_re.search(fragments_html, pos)
        if not m:
            break
        section_id = m.group(1)
        start = m.start()
        depth = 1
        cursor = m.end()
        tag_re = re.compile(r'<section\b|</section>')
        while depth > 0:
            m2 = tag_re.search(fragments_html, cursor)
            if not m2:
                raise ValueError(f"section '{section_id}' has no matching </section>")
            if m2.group(0) == "</section>":
                depth -= 1
            else:
                depth += 1
            cursor = m2.end()
        fragments[section_id] = fragments_html[start:cursor]
        pos = cursor
    return fragments


def replace_section(template_html, section_id, new_fragment):
    """Replace the template's existing <section id="section_id">...</section> block
    (whatever it currently contains — a placeholder-note, or another group's earlier
    stitch) with new_fragment. Returns (new_html, found: bool)."""
    open_re = re.compile(r'<section\s+id="' + re.escape(section_id) + r'"[^>]*>')
    m = open_re.search(template_html)
    if not m:
        return template_html, False
    start = m.start()
    depth = 1
    cursor = m.end()
    tag_re = re.compile(r'<section\b|</section>')
    while depth > 0:
        m2 = tag_re.search(template_html, cursor)
        if not m2:
            raise ValueError(f"template's '{section_id}' section has no matching </section>")
        if m2.group(0) == "</section>":
            depth -= 1
        else:
            depth += 1
        cursor = m2.end()
    return template_html[:start] + new_fragment + template_html[cursor:], True


def main(argv):
    if len(argv) != 3:
        print("Usage: stitch_group.py <template.html> <fragments.html> <out.html>", file=sys.stderr)
        return 2

    template_path, fragments_path, out_path = argv
    template_html = Path(template_path).read_text(encoding="utf-8")
    fragments_html = Path(fragments_path).read_text(encoding="utf-8")

    try:
        fragments = extract_fragments(fragments_html)
    except ValueError as exc:
        print(f"cannot parse fragments: {exc}", file=sys.stderr)
        return 1

    if not fragments:
        print(f"no <section id=\"...\"> fragments found in {fragments_path}", file=sys.stderr)
        return 1

    missing = []
    for section_id, fragment in fragments.items():
        template_html, found = replace_section(template_html, section_id, fragment)
        if not found:
            missing.append(section_id)
        else:
            print(f"  stitched  {section_id}")

    if missing:
        print(f"FAIL: {len(missing)} section id(s) not found in the template (typo, "
              f"or a section this group doesn't own): {missing}", file=sys.stderr)
        return 1

    Path(out_path).write_text(template_html, encoding="utf-8")
    print(f"Wrote {out_path} ({len(fragments)} section(s) stitched in)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
