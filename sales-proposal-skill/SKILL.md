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
- `scripts/validate-proposal.py` — the Phase 5 mechanical validator (run via `python`).
  Checks only what's objectively countable: no leftover placeholders, no
  internal-anchor citations, citation/Appendix consistency, required-section
  coverage, `.assess` presence on the three delivery sections, and `findings.json`
  consistency. It does not check factual accuracy or content depth — those stay
  judgment calls. See Phase 5 for when to run it.

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

## Phase 1 — Parallel research fan-out

**Cost note — read before spawning anything.** An earlier version of this skill
suggested 6 research agents here plus 9 section-writing agents in Phase 3 — roughly 16
agent calls per proposal, which made a single run take 45–60 minutes and burn a large
amount of tokens for output that wasn't proportionally better. Merged, 3 broader
research agents here consistently cover the same ground with far less overhead. Do not
re-expand this back toward one-agent-per-topic — the merge is deliberate, not a
placeholder to split further "for thoroughness."

Launch 3 `Agent` calls in parallel (single message, multiple tool uses). Use
`general-purpose` for all three — each prompt below is fully self-contained; use `fork`
only if a track genuinely needs this conversation's own context (rare here):

1. **Company & Leadership** — history, business model, products/services, locations,
   scale, founders/leadership, public org signals, headcount estimates, hiring
   patterns. (Merges what used to be two separate tracks — company profile and
   leadership research overlap heavily in practice; splitting them just meant both
   agents re-reading the same "About" and LinkedIn pages.)
2. **Digital, Market & Competitors** — website quality, social media activity (posting
   frequency, follower counts, engagement, platforms used), review sites, customer
   sentiment, industry sizing/trends, direct competitors, customer personas typical of
   this industry. Feeds Digital & Web Presence, Market & Industry, Porter's Five
   Forces, Competitor Deep-Dive, and — capture social-specific detail explicitly
   (which platforms are active vs. absent, content mix, posting cadence, obvious gaps)
   — the Social Media Marketing solution pitch.
3. **Operations & Strategy consultant** — one agent doing both passes that used to be
   separate: the `business-analyst` discovery checklist (stakeholders, process
   mapping, pain points, KPIs) to infer likely department workflows and pain points,
   **and** the management-consultant reasoning (growth strategy, pricing strategy,
   regional expansion, risk factors) for this client. Feeds Operations,
   Pain→Solution Matrix, Growth & Strategy, and Risk Register & RACI.

Each agent should return **structured findings**, not finished HTML — bullet facts,
grouped by which sidebar section(s) they feed. **Every fact must carry the exact URL
it came from** (the specific page, not just the domain) — instruct each research agent
explicitly to attach a source URL to every claim it reports, and to mark clearly which
findings it could *not* verify with a real source rather than smoothing over the gap.
A finding with no URL and no "unverified" flag is not usable in Phase 3 — treat it as
if it weren't reported.

**Source independence (adapted from OSINT investigation practice).** A fact that's been
copy-pasted across ten content-farm/aggregator sites that all trace back to the same
original bio or press release is **one source, not ten** — this matters most for
Founders & Leadership, Staff & Org, and Reviews & Reputation, where mirrored content is
common. Tell each research agent to trace a claim back toward its original source
(company site, primary filing, the actual review platform) rather than counting
duplicates as independent confirmation, and to note in its findings when a claim only
has one real underlying source even if it "appears" in several places.

**Confidence grading.** Alongside the URL, each finding gets a rough confidence grade:
- **A** — primary/official source (company site, filing, direct quote).
- **B** — reputable independent secondary source (established press, industry report).
- **C** — single unverified or user-generated source (one review, one social post).
- **D** — unverifiable / TechNext inference — this is what becomes an `.assess` tag,
  never a `.cite` link, in the delivered HTML (see Phase 3).

**Structured findings file.** In addition to the HTML deliverable, also write a
`<client-slug>-findings.json` alongside it: an array of
`{ "claim": "...", "section": "<sidebar slug>", "source_url": "...", "grade": "A|B|C|D" }`
objects, one per citation actually used. This is the "next step for the AI to connect to
MCP" that `prompt.txt` calls out — a machine-readable fact base is what a later
MCP-connected session would load into Odoo as CRM/company records, instead of having to
re-parse the HTML.

## Phase 2 — Build the strategic frameworks and the three service-line plans yourself

These are synthesis of Phase 1's findings, not new research — do these directly rather
than spinning up more agents:

- **PESTLE / SWOT-TOWS / Porter's Five Forces** — derived from the market/competitor
  findings; internally consistent (a SWOT weakness should trace to something the
  due-diligence research actually found, not be invented to fill the framework).
- **TAM/SAM/SOM sizing** (adapted from market-research practice) inside Market &
  Industry — Total Addressable Market (the whole relevant market), Serviceable
  Available Market (the slice this client could realistically reach), Serviceable
  Obtainable Market (what they could realistically capture) — each number sourced
  (`.cite`) where a real market-sizing figure exists, or explicitly marked as a
  TechNext estimate (`.assess`) with the reasoning shown, never presented as precise
  when it's actually a rough order-of-magnitude guess.
- **Competitor comparison table** (adapted from competitive-intel practice) inside
  Competitor Deep-Dive / Top-3 Competitor Deep-Dive — one `.tbl` row per competitor,
  columns for positioning, pricing tier, strengths/weaknesses, each cell's factual
  claims individually cited — not a wall of prose per competitor.
- **Messaging Comparison Matrix + Content Gap Analysis** (adapted from
  `marketing:competitive-brief`), added inside `top3-competitor-deep-dive` alongside
  the comparison table above: a second `.tbl` with one row per messaging theme
  (e.g. "price", "speed of service", "sustainability") and one column per competitor
  plus TechNext's client, showing who claims what — this is what directly answers "why
  choose this client over competitor X" instead of leaving the reader to infer it from
  separate paragraphs. Follow it with a short Content Gap Analysis: topics/formats
  competitors cover in their own marketing that the client doesn't (found from Phase
  1's digital/social research) — this feeds straight into the Social Media Marketing
  solution pitch as a concrete opportunity, not a generic "post more" suggestion.
- **Whitespace framing** (adapted from `sales:expansion-whitespace`) inside
  `solution-odoo-erp`/`solution-ai`/`solution-social-media`: frame each pitch as what
  the client already has vs. what they could have — e.g. "has a Facebook page,
  doesn't have Instagram or a content cadence" → the Social Media whitespace; "has
  spreadsheet-based inventory, no CRM" → the Odoo whitespace. This is what makes
  pitching all three services at once read as one coherent story instead of three
  separate unrelated pitches stapled together.
- **Odoo 19 architecture, module plan, and demo-data plan** — the concrete next step
  the prompt calls out ("next step is for the AI to connect to MCP and do... make sure
  Odoo ERP is filled extensively with demo data"). Name the specific Odoo 19 modules
  this client needs (based on their business model from Phase 1), what demo data
  should populate each module for a convincing demo, and the data-migration plan from
  their likely current tools. This section is what an MCP-connected follow-up session
  would actually execute against a live Odoo instance — be concrete, not generic.
- **AI Solutions plan** — 2–4 concrete AI/automation use cases specific to this
  client's actual operations (found in Phase 1, not generic "AI can help with
  everything"), each tied to a real pain point or process gap, with a rough sense of
  what data/system it would need to plug into. This feeds both `solution-ai` and
  `ai-automation-catalog`.
- **Social Media Marketing plan** — grounded in the digital/social research from
  Phase 1's track 3: which platforms this client is missing or under-using, a content
  strategy sketch (pillars, posting cadence, tone) that fits their industry and
  current audience size, and how it complements (not duplicates) the AI and Odoo
  plans — e.g. Odoo CRM capturing leads that social content generates. Feeds
  `solution-social-media` and `social-media-architecture`.

## Phase 3 — Section-writing fan-out

Launch a second batch of **5** parallel `Agent` calls — not one per sidebar group.
Nine section-writing agents (one per group) was the old design; merging adjacent
groups into 5 broader agents covers the same ~45 sections with far less overhead and
more consistent cross-references (an agent writing both Due Diligence and Strategic
Analysis can cite its own due-diligence facts directly instead of guessing what a
separate agent found). The 5 groupings:

1. **Overview + Proposed Solutions** — `overview`, `why-ai`, `exec-summary`,
   `solution-odoo-erp`, `solution-ai`, `solution-social-media`. This is the
   front-facing pitch — it runs in the same parallel batch as the other four agents
   (no need to wait for their output), just make sure it also receives the Phase 2
   service-line plans directly, since that's what it's pitching.
2. **Due Diligence + Strategic Analysis** — `due-diligence`, `company-profile`,
   `product-catalog`, `founders-leadership`, `staff-org`, `digital-web`,
   `reviews-reputation`, `strategic-analysis`, `pestle`, `swot-tows`,
   `porter-5-forces`, `competitor-deep-dive`, `market-industry`,
   `customer-personas`. Paired because Strategic Analysis is directly derived from
   Due Diligence facts — one agent keeps that traceability tight.
3. **Operations + Technology** — `operations`, `stakeholder-perspectives`,
   `department-workflows`, `pain-solution-matrix`, `bpmn-blueprint-uml`,
   `ai-automation-catalog`, `ai-in-action`, `odoo-architecture`, `data-migration`,
   `social-media-architecture`. Paired because the Technology plan is the direct
   answer to the pains found in Operations.
4. **Delivery + Competitive Intel + Growth & Strategy** — `implementation-roadmap`,
   `change-management`, `hypercare-support`, `risk-register-raci`, `kpis-benefits`,
   `competitive-intel`, `top3-competitor-deep-dive`, `pricing-strategy`,
   `regional-expansion`, `modern-alternative-services`, `advisory`,
   `appendix-sources`.
5. **Tools & Documents** — all `tool-*` sections. Kept separate because these are a
   different genre entirely (practical artifacts — calculators, playbooks, BRD,
   quotation) rather than research-derived narrative, so mixing it into another
   agent's prompt would dilute both.

Give each agent:
- The relevant Phase 1/2 findings for its group.
- The exact section slugs/headings it owns, from `assets/menu-structure.md`.
- Instructions to write bilingual VI/EN content: every visible string as a
  `<span class="t-vi">...</span><span class="t-en">...</span>` pair (see the toggle
  pattern already wired into `proposal-template.html` — `t-vi`/`t-en` siblings shown/
  hidden by `body[data-lang]`, do not invent a different mechanism).
- The existing CSS classes to reuse for structure (`.card`, `.grid.g2/g3/g4`, `.kpi`,
  `.pill.p-*`, `.tbl`, `.quad`, `.tl`, `.acc`, `.tabs`/`.tabpane`, `.callout`) —
  sections should look consistent without a later restyle pass.

**Citations — required, not optional.** Every sourced claim gets an inline citation
link immediately after it, using the template's `.cite` class:
```html
<span class="t-vi">Công ty được thành lập năm 2009</span><span class="t-en">The company was founded in 2009</span><a class="cite" href="https://example.com/about" target="_blank" rel="noopener">[1]</a>
```
- Number citations sequentially as they first appear (`[1]`, `[2]`, ...) across the
  whole document — reuse the same number if the same source is cited again elsewhere.
- **The `href` is always the real external source URL directly, never an internal
  anchor jump like `href="#src-1"` pointing at the Appendix row.** A reader clicking a
  citation should land on the actual evidence page in one click, not on a table row
  that then makes them click again. This has been gotten wrong before — a fresh run of
  this skill built every inline citation as `href="#src-slug"` pointing into the
  Appendix table instead of the source itself; treat that as a defect to catch in the
  Phase 5 citation audit below, not an acceptable alternative pattern.
- Every citation number must have a matching row in the `appendix-sources` section's
  table (section slug it's used in + the real URL) — a `[n]` with no row in Appendix,
  or a row with no `[n]` anywhere in the body, means Phase 5 isn't done yet.
- A claim that is TechNext's own inference, not sourced, gets `<span class="assess">
  <span class="t-vi">Đánh giá của Technext</span><span class="t-en">Technext assessment</span></span>`
  next to it instead of a `.cite` link — never attach a citation link to something
  nobody actually looked up.

**Customer Personas** (adapted from persona-building practice): each persona is a
structured card, not a paragraph — name/role archetype, goals, pains/frustrations,
preferred channels, and how Odoo/TechNext specifically addresses their pains. Use
`.grid.g2`/`.g3` of `.card` elements, one per persona; ground each in patterns actually
observed in Phase 1's reviews/social/market findings, cited where a specific pattern
traces to a real review or source, `.assess`-tagged where it's a reasonable inference
for the industry.

**Stakeholder Perspectives** (adapted from `sales:stakeholder-map`): a `.tbl` with
columns Person/Role (or inferred title if no name is public) / Likely stance toward
this project / Influence level / Evidence — one row per stakeholder found or
reasonably inferred from Phase 1 (founders/leadership, staff/org, reviews). Then a
**single-threaded warning**: if research surfaced only one named contact or decision-
maker for this client, say so explicitly in a `.callout.warn` — a deal that only ever
reaches one person at the client is a known, common failure mode, and the proposal
should name which other roles (ops manager, IT lead, finance) TechNext should try to
reach and why, not silently leave the gap unmentioned.

**Executive Summary ICP-fit table** (adapted from `sales:account-research`): inside
`exec-summary`, before the prose recommendation, add a small `.tbl` scoring this
client's fit — rows for industry match, company size, likely buyer persona reached,
and timing signal (e.g. a recent expansion, a hiring wave, a visible pain point found
in Phase 1) — each cell tagged **Strong / Moderate / Poor** with the evidence it's
based on (`.cite` or `.assess`). Close the table with 2–3 concrete "why now" hooks —
specific findings from Phase 1 that make this client worth pursuing right now, not
generic value-prop language that could apply to any prospect.

**Pain → Solution Matrix** (adapted from business-analyst practice): prioritize with
MoSCoW inside the `.tbl` — a `Must/Should/Could/Won't`-style `.pill` per row — so the
client can see at a glance which pains Odoo addresses in phase one vs. later.

**Digital & Web Presence as a real audit, not a description** (adapted from
`marketing:brand-review` + `marketing:seo-audit`): don't just describe the client's
website/social presence — audit it. For each issue found (weak meta tags, missing
alt text, inconsistent brand voice across pages, an unsubstantiated marketing claim,
missing legal disclaimer, thin content on a key page), give it a severity `.pill`
(**High/Medium/Low**, reusing `.p-red`/`.p-amber`/`.p-green`) and, for the highest-
severity ones, a short **before/after** example — the client's actual current text
next to a corrected version — so the reader sees a concrete fix, not just a critique.
Fold in a small SEO checklist table (title tags, meta descriptions, mobile
responsiveness, page speed signal, structured data) with a pass/fail `.pill` per item,
sourced from what Phase 1 actually observed on their site — don't invent technical
findings that weren't actually checked.

**Risk Register & RACI** (adapted from project-risk-register + RACI-matrix practice):
- Risk register: a `.tbl` with columns Risk / Probability (1–5) / Impact (1–5) / Score
  (probability × impact) / Owner / Mitigation / Contingency. Scores ≥20 get a `.p-red`
  pill and a note that they need executive attention; 12–19 `.p-amber`; below that
  `.p-green`. Aim for a realistic spread (not every risk scored 3×3) and name a
  plausible owner role (e.g. "TechNext Project Lead", "Client IT Owner") even when this
  is a proposal stage and no real names are assigned yet.
- RACI: a `.tbl` with activities as rows, roles as columns, R/A/C/I cells. **Golden
  rule: exactly one A per row, never zero, never two** — if a row seems to need two
  Accountables, that's a sign the activity should split into two rows. Cap Consulted at
  roughly 3 roles per row; more than that usually means the row is too broad.

**Implementation Roadmap, Change Management, and Hypercare & Support all get an
`.assess` disclaimer, every time — not optional.** These three sections are inherently
TechNext's own standard delivery methodology (phase names, week counts, training
cadence, SLA response thresholds) — none of it is researched fact about the specific
client, and a long, detailed-looking timeline reads as more "verified" than it actually
is if left unlabeled. Put one `.assess` span right after each section's `.lead`
paragraph (before the phase timeline/cards), stating plainly that the specific
durations/thresholds are a standard template, not yet confirmed against this client's
real team capacity, data readiness, or signed SLA — see the fixed pattern already
applied to `kpis-benefits`, `pricing-strategy`, and `risk-register-raci` for the exact
tone and placement to reuse. A benchmark run of this skill shipped all three of these
sections with zero `.assess` labeling despite being just as much "TechNext's own
projection" as the KPI targets — don't repeat that gap.

**Mutual Action Plan** (adapted from `sales:close-plan`), added at the end of
`implementation-roadmap` after the phase timeline: a short `.tbl` with columns Step /
Owner (TechNext or Client) / Target date (relative, e.g. "Week 1", not a fake
calendar date) / Done-when, covering the concrete path from "proposal delivered" to
signature — discovery call scheduled, BRD sign-off, contract review, kickoff. This is
what gives the client a next step to act on immediately instead of the roadmap
implicitly starting only after a contract already exists.

**Proposed Solutions** group specifically (`solution-odoo-erp`, `solution-ai`,
`solution-social-media`) is the pitch itself, placed early (right after Executive
Summary, before Due Diligence) — this is "what TechNext recommends," written before
the reader has seen all the supporting research, so each of the three sections must
stand on its own: what TechNext would actually do for this client in that service
line, why it fits what Phase 1 found about them specifically, and a rough indication of
scope/effort (detailed pricing stays in `tool-quotation`, detailed architecture stays
in `odoo-architecture`/`ai-automation-catalog`/`social-media-architecture` — this
section is the pitch, not the technical spec). Every one of the three gets real
content every time; never present only one or two service lines because the client
"seems like" a better fit for those — TechNext's decision to always pitch all three was
made deliberately, this skill doesn't second-guess it per client.

For the **Tools & Documents** group specifically, each item is a practical artifact
inlined as its own section (not a link to a separate file): AI Build Playbook (a short
how-to for adopting AI in this client's context), Profit Estimator (a simple
interactive calculator — plain inline `<script>`, inputs/outputs only, no external
libraries), Owner FAQ, Odoo Platform overview, Requirements/BRD draft, Quotation
(indicative pricing table — must itemize all three service lines, not just Odoo),
Accounting Overhaul notes, Demo Walkthrough script, Staff Guides outline, Discovery
Questions (the questions TechNext would ask this client in a real discovery call), and
**Social Media Content Calendar** — a concrete sample 4-week posting plan grounded in
the Phase 2 social media plan, upgraded with two techniques from the marketing
skills:
- **O-A-M-C-M framing** (adapted from `marketing:campaign-plan`): before the calendar
  grid, state the Objective (what this content is actually meant to achieve —
  awareness, leads, retention), the Audience segment it targets, the core Message,
  the Channel(s), and how it will be Measured — with **realistic production
  timelines** (a blog-style post ~3–5 days, a landing-page-style asset ~5–7 days) and
  **campaign-type-specific KPIs** (lead-gen tracks CPL/MQL conversion; awareness
  tracks reach/share-of-voice) rather than one generic "engagement" metric for
  everything.
- **Real sample posts, not just a schedule grid** (adapted from
  `marketing:draft-content`): write out 1–2 actual sample posts in full (hook line,
  body, CTA) for the highest-priority pillar/platform, not just a row in a table
  saying "post about X" — this is what lets the client see actual content quality
  instead of an abstract plan.

**Requirements (BRD)** specifically: write
requirements as
Given/When/Then acceptance criteria (adapted from business-analyst practice) tied to a
pain point from the Pain → Solution Matrix, not vague statements — e.g. "Given a
reservation is confirmed, when payment is captured, then Odoo Accounting posts the
invoice automatically" rather than "system should handle payments."

**Executive Summary** (adapted from management-consulting communication style): lead
with the answer/recommendation in the first sentence, then the supporting evidence,
then the roadmap and biggest risk — not a chronological recap of the research process.
A reader who only reads this one section should already know what TechNext recommends
and why.

## Phase 4 — Assembly

Take a fresh copy of `assets/proposal-template.html`, replace every placeholder
section body with the corresponding agent's output in the fixed order from
`assets/menu-structure.md`, fill in the client name/title, and remove every
`placeholder-note` element and the template-instructions comment. The result must be
one `.html` file with no other files alongside it.

## Phase 5 — Mandatory second comprehensive pass

`prompt.txt`'s own instruction is explicit: *"after completion, do another round, make
it super comprehensive."* Treat this as a required step, not optional polish.

**Step 5a — run the mechanical validator first, every time:**
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

**Step 5b — judgment-based review pass** over the assembled file (a `fork` works well
here since it needs this conversation's full context of what was researched):

- Every one of the ~45 sections has real, specific content — grep the file for
  `placeholder-note` or generic filler phrases; there should be none left.
- Every visible string has both a `t-vi` and a `t-en` span filled in — spot-check
  several sections, not just the first few.
- Any section that reads thin (a couple of generic sentences instead of grounded
  detail) gets re-sent to its Phase 3 agent with a "go deeper, more specific to this
  client" instruction — don't pad thin sections by hand with filler.
- Cross-check internal consistency: the Odoo module plan should match the pain points
  found in Operations; the pricing/quotation should match the module plan's scope.
- **Citation content check** (the script already confirmed the *links* aren't
  orphaned — this checks whether they're actually right): spot-check a sample of
  cited pages and confirm each one really supports the claim it's attached to, don't
  just trust that a URL resolves. Any sentence that states a specific fact about the
  client (a number, a date, a quote, a review, a named person) with neither a `.cite`
  link nor an `.assess` tag is a gap — go back to Phase 1/3 and either find the source
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
