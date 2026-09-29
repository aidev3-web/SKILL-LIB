---
name: mechanical-validator
description: Runs assets/validate-proposal.py against an assembled sales-proposal HTML — the objectively-countable checks (chart/diagram manifest, hover-citation markup, no leftover placeholders, findings.json consistency, real template shell used). Called by the technext-sales-proposal orchestrator skill's Phase 4, right after html-renderer produces the draft, before judgment-reviewer.
---

# Mechanical validator — run the script first, every time

*Only `<client-slug>-proposal.html` needs to exist — safe to re-run any time (e.g.
right after a manual fix) without touching earlier phases.*

`prompt.txt`'s own instruction is explicit: *"after completion, do another round, make
it super comprehensive."* Treat this as a required step, not optional polish — and
this mechanical pass is the first half of it.

## Run it

```
python <skill-root>/assets/validate-proposal.py <client-slug>-proposal.html <client-slug>-findings.json
```

This checks exactly the objectively-countable rules — no leftover `placeholder-note`,
no internal-anchor citations, every citation has a matching Sources & Citation row and
vice versa, every required section from `menu-structure.md` is present,
`recommendations` actually has `.assess` labeling, `findings.json` matches the body's
citations, the real template shell/mechanism was used (not a rebuilt design), a real
spread of Chart.js canvases + static diagram blocks is present, citations use the
hover-card markup, and no `<CLIENT NAME>` placeholder or stale "Odoo 19" sidebar text
is left unfilled anywhere — including inside `buildNav()`'s JS string, which a quick
visual skim of the rendered page can miss until the sidebar is actually opened.

**Do not skip this because the file "looks" done** — the whole point is that these are
exactly the mistakes a careful-looking pass still makes (a prior real run of this
skill shipped with 27 orphaned citations and zero `.assess` labels despite looking
complete). Fix every failure it reports before moving on.

It does **not** replace `judgment-reviewer`'s checks — a clean run of this script is
necessary, not sufficient. Once it passes, hand off to `judgment-reviewer`.

## On failure

Route the specific failure back to whichever piece owns that content — a missing
chart/diagram goes back to the owning Phase 1 subagent (see the chart/diagram
ownership table in `technext-sales-proposal`'s `assets/charts-and-diagrams.md`), a
missing `.assess` on `recommendations` goes back to `front-matter-writer`, a broken
template-shell marker goes back to `html-renderer`. Don't hand-patch the HTML directly
to make the script pass — that just hides the same mistake happening again next run.
