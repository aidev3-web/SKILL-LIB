#!/usr/bin/env python3
"""
Mechanical Phase-4 checks for sales-proposal-skill.

Run: python validate-proposal.py <client-slug>-proposal.html <client-slug>-findings.json

This checks only what's objectively countable — it does NOT verify that a cited
URL actually supports its claim, that a fact isn't fabricated, or that content is
"deep enough". Those stay judgment calls for the devil's-advocate review. This
script exists so the mechanical stuff (orphaned citations, missing sections, missing
.assess labels, broken findings.json) gets caught every time instead of depending on
someone remembering to grep for it by hand.

Exit code 0 = all checks passed. Exit code 1 = at least one check failed (see output).
"""
import json
import re
import sys
from pathlib import Path

REQUIRED_ASSESS_SECTIONS = ["implementation-roadmap", "change-management", "hypercare-support"]

MENU_STRUCTURE_PATH = Path(__file__).parent / "menu-structure.md"


def fail(msg):
    print(f"  FAIL  {msg}")
    return False


def ok(msg):
    print(f"  ok    {msg}")


def load_required_slugs():
    text = MENU_STRUCTURE_PATH.read_text(encoding="utf-8")
    return set(re.findall(r"^- `([a-z0-9-]+)`", text, re.MULTILINE))


def extract_section_ids(html):
    return set(re.findall(r'<section\s+id="([a-z0-9-]+)"', html))


def extract_section_body(html, section_id):
    # Grab from this section's opening tag to the next <section or </main>, whichever comes first.
    pattern = re.compile(
        r'<section\s+id="' + re.escape(section_id) + r'"[^>]*>(.*?)(?=<section\s+id="|</main>)',
        re.DOTALL,
    )
    m = pattern.search(html)
    return m.group(1) if m else None


def extract_cite_links(html):
    """Returns list of (href, is_inside_appendix) for every <a class="cite" href="...">."""
    appendix_body = extract_section_body(html, "appendix-sources") or ""
    all_links = re.findall(r'<a class="cite" href="([^"]+)"', html)
    appendix_links = set(re.findall(r'<a class="cite" href="([^"]+)"', appendix_body))
    return all_links, appendix_links


def main():
    if len(sys.argv) != 3:
        print("Usage: python validate-proposal.py <proposal.html> <findings.json>")
        sys.exit(2)

    html_path = Path(sys.argv[1])
    json_path = Path(sys.argv[2])
    passed = True

    print(f"\n=== 1. Output files exist ===")
    if not html_path.exists():
        passed = fail(f"missing {html_path}") and passed
    else:
        ok(f"{html_path.name} found")
    if not json_path.exists():
        passed = fail(f"missing {json_path}") and passed
    else:
        ok(f"{json_path.name} found")
    if not html_path.exists() or not json_path.exists():
        sys.exit(1)

    html = html_path.read_text(encoding="utf-8")
    findings = json.loads(json_path.read_text(encoding="utf-8"))

    print(f"\n=== 2. No leftover placeholder-note ===")
    # Only count actual usage (class="placeholder-note" on an element), not the
    # CSS rule definition (.placeholder-note{...} in <style>), which is always present.
    leftover = len(re.findall(r'class="placeholder-note"', html))
    if leftover:
        passed = fail(f"{leftover} placeholder-note occurrence(s) still in the file") and passed
    else:
        ok("none found")

    print(f"\n=== 3. No internal-anchor citations (href=\"#...\") ===")
    bad_anchors = re.findall(r'<a class="cite" href="(#[^"]*)"', html)
    if bad_anchors:
        passed = fail(f"{len(bad_anchors)} citation(s) point at an internal anchor instead of a real URL: {bad_anchors[:5]}") and passed
    else:
        ok("every citation href is an external URL")

    print(f"\n=== 4. Citation <-> Appendix consistency ===")
    _, appendix_links = extract_cite_links(html)
    appendix_body = extract_section_body(html, "appendix-sources") or ""
    non_appendix_html = html.replace(appendix_body, "")
    body_only_links = set(re.findall(r'<a class="cite" href="([^"]+)"', non_appendix_html))
    orphaned = body_only_links - appendix_links
    unused = appendix_links - body_only_links
    if orphaned:
        passed = fail(f"{len(orphaned)} citation(s) in the body have no matching Appendix row: {sorted(orphaned)[:5]}") and passed
    else:
        ok("every body citation has a matching Appendix row")
    if unused:
        passed = fail(f"{len(unused)} Appendix source(s) are never cited in the body: {sorted(unused)[:5]}") and passed
    else:
        ok("every Appendix source is actually cited")

    print(f"\n=== 5. Required sections present (from menu-structure.md) ===")
    required = load_required_slugs()
    present = extract_section_ids(html)
    missing = required - present
    if missing:
        passed = fail(f"{len(missing)} required section(s) missing: {sorted(missing)}") and passed
    else:
        ok(f"all {len(required)} required sections present ({len(present)} total in file)")

    print(f"\n=== 6. .assess label on Roadmap/Change Management/Hypercare ===")
    for sid in REQUIRED_ASSESS_SECTIONS:
        body = extract_section_body(html, sid)
        if body is None:
            passed = fail(f"section '{sid}' not found at all") and passed
        elif 'class="assess"' not in body:
            passed = fail(f"section '{sid}' has no .assess disclaimer") and passed
        else:
            ok(f"'{sid}' has an .assess disclaimer")

    print(f"\n=== 7. findings.json matches the body's citations ===")
    finding_urls = {f.get("source_url") for f in findings if f.get("source_url")}
    cited_urls = appendix_links  # appendix URLs are the canonical cited-source list
    missing_in_findings = cited_urls - finding_urls
    stale_in_findings = finding_urls - cited_urls
    if missing_in_findings:
        passed = fail(f"{len(missing_in_findings)} cited source(s) missing from findings.json: {sorted(missing_in_findings)[:5]}") and passed
    else:
        ok("every cited source has a findings.json entry")
    if stale_in_findings:
        passed = fail(f"{len(stale_in_findings)} findings.json entries don't correspond to any citation: {sorted(stale_in_findings)[:5]}") and passed
    else:
        ok("no stale findings.json entries")

    print(f"\n=== 8. Uses the real proposal-template.html shell (not a rebuilt design) ===")
    # A real run of this skill once shipped a completely different page (light theme,
    # purple hero, two separate VI/EN buttons) instead of the actual template. These
    # markers only exist in the real template's shell — if they're missing, something
    # upstream built its own design instead of filling in assets/proposal-template.html.
    TEMPLATE_MARKERS = [
        ('--teal:#19c6c6', "template's --teal color token"),
        ('id="sidenav"', "the #sidenav sidebar container"),
        ('id="progress"', "the #progress scroll bar"),
        ('onclick="toggleLang()"', "the single sliding VI/EN switch"),
        ('function buildNav()', "the buildNav() sidebar generator"),
    ]
    missing_markers = [desc for marker, desc in TEMPLATE_MARKERS if marker not in html]
    if missing_markers:
        passed = fail(
            "this file does not look like assets/proposal-template.html — missing: "
            + "; ".join(missing_markers)
            + ". Likely cause: an agent built its own page design instead of filling in "
            "the real template. Re-do Phase 1/3 with the actual template file attached."
        ) and passed
    else:
        ok("all template shell markers present — this is the real template, filled in")

    print()
    if passed:
        print("ALL MECHANICAL CHECKS PASSED. Still do the judgment-based Phase 4 checks by hand:")
        print("  - spot-check a sample of cited URLs actually supports the claim")
        print("  - devil's-advocate review of Odoo Architecture / Roadmap / RACI")
        print("  - RACI golden rule (exactly one A per row) — not auto-checked here")
        sys.exit(0)
    else:
        print("ONE OR MORE CHECKS FAILED. Fix them before delivering.")
        sys.exit(1)


if __name__ == "__main__":
    main()
