---
name: workflow-diagram-skill
description: Turn a description of an orchestrator/multi-agent or multi-stage pipeline (a trigger, one or more agents/skills/tools, and the deliverables they produce) into ONE self-contained, print-ready, bilingual (VI/EN toggle) HTML "black-box + node-graph" page, in the exact warm-brown/Claude-orange visual style and data-driven layout engine of TechNext's qa-qc-workflow reference site. Use when asked to "vẽ workflow", "document a pipeline/workflow diagram", "làm sơ đồ quy trình multi-agent", or to visualize how an orchestrator dispatches subagents/skills/tools into deliverables.
---

# Workflow diagram skill — pipeline description → black-box + node-graph HTML page

## What this is for

Turns a description of ANY staged, multi-agent/orchestrator pipeline — not just
TechNext's own QA/QC pipeline — into one self-contained HTML page with exactly two
sections:

1. **Overview (black-box)**: 3-column layout — Inputs (what goes in) | What runs inside
   (animated counters + one summary paragraph + agent-pill strip) | Outputs (client-ready
   deliverables).
2. **Node graph (detail)**: a left-to-right, phase-by-phase graph. Each phase is a
   column; each node in that phase is a colored card (kind: trigger / agent / skill /
   tool / deliverable); hover a node on screen (or read its callout when printed/exported
   to PDF) to see its full detail card (Purpose / Tools / Upstream / Downstream / On
   failure). SVG edges with an animated pulse connect the nodes in data-flow order.

**This entire page is driven by three JS data arrays — `PHASES`, `NODES`, `EDGES` — that
a small, fixed rendering engine turns into the graph automatically.** You never hand-lay
out node positions, draw the SVG paths, or touch the CSS/animation logic. Your job is
Interviewing the user for their real pipeline, then filling in accurate data.

## Reference file — copy this exact starting point

`assets/workflow-template.html` is the reference site (`qa-qc-workflow.vercel.app`,
TechNext's own QA/QC pipeline), with one addition on top of the original: a working
**VI/EN language toggle** (top-right button, `body[data-lang]` + `.t-vi`/`.t-en` CSS,
defaults to `vi`, persisted via `localStorage`). Copy it as your starting point for
every run. It contains:

- Full CSS design tokens (`--bg`, `--ink`, `--accent`, `--claude` orange, `--trigger`,
  `--agent`, `--skill`, `--tool`, `--deliverable` + their `-soft` backgrounds), fonts
  (Plus Jakarta Sans body, Playfair Display display type, JetBrains Mono for code/chips),
  and print rules (`page-break-before` per `.section`, so it exports cleanly via
  browser print-to-PDF).
- The full rendering engine (`<script>` near the bottom): reads `PHASES`/`NODES`/`EDGES`,
  computes column/row positions, draws node cards, draws animated SVG edges with a
  moving pulse dot, wires hover-to-highlight (fades every other node/edge when you hover
  one), animates the overview counters on scroll-into-view, and handles a `beforeprint`
  fallback so counters/nodes are fully rendered in the printed/exported version.
- A fixed icon set (`var ICO = {...}`) with 16 ready-made stroke icons: `claude`,
  `playwright`, `user`, `orchestrator`, `browser`, `clipboard`, `shield`, `camera`,
  `doc_sparkle`, `terminal`, `cursor`, `md`, `json`, `check_x`, `media`, `pdf`.

**What you change per workflow:** the `PHASES`/`NODES`/`EDGES` data arrays, the Section-1
overview HTML (Inputs list, counters, summary paragraph, agent-pill strip, Outputs
cards), the `<title>`, kicker text, `<h1>`, and lede paragraph.

**What you never change:** the CSS tokens/rules, the rendering engine's layout math
(`colX`/`nodeX`/`nodeY`/`COL_W`/`ROW_GAP`/etc.), the SVG edge-drawing logic, the hover/
counter/print JS, the VI/EN toggle mechanism (`setLang`/`.lang-toggle`/`t-vi`/`t-en`), or
the overall two-section structure (`#overview` then `#detail`).

**Every visible string must be bilingual, no exceptions.** Every `PHASES`/`NODES` text
field (`title`, `kindTag`, `desc`, `caption`, and every `detail.*` field) and every
Section-1 overview string (Inputs list, counters, box-sum, agent-strip, Outputs cards,
kicker/h1/lede in both sections) must be authored as a `<span class="t-vi">...</span
><span class="t-en">...</span>` pair at the same DOM position — the template's own
`var t = function (vi, en) { return '<span class="t-vi">'+vi+'</span><span class="t-en">'+en+'</span>'; }`
helper is already wired in for exactly this; use it for every `NODES`/`PHASES` field
instead of a bare string. Exceptions: literal code/file identifiers that don't
translate (a skill name like `qa-run`, a filename like `checks.json`, a model id like
`claude-sonnet-4-6`) can stay as plain text — don't force a translation onto something
that isn't actually language-dependent.

## Phase 0 — Interview for the real pipeline

Before writing anything, get from the user (ask if not given):
- **The trigger**: what actually kicks the pipeline off (a slash command, a webhook, a
  cron, a human action)?
- **The stages, in order**: each stage's real agent/subagent (and its actual model, if
  known — don't invent a model name), the skill/prompt-logic it runs, and the concrete
  tool(s) it calls (a real tool name, not "some tool").
- **Data flow between stages**: what file/object each stage reads (upstream) and
  produces (downstream) — this is what becomes `EDGES` and each node's `detail.upstream`/
  `detail.downstream`.
- **Failure/gate behavior**: does any stage gate the next one (pass/fail, human
  approval)? This becomes `detail.failure` and should show up as a real branch/label in
  the graph (e.g. the reference's `happy.md (PASS)` / `error.md (FAIL)` gate), not
  smoothed over.
- **The inputs** (what the user/operator supplies before the pipeline starts) and the
  **final deliverables** (what comes out at the end, with real file extensions).

**Never invent a specific detail you weren't given** (a model name, a tool name, a file
name) — ask, or leave that field generic/omitted, the same anti-fabrication standard
used elsewhere in this skill library (ba-skill, sales-proposal-skill): a confident-looking
but made-up detail is worse than an honestly generic one.

## Phase 1 — Build the data model

### `PHASES` — one entry per pipeline stage/column
```js
{ id: 0, title: 'Stage name', caption: '<b>Out:</b> what this phase produces, in one line.' }
```
`id` is the column index (0, 1, 2, ...), left to right, in real pipeline order.

### `NODES` — one entry per box in the graph
```js
{ id: 'unique-id', phase: 0, row: 0, kind: 'trigger'|'agent'|'skill'|'tool'|'deliverable',
  title: 'Node name', kindTag: 'Short label shown under the title',
  desc: 'One-line plain description of what this node does.',
  icon: 'one of the 16 ICO keys above',
  model: 'claude-sonnet-4-6' /* OPTIONAL — only for a real LLM agent node, real model id */,
  detail: { purpose, tools, upstream, downstream, failure } /* OPTIONAL — add for agent/skill
    nodes where you have real specifics; omit rather than pad it out for a trivial node */
}
```
- **`row` convention** (matches the reference, keep it for visual consistency): row 0 =
  trigger/agent for that phase, row 1 = the skill/logic behind it, row 2 = the tool(s) it
  calls, row 3 = the deliverable/gate output of that phase. Not every phase needs all 4
  rows — the reference's own Phase 0 only uses rows 0-2 (no deliverable row there).
- **`kind` → color**: `trigger` (blue-grey), `agent` (Claude orange, gets the Claude mark
  + model chip automatically if `model` is set), `skill` (tan/brown), `tool` (green),
  `deliverable` (dark terracotta). Pick the `kind` that matches what the node actually
  is, not what color you want.
- **Icons**: reuse one of the 16 existing keys by semantic fit (e.g. `user` for a human
  trigger, `terminal` for a CLI/SSH tool, `json`/`md`/`pdf` for typed deliverables,
  `shield` for a verification/gate step). Only add a new SVG entry to `ICO` if truly
  nothing fits — match the existing style exactly (24×24 viewBox, `stroke="currentColor"`,
  `stroke-width="2"`, no fill), don't introduce a different icon visual language.

### `EDGES` — one `['from-id', 'to-id']` pair per real data-flow connection
Follow the actual flow: trigger → first agent, agent → its own skill/tool/deliverable
chain, last node of a phase → first node of the next phase. The engine auto-draws a
smooth vertical connector for same-phase edges and a smooth horizontal one for
cross-phase edges — you never specify the path itself.

## Phase 2 — Section 1 overview content

Rewrite, using the reference's exact markup patterns as a mold:
- **Kicker** (`<span class="kicker">`), `<h1>` + `<span class="thin">— subtitle</span>`,
  and one `<p class="lede">` — name the real orchestrator/pipeline and give the one-line
  shape ("N stages, driven by X, producing Y").
- **Inputs panel**: one `<li>` per real input, each with a small stroke-icon glyph (reuse
  patterns from the reference — file, mic/transcript, flow-diagram, screenshot, globe,
  config — or a simple new one in the same 2px-stroke style), a bold label, and a short
  description.
- **Black-box panel**: 2-4 `<div class="counter" data-count="N">` blocks with a real
  count (e.g. number of stages, number of tools, number of skills) — the engine animates
  these on scroll automatically, you only set `data-count`. Follow with one `<div
  class="box-sum">` paragraph explaining the whole pipeline in plain language, and an
  `.agent-strip` listing each real agent name (only include the Claude mark SVG if that
  agent really is a Claude model — for a non-Claude/non-LLM step, drop the mark or the
  whole strip rather than implying it's Claude when it isn't).
- **Outputs panel**: one `.out-card` per real deliverable, each with a short `.tag`, a
  title, a real file extension in `.ext`, and one sentence on what it actually contains.

## Phase 3 — Assemble and verify

1. Replace `<title>` to name the real pipeline.
2. Confirm every `EDGES` pair references an `id` that actually exists in `NODES` — a
   dangling edge silently draws nothing and is easy to miss.
3. Confirm every `NODES.phase` value has a matching entry in `PHASES` — an orphaned
   phase number renders the node in a column with no header.
4. Confirm the overview counters' numbers actually match what's really in `NODES`/
   `PHASES` (e.g. if `PHASES.length` is 5, don't say "4 stages" in the lede).
5. Grep the assembled file for leftover reference-specific text (`qa-run`, `Odoo`,
   `qa-qc-workspace`, `QA/QC`) that wasn't actually replaced — a stray leftover string
   from the template is a sign Phase 1/2 wasn't fully done, not something to ship.
6. Confirm the CSS/JS sections are byte-identical to the template (diff against
   `assets/workflow-template.html` outside the `PHASES`/`NODES`/`EDGES`/overview-HTML/
   title/kicker/lede regions) — this skill's whole value is the tested rendering engine;
   don't let a rewrite drift from it.
7. Grep the assembled file for `class="t-vi"` and `class="t-en"` and confirm the counts
   match exactly — a mismatch means some string was authored in only one language
   (usually a forgotten `t(...)` wrap on a new `NODES`/`PHASES` field).

## Delivery

One self-contained `.html` file, named after the pipeline (e.g.
`<pipeline-slug>-workflow.html`) — nothing else to send alongside it. Mention in your
summary which pipeline details came directly from the user vs. which fields you left
generic/omitted for lack of real specifics.

## Judgment calls

- **User describes a pipeline with only 1-2 stages** — still use the same two-section
  shape; fewer `PHASES` entries and a smaller graph is correct, don't pad it out to look
  like the 5-phase reference.
- **Pipeline isn't Claude/LLM-based at all** (e.g. a plain CI/CD or ETL pipeline) — drop
  the Claude mark/model chip entirely; `kind: 'agent'` still applies to "the thing that
  does the work" in a stage, it doesn't require an LLM.
- **No real failure/gate behavior exists** — say so plainly (a `detail.failure` of "no
  gate; always proceeds" is honest), don't invent a gate to look more sophisticated than
  the real pipeline is.
