---
name: nextcore-presentation
description: Use when building, revising or checking a NextCore client presentation, the Presentation card (`deck`) of NextCore - e.g. "nextcore presentation", "nextcore deck", "build the presentation for <client>", "client deck from the profile", "presentation builder", "new revision of <client>'s deck", or when NextCore's build order reaches the deck card - even if the user doesn't say "skill". Makes ONE self-contained six-slide HTML from the client's client-profile.json in TechNext's house design (no launcher, buttons or settings) and files it into 01. Client Folder\NN. <Client>\04. Presentation. Not for decks in the technext-presentations repo or its launcher (technext-presentations), the sales proposal (nextcore-proposal), the SLA (nextcore-sla) or PowerPoint files (pptx).
---

# NextCore presentation builder

One client profile in, one HTML presentation out: the Presentation card (`deck`) of NextCore, TechNext's material production system. Nothing is sent to a client automatically.

The user's words (5 Nov 2026): "duplicate the technext presentation skills, create a skills where to create a html presentation using skills of technext presentation. dont create a compilation. just create a html. dont add button or setting that not needed." (8 Nov 2026): "enrich the skill for building presentation. create a framework and check all lapses and needed to be address."

| What | Where |
|---|---|
| This skill | `~/.claude/skills/nextcore-presentation/` (template, scripts, assets, `tests/cases.json`) |
| Working folder | `~/ClaudeWork/nextcore-presentation/clients/<client-slug>/` (profile, logo, `deck.json`, `out/`); suite builds in `.../tests/` |
| Client delivery | `G:\Shared drives\Marketing\01. Client Folder\NN. <Client>\04. Presentation\` (+ `preview\`, sources in `_build\presentation\`, old revisions in `NN. <Client>\00. old\`) |
| Builder home on Drive | `G:\Shared drives\Marketing\02. TechNext Folder\24. NextCore (New Client Build)\Presentation builder\` |
| Source skill (read, never edit) | `~/.claude/skills/technext-presentations/` and the repo `TechNextSG/technext-presentations` |
| Memory | `project_nextcore_presentation_builder.md` |

## Read first
- `reference/framework.md`: the six gated stages (brief, story, slide craft, claims, review, delivery), the headline-only test, the rationalisation table and the lapse register. **Follow it for every deck.**
- `reference/rules.md` (claims, voice, design, motion) · `reference/mapping.md` (profile → slides, the pain library) · `reference/engine.md` (before touching the template) · `reference/qa.md` (the gate, reviewer briefs) · `reference/evals.md` (how to test the skill) · `reference/lessons.md` (what went wrong before).
- The profile is the only source of client facts. Never invent a figure, client, price or date. Pain points are hypotheses.

## The pipeline (each step is a gate)
1. **Client folder:** `clients/<slug>/client-profile.json` + the logo named in `brand.logo` (none = the name is set as text). Add `"country"` when the city has no PH/SG/VN suffix: it decides the tax wording (PH = BIR + disclaimer, SG = GST, else local requirements).
2. **Build:** `python -I -X utf8 ~/.claude/skills/nextcore-presentation/scripts/build_deck.py <client dir>`
   - First run writes `deck.json` (all the words). Read the printed **storyline**: the six headlines alone must tell the story and end on the ask (framework Stage 2). Edit `deck.json` to fit this client, then build again (`--regen` rebuilds it from the profile and loses edits).
   - The build stops with fix-it messages when `deck.json` breaks a rule (markers, title length, counts) and when `check_deck.py` fails (claims, other clients' names, leaked internal text, external loads, extra UI, BIR in a non-PH deck, the BIR disclaimer).
   - If the Sales Proposal exists, copy its weeks and sprints into `deck.json` (`plan`, `method.steps[].em`).
3. **Shoot:** `python -I -X utf8 scripts/shots.py <client dir>/out/presentation.html --name <slug>`. It fails on text outside the frame, text on text, clipped text, glyphs cut by masks, hidden builds, the arrow walk, print (6 finished pages) and the phone turn. LOOK at every shot and `out/shots/qa/sheet.jpg`.
4. **Review:** Impeccable critique (/40) + audit (/20) as two isolated agents on fresh shots, motion via `find-animation-opportunities` (`reference/qa.md`). Verify findings by measuring, fix in one batch, confirm once, then a refine-only pass. Gate: design ≥ 28/32, technical ≥ 17/20, no P0/P1.
5. **Deliver:** `python -I -X utf8 scripts/deliver.py <client dir> --dry-run`, then for real. md5 on every copy; an older revision moves whole to `00. old`. Name: `<Client> - TechNext Presentation Rev X.Y (Draft).html`; bump `rev` for every re-issue; `--status Sample` for test clients; `--to "<folder>" --name nextcore` for a flat copy.
6. **Hand over:** send the HTML + previews (SendUserFile) with the Drive path and how to present: download the HTML and open it in Chrome or Edge (Drive's preview does not run it), F11 for full screen, arrows or a clicker; on a phone it turns sideways.
7. **Train the skill:** log the job in `lessons.md`; a new lapse gets a failing case in `tests/cases.json` first, then the fix; run `python -I -X utf8 scripts/test_suite.py --shots` (all PASS) after any change to the template, builder or libraries; update the memory file.

## Non-negotiables
| Rule | Source |
|---|---|
| ONE standalone HTML per client. No launcher, deck index, repo entry, share links, or PDF unless asked (print CSS exists). | user, 5 Nov 2026 |
| Only arrows / PageUp / PageDown / Space (clickers), click or tap, swipe, and the footer page number. No presenter view, TV mode, settings, menus, share/print/download buttons, progress bar or toolbars. | user, 5 Nov 2026 |
| 1600x900 stage that scales whole; a phone held upright turns the deck 90°. | engine |
| technext.asia branding: site.css tokens, Plus Jakarta Sans + Inter (+ Caveat kicker), light slides, navy only for the opener and close. No dark mode. | feedback_technext_website_branding_design, feedback_no_dark_mode |
| No background masking (fields, ovals, bands, glows, fades, blur, greyed icons). No icon tiles. | feedback_no_background_masking_decks, feedback_no_icon_tiles |
| Adviser voice: "Your trusted expert adviser for ERP and compliance."; "We advise first, then deliver the whole solution."; British "adviser". | feedback_technext_adviser_voice |
| Odoo never "free"; no prices in the deck. | feedback_odoo_not_free_claims |
| No BIR guarantees or BIR-ready/compliant/accredited; any BIR mention carries the not-affiliated disclaimer; BIR wording only for Philippine clients. | feedback_no_bir_guarantees_in_copy |
| "Odoo Ready Partner in Singapore" only. | feedback_odoo_partner_singapore_only |
| No other client's name anywhere in a client deck. | feedback_client_isolation |
| Every deck: Impeccable critique + audit (two isolated agents), purposeful motion, and a glyph-clip check of every title. | feedback_presentations_impeccable_motionmaxxing, feedback_audit_clipped_type_and_lapses |
| Approved figures only: 142 ERP projects, 40+ years of excellence, 90+ enterprise clients, 25+ countries. | technext-presentations content rules |
| No WhatsApp link or number; sales@technext.asia as plain text. | feedback_technext_site_rules_oct21, feedback_sales_email_not_clickable |
| Split, never shrink: content that does not fit is cut or moved to the proposal, never set below the type scale. | frontend-slides, 8 Nov 2026 |
