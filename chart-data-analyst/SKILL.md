---
name: chart-data-analyst
description: Decides the real numbers for all 18 charts + 4 diagrams from the 4 subagents' digests and audited findings — one place deciding data, instead of each subagent inventing chart values independently. Called by the technext-sales-proposal orchestrator right after source-auditor passes (audited-findings.json exists with no blocking issues), before front-matter-writer/html-renderer.
---

# Chart data analyst — one place decides every number

## Why this exists

When each of the 4 research subagents built its own charts inline while writing,
nothing forced consistency: one might round differently, one might invent illustrative
numbers without the `.assess` tag another one always used, and there was no single
place to catch a chart whose data quietly contradicted a fact `source-auditor` had
just flagged. This skill is that single place.

## Precondition

**Only run after `source-auditor` has produced `audited-findings.json` with an empty
`blocking_issues` array.** If `source-auditor` is still blocking on unresolved
issues, this skill has nothing trustworthy to compute numbers from yet — don't run it
against raw, unaudited subagent output.

## What to do

Read `audited-findings.json` and all 4 subagents' digests. For each of the 18
required charts + 4 diagrams (see `technext-sales-proposal`'s
`assets/charts-and-diagrams.md` for the exact manifest — canvas id, type, owning
group, what it shows):

1. **Pull the real number from a finding when one exists.** If `audited-findings.json`
   contains an actual sourced or `Confirmed` figure that maps to this chart (e.g. a
   `.cite`-graded staff count for `cHeadcount`), use it directly — don't re-estimate
   something that's already a real fact.
2. **When no real figure exists, build an explicit `.assess` estimate** and record
   *what it's based on* (e.g. "modelled from a 4.3★ average across N reviews") —
   never a bare invented number with no stated reasoning.
3. **Keep scale and style consistent across charts** — if `cRevStream` uses percentage
   shares, don't have `cRevMix` silently switch to raw dollar figures without saying
   so; a reader flipping between charts shouldn't have to guess the unit changed.
4. **Percentages always get a labeled tooltip** — carry this rule forward into the
   config you emit (`plugins.tooltip.callbacks.label` appending `%`), matching the
   chart-manifest rule.

## Output

One file, `chart-manifest.json`: an array of
`{ "canvasId": "...", "type": "...", "data": {...Chart.js-shaped data...}, "assess": true|false, "basis": "..." (only when assess is true) }`
objects, one per required chart, plus a parallel array for the 4 diagram slots
(`{ "diagramId": "...", "content": "...static HTML fragment..." }`). `html-renderer`
reads this file to generate the `regChart(() => mkChart(...))` calls and diagram
markup — it does not invent chart data itself.
