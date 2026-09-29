# Section shell — the markup contract for Phase 1 writers

**Read this instead of the full `proposal-template.html`.** That file is ~250KB
(~65-70k tokens with Chart.js embedded) — every Phase 1 subagent reading the whole
thing to write a handful of `<section>` fragments was pure waste: the checkpoint
files those agents actually produce are bare `<section>` fragments, never the rest of
the shell (nav JS, theme CSS, Chart.js runtime). This file has just the markup
contract you need to write a valid section — everything else about the page (colors,
nav, toggles) is the orchestrator/assembler's problem, not yours.

## What you return

One or more `<section id="...">...</section>` fragments, using **only** the ids
listed in your own agent definition and in `assets/menu-structure.md`. Do not touch
the sidebar, `<head>`, or any other section's id.

## Basic section skeleton

```html
<section id="your-section-slug">
  <div class="wrap">
    <h2><span class="t-vi">Tiêu đề tiếng Việt</span><span class="t-en">English Title</span></h2>
    <p><span class="t-vi">Nội dung...</span><span class="t-en">Content...</span></p>
  </div>
</section>
```
Every visible string needs both a `t-vi` and a `t-en` sibling span — the page's
language toggle just shows/hides these, nothing else. Never leave one language empty.

**Keep the opening tag plain:** write exactly `<section id="slug">`. The template's own
`<section>` tag carries `data-nav`/`data-star`; `assembler` keeps that tag and swaps in
only your section's inner content, so extra attributes on yours are dropped.
**Citation labels are plain numbers** (`[1]`, `[2]`… in first-use order within your own
fragments) - never `[B1]`/`[D1]`-style group prefixes; `assembler` renumbers them globally.

## Citations — `.cite-wrap`/`.cite-tip` hover card

Every specific factual claim (a number, date, quote, named person) needs one of
these, never a bare link:
```html
<span class="cite-wrap">
  <a class="cite" href="https://real-source-url">[1]</a>
  <span class="cite-tip">
    <span class="cite-tip-excerpt">A verbatim quote (10+ characters) copied from
    that source page - never a paraphrase.</span>
  </span>
</span>
```
`href` must be a real external URL, never `#anchor`. Append the same URL + excerpt to
your `<client-slug>-findings-group<X>.json` (see "Findings file" below).

## `.assess` — TechNext's own estimate, not a cited fact

```html
<span class="assess">TechNext estimate — reasoning shown here, not sourced from a
citable page.</span>
```

## Table — `.tbl-wrap`/`.tbl`

```html
<div class="tbl-wrap">
  <table class="tbl">
    <thead><tr><th>Column A</th><th>Column B</th></tr></thead>
    <tbody>
      <tr><td>...</td><td>...</td></tr>
    </tbody>
  </table>
</div>
```

## Severity/status badge — `.pill`

```html
<span class="pill" style="background:var(--red-soft);color:var(--red)">High</span>
```
Use the palette variables already defined by the template (`--red`/`--red-soft`,
`--amber`/`--amber-soft`, `--green`/`--teal-soft`, etc.) — don't invent new colors.

## Callout box — `.callout`

```html
<div class="callout"><span class="t-vi">...</span><span class="t-en">...</span></div>
```

## Two-column pro/con grid — `.grid.g2` + `.q.s`/`.q.w`

```html
<div class="grid g2">
  <div class="q s"><span class="t-vi">👍 Điểm khách hàng thích</span><span class="t-en">👍 What customers love</span><ul>...</ul></div>
  <div class="q w"><span class="t-vi">👎 Điểm cần cải thiện</span><span class="t-en">👎 Friction points</span><ul>...</ul></div>
</div>
```
`.grid.g3` is the same but 3 columns — used for card grids (personas, role cards).

## Tabs — `.tabs`/`.tabpane` (one tab per competitor, etc.)

```html
<div class="tabs">
  <button class="tab active" data-tab="comp1">Competitor 1</button>
  <button class="tab" data-tab="comp2">Competitor 2</button>
</div>
<div class="tabpane" id="comp1">...</div>
<div class="tabpane" id="comp2" hidden>...</div>
```

## Static diagram — `.diagram-block` (never Mermaid)

```html
<div class="diagram-block">
  <div class="tl"><!-- a timeline/swimlane row per step/role --></div>
</div>
```
Or a `.grid.g3` of `.card`s for a simple org-chart/role-card layout. Mermaid is
banned — `validate-proposal.py` fails the build if it finds `class="mermaid"`
anywhere.

## Charts — canvas + `regChart(() => mkChart(...))`

```html
<div class="chart-box" style="height:300px"><canvas id="cYourChartId"></canvas></div>
<script>
regChart(() => mkChart('cYourChartId', {
  type: 'bar', // or doughnut/radar/line/bubble — see assets/charts-and-diagrams.md
  data: { labels: [...], datasets: [{ data: [...] }] },
  options: { /* keep minimal, theme colors are applied globally */ }
}));
</script>
```
**Every canvas is the direct child of a `<div class="chart-box">` with a fixed height**
(260–400px) — never a bare `<canvas>` inside a `.card`: with no fixed-height box the chart
grows without limit. **Colours only from `PAL[i]`** (add an alpha suffix as `PAL[0]+'33'`),
never hex/`rgba()` literals — hard-coded colours ignore the palette and theme.
`validate-proposal.py` check 14 fails the build on either.

**Always use `regChart(() => mkChart(...))`, never a bare `new Chart(...)`** — charts
built without `regChart` don't re-render on theme toggle. Which exact canvas id/chart
type you owe is listed in `assets/charts-and-diagrams.md` and your own agent
definition — build exactly those, no more, no fewer.

## Findings file — one per group, not a shared file

Write your own `<client-slug>-findings-group<X>.json` (`X` = A/B/C/D) — **do not**
write to a shared `<client-slug>-findings.json` directly; 4 agents appending to the
same file in parallel is a real race condition (confirmed: this silently drops
citations when two groups finish close together). `source-auditor` merges the 4
group files into the final `<client-slug>-findings.json` during its own pass, and
re-grades every entry — this requires the same fields `research-rules.md` always
specified, not a smaller ad-hoc shape. Each entry:
```json
{ "claim": "the specific fact/number/quote stated", "section": "your-section-slug", "source_url": "https://...", "grade": "Confirmed|A|B|C|D", "excerpt": "the real quote/close paraphrase from the source" }
```
`source_url` is omitted/null for a `Confirmed` entry (cite the meeting/transcript
instead). `excerpt` must match what's actually inside that citation's
`.cite-tip-excerpt` span in your HTML — `source-auditor`'s `bind_check.py` checks that
excerpt against the real source page, so it has to be the same text, not a
paraphrase-of-the-paraphrase.
