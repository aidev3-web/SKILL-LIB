---
name: sales-proposal-skill
description: Turn a prospective TechNext client (a company name, website, or short brief) into one comprehensive, bilingual (VI/EN toggle) self-contained HTML sales proposal website covering all three TechNext service lines — Odoo ERP implementation, AI Solutions, and Social Media Marketing — deep web/social research, a fixed ~45-item sidebar covering Due Diligence, Strategic Analysis (PESTLE/SWOT/Porter's/competitors), Operations, Technology architecture (Odoo 19 + AI + social media) & demo-data plan, Delivery roadmap, Growth strategy, and a Tools & Documents section (AI Build Playbook, Profit Estimator, Quotation, Content Calendar, Discovery Questions, etc). Use when asked to research a client and build a sales proposal / due-diligence site, "làm sales proposal", "nghiên cứu khách hàng làm đề xuất", or when the request matches the client-research-to-proposal workflow (spin up agents, research a company, produce a growth plan with a big sidebar).
---

# Sales proposal skill — client research → TechNext sales proposal site (Odoo ERP · AI · Social Media)

## What this is for

TechNext sells three service lines: **Odoo ERP implementation, AI Solutions, and
Social Media Marketing** — not just Odoo. Before pitching a prospective client, Trung
researches them thoroughly and produces one big HTML "site" that doubles as a
due-diligence report and a sales proposal: who the client is, their market and
competitors, and a concrete plan across all three TechNext service lines for them. He
used to re-type a long manual prompt for this every time (`prompt.txt` in the original
working folder, originally Odoo-only) — this skill packages that workflow, now
generalized to all three lines, so anyone at TechNext can run it consistently.

**Every proposal always pitches all three service lines** — Odoo ERP, AI Solutions,
and Social Media Marketing — grounded in this specific client's own research (their
real pain points, their real digital/social presence), never a generic three-service
pitch copy-pasted across clients. Don't ask the user which service(s) to include;
that decision was already made — always all three.

**Output**: exactly one self-contained `.html` file, `<client-slug>-proposal.html`,
with a fixed ~45-item sidebar (client-side JS nav, no page reloads), a VI/EN language
toggle, and a light/dark theme toggle. Never split "Tools & Documents" items into
separate files — they are sections inside the same file.

**Every factual claim must be verifiable, not just plausible-sounding.** This is a
hard requirement, not a style preference: a sales/due-diligence document that states
facts about a real company with no way to check them is not trustworthy, and TechNext
is putting its name on it. Concretely:
- Any claim that came from a real source (a web page, an article, a review site, a
  social profile, an official filing) gets a visible, clickable citation link right
  next to it in the delivered HTML — see "Citations" under Phase 3/4 below.
- Any claim that is TechNext's own inference/estimate/opinion rather than something
  found in a source (an assumption about likely pain points, a projected KPI, a
  strategic recommendation) must be **labeled as such** — never presented with the
  same visual weight as a sourced fact. Use `.assess` (see template CSS) or an explicit
  "Đánh giá của Technext / Technext assessment" tag.
- Never invent a number, quote, review, or named person and attach a fake-looking
  citation to it. If something can't be found or verified, say so in the section
  instead of guessing confidently.

## Reference files — read before writing anything

- `assets/menu-structure.md` — the exact, fixed sidebar structure (group → item →
  slug → VI/EN labels). This is the source of truth for section IDs, order, and
  grouping. Do not drop, rename, or reorder items; you may add an extra item inside an
  existing group if research surfaces something that doesn't fit anywhere ("add more
  relevant categories" is allowed, removing/reordering fixed ones is not).
- `assets/proposal-template.html` — the working shell, styled to match Trung's actual
  reference build ("Casa Escondida Anilao · Strategic Due Diligence & Odoo 19 ERP
  Blueprint · Technext.html", kept alongside `prompt.txt` in the original working
  folder): dark/light `--bg`/`--panel`/`--teal` CSS-variable theme, sticky `#sidenav`,
  scroll progress bar, mobile hamburger nav, hero cover section, and a component
  library (`.card`, `.grid.g2/g3/g4`, `.kpi`, `.pill.p-*`, `.tbl`, `.quad` for SWOT,
  `.tl` timeline, `.acc` accordion, `.tabs`/`.tabpane`, `.callout`). Copy this file as
  your starting point for every run.
  - **The sidebar is not hand-written.** `buildNav()` generates it at load time from
    every `<section data-nav-vi="..." data-nav-en="..." data-grp-vi="..." data-grp-en="...">`
    in `<main>` — tag each section correctly and the nav (grouped, ordered by DOM
    order) appears automatically, exactly the mechanism the real reference file uses
    (there it reads plain `data-nav`/`data-grp`; this template adds the `-vi`/`-en`
    suffix pair so `buildNav()` can also switch label language). Never add `<a>` links
    to `#sidenav` by hand.
  - The nav also has an **⬇ Install** button (PWA `beforeinstallprompt`/`pwaInstall`).
    It stays hidden until the browser's PWA install criteria are actually met, which
    needs **all four** of: served over https (or localhost), the linked
    `manifest.webmanifest` (already in `<head>`), a registered `sw.js`, and at least a
    192×192 + 512×512 icon — `assets/manifest.webmanifest`, `assets/sw.js`,
    `assets/icon-192.png`, `assets/icon-512.png` are provided for exactly this and must
    be deployed **alongside** the final HTML file, at the same relative path (all four
    files sit next to `<client-slug>-proposal.html`, not nested differently). It's a
    no-op, not a bug, when the file is opened locally via `file://` — browsers never
    install from `file://`. Don't try to "fix" it into always showing — that would be a
    fake state, not a working install button.
    - **Deploying through a wrapper/router app** (e.g. a personal "reports viewer" on
      Vercel that serves this file at a hash-routed URL like `#Sales%20Proposal/
      proposal-template.html` instead of as a real static file at its own path) breaks
      the relative `manifest.webmanifest`/`sw.js`/icon links — the browser resolves
      them against whatever the wrapper's actual base path is, which usually isn't
      where these four files were uploaded. If the install button needs to work, the
      proposal + its 4 companion files need to be deployed as their own static site at
      a real path (GitHub Pages, a plain Vercel static deployment, or any static host)
      — not embedded inside another app's hash-routed viewer. Say this explicitly if
      the user reports the button missing after deploying through such a wrapper,
      rather than re-debugging the HTML/JS itself.
  - Fill in each section's body (replace every `placeholder-note` paragraph with real
    bilingual `t-vi`/`t-en` span pairs), replace `<CLIENT NAME>`/`<TÊN KHÁCH HÀNG>` in
    the hero and `<title>`, and delete the template-instructions HTML comment before
    delivering. Do not restructure the shell (CSS tokens, `buildNav`/`toggleTheme`/
    `setLang` scripts) per client — only section bodies, hero text, and title/branding
    change.
- `scripts/validate-proposal.py` — the Phase 4 mechanical validator (run via `python`).
  Checks only what's objectively countable: no leftover placeholders, no
  internal-anchor citations, citation/Appendix consistency, required-section
  coverage, `.assess` presence on the three delivery sections, and `findings.json`
  consistency. It does not check factual accuracy or content depth — those stay
  judgment calls. See Phase 4 for when to run it.

## Phase 0 — Intake

Get the client identifier: company name, plus any URL/socials the user already gives.
If all you have is a bare name, do one round of web search to find their site/socials
yourself rather than stopping to ask — only ask the user directly if the name is too
ambiguous to search confidently (e.g. a generic name with many unrelated companies).
Confirm the client name you'll use in the page `<title>`, following the pattern
`"<Client> · Strategic Due Diligence & Growth Blueprint (Odoo ERP · AI · Social Media) · Technext"`.

**Disambiguation gate (adapted from OSINT investigation practice).** Before spending
any research effort, confirm you have the *right* company — many names collide across
industries and countries. Pin down: legal/trading name, country/city, industry, and (if
findable) a registration number or official domain. If two candidates are plausible, say
so and ask rather than silently picking one and researching the wrong company for 40
sections.

**Research depth.** Default to a full "Standard" pass across every section. If the user
says they just want a quick draft, or the client clearly has very little public
footprint, use a "Quick" pass instead: fewer research agents, thinner sections, but
still real citations — never fabricate depth that wasn't actually researched. State
which depth you're using before starting.

**Engagement framing (adapted from management-consulting practice).** Before research
starts, note — in your own head, not necessarily asked aloud unless genuinely unclear —
what TechNext is trying to accomplish with this specific proposal (a cold pitch? a
follow-up after a call? a specific pain point already mentioned?). This shapes which
sections deserve the most depth; a cold pitch needs a stronger Due Diligence + Executive
Summary, a warm follow-up can lean harder into the relevant Proposed Solutions section
+ Quotation. It does **not** change which service lines appear — all three (Odoo ERP,
AI, Social Media) are always pitched, only how much depth each gets.

**Scope & ethics boundary (adapted from OSINT practice).** Research stays limited to
information a company and its leadership have made public in a business capacity
(company sites, business filings, press, professional social profiles, public reviews).
Never pursue private/personal information about individuals unrelated to their business
role, and never use non-public collection methods (scraping behind logins, social
engineering, breach data). If a request pushes past this line, decline that part and
say why, rather than quietly complying.

## Phase 1 — Research + write fan-out (one round, not two)

**Wall-clock note — read before spawning anything.** The number of agents controls
token cost; the number of *sequential phases* controls wall-clock time, and that
matters more here. An earlier version of this skill ran research and writing as two
separate sequential phases (agents research → hand off findings → different agents
write), which — even with every agent inside each phase running in parallel — still
meant the whole pipeline queued through 4–5 sequential stages, adding up to 45
minutes–2 hours per proposal. The fix is to stop separating "research" from "write":
**each agent below does its own research (via its own WebSearch/WebFetch calls) and
writes its own final HTML sections in the same call**, cutting one entire sequential
stage. Combined with the earlier agent-count reduction, this is what actually moves
the needle on total time, not just token spend.

Launch **4** `Agent` calls in parallel (single message, multiple tool uses), all
`general-purpose` (each prompt is fully self-contained — no need for `fork` here).
Each one gets: the client identifier from Phase 0, the exact section slugs/headings it
owns (from `assets/menu-structure.md`), the citation/`.assess` rules below, and the
CSS classes to reuse for structure (`.card`, `.grid.g2/g3/g4`, `.kpi`, `.pill.p-*`,
`.tbl`, `.quad`, `.tl`, `.acc`, `.tabs`/`.tabpane`, `.callout`). Instruct every agent to
return, alongside its finished section HTML, a short plain-text digest of its 3–5
most important findings — Phase 2 uses these digests to write the front matter without
re-reading every agent's full section HTML.

**Group A — Due Diligence + Strategic Analysis** (`due-diligence`, `company-profile`,
`product-catalog`, `founders-leadership`, `staff-org`, `digital-web`,
`reviews-reputation`, `strategic-analysis`, `pestle`, `swot-tows`, `porter-5-forces`,
`competitor-deep-dive`, `market-industry`, `customer-personas`): research the company
itself, its founders/leadership, staff/org signals, digital & social presence, reviews,
market/industry, and direct competitors — then build PESTLE/SWOT-TOWS/Porter's Five
Forces and write all these sections itself, in the same call. Paired because Strategic
Analysis is directly derived from Due Diligence facts — one agent keeps that
traceability tight instead of a second agent guessing what the first one found.
Capture social-specific detail explicitly in `digital-web` (which platforms are active
vs. absent, content mix, posting cadence, obvious gaps) — Group C's Social Media
pitch depends on this. Also build:
- **TAM/SAM/SOM sizing** (adapted from market-research practice) inside
  `market-industry` — Total Addressable Market, Serviceable Available Market,
  Serviceable Obtainable Market — each number sourced (`.cite`) where a real
  market-sizing figure exists, or `.assess`-tagged with the reasoning shown, never
  presented as precise when it's actually a rough order-of-magnitude guess.
- **Competitor comparison table** inside `competitor-deep-dive` — one `.tbl` row per
  competitor, columns for positioning, pricing tier, strengths/weaknesses, each cell's
  claims individually cited.
- **Messaging Comparison Matrix + Content Gap Analysis** (adapted from
  `marketing:competitive-brief`) inside `top3-competitor-deep-dive` (this section
  lives with Group C below, but if Group A finds strong messaging/content-gap
  material while researching competitors, pass it to Group C rather than duplicating
  the research) — a `.tbl` with one row per messaging theme (e.g. "price", "speed of
  service") and one column per competitor plus this client, showing who claims what.
- **Digital & Web Presence as a real audit, not a description** (adapted from
  `marketing:brand-review` + `marketing:seo-audit`): audit the client's actual
  site/social content — each issue found gets a severity `.pill`
  (**High/Medium/Low**), and the highest-severity ones get a short **before/after**
  example (their actual current text next to a corrected version). Fold in a small
  SEO checklist table (title tags, meta descriptions, mobile responsiveness, page
  speed signal, structured data) with a pass/fail `.pill` per item — only for what was
  actually checked, don't invent technical findings.
- **Customer Personas** (adapted from persona-building practice): structured cards
  (`.grid.g2`/`.g3` of `.card`) — name/role archetype, goals, pains, preferred
  channels, how TechNext addresses each — grounded in this group's own
  reviews/social/market findings.

**Group B — Operations + Technology** (`operations`, `stakeholder-perspectives`,
`department-workflows`, `pain-solution-matrix`, `bpmn-blueprint-uml`,
`ai-automation-catalog`, `ai-in-action`, `odoo-architecture`, `data-migration`,
`social-media-architecture`): all 4 groups launch in the same parallel batch, so this
group does its own quick check of the client's leadership/staff/about pages for
`stakeholder-perspectives` rather than waiting on Group A's output (a little
redundant research across groups, same trade-off as Group D below — worth it to stay
parallel). Then infer likely department workflows and pain points for a company of
this profile/industry (the `business-analyst` discovery checklist — stakeholders,
process mapping, pain points, KPIs), and build and write, itself, in the same call:
- **Stakeholder Perspectives** (adapted from `sales:stakeholder-map`): a `.tbl` —
  Person/Role / Likely stance / Influence level / Evidence — one row per stakeholder
  found or reasonably inferred. Add a **single-threaded warning** (`.callout.warn`) if
  only one named contact was found — name which other roles TechNext should try to
  reach and why. (Phase 4's review pass cross-checks this against Group A's
  founders/leadership findings and reconciles any mismatch.)
- **Odoo 19 architecture, module plan, and demo-data plan** — the concrete next step
  `prompt.txt` calls out. Name specific Odoo 19 modules this client needs, what demo
  data should populate each for a convincing demo, and the data-migration plan from
  their likely current tools — concrete, not generic.
- **AI Solutions plan** — 2–4 concrete AI/automation use cases tied to a real pain
  point or process gap this group found, not generic "AI can help with everything."
- **Social Media Marketing architecture plan** inside `social-media-architecture` —
  platforms, content pipeline, tools/reporting stack; if this group needs specifics
  about the client's current social presence beyond what it can reasonably infer, do
  a quick independent check rather than blocking on Group A's output (a little
  redundant research across groups is a fine trade for staying parallel).
- **Pain → Solution Matrix**: prioritize with MoSCoW inside the `.tbl` — a
  `Must/Should/Could/Won't`-style `.pill` per row.

**Group C — Delivery + Competitive Intel + Growth & Strategy**
(`implementation-roadmap`, `change-management`, `hypercare-support`,
`risk-register-raci`, `kpis-benefits`, `competitive-intel`,
`top3-competitor-deep-dive`, `pricing-strategy`, `regional-expansion`,
`modern-alternative-services`, `advisory`, `appendix-sources`): reason about growth
strategy, pricing strategy, regional expansion, and risk factors for this client (the
management-consultant pass), do its own competitor research for
`top3-competitor-deep-dive` (including the Messaging Comparison Matrix + Content Gap
Analysis described under Group A), and write:
- **Risk Register & RACI** (adapted from project-risk-register + RACI-matrix
  practice): Risk register `.tbl` — Risk / Probability (1–5) / Impact (1–5) / Score /
  Owner / Mitigation / Contingency, scores ≥20 get `.p-red` + an executive-attention
  note, 12–19 `.p-amber`, below that `.p-green`, realistic spread, plausible owner
  roles even with no real names yet. RACI `.tbl` — activities as rows, roles as
  columns. **Golden rule: exactly one A per row, never zero, never two.** Cap
  Consulted at ~3 roles per row.
- **`.assess` disclaimer on Implementation Roadmap, Change Management, and Hypercare
  & Support, every time — not optional.** These are TechNext's own standard delivery
  methodology (phase names, week counts, SLA thresholds), not researched fact — put
  one `.assess` span right after each section's `.lead` paragraph saying so. A prior
  run shipped all three with zero `.assess` labeling — don't repeat that.
- **Mutual Action Plan** (adapted from `sales:close-plan`) at the end of
  `implementation-roadmap`: a `.tbl` — Step / Owner (TechNext or Client) / Target date
  (relative, e.g. "Week 1") / Done-when — the concrete path from "proposal delivered"
  to signature.

**Group D — Tools & Documents** (all `tool-*` sections): each item is a practical
artifact inlined as its own section (not a separate file): AI Build Playbook, Profit
Estimator (plain inline `<script>` calculator, no external libraries), Owner FAQ,
Odoo Platform overview, Requirements/BRD, Quotation (itemize all three service lines),
Accounting Overhaul notes, Demo Walkthrough script, Staff Guides outline, Discovery
Questions, and Social Media Content Calendar. This group works from general
industry-appropriate assumptions about pain points/modules rather than waiting on
Groups A/B's exact output — Phase 4's devil's-advocate review is what catches any
mismatch, so a little independence here is an acceptable trade for staying parallel.
- **Requirements (BRD)**: Given/When/Then acceptance criteria (adapted from
  business-analyst practice) tied to a plausible pain point — e.g. "Given a
  reservation is confirmed, when payment is captured, then Odoo Accounting posts the
  invoice automatically" rather than "system should handle payments."
- **Social Media Content Calendar**: a concrete sample 4-week posting plan using
  **O-A-M-C-M framing** (adapted from `marketing:campaign-plan`) — Objective,
  Audience, Message, Channel, Measure — with realistic production timelines (a
  blog-style post ~3–5 days, a landing-page-style asset ~5–7 days) and
  campaign-type-specific KPIs (lead-gen tracks CPL/MQL; awareness tracks
  reach/share-of-voice). Include **1–2 real sample posts written out in full**
  (adapted from `marketing:draft-content` — hook line, body, CTA), not just a
  schedule grid.

Each agent must attach a source URL to every claim it makes (**every fact must carry
the exact page it came from**, not just the domain), and mark clearly which findings
it could *not* verify with a real source rather than smoothing over the gap. A claim
with no URL and no "unverified"/`.assess` flag is not usable — treat it as if it
weren't written.

**Source independence (adapted from OSINT investigation practice).** A fact
copy-pasted across ten content-farm/aggregator sites that all trace back to the same
original bio or press release is **one source, not ten** — this matters most for
Founders & Leadership, Staff & Org, and Reviews & Reputation. Trace a claim back
toward its original source rather than counting duplicates as independent
confirmation.

**Confidence grading.** Alongside the URL, each finding gets a rough confidence grade:
- **A** — primary/official source (company site, filing, direct quote).
- **B** — reputable independent secondary source (established press, industry report).
- **C** — single unverified or user-generated source (one review, one social post).
- **D** — unverifiable / TechNext inference — this is what becomes an `.assess` tag,
  never a `.cite` link, in the delivered HTML.

**Structured findings file.** In addition to the HTML deliverable, also write a
`<client-slug>-findings.json` alongside it: an array of
`{ "claim": "...", "section": "<sidebar slug>", "source_url": "...", "grade": "A|B|C|D" }`
objects, one per citation actually used. This is the "next step for the AI to connect to
MCP" that `prompt.txt` calls out — a machine-readable fact base is what a later
MCP-connected session would load into Odoo as CRM/company records, instead of having to
re-parse the HTML.

## Phase 2 — Write the front matter yourself (no agent needed)

`overview`, `why-ai`, `exec-summary`, `solution-odoo-erp`, `solution-ai`, and
`solution-social-media` are written directly by you, not another agent — this is fast
synthesis of what Phase 1's four groups already found and returned (their short
digests, from Phase 1's instructions), not new research, so spawning a fifth agent for
it would just add another sequential wait for no real benefit.

- **Executive Summary ICP-fit table** (adapted from `sales:account-research`): before
  the prose recommendation, a small `.tbl` scoring this client's fit — industry match,
  company size, likely buyer persona reached, timing signal — each cell **Strong /
  Moderate / Poor** with its evidence (`.cite`/`.assess`). Close with 2–3 concrete
  "why now" hooks from Phase 1's findings, not generic value-prop language.
- **Executive Summary prose** (management-consulting communication style): lead with
  the answer/recommendation in the first sentence, then supporting evidence, then the
  roadmap and biggest risk — not a chronological recap. A reader who only reads this
  section should already know what TechNext recommends and why.
- **Proposed Solutions** (`solution-odoo-erp`/`solution-ai`/`solution-social-media`):
  the pitch itself, placed right after Executive Summary, before Due Diligence — what
  TechNext would actually do for this client in that service line, why it fits Phase
  1's findings, a rough scope/effort indication (detailed pricing stays in
  `tool-quotation`, detailed architecture stays in Group A/B's technical sections —
  this is the pitch, not the spec). **Whitespace framing** (adapted from
  `sales:expansion-whitespace`): frame each as what the client already has vs. could
  have — e.g. "has a Facebook page, no Instagram or content cadence" → the Social
  Media whitespace; "spreadsheet-based inventory, no CRM" → the Odoo whitespace. Every
  one of the three gets real content every time — TechNext's decision to always pitch
  all three was made deliberately, this skill doesn't second-guess it per client.

## Phase 3 — Assembly

Take a fresh copy of `assets/proposal-template.html`, replace every placeholder
section body with the corresponding agent's output in the fixed order from
`assets/menu-structure.md`, fill in the client name/title, and remove every
`placeholder-note` element and the template-instructions comment. The result must be
one `.html` file with no other files alongside it.

## Phase 4 — Mandatory second comprehensive pass

`prompt.txt`'s own instruction is explicit: *"after completion, do another round, make
it super comprehensive."* Treat this as a required step, not optional polish.

**Step 4a — run the mechanical validator first, every time:**
```
python scripts/validate-proposal.py <client-slug>-proposal.html <client-slug>-findings.json
```
This checks exactly the objectively-countable rules — no leftover `placeholder-note`,
no internal-anchor citations, every citation has a matching Appendix row and vice
versa, every required section from `menu-structure.md` is present, the three
`.assess`-required sections actually have one, and `findings.json` matches the body's
citations. **Do not skip this because the file "looks" done** — the whole point is
that these are exactly the mistakes a careful-looking pass still makes (a prior real
run of this skill shipped with 27 orphaned citations and zero `.assess` labels despite
looking complete). Fix every failure it reports before moving on. It does **not**
replace the judgment-based checks below — a clean run of the script is necessary, not
sufficient.

**Step 4b — judgment-based review pass** over the assembled file (a `fork` works well
here since it needs this conversation's full context of what was researched):

- Every one of the ~45 sections has real, specific content — grep the file for
  `placeholder-note` or generic filler phrases; there should be none left.
- Every visible string has both a `t-vi` and a `t-en` span filled in — spot-check
  several sections, not just the first few.
- Any section that reads thin (a couple of generic sentences instead of grounded
  detail) gets re-sent to its Phase 1 group agent with a "go deeper, more specific to
  this client" instruction — don't pad thin sections by hand with filler.
- Cross-check internal consistency: the Odoo module plan should match the pain points
  found in Operations; the pricing/quotation should match the module plan's scope.
- **Citation content check** (the script already confirmed the *links* aren't
  orphaned — this checks whether they're actually right): spot-check a sample of
  cited pages and confirm each one really supports the claim it's attached to, don't
  just trust that a URL resolves. Any sentence that states a specific fact about the
  client (a number, a date, a quote, a review, a named person) with neither a `.cite`
  link nor an `.assess` tag is a gap — go back to Phase 1 and either find the source
  or mark it as an assessment, don't leave it looking like an unverified fact.

**Devil's-advocate review (adapted from issue-task-planning practice).** Before calling
the proposal done, argue against your own Odoo Architecture, Implementation Roadmap,
and RACI sections specifically — the parts a real client's IT lead or ops manager would
push back on hardest: Is any module choice unjustified by the actual pain points found?
Does the roadmap assume dependencies that were never confirmed (e.g. data export access
from a legacy system nobody verified exists)? Is any RACI row's "Accountable" actually
plausible for that client's org size? Fix what a skeptical reader would flag, rather
than presenting the first draft as final.

## Delivery

Save as `<client-slug>-proposal.html` plus its companion `<client-slug>-findings.json`
(or whatever filenames the user requests) and hand both to the user directly, along
with the 4 PWA companion files (`manifest.webmanifest`, `sw.js`, `icon-192.png`,
`icon-512.png`) copied unchanged from `assets/` — mention that the Install button only
works if all four are deployed alongside the HTML at a real static path (see the
Reference files note above), not when the HTML is opened alone via `file://`. Note in
your summary which research areas came back thin or unverifiable (e.g. no public data
on staff count) rather than presenting guesses as fact, and which research depth
(Quick/Standard) was actually used.

## Judgment calls

- **Client has very little public presence** (small/local business) — say so plainly
  in the relevant sections rather than inventing specifics; keep frameworks (SWOT etc.)
  grounded in what's actually knowable, note assumptions explicitly.
- **User wants fewer sections for a quick draft** — you can trim scope if they
  explicitly ask for a shorter version, but the default or unspecified case always
  produces the full sidebar from `assets/menu-structure.md`.
- **Odoo version other than 19 mentioned** — ask; the fixed instruction set here
  assumes Odoo 19 per the original prompt, but a client conversation may specify
  differently.
