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
    """Returns list of (href, is_inside_sources_citation) for every <a class="cite" href="...">."""
    sources_body = extract_section_body(html, "sources-citation") or ""
    all_links = re.findall(r'<a class="cite" href="([^"]+)"', html)
    sources_links = set(re.findall(r'<a class="cite" href="([^"]+)"', sources_body))
    return all_links, sources_links


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

    print(f"\n=== 4. Citation <-> Sources & Citation consistency ===")
    _, sources_links = extract_cite_links(html)
    sources_body = extract_section_body(html, "sources-citation") or ""
    non_sources_html = html.replace(sources_body, "")
    body_only_links = set(re.findall(r'<a class="cite" href="([^"]+)"', non_sources_html))
    orphaned = body_only_links - sources_links
    unused = sources_links - body_only_links
    if orphaned:
        passed = fail(f"{len(orphaned)} citation(s) in the body have no matching Sources & Citation row: {sorted(orphaned)[:5]}") and passed
    else:
        ok("every body citation has a matching Sources & Citation row")
    if unused:
        passed = fail(f"{len(unused)} Sources & Citation entries are never cited in the body: {sorted(unused)[:5]}") and passed
    else:
        ok("every Sources & Citation entry is actually cited")

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
    cited_urls = sources_links  # Sources & Citation URLs are the canonical cited-source list
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

    print(f"\n=== 9. Full chart & Mermaid manifest present (19 canvases + 9 diagrams, exact ids) ===")
    # The reference build (full1 / Casa Escondida) ships 21 named Chart.js canvases;
    # this skill drops the 2 tied to the removed PESTLE/Porter's Five Forces sections,
    # leaving 19 — SKILL.md's "Charts & diagrams" manifest requires this skill's output
    # to match that count and those exact canvas ids (content adapted per client, but
    # the slot itself must exist). This does not judge whether the plotted data is any
    # good — that's a judgment call.
    REQUIRED_CANVAS_IDS = [
        "cRevMix", "cScorecard", "cRevStream", "cHeadcount", "cSeasonStaff", "cChannel",
        "cDigital", "cSentiment", "cThemes", "cPosition", "cGap",
        "cOrigin", "cSeason", "cPersona", "cAuto", "cRisk", "cKpi", "cRoi", "cOwner",
    ]
    canvas_count = len(re.findall(r'<canvas\s+id="', html))
    mermaid_count = len(re.findall(r'class="mermaid"', html))
    regchart_count = len(re.findall(r'regChart\s*\(', html))
    has_chartjs = "chart.js" in html.lower() or "new Chart(" in html or "mkChart(" in html
    present_ids = set(re.findall(r'<canvas\s+id="([^"]+)"', html))
    missing_ids = [cid for cid in REQUIRED_CANVAS_IDS if cid not in present_ids]
    if missing_ids:
        passed = fail(f"{len(missing_ids)} of {len(REQUIRED_CANVAS_IDS)} required chart canvas ids missing: {missing_ids}") and passed
    else:
        ok(f"all {len(REQUIRED_CANVAS_IDS)} required canvas ids present")
    if canvas_count < len(REQUIRED_CANVAS_IDS):
        passed = fail(f"only {canvas_count} <canvas> chart(s) found total (manifest requires {len(REQUIRED_CANVAS_IDS)})") and passed
    else:
        ok(f"{canvas_count} chart canvas(es) found")
    if mermaid_count < 9:
        passed = fail(f"only {mermaid_count} Mermaid diagram(s) found (manifest requires 9: 1 Group A + 5 Group B + 3 Group C)") and passed
    else:
        ok(f"{mermaid_count} Mermaid diagram(s) found")
    if canvas_count and not has_chartjs:
        passed = fail("canvas elements present but no Chart.js script/mkChart() call found — charts won't render") and passed
    if canvas_count and regchart_count < canvas_count:
        passed = fail(f"{canvas_count} canvas(es) but only {regchart_count} regChart(...) registration(s) — charts built via a bare new Chart(...) call won't re-render on theme toggle") and passed

    print(f"\n=== 10. Citations use Wikipedia-style hover-card markup (.cite-wrap/.cite-tip + real excerpt) ===")
    # A citation must be wrapped so the source previews on hover/focus instead of only
    # being visible after clicking through, and the preview must actually contain an
    # excerpt (not an empty/placeholder tooltip).
    all_cite_tags = re.findall(r'<a class="cite" href="[^"]+"[^>]*>', html)
    wrapped_cites = re.findall(
        r'<span class="cite-wrap"[^>]*>\s*<a class="cite"[^>]*>.*?</a>\s*'
        r'<span class="cite-tip">\s*<span class="cite-tip-excerpt">(.*?)</span>',
        html, re.DOTALL,
    )
    bare_count = len(all_cite_tags) - len(wrapped_cites)
    empty_excerpts = sum(1 for ex in wrapped_cites if len(ex.strip()) < 10)
    if all_cite_tags and bare_count > 0:
        passed = fail(f"{bare_count} of {len(all_cite_tags)} .cite link(s) are not wrapped in .cite-wrap/.cite-tip/.cite-tip-excerpt — hover preview won't work for them") and passed
    elif all_cite_tags:
        ok(f"all {len(all_cite_tags)} citations use the .cite-wrap/.cite-tip hover-card markup")
    else:
        ok("no citations found to check (nothing to fail on)")
    if empty_excerpts:
        passed = fail(f"{empty_excerpts} .cite-tip-excerpt(s) are empty or near-empty (<10 chars) — need a real quote/paraphrase from the source") and passed

    print(f"\n=== 11. No unfilled <CLIENT NAME> placeholder anywhere ===")
    # The hero title, <title>, and the sidebar brand line in buildNav() ('× <CLIENT
    # NAME>') are all supposed to be replaced with the real client name during Phase 3
    # assembly. A real run once shipped with the hero still literally reading
    # "<CLIENT NAME>" and the sidebar still reading "Technext × Odoo 19" — both easy to
    # miss by eye since one is inside a JS string, not visible in a quick HTML skim.
    CLIENT_PLACEHOLDER_PATTERNS = [
        r'<CLIENT NAME>', r'&lt;CLIENT NAME&gt;',
        r'<TÊN KHÁCH HÀNG>', r'&lt;TÊN KHÁCH HÀNG&gt;',
        r'×\s*Odoo 19',  # the old hardcoded sidebar brand text this must never still say
    ]
    found_placeholders = [p for p in CLIENT_PLACEHOLDER_PATTERNS if re.search(p, html)]
    if found_placeholders:
        passed = fail(f"unfilled client-name placeholder(s)/stale text still in the file: {found_placeholders} — check the hero, <title>, AND the buildNav() sidebar brand line") and passed
    else:
        ok("no unfilled <CLIENT NAME> placeholder or stale 'Odoo 19' sidebar text found")

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
