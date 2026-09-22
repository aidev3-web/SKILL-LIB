---
name: technext-sales-proposal
description: Turn a prospective TechNext client (a company name, website, or short brief) into one comprehensive, bilingual (VI/EN toggle) self-contained HTML sales proposal website covering all three TechNext service lines — Odoo ERP implementation, AI Solutions, and Social Media Marketing — deep web/social research, a fixed sidebar covering Due Diligence, Strategic Analysis (competitors/market), Operations, Technology architecture (Odoo 19 + AI + social media) & demo-data plan, Delivery roadmap, Growth strategy, and a Tools & Documents section (AI Build Playbook, Profit Estimator, Quotation, Meeting Minutes, Discovery Questions, etc). Use when asked to research a client and build a sales proposal / due-diligence site, "làm sales proposal", "nghiên cứu khách hàng làm đề xuất", or when the request matches the client-research-to-proposal workflow (spin up agents, research a company, produce a growth plan with a big sidebar).
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
with a fixed ~42-item sidebar (client-side JS nav, no page reloads), a VI/EN language
toggle, and a light/dark theme toggle. Never split "Tools & Documents" items into
separate files — they are sections inside the same file.

**Every factual claim must be verifiable, not just plausible-sounding.** This is a
hard requirement, not a style preference: a sales/due-diligence document that states
facts about a real company with no way to check them is not trustworthy, and TechNext
is putting its name on it. Concretely:
- Any claim that came from a real source (a web page, an article, a review site, a
  social profile, an official filing) gets a citation marker right next to it in the
  delivered HTML — see "Citations" under Phase 3/4 below. **The source preview appears
  on hover/focus, not only on click** — the reader shouldn't have to leave the page or
  click through to see what's being cited; clicking still works underneath as a
  fallback (opens the real source in a new tab), it's just not the primary way to see
  it anymore.
- Any claim that is TechNext's own inference/estimate/opinion rather than something
  found in a source (an assumption about likely pain points, a projected KPI, a
  strategic recommendation) must be **labeled as such** — never presented with the
  same visual weight as a sourced fact. Use `.assess` (see template CSS) or an explicit
  "Đánh giá của Technext / Technext assessment" tag.
- Never invent a number, quote, review, or named person and attach a fake-looking
  citation to it. If something can't be found or verified, say so in the section
  instead of guessing confidently.

## Charts & diagrams — required, not optional

Trung's original reference build (`full1`, Casa Escondida Anilao) is not just tables and
prose — it has **21 Chart.js canvas charts** and **9 Mermaid diagrams**, styled
consistently (theme-aware grid/legend colors, a shared color palette, re-rendered on
light/dark toggle). A proposal with zero, or with charts that look like bare
default-styled Chart.js output, is missing a real part of the deliverable — an earlier
real run of this skill shipped with none at all, and a later one shipped a handful that
didn't match the reference's look.

**Use the real helper functions, don't hand-roll chart configs.**
`assets/proposal-template.html` now ports these **verbatim from `full1`** — every chart
must be built through them, never via a bare `new Chart(el, {...})` call, so it
automatically gets the right colors and survives the light/dark theme toggle:
```js
regChart(() => mkChart('cSentiment', {
  type: 'bar',
  data: {
    labels: ['5★','4★','3★','2★','1★'],
    datasets: [{ label: 'Share of reviews (est. %)', data: [72,18,6,2,2], backgroundColor: PAL, borderRadius: 6 }]
  },
  options: baseOpts({ scales: gridScale(), plugins: { legend: { display: false } } })
}));
```
- `regChart(fn)` registers the chart-builder so it (re-)runs on load **and** whenever
  `toggleTheme()` fires (`reRenderCharts()` destroys and rebuilds every registered
  chart) — a chart built with a bare `new Chart(...)` call outside `regChart(...)`
  will look wrong after a theme switch. Always wrap in `regChart(() => mkChart(...))`.
- `PAL` is the shared 10-color palette (`#19c6c6`, `#3b82f6`, `#6366f1`, `#ffb454`,
  `#ff6b6b`, `#36d399`, `#a78bfa`, `#f472b6`, `#37e0c8`, `#7eb0ff`) — use it for
  multi-category datasets (doughnut slices, grouped bars) instead of inventing new
  colors per chart.
- `baseOpts(extra)` sets `responsive`/`maintainAspectRatio`/theme-aware legend text
  color; merge your own `scales`/`plugins` into it via the `extra` argument rather than
  writing `options` from scratch.
- `gridScale(stacked?)` gives theme-aware x/y grid+tick colors for bar/line charts —
  use it for any chart with cartesian axes.
- `inkColors()` returns the current theme's `{grid, tick, ink}` — needed directly for
  radar (`scales.r`) configs, which `gridScale()` doesn't cover.
- **Chart labels/dataset labels are always plain strings, never HTML.** Chart.js
  renders them as plain canvas text, not HTML — `'<span class="t-vi">Facebook</span>
  <span class="t-en">Facebook</span>'` as a label literally prints the tag markup on
  the chart, it doesn't toggle with VI/EN like the rest of the page (a real run once
  did exactly this). Charts don't support the bilingual toggle — use a single combined
  string instead, e.g. `'Trực tiếp/Direct'` or just the term if it's the same in both
  languages (`'Facebook'`, `'Analytics'`).

**Full chart manifest — all 19, not a representative sample.** `full1` has 21 named
charts; this skill drops the 2 tied to the removed PESTLE/Porter's Five Forces
sections, leaving 19 required. Content adapted per client's
actual industry, counts/labels never invented from nothing — an `.assess`-labeled
illustrative estimate is fine, an empty/missing chart is not). Each row below is one
required `<canvas id="...">`, its Chart.js `type`, which group writes it, and what it
shows (adapt the specific framing to the client's actual business — e.g. `cSeason`
becomes whatever this client's real demand-cycle driver is, not literally diving
season, if the client isn't a dive resort):

| Canvas id | Type | Owner | Shows |
|---|---|---|---|
| `cRevMix` | doughnut | Phase 2 (`exec-summary`) | Illustrative revenue/effort mix across the 3 proposed service lines |
| `cScorecard` | bar | Phase 2 (`exec-summary`) | Today vs. 12-months-post-engagement, indexed to 100 |
| `cRevStream` | bar (horizontal) | Group A (`company-profile`/`due-diligence`) | Revenue or activity share by product/service line |
| `cHeadcount` | bar | Group A (`staff-org`) | Estimated headcount by department |
| `cSeasonStaff` | line (dual-axis) | Group A (`staff-org`) | Staffing level vs. demand-cycle driver over the year |
| `cChannel` | doughnut | Group A (`digital-web`) | Acquisition/inquiry channel mix |
| `cDigital` | radar | Group A (`digital-web`) | Digital maturity today vs. post-engagement target |
| `cSentiment` | bar | Group A (`reviews-reputation`) | Review star-rating distribution |
| `cThemes` | bar (stacked) | Group A (`reviews-reputation`) | Recurring praise vs. complaint themes |
| `cPosition` | bubble | Group A (`competitor-deep-dive`) | Positioning map — price vs. rating, bubble ≈ scale |
| `cGap` | radar | Group A (`competitor-deep-dive`) | Feature-gap vs. premium peers |
| `cOrigin` | doughnut | Group A (`market-industry`) | Customer origin/segment mix |
| `cSeason` | line | Group A (`market-industry`) | Demand-cycle curve for this client's actual industry |
| `cPersona` | bubble | Group A (`customer-personas`) | CLV & volume by persona, bubble = share |
| `cAuto` | bubble | Group B (`ai-automation-catalog`) | Automation portfolio — impact vs. effort (top-left = quick win) |
| `cRisk` | bubble | Group C (`risk-register-raci`) | Risk heat-map — probability × impact, bubble = urgency |
| `cKpi` | bar | Group C (`kpis-benefits`) | Baseline vs. 12-month target per KPI |
| `cRoi` | line | Group C (`kpis-benefits`) | Cumulative cost vs. cumulative benefit, break-even visible |
| `cOwner` | bubble | Group C (`advisory` or growth-strategy section) | The major recommended decisions — impact vs. effort |

That's **12 charts for Group A, 1 for Group B, 4 for Group C, 2 for Phase 2** = 19 total.
Group A owning most of them is expected — it's chart-config generation from research
Group A already did, not new research, so it doesn't need extra research time.

**Full Mermaid manifest — all 9:**

| # | Type | Owner | Shows |
|---|---|---|---|
| 1 | `flowchart` | Group A (`staff-org`) | Organisation chart / reporting lines |
| 2 | `flowchart` | Group B (`department-workflows`) | Acquisition funnel / manual-handling load, as-is |
| 3 | `flowchart` | Group B (`odoo-architecture`) | Module dependency & data flow |
| 4 | `flowchart` | Group B (`odoo-architecture` or `ai-in-action`) | Integration map (Odoo ↔ AI ↔ social/other systems) |
| 5 | `flowchart` | Group B (`bpmn-blueprint-uml`) | BPMN-style swimlane — the client's core operational process, as-is → to-be |
| 6 | `sequenceDiagram` | Group B (`bpmn-blueprint-uml`) | UML sequence — a key transaction flow (e.g. order → fulfillment → invoice) |
| 7 | `flowchart` | Group C (`implementation-roadmap`) | Migration approach / cutover flow |
| 8 | `gantt` | Group C (`implementation-roadmap`) | Roadmap timeline by phase |
| 9 | `flowchart` | Group C (`hypercare-support`) | Issue-triage flow during hypercare |

That's **1 for Group A, 5 for Group B, 3 for Group C** = 9 total. Group D (Tools &
Documents) does not own any required chart/diagram in this manifest — its content is
mostly tables/calculators, per its own instructions above.

Each `<canvas id="...">` above must appear in the HTML with that exact id and exactly
one matching `regChart(() => mkChart('...', {...}))` call in a `<script>` block placed
right after that section's HTML (or batched at the end of `<main>` — either is fine as
long as every canvas gets registered). Each Mermaid diagram is a
`<div class="mermaid">...</div>` containing raw Mermaid syntax
(`flowchart`/`gantt`/`sequenceDiagram`), never a hand-drawn image — Mermaid renders it
client-side automatically (`startOnLoad:true`, already wired in the template). Phase 4's
mechanical validator (check #9) now checks for all 21 canvases and all 9 diagrams by
count — missing several is a fail, not a warning.

## Reference files — read before writing anything

**Hard rule, checked mechanically in Phase 4: the delivered file must be
`assets/proposal-template.html` with placeholders filled in — never a new design
built from scratch.** A real run of this skill once shipped a light-theme, purple-hero,
two-separate-button-VI/EN page with none of the template's actual CSS — a completely
different visual system, not a styling variation. That is a failed run, full stop, even
if the content inside is good. Every Phase 1 group agent and the final assembly step
must work from the literal contents of `assets/proposal-template.html` — its
`:root{--bg:#0a0f1a...--teal:#19c6c6...}` tokens, its `#sidenav`/`buildNav()`
mechanism, its single sliding `.tb-btn` VI/EN switch (not two separate buttons), its
`#progress` bar. If an agent's returned section HTML uses different colors, a
different toggle pattern, or wraps itself in its own `<html>`/`<head>` instead of
being a `<section>` fragment for the existing shell, that agent's output must be
rejected and re-generated with the actual template file attached to its prompt — do
not merge it in and hope it blends.

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
  library (`.card`, `.grid.g2/g3/g4`, `.kpi`, `.pill.p-*`, `.tbl`, `.quad` for any
  2×2 layout, `.tl` timeline, `.acc` accordion, `.tabs`/`.tabpane`, `.callout`). Copy
  this file as your starting point for every run.
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
- `assets/validate-proposal.py` — the Phase 4 mechanical validator (run via `python`).
  Checks only what's objectively countable: no leftover placeholders, no
  internal-anchor citations, citation/Sources & Citation consistency, required-section
  coverage, `.assess` presence on the three delivery sections, `findings.json`
  consistency, that the real template shell was used, that a real spread of
  Chart.js canvases + Mermaid diagrams is present (not a text/table-only file), that
  citations use the hover-card markup, and that no `<CLIENT NAME>` placeholder or
  stale "Odoo 19" sidebar-brand text is left unfilled anywhere (including inside
  `buildNav()`'s JS string, not just the visible hero/`<title>`). It
  does not check factual accuracy, content depth, or whether a chart's data is any
  good — those stay judgment calls. See Phase 4 for when to run it.

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

**Research depth.** Always a full "Standard" pass across every section — there is no
"Quick" mode anymore, don't offer or default to one. If a client genuinely has very
little public footprint, say so plainly in the relevant sections (see "Judgment calls"
below) rather than switching to a thinner research pass; the depth of effort stays the
same regardless of how much was actually found.

**Engagement framing (adapted from management-consulting practice).** Before research
starts, note — in your own head, not necessarily asked aloud unless genuinely unclear —
what TechNext is trying to accomplish with this specific proposal (a cold pitch? a
follow-up after a call? a specific pain point already mentioned?). This shapes which
sections deserve the most depth; a cold pitch needs a stronger Due Diligence + Executive
Summary, a warm follow-up can lean harder into the relevant Proposed Solutions section
+ Quotation. It does **not** change which service lines appear — all three (Odoo ERP,
AI, Social Media) are always pitched, only how much depth each gets.

**Client-provided info (discovery call notes, transcript, direct answers) — ask for
this before researching, don't skip it.** Ask: *"Bạn có ghi chú/bản ghi/transcript nào
từ buổi gọi hoặc họp với khách hàng này chưa? Nếu có, dán vào đây."* If the user
pastes something, this is a **different, higher-trust source than anything found by
web/social research** — a client directly stating "we have 24 rooms, 8 ocean-view" or
naming their own operations lead is not something to re-verify by searching the web,
it's simply true (assuming the user pasted it accurately). Treat it as the first thing
to check when writing any section, before falling back to public search for the same
fact. See "Confidence grading" under Phase 1 for how this is graded and cited
differently from `.cite`/`.assess`.

**Scope & ethics boundary (adapted from OSINT practice).** Research stays limited to
information a company and its leadership have made public in a business capacity
(company sites, business filings, press, professional social profiles, public reviews).
Never pursue private/personal information about individuals unrelated to their business
role, and never use non-public collection methods (scraping behind logins, social
engineering, breach data). If a request pushes past this line, decline that part and
say why, rather than quietly complying.

## Checkpoints — run one phase at a time instead of the whole pipeline

**Ask this in Phase 0, right after confirming the client:** *"Chạy toàn bộ pipeline
luôn, hay chỉ chạy 1 phase cụ thể?"* Running the full Phase 1→4 pipeline in one go is
the default, but it's also the slowest/most expensive path — if the user only wants to
re-run Group B after a bad first pass, or just wants Phase 4's validator re-checked
after a manual edit, don't force them through everything again.

**How checkpointing works.** Every phase writes its output to its own intermediate
file(s) instead of only living in conversation context, so a *later, separate*
invocation of this skill can resume from any completed phase without re-running the
ones before it:

- `<client-slug>-checkpoint.json` — one small file tracking what's done:
  `{ "phase1_groupA": "done", "phase1_groupB": "done", "phase1_groupC": "pending", "phase1_groupD": "pending", "phase2": "pending", "phase3": "pending", "phase4": "pending" }`.
  Read this file first, if it exists, to know what's already been done before deciding
  what to run.
- **Every intermediate file must be a real, directly-openable HTML page — never a bare
  `<section>` fragment saved on its own.** A fragment can't be previewed in a browser
  to sanity-check it, which is exactly when you most want to look at it (right after a
  single group/section just ran). So `<client-slug>-p1-groupA.html` (and B/C/D) is a
  **full copy of `assets/proposal-template.html`** with that group's real sections
  filled in and every other section left as its original `placeholder-note` — openable
  and previewable on its own, dark navy/teal theme, nav, hover-citations and all,
  exactly like the final deliverable, just with most sections still empty. Plus a
  shared `<client-slug>-p1-digests.json` (each group's 3–5-point digest for Phase 2,
  kept separate since Phase 2 only needs the digests, not full HTML). A group can be
  (re-)run alone — e.g. "chạy lại Group B thôi" — by reading the other 3 groups'
  already-saved files rather than re-invoking them.
- **Phase 2** saves its own preview the same way — a full template copy with just the
  front-matter sections (`overview`, `exec-summary`, `solution-*`) filled in — to
  `<client-slug>-p2-frontmatter.html` (reads `<client-slug>-p1-digests.json` for
  content, not the full Phase 1 group files, per its own instructions below).
- **Phase 3 (Assembly)** requires all of Phase 1 (4 groups) + Phase 2 to be `"done"` in
  the checkpoint file — if any are still `"pending"`, say so and stop rather than
  assembling with gaps. Since every `-p1-group*.html`/`-p2-frontmatter.html` is itself a
  full template-shaped page (see above), Phase 3 doesn't paste them in whole — it
  **extracts only the finished `<section id="...">...</section>` blocks** from each one
  (the same extraction `assets/validate-proposal.py` already does — grab from a
  section's opening tag to the next `<section id="` or `</main>`) and drops each into a
  fresh copy of `assets/proposal-template.html` in the fixed order from
  `assets/menu-structure.md`, producing the final `<client-slug>-proposal.html`.
- **Phase 4** only needs Phase 3's `<client-slug>-proposal.html` to exist — it can be
  re-run alone any time (e.g. after a manual fix) without touching Phases 1–3.

After running whichever phase(s) were requested, update `<client-slug>-checkpoint.json`
and tell the user plainly what just ran and what's still pending — e.g. *"Đã chạy xong
Phase 1 Group A + B (2 agent). Group C, D, Phase 2-4 vẫn đang pending."* Note: this
tracks **how many `Agent` calls were made**, a rough proxy for cost — it is not an
exact token/dollar count (only Claude Code's own session-cost reporting has that).

**Section-level touch-ups — smaller than a whole group.** A group is 6–14 sidebar
sections bundled into one `Agent` call — if the user only wants one specific section
redone (e.g. "chỉ nghiên cứu lại phần Digital & Web Presence thôi" — that's one section
inside Group A, not all of Group A), don't re-run the whole group:
1. Identify which group owns that section (see the Group A/B/C/D descriptions below,
   or just match the section name against `assets/menu-structure.md`).
2. Spawn a single, narrowly-scoped `Agent` call for **just that one section** (still
   give it the real template contents + the citation/chart rules that apply, same as
   any Phase 1 agent — a smaller scope doesn't mean lower quality bar).
3. Open the group's existing `<client-slug>-p1-group<X>.html`, find that section's
   `<section id="...">...</section>` block, and replace only that block in place —
   every other section in the file stays untouched, byte for byte.
4. The group's checkpoint status stays whatever it already was (this is an in-place
   patch, not a new phase) — no new checkpoint field needed for this.
If the user doesn't know which group owns a section, they don't need to — just name
the section (as it appears in the sidebar) and resolve the mapping yourself.

## Phase 1 — Research + write fan-out (one round, not two)

*Running this phase alone, or just one group (checkpoint resume)? Only spawn the
group(s) actually requested/still `"pending"` in `<client-slug>-checkpoint.json` — a
single group (e.g. "chạy lại Group B") is a single `Agent` call, not all 4. Each group
saves its own `<client-slug>-p1-group<X>.html` — **a full copy of
`assets/proposal-template.html` with just this group's sections filled in, everything
else left as `placeholder-note`** (so it's directly openable in a browser to preview,
not a bare fragment) — and appends its digest to the shared
`<client-slug>-p1-digests.json` (create it if it doesn't exist yet), then marks its
own `phase1_group<X>: "done"`.*

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
owns (from `assets/menu-structure.md`), the citation/`.assess` rules below, and **the
literal contents of `assets/proposal-template.html` pasted into the prompt (or the
file path if the agent can read files itself) — not just a list of CSS class names.**
Naming classes like `.card`/`.kpi` without the actual file lets an agent invent its
own meanings for them (or invent an entirely different page); pasting the real file
is what forces it to produce a `<section id="...">` fragment matching the existing
dark navy/teal shell instead of a freestanding page with its own colors, header, and
toggle mechanism. Tell each agent explicitly: return only the `<section>` fragment(s)
for its owned slugs, not a full `<html>` document. Instruct every agent to also
return, alongside its finished section HTML, a short plain-text digest of its 3–5
most important findings — Phase 2 uses these digests to write the front matter without
re-reading every agent's full section HTML.

**Group A — Due Diligence + Strategic Analysis** (`due-diligence`, `company-profile`,
`product-catalog`, `founders-leadership`, `staff-org`, `current-operations`,
`current-tools-saas`, `digital-web`,
`reviews-reputation`, `strategic-analysis`,
`competitor-deep-dive`, `market-industry`, `customer-personas`): also owns **12 of the
19 required charts + 1 Mermaid diagram** — see the full manifest under "Charts &
diagrams" above (`cRevStream`, `cHeadcount`, `cSeasonStaff`, `cChannel`, `cDigital`,
`cSentiment`, `cThemes`, `cPosition`, `cGap`, `cOrigin`,
`cSeason`, `cPersona`, plus the org-chart flowchart) — build all of them as part of
this same call, via `regChart(() => mkChart(...))`, not a separate pass. Research the
company itself, its founders/leadership, staff/org signals, digital & social presence,
reviews, market/industry, and direct competitors — then write all these sections
itself, in the same call. Paired because Strategic
Analysis is directly derived from Due Diligence facts — one agent keeps that
traceability tight instead of a second agent guessing what the first one found.
Capture social-specific detail explicitly in `digital-web` (which platforms are active
vs. absent, content mix, posting cadence, obvious gaps) — Group C's Social Media
pitch depends on this. Also build:
- **Current Operations** (`current-operations`) and **Current Tools & SaaS**
  (`current-tools-saas`): document how the client actually runs today — before any
  TechNext change — and every tool/spreadsheet/SaaS currently in use, each with what
  it's used for and its observed limitation (`.cite` where found publicly, `.assess`
  where inferred). This is the "as-is" baseline the Proposed Solutions pitch and the
  Odoo/AI/Social architecture plans (Group B) are pitched against — a whitespace claim
  like "spreadsheet-based inventory, no CRM" needs this section to actually say so
  first, not just assert it later in Phase 2.
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
- **Reviews & Reputation — mine it, don't just chart it** (`full1`'s reference build
  has this and it's easy to skip): beyond `cSentiment`/`cThemes`, add a two-column
  `.grid.g2` breakdown — `.q s` "👍 What customers love" and `.q w` "👎 Friction
  points" — each a bullet list of **specific, concrete items actually found** in
  reviews/social comments (not generic filler like "good service"). Close with a
  `.callout` giving an **estimated NPS/reputation-score range** (e.g. "modelled NPS of
  +40 to +60 given a 4.3★ Google profile") — this is a modelled estimate, not a
  measured metric, so tag it `.assess` and say what it's based on.

**Group B — Operations + Technology** (`operations`, `stakeholder-perspectives`,
`department-workflows`, `pain-solution-matrix`, `bpmn-blueprint-uml`,
`ai-automation-catalog`, `ai-in-action`, `odoo-architecture`, `data-migration`,
`social-media-architecture`): also owns **1 chart (`cAuto`) + 5 Mermaid diagrams** —
see the full manifest under "Charts & diagrams" above (acquisition-funnel flowchart,
module-dependency flowchart, integration-map flowchart, BPMN swimlane, UML sequence).
All 4 groups launch in the same parallel batch, so this
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
`advisory`, `sources-citation`): also owns **4 charts
(`cRisk`, `cKpi`, `cRoi`, `cOwner`) + 3 Mermaid diagrams** (cutover-flow, roadmap
`gantt`, hypercare issue-triage flowchart) — see the full manifest under "Charts &
diagrams" above. Reason about growth
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

**Group D — Tools & Documents** (all `tool-*` sections plus `meeting-minutes`): each
item is a practical artifact inlined as its own section (not a separate file): AI
Build Playbook, Profit Estimator (plain inline `<script>` calculator, no external
libraries), Owner FAQ, Odoo Platform overview, Requirements/BRD, Quotation (itemize
all three service lines), Accounting Overhaul notes, Demo Walkthrough script, Staff
Guides outline, Discovery Questions, and Meeting Minutes. This group works from
general industry-appropriate assumptions about pain points/modules rather than
waiting on Groups A/B's exact output — Phase 4's devil's-advocate review is what
catches any mismatch, so a little independence here is an acceptable trade for
staying parallel.
- **Requirements (BRD)**: Given/When/Then acceptance criteria (adapted from
  business-analyst practice) tied to a plausible pain point — e.g. "Given a
  reservation is confirmed, when payment is captured, then Odoo Accounting posts the
  invoice automatically" rather than "system should handle payments."
- **Meeting Minutes**: a realistic template for the discovery/kickoff meeting this
  proposal is based on — date, attendees (role, not necessarily a real name if
  unconfirmed), key discussion points, decisions made, and action items with an owner
  and due date per row. Mark clearly which parts are illustrative/assumed (`.assess`)
  vs. anything actually confirmed with the client.

Each agent must attach a source URL to every claim it makes (**every fact must carry
the exact page it came from**, not just the domain), and mark clearly which findings
it could *not* verify with a real source rather than smoothing over the gap. A claim
with no URL and no "unverified"/`.assess` flag is not usable — treat it as if it
weren't written.

**Citation markup — Wikipedia-style hover card, not click-to-see.** Every citation is
a `.cite-wrap` span (already styled in the template) wrapping the `.cite` link plus a
`.cite-tip` card shown on hover/focus, with the actual excerpt up top and the
source's domain + a link-out affordance in a footer row at the bottom — mirroring how
Wikipedia's own link-preview popups work (excerpt text, then where it's from, no
click needed to see either):
```html
<span class="cite-wrap" tabindex="0">
  <a class="cite" href="https://jrtech.com.my/" target="_blank" rel="noopener">[2]</a>
  <span class="cite-tip">
    <span class="cite-tip-excerpt">"24/7/365 service availability with 100% spare parts stock, 18 in-house technicians committed to a 24-hour response time."</span>
    <span class="cite-tip-foot">
      <a class="cite-tip-domain" href="https://jrtech.com.my/" target="_blank" rel="noopener">jrtech.com.my</a>
      <span class="cite-tip-icon">↗</span>
    </span>
  </span>
</span>
```
- `.cite-tip-excerpt` is a **real short quote or close paraphrase actually taken from
  that source page** supporting this exact claim (1–2 sentences) — not a restatement
  of the claim itself and not a generic description of the site. If you can't produce
  a real excerpt for a claim, that's a signal the source may not actually support it —
  re-check it rather than inventing filler text for the tooltip.
- `.cite-tip-domain` is a **real clickable `<a href="...">`** (same URL as the `.cite`
  link above it), showing just the bare domain (`jrtech.com.my`, not the full URL) —
  the reader can click it directly from inside the open card, they don't have to
  chase the tiny `[n]` marker again. The card itself is hoverable
  (`pointer-events:auto`) and stays open while the mouse is over it, specifically so
  there's time to move the pointer down and click this link — if a card closes before
  the pointer reaches it, that's the `.cite-tip`/`::before` bridge CSS being broken,
  fix that rather than reverting to click-only.
- Never emit a bare `<a class="cite" href="...">[n]</a>` with no `.cite-wrap`/
  `.cite-tip` around it, and never leave `.cite-tip-excerpt` empty — both are checked
  mechanically (see Phase 4 check #10).
- **Mobile/touch has no hover at all**, so the template's shared `<script>` (already
  in `assets/proposal-template.html`, nothing per-run to author here) adds a
  tap-to-preview fallback: first tap on `[n]` opens the card instead of navigating,
  a second tap (or tapping the domain link inside the open card) navigates to the
  source, and tapping elsewhere closes it. Don't re-implement this per client — it's
  shell behavior, not content.

**Source independence (adapted from OSINT investigation practice).** A fact
copy-pasted across ten content-farm/aggregator sites that all trace back to the same
original bio or press release is **one source, not ten** — this matters most for
Founders & Leadership, Staff & Org, and Reviews & Reputation. Trace a claim back
toward its original source rather than counting duplicates as independent
confirmation.

**Confidence grading.** Alongside the URL, each finding gets a rough confidence grade:
- **Confirmed** — stated directly by the client themselves, in meeting notes/transcript
  the user pasted at Phase 0. This is not "higher than A" on the same scale — it's a
  **different kind of source** (nobody else needs to publish it for it to be true; the
  client saying it *is* the fact). Never render it as a `.cite` link (there's no URL to
  link to) — use a distinct `.grade.confirmed` badge instead (see template CSS), with a
  short note of what it's from, e.g. "Confirmed — discovery call 18/06".
- **A** — primary/official source (company site, filing, direct quote).
- **B** — reputable independent secondary source (established press, industry report).
- **C** — single unverified or user-generated source (one review, one social post).
- **D** — unverifiable / TechNext inference — this is what becomes an `.assess` tag,
  never a `.cite` link, in the delivered HTML.

**"To confirm" gaps — a third state, not the same as `.assess`.** When the pasted
meeting notes/transcript **raise** a topic but don't actually answer it (the client's
own certifications, an unconfirmed headcount, a detail the meeting ran out of time
for), that's neither a sourced fact nor a TechNext inference — it's a known gap with a
clear next action. Flag it with a `.callout warn` right in the relevant section: *"Chưa
xác nhận được X trong buổi họp — cần hỏi lại khách trước khi [ví dụ: chốt số liệu
demo]."* Don't silently drop it, and don't disguise it as an `.assess` estimate.

**Structured findings file.** In addition to the HTML deliverable, also write a
`<client-slug>-findings.json` alongside it: an array of
`{ "claim": "...", "section": "<sidebar slug>", "source_url": "...", "grade": "Confirmed|A|B|C|D" }`
objects, one per citation actually used (`source_url` is omitted/null for `Confirmed`
entries — cite the meeting instead, e.g. `"source": "discovery call 18/06/2026"`). This
is the "next step for the AI to connect to MCP" that `prompt.txt` calls out — a
machine-readable fact base is what a later MCP-connected session would load into Odoo
as CRM/company records, instead of having to re-parse the HTML.

## Phase 2 — Write the front matter yourself (no agent needed)

*Running this phase alone (checkpoint resume)? Read `<client-slug>-p1-digests.json` —
you don't need the full Phase 1 group HTML files, just the digests. Save output to
`<client-slug>-p2-frontmatter.html` as a full template copy (like Phase 1's group
files — openable/previewable, everything but the front matter left as
`placeholder-note`) and mark `phase2: "done"` in the checkpoint file.*

`overview`, `exec-summary`, `solution-odoo-erp`, `solution-ai`, and
`solution-social-media` are written directly by you, not another agent — this is fast
(also add the revenue-mix + scorecard charts described under "Charts & diagrams" above
while you're writing `exec-summary`, via `regChart(() => mkChart(...))`, not a separate
step later)
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

*Running this phase alone (checkpoint resume)? Check `<client-slug>-checkpoint.json`
first — all 4 Phase 1 groups and Phase 2 must be `"done"`; if not, say what's still
missing and stop rather than assembling with gaps. Read all 4
`<client-slug>-p1-group*.html` files + `<client-slug>-p2-frontmatter.html` —
**extract just the finished `<section>` blocks from each** (they're full template
pages, not fragments — see "Checkpoints" above), don't paste the whole files in. Mark
`phase3: "done"` once `<client-slug>-proposal.html` is written.*

Take a fresh copy of `assets/proposal-template.html` — **the actual file, byte for
byte, as your starting point** — and replace every placeholder section body with the
corresponding agent's output in the fixed order from `assets/menu-structure.md`, fill
in the client name/title. **There are three spots, not one** — the `<title>`, the
hero's `.chip` badge (`'× &lt;CLIENT NAME&gt;'`), and the sidebar brand line inside
`buildNav()` (`'× &lt;CLIENT NAME&gt;'`, generated by JS — the easiest of the three to
miss since it's not visible as literal HTML). A prior real run fixed the hero title but
left the hero chip AND the sidebar both still reading "Technext × Odoo 19" — check all
three every time, don't assume fixing one fixes the others. Remove every
`placeholder-note` element and the
template-instructions comment. The result must be one `.html` file with no other
files alongside it. If any Phase 1 agent returned a full page instead of a
`<section>` fragment (its own `<html>`/`<head>`/different CSS), do not paste that in —
extract only its content into the existing shell's structure, rewriting it into the
template's classes if needed. **Before moving to Phase 4, visually sanity-check the
assembled file has the dark navy/teal theme, the single sliding VI/EN switch, the
`#progress` bar at the top, and a real spread of Chart.js canvases + Mermaid diagrams
across sections (not just tables)** — if any of these is missing, something upstream
produced an off-template or chart-less page and needs fixing now, not after delivery.

## Phase 4 — Mandatory second comprehensive pass

*Running this phase alone (checkpoint resume)? Only `<client-slug>-proposal.html` from
Phase 3 needs to exist — safe to re-run any time, e.g. right after a manual fix,
without touching Phases 1–3. Mark `phase4: "done"` when it passes.*

`prompt.txt`'s own instruction is explicit: *"after completion, do another round, make
it super comprehensive."* Treat this as a required step, not optional polish.

**Step 4a — run the mechanical validator first, every time:**
```
python assets/validate-proposal.py <client-slug>-proposal.html <client-slug>-findings.json
```
This checks exactly the objectively-countable rules — no leftover `placeholder-note`,
no internal-anchor citations, every citation has a matching Sources & Citation row and vice
versa, every required section from `menu-structure.md` is present, the three
`.assess`-required sections actually have one, `findings.json` matches the body's
citations, the real template shell was used (not a rebuilt design), a real spread
of Chart.js canvases + Mermaid diagrams is present, citations use the hover-card
markup, and no `<CLIENT NAME>` placeholder or stale "Odoo 19" sidebar text is left
unfilled anywhere — including inside `buildNav()`'s JS string, which a quick visual
skim of the rendered page can miss until the sidebar is actually opened. **Do not
skip this because the file "looks" done** — the whole point is
that these are exactly the mistakes a careful-looking pass still makes (a prior real
run of this skill shipped with 27 orphaned citations and zero `.assess` labels despite
looking complete). Fix every failure it reports before moving on. It does **not**
replace the judgment-based checks below — a clean run of the script is necessary, not
sufficient.

**Step 4b — judgment-based review pass** over the assembled file (a `fork` works well
here since it needs this conversation's full context of what was researched):

- Every one of the ~42 sections has real, specific content — grep the file for
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
- If Phase 0 had meeting notes/transcript pasted in: confirm every fact actually
  stated there made it in with a `.grade.confirmed` badge (not silently downgraded to
  `.assess`), and every topic the notes *raised but didn't answer* has an explicit
  `.callout warn` "to confirm" note rather than being quietly dropped.

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
on staff count) rather than presenting guesses as fact.

Once Phase 4 passes and the file is handed over, the `-p1-group*.html`,
`-p1-digests.json`, and `-p2-frontmatter.html` intermediate files are no longer
needed for a fresh run — but **don't delete them automatically**; ask the user first
in case they want to keep them around for a future incremental re-run (e.g. after a
follow-up client meeting surfaces new confirmed details).

## Judgment calls

- **Client has very little public presence** (small/local business) — say so plainly
  in the relevant sections rather than inventing specifics; keep every framework
  grounded in what's actually knowable, note assumptions explicitly.
- **User wants fewer sections for a quick draft** — you can trim scope if they
  explicitly ask for a shorter version, but the default or unspecified case always
  produces the full sidebar from `assets/menu-structure.md`.
- **Odoo version other than 19 mentioned** — ask; the fixed instruction set here
  assumes Odoo 19 per the original prompt, but a client conversation may specify
  differently.
