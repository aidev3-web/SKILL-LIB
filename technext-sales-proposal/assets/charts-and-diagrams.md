# Charts & diagrams — required, not optional

Read this before Phase 1 (research subagents) or Phase 2 (front-matter) build any
chart/diagram.

The original hand-built reference proposal this skill is modeled on is not just tables and
prose — it has **21 Chart.js canvas charts** and **9 process/flow diagrams** (rebuilt as
static HTML, not Mermaid — see below), styled
consistently (theme-aware grid/legend colors, a shared color palette, re-rendered on
light/dark toggle). A proposal with zero, or with charts that look like bare
default-styled Chart.js output, is missing a real part of the deliverable — an earlier
real run of this skill shipped with none at all, and a later one shipped a handful that
didn't match the reference's look.

**Use the real helper functions, don't hand-roll chart configs.**
`assets/proposal-template.html` now ports these **verbatim from that original reference build** — every chart
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
- **Chart labels/dataset labels are always plain strings, never HTML, written as
  `"Tiếng Việt||English"`.** Chart.js draws labels as canvas text, so HTML spans would
  print literally. The template's `trChartCfg()` splits every label, dataset label,
  axis title and chart title on `||` and shows only the active language; toggling VI/EN
  re-renders every chart. Examples: `'Trực tiếp||Direct'`, `'T1||Jan'`,
  `'Hôm nay (ước tính)||Today (est.)'`. A term that is the same in both languages needs
  no `||` (`'Facebook'`, `'KONE'`). Never use the old `'Việt/English'` form.
- **Colours come from the active palette.** The first `PAL` colours (`PAL[0]`,
  `PAL[1]`, `PAL[2]`, `PAL[8]`) follow the palette the viewer picks with the 🎨 button,
  so reach for `PAL[...]` or `var(--teal)`-derived colours rather than hard-coding hex.
- **Tooltips on any chart plotting percentages must say so.** Chart.js's default
  tooltip shows a bare number (`"25"`) with no unit — a real reader hovering has no
  idea if that's a percent, a count, or a score. Any chart whose `data` values are
  percentages (most doughnut/pie charts here — `cRevMix`, `cChannel`, `cOrigin`, etc.)
  needs a tooltip callback that appends the unit, e.g.:
  ```js
  plugins: { tooltip: { callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.parsed}%` } } }
  ```
  merge this into the chart's `plugins` alongside `legend`, same pattern as `baseOpts`.

**Full chart manifest — all 18, not a representative sample.** The original reference
build has 21 named charts; this skill drops the 2 tied to the removed PESTLE/Porter's Five Forces
sections and 1 (`cAuto`) tied to the section removals below, leaving 18 required.
Content adapted per client's
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
| `cOwner` | bubble | Group C (`advisory`) | The major recommended decisions — impact vs. effort |
| `cRisk` | bubble | Phase 2 (`recommendations`) | Risk highlights — probability × impact, bubble = urgency |
| `cKpi` | bar | Phase 2 (`recommendations`) | Recommended baseline vs. 12-month target per KPI |
| `cRoi` | line | Phase 2 (`recommendations`) | Recommended cumulative cost vs. cumulative benefit, break-even visible |

That's **12 charts for Group A, 1 for Group C (`cOwner`), 2 for Phase 2's `exec-summary`,
3 for Phase 2's `recommendations` section** = 18 total. Group A owning most of them is
expected — it's chart-config generation from research Group A already did, not new
research, so it doesn't need extra research time.

**Full diagram manifest — 4, no Mermaid.** Every diagram slot below is built as
**static HTML using the template's own component classes**, never
`<div class="mermaid">`/Mermaid syntax.

| # | Static shape | Owner | Shows |
|---|---|---|---|
| 1 | `.tl` timeline (vertical) | Group A (`staff-org`) | Organisation chart / reporting lines — render as a nested `.tl` (manager → reports) or a `.grid.g3` of role `.card`s with a "reports to" line, not a literal org-chart image |
| 2 | numbered `.tl` steps | Group B (`department-workflows`) | Acquisition funnel / manual-handling load, as-is — one `.tl` step per stage with a volume/drop-off note |
| 3 | `.tl` swimlane-by-role | Group B (`bpmn-blueprint-uml`) | BPMN-style process — one `.tl` per role/lane (labelled), steps in sequence, the client's core operational process as-is → to-be |
| 4 | numbered `.tl` sequence | Group B (`bpmn-blueprint-uml`) | UML-style sequence — a key transaction flow (e.g. order → fulfillment → invoice) as ordered steps, actor named per step |

That's **1 for Group A, 3 for Group B** = 4 total. Group C and Group D (Tools &
Documents) don't own any required diagram in this manifest. Give each of these 4 a
`<div class="diagram-block" data-diagram="N">` wrapper (any real content inside is
fine — `.tl`/`.tbl`/`.quad`/`.acc` — the wrapper is just what Phase 4's validator
counts) so the mechanical check can confirm all 4 are present without depending on any
one specific inner markup shape.

### Drawing diagrams with the bundled `diagram-design` skill

`diagram-design` ships with this skill (`skills/diagram-design/`, MIT) and is installed
alongside it. Use it to draw each diagram-block instead of hand-built `.tl` markup
whenever it produces a clearer, better-looking result — pick the type that fits the
content, e.g. **org chart / tree** (#1), **funnel / pyramid** (#2), **swimlane** (#3),
**sequence** (#4). Hand-built `.tl` remains a valid fallback.

Rules when embedding its output:
- Paste only the **inline `<svg>…</svg>`** inside the `<div class="diagram-block"
  data-diagram="N">` wrapper — never its full example page, never a `<link>` to Google
  Fonts or any CDN (validator check #13 fails the build on external assets).
- Skin it with this client's palette (map diagram-design's `paper/ink/accent/muted`
  roles to the proposal's CSS variables) so it matches the page in both themes.
- Every visible label stays bilingual: wrap SVG text in `<tspan class="t-vi">` /
  `<tspan class="t-en">`.
- No Mermaid, ever — diagram-design draws static SVG, which is what's required.

**Charts: model's choice, within the validator contract.** The 18 required canvases
above stay Chart.js (the validator checks their ids + `regChart`). Beyond those, when a
visual reads better as a diagram-design chart type (Sankey, waterfall, Gantt, quadrant,
Wardley, radar…), add it as an extra `diagram-block` — choose whichever renders the
data most clearly and fits the section.

Each `<canvas id="...">` above must appear in the HTML with that exact id and exactly
one matching `regChart(() => mkChart('...', {...}))` call in a `<script>` block placed
right after that section's HTML (or batched at the end of `<main>` — either is fine as
long as every canvas gets registered). Phase 4's mechanical validator (check #9) checks
for all 18 canvases (by exact id) and all 4 `diagram-block` wrappers by count — missing
several is a fail, not a warning.
