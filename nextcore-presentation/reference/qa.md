# QA gate (before every delivery)

The scripts check what they can; you check the rest by looking. Never say "verified" for something you did not open.

## Automatic
- [ ] `build_deck.py` ends with `checks: PASS` (check_deck.py: claims, other clients' names, nothing loaded from outside the file, no extra UI, 6 slides, one marker per headline).
- [ ] `build_deck.py` storyline: the six headlines read as one argument ending on the ask; `validate_deck` passes.
- [ ] `shots.py` ends with `PASS`: no script errors; every slide finished at its last build; no text outside the 120px frame or below y 842; no text on text; no clipped one-line text; no glyph cut by a word mask or overflow clip; the arrow key walks the deck to the last slide; print gives 6 finished pages; a phone held upright turns the deck.
- [ ] After a template or builder change: `test_suite.py --shots` all PASS.
- [ ] `deliver.py --dry-run` lists the right client folder, file name and revision, and any move to `00. old`.

## By eye (shots + contact sheet `out/shots/qa/sheet.jpg`)
- [ ] Every slide: one headline with one marker, the hierarchy reads at a glance, nothing crowded, nothing in the chrome or footer band, left and right balanced.
- [ ] First builds (`out/shots/qa/0N-first-build.png`): what the room sees on arrival is never an empty frame.
- [ ] The client's logo is crisp on the opener plate and legible in the chrome; the client colour reads against paper.
- [ ] Copy: British spelling, the client's name and short name right, numbers match the profile (users, apps), the plan weeks match the proposal if it exists.
- [ ] Phone shot: the deck turned sideways and fills the screen's long side.

## Impeccable (owner rule: every deck)
Run the `impeccable` skill's critique and audit as TWO isolated sub-agents (Sonnet is enough), on shots taken right before launch (reviewers judge the shots they get). Give each the target path, the shots, `qa/probe.py` for live JS probes, and the fixed constraints (branding, no masking, no icon tiles, only the asked-for controls, light only, the copy rules) so they do not recommend breaking them.
- **A: critique** (design review, Nielsen /40; Persuade mode so 7 and 10 may be n/a): specificity verdict, scores, cognitive load, peak-end, strengths, 3-5 P0-P3 issues with concrete fixes, personas (the adviser with a clicker; the client's manager alone on a laptop; the same on a phone).
- Add to A's brief: name each slide's composition (no two consecutive slides alike); list any AI tells (decorative numbering, a highlight in every line, fade-up on everything, symmetrical card grids, gradient text, "streamline/seamless/unlock"), exempting our single marker per headline and the real seven steps; answer "what can be taken away?".
- **B: audit** (technical /20): `impeccable detect --json <html>` once, verified in context; measured contrast per slide (dark slides against navy), text sizes, keyboard and focus, reduced motion, print, performance, phone rotation and swipe, tokens.
- Verify each finding before acting (reviewers estimate sizes from contact sheets; measure in the page). Fix everything real in one batch, rebuild, reshoot, confirm once with one fresh agent. Then a refine-only pass (align, tighten, remove; never add). Report both scores (before and after). Gate: design >= 28/32, technical >= 17/20, no P0/P1.

## Motion
- [ ] Each slide's object moves with meaning (rules.md, Motion); a slide is built by about 1.5 s; one spring in the deck; reduced motion lands finished.
- [ ] Use `find-animation-opportunities` / `improve-animations` when the template's motion changes.
