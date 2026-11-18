# The framework: how to reason about a client deck

Use it in order. Each stage ends in a gate: do not start the next stage until the gate is passed. Sources are in brackets: TechNext's own rules, and the public skills we borrowed from (see `lessons.md`, 8 Nov 2026).

## Stage 1 · Brief: who is in the room, and what must they decide?
- **Audience:** the client's decision makers at the proposal meeting, then the same file opened alone on a laptop or phone. Name the `contact` (the profile's job title) and write to them.
- **The one decision:** "agree the scope, then kick off". Every slide must earn that ask. [proof before ask: owl-listener presentation-deck; claude-octopus skill-deck "end on decisions needed"]
- **Facts you may use:** the profile, TechNext's approved figures, the Odoo 20 catalogue line. Nothing else without a source the user gives.
- **Gate 1:** the profile validates (required fields, known apps, a country). Missing data is asked for or left out, never invented.

## Stage 2 · Story: six slides, one argument
| # | Job in the argument | Narrative beat | The one working object |
|---|---|---|---|
| 1 | Earn the right to advise | Who we are (credibility) | the approved figures counting up + the client's own nameplate |
| 2 | Show we listened | Situation and complication, in the client's words | ledger: their words → how Odoo answers (one per press) |
| 3 | Show the answer works as one system | Resolution | one sample record travelling app to app |
| 4 | Show how we work, and where they decide | De-risk the how | NextSprint rail: three disciplines, seven steps, the client's gates |
| 5 | Show when | De-risk the when | Gantt: four phases + hypercare, click for who does what |
| 6 | Ask | The decision | three steps + the booking QR |
- **Headline-only test:** the build prints the six headlines alone. Read them as one paragraph: they must tell the whole story and end on the ask. If one headline could sit in any other company's deck, rewrite it with the client's words. [claude-octopus skill-deck outline gate]
- **Proof before ask:** slide 6 may only ask for what slides 1-5 showed. No new claim, figure or promise on the close.
- **Gate 2:** storyline reads cleanly; `validate_deck` passes (one marker per title, titles ≤ 70 characters, 1-3 pain points, 1-6 apps on the rail, seven steps).

## Stage 3 · Slide craft: one statement + one working object
- **Statement:** the headline makes the point; exactly one marker phrase; 2-3 lines at most. [technext-presentations design]
- **Object:** something that moves or answers a press with meaning (counts, travels, draws, reveals). No decoration-only motion.
- **Split, never shrink:** when content does not fit, cut words or move them to the proposal; never shrink type below the scale (body 18-22, labels 15-16, titles 44/64/92). [zarazhangrui/frontend-slides]
- **Different compositions:** no two consecutive slides share a layout (stats + card / ledger / rail / steps / Gantt / QR). [anthropics/skills pptx]
- **Avoid the AI tells:** decorative numbering, a highlighted word in every line, fade-up on everything, symmetrical card grids, gradient text, generic stock phrases ("streamline", "seamless", "unlock"). Our one marker per headline and the real seven-step sequence are deliberate, not tells. [anthropics/skills frontend-design]
- **Gate 3:** `shots.py` passes (frame, overlap, clipped text, glyph clips, builds, arrow walk, print, phone) and every shot has been looked at.

## Stage 4 · Claims and voice
Run the rules in `rules.md`. Then the rationalisation check: if you catch yourself thinking any line in the table below, stop.

| The thought | The answer |
|---|---|
| "The client asked us to say BIR-ready." | Never. Say "set up for BIR requirements"; the disclaimer goes on the close. |
| "One price would give context." | No prices in the deck. The proposal carries every figure. |
| "The text is a bit long; shrink it to fit." | Split, never shrink. Cut the words. |
| "Northgate's pain point is vague; I'll add a number to make it vivid." | Pain points are hypotheses in the client's own words. Add nothing they did not say. |
| "This client is in Singapore but the tax line says BIR." | Country decides tax wording: PH = BIR, SG = GST, else local requirements. |
| "Another client's deck had a nice line; reuse it with their name." | Never another client's name or sample in a client deck. |
| "Odoo Community is free, so…" | Odoo is never "free". Licences are billed by Odoo, per user per month. |
| "Let me add a quick button for the presenter." | Only arrows, click, tap, swipe and the page counter. |
| "The plan is a guess anyway; I'll promise a go-live date." | Indicative plan, confirmed at kick-off. No dates. |

## Stage 5 · Review: Impeccable, then refine only
- Critique (/40) and audit (/20) as two isolated agents on fresh shots; verify every finding by measuring before acting.
- Fix everything real in ONE batch, rebuild, rerun `test_suite.py --shots`, confirm with one fresh agent, stop.
- **The last pass refines only:** align, tighten, remove. Never add a new element after the review. Ask "what can be taken away?" [anthropics/skills canvas-design]
- **Gate 5:** design ≥ 28/32 (7 and 10 n/a) and technical ≥ 17/20, no P0/P1 open.

## Stage 6 · Delivery
`deliver.py` (dry run first), md5 on every file, old revision to `00. old`, the user gets the HTML + previews + the Drive path, and how to open it: download the HTML and open it in Chrome or Edge (Google Drive's preview does not run it), F11 for full screen, arrows or a clicker to present.

## Lapse register (found 8 Nov 2026 by the edge-case suite; each now has a guard)
| Lapse | Seen in | Guard |
|---|---|---|
| "Point of Sale" rejected (catalogue names it "Point of Sale — Shop") | solo | ALIAS + suite case `solo` |
| "1 users" | solo | plural helper + check_deck |
| A cashier pain point answered as stock counting (`count` matched stock) | solo | ordered, bounded patterns + suite `must_not` |
| "notebook" matched books → patient bookings answered by Accounting | stalucia | `\bbooks?\b`, appointments entry + suite |
| Missing sample record → "creates Sample" | stalucia | RECORD for every common app + suite |
| BIR pain point treated as reporting (wrong pattern order) | pacific | tax pattern first + suite `must` |
| BIR mentioned without the not-affiliated disclaimer | pacific | auto disclaimer on the close + check_deck |
| BIR wording in a Singapore deck | lionsg | country-aware tax line + check_deck |
| No logo file → unreadable 10px SVG nameplate | pacific, stalucia | the name set as text on the plate and in the chrome |
| POS icon missing on slide 2 (lookup by display name) | solo | rows carry the module; build stops if an icon is missing |
| Record id wrapped under "creates" with 6 apps | pacific | `.many` layout for 5-6 stations |
| One pain point leaves slide 2 small and empty | solo | `.single` layout |
| "Sprint" tripped the print-button ban; Odoo's "vendor pricelists" tripped the brand-word ban | pacific | word boundaries, TechNext-only phrasing |
| Glyphs cut by word masks or overflow clips (owner rule 7 Nov) | all | shots.py glyph-clip pixel test (proved on a tight-mask copy) |
| Text on text (overflow checks miss overlap) | all | shots.py overlap test (proved on a moved element) |
| Internal text on a slide (TODO, file paths, null) | all | check_deck leak scan (proved) |
| A hand edit breaks the deck silently | all | validate_deck with fix-it messages |
